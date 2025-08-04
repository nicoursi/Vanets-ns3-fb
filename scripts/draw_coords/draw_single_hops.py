#!/usr/bin/env python3
"""Draw Single Hops Visualization Tool

This script generates hop-by-hop visualization plots from simulation data.

Usage:
    ./draw_single_hops.py [options]

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
    ./draw_single_hops.py -f data.csv -m mobility.ns2 -p buildings.xml -r 1000

    # Process single file with map folder (auto-detects scenario)
    ./draw_single_hops.py -f /path/to/Padova-25/b0/e0/r100/j0/cw32-1024/Fast-Broadcast/data.csv --mapfolder /path/to/maps

    # Batch process folder
    ./draw_single_hops.py -b /path/to/basefolder --mapfolder /path/to/maps -r 1500

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


def find_max_hop(transmission_vector):
    """Find the maximum hop count in the transmission vector."""
    return max(map(lambda edge: edge.phase, transmission_vector))


def plot_single_hops(csv_file_path, output_file_path, config):
    """Plot hop-by-hop visualization from simulation data.

    Args:
        csv_file_path (str): Path to CSV file containing simulation results
        output_file_path (str): Base path where to save the output plots (hop number will be appended)
        config (SimulationConfig): Configuration object with mobility and poly files

    """
    print(f"Plotting hops for: {csv_file_path}")

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

    # Create node coordinates map for efficient lookups
    node_coords_map = {}

    # Calculate coordinate bounds for proper scaling
    coord_bounds = coord_utils.calculate_coord_bounds(
        x_node_coords, y_node_coords, starting_x, starting_y, config.circ_radius,
    )

    # Find maximum hop count
    max_hop = find_max_hop(transmission_vector)

    success = True

    # Generate a plot for each hop
    for hop in range(max_hop + 1):
        if config.verbose:
            print(f"Processing hop {hop + 1}")

        # Create new figure for this hop
        plt.figure(figsize=(10, 10))

        # Plot nodes not reached by alert message (red dots)
        plt.plot(
            x_node_coords,
            y_node_coords,
            ".",
            markersize=5,
            color="#A00000",
            label="Not reached by Alert Message",
        )

        # Filter transmission vector for current hop and previous hops
        filtered_transmission_vector = list(filter(lambda x: x.phase <= hop, transmission_vector))

        # Keep track of which labels we've already added to avoid duplicates
        reached_label_added = False
        previous_forwarder_label_added = False
        latest_forwarder_label_added = False

        # Process each transmission edge
        for edge in filtered_transmission_vector:
            # Set colors and labels based on hop phase
            line_color = "0.8"
            source_color = "#560589"
            forwarder_label = "Previous forwarder"
            reached_label = "Reached by Alert Message"

            if edge.phase == hop:
                line_color = "0.35"
                source_color = "#bf59ff"
                forwarder_label = "Latest forwarder"

            source = edge.source
            destination = edge.destination

            # Get coordinates with caching
            if source not in node_coords_map:
                node_coords_map[source] = coord_utils.find_coords_from_file(
                    edge.source, config.mobility_file,
                )
            if destination not in node_coords_map:
                node_coords_map[destination] = coord_utils.find_coords_from_file(
                    edge.destination, config.mobility_file,
                )

            source_coord = node_coords_map[source]
            dest_coord = node_coords_map[destination]

            # Skip if coordinates not found
            if source_coord is None or dest_coord is None:
                continue

            # Plot destination node (reached by alert message)
            if not reached_label_added:
                plt.plot(dest_coord.x, dest_coord.y, ".", color="#32DC32", label=reached_label)
                reached_label_added = True
            else:
                plt.plot(dest_coord.x, dest_coord.y, ".", color="#32DC32")

            # Plot source node (forwarder) with appropriate label
            if edge.phase == hop and not latest_forwarder_label_added:
                plt.plot(
                    source_coord.x,
                    source_coord.y,
                    "o",
                    color=source_color,
                    markersize=5,
                    label=forwarder_label,
                )
                latest_forwarder_label_added = True
            elif edge.phase < hop and not previous_forwarder_label_added:
                plt.plot(
                    source_coord.x,
                    source_coord.y,
                    "o",
                    color=source_color,
                    markersize=5,
                    label=forwarder_label,
                )
                previous_forwarder_label_added = True
            else:
                plt.plot(source_coord.x, source_coord.y, "o", color=source_color, markersize=5)

            # Draw transmission line
            plt.plot(
                [source_coord.x, dest_coord.x],
                [source_coord.y, dest_coord.y],
                color=line_color,
                linewidth=0.3,
                alpha=0.7,
            )

        # Plot source of alert message
        plt.plot(
            starting_x,
            starting_y,
            "o",
            color="yellow",
            markeredgecolor="blue",
            markersize=5,
            label="Source of Alert Message",
        )

        # Add legend
        plt.legend(loc="best", framealpha=1.0, fontsize=10)

        # Plot transmission range
        coord_utils.plot_tx_range(
            config.circ_radius,
            starting_x,
            starting_y,
            vehicle_distance,
            color="#840000",
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
        plt.title(
            f"Alert Message Propagation - Hop {hop + 1} (Radius: {config.circ_radius}m)",
            fontsize=14,
        )

        # Generate output file path for this hop
        hop_output_path = f"{output_file_path}-hop{hop + 1}.png"

        # Ensure output directory exists
        if not coord_utils.ensure_output_directory(hop_output_path):
            success = False
            plt.close()
            continue

        # Save the figure
        try:
            plt.savefig(hop_output_path, dpi=config.dpi, bbox_inches=config.bbox_inches)
            if config.verbose:
                print(f"Hop {hop + 1} plot saved to: {hop_output_path}")
        except Exception as e:
            print(f"Error saving hop {hop + 1} plot to {hop_output_path}: {e}")
            success = False
        finally:
            plt.close()  # Clean up to prevent memory leaks

    if success:
        print(f"All hop plots saved with base path: {output_file_path}")

    return success


def main():
    """Main function to handle command line arguments and execute appropriate actions."""
    # Script-specific configuration
    script_config = {
        "description": "Draw Single Hops Visualization Tool",
        "tool_name": "Draw Single Hops Tool",
        "output_subfolder": "hops",
        "single_output_subfolder": "singlefileHops",
        "default_base_map_folder": DEFAULT_BASE_MAP_FOLDER,
        "plot_function": plot_single_hops,
        #        'additional_args': [
        #            {
        #                'name': '--output-single',
        #                'help': 'Output file base path for single file mode (hop number will be appended)'
        #            }
        #        ]
    }

    # Use coord_utils generic main function
    coord_utils.generic_main(script_config)


if __name__ == "__main__":
    main()
