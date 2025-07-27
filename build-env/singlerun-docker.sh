#!/bin/bash

GREEN="\e[32m"
RED="\e[31m"
YELLOW="\e[33m"
BLUE="\e[34m"
BOLD="\e[1m"
RESET="\e[0m"

if [ "$#" -lt 1 ]; then
  echo -e "${YELLOW}Usage: $0 <job_file> [run_number]${RESET}"
  exit 1
fi

read -p "Do you want to run a dirty-build? before running the simulations? (y/n): " choice

if [[ "$choice" =~ ^[Yy]$ ]]; then
  echo "Running dirty-build..."
  docker compose run --rm dirty-build
  result=$?
  if [ $result -ne 0 ]; then
    echo "Dirty-build failed (exit code $result). Exiting."
    exit $result
  fi
else
  echo "Skipping dirty-build."
fi

JOB_FILE="$1"
RUN_NUMBER="${2:-1}"
JOB_NAME=$(basename "$JOB_FILE" .job)
INSTANCE_ID=$(head /dev/urandom | tr -dc a-z0-9 | head -c 6)
DOCKER_SERVICE="simulation"
JOB_FOLDER=$(dirname "$JOB_FILE")
LOG_DIR="$JOB_FOLDER/run_logs"
mkdir -p "$LOG_DIR"

CONTAINER_TAG="${INSTANCE_ID}_${JOB_NAME}_run${RUN_NUMBER}"
export SIMULATION_CMD=$(cat "$JOB_FILE")
export RngRun=NS_GLOBAL_VALUE=RngRun=$RUN_NUMBER

LOG_FILE="$LOG_DIR/${JOB_NAME}_run${RUN_NUMBER}.log"
echo "Simulation command is: $SIMULATION_CMD" >> "$LOG_FILE"
echo "Container name: $CONTAINER_TAG" >> "$LOG_FILE"

cleanup() {
  echo -e "${RED} Caught interrupt. Stopping container ${CONTAINER_TAG}...${RESET}"
  docker stop "$CONTAINER_TAG" &>/dev/null
  exit 1
}
trap cleanup SIGINT

start_time=$(date +%s)
start_readable=$(date +"%Y-%m-%d %H:%M:%S")
echo ">>> [${JOB_NAME}_run${RUN_NUMBER}] Started at $start_readable" >> "$LOG_FILE"
echo -e "${BLUE}Instance ID: ${INSTANCE_ID}${RESET}"
echo -e "\n>>> [${JOB_NAME}_${BOLD}${RED}run${RUN_NUMBER}${RESET}] Started at $start_readable"

docker compose run --rm --name "$CONTAINER_TAG" "$DOCKER_SERVICE" &>> "$LOG_FILE"
exit_code=$?

if [ $exit_code -eq 0 ]; then
  echo ">>> [${JOB_NAME}_run${RUN_NUMBER}] SUCCESS" >> "$LOG_FILE"
else
  echo ">>> [${JOB_NAME}_run${RUN_NUMBER}] FAILED with exit code $exit_code" >> "$LOG_FILE"
  exit $exit_code
fi

end_time=$(date +%s)
end_readable=$(date +"%Y-%m-%d %H:%M:%S")
elapsed=$((end_time - start_time))
mins=$((elapsed / 60))
secs=$((elapsed % 60))

echo ">>> Finished at $end_readable with duration: ${mins}m ${secs}s" >> "$LOG_FILE"
echo -e "\n>>> [${JOB_NAME}_${BOLD}${RED}run${RUN_NUMBER}${RESET}] ${BOLD}${BLUE}Duration:${RESET} ${mins}m ${secs}s"
