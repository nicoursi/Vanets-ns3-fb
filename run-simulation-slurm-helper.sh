#!/bin/bash
# Script to run NS-3 simulations inside a Singularity container
# Save this in your PROJECT_PATH

NS3_DIR="$1"
SIMULATION_CMD="$2"
RNG_RUN="$3"
LOG_FILE="$4"  # Optional log file path

# Function to log messages both to console and log file if provided
log_message() {
    echo "$1"
    if [ -n "$LOG_FILE" ]; then
        echo "$1" >> "$LOG_FILE"
    fi
}

# Set environment variables inside the container
export NS_GLOBAL_VALUE="RngRun=${RNG_RUN}"
export NS_LOG="*=warn|prefix_func|prefix_time"

# Set up NS3 environment variables inside the container
export NS3_EXECUTABLE_PATH=${NS3_DIR}/build/src/fd-net-device:${NS3_DIR}/build/src/tap-bridge
export NS3_MODULE_PATH=${NS3_DIR}/build
export PATH=${NS3_DIR}/build/src/fd-net-device:${NS3_DIR}/build/src/tap-bridge:${NS3_DIR}:${PATH}
export LD_LIBRARY_PATH=${NS3_DIR}/build/lib:${NS3_DIR}/build:${LD_LIBRARY_PATH}

log_message ""
log_message "=== Container Environment ==="
log_message "NS3_DIR: $NS3_DIR"
log_message "SIMULATION_CMD: $SIMULATION_CMD"
log_message "RNG_RUN: $RNG_RUN"
log_message "NS_GLOBAL_VALUE: $NS_GLOBAL_VALUE"
log_message "NS3_EXECUTABLE_PATH: $NS3_EXECUTABLE_PATH"
log_message "NS3_MODULE_PATH: $NS3_MODULE_PATH"
log_message "Current directory: $(pwd)"
log_message "Container hostname: $(hostname)"
log_message "Container distribution: $(cat /etc/os-release | grep PRETTY_NAME)"
log_message "========================"
log_message ""

# Change to NS-3 directory and run the simulation
cd ${NS3_DIR}
log_message "Changed directory to: $(pwd)"
log_message "Running: ./build/scratch/${SIMULATION_CMD}"
log_message "Start time: $(date)"

# Run the command and capture its output to the log file
if [ -n "$LOG_FILE" ]; then
    ./build/scratch/${SIMULATION_CMD} 2>&1 | tee -a "$LOG_FILE"
else
    ./build/scratch/${SIMULATION_CMD}
fi

EXIT_CODE=$?
log_message "End time: $(date)"
log_message "Command exit code: $EXIT_CODE"
