#!/bin/bash -l
### job name
#SBATCH --job-name={**jobName}

### Email notification
###SBATCH --mail-user=youremailaddress@youremail.com
###SBATCH --mail-type=FAIL

#SBATCH --array=1-1

### Standard output and standard error for our job
#SBATCH --error=./logs/%x_id_%A_run_%a.err
#SBATCH --output=./logs/%x_id_%A_run_%a.out

### queue/partition choosed
#SBATCH --partition=allgroups

### Number of tasks
#SBATCH --ntasks=1

### RAM requirement
#SBATCH --mem=1G

### Time limit for our job (ten minutes here: HH:MM:SS)
#SBATCH --time={**neededTime}

### GPU request
###SBATCH --gres=gpu
####SBATCH --constraint=A6000

### Some useful informative commands
echo -n 'Date: '
date
echo -n 'Directory: '
pwd
echo -n 'This job will be executed on th following nodes: '
echo ${SLURM_NODELIST}
echo

SHELL=/bin/bash

### Find the actual project root
CURRENT_DIR="$(pwd)"
PROJECT_PATH=""
while [[ "$CURRENT_DIR" != "/" ]]; do
 if [[ -d "$CURRENT_DIR/ns-3" ]] && [[ -d "$CURRENT_DIR/simulations" ]]; then
     PROJECT_PATH="$CURRENT_DIR"
     break
 fi
 CURRENT_DIR="$(dirname "$CURRENT_DIR")"
done

if [[ -z "$PROJECT_PATH" ]]; then
 echo "ERROR: Could not find project root (looking for $IMAGE_NAME and ns-3/)"
 echo "Searched from: $(pwd)"
 exit 1
fi


### Jobs execution commands
conda info --envs
source /conf/shared-software/anaconda/etc/profile.d/conda.sh
conda activate generate_graphs
which python3
python3 --version
python3 $PROJECT_PATH/scripts/drawCoords/{**script}.py \
    -b $PROJECT_PATH/simulations/scenario-urbano-con-coord/{**scenario} \
    --mapfolder $PROJECT_PATH/maps \
    --maxfiles 100 \
    -o $PROJECT_PATH/scripts/drawCoords/out \
    {**Additional_args}
