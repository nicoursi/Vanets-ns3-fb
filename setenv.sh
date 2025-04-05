#!/bin/bash

# Set relative paths to libraries
LIBS_BASE_PATH="/home/nicola/tesi/libraries/libs/linker"
REPO_PATH="/home/nicola/tesi/submodule-exp/ns-3"

export NS3_EXECUTABLE_PATH=$REPO_PATH/build/src/fd-net-device:$REPO_PATH/build/src/tap-bridge

export NS3_MODULE_PATH=$REPO_PATH/build

# Set custom library paths for each library
export LD_LIBRARY_PATH=$LIBS_BASE_PATH/boost_1_54_0/lib:$LIBS_BASE_PATH/boost_1_65_1/lib:$LIBS_BASE_PATH/boost_1_67_0/lib:$LIBS_BASE_PATH/CGAL_4_11/lib:$LIBS_BASE_PATH/gmp_6_1_2/lib:$LIBS_BASE_PATH/mpfr_4_0_1/lib:$REPO_PATH/build/lib:$REPO_PATH/build:$LD_LIBRARY_PATH

export PATH=$REPO_PATH/build/src/fd-net-device:$REPO_PATH/build/src/tap-bridge:$REPO_PATH:$PATH

# activate conda environment
 conda activate ns3.26-env
