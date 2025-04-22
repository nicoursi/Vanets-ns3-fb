#!/bin/bash

GREEN="\e[32m"
RED="\e[31m"
YELLOW="\e[33m"
BLUE="\e[34m"
BOLD="\e[1m"
RESET="\e[0m"

# Check args
if [ "$#" -lt 1 ]; then
  echo -e "${YELLOW}Usage: $0 <job_folder> [num_runs_per_job] [num_cores]${RESET}"
  exit 1
fi

JOB_FOLDER="$1"
NUM_RUNS="${2:-1}"
CORES="${3:-4}"
DOCKER_SERVICE="simulation"

# Make sure folder exists
if [ ! -d "$JOB_FOLDER" ]; then
  echo -e "${RED}Error: Folder '$JOB_FOLDER' not found.${RESET}"
  exit 1
fi

# Logs
LOG_DIR="$JOB_FOLDER/run_logs"
mkdir -p "$LOG_DIR"


cleanup() {
  echo -e "${RED}✋ Caught interrupt. Cleaning up...${RESET}"
  pkill -P $$  # kill all child processes
  docker ps --format '{{.Names}}' | grep '_run' | xargs -r docker stop
  exit 1
}
trap cleanup SIGINT

TEMP_RUNNER=$(mktemp)
cat > "$TEMP_RUNNER" << 'EOL'
#!/bin/bash
job_file="$1"
run_number="$2"
job_name=$(basename "$job_file" .job)
tag="${job_name}_run${run_number}"

# Check if the job has already been completed
if [ -f "$LOG_DIR/completed_jobs.txt" ] && grep -q "$tag" "$LOG_DIR/completed_jobs.txt"; then
  exit 0  # Skip the job if it's already completed
fi

echo "\nProcessing job: $tag"
export SIMULATION_CMD=$(cat "$job_file")
echo "Simulation command is: $SIMULATION_CMD" >> "$LOG_DIR/${tag}.log"

start_time=$(date +%s)
start_readable=$(date +"%Y-%m-%d %H:%M:%S")
echo ">>> [$tag] Started at $start_readable" >> "$LOG_DIR/${tag}.log"

docker compose run --rm --name "$tag" "$DOCKER_SERVICE" &>> "$LOG_DIR/${tag}.log"
exit_code=$?

# If the job finishes successfully, mark it as completed
if [ $exit_code -eq 0 ]; then
  echo "$tag" >> "$LOG_DIR/completed_jobs.txt"

  job_counter_file="$LOG_DIR/${job_name}.counter"

  (
    flock -x 200
    current_count=0
    [ -f "$job_counter_file" ] && current_count=$(cat "$job_counter_file")
    new_count=$((current_count + 1))
    echo "$new_count" > "$job_counter_file"

    if [ "$new_count" -eq "$NUM_RUNS" ]; then
      echo ">>> [$job_name] All $NUM_RUNS runs completed. Moving to completed/" >> "$LOG_DIR/${tag}.log"
      mv "$job_file" "$JOB_FOLDER/completed/"
      rm -f "$job_counter_file"
    fi
  ) 200>"$job_counter_file.lock"

  echo ">>> [$tag] SUCCESS" >> "$LOG_DIR/${tag}.log"
else
  echo ">>> [$tag] FAILED with exit code $exit_code" >> "$LOG_DIR/${tag}.log"
  exit $exit_code
fi

end_time=$(date +%s)
end_readable=$(date +"%Y-%m-%d %H:%M:%S")
elapsed=$((end_time - start_time))
mins=$((elapsed / 60))
secs=$((elapsed % 60))

echo ">>> Finished at $end_readable with duration: ${mins}m ${secs}s" >> "$LOG_DIR/${tag}.log"
echo -e "\n>>> [$tag] ${BOLD}${BLUE}Duration:${RESET} ${mins}m ${secs}s"

EOL
chmod +x "$TEMP_RUNNER"


# Generate list of job/run pairs
JOB_LIST=$(mktemp)
for job_file in "$JOB_FOLDER"/*.job; do
  for ((run=1; run<=NUM_RUNS; run++)); do
    echo "$job_file $run" >> "$JOB_LIST"
  done
done

# Export variables needed by TEMP_RUNNER
export DOCKER_SERVICE
export LOG_DIR
export GREEN RED YELLOW BLUE BOLD RESET
export NUM_RUNS
export JOB_FOLDER

# Run jobs in parallel
#cat "$JOB_LIST" | parallel -j "$CORES" --colsep ' ' --joblog "$LOG_DIR/joblog.txt" --tag "$TEMP_RUNNER" {1} {2}
cat "$JOB_LIST" | parallel -j "$CORES" --colsep ' ' --joblog "$LOG_DIR/joblog.txt" "$TEMP_RUNNER" {1} {2} --progress


# Cleanup
rm "$TEMP_RUNNER" "$JOB_LIST"

echo -e "${GREEN}✅ All jobs completed. Logs saved to $LOG_DIR${RESET}"
