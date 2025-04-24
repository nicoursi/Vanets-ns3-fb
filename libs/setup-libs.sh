#!/bin/bash
set -e

# Paths to compiled libraries
export CGAL_DIR="/my-project/libs/CGAL_4_13"
BOOST_DIR="/my-project/libs/boost_1_54_0"

echo "Installing Boost 1.54.0 and CGAL 4.13 from local directories..."

# Install   libs
echo "Installing Boost 1.54.0 libraries..."
#mkdir -p /usr/local/boost_1_54_0/include
mkdir -p /usr/local/boost_1_54_0/lib

#cp -r $BOOST_DIR/include/* /usr/local/boost_1_54_0/include/
cp -r $BOOST_DIR/lib/* /usr/local/boost_1_54_0/lib/

# Install   headers and libs
echo "Installing CGAL 4.13 libraries and headers..."
mkdir -p /usr/local/cgal_4_13/include
mkdir -p /usr/local/cgal_4_13/lib

cp -r $CGAL_DIR/include/* /usr/local/cgal_4_13/include/
cp -r $CGAL_DIR/lib/* /usr/local/cgal_4_13/lib/

# Export paths for later use (like compiling projects depending on these versions)
#export BOOST_ROOT=/usr/local/boost_1_54_0
export CGAL_DIR=/usr/local/cgal_4_13
export CPATH=/usr/local/cgal_4_13/include:/usr/include
export LIBRARY_PATH=/usr/local/cgal_4_13/lib:/usr/lib:/usr/lib/x86_64-linux-gnu/
export LD_LIBRARY_PATH=/usr/local/cgal_4_13/lib:/usr/local/boost_1_54_0/lib


echo "Boost 1.54.0 and CGAL 4.13 correctly linked"
exec "$@"
