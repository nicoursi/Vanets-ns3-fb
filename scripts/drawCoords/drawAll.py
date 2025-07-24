#!/usr/bin/python3

"""
Enhanced drawAll.py script that supports all parameters from the individual drawing scripts
and passes them to all four scripts running in parallel.

Usage examples:
    ./drawAll.py -f data.csv -m mobility.xml -p poly.xml -r 500 -o ./output --dpi 150 -v
    ./drawAll.py -b /path/to/data --mapfolder /path/to/maps -r 1000 --maxfiles 5
"""

import os
import sys
import argparse
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import csv
import xml.etree.ElementTree as ET
import coordUtils as coordUtils
from multiprocessing import Pool

def run_process(process):
    """Execute a single drawing script with given arguments"""
    print(f"Running: {process}")
    os.system(f'python {process}')

def build_argument_string(args):
    """Build argument string from parsed arguments"""
    arg_parts = []

    # File processing group (one is mandatory)
    if args.file:
        arg_parts.extend(['-f', args.file])
    elif args.basefolder:
        arg_parts.extend(['-b', args.basefolder])

    # Mobility source group (one is mandatory)
    if args.mobility:
        arg_parts.extend(['-m', args.mobility])
    elif args.mapfolder:
        arg_parts.extend(['--mapfolder', args.mapfolder])

    # Optional arguments
    if args.poly:
        arg_parts.extend(['-p', args.poly])

    # Optional parameters with defaults (only add if different from default)
    if args.radius != 1000:
        arg_parts.extend(['-r', str(args.radius)])

    if args.output != './out':
        arg_parts.extend(['-o', args.output])

    if args.maxfiles != 3:
        arg_parts.extend(['--maxfiles', str(args.maxfiles)])

    if args.dpi != 300:
        arg_parts.extend(['--dpi', str(args.dpi)])

    # Boolean flags
    if args.verbose:
        arg_parts.append('-v')

    return ' '.join(arg_parts)

def setup_common_argument_parser(description="Simulation analysis tool"):
    """
    Create an argument parser with common parameters used by multiple scripts.
    Implements mandatory argument groups as specified.

    Args:
        description (str): Description for the argument parser

    Returns:
        argparse.ArgumentParser: Configured argument parser
    """
    parser = argparse.ArgumentParser(description=description,
                                   formatter_class=argparse.RawDescriptionHelpFormatter)

    # Create mutually exclusive group for file processing options (one is mandatory)
    file_group = parser.add_mutually_exclusive_group(required=True)
    file_group.add_argument('-f', '--file',
                           help='Single CSV file to process')
    file_group.add_argument('-b', '--basefolder',
                           help='Base folder for batch processing')

    # Create mutually exclusive group for mobility source (one is mandatory)
    mobility_group = parser.add_mutually_exclusive_group(required=True)
    mobility_group.add_argument('-m', '--mobility',
                               help='NS2 mobility file path')
    mobility_group.add_argument('--mapfolder',
                               help='Base map folder containing scenario subdirectories')

    # Optional arguments
    parser.add_argument('-p', '--poly',
                       help='Polygon/building file path (optional)')
    parser.add_argument('-r', '--radius', type=int, default=1000,
                       help='Transmission radius in meters (default: 1000)')
    parser.add_argument('-o', '--output', default='./out',
                       help='Output base directory (default: ./out)')
    parser.add_argument('--maxfiles', type=int, default=3,
                       help='Maximum files to process per protocol (default: 3)')
    parser.add_argument('--dpi', type=int, default=300,
                       help='DPI for output images (default: 300)')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Enable verbose output')

    return parser

def main():
    # Set up argument parser using the common function
    parser = setup_common_argument_parser(
        'Run all drawing scripts in parallel with unified parameter support'
    )

    # Add epilog with examples
    parser.epilog = """
Examples:
  ./drawAll.py -f data.csv -m mobility.xml -p poly.xml
  ./drawAll.py -b /data/folder --mapfolder /maps -r 500 -v
  ./drawAll.py -f data.csv -m mobility.xml -o ./results --dpi 150
        """

    # Parse arguments
    args = parser.parse_args()

    # Build argument string for all scripts
    script_args = build_argument_string(args)

    if args.verbose:
        print(f"Arguments to pass to scripts: {script_args}")
        print("Starting parallel execution of drawing scripts...")

    # Define the four drawing scripts with arguments
    processes = [
        f"./drawCoverage.py {script_args}",
        f"./drawAlertPaths.py {script_args}",
        f"./drawSingleHops.py {script_args}",
        f"./drawMultipleTransmissions.py {script_args}",
    ]

    if args.verbose:
        print("Scripts to execute:")
        for i, process in enumerate(processes, 1):
            print(f"  {i}. {process}")
        print()

    # Execute scripts in parallel
    try:
        pool = Pool(processes=4)
        pool.map(run_process, processes)
        pool.close()
        pool.join()

        if args.verbose:
            print("All drawing scripts completed successfully!")

    except KeyboardInterrupt:
        print("\nExecution interrupted by user")
        pool.terminate()
        pool.join()
        sys.exit(1)
    except Exception as e:
        print(f"Error during execution: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
