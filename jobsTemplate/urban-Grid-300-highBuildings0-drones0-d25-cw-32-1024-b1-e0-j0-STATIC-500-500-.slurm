#!/bin/bash
### Job name - can be easily modified for each experiment
#SBATCH --job-name=urban-Grid-300-highBuildings0-drones0-d25-cw-32-1024-b1-e0-j0-STATIC-500-500

### Job array specification
#SBATCH --array=6-9  # Run tasks 1-10, max 5 concurrent jobs
                        # Modify this range as needed

### Email notification
#SBATCH --mail-user=nicola.ursino@studenti.unipd.it
#SBATCH --mail-type=ALL

### Create log directory and define log file paths
### Set this to your project repository path
PROJECT_PATH="/home/nursino/storage/Vanets-ns3-fb"  # Update this together with "#SBATCH --error" and "SBATCH --output" !
LOG_DIR="${PROJECT_PATH}/jobsTemplate/logs"
mkdir -p ${LOG_DIR}

### Generate timestamp for log files
JOB_NAME=urban-Grid-300-highBuildings0-drones0-d25-cw-32-1024-b1-e0-j0-STATIC-500-500
ENV_LOG_FILE="${LOG_DIR}/${JOB_NAME}_${SLURM_JOB_ID}_run_${SLURM_ARRAY_TASK_ID}.env"

### Standard output and error redirection

#SBATCH --error=%x_id_%A_run_%a.err
#SBATCH --output=%x_id_%A_run_%a..out

### Queue selection
#SBATCH --partition=debug

### Resource allocation
#SBATCH --ntasks=1
#SBATCH --mem=7G  # Adjust based on your simulation needs

### Time limit (HH:MM:SS)
#SBATCH --time=02:00:00

### Node constraint (if needed)
#SBATCH --constraint=debug02

### GPU resources (if needed)

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

# Save full environment to log file (like the 'set' command did in PBS)
env > ${ENV_LOG_FILE}
echo "Environment saved to: ${ENV_LOG_FILE}"

### Define paths and parameters
REPO_PATH="/mnt/ns-3"   # Path to the ns-3 submodule

# Define the simulation command (binary name and parameters)
SIMULATION_CMD="fb-vanet-urban --buildings=1 --actualRange=500 --mapBasePath=../maps/Grid-300/Grid-300 --cwMin=32 --cwMax=1024 --vehicleDistance=25 --startingNode=4896 --propagationLoss=1 --protocol=4 --area=2000 --smartJunctionMode=0 --errorRate=0 --nVehicles=0 --droneTest=0 --highBuildings=0 --flooding=0  --printToFile=1 --printCoords=0 --createObstacleShadowingLossFile=0 --useObstacleShadowingLossFile=1 --forgedCoordTest=0 --forgedCoordRate=0 --maxRun=1"  # Update this!

# Setup Singularity container path
CONTAINER_PATH="$PROJECT_PATH/singularity-ns3-image.sif"

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
  --bind $PROJECT_PATH:/mnt \
  $CONTAINER_PATH \
  /mnt/run-simulation-slurm-helper.sh \
  "$REPO_PATH" \
  "fb-vanet-urban/$SIMULATION_CMD" \
  "${SLURM_ARRAY_TASK_ID}"

EXIT_CODE=$?

echo "Simulation completed at $(date) with exit code: $EXIT_CODE"
echo "Environment log: ${ENV_LOG_FILE}"
echo "========================"

exit $EXIT_CODE
