#!/bin/bash
# ns3_singularity.sh - Simple script to build and run NS-3 simulations with Singularity

# Path to your Singularity image
SIF_IMAGE="singularity-ns3-image.sif"  # Singularity image name

# Default mode
DEFAULT_MODE="release" # default

# Environment variables (same as in your docker-compose)
# export CXXFLAGS="-Wall -O3" #for hardware specific optimizations
export CXXFLAGS="-Wall"
# export CONFIGURE_OPTIONS="-d optimized"
export CONFIGURE_OPTIONS="" # for debug

### Find the Directory containing the NS-3 installation - this is the actual directory, not a mount
# Get absolute path to the folder where THIS script resides
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Then call find_project_root.sh from there
source $SCRIPT_DIR/find_project_root.sh
status=$?
echo "Project path is $PROJECT_ROOT"
if [[ -z "$PROJECT_ROOT" ]]; then
    # find_project_root.sh already printed the error
    exit 1
fi


# Setup Singularity container path
ENV_FOLDER="build-env"
CONTAINER_PATH="${PROJECT_ROOT}/${ENV_FOLDER}/${SIF_IMAGE}"
NS3_DIR="${PROJECT_ROOT}/ns-3/"
echo "ns3_dir: $NS3_DIR"
echo "CONTAINER_PATH ${CONTAINER_PATH}"

# Function to display usage information
show_usage() {
    echo "Usage:"
    echo "  $0 build [debug|release|optimized]"
    echo "  $0 dirty-build [debug|release|optimized]"
    echo "  $0 shell"
    echo "  $0 run <simulation_command_file> [rng_run_value]"
    echo ""
    echo "Commands:"
    echo "  build         - Configure, clean, and build NS-3"
    echo "  dirty-build   - Configure and build NS-3 without cleaning"
    echo "  shell         - Open a shell in the Singularity environment"
    echo "  run           - Run a simulation (no build mode needed)"
    echo ""
    echo "Build Modes (only used with build/dirty-build):"
    echo "  debug         - Default. Debug build, necessary for NS-logging."
    echo "  release       - Release build (-d release, no O3). Better on the cluster"
    echo "  optimized     - Optimized build (-d optimized, adds -O3)."
    echo ""
    echo "Run Arguments:"
    echo "  simulation_command_file - File containing the NS-3 simulation command."
    echo "  rng_run_value           - Optional RngRun value (default: 1)."
    echo ""
    echo "Examples:"
    echo "  $0 build                # build with debug"
    echo "  $0 build release        # build with release settings"
    echo "  $0 dirty-build optimized # build without cleaning with optimized settings"
    echo "  $0 run sim_cmd.txt      # run simulation with default rng"
    echo "  $0 run sim_cmd.txt 5    # run simulation with RngRun=5"
    exit 1
}

# Check for command argument
if [ $# -lt 1 ]; then
    show_usage
fi

COMMAND=$1
shift # drop the command

MODE=$DEFAULT_MODE

if [[ "$COMMAND" == "build" || "$COMMAND" == "dirty-build" ]]; then
    # check if user gave a mode
    case "$1" in
      debug|release|optimized)
        MODE=$1
        shift
        ;;
    esac

    echo "==> Using build mode: $MODE"

    case "$MODE" in
      debug)
        export CXXFLAGS="-Wall"
        export CONFIGURE_OPTIONS=""
        ;;
      release)
        export CXXFLAGS="-Wall"
        export CONFIGURE_OPTIONS="-d release"
        ;;
      optimized)
        export CXXFLAGS="-Wall -O3"
        export CONFIGURE_OPTIONS="-d optimized"
        ;;
    esac
fi

# Handle different commands
case $COMMAND in
    build)
        echo "=== Configuring and building NS-3 (clean build) ==="
       	singularity exec \
            --bind $NS3_DIR:/mnt \
            $CONTAINER_PATH \
            bash -c "cd /mnt/ && \
                ./waf configure ${CONFIGURE_OPTIONS} && \
                ./waf clean && \
                ./waf build"
        ;;

    dirty-build)
        echo "=== Configuring and building NS-3 (dirty build) ==="
	singularity exec \
        --bind $NS3_DIR:/mnt \
        $CONTAINER_PATH \
            bash -c "cd /mnt/ && \
                ./waf configure ${CONFIGURE_OPTIONS} && \
                ./waf build"
        ;;

    shell)
        echo "=== Opening shell in Singularity container ==="
        singularity shell --bind $PROJECT_ROOT:/mnt \
        $CONTAINER_PATH \
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
        singularity exec \
            --bind $NS3_DIR:/mnt \
            $CONTAINER_PATH \
            bash -c "cd /mnt && ./waf --run \"${SIMULATION_CMD}\""
        ;;

    *)
        echo "Error: Unknown command '$COMMAND'"
        show_usage
        ;;
esac

echo "Done!"
