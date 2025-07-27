#!/bin/bash

GREEN="\e[32m"
RED="\e[31m"
YELLOW="\e[33m"
BLUE="\e[34m"
BOLD="\e[1m"
RESET="\e[0m"

# Check args
if [ "$#" -lt 1 ]; then
  echo -e "${YELLOW}Usage: $0 <job_folder> [num_runs_per_job] [num_cores] [--reverse] [--strategy=batch|round-robin|shuffled] [--b1-first] [--bmode=both|b1|b0] [--test] [--concurrent] [--b1-cores=N]${RESET}"
  echo -e "${YELLOW}
  --strategy=batch        Run each job completely before moving to the next.
  --strategy=round-robin  Interleave jobs by doing one run of each before repeating.
  --strategy=shuffled     Randomize the order of job-run pairs.
  --reverse               Sort job files in reverse order.
  --b1-first              Run b1 jobs first (high RAM jobs), then b0 jobs. Default is b0 first.
  --bmode=both|b1|b0      Choose which batch types to run: both (default), only b1, or only b0.
  --test                  Only print execution plan (job files and run numbers), don't run anything.
  --concurrent            Run B0 and B1 jobs concurrently (otherwise sequential).
  --b1-cores=N            Set max number of B1 cores to use (default is 2).
${RESET}"
  exit 1
fi

INSTANCE_ID=$(head /dev/urandom | tr -dc a-z0-9 | head -c 6)

REVERSE_SORT=false
STRATEGY="round-robin"
TEST_MODE=false
B1_FIRST=false
BMODE="both"
CONCURRENT=false
B1_CORES_MAX=2

for arg in "$@"; do
  case "$arg" in
    --reverse) REVERSE_SORT=true ;;
    --strategy=*) STRATEGY="${arg#*=}" ;;
    --test) TEST_MODE=true ;;
    --b1-first) B1_FIRST=true ;;
    --bmode=*) BMODE="${arg#*=}" ;;
    --concurrent) CONCURRENT=true ;;
    --b1-cores=*)
      B1_CORES_MAX="${arg#*=}"
      # Make sure B1 cores is never more than 2 (for safety)
      if [ "$B1_CORES_MAX" -gt 2 ]; then
        echo -e "${YELLOW}Warning: B1 cores limited to 2 to prevent swapping issues.${RESET}"
        B1_CORES_MAX=2
      fi
      ;;
  esac
done

JOB_FOLDER="$1"
NUM_RUNS="${2:-1}"
CORES="${3:-4}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ ! -d "$JOB_FOLDER" ]; then
  echo -e "${RED}Error: Folder '$JOB_FOLDER' not found.${RESET}"
  exit 1
fi

LOG_DIR="$JOB_FOLDER/run_logs"
mkdir -p "$LOG_DIR"

# Setup logging without breaking signal handling
LOG_FILE="$LOG_DIR/full_run_${INSTANCE_ID}.log"
# Function to log output to both console and file
log() {
  # Print colored text to the terminal
  echo -e "$@"

  # Strip color codes and write plain text to the log file
  echo -e "$@" | sed 's/\x1b\[[0-9;]*m//g' >> "$LOG_FILE"
}

log "$(date +"%Y-%m-%d %H:%M:%S") ${BLUE}Starting batch simulation with instance ID: ${INSTANCE_ID}${RESET} PID:$$"

# Create stats tracking files for this instance
FIRST_JOB_START_FILE="$LOG_DIR/first_job_start_${INSTANCE_ID}.txt"
LAST_JOB_END_FILE="$LOG_DIR/last_job_end_${INSTANCE_ID}.txt"

# Initialize script start time (different from first job time)
SCRIPT_START_TIME=$(date +%s)


