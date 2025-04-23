#!/bin/bash

GREEN="\e[32m"
RED="\e[31m"
YELLOW="\e[33m"
BLUE="\e[34m"
BOLD="\e[1m"
RESET="\e[0m"

# Ensure at least one argument is passed
if [ "$#" -lt 1 ]; then
  echo "Usage: $0 [cmd_file] [n]"
  exit 1
fi

# Required and optional arguments
DOCKER_SERVICE="simulation"
CMD_FILE="$1"
N="${2:-1}"  # Default to 1 if not provided

# Clean up orphaned/stopped containers
echo "Cleaning up stopped containers..."
docker container prune -f

# If a cmd_file is provided, export SIMULATION_CMD from it
if [ -n "$CMD_FILE" ]; then
  if [ -f "$CMD_FILE" ]; then
    echo "Exporting SIMULATION_CMD from file: $CMD_FILE"
    export SIMULATION_CMD=$(cat "$CMD_FILE")
  else
    echo "Error: File '$CMD_FILE' not found!"
    exit 1
  fi
fi

# Run the Docker service N times with individual timing
for ((i=1; i<=N; i++)); do
  echo -e "\n========================= Run #$i of $N ========================="

  run_start_time=$(date +%s)
  run_start_readable=$(date +"%Y-%m-%d %H:%M:%S")
  echo ">>> Starting at: $run_start_readable"

  docker compose run --rm "$DOCKER_SERVICE"
  exit_code=$?

  run_end_time=$(date +%s)
  run_end_readable=$(date +"%Y-%m-%d %H:%M:%S")
  elapsed=$((run_end_time - run_start_time))
  mins=$((elapsed / 60))
  secs=$((elapsed % 60))

  echo ">>> Finished at: $run_end_readable"
  echo -e "${BOLD}${BLUE}>>> Elapsed time for run #$i: ${mins}m ${secs}s${RESET}"

  if [ $exit_code -ne 0 ]; then
    echo -e "${RED}>>> ERROR: Docker service failed on run #$i with exit code $exit_code${RESET}"
    break
  fi
done

exit $exit_code
