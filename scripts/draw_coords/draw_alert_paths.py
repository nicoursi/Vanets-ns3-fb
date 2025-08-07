#!/usr/bin/env python3
"""Modified Draw Alert Paths Visualization Tool.

- Now shows arrows from sender to sender for every hop in transmission_map (not just circumference paths)
- Nodes that only receive but never forward are not considered forwarders
- All receivers from the same sender share the same arrow color
- The last sender(s) that lead to circumference nodes still connect with rays as before.
"""

import os

import matplotlib
import numpy as np

matplotlib.use("Agg")
import coord_utils
import matplotlib.pyplot as plt

plt.rcParams["figure.figsize"] = [10, 10]
plt.rcParams["figure.dpi"] = 300
plt.rcParams["savefig.dpi"] = 300
plt.rcParams["savefig.bbox"] = "tight"

DEFAULT_BASE_MAP_FOLDER = "../../../maps"


def find_circumference_candidates(x_coords, y_coords, starting_x, starting_y, node_spacing, config):
    """Find nodes within a specified distance band from the starting position.

    Args:
        x_coords (list or array): X coordinates of nodes
        y_coords (list or array): Y coordinates of nodes
        starting_x (float): X coordinate of source node
        starting_y (float): Y coordinate of source node
        min_distance (float): Minimum distance from source to consider
        max_distance (float): Maximum distance from source to consider
        node_ids (list, optional): List of node IDs corresponding to coordinates

    Returns:
        list of tuples: Coordinates of nodes within the distance band

    """
    min_distance = config.circ_radius - node_spacing
    max_distance = config.circ_radius + node_spacing
    circumference_candidates = []

    for i in range(len(x_coords)):
        node_x = x_coords[i]
        node_y = y_coords[i]
        distance = np.sqrt((node_x - starting_x) ** 2 + (node_y - starting_y) ** 2)

        if min_distance <= distance <= max_distance:
            circumference_candidates.append((node_x, node_y))

    return circumference_candidates