# Function to display statistics
display_stats() {
  # Count completed jobs for this instance
  completed_count=0
  if [ -f "$LOG_DIR/instance_jobs_${INSTANCE_ID}.txt" ]; then
    completed_count=$(wc -l < "$LOG_DIR/instance_jobs_${INSTANCE_ID}.txt")
  fi

  # If no jobs completed yet, show script runtime stats only
  if [ "$completed_count" -eq 0 ]; then
    current_ts=$(date +%s)
    script_runtime=$((current_ts - SCRIPT_START_TIME))

    # Format runtime as HH:MM:SS
    hours_fmt=$((script_runtime / 3600))
    minutes_fmt=$(((script_runtime % 3600) / 60))
    seconds_fmt=$((script_runtime % 60))

    log "\n${BOLD}${BLUE}=== INSTANCE STATISTICS (${INSTANCE_ID}) ===${RESET}"
    log "${BOLD}Script runtime:${RESET} ${hours_fmt}h ${minutes_fmt}m ${seconds_fmt}s"
    log "${BOLD}Completed jobs:${RESET} 0"
    log "${YELLOW}No jobs completed yet.${RESET}"
    return
  fi

  # Get first job start time and last job end time
  first_job_start=""
  last_job_end=""

  if [ -f "$FIRST_JOB_START_FILE" ]; then
    first_job_start=$(cat "$FIRST_JOB_START_FILE")
  else
    # Fallback to script start time if no jobs have started
    first_job_start=$SCRIPT_START_TIME
  fi

  if [ -f "$LAST_JOB_END_FILE" ]; then
    last_job_end=$(cat "$LAST_JOB_END_FILE")
  else
    # If no jobs have completed yet, use current time
    last_job_end=$(date +%s)
  fi

  # Calculate actual processing time
  actual_runtime=$((last_job_end - first_job_start))

  # Calculate jobs per hour based on actual job processing time
  if [ "$actual_runtime" -gt 0 ]; then
    hours=$(echo "scale=2; $actual_runtime / 3600" | bc)
    jobs_per_hour=$(echo "scale=2; $completed_count / $hours" | bc)

    # Also calculate script total runtime for reference
    current_ts=$(date +%s)
    script_runtime=$((current_ts - SCRIPT_START_TIME))

    # Format runtimes as HH:MM:SS
    actual_hours=$((actual_runtime / 3600))
    actual_minutes=$(((actual_runtime % 3600) / 60))
    actual_seconds=$((actual_runtime % 60))

    script_hours=$((script_runtime / 3600))
    script_minutes=$(((script_runtime % 3600) / 60))
    script_seconds=$((script_runtime % 60))

    log "\n${BOLD}${BLUE}=== INSTANCE STATISTICS (${INSTANCE_ID}) ===${RESET}"
    log "${BOLD}Job processing time:${RESET} ${actual_hours}h ${actual_minutes}m ${actual_seconds}s"
    log "${BOLD}Script total runtime:${RESET} ${script_hours}h ${script_minutes}m ${script_seconds}s"
    log "${BOLD}Completed jobs:${RESET} $completed_count"
    log "${BOLD}Jobs per hour:${RESET} $jobs_per_hour"

    # Get detailed B0/B1 stats if available
    if [ -f "$LOG_DIR/instance_b0_jobs_${INSTANCE_ID}.txt" ] || [ -f "$LOG_DIR/instance_b1_jobs_${INSTANCE_ID}.txt" ]; then
      b0_count=0
      b1_count=0

      if [ -f "$LOG_DIR/instance_b0_jobs_${INSTANCE_ID}.txt" ]; then
        b0_count=$(wc -l < "$LOG_DIR/instance_b0_jobs_${INSTANCE_ID}.txt")
      fi

      if [ -f "$LOG_DIR/instance_b1_jobs_${INSTANCE_ID}.txt" ]; then
        b1_count=$(wc -l < "$LOG_DIR/instance_b1_jobs_${INSTANCE_ID}.txt")
      fi

      # Calculate B0/B1 jobs per hour
      b0_per_hour=$(echo "scale=2; $b0_count / $hours" | bc)
      b1_per_hour=$(echo "scale=2; $b1_count / $hours" | bc)

      log "${BOLD}B0 jobs completed:${RESET} $b0_count (${b0_per_hour} per hour)"
      log "${BOLD}B1 jobs completed:${RESET} $b1_count (${b1_per_hour} per hour)"
    fi
  else
    log "\n${YELLOW}Not enough runtime to calculate statistics.${RESET}"
  fi

  #cleanup
  rm -f "$LOG_DIR/instance_b1_jobs_${INSTANCE_ID}.txt"
  rm -f "$LOG_DIR/instance_b0_jobs_${INSTANCE_ID}.txt"
  rm -f "$LOG_DIR/instance_jobs_${INSTANCE_ID}.txt"
  rm -f $FIRST_JOB_START_FILE
  rm -f $LAST_JOB_END_FILE

}

