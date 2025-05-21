#!/bin/bash
# ns3_singularity.sh - Simple script to build and run NS-3 simulations with Singularity
# This mimics the behavior of your docker-compose.yml file commands

# Path to your Singularity image
SIF_IMAGE="../singularity-ns3-image.sif"  # Singularity image name

# Environment variables (same as in your docker-compose)
export CXXFLAGS="-Wall -O3"
export CONFIGURE_OPTIONS="-d optimized"

# Directory containing your NS-3 installation - this is the actual directory, not a mount
NS3_DIR="$(pwd)"  # Update this to your NS-3 directory path

# Function to display usage information
show_usage() {
    echo "Usage: $0 [build|dirty-build|shell|run] [simulation_command_file] [rng_run_value]"
    echo ""
    echo "Commands:"
    echo "  build         - Configure, clean, and build NS-3 (equivalent to docker-compose build)"
    echo "  dirty-build   - Configure and build NS-3 without cleaning"
    echo "  shell         - Open a shell in the Singularity environment"
    echo "  run           - Run a simulation (requires simulation_command_file argument)"
    echo ""
    echo "Arguments:"
    echo "  simulation_command_file - File containing the NS-3 simulation command to run (required for 'run')"
    echo "  rng_run_value           - Optional RngRun value (default: RngRun=1)"
    echo ""
    echo "Examples:"
    echo "  $0 build"
    echo "  $0 dirty-build"
    echo "  $0 shell"
    echo "  $0 run simulation_cmd.txt"
    echo "  $0 run simulation_cmd.txt 5"
    exit 1
}

# Check for command argument
if [ $# -lt 1 ]; then
    show_usage
fi

COMMAND=$1

# Handle different commands
case $COMMAND in
    build)
        echo "=== Configuring and building NS-3 (clean build) ==="
        singularity exec --bind $NS3_DIR:$NS3_DIR $SIF_IMAGE \
            bash -c "cd $NS3_DIR && \
                ./waf configure ${CONFIGURE_OPTIONS} && \
                ./waf clean && \
                ./waf build"
        ;;

    dirty-build)
        echo "=== Configuring and building NS-3 (dirty build) ==="
        singularity exec --bind $NS3_DIR:$NS3_DIR $SIF_IMAGE \
            bash -c "cd $NS3_DIR && \
                ./waf configure ${CONFIGURE_OPTIONS} && \
                ./waf build"
        ;;

    shell)
        echo "=== Opening shell in Singularity container ==="
        singularity shell --bind $NS3_DIR:$NS3_DIR $SIF_IMAGE
        ;;

    run)
        # Check if simulation command file is provided
        if [ -z "$2" ]; then
            echo "Error: Simulation command file is required for 'run'"
            show_usage
        fi

        # Read simulation command from the file
        if [ ! -f "$2" ]; then
            echo "Error: Simulation command file '$2' does not exist"
            exit 1
        fi

        # Read the file content into SIMULATION_CMD
        SIMULATION_CMD=$(cat "$2")

        # Set RngRun value (default to 1 if not provided)
        RNG_VALUE=${3:-1}
        export NS_GLOBAL_VALUE="RngRun=$RNG_VALUE"
        export NS_LOG="*=warn|prefix_func|prefix_time"

        echo "=== Running simulation from file: $2 ==="
        echo "=== Command: $SIMULATION_CMD ==="
        echo "=== Using $RNG_RUN ==="

        # Bind the actual NS-3 directory and run the simulation
        singularity exec --bind $NS3_DIR:$NS3_DIR $SIF_IMAGE \
            bash -c "cd $NS3_DIR && ./waf --run \"${SIMULATION_CMD}\""
        ;;

    *)
        echo "Error: Unknown command '$COMMAND'"
        show_usage
        ;;
esac

echo "Done!"