def plot_alert_paths(csv_file_path, output_file_path, config):
    print(f"Plotting alert paths for: {csv_file_path}")
    if not config.mobility_file or not os.path.exists(config.mobility_file):
        print(f"Error: Mobility file not found: {config.mobility_file}")
        return False

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
    node_bounds = coord_utils.calculate_coord_bounds(
        x_node_coords,
        y_node_coords,
        starting_x,
        starting_y,
        config.circ_radius,
    )
    node_x_min, node_x_max, node_y_min, node_y_max = node_bounds
    margin = max(config.circ_radius * 0.05, 100)
    circle_x_min = starting_x - config.circ_radius - margin
    circle_x_max = starting_x + config.circ_radius + margin
    circle_y_min = starting_y - config.circ_radius - margin
    circle_y_max = starting_y + config.circ_radius + margin
    x_min = min(node_x_min, circle_x_min)
    x_max = max(node_x_max, circle_x_max)
    y_min = min(node_y_min, circle_y_min)
    y_max = max(node_y_max, circle_y_max)
    x_range = x_max - x_min
    y_range = y_max - y_min
    if x_range > y_range:
        y_center = (y_min + y_max) / 2
        y_min = y_center - x_range / 2
        y_max = y_center + x_range / 2
    elif y_range > x_range:
        x_center = (x_min + x_max) / 2
        x_min = x_center - y_range / 2
        x_max = x_center + y_range / 2

    coord_bounds = (x_min, x_max, y_min, y_max)

    plt.figure(figsize=(10, 10))

    if hasattr(config, "show_nodes") and config.show_nodes:
        #        plt.plot(x_node_coords, y_node_coords, ".", markersize=5, color="red", alpha=0.3, label="All nodes")
        plt.plot(
            x_node_coords,
            y_node_coords,
            ".",
            color="red",
            alpha=0.6,
            label="Not receiving nodes",
        )
        plt.plot(
            x_received_coords,
            y_received_coords,
            ".",
            color="green",
            alpha=0.5,
            label="Receiving nodes",
        )

    # plot source
    plt.plot(
        starting_x,
        starting_y,
        "*",
        color="yellow",
        markersize=10,
        markeredgecolor="blue",
        markeredgewidth=1,
        label="Source node",
        zorder=10,
    )

    colors = [
        "#FF0000",
        "#00FF00",
        "#0000FF",
        "#FF00FF",
        "#00FFFF",
        "#FF8000",
        "#8000FF",
        "#008000",
    ]
    sender_color_map = {}
    color_index = 0
    plotted_forwarders = set()

    # draw arrows from sender to sender
    for sender, receivers in transmission_map.items():
        if not receivers:
            continue
        # assign color for this sender
        if sender not in sender_color_map:
            sender_color_map[sender] = colors[color_index % len(colors)]
            color_index += 1
        path_color = sender_color_map[sender]

        sender_coord = coord_utils.find_coords_from_file(sender, config.mobility_file)
        if sender_coord is None:
            continue
        # mark sender as forwarder
        if sender not in plotted_forwarders:
            plt.plot(
                sender_coord.x,
                sender_coord.y,
                "o",
                color=path_color,
                markersize=6,
                markeredgecolor="black",
                markeredgewidth=1,
                zorder=8,
            )
            plotted_forwarders.add(sender)

        # draw arrows to each receiver if that receiver also forwards (i.e. exists as a key in transmission_map)
        for recv in receivers:
            recv_coord = coord_utils.find_coords_from_file(recv, config.mobility_file)
            if recv_coord is None:
                continue
            if transmission_map.get(recv):
                plt.annotate(
                    "",
                    xy=(recv_coord.x, recv_coord.y),
                    xytext=(sender_coord.x, sender_coord.y),
                    arrowprops=dict(
                        arrowstyle="->",
                        color=path_color,
                        lw=1.5,
                        alpha=0.8,
                        shrinkA=3,
                        shrinkB=3,
                        mutation_scale=15,
                    ),
                    zorder=5,
                )

    simulation_bug_detected = False
    received_on_circ_ids_fallback = []
    bug_warning = ""
    node_spacing = 25  # TODO: Hard-coded node spacing in meters, add parameter
    if hasattr(config, "debug") and config.debug:
        # BUG DETECTION: Check if circumference data is invalid
        circumference_candidates = find_circumference_candidates(
            x_received_coords,
            y_received_coords,
            starting_x,
            starting_y,
            node_spacing,
            config,
        )
        received_on_circ_ids_fallback = coord_utils.find_node_ids_from_coords(
            circumference_candidates,
            config.mobility_file,
        )
        if sorted(received_on_circ_ids_fallback) == sorted(received_on_circ_ids):
            print(
                "✅ The receivers on circumference from the NS-3 simulation and the fallback correspond",
            )
        else:
            print("⚠️ Received_on_circ_ids DO NOT correspond with the fallback ones!")

    # Check if ns3-simulation script has a bug not reporting conference nodes
    if not received_on_circ_ids or received_on_circ_ids in (["0"], [0]):
        simulation_bug_detected = True
        bug_warning = "⚠️  SIMULATION BUG: 'Nodes on circ' field is empty/zero! Used fallback"
        print(f"WARNING: {bug_warning}")
        print(
            "\nThis indicates the NS-3 simulation isn't properly calculating circumference nodes.",
        )
        print(
            f"Node spacing used to calculate the circumference: {node_spacing}. Change if different!\n",
        )

        # Fallback: Calculate circumference nodes from received nodes
        print("Fallback: Calculating circumference nodes based on distance...")
        print(f"Source position: ({starting_x}, {starting_y})")
        print(f"Transmission range: {tx_range}m")
        print(f"Analysis circumference radius: {config.circ_radius}m")

        if config.debug:
            received_on_circ_ids = received_on_circ_ids_fallback
        else:
            circumference_candidates = find_circumference_candidates(
                x_received_coords,
                y_received_coords,
                starting_x,
                starting_y,
                node_spacing,
                config,
            )

            received_on_circ_ids = coord_utils.find_node_ids_from_coords(
                circumference_candidates,
                config.mobility_file,
            )

        print(f"Found {len(received_on_circ_ids)} circumference nodes using fallback method")

    # draw rays from last forwarders to circumference nodes (keep existing logic)
    for circ_id in received_on_circ_ids:
        for sender, receivers in transmission_map.items():
            if circ_id in receivers:
                last_forwarder_coord = coord_utils.find_coords_from_file(
                    sender,
                    config.mobility_file,
                )
                circ_coord = coord_utils.find_coords_from_file(circ_id, config.mobility_file)
                if last_forwarder_coord is not None and circ_coord is not None:
                    plt.plot(
                        [last_forwarder_coord.x, circ_coord.x],
                        [last_forwarder_coord.y, circ_coord.y],
                        "k-",
                        linewidth=1.5,
                        alpha=0.6,
                        zorder=3,
                    )
                    plt.plot(
                        circ_coord.x,
                        circ_coord.y,
                        ".",
                        color="green",
                        markersize=5,
                        alpha=0.5,
                        zorder=9,
                    )

    coord_utils.plot_tx_range(
        config.circ_radius,
        starting_x,
        starting_y,
        vehicle_distance,
        color="#840000",
        plot_interval=True,
        coord_bounds=coord_bounds,
    )

    plt.xlim(x_min, x_max)
    plt.ylim(y_min, y_max)
    plt.gca().set_aspect("equal", adjustable="box")

    if config.poly_file and os.path.exists(config.poly_file):
        coord_utils.plot_buildings(config.poly_file)

    # Plot dummy forwarder node for the legend
    plt.plot(
        [],
        [],
        "o",
        color="gray",
        markersize=6,
        markeredgecolor="black",
        markeredgewidth=1,
        label="Forwarding nodes",
    )

    leg = plt.legend(loc="upper right", framealpha=1.0, fontsize=10)
    leg.set_zorder(11)
    plt.xlabel("X Coordinate (m)", fontsize=12)
    plt.ylabel("Y Coordinate (m)", fontsize=12)

    # Modify title to include warning if bug detected
    base_title = (
        f"{config.scenario} (Transmission range: {tx_range}m) - Alert Message Propagation Paths"
    )
    if simulation_bug_detected:
        title_color = "red"
        plt.title(base_title, fontsize=14, color=title_color)
        # Add warning text
        plt.text(
            0.02,
            0.02,
            bug_warning,
            transform=plt.gca().transAxes,
            fontsize=10,
            color="red",
            weight="bold",
            verticalalignment="bottom",  # align text above this point
            bbox={"boxstyle": "round", "facecolor": "yellow", "alpha": 0.7},
        )
    else:
        plt.title(base_title, fontsize=13)

    plt.grid(True, alpha=0.3)

    if not coord_utils.ensure_output_directory(output_file_path):
        return False
    try:
        plt.savefig(output_file_path, dpi=config.dpi, bbox_inches=config.bbox_inches)
        if simulation_bug_detected:
            print(f"⚠️  Alert paths plot saved with BUG WARNING to: {output_file_path}")
        else:
            print(f"Alert paths plot saved to: {output_file_path}")
    except Exception as e:
        print(f"Error saving plot to {output_file_path}: {e}")
        return False
    finally:
        plt.close()

    return True


def main():
    script_config = {
        "description": "Draw Alert Paths Visualization Tool",
        "tool_name": "Draw Alert Paths Tool",
        "output_subfolder": "alertPaths",
        "single_output_subfolder": "singlefileAlertPath",
        "default_base_map_folder": DEFAULT_BASE_MAP_FOLDER,
        "plot_function": plot_alert_paths,
        "additional_args": [
            {
                "name": "--show-nodes",
                "action": "store_true",
                "help": "Show all receiving nodes in the visualization",
            },
            {
                "name": "--debug",
                "action": "store_true",
                "help": "Checks and report if the nodes on circumference metric"
                " reported in the csv file corresponds to the reported receiving nodes",
            },
        ],
    }
    coord_utils.generic_main(script_config)


if __name__ == "__main__":
    main()