# Function to kill containers and parallel jobs
killeverything() {
#  log "${RED}Killing Docker containers...${RESET}"
#  docker ps --format '{{.Names}}' | grep "i${INSTANCE_ID}_" | xargs -r docker stop
  log "${YELLOW}Killing parallel child jobs...${RESET}"
  pkill -P $$
}


# Unified trap handler
handle_signal() {
  local signal="$1"
  case "$signal" in
    SIGINT|SIGTERM)
      interactive_cleanup
      ;;
    SIGHUP)
      noninteractive_cleanup
      ;;
  esac
}

# Trap all relevant signals
trap 'handle_signal SIGINT' SIGINT
trap 'handle_signal SIGTERM' SIGTERM
trap 'handle_signal SIGHUP' SIGHUP

# Interactive cleanup for SIGINT/SIGTERM
interactive_cleanup() {
  log "\n${RED}✋ Caught interrupt (${BOLD}$1${RESET}${RED}).${RESET}"
  display_stats
  killeverything
  exit 1
}

# Non-interactive cleanup for SIGHUP
noninteractive_cleanup() {
  log "\n${RED}💀 Terminal closed or hangup detected (SIGHUP).${RESET}"
  display_stats
  log "${YELLOW}Auto-cleaning everything...${RESET}"
  killeverything
  exit 1
}



TEMP_RUNNER=$(mktemp)
cat > "$TEMP_RUNNER" << 'EOL'
#!/bin/bash
job_file="$1"
run_number="$2"
job_name=$(basename "$job_file" .job)
container_tag="i${INSTANCE_ID}_${job_name}_run${run_number}"

# Simple function to log echo statements to both console and main log file
fullrun_log() {
  # Print to console with colors
  echo -e "$1"

  # Also append to main log file without colors
  echo -e "$1" | sed 's/\x1b\[[0-9;]*m//g' >> "$LOG_FILE"
}

if [ -f "$LOG_DIR/completed_jobs.txt" ] && grep -q "${job_name}_run${run_number}" "$LOG_DIR/completed_jobs.txt"; then
  exit 0
fi

export SIMULATION_CMD=$job_file
#export NS_GLOBAL_VALUE=RngRun
export run_number

echo "Simulation command is: $SIMULATION_CMD" >> "$LOG_DIR/${job_name}_run${run_number}.log"
echo "Container name: $container_tag" >> "$LOG_DIR/${job_name}_run${run_number}.log"

start_time=$(date +%s)
start_readable=$(date +"%Y-%m-%d %H:%M:%S")
start_short=$(date +"%H:%M:%S")
echo ">>> [${job_name}_run${run_number}] Started at $start_readable" >> "$LOG_DIR/${job_name}_run${run_number}.log"
fullrun_log "\n[${job_name}_run${run_number}] ${RED}Started at${RESET} $start_short"

#docker compose run --rm --name "$container_tag" "$DOCKER_SERVICE" &>> "$LOG_DIR/${job_name}_run${run_number}.log"
$SCRIPT_DIR/run_singularity_local.sh run $SIMULATION_CMD "$run_number" &>> "$LOG_DIR/${job_name}_run${run_number}.log"
exit_code=$?

# Track job start/end times for statistics
job_end_time=$(date +%s)

