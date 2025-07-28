#!/bin/bash
# This script runs an NS-3 simulation from within a Singularity container.
# It uses the precompiled simulation binary directly (not waf), 
# which is needed for cluster execution.

NS3_DIR="$1"
SIMULATION_CMD="$2"
RNG_RUN="$3"

# Set environment variables inside the container
export NS_GLOBAL_VALUE="RngRun=${RNG_RUN}"
export NS_LOG="*=warn|prefix_func|prefix_time"

# Set up NS3 environment variables inside the container
export NS3_EXECUTABLE_PATH=${NS3_DIR}/build/src/fd-net-device:${NS3_DIR}/build/src/tap-bridge
export NS3_MODULE_PATH=${NS3_DIR}/build
export PATH=${NS3_DIR}/build/src/fd-net-device:${NS3_DIR}/build/src/tap-bridge:${NS3_DIR}:${PATH}
export LD_LIBRARY_PATH=${NS3_DIR}/build/lib:${NS3_DIR}/build:${LD_LIBRARY_PATH}

echo ""
echo "=== Container Environment ==="
echo "NS3_DIR: $NS3_DIR"
echo "SIMULATION_CMD: $SIMULATION_CMD"
echo "RNG_RUN: $RNG_RUN"
echo "NS_GLOBAL_VALUE: $NS_GLOBAL_VALUE"
echo "NS3_EXECUTABLE_PATH: $NS3_EXECUTABLE_PATH"
echo "NS3_MODULE_PATH: $NS3_MODULE_PATH"
echo "Current directory: $(pwd)"
echo "Container hostname: $(hostname)"
echo "Container distribution: $(cat /etc/os-release | grep PRETTY_NAME)"
echo "TZ is: $TZ"
echo "========================"
echo ""

# Change to NS-3 directory and run the simulation
cd ${NS3_DIR}
echo "Changed directory to: $(pwd)"
echo "Running: ./build/scratch/${SIMULATION_CMD}"
echo "Start time: $(date)"

# Run the command and capture its output to the log file
if [ -n "$LOG_FILE" ]; then
    ./build/scratch/${SIMULATION_CMD}
else
    ./build/scratch/${SIMULATION_CMD}
fi

EXIT_CODE=$?
echo "End time: $(date)"
echo "Command exit code: $EXIT_CODE"
