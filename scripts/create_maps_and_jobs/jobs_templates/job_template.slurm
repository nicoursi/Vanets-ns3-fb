#!/bin/bash
### Job name - can be easily modified for each experiment
#SBATCH --job-name={**jobName}

### Email notification
###SBATCH --mail-user=youremailaddress@email.com
###SBATCH --mail-type=FAIL

### Job array specification %5 means maximum 5 jobs concurrently
#SBATCH --array={**jobarray}

### Standard output and error redirection
#SBATCH --error=./logs/%x_id_%A_run_%a.err
#SBATCH --output=./logs/%x_id_%A_run_%a.out

### Queue selection
#SBATCH --partition=allgroups

### Resource allocation
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem={**ram}
#SBATCH --exclude=dellcuda0,dellcuda1,dellcuda2,dellsrv1,dellsrv4,dellsrv5,vgpu0-0,vgpu1-0,vgpu2-0,vgpu3-0,vgpu4-0,vgpu5-0,vgpu0-1,vgpu1-1,vgpu2-1,vgpu3-1,vgpu4-1,vgpu5-1,vgpu6-0,vgpu7-0,vgpu8-0,vgpu9-0,vgpu10-0,debug00,debug01,debug02,debug03,debug04
### we will use only the nodes hpblade[] except hpblade[16]

### Time limit (HH:MM:SS)
#SBATCH --time={**neededTime}

### Node constraint (if needed)
### SBATCH --constraint=debug02

### spellchecker:words NODELIST allgroups jobarray localtime ntasks zoneinfo

### Find the actual project root
IMAGE_NAME="singularity-ns3-image.sif"
CURRENT_DIR="$(pwd)"
PROJECT_PATH=""
while [[ "$CURRENT_DIR" != "/" ]]; do
  if [[ -d "$CURRENT_DIR/ns-3" ]]; then
    PROJECT_PATH="$CURRENT_DIR"
    break
  fi
  CURRENT_DIR="$(dirname "$CURRENT_DIR")"
done

if [[ -z "$PROJECT_PATH" ]]; then
  echo "ERROR: Could not find project root (looking for the ns-3/ folder)"
  echo "Searched from: $(pwd)"
  exit 1
fi

### Create log directory and define log file paths
LOG_DIR="$(pwd)/logs"
mkdir -p "${LOG_DIR}"

# shellcheck disable=SC1083,SC2125
JOB_NAME={**jobName}
# ENV_LOG_FILE="${LOG_DIR}/${JOB_NAME}_id_${SLURM_JOB_ID}_run_${SLURM_ARRAY_TASK_ID}.env"

### Print detailed job and system information
echo "=== Job Information ==="
echo "Job ID: ${SLURM_JOB_ID}"
echo "Job Name: ${JOB_NAME}"
echo "Array Task ID: ${SLURM_ARRAY_TASK_ID}"
echo "Date: $(date)"
echo "Host: $(hostname)"
echo "Working Directory: $(pwd)"
echo "Running on nodes: ${SLURM_NODELIST}"
echo "SLURM_SUBMIT_DIR: ${SLURM_SUBMIT_DIR}"
echo "========================"

### Save full environment to log file (like the 'set' command did in PBS)
# env >"${ENV_LOG_FILE}"
# echo "Environment saved to: ${ENV_LOG_FILE}"

### Define paths and parameters
REPO_PATH="/mnt/ns-3" # Path to the ns-3 submodule

# Define the simulation command (binary name and parameters)
SIMULATION_CMD="{**command}" # Update this!

# Setup Singularity container path
ENV_FOLDER="build_env"
CONTAINER_PATH="$PROJECT_PATH/$ENV_FOLDER/container/${IMAGE_NAME}"

echo "=== Simulation Parameters ==="
echo "PROJECT_PATH: ${PROJECT_PATH}"
echo "REPO_PATH: ${REPO_PATH}"
echo "SIMULATION_CMD: ${SIMULATION_CMD}"
echo "CONTAINER_PATH: ${CONTAINER_PATH}"
echo "========================"

echo "=== Running Simulation ==="
echo "Starting NS3 simulation at $(date) with RngRun=${SLURM_ARRAY_TASK_ID}"

# Run the NS3 simulation using the runner script inside Singularity
singularity exec \
  --env TZ=Europe/Rome \
  --bind "$PROJECT_PATH":/mnt \
  --bind /usr/share/zoneinfo:/usr/share/zoneinfo:ro \
  --bind /etc/localtime:/etc/localtime:ro \
  "$CONTAINER_PATH" \
  /mnt/$ENV_FOLDER/run_simulation_slurm_helper.sh \
  "$REPO_PATH" \
  "{**sim_folder}/$SIMULATION_CMD" \
  "${SLURM_ARRAY_TASK_ID}"

EXIT_CODE=$?

echo "Simulation completed at $(date) with exit code: $EXIT_CODE"
echo "Environment log: ${ENV_LOG_FILE}"
echo "========================"

exit $EXIT_CODE