# Update first job start time and last job end time (with file locks)
(
  flock -x 200
  # For the first job ever, record start time if not already set
  if [ ! -f "$LOG_DIR/first_job_start_${INSTANCE_ID}.txt" ]; then
    echo "$start_time" > "$LOG_DIR/first_job_start_${INSTANCE_ID}.txt"
  fi

  # Always update the last job end time
  echo "$job_end_time" > "$LOG_DIR/last_job_end_${INSTANCE_ID}.txt"
) 200>"$LOG_DIR/job_times_${INSTANCE_ID}.lock"
rm -f "$LOG_DIR/job_times_${INSTANCE_ID}.lock"

if [ $exit_code -eq 0 ]; then
  # Add to global completed jobs file (for resuming)
  (
    flock -x 200
    echo "${job_name}_run${run_number}" >> "$LOG_DIR/completed_jobs.txt"
  ) 200>"$LOG_DIR/completed_jobs.txt.lock"
  rm -f "$LOG_DIR/completed_jobs.txt.lock"

  # Add to instance-specific completed jobs file (for stats)
  (
    flock -x 200
    echo "${job_name}_run${run_number}" >> "$LOG_DIR/instance_jobs_${INSTANCE_ID}.txt"

    # Track job type (B0 or B1)
    if [[ "$job_name" == *"-b1-"* ]]; then
      echo "${job_name}_run${run_number}" >> "$LOG_DIR/instance_b1_jobs_${INSTANCE_ID}.txt"
    else
      echo "${job_name}_run${run_number}" >> "$LOG_DIR/instance_b0_jobs_${INSTANCE_ID}.txt"
    fi
  ) 200>"$LOG_DIR/instance_jobs_${INSTANCE_ID}.lock"
  rm -f "$LOG_DIR/instance_jobs_${INSTANCE_ID}.lock"

  job_counter_file="$LOG_DIR/${job_name}.counter"
  (
    flock -x 200
    current_count=0
    [ -f "$job_counter_file" ] && current_count=$(cat "$job_counter_file")
    new_count=$((current_count + 1))
    echo "$new_count" > "$job_counter_file"

    if [ "$new_count" -eq "$NUM_RUNS" ]; then
      echo ">>> [$job_name] All $NUM_RUNS runs completed. Moving to completed/" >> "$LOG_DIR/${job_name}_run${run_number}.log"
      mkdir -p "$JOB_FOLDER/completed/"
      mv "$job_file" "$JOB_FOLDER/completed/"
#      rm -f "$job_counter_file"
    fi
  ) 200>"$job_counter_file.lock"
  rm -f "$job_counter_file.lock"

  echo ">>> [${job_name}_run${run_number}] SUCCESS" >> "$LOG_DIR/${job_name}_run${run_number}.log"
else
  echo ">>> [${job_name}_run${run_number}] FAILED with exit code $exit_code" >> "$LOG_DIR/${job_name}_run${run_number}.log"
  exit $exit_code
fi

end_time=$(date +%s)
end_readable=$(date +"%Y-%m-%d %H:%M:%S")
end_short=$(date +"%H:%M:%S")
elapsed=$((end_time - start_time))
mins=$((elapsed / 60))
secs=$((elapsed % 60))

echo ">>> Finished at $end_readable with duration: ${mins}m ${secs}s" >> "$LOG_DIR/${job_name}_run${run_number}.log"
fullrun_log "\n>>> [${job_name}_${BOLD}${RED}run${run_number}${RESET}] ${BOLD}${BLUE}Duration:${RESET} ${mins}m ${secs}s ${RED}finished at${RESET} $end_short"
EOL

chmod +x "$TEMP_RUNNER"

