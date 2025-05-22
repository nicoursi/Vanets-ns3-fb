#!/bin/bash
### Job name - can be easily modified for each experiment
#SBATCH --job-name=urban-Grid-300-highBuildings0-drones0-d25-cw-32-1024-b0-e0-j0-STATIC-300-500

### Job array specification
#SBATCH --array=6-9

### Email notification
#SBATCH --mail-user=nicola.ursino@studenti.unipd.it
#SBATCH --mail-type=ALL

### Standard output and error redirection
#SBATCH --error=urban-Grid-300-highBuildings0-drones0-d25-cw-32-1024-b0-e0-j0-STATIC-300-500_%A_run_%a.err
#SBATCH --output=urban-Grid-300-highBuildings0-drones0-d25-cw-32-1024-b0-e0-j0-STATIC-300-500_%A_run_%a.out

### Queue selection
#SBATCH --partition=debug

### Resource allocation
#SBATCH --ntasks=1
#SBATCH --mem=7G

### Time limit (HH:MM:SS)
#SBATCH --time=02:00:00

### Node constraint (if needed)
#SBATCH --constraint=debug02

### Set this to your project repository path
PROJECT_PATH="/home/nursino/storage/Vanets-ns3-fb"

### Print basic job information
echo "=== Job Information ==="
echo "Job ID: ${SLURM_JOB_ID}"
echo "Array Task ID: ${SLURM_ARRAY_TASK_ID}"
echo "Date: $(date)"
echo "Host: $(hostname)"
echo "========================"

### Define paths and parameters
REPO_PATH="/mnt/ns-3"

### Define the simulation command
SIMULATION_CMD="fb-vanet-urban --buildings=0 --actualRange=500 --mapBasePath=../maps/Grid-300/Grid-300 --cwMin=32 --cwMax=1024 --vehicleDistance=25 --startingNode=4896 --propagationLoss=1 --protocol=3 --area=2000 --smartJunctionMode=0 --errorRate=0 --nVehicles=0 --droneTest=0 --highBuildings=0 --flooding=0  --printToFile=1 --printCoords=0 --createObstacleShadowingLossFile=0 --useObstacleShadowingLossFile=1 --forgedCoordTest=0 --forgedCoordRate=0 --maxRun=1"

### Setup Singularity container path
CONTAINER_PATH="$PROJECT_PATH/singularity-ns3-image.sif"

echo "Starting NS3 simulation at $(date) with RngRun=${SLURM_ARRAY_TASK_ID}"

### Run the NS3 simulation using the runner script inside Singularity
singularity exec \
  --bind $PROJECT_PATH:/mnt \
  $CONTAINER_PATH \
  /mnt/run-simulation-slurm-helper.sh \
  "$REPO_PATH" \
  "fb-vanet-urban/$SIMULATION_CMD" \
  "${SLURM_ARRAY_TASK_ID}"

EXIT_CODE=$?

echo "Simulation completed at $(date) with exit code: $EXIT_CODE"

exit $EXIT_CODE
