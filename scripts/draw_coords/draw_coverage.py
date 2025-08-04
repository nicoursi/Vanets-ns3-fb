#!/usr/bin/env python3
"""Draw Coverage Visualization Tool

This script generates coverage visualization plots from simulation data.

Usage:
    ./draw_coverage.py [options]

Options:
    -h, --help                  Show this help message and exit
    -f, --file FILE             Single CSV file to process
    -m, --mobility FILE         NS2 mobility file path
    -p, --poly FILE             Polygon/building file path (optional)
    --mapfolder PATH            Base map folder containing scenario subdirectories
    -b, --basefolder PATH       Base folder for batch processing
    -r, --radius RADIUS         Transmission radius in meters (default: 1000)
    -o, --output PATH           Output base directory (default: ./out)
    --maxfiles INT              Maximum files to process per protocol (default: 3)
    --dpi INT                   DPI for output images (default: 300)
    -v, --verbose               Enable verbose output

Examples:
    # Process single file with explicit mobility and poly files
    ./draw_coverage.py -f data.csv -m mobility.ns2 -p buildings.xml -r 1000

    # Process single file with map folder (auto-detects scenario)
    ./draw_coverage.py -f /path/to/Padova-25/b0/e0/r100/j0/cw32-1024/Fast-Broadcast/data.csv --mapfolder /path/to/maps

    # Batch process folder
    ./draw_coverage.py -b /path/to/basefolder --mapfolder /path/to/maps -r 1500

"""

import os

import matplotlib

matplotlib.use("Agg")  # Use non-interactive backend
import coord_utils
import matplotlib.pyplot as plt

# Set high DPI for better quality figures
plt.rcParams["figure.figsize"] = [10, 10]
plt.rcParams["figure.dpi"] = 300
plt.rcParams["savefig.dpi"] = 300
plt.rcParams["savefig.bbox"] = "tight"

# Default values
DEFAULT_BASE_MAP_FOLDER = "../../../maps"  # If you execute the script in its folder


def plot_coverage(csv_file_path, output_file_path, config) -> bool:
    """Plot coverage visualization from simulation data.

    Args:
        csv_file_path (str): Path to CSV file containing simulation results
        output_file_path (str): Path where to save the output plot
        config (SimulationConfig): Configuration object with mobility and poly files

    """
    print(f"Plotting coverage for: {csv_file_path}")

    # Validate required files
    if not config.mobility_file or not os.path.exists(config.mobility_file):
        print(f"Error: Mobility file not found: {config.mobility_file}")
        return False

    # Parse the CSV file
    try:
        (
            tx_range,
            starting_x,
            starting_y,
            starting_vehicle,
            vehicle_distance,
            x_received_coords,
            y_received_coords,
            x_node_coords,
            y_node_coords,
            transmission_map,
            received_coords_on_circ,
            received_on_circ_ids,
            transmission_vector,
            node_ids,
        ) = coord_utils.parse_file(csv_file_path, config.mobility_file)
    except Exception as e:
        print(f"Error parsing file {csv_file_path}: {e}")
        return False

    # Calculate coordinate bounds for proper scaling
    coord_bounds = coord_utils.calculate_coord_bounds(
        x_node_coords, y_node_coords, starting_x, starting_y, config.circ_radius,
    )

    # Create the plot
    plt.figure(figsize=(10, 10))

    # Plot nodes not reached by alert message
    plt.plot(
        x_node_coords,
        y_node_coords,
        ".",
        markersize=5,
        color="#A00000",
        label="Not reached by Alert Message",
    )

    # Plot nodes reached by alert message
    plt.plot(
        x_received_coords,
        y_received_coords,
        ".",
        markersize=5,
        color="#32DC32",
        label="Reached by Alert Message",
    )

    # Plot source of alert message
    plt.plot(
        starting_x,
        starting_y,
        "o",
        color="yellow",
        markersize=8,
        markeredgecolor="blue",
        markeredgewidth=2,
        label="Source of Alert Message",
    )

    # Add legend in top right
    plt.legend(loc="upper right", framealpha=1.0, fontsize=10)

    # Plot transmission range with proper bounds
    coord_utils.plot_tx_range(
        config.circ_radius,
        starting_x,
        starting_y,
        vehicle_distance,
        color="black",
        plot_interval=True,
        coord_bounds=coord_bounds,
    )

    # Plot buildings if polygon file is provided and exists
    if config.poly_file and os.path.exists(config.poly_file):
        coord_utils.plot_buildings(config.poly_file)

    # Set axis limits based on calculated bounds
    plt.xlim(coord_bounds[0], coord_bounds[1])
    plt.ylim(coord_bounds[2], coord_bounds[3])

    # Set equal aspect ratio to keep circles circular
    plt.gca().set_aspect("equal", adjustable="box")

    # Add grid and labels
    plt.grid(True, alpha=0.3)
    plt.xlabel("X Coordinate (m)", fontsize=12)
    plt.ylabel("Y Coordinate (m)", fontsize=12)
    plt.title(f"Alert Message Coverage (Radius: {config.circ_radius}m)", fontsize=14)

    # Ensure output directory exists
    if not coord_utils.ensure_output_directory(output_file_path):
        return False

    # Save the figure
    try:
        plt.savefig(output_file_path, dpi=config.dpi, bbox_inches=config.bbox_inches)
        print(f"Coverage plot saved to: {output_file_path}")
    except Exception as e:
        print(f"Error saving plot to {output_file_path}: {e}")
        return False
    finally:
        plt.close()  # Clean up to prevent memory leaks

    return True


def main():
    """Main function to handle command line arguments and execute appropriate actions."""
    # Script-specific configuration
    script_config = {
        "description": "Draw Coverage Visualization Tool",
        "tool_name": "Draw Coverage Tool",
        "output_subfolder": "coverages",
        "single_output_subfolder": "single_file_coverage",
        "default_base_map_folder": DEFAULT_BASE_MAP_FOLDER,
        "plot_function": plot_coverage,
        #        'additional_args': [
        #            {
        #                'name': '--output-single',
        #                'help': 'Output file path for single file mode'
        #            }
        #        ]
    }

    # Use coord_utils generic main function
    coord_utils.generic_main(script_config)


if __name__ == "__main__":
    main()
