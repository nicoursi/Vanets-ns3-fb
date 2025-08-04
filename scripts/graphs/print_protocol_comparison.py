#!/usr/bin/env python3
import argparse
import sys

from graph_utils import find_project_root
import print_multiple_graphs

# DEFAULT VALUES - MODIFY THESE AS NEEDED
DEFAULT_INITIAL_BASE_PATH = find_project_root() + "/simulations/scenario-urbano"
DEFAULT_OUT_FOLDER = "out"
DEFAULT_SCENARIOS = ["LA-25"]
DEFAULT_BUILDINGS = ["1", "0"]
DEFAULT_ERROR_RATE = "e0"
DEFAULT_TX_RANGES = ["100", "300", "500", "700"]
DEFAULT_PROTOCOLS = [
    "Fast-Broadcast",
    "STATIC-100",
    "STATIC-300",
    "STATIC-500",
    "STATIC-700",
    "ROFF",
]
DEFAULT_CWS = ["cw[32-1024]"]
DEFAULT_JUNCTIONS = ["0"]
DEFAULT_METRICS = ["totCoverage", "covOnCirc", "hops", "slotsWaited", "messageSent"]
DEFAULT_SHOW_LEGEND = False
DEFAULT_FILE_TYPE = "png"


def parse_list_argument(arg_string):
    """Parse comma-separated string into list, handling empty strings."""
    if not arg_string:
        return []
    return [item.strip() for item in arg_string.split(",") if item.strip()]


def parse_arguments():
    """Parse command line arguments with sensible defaults."""
    parser = argparse.ArgumentParser(
        description="Generate protocol comparison graphs for network simulations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s
  %(prog)s -s "Grid-300,LA-25" -b "0,1" -t "300,500,700"
  %(prog)s --scenarios "Padova-25" --protocols "Fast-Broadcast,ROFF" --tx-ranges "100,300,500"
  %(prog)s --initial-base-path "/custom/path" --buildings "1" --junctions "0,1"
        """,
    )

    parser.add_argument(
        "-p",
        "--initial-base-path",
        type=str,
        default=DEFAULT_INITIAL_BASE_PATH,
        help=f"Initial base path for simulation data, where .csv files are located (default: {DEFAULT_INITIAL_BASE_PATH})",
    )

    parser.add_argument(
        "-ft",
        "--file-type",
        type=str,
        default=DEFAULT_FILE_TYPE,
        help=f"File type for the output files (default: {DEFAULT_FILE_TYPE})",
    )

    parser.add_argument(
        "-o",
        "--out-folder",
        type=str,
        default=DEFAULT_OUT_FOLDER,
        help=f"Folder where the output files will be saved (default: {DEFAULT_OUT_FOLDER})",
    )

    parser.add_argument(
        "-s",
        "--scenarios",
        type=parse_list_argument,
        default=DEFAULT_SCENARIOS,
        help=f"Comma-separated list of scenarios (default: {','.join(DEFAULT_SCENARIOS)})",
    )

    parser.add_argument(
        "-b",
        "--buildings",
        type=parse_list_argument,
        default=DEFAULT_BUILDINGS,
        help=f"Comma-separated list of building configurations (default: {','.join(DEFAULT_BUILDINGS)})",
    )

    parser.add_argument(
        "-e",
        "--error-rate",
        type=str,
        default=DEFAULT_ERROR_RATE,
        help=f"Error rate configuration (default: {DEFAULT_ERROR_RATE})",
    )

    parser.add_argument(
        "-tx",
        "--tx-ranges",
        type=parse_list_argument,
        default=DEFAULT_TX_RANGES,
        help=f"Comma-separated list of transmission ranges (default: {','.join(DEFAULT_TX_RANGES)})",
    )

    parser.add_argument(
        "--protocols",
        type=parse_list_argument,
        default=DEFAULT_PROTOCOLS,
        help=f"Comma-separated list of protocols (default: {','.join(DEFAULT_PROTOCOLS)})",
    )

    parser.add_argument(
        "-c",
        "--cws",
        type=parse_list_argument,
        default=DEFAULT_CWS,
        help=f"Comma-separated list of contention window configurations (default: {','.join(DEFAULT_CWS)})",
    )

    parser.add_argument(
        "-j",
        "--junctions",
        type=parse_list_argument,
        default=DEFAULT_JUNCTIONS,
        help=f"Comma-separated list of junction configurations (default: {','.join(DEFAULT_JUNCTIONS)})",
    )

    parser.add_argument(
        "-m",
        "--metrics",
        type=parse_list_argument,
        default=DEFAULT_METRICS,
        help=f"Comma-separated list of metrics to analyze (default: {','.join(DEFAULT_METRICS)})",
    )

    parser.add_argument(
        "-l",
        "--show-legend",
        action="store_true",
        default=DEFAULT_SHOW_LEGEND,
        help=f"Enable legend (default: {DEFAULT_SHOW_LEGEND})",
    )

    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")

    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_arguments()

    if args.verbose:
        print("Configuration:")
        print(f"  Initial base path: {args.initial_base_path}")
        print(f"  Scenarios: {args.scenarios}")
        print(f"  Buildings: {args.buildings}")
        print(f"  Error rate: {args.error_rate}")
        print(f"  TX ranges: {args.tx_ranges}")
        print(f"  Protocols: {args.protocols}")
        print(f"  CWs: {args.cws}")
        print(f"  Junctions: {args.junctions}")
        print(f"  Metrics: {args.metrics}")
        print(f"  Show Legend: {args.show_legend}")
        print(f"  Output file type: {args.file_type}")
        print(f"  Output folder: {args.out_folder}")
        print()

    try:
        # Call the function with parsed parameters
        print_multiple_graphs.print_protocol_comparison(
            initial_base_path=args.initial_base_path,
            scenarios=args.scenarios,
            buildings=args.buildings,
            error_rate=args.error_rate,
            tx_ranges=args.tx_ranges,
            protocols=args.protocols,
            cws=args.cws,
            junctions=args.junctions,
            metrics=args.metrics,
            show_legend=args.show_legend,
            file_type=args.file_type,
            root_out_folder=args.out_folder,
        )

    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
