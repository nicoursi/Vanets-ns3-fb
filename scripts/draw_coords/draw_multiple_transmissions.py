#!/usr/bin/env python3
# coding=utf-8
"""
Draw Multiple Transmissions Visualization Tool

This script generates multiple transmission phase plots from simulation data,
showing how alert messages propagate through the network in sequential phases.

Usage:
    ./draw_multiple_transmissions.py [options]

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
    ./draw_multiple_transmissions.py -f data.csv -m mobility.ns2 -p buildings.xml -r 1000

    # Process single file with map folder (auto-detects scenario)
    ./draw_multiple_transmissions.py -f /path/to/Padova-25/b0/e0/r100/j0/cw32-1024/Fast-Broadcast/data.csv --mapfolder /path/to/maps

    # Batch process folder
    ./draw_multiple_transmissions.py -b /path/to/basefolder --mapfolder /path/to/maps -r 1500
"""

import os
import matplotlib

matplotlib.use("Agg")  # Use non-interactive backend
import matplotlib.pyplot as plt
import coord_utils as coord_utils


# Set high DPI for better quality figures
plt.rcParams["figure.figsize"] = [10, 10]
plt.rcParams["figure.dpi"] = 300
plt.rcParams["savefig.dpi"] = 300
plt.rcParams["savefig.bbox"] = "tight"

# Default values
DEFAULT_BASE_MAP_FOLDER = "../../../maps"  # If you execute the script in its folder


def create_ordered_sources_list(transmission_vector):
    """Create an ordered list of sources from the transmission vector."""
    ordered_sources_list = []
    for edge in transmission_vector:
        source = edge.source
        if source not in ordered_sources_list:
            ordered_sources_list.append(source)
    return ordered_sources_list


def plot_multiple_transmissions(csv_file_path, output_file_path, config):
    """
    Plot multiple transmission phases for a single simulation.

    Args:
        csv_file_path (str): Path to CSV file containing simulation results
        output_file_path (str): Base path where to save the output plots (will append phase numbers)
        config (SimulationConfig): Configuration object with mobility and poly files
    """
    print(f"Plotting multiple transmissions for: {csv_file_path}")

    # Validate required files
    if not config.mobility_file or not os.path.exists(config.mobility_file):
        print(f"Error: Mobility file not found: {config.mobility_file}")
        return False

    # Parse simulation data
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

    # Calculate coordinate bounds
    coord_bounds = coord_utils.calculate_coord_bounds(
        x_node_coords, y_node_coords, starting_x, starting_y, config.circ_radius
    )

    node_coords_map = {}
    color1 = "#840000"

    ordered_sources_list = create_ordered_sources_list(transmission_vector)

    if not ordered_sources_list:
        print("No transmission sources found in the data")
        return False

    success_count = 0

    for count, ordered_source in enumerate(ordered_sources_list, 1):
        print(f"Processing transmission phase {count}/{len(ordered_sources_list)}")

        # Create new figure for each transmission phase
        fig, ax = plt.subplots(figsize=(10, 10))

        # Set equal aspect ratio to keep circles circular
        ax.set_aspect("equal", adjustable="box")

        # Plot all nodes (not reached by alert message)
        ax.plot(
            x_node_coords,
            y_node_coords,
            ".",
            markersize=5,
            color="#A00000",
            label="Not reached by Alert Message",
        )

        # Plot transmission range circle
        coord_utils.plot_tx_range(
            config.circ_radius, starting_x, starting_y, vehicle_distance, color1, True, coord_bounds
        )

        # Plot transmission edges
        for edge in transmission_vector:
            if edge.source not in ordered_sources_list[0:count]:
                continue

            line_color = "0.8"
            source_color = "#560589"
            forwarder_label = "Previous forwarder"

            if edge.source == ordered_source:
                line_color = "0.35"
                source_color = "#bf59ff"
                forwarder_label = "Latest forwarder"

            source = edge.source
            destination = edge.destination

            # Cache coordinate lookups
            if source not in node_coords_map:
                node_coords_map[source] = coord_utils.find_coords_from_file(
                    source, config.mobility_file
                )
            if destination not in node_coords_map:
                node_coords_map[destination] = coord_utils.find_coords_from_file(
                    destination, config.mobility_file
                )

            source_coord = node_coords_map[source]
            dest_coord = node_coords_map[destination]

            # Plot destination (reached by alert message)
            ax.plot(
                dest_coord.x,
                dest_coord.y,
                ".",
                color="#32DC32",
                markersize=5,
                label="Reached by Alert Message",
            )

            # Plot source (forwarder)
            ax.plot(
                source_coord.x,
                source_coord.y,
                "o",
                color=source_color,
                markersize=5,
                label=forwarder_label,
            )

            # Plot transmission line
            ax.plot(
                [source_coord.x, dest_coord.x],
                [source_coord.y, dest_coord.y],
                color=line_color,
                linewidth=0.3,
                alpha=0.7,
            )

        # Plot starting node (source of alert message)
        ax.plot(
            starting_x,
            starting_y,
            "o",
            color="yellow",
            markeredgecolor="blue",
            markersize=8,
            markeredgewidth=2,
            label="Source of Alert Message",
        )

        # Plot transmission range again (to ensure it's on top)
        coord_utils.plot_tx_range(
            config.circ_radius, starting_x, starting_y, vehicle_distance, color1, True, coord_bounds
        )

        # Plot buildings if provided
        if config.poly_file and os.path.exists(config.poly_file):
            coord_utils.plot_buildings(config.poly_file)

        # Set coordinate bounds
        ax.set_xlim(coord_bounds[0], coord_bounds[1])
        ax.set_ylim(coord_bounds[2], coord_bounds[3])

        # Add legend with unique labels only
        handles, labels = ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        ax.legend(by_label.values(), by_label.keys(), loc="upper right", framealpha=0.9, fontsize=8)

        # Add grid and labels
        ax.grid(True, alpha=0.3)
        ax.set_xlabel("X Coordinate (m)", fontsize=12)
        ax.set_ylabel("Y Coordinate (m)", fontsize=12)
        ax.set_title(f"Transmission Phase {count} (Radius: {config.circ_radius}m)", fontsize=14)

        # Generate output file path for this phase
        output_base = os.path.splitext(output_file_path)[0]
        phase_output_file = f"{output_base}-phase-{count:02d}.png"

        # Ensure output directory exists
        if not coord_utils.ensure_output_directory(phase_output_file):
            plt.close()
            continue

        # Save figure
        try:
            plt.savefig(phase_output_file, dpi=config.dpi, bbox_inches=config.bbox_inches)
            print(f"Saved phase {count}: {phase_output_file}")
            success_count += 1
        except Exception as e:
            print(f"Error saving phase {count} to {phase_output_file}: {e}")
        finally:
            plt.close()

    return success_count > 0


def main():
    """Main function to handle command line arguments and execute appropriate actions."""

    # Script-specific configuration
    script_config = {
        "description": "Draw Multiple Transmissions Visualization Tool",
        "tool_name": "Draw Multiple Transmissions Tool",
        "output_subfolder": "multipleTransmissions",
        "single_output_subfolder": "singlefileMultipleTransmission",
        "default_base_map_folder": DEFAULT_BASE_MAP_FOLDER,
        "plot_function": plot_multiple_transmissions,
    }

    # Use coord_utils generic main function
    coord_utils.generic_main(script_config)


if __name__ == "__main__":
    main()
