#!/bin/bash
# ns3_singularity.sh - Simple script to build and run NS-3 simulations with Singularity

# Function to display usage information
show_usage() {
    echo "Usage:"
    echo "  $0 build [debug|release|optimized]"
    echo "  $0 dirty-build [debug|release|optimized]"
    echo "  $0 shell"
    echo "  LOG_LEVEL=[error|warn|info|debug|function|logic] $0 run <simulation_command_file> [rng_run_value]"
    echo ""
    echo "Commands:"
    echo "  build         - Configure, clean, and build NS-3"
    echo "  dirty-build   - Configure and build NS-3 without cleaning"
    echo "  shell         - Open a shell in the Singularity environment"
    echo "  run           - Run a simulation (no build mode needed)"
    echo ""
    echo "Build Modes (only used with build/dirty-build):"
    echo "  debug         - Default on local machine. Debug build, necessary for NS-logging."
    echo "  release       - Default on Cluster submit hosts. Release build (-d release, no O3). Better on the cluster"
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
    echo "  $0 run sim_cmd.job      # run simulation with default rng"
    echo "  $0 run sim_cmd.job 5    # run simulation with RngRun=5"
    echo "  LOG_LEVEL='info' $0 run sim_cmd.job 5    # run simulation with RngRun=5"
    exit 1
}

# Path to the Singularity image
SIF_IMAGE="singularity-ns3-image.sif" # Singularity image name

# Get absolute path to the folder where THIS script resides
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Then call find_project_root.sh from there
source "$SCRIPT_DIR"/find_project_root.sh
echo "=== Project path is $PROJECT_ROOT"
if [[ -z "$PROJECT_ROOT" ]]; then
    # find_project_root.sh already printed the error
    exit 1
fi

# Setup Singularity container path
ENV_FOLDER="build_env"
CONTAINER_PATH="${PROJECT_ROOT}/${ENV_FOLDER}/container/${SIF_IMAGE}"
NS3_DIR="${PROJECT_ROOT}/ns-3/"
echo "=== ns3_dir: $NS3_DIR"
echo "=== CONTAINER_PATH ${CONTAINER_PATH}"

# Detect environment and set bind path and default building mode accordingly
HOSTNAME=$(hostname)
echo "=== HOSTNAME: $HOSTNAME"
echo "=== NS3_DIR: $NS3_DIR"
if [[ "$HOSTNAME" == labsrv* ]]; then # cluster submit hosts
    DEFAULT_MODE="release"
    # Cluster environment - bind to /mnt
    BIND_PATH="${PROJECT_ROOT}:/mnt"
    WORK_DIR="/mnt/ns-3"
    echo "=== Detected cluster environment (${HOSTNAME}) ==="
else
    DEFAULT_MODE="debug"
    # Local environment - bind to same path
    BIND_PATH="$NS3_DIR:$NS3_DIR"
    WORK_DIR="$NS3_DIR"
    echo "=== Detected local environment (${HOSTNAME}) ==="
fi

# Default flags for Waf
export CXXFLAGS="-Wall -Wsign-compare" # -Wsign-compare is redundant but needed for clangd VSCode extension
export CONFIGURE_OPTIONS=""            # for debug

# Debug components
fb_components=(
    fb-vanet-urban
    FBApplication
    FBHeader
    FBNode
)
roff_components=(
    NBTEntry
    NeighborTable
    PositionRankingKey
    PositionRankingMap
    ROFFApplication
    ROFFHeader
    ROFFNode
    roff-test
)
LOG_LEVEL="${LOG_LEVEL:-warn}"
LOG_FLAGS="|prefix_func|prefix_time"

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
    debug | release | optimized)
        MODE=$1
        shift
        ;;
    esac

    echo "==> Using build mode: $MODE"

    case "$MODE" in
    debug)
        # nothing to do, the default flags apply here
        ;;
    release)
        export CONFIGURE_OPTIONS="${CONFIGURE_OPTIONS} -d release" # faster than debug and works on all hardwares (cluster)
        ;;
    optimized)
        export CXXFLAGS="${CXXFLAGS} -O3" # for hardware specific optimizations, breaks on cluster
        export CONFIGURE_OPTIONS="${CONFIGURE_OPTIONS} -d optimized"
        ;;
    esac
fi
echo "=== CXXFLAGS: ${CXXFLAGS}"
echo "=== CONFIGURE_OPTIONS: ${CONFIGURE_OPTIONS}"

# Handle different commands
case $COMMAND in
build)
    echo "=== Configuring and building NS-3 (clean build) ==="
    singularity exec \
        --bind "$BIND_PATH" \
        "$CONTAINER_PATH" \
        bash -c "cd $WORK_DIR && \
                ./waf configure ${CONFIGURE_OPTIONS} && \
                ./waf clean && \
                ./waf build"
    ;;

dirty-build)
    echo "=== Configuring and building NS-3 (dirty build) ==="
    echo "=== WORK_DIR: $WORK_DIR"
    singularity exec \
        --bind "$BIND_PATH" \
        "$CONTAINER_PATH" \
        bash -c "cd $WORK_DIR && \
                ./waf configure ${CONFIGURE_OPTIONS} && \
                ./waf build"
    ;;

shell)
    echo "=== Opening shell in Singularity container ==="
    # Shell always uses PROJECT_ROOT:/mnt for both environments
    singularity shell --bind "$PROJECT_ROOT:/mnt" \
        "$CONTAINER_PATH"
    ;;

run)
    # Check if simulation command file is provided
    if [ -z "$1" ]; then
        echo "Error: Simulation command file is required for 'run'"
        show_usage
    fi

    # Read simulation command from the file
    if [ ! -f "$1" ]; then
        echo "Error: Simulation command file '$2' does not exist"
        exit 1
    fi

    # Read the file content into SIMULATION_CMD
    SIMULATION_CMD=$(cat "$1")

    # Set RngRun value (default to 1 if not provided)
    RNG_VALUE=${2:-1}
    export NS_GLOBAL_VALUE="RngRun=$RNG_VALUE"
    if [[ "$MODE" == 'debug' ]]; then
        # Extract the first word from SIMULATION_CMD to determine which components to use
        FIRST_WORD=$(echo "$SIMULATION_CMD" | head -n 1 | awk '{print $1}')
        # Select components array based on the first word
        if [[ "$FIRST_WORD" == "fb-vanet-urban" ]]; then
            components=("${fb_components[@]}")
        elif [[ "$FIRST_WORD" == "roff-test" ]]; then
            components=("${roff_components[@]}")
        fi

        # Build NS_LOG string by joining with colon
        NS_LOG=""
        for comp in "${components[@]}"; do
            if [[ -z "$NS_LOG" ]]; then
                NS_LOG="${comp}=${LOG_LEVEL}${LOG_FLAGS}"
            else
                NS_LOG="${NS_LOG}:${comp}=${LOG_LEVEL}${LOG_FLAGS}"
            fi
        done
        export NS_LOG

        echo "=== NS_LOG is set to:"
        echo "$=== NS_LOG"
    fi
    echo "=== Running simulation from file: $1"
    echo "=== Command: $SIMULATION_CMD"
    echo "=== Using RngRun=$RNG_VALUE"

    singularity exec \
        --bind "$BIND_PATH" \
        "$CONTAINER_PATH" \
        bash -c "cd $WORK_DIR && ./waf --run \"${SIMULATION_CMD}\""
    ;;

*)
    echo "Error: Unknown command '$COMMAND'"
    show_usage
    ;;
esac

echo "Done!"