JOB_FILES_ARRAY=()
if $REVERSE_SORT; then
  mapfile -t JOB_FILES_ARRAY < <(ls -1 "$JOB_FOLDER"/*.job | sort -r)
else
  mapfile -t JOB_FILES_ARRAY < <(ls -1 "$JOB_FOLDER"/*.job | sort)
fi

log "\n$(date +"%Y-%m-%d %H:%M:%S") >> Jobs identified:"

B0_FILES=()
B1_FILES=()
for job_file in "${JOB_FILES_ARRAY[@]}"; do
  job_basename=$(basename "$job_file")
  if [[ "$job_basename" == *"-b1-"* ]]; then
    B1_FILES+=("$job_file")
    log "${YELLOW}B1 (high RAM):${RESET} $job_file"
  else
    B0_FILES+=("$job_file")
    log "${GREEN}B0 (standard):${RESET} $job_file"
  fi
done

# Apply BMODE filtering
case "$BMODE" in
  b1)
    B0_FILES=()
    log "${BLUE}Only B1 jobs will be executed (--bmode=b1)${RESET}"
    ;;
  b0)
    B1_FILES=()
    log "${BLUE}Only B0 jobs will be executed (--bmode=b0)${RESET}"
    ;;
  both) ;; # default behavior
  *)
    log "${RED}Invalid bmode: $BMODE${RESET}"
    exit 1
    ;;
esac

generate_job_list() {
  local job_list_file=$1
  local job_files=("${@:2}")
  case "$STRATEGY" in
    batch)
      for job_file in "${job_files[@]}"; do
        for ((run=1; run<=NUM_RUNS; run++)); do
          echo "$job_file $run" >> "$job_list_file"
        done
      done
      ;;
    round-robin)
      for ((run=1; run<=NUM_RUNS; run++)); do
        for job_file in "${job_files[@]}"; do
          echo "$job_file $run" >> "$job_list_file"
        done
      done
      ;;
    shuffled)
      for job_file in "${job_files[@]}"; do
        for ((run=1; run<=NUM_RUNS; run++)); do
          echo "$job_file $run"
        done
      done | shuf >> "$job_list_file"
      ;;
    *)
      log "${RED}Invalid strategy: $STRATEGY${RESET}"
      exit 1
      ;;
  esac
}

B0_JOB_LIST=$(mktemp)
B1_JOB_LIST=$(mktemp)

generate_job_list "$B0_JOB_LIST" "${B0_FILES[@]}"
generate_job_list "$B1_JOB_LIST" "${B1_FILES[@]}"

COMBINED_JOB_LIST=$(mktemp)
if $B1_FIRST; then
  cat "$B1_JOB_LIST" > "$COMBINED_JOB_LIST"
  cat "$B0_JOB_LIST" >> "$COMBINED_JOB_LIST"
else
  cat "$B0_JOB_LIST" > "$COMBINED_JOB_LIST"
  cat "$B1_JOB_LIST" >> "$COMBINED_JOB_LIST"
fi

# Set B0 cores to use all available cores minus B1 cores when running concurrently
B0_CORES=$CORES
B1_CORES=$B1_CORES_MAX

# Ensure B1 cores never exceed maximum allowed
if [ "$B1_CORES" -gt "$B1_CORES_MAX" ]; then
  B1_CORES=$B1_CORES_MAX
fi

# If overall cores is less than B1 cores, adjust B1 cores down
if [ "$CORES" -lt "$B1_CORES" ]; then
  B1_CORES=$CORES
fi

# Calculate available B0 cores for concurrent mode
if $CONCURRENT; then
  B0_CORES=$((CORES - B1_CORES))
  # Ensure at least 1 core for B0 jobs
  if [ "$B0_CORES" -lt 1 ]; then
    B0_CORES=1
  fi
fi

if $CONCURRENT; then
  log "\n${BLUE}Running in concurrent mode with $B0_CORES cores for B0 jobs and $B1_CORES cores for B1 jobs${RESET}"
else
  if [ "$CORES" -le 2 ]; then
    B1_CORES=$CORES
    log "\n${BLUE}Using $CORES cores for all jobs (no separation)${RESET}"
  else
    log "\n${BLUE}Using $B0_CORES cores for B0 jobs and $B1_CORES cores for B1 jobs${RESET}"
  fi
fi

if $TEST_MODE; then
  log "\n${BLUE}Test mode enabled. The following jobs would be executed:${RESET}"

  if [ ${#B0_FILES[@]} -gt 0 ]; then
    log "\n${GREEN}B0 jobs (standard) - would run with $B0_CORES cores:${RESET}"
    grep -f <(printf "%s\n" "${B0_FILES[@]}") "$COMBINED_JOB_LIST" | while IFS=' ' read -r job_file run; do
      log "  - $(basename "$job_file") run $run"
    done
  fi

  if [ ${#B1_FILES[@]} -gt 0 ]; then
    log "\n${YELLOW}B1 jobs (high RAM) - would run with $B1_CORES cores:${RESET}"
    grep -f <(printf "%s\n" "${B1_FILES[@]}") "$COMBINED_JOB_LIST" | while IFS=' ' read -r job_file run; do
      log "  - $(basename "$job_file") run $run"
    done
  fi

  if $CONCURRENT; then
    log "\n${BLUE}Jobs would run concurrently with:${RESET}"
    log "  - $B0_CORES cores for B0 jobs"
    log "  - $B1_CORES cores for B1 jobs (hard limit of $B1_CORES_MAX)"
  else
    log "\n${BLUE}Jobs would run sequentially.${RESET}"
  fi

  log "\n${YELLOW}Note: No jobs were actually executed.${RESET}"
  rm "$TEMP_RUNNER" "$B0_JOB_LIST" "$B1_JOB_LIST" "$COMBINED_JOB_LIST"
  exit 0
fi

read -p "Do you want to run a dirty-build or fullbuild with cleanup before running the simulations? (d[irty]/f[ull]/n[o]): " choice

case "$choice" in
  [Dd])
    log "Running dirty-build..."
    $SCRIPT_DIR/run_singularity_local.sh dirty-build
    result=$?
    if [ $result -ne 0 ]; then
      log "Dirty-build failed (exit code $result). Exiting."
      exit $result
    fi
    ;;
  [Ff])
    log "Running full build..."
    $SCRIPT_DIR/run_singularity_local.sh build
    result=$?
    if [ $result -ne 0 ]; then
      log "Full build failed (exit code $result). Exiting."
      exit $result
    fi
    ;;
  *)
    log "Skipping build."
    ;;
esac
echo "Scriptdir: $SCRIPT_DIR"
export LOG_DIR
export GREEN RED YELLOW BLUE BOLD RESET
export NUM_RUNS
export JOB_FOLDER
export INSTANCE_ID
export FIRST_JOB_START_FILE
export LAST_JOB_END_FILE
export LOG_FILE
export SCRIPT_DIR

# Concurrent execution - run B0 and B1 jobs simultaneously
if $CONCURRENT; then
  log "${BLUE}Running B0 and B1 jobs concurrently${RESET}"

  # Create the named pipes for status updates
  B0_PIPE=$(mktemp -u)
  B1_PIPE=$(mktemp -u)
  mkfifo "$B0_PIPE"
  mkfifo "$B1_PIPE"

  # Start B0 jobs in background
  if [ ${#B0_FILES[@]} -gt 0 ]; then
    (cat "$B0_JOB_LIST" | parallel -j "$B0_CORES" --line-buffer --colsep ' ' "$TEMP_RUNNER" {1} {2}; echo "B0_DONE" > "$B0_PIPE") &
    B0_PID=$!
    log "${GREEN}Startied B0 jobs with $B0_CORES cores$ PID: $B0_PID${RESET} "
  else
    echo "B0_DONE" > "$B0_PIPE" &
  fi

  # Start B1 jobs in background
  if [ ${#B1_FILES[@]} -gt 0 ]; then
    (cat "$B1_JOB_LIST" | parallel -j "$B1_CORES" --line-buffer --colsep ' ' "$TEMP_RUNNER" {1} {2}; echo "B1_DONE" > "$B1_PIPE") &
    B1_PID=$!
    log "${YELLOW}Started B1 jobs with $B1_CORES cores (max $B1_CORES_MAX) PID: $B1_PID${RESET}"
  else
    echo "B1_DONE" > "$B1_PIPE" &
  fi

  # Wait for both types of jobs to complete using more efficient approach
  log "${BLUE}Waiting for all jobs to complete...${RESET}"

  # Setup a background process to monitor B0 completion
  if [ ${#B0_FILES[@]} -gt 0 ]; then
    {
      # Read from pipe in background - blocks until data is available
      read line < "$B0_PIPE"
      if [ "$line" = "B0_DONE" ]; then
        log "${GREEN}✅ All B0 jobs completed${RESET}"
      fi
    } &
    B0_MONITOR_PID=$!
  else
    B0_MONITOR_PID=""
  fi

  # Setup a background process to monitor B1 completion
  if [ ${#B1_FILES[@]} -gt 0 ]; then
    {
      # Read from pipe in background - blocks until data is available
      read line < "$B1_PIPE"
      if [ "$line" = "B1_DONE" ]; then
        log "${YELLOW}✅ All B1 jobs completed${RESET}"
      fi
    } &
    B1_MONITOR_PID=$!
  else
    B1_MONITOR_PID=""
  fi

  # Wait for all the job processes to complete
  if [ ${#B0_FILES[@]} -gt 0 ]; then
    wait $B0_PID || log "${RED}B0 process exited with error${RESET}"
    wait $B0_MONITOR_PID 2>/dev/null || true
  fi

  if [ ${#B1_FILES[@]} -gt 0 ]; then
    wait $B1_PID || log "${RED}B1 process exited with error${RESET}"
    wait $B1_MONITOR_PID 2>/dev/null || true
  fi

  # Clean up the named pipes
  rm -f "$B0_PIPE" "$B1_PIPE"

# Sequential execution (original behavior)
else
  if [ "$CORES" -le 2 ]; then
    log "${BLUE}Running all jobs with $CORES cores${RESET}"
    cat "$COMBINED_JOB_LIST" | parallel -j "$CORES" --line-buffer --colsep ' ' "$TEMP_RUNNER" {1} {2}
  else
    if $B1_FIRST; then
      if [ ${#B1_FILES[@]} -gt 0 ]; then
        log "\n${YELLOW}Running B1 jobs with $B1_CORES cores${RESET}"
        cat "$B1_JOB_LIST" | parallel -j "$B1_CORES" --line-buffer --colsep ' ' "$TEMP_RUNNER" {1} {2}
      fi
      if [ ${#B0_FILES[@]} -gt 0 ]; then
        log "\n${GREEN}Running B0 jobs with $B0_CORES cores${RESET}"
        cat "$B0_JOB_LIST" | parallel -j "$B0_CORES" --line-buffer --colsep ' ' "$TEMP_RUNNER" {1} {2}
      fi
    else
      if [ ${#B0_FILES[@]} -gt 0 ]; then
        log "\n${GREEN}Running B0 jobs with $B0_CORES cores${RESET}"
        cat "$B0_JOB_LIST" | parallel -j "$B0_CORES" --line-buffer --colsep ' ' "$TEMP_RUNNER" {1} {2}
      fi
      if [ ${#B1_FILES[@]} -gt 0 ]; then
        log "\n${YELLOW}Running B1 jobs with $B1_CORES cores${RESET}"
        cat "$B1_JOB_LIST" | parallel -j "$B1_CORES" --line-buffer --colsep ' ' "$TEMP_RUNNER" {1} {2}
      fi
    fi
  fi
  PID=$!
  log "\n${BLUE}PID = $PID${RESET}"
fi

# Display final statistics
display_stats

rm "$TEMP_RUNNER" "$B0_JOB_LIST" "$B1_JOB_LIST" "$COMBINED_JOB_LIST"
log "${GREEN}✅ All jobs completed. Logs saved to $LOG_DIR${RESET}"
