#!/usr/bin/python3
"""
Coordinate utilities for simulation analysis and visualization.

This module provides utilities for handling 3D coordinates, edges, parsing
mobility files, plotting transmission ranges, and managing simulation
configurations for network analysis.
"""

import os
import sys
import argparse
import errno
import re
import csv
import xml.etree.ElementTree as ET

import numpy as np
import matplotlib.pyplot as plt


# ============================================================================
# COORDINATES RELATED FUNCTIONS
# ============================================================================


class Vector:
    """
    Represents a 3D coordinate vector.

    Attributes:
        x (float): X coordinate
        y (float): Y coordinate
        z (float): Z coordinate
    """

    def __init__(self, x, y, z):
        """
        Initialize a Vector with x, y, z coordinates.

        Args:
            x (float): X coordinate
            y (float): Y coordinate
            z (float): Z coordinate
        """
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __hash__(self):
        """Return hash of the vector coordinates."""
        return hash((self.x, self.y, self.z))

    def __eq__(self, other):
        """Check equality with another vector."""
        return (self.x, self.y, self.z) == (
            other.x,
            other.y,
            other.z,
        )

    def __ne__(self, other):
        """Check inequality with another vector."""
        return not (self == other)

    def __repr__(self):
        """Return string representation for debugging."""
        return "({0}, {1}, {2})\n".format(self.x, self.y, self.z)

    def __str__(self):
        """Return human-readable string representation."""
        return "Vector({0},{1},{2})".format(self.x, self.y, self.z)


class Edge:
    """
    Represents an edge in a network transmission graph.

    Attributes:
        source (int): Source node ID
        destination (int): Destination node ID
        phase (int): Transmission phase
    """

    def __init__(self, x, y, z):
        """
        Initialize an Edge.

        Args:
            x (int): Source node ID
            y (int): Destination node ID
            z (int): Transmission phase
        """
        self.source = int(x)
        self.destination = int(y)
        self.phase = int(z)

    def __repr__(self):
        """Return string representation for debugging."""
        return "({0}, {1}, {2})".format(
            self.source,
            self.destination,
            self.phase,
        )

    def __str__(self):
        """Return human-readable string representation."""
        return "Edge({0},{1},{2})".format(
            self.source,
            self.destination,
            self.phase,
        )


def is_file_complete(file_path):
    """
    Check if a file is complete by counting lines.

    Args:
        file_path (str): Path to the file to check

    Returns:
        bool: True if file has more than one line, False otherwise
    """
    with open(file_path) as f:
        for i, line in enumerate(f):  # noqa: B007
            pass
    return i == 1


def plot_tx_range(
    tx_range,
    starter_coord_x,
    starter_coord_y,
    vehicle_distance,
    color="black",
    plot_interval=True,
    coord_bounds=None,
):
    """
    Plot transmission range circles on current matplotlib plot.

    Args:
        tx_range (float): Transmission range in meters
        starter_coord_x (float): X coordinate of transmitter
        starter_coord_y (float): Y coordinate of transmitter
        vehicle_distance (float): Vehicle distance for interval plotting
        color (str, optional): Color for the circles. Defaults to "black"
        plot_interval (bool, optional): Whether to plot inner/outer ranges.
            Defaults to True
        coord_bounds (tuple, optional): Coordinate bounds (xMin, xMax, yMin, yMax).
            Defaults to None
    """
    color = "black"

    # If coord_bounds is provided, use it; otherwise use default 5000x5000
    if coord_bounds is not None:
        x_min, x_max, y_min, y_max = coord_bounds
        # Add some padding around the bounds
        padding = max(tx_range * 1.2, 200)  # Use transmission range or min 200m
        x_min -= padding
        x_max += padding
        y_min -= padding
        y_max += padding
    else:
        x_min, x_max, y_min, y_max = (
            0,
            5000,
            0,
            5000,
        )

    x = np.linspace(x_min, x_max, 100)
    y = np.linspace(y_min, y_max, 100)
    x_grid, y_grid = np.meshgrid(x, y)
    real_tx_range = (x_grid - starter_coord_x) ** 2 + (y_grid - starter_coord_y) ** 2 - tx_range**2
    plt.contour(x_grid, y_grid, real_tx_range, [0], colors=color)

    if plot_interval:
        outer_tx_range = (
            (x_grid - starter_coord_x) ** 2
            + (y_grid - starter_coord_y) ** 2
            - (tx_range + vehicle_distance) ** 2
        )
        inner_tx_range = (
            (x_grid - starter_coord_x) ** 2
            + (y_grid - starter_coord_y) ** 2
            - (tx_range - vehicle_distance) ** 2
        )
        plt.contour(
            x_grid,
            y_grid,
            outer_tx_range,
            [0],
            colors=color,
            linestyles="dashed",
        )
        plt.contour(
            x_grid,
            y_grid,
            inner_tx_range,
            [0],
            colors=color,
            linestyles="dashed",
        )


def find_coords_from_file(node_id, ns2_mobility_file):
    """
    Find coordinates for a specific node ID from NS2 mobility file.

    Args:
        node_id (str): Node ID to search for
        ns2_mobility_file (str): Path to NS2 mobility file

    Returns:
        Vector: Vector object with coordinates, or None if not found
    """
    node_id = str(node_id)
    with open(ns2_mobility_file, "r") as file:
        lines = file.readlines()
        num_lines = len(lines)
        count = 0
        while count < num_lines:
            line = lines[count]
            split_line = line.split(" ")
            if len(split_line) != 4:
                count = count + 1
                continue
            id_part = split_line[0].split("_")
            id_part = id_part[1].replace("(", "")
            id_part = id_part.replace(")", "")
            if id_part == node_id:
                x = split_line[3].strip()
                y = lines[count + 1].split(" ")[3].strip()
                z = lines[count + 2].split(" ")[3].strip()
                return Vector(x, y, z)
            count = count + 1
    print("error: coordinate not found for node")
    print(node_id)
    return None


def find_node_ids_from_coords(
    circumference_candidates,
    ns2_mobility_file_path,
):
    """
    Find node IDs whose coordinates match any (x,y) in the candidate list.

    Args:
        circumference_candidates (list): List of (x,y) coordinate tuples
        ns2_mobility_file_path (str): Path to NS2 mobility file

    Returns:
        list: List of node IDs with matching coordinates
    """
    coord_dict = parse_node_list(ns2_mobility_file_path)
    result_ids = []

    # Build a set for fast lookup
    candidate_set = set((float(x), float(y)) for x, y in circumference_candidates)

    for node_id, vector in coord_dict.items():
        node_coords = (vector.x, vector.y)
        if node_coords in candidate_set:
            result_ids.append(node_id)

    return result_ids


def retrieve_coords(ids, ns2_mobility_file):
    """
    Retrieve x and y coordinates for a string of underscore-separated node IDs.

    Args:
        ids (str): Underscore-separated string of node IDs
        ns2_mobility_file (str): Path to NS2 mobility file

    Returns:
        tuple: Two lists containing x coordinates and y coordinates
    """
    x_coords = []
    y_coords = []
    split_ids = ids.split("_")

    for node_id in split_ids:
        if len(node_id) == 0:
            continue
        coords = find_coords_from_file(node_id, ns2_mobility_file)
        if coords is not None:
            x_coords.append(coords.x)
            y_coords.append(coords.y)
    return x_coords, y_coords


def retrieve_coords_as_vector(ids, ns2_mobility_file):
    """
    Retrieve coordinates as Vector objects for underscore-separated node IDs.

    Args:
        ids (str): Underscore-separated string of node IDs
        ns2_mobility_file (str): Path to NS2 mobility file

    Returns:
        list: List of Vector objects containing coordinates
    """
    coords = []
    split_ids = ids.split("_")
    for node_id in split_ids:
        if len(node_id) == 0:
            continue
        coord = find_coords_from_file(node_id, ns2_mobility_file)
        if coord is not None:
            coords.append(coord)
    return coords


def build_vector_from_coords(coords):
    """
    Build a Vector object from colon-separated coordinate string.

    Args:
        coords (str): Colon-separated coordinates "x:y:z"

    Returns:
        Vector: Vector object with parsed coordinates
    """
    split_coords = coords.split(":")
    return Vector(
        split_coords[0],
        split_coords[1],
        split_coords[2],
    )


def parse_transmission_map(raw_transmission_map):
    """
    Parse raw transmission map string into dictionary structure.

    Args:
        raw_transmission_map (str): Raw transmission map string

    Returns:
        dict: Dictionary mapping source nodes to destination lists
    """
    count = 0
    after_close_curly_remove = raw_transmission_map.split("}")
    transmission_map = {}
    for s in after_close_curly_remove:
        if len(s) == 0:
            continue
        after_open_curly_remove = s.split("{")
        key_node = after_open_curly_remove[0].split(":")[0]
        destinations = after_open_curly_remove[1]
        split_destinations = destinations.split(";")
        transmission_map[key_node] = []
        for dest in split_destinations:
            if len(dest) == 0:
                continue
            transmission_map[key_node].append(dest)
    return transmission_map


def parse_transmission_vector(
    raw_transmission_vector,
):
    """
    Parse raw transmission vector string into list of Edge objects.

    Args:
        raw_transmission_vector (str): Raw transmission vector string

    Returns:
        list: List of Edge objects representing transmissions
    """
    raw_edges = raw_transmission_vector.split("_")
    transmission_vector = []
    for raw_edge in raw_edges:
        if len(raw_edge) > 0:
            after_dash_split = raw_edge.split("-")
            source = after_dash_split[0]
            after_star_split = after_dash_split[1].split("*")
            destination = after_star_split[0]
            phase = after_star_split[1]
            transmission_vector.append(Edge(source, destination, phase))
    return transmission_vector


import csv


def parse_file(file_path, ns2_mobility_file):
    """
    Parse simulation CSV file and extract all relevant data using column names.
    Args:
        file_path (str): Path to CSV file to parse
        ns2_mobility_file (str): Path to NS2 mobility file
    Returns:
        tuple: Contains all parsed simulation data including:
            - tx_range, starting coordinates, vehicle info
            - coordinate lists, transmission maps and vectors
            - node IDs and received coordinates
    """
    starting_vehicle = 0
    vehicle_distance = 0
    tx_range = 0
    x_received_coords = []
    y_received_coords = []
    x_node_coords = []
    y_node_coords = []
    raw_node_ids = []
    received_ids = []
    received_coords_on_circ = []
    starting_x = 0
    starting_y = 0

    with open(file_path, "r") as file:
        csv_reader = csv.DictReader(file)

        # Get the first (and presumably only) data row
        raw_row = next(csv_reader)

        # Strip whitespace from column names
        row = {key.strip(): value for key, value in raw_row.items()}

        # Extract values using column names
        tx_range = int(row["Actual Range"])
        starting_x = float(row["Starting x"])
        starting_y = float(row["Starting y"])
        starting_vehicle = int(row["Starting node"])
        vehicle_distance = int(row["Vehicle distance"])
        received_ids = row["Received node ids"]
        raw_node_ids = row["Node ids"]
        raw_transmission_map = row["Transmission map"]
        received_on_circ_ids = row["Received on circ nodes"]
        raw_transmission_vector = row["Transmission vector"]

        # Process the extracted data
        node_ids = [x for x in raw_node_ids.split("_") if x]
        x_received_coords, y_received_coords = retrieve_coords(received_ids, ns2_mobility_file)
        x_node_coords, y_node_coords = retrieve_coords(raw_node_ids, ns2_mobility_file)
        received_coords_on_circ = retrieve_coords_as_vector(
            received_on_circ_ids,
            ns2_mobility_file,
        )
        received_on_circ_ids = [x for x in received_on_circ_ids.split("_") if x]
        transmission_map = parse_transmission_map(raw_transmission_map)
        transmission_vector = parse_transmission_vector(raw_transmission_vector)

    return (
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
    )


def parse_file(file_path, ns2_mobility_file):
    """
    Parse simulation CSV file and extract all relevant data using column names.
    Args:
        file_path (str): Path to CSV file to parse
        ns2_mobility_file (str): Path to NS2 mobility file
    Returns:
        tuple: Contains all parsed simulation data including:
            - tx_range, starting coordinates, vehicle info
            - coordinate lists, transmission maps and vectors
            - node IDs and received coordinates
    """
    starting_vehicle = 0
    vehicle_distance = 0
    tx_range = 0
    x_received_coords = []
    y_received_coords = []
    x_node_coords = []
    y_node_coords = []
    raw_node_ids = []
    received_ids = []
    received_coords_on_circ = []
    starting_x = 0
    starting_y = 0

    with open(file_path, "r") as file:
        csv_reader = csv.DictReader(file)

        # Get the first (and presumably only) data row
        raw_row = next(csv_reader)

        # Strip quotes from column names
        row = {key.strip().strip('"'): value for key, value in raw_row.items()}

        # Extract values using column names
        tx_range = int(row["Actual Range"])
        starting_x = float(row["Starting x"])
        starting_y = float(row["Starting y"])
        starting_vehicle = int(row["Starting node"])
        vehicle_distance = int(row["Vehicle distance"])
        received_ids = row["Received node ids"]
        raw_node_ids = row["Node ids"]
        raw_transmission_map = row["Transmission map"]
        received_on_circ_ids = row["Received on circ nodes"]
        raw_transmission_vector = row["Transmission vector"]

        # Process the extracted data
        node_ids = [x for x in raw_node_ids.split("_") if x]
        x_received_coords, y_received_coords = retrieve_coords(received_ids, ns2_mobility_file)
        x_node_coords, y_node_coords = retrieve_coords(raw_node_ids, ns2_mobility_file)
        received_coords_on_circ = retrieve_coords_as_vector(
            received_on_circ_ids,
            ns2_mobility_file,
        )
        received_on_circ_ids = [x for x in received_on_circ_ids.split("_") if x]
        transmission_map = parse_transmission_map(raw_transmission_map)
        transmission_vector = parse_transmission_vector(raw_transmission_vector)

    return (
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
    )


# Usage example:
# Method 1: Using the tuple return (same as before but with column names)
# result = parse_file("data.csv", "mobility.txt")
# tx_range, starting_x, starting_y, ... = result

# Method 2: Using the dictionary return (more readable)
# data = parse_file_dict("data.csv", "mobility.txt")
# print(f"TX Range: {data['tx_range']}")
# print(f"Starting position: ({data['starting_x']}, {data['starting_y']})")


def plot_shape(shape, p_color="red", p_alpha=0.15):
    """
    Plot a shape defined by space-separated coordinate pairs.

    Args:
        shape (str): Space-separated coordinate pairs "x1,y1 x2,y2 ..."
        p_color (str, optional): Fill color. Defaults to "red"
        p_alpha (float, optional): Fill transparency. Defaults to 0.15
    """
    split_coords = shape.split()
    x_shape_coords = []
    y_shape_coords = []
    for coord in split_coords:
        split_coords2 = coord.split(",")
        x_shape_coords.append(float(split_coords2[0]))
        y_shape_coords.append(float(split_coords2[1]))
    plt.fill(
        x_shape_coords,
        y_shape_coords,
        color=p_color,
        alpha=p_alpha,
    )


def get_bounding_box(shape, extension=10):
    """
    Get bounding box coordinates for a shape with optional extension.

    Args:
        shape (str): Space-separated coordinate pairs "x1,y1 x2,y2 ..."
        extension (int, optional): Extension margin in meters. Defaults to 10

    Returns:
        tuple: Bounding box coordinates (x_min, x_max, y_min, y_max)
    """
    split_coords = shape.split()
    x_shape_coords = []
    y_shape_coords = []
    for coord in split_coords:
        split_coords2 = coord.split(",")
        x_shape_coords.append(float(split_coords2[0]))
        y_shape_coords.append(float(split_coords2[1]))
    x_min, x_max = (
        min(x_shape_coords) - extension,
        max(x_shape_coords) + extension,
    )
    y_min, y_max = (
        min(y_shape_coords) - extension,
        max(y_shape_coords) + extension,
    )
    return x_min, x_max, y_min, y_max


def plot_bounding_box(
    shape,
    extension=10,
    p_color="yellow",
    p_alpha=0.45,
):
    """
    Plot bounding box around a shape.

    Args:
        shape (str): Space-separated coordinate pairs "x1,y1 x2,y2 ..."
        extension (int, optional): Extension margin. Defaults to 10
        p_color (str, optional): Fill color. Defaults to "yellow"
        p_alpha (float, optional): Fill transparency. Defaults to 0.45
    """
    x_min, x_max, y_min, y_max = get_bounding_box(shape, extension)
    bounding_box_x = [x_min, x_max, x_max, x_min]
    bounding_box_y = [y_max, y_max, y_min, y_min]
    plt.fill(
        bounding_box_x,
        bounding_box_y,
        color=p_color,
        alpha=p_alpha,
    )


def plot_buildings(
    poly_file_path,
    plot_building_ids=False,
    ax=None,
):
    """
    Plot buildings from polygon XML file.

    Args:
        poly_file_path (str): Path to polygon XML file
        plot_building_ids (bool, optional): Whether to plot building IDs.
            Defaults to False
        ax (matplotlib.axes.Axes, optional): Matplotlib axes object.
            Defaults to None
    """
    if poly_file_path is None:
        return
    print("coord_utils::plot_buildings")
    tree = ET.parse(poly_file_path)
    root = tree.getroot()
    poly_list = list(root.iter("poly"))
    count = 0
    print("coord_utils::plot_buildings found " + str(len(poly_list)) + " buildings")
    for poly in poly_list:
        poly_id = poly.get("id")
        poly_type = poly.get("type")
        if poly_type not in {"building", "unknown"}:
            continue
        count = count + 1
        coords = poly.get("shape")
        split_coords = coords.split()
        x_shape_coords = []
        y_shape_coords = []
        sum_x = 0
        sum_y = 0
        for coord in split_coords:
            split_coords2 = coord.split(",")
            x_shape_coords.append(float(split_coords2[0]))
            y_shape_coords.append(float(split_coords2[1]))
            sum_x += x_shape_coords[-1]
            sum_y += y_shape_coords[-1]
        plt.fill(
            x_shape_coords,
            y_shape_coords,
            color="red",
            alpha=0.15,
        )

        if plot_building_ids:
            x_center = sum_x / len(x_shape_coords)
            y_center = sum_y / len(y_shape_coords)
            ax.annotate(
                poly_id,
                xy=(x_center, y_center),
                size=8,
            )


def parse_node_list(ns2_mobility_file_path):
    """
    Parse NS2 mobility file and create dictionary of node coordinates.

    Args:
        ns2_mobility_file_path (str): Path to NS2 mobility file

    Returns:
        dict: Dictionary mapping node IDs to Vector coordinates
    """
    coord_dict = {}
    with open(ns2_mobility_file_path) as f:
        lines = f.readlines()
        num_lines = len(lines)
        count = 0
        while count < num_lines:
            line = lines[count].strip()
            split_line = line.split(" ")
            if len(split_line) != 4:
                count = count + 1
                continue
            id_part = split_line[0].split("_")
            id_part = id_part[1].replace("(", "")
            id_part = id_part.replace(")", "")
            x = split_line[3].strip()
            y = lines[count + 1].split(" ")[3].strip()
            z = lines[count + 2].split(" ")[3].strip()
            coords = Vector(x, y, z)
            count = count + 3
            coord_dict[id_part] = coords
    return coord_dict


def plot_node_list(ns2_mobility_file_path):
    """
    Plot all nodes from NS2 mobility file as green dots.

    Args:
        ns2_mobility_file_path (str): Path to NS2 mobility file
    """
    coord_dict = parse_node_list(ns2_mobility_file_path)
    x_coord = []
    y_coord = []
    for (
        key,
        coord,
    ) in coord_dict.items():  # Python 3 compatible items()
        x_coord.append(coord.x)
        y_coord.append(coord.y)
    plt.plot(x_coord, y_coord, ".", color="#32DC32")


def plot_starting_node(starting_node_id, ns2_mobility_file):
    """
    Plot the starting node with transmission range circle.

    Args:
        starting_node_id (str): ID of the starting node
        ns2_mobility_file (str): Path to NS2 mobility file
    """
    coord_dict = parse_node_list(ns2_mobility_file)
    starting_x = coord_dict[starting_node_id].x
    starting_y = coord_dict[starting_node_id].y
    plt.plot(
        starting_x,
        starting_y,
        "ro",
        color="yellow",
        markeredgecolor="blue",
        markersize=5,
        label="Source of Alert Message",
    )
    plot_tx_range(1000, starting_x, starting_y, 25)


def parse_junction_list(net_file_path):
    """
    Parse junction list from network XML file.

    Args:
        net_file_path (str): Path to network XML file

    Returns:
        list: List of junction XML elements
    """
    tree = ET.parse(net_file_path)
    root = tree.getroot()
    junction_list = list(root.iter("junction"))
    return junction_list


def calculate_coord_bounds(
    x_node_coords,
    y_node_coords,
    starting_x,
    starting_y,
    circ_radius,
):
    """
    Calculate coordinate bounds ensuring circular transmission range remains circular.

    Args:
        x_node_coords (list): List of x coordinates
        y_node_coords (list): List of y coordinates
        starting_x (float): Starting x coordinate
        starting_y (float): Starting y coordinate
        circ_radius (float): Circular transmission radius

    Returns:
        tuple: Coordinate bounds (x_min, x_max, y_min, y_max)
    """
    # Get bounds from all node coordinates
    all_x = [*list(x_node_coords), starting_x]
    all_y = [*list(y_node_coords), starting_y]

    x_min, x_max = min(all_x), max(all_x)
    y_min, y_max = min(all_y), max(all_y)

    # Calculate margin: 5% of transmission range or 100m minimum
    margin = max(circ_radius * 0.05, 100)

    # Extend bounds with margin
    x_min -= margin
    x_max += margin
    y_min -= margin
    y_max += margin

    # Ensure equal scaling (square aspect ratio) to keep circles circular
    x_range = x_max - x_min
    y_range = y_max - y_min

    if x_range > y_range:
        # Extend y range to match x range
        y_center = (y_min + y_max) / 2
        y_min = y_center - x_range / 2
        y_max = y_center + x_range / 2
    elif y_range > x_range:
        # Extend x range to match y range
        x_center = (x_min + x_max) / 2
        x_min = x_center - y_range / 2
        x_max = x_center + y_range / 2

    return x_min, x_max, y_min, y_max


def plot_junctions(net_file_path):
    """
    Plot junctions from network XML file.

    Args:
        net_file_path (str): Path to network XML file
    """
    print("coord_utils::plot_junctions")
    count = 0
    junction_list = parse_junction_list(net_file_path)
    for junction in junction_list:
        count += 1
        shape = junction.get("shape")
        if shape is None or shape == "":
            continue
        plot_shape(shape)
        plot_bounding_box(shape)
    print("Plotted " + str(count) + " junctions")


# ============================================================================
# FOLDER STRUCTURE AND COMMON PARAMETER HANDLING
# ============================================================================


class SimulationConfig:
    """Configuration class for simulation parameters and paths."""

    def __init__(self):
        """Initialize SimulationConfig with default values."""
        self.base_folder = None
        self.folder = None  # New parameter for non-recursive folder processing
        self.base_map_folder = None
        self.scenario = None
        self.mobility_file = None
        self.poly_file = None
        self.original_poly_file = None  # Store original poly file path
        self.circ_radius = 1000
        self.output_base = "./out"
        self.dpi = 150
        self.bbox_inches = "tight"
        self.force_buildings = False  # New parameter to force building plotting
        self.building_mode = None  # Track detected building mode (b0/b1)
        self.verbose = False
        self.max_files_per_protocol = 3

    def set_paths_from_scenario(self, base_map_folder, scenario):
        """
        Set mobility and poly file paths based on scenario name.

        Args:
            base_map_folder (str): Base folder containing map files
            scenario (str): Scenario name (e.g., 'Padova-25')
        """
        self.base_map_folder = base_map_folder
        self.scenario = scenario
        self.mobility_file = os.path.join(
            base_map_folder,
            scenario,
            scenario + ".ns2mobility.xml",
        )
        self.original_poly_file = os.path.join(
            base_map_folder,
            scenario,
            scenario + ".poly.xml",
        )
        self.poly_file = self.original_poly_file  # Set initial value

    def configure_buildings(
        self,
        building_mode,
        filename=None,
        verbose=False,
    ):
        """
        Configure building plotting based on building mode detection.

        Args:
            building_mode (str): Building mode from folder structure ('b0' or 'b1')
            filename (str, optional): Filename to check for additional building
                indicators. Defaults to None
            verbose (bool, optional): Enable verbose output. Defaults to False
        """
        self.building_mode = building_mode

        # Check if buildings should be disabled
        should_disable_buildings = False

        if building_mode == "b0":
            should_disable_buildings = True
            if verbose:
                print(f"Building mode 'b0' detected from folder structure - buildings disabled")

        # Additional check in filename if provided
        if filename and "b0" in filename.lower():
            should_disable_buildings = True
            if verbose:
                print(f"'b0' detected in filename '{filename}' - buildings disabled")

        # Apply building configuration unless forced
        if should_disable_buildings and not self.force_buildings:
            if verbose:
                print("Setting poly_file to None (no buildings will be plotted)")
            self.poly_file = None
        elif self.force_buildings and self.original_poly_file:
            if verbose:
                print("Force buildings enabled - using original poly file")
            self.poly_file = self.original_poly_file
        elif building_mode == "b1" or (filename and "b1" in filename.lower()):
            if verbose:
                print("Building mode 'b1' detected - buildings enabled")
            self.poly_file = self.original_poly_file

    def validate_paths(self):
        """
        Validate that required files exist.

        Returns:
            list: List of error messages for missing files
        """
        errors = []

        if self.mobility_file and not os.path.exists(self.mobility_file):
            errors.append(f"Mobility file not found: {self.mobility_file}")

        if self.poly_file and not os.path.exists(self.poly_file):
            # Poly file is optional, just warn
            print(f"Warning: Poly file not found: {self.poly_file}")
            self.poly_file = None

        if self.base_folder and not os.path.exists(self.base_folder):
            errors.append(f"Base folder not found: {self.base_folder}")

        if self.folder and not os.path.exists(self.folder):
            errors.append(f"Folder not found: {self.folder}")

        return errors


def parse_csv_path_structure(csv_path):
    """
    Parse CSV file path to extract scenario and folder structure information.
    Enhanced to handle sub-branch detection, scenario reconstruction, and optional cw level.

    Expected structures:
    - Standard: scenario/building/errorRate/txRange/junction/cw/Protocol/csv_filename
    - No CW: scenario/building/errorRate/txRange/junction/Protocol/csv_filename (e.g., ROFF)

    Examples:
    - Padova-25/b0/e0/r300/j0/cw[32-1024]/Fast-Broadcast/filename.csv
    - Padova-25/b1/e0/r700/j0/ROFF/filename.csv

    Args:
        csv_path (str): Path to CSV file

    Returns:
        dict: Dictionary with extracted components or None if parsing fails
    """
    try:
        # Normalize path separators
        normalized_path = csv_path.replace("\\", "/")

        # Get directory path (remove filename)
        dir_path = os.path.dirname(normalized_path)
        csv_filename = os.path.basename(normalized_path)

        if not csv_filename.endswith(".csv"):
            return None

        # Try to extract scenario from filename first
        filename_parts = csv_filename.replace(".csv", "").split("-")
        potential_scenario = None

        # Look for scenario pattern in filename (e.g., "Padova-25")
        for i in range(len(filename_parts) - 1):
            potential_scenario_part = "-".join(filename_parts[: i + 2])
            if re.match(
                r"^[A-Za-z]+-\d+$",
                potential_scenario_part,
            ):
                potential_scenario = potential_scenario_part
                break

        # Use scenario detection to find the proper structure
        detection_result = detect_scenario_from_basepath(dir_path)

        # If we found a valid structure, use it
        if detection_result["structure_valid"]:
            scenario_name = detection_result["scenario_name"]

            # Parse the relative path from scenario to get components
            if detection_result["sub_path"]:
                path_parts = detection_result["sub_path"].split("/")
            else:
                path_parts = []

            # Initialize with defaults
            components = {
                "scenario": scenario_name,
                "building": "unknown",
                "error_rate": "unknown",
                "txRange": "unknown",
                "junction": "unknown",
                "cw": "unknown",
                "protocol": "unknown",
                "csv_filename": csv_filename,
                "csv_path": csv_path,
            }

            # Determine structure type by checking path patterns
            has_cw_level = False
            if len(path_parts) >= 5:
                # Check if 5th element matches cw pattern
                if re.match(r"^cw\[.*\]$", path_parts[4]):
                    has_cw_level = True

            # Map path parts to components based on structure type
            if len(path_parts) >= 1 and path_parts[0]:
                components["building"] = path_parts[0]
            if len(path_parts) >= 2:
                components["error_rate"] = path_parts[1]
            if len(path_parts) >= 3:
                components["txRange"] = path_parts[2]
            if len(path_parts) >= 4:
                components["junction"] = path_parts[3]

            if has_cw_level:
                # Standard structure with cw level
                if len(path_parts) >= 5:
                    components["cw"] = path_parts[4]
                if len(path_parts) >= 6:
                    components["protocol"] = path_parts[5]
            else:
                # Structure without cw level (e.g., ROFF)
                components["cw"] = "none"  # Indicate no cw level
                if len(path_parts) >= 5:
                    components["protocol"] = path_parts[4]

            return components

        # Fallback to original parsing method with enhanced cw detection
        path_parts = normalized_path.split("/")

        # Try both structures:
        # Standard: filename, Protocol, cw, junction, txRange, errorRate, building, scenario (8 parts minimum)
        # No CW: filename, Protocol, junction, txRange, errorRate, building, scenario (7 parts minimum)

        if len(path_parts) >= 8:
            # Try standard structure first
            potential_cw = path_parts[-3]
            if re.match(r"^cw\[.*\]$", potential_cw):
                # Standard structure with cw
                protocol = path_parts[-2]
                cw = potential_cw
                junction = path_parts[-4]
                tx_range = path_parts[-5]
                error_rate = path_parts[-6]
                building = path_parts[-7]
                scenario = path_parts[-8]

                return {
                    "scenario": scenario,
                    "building": building,
                    "error_rate": error_rate,
                    "txRange": tx_range,
                    "junction": junction,
                    "cw": cw,
                    "protocol": protocol,
                    "csv_filename": csv_filename,
                    "csv_path": csv_path,
                }

        if len(path_parts) >= 7:
            # Try structure without cw
            protocol = path_parts[-2]
            junction = path_parts[-3]
            tx_range = path_parts[-4]
            error_rate = path_parts[-5]
            building = path_parts[-6]
            scenario = path_parts[-7]

            return {
                "scenario": scenario,
                "building": building,
                "error_rate": error_rate,
                "txRange": tx_range,
                "junction": junction,
                "cw": "none",  # No cw level
                "protocol": protocol,
                "csv_filename": csv_filename,
                "csv_path": csv_path,
            }

        return None

    except (IndexError, ValueError):
        return None


def find_csv_files(base_folder, max_files_per_protocol):
    """
    Find all CSV files in the folder structure and return them organized.

    Args:
        base_folder (str): Base folder to search
        max_files_per_protocol (int): Maximum files to process per protocol

    Returns:
        list: List of dictionaries with CSV file information
    """
    csv_files = []

    if not os.path.exists(base_folder):
        print(f"Error: Base folder does not exist: {base_folder}")
        return csv_files

    print(f"Scanning folder structure in: {base_folder}")

    for root, dirs, files in os.walk(base_folder):
        protocol_file_count = 0
        for filename in files:
            if not filename.endswith(".csv"):
                continue

            if protocol_file_count >= max_files_per_protocol:
                break

            csv_path = os.path.join(root, filename)

            # Check if file is complete
            if not is_file_complete(csv_path):
                continue

            # Parse the path structure
            path_info = parse_csv_path_structure(csv_path)
            if path_info:
                csv_files.append(path_info)
                protocol_file_count += 1

    print(f"Found {len(csv_files)} valid CSV files")
    return csv_files


def find_csv_files_in_folder(folder_path, max_files):
    """
    Find all CSV files directly in the specified folder (non-recursive).

    Args:
        folder_path (str): Folder to search for CSV files
        max_files (int, optional): Maximum number of files to process

    Returns:
        list: List of dictionaries with CSV file information
    """
    csv_files = []

    if not os.path.exists(folder_path):
        print(f"Error: Folder does not exist: {folder_path}")
        return csv_files

    print(f"Scanning CSV files in folder: {folder_path}")

    # Get all files directly in the folder (non-recursive)
    try:
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    except OSError as e:
        print(f"Error reading folder {folder_path}: {e}")
        return csv_files

    file_count = 0
    for filename in sorted(files):  # Sort for consistent processing order
        if not filename.endswith(".csv"):
            continue

        if max_files is not None and file_count >= max_files:
            break

        csv_path = os.path.join(folder_path, filename)

        # Check if file is complete
        if not is_file_complete(csv_path):
            print(f"Skipping incomplete file: {filename}")
            continue

        # Try to parse the path structure - this might fail for files not following the expected structure
        path_info = parse_csv_path_structure(csv_path)
        if path_info:
            csv_files.append(path_info)
        else:
            # If parsing fails, create a basic structure
            csv_files.append(
                {
                    "scenario": "unknown",
                    "building": "unknown",
                    "error_rate": "unknown",
                    "txRange": "unknown",
                    "junction": "unknown",
                    "cw": "unknown",
                    "protocol": "unknown",
                    "csv_filename": filename,
                    "csv_path": csv_path,
                }
            )

        file_count += 1

    print(f"Found {len(csv_files)} valid CSV files")
    return csv_files


def setup_common_argument_parser(
    description="Simulation analysis tool",
):
    """
    Create an argument parser with common parameters used by multiple scripts.
    Implements mandatory argument groups as specified.

    Args:
        description (str): Description for the argument parser

    Returns:
        argparse.ArgumentParser: Configured argument parser
    """
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Create mutually exclusive group for file processing options (one is mandatory)
    file_group = parser.add_mutually_exclusive_group(required=True)
    file_group.add_argument(
        "-f",
        "--file",
        help="Single CSV file to process",
    )
    file_group.add_argument(
        "-d",
        "--folder",
        help="Folder containing CSV files to process (non-recursive)",
    )
    file_group.add_argument(
        "-b",
        "--basefolder",
        help="Base folder for batch processing (recursive)",
    )

    # Create mutually exclusive group for mobility source (one is mandatory)
    mobility_group = parser.add_mutually_exclusive_group(required=True)
    mobility_group.add_argument(
        "-m",
        "--mobility",
        help="NS2 mobility file path",
    )
    mobility_group.add_argument(
        "--mapfolder",
        help="Base map folder containing scenario subdirectories",
    )

    # Optional arguments
    parser.add_argument(
        "-p",
        "--poly",
        help="Polygon/building file path (optional)",
    )
    parser.add_argument(
        "-r",
        "--radius",
        type=int,
        help="Transmission radius in meters (default: 1000 for non-Grid scenarios, 2000 for Grid scenarios)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="./out",
        help="Output base directory (default: ./out)",
    )
    parser.add_argument(
        "--maxfiles",
        type=int,
        default=3,
        help="Maximum files to process per protocol for -b, or total files for -d (default: 3)",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=150,
        help="DPI for output images (default: 150)",
    )
    parser.add_argument(
        "--force-buildings",
        action="store_true",
        help="Force building plotting regardless of b0/b1 detection",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    return parser


def determine_default_radius(scenario_name):
    """
    Determine default radius based on scenario name.

    Args:
        scenario_name (str): Name of the scenario

    Returns:
        int: Default radius (2000 for Grid scenarios, 1000 for others)
    """
    if scenario_name and "Grid" in scenario_name:
        return 2000
    return 1000


def process_common_arguments(args, additional_args=None):
    """
    Process common arguments and return a SimulationConfig object.

    Args:
        args: Parsed arguments from argparse
        additional_args: Additional arguments configuration

    Returns:
        SimulationConfig: Configured simulation config object
    """
    config = SimulationConfig()

    # Determine scenario name for radius calculation
    scenario_name = None

    # Try to extract scenario from file path if single file provided
    if args.file:
        path_info = parse_csv_path_structure(args.file)
        if path_info:
            scenario_name = path_info["scenario"]

    # Try to extract scenario from folder name if folder provided
    elif args.folder:
        # Use folder name as scenario name
        scenario_name = os.path.basename(args.folder.rstrip("/\\"))

    # Try to detect scenario from base folder if batch processing
    elif args.basefolder:
        detection_result = detect_scenario_from_basepath(args.basefolder)
        if detection_result["structure_valid"]:
            scenario_name = detection_result["scenario_name"]
        else:
            # Fallback to folder name
            scenario_name = os.path.basename(args.basefolder.rstrip("/\\"))

    # Set radius with conditional default
    if args.radius is not None:
        config.circ_radius = args.radius
    else:
        config.circ_radius = determine_default_radius(scenario_name)

    # Set basic parameters
    config.base_folder = args.basefolder
    config.folder = args.folder
    config.output_base = args.output
    config.base_map_folder = args.mapfolder
    config.dpi = args.dpi
    config.verbose = args.verbose
    config.force_buildings = args.force_buildings

    # Handle script-specific arguments dynamically
    if additional_args:
        for arg_config in additional_args:
            arg_name = (
                arg_config["name"].lstrip("-").replace("-", "_")
            )  # Convert --show-nodes to show_nodes
            if hasattr(args, arg_name):
                setattr(
                    config,
                    arg_name,
                    getattr(args, arg_name),
                )

    # Handle legacy script-specific arguments that might be present
    if hasattr(args, "maxfiles"):
        config.max_files_per_protocol = args.maxfiles

    # Handle mobility and poly files
    if args.mobility:
        config.mobility_file = args.mobility
    if args.poly:
        config.poly_file = args.poly
        config.original_poly_file = args.poly

    # If map folder is provided and we have a single file, try to extract scenario
    if args.mapfolder and args.file:
        path_info = parse_csv_path_structure(args.file)
        if path_info:
            config.set_paths_from_scenario(
                args.mapfolder,
                path_info["scenario"],
            )
            # Configure buildings for single file
            config.configure_buildings(
                path_info["building"],
                path_info["csv_filename"],
                args.verbose,
            )

    return config


def add_script_specific_arguments(parser, additional_args):
    """
    Add script-specific arguments to the parser.

    Args:
        parser: ArgumentParser instance
        additional_args: List of argument configurations
    """
    if not additional_args:
        return

    for arg_config in additional_args:
        # Make a copy to avoid modifying the original
        arg_config_copy = arg_config.copy()
        arg_name = arg_config_copy.pop("name")
        parser.add_argument(arg_name, **arg_config_copy)


def validate_folder_structure_from_scenario_enhanced(scenario_path, target_path):
    """
    Validate that the folder structure from scenario to target follows the expected pattern.
    Enhanced to handle optional cw level and better structure validation.

    Args:
        scenario_path (str): Path to the scenario root
        target_path (str): Path to validate against

    Returns:
        bool: True if structure is valid
    """
    if not os.path.exists(scenario_path):
        return False

    try:
        rel_path = os.path.relpath(target_path, scenario_path)
        if rel_path == ".":
            return True  # target_path is the scenario_path itself

        path_parts = rel_path.split(os.sep)

        # Structure patterns for validation
        patterns = {
            "building": r"^b[01]$",  # "b0" or "b1"
            "error_rate": r"^e\d+$",  # e.g., "e0"
            "txRange": r"^r\d+$",  # e.g., "r300"
            "junction": r"^j\d+$",  # e.g., "j0"
            "cw": r"^cw\[.*\]$",  # e.g., "cw[32-1024]"
            "protocol": r"^[A-Za-z-]+$",  # e.g., "Fast-Broadcast" or "ROFF"
        }

        return validate_structure_parts(path_parts, patterns)

    except (ValueError, OSError):
        return False


def generate_output_path(path_info, output_base, suffix, output_subfolder):
    """
    Generate output file path based on CSV path structure.
    Enhanced to handle optional cw level.

    Creates structure:
    - Standard: scenario/building/error_rate/txRange/junction/cw/protocol/output_subfolder/filename.ext
    - No CW: scenario/building/error_rate/txRange/junction/protocol/output_subfolder/filename.ext

    Args:
        path_info (dict): Path information from parse_csv_path_structure
        output_base (str): Base output directory
        suffix (str): File suffix (default: ".png")
        output_subfolder (str): Dynamic subfolder name (e.g., "plots", "heatmaps", etc.)

    Returns:
        str: Generated output path
    """
    filename_no_ext = os.path.splitext(path_info["csv_filename"])[0]
    output_filename = filename_no_ext + suffix + ".png"

    # Build path components
    path_components = [
        output_base,
        path_info["scenario"],
        path_info["building"],
        path_info["error_rate"],
        path_info["txRange"],
        path_info["junction"],
    ]

    # Add cw level only if it exists (not 'none')
    if path_info["cw"] != "none":
        path_components.append(path_info["cw"])

    # Add protocol, filename directory, then dynamic subfolder, then final filename
    path_components.extend(
        [
            path_info["protocol"],
            filename_no_ext,  # Add filename as directory (like before)
            output_subfolder,  # Dynamic subfolder name passed as parameter
            output_filename,
        ]
    )

    output_path = os.path.join(*path_components)
    return output_path


def ensure_output_directory(file_path):
    """
    Ensure that the directory for the given file path exists.
    Includes protection against race conditions when used with multiprocessing.

    Args:
        file_path (str): Full path to the output file

    Returns:
        bool: True if directory exists or was created successfully, False otherwise
    """
    directory = os.path.dirname(file_path)

    if not directory:  # Handle case where file_path has no directory component
        return True

    try:
        os.makedirs(directory, exist_ok=True)
        return True
    except OSError as exc:  # Guard against race condition
        if exc.errno != errno.EEXIST:
            print(f"Error creating directory {directory}: {exc}")
            return False
        # If errno is EEXIST, directory already exists (race condition), which is fine
        return True


def validate_folder_structure_from_scenario(scenario_path, target_path):
    """
    Validate that the folder structure from scenario to target follows the expected pattern.

    Args:
        scenario_path (str): Path to the scenario root
        target_path (str): Path to validate against

    Returns:
        bool: True if structure is valid
    """
    if not os.path.exists(scenario_path):
        return False

    try:
        rel_path = os.path.relpath(target_path, scenario_path)
        if rel_path == ".":
            return True  # target_path is the scenario_path itself

        path_parts = rel_path.split(os.sep)

        # Structure patterns (same as in detect_scenario_from_basepath)
        structure_patterns = [
            r"^b[01]$",  # building: "b0" or "b1"
            r"^e\d+$",  # errorRate: e.g., "e0"
            r"^r\d+$",  # txRange: e.g., "r300"
            r"^j\d+$",  # junction: e.g., "j0"
            r"^cw\[.*\]$",  # cw: e.g., "cw[32-1024]"
            r"^[A-Za-z-]+$",  # protocol: e.g., "Fast-Broadcast"
        ]

        # Validate each part against expected pattern
        for i, part in enumerate(path_parts):
            if i >= len(structure_patterns):
                break  # More levels than expected, but still valid
            if not re.match(structure_patterns[i], part):
                return False

        return True

    except (ValueError, OSError):
        return False


def detect_scenario_from_basepath(base_folder):
    """
    Detect if the provided base folder is a sub-branch of the expected structure
    and try to reconstruct the full scenario path by going backwards.
    Enhanced to handle optional cw level and better scenario detection.

    Expected structures:
    - Standard: scenario/building/errorRate/txRange/junction/cw/Protocol/
    - No CW: scenario/building/errorRate/txRange/junction/Protocol/

    Args:
        base_folder (str): Base folder path that might be a sub-branch

    Returns:
        dict: Dictionary containing:
            - 'scenario_path': Full path to scenario root
            - 'scenario_name': Name of the scenario
            - 'sub_path': Relative path from scenario to base_folder
            - 'is_sub_branch': Whether base_folder is a sub-branch
            - 'structure_valid': Whether the detected structure is valid
    """
    result = {
        "scenario_path": base_folder,
        "scenario_name": os.path.basename(base_folder.rstrip("/\\")),
        "sub_path": "",
        "is_sub_branch": False,
        "structure_valid": False,
    }

    # Normalize path
    normalized_path = os.path.normpath(base_folder.rstrip("/\\"))
    path_parts = normalized_path.split(os.sep)

    if len(path_parts) == 0:
        return result

    # Structure patterns for validation
    structure_patterns = {
        "scenario": r"^[A-Za-z]+-\d+$",  # e.g., "Padova-25", "Grid-100"
        "building": r"^b[01]$",  # "b0" or "b1"
        "error_rate": r"^e\d+$",  # e.g., "e0"
        "txRange": r"^r\d+$",  # e.g., "r300"
        "junction": r"^j\d+$",  # e.g., "j0"
        "cw": r"^cw\[.*\]$",  # e.g., "cw[32-1024]" (optional)
        "protocol": r"^[A-Za-z-]+$",  # e.g., "Fast-Broadcast" or "ROFF"
    }

    # Try to find the scenario by going backwards through the path
    current_path = normalized_path
    levels_back = 0

    while current_path and levels_back < 10:  # Max 10 levels to prevent infinite loops
        current_basename = os.path.basename(current_path)

        # Check if current basename matches scenario pattern
        if re.match(
            structure_patterns["scenario"],
            current_basename,
        ):
            # Found potential scenario, now validate the structure from scenario to original path
            try:
                rel_path = os.path.relpath(normalized_path, current_path)

                # If the relative path is just '.', we're at the scenario level
                if rel_path == ".":
                    result["scenario_path"] = current_path
                    result["scenario_name"] = current_basename
                    result["sub_path"] = ""
                    result["is_sub_branch"] = False
                    result["structure_valid"] = True
                    break

                # Parse the relative path to validate structure
                rel_path_parts = rel_path.split(os.sep)

                # Check if the structure is valid
                if validate_structure_parts(
                    rel_path_parts,
                    structure_patterns,
                ):
                    result["scenario_path"] = current_path
                    result["scenario_name"] = current_basename
                    result["sub_path"] = rel_path
                    result["is_sub_branch"] = levels_back > 0
                    result["structure_valid"] = True
                    break

            except (ValueError, OSError):
                pass  # Continue searching

        # Move up one level
        parent_path = os.path.dirname(current_path)
        if parent_path == current_path:  # Reached root
            break
        current_path = parent_path
        levels_back += 1

    return result


def validate_structure_parts(path_parts, patterns):
    """
    Validate that path parts follow the expected structure.

    Args:
        path_parts (list): List of path components from scenario to target
        patterns (dict): Dictionary of regex patterns for validation

    Returns:
        bool: True if structure is valid
    """
    if not path_parts:
        return True  # Empty path is valid (we're at scenario level)

    # Define the expected order of components
    expected_order = [
        "building",
        "error_rate",
        "txRange",
        "junction",
        "cw",
        "protocol",
    ]

    # Check if we have cw level by looking at the appropriate position
    has_cw_level = False
    if len(path_parts) >= 5:
        # Check if the 5th element (index 4) matches cw pattern
        if re.match(patterns["cw"], path_parts[4]):
            has_cw_level = True

    # Define expected patterns based on structure type
    if has_cw_level:
        # Standard structure: building/errorRate/txRange/junction/cw/protocol
        expected_patterns = [
            patterns["building"],
            patterns["error_rate"],
            patterns["txRange"],
            patterns["junction"],
            patterns["cw"],
            patterns["protocol"],
        ]
    else:
        # Structure without cw: building/errorRate/txRange/junction/protocol
        expected_patterns = [
            patterns["building"],
            patterns["error_rate"],
            patterns["txRange"],
            patterns["junction"],
            patterns["protocol"],
        ]

    # Validate each part against expected pattern
    min_required_parts = min(len(path_parts), len(expected_patterns))

    for i in range(min_required_parts):
        if not re.match(expected_patterns[i], path_parts[i]):
            return False

    # If we have more parts than expected patterns, that's also invalid
    # (unless it's just filename-level stuff which we can ignore)
    if len(path_parts) > len(expected_patterns):
        # Allow additional levels for files/directories beyond the expected structure
        pass

    return True


def generic_process_single_file(
    csv_file,
    config,
    output_file,
    plot_function,
    output_subfolder="plots",
    single_output_subfolder="singlefile",
):
    """
    Generic function to process a single CSV file.

    Args:
        csv_file (str): Path to CSV file
        config (SimulationConfig): Configuration object
        output_file (str, optional): Custom output file path
        plot_function (callable): Function to call for plotting
        output_subfolder (str): Subfolder name for organized batch outputs
        single_output_subfolder (str): Subfolder name for single file outputs

    Returns:
        bool: True if successful, False otherwise
    """
    print(f"Processing single file: {csv_file}")

    if not os.path.exists(csv_file):
        print(f"Error: CSV file does not exist: {csv_file}")
        return False

    # Check if file is complete
    if not is_file_complete(csv_file):
        print(f"Error: CSV file appears incomplete: {csv_file}")
        return False

    # Configure buildings if not already done
    path_info = parse_csv_path_structure(csv_file)
    if path_info and not hasattr(config, "building_mode"):
        config.configure_buildings(
            path_info["building"],
            path_info["csv_filename"],
            config.verbose,
        )

    if config.verbose:
        print(
            f"Building configuration: mode='{config.building_mode}', "
            f"poly_file={'None' if config.poly_file is None else 'enabled'}, "
            f"force_buildings={config.force_buildings}"
        )

    # Generate output path
    show_nodes = ""
    if hasattr(config, "show_nodes") and config.show_nodes:
        show_nodes = "-show-nodes"

    if output_file:
        output_path = output_file
    # Try to parse path structure for organized output
    elif path_info:
        output_path = generate_output_path(
            path_info, config.output_base, show_nodes, output_subfolder
        )
    else:
        # Fallback to simple output
        csv_filename = os.path.basename(csv_file)
        output_filename = os.path.splitext(csv_filename)[0] + show_nodes + ".png"
        output_path = os.path.join(
            config.output_base,
            single_output_subfolder,
            output_filename,
        )

    # Call the plotting function
    return plot_function(csv_file, output_path, config)


def generic_process_folder(
    config,
    plot_function,
    output_subfolder="plots",
    verbose_mode=False,
):
    """
    Generic function to process all CSV files in a single folder (non-recursive).

    Args:
        config (SimulationConfig): Configuration object
        plot_function (callable): Function to call for plotting
        output_subfolder (str): Subfolder name for organized batch outputs
        verbose_mode (bool): Enable verbose output

    Returns:
        dict: Statistics about processing
    """
    print(f"Processing CSV files from folder: {config.folder}")

    # Find all CSV files in the folder
    max_files = getattr(config, "max_files_per_protocol", None)
    csv_files = find_csv_files_in_folder(config.folder, max_files)

    if not csv_files:
        print("No valid CSV files found in the specified folder")
        return {
            "processed_count": 0,
            "successful_count": 0,
            "failed_count": 0,
        }

    processed_count = 0
    successful_count = 0

    # Try to determine scenario from the first file that has proper structure
    scenario_name = None
    for file_info in csv_files:
        if file_info["scenario"] != "unknown":
            scenario_name = file_info["scenario"]
            break

    # If no scenario found from file structure, use folder name as fallback
    if not scenario_name:
        scenario_name = os.path.basename(config.folder.rstrip("/\\"))

    print(f"Detected/using scenario: {scenario_name}")

    # Set up scenario paths if we have a map folder and detected a valid scenario
    if config.base_map_folder and scenario_name != "unknown":
        config.set_paths_from_scenario(config.base_map_folder, scenario_name)

    for file_info in csv_files:
        processed_count += 1

        print(f"\nProcessing file {processed_count}/{len(csv_files)}: {file_info['csv_filename']}")

        # Configure buildings for this specific file
        if file_info["building"] != "unknown":
            config.configure_buildings(
                file_info["building"],
                file_info["csv_filename"],
                verbose_mode,
            )

            if verbose_mode:
                print(f"  Building mode: {config.building_mode}")
                print(f"  Buildings enabled: {'No' if config.poly_file is None else 'Yes'}")
                print(f"  Force buildings: {config.force_buildings}")

        if verbose_mode:
            print(f"  Base map folder: {config.base_map_folder}")
            print(f"  Mobility file: {config.mobility_file}")
            print(f"  Poly file: {config.poly_file}")

        # Validate paths for this file
        errors = config.validate_paths()
        if errors:
            print(f"Skipping file due to missing required files:")
            for error in errors:
                print(f"  - {error}")
            continue

        # Generate output path
        show_nodes = ""
        if hasattr(config, "show_nodes") and config.show_nodes:
            show_nodes = "-show-nodes"

        if file_info["scenario"] != "unknown":
            # Use proper structure if available
            file_info_copy = file_info.copy()
            file_info_copy["scenario"] = scenario_name
            output_path = generate_output_path(
                file_info_copy,
                os.path.join(
                    config.output_base,
                    output_subfolder,
                ),
                show_nodes,
            )
        else:
            # Fallback to simple structure for files without proper path structure
            filename_no_ext = os.path.splitext(file_info["csv_filename"])[0]
            output_filename = filename_no_ext + show_nodes + ".png"
            output_path = os.path.join(
                config.output_base,
                output_subfolder,
                scenario_name,
                "unknown",
                filename_no_ext,
                output_filename,
            )

        # Call the plotting function
        if plot_function(
            file_info["csv_path"],
            output_path,
            config,
        ):
            successful_count += 1

    failed_count = processed_count - successful_count

    print(f"\nFolder processing completed.")
    print(f"Processed: {processed_count} files")
    print(f"Successful: {successful_count} files")
    print(f"Failed: {failed_count} files")

    return {
        "processed_count": processed_count,
        "successful_count": successful_count,
        "failed_count": failed_count,
    }


def generic_process_batch(
    config,
    plot_function,
    output_subfolder="plots",
    verbose_mode=False,
):
    """
    Generic function to process multiple files in batch mode using the folder structure.
    Enhanced to handle sub-branch detection and proper scenario reconstruction.

    Args:
        config (SimulationConfig): Configuration object
        plot_function (callable): Function to call for plotting
        output_subfolder (str): Subfolder name for organized batch outputs
        verbose_mode (bool): Enable verbose output

    Returns:
        dict: Statistics about processing
    """
    print(f"Processing batch from base folder: {config.base_folder}")

    # Detect if base folder is a sub-branch and get scenario information
    detection_result = detect_scenario_from_basepath(config.base_folder)

    if verbose_mode:
        print(f"Folder structure detection:")
        print(f"  Is sub-branch: {detection_result['is_sub_branch']}")
        print(f"  Structure valid: {detection_result['structure_valid']}")
        print(f"  Detected scenario: {detection_result['scenario_name']}")
        print(f"  Scenario path: {detection_result['scenario_path']}")
        print(f"  Sub-path: {detection_result['sub_path']}")

    # Use detected scenario information
    if detection_result["structure_valid"]:
        scenario_name = detection_result["scenario_name"]
        scenario_path = detection_result["scenario_path"]

        print(f"Detected scenario: {scenario_name}")
        if detection_result["is_sub_branch"]:
            print(f"Processing sub-branch: {detection_result['sub_path']}")
            print(f"Full scenario path: {scenario_path}")
    else:
        # Fallback: use original behavior
        scenario_name = os.path.basename(config.base_folder.rstrip("/\\"))
        scenario_path = config.base_folder
        print(f"Using fallback scenario detection: {scenario_name}")

    # Find all CSV files in the folder structure
    csv_files = find_csv_files(
        config.base_folder,
        max_files_per_protocol=getattr(config, "max_files_per_protocol", None),
    )

    if not csv_files:
        print("No valid CSV files found in the specified folder structure")
        return {
            "processed_count": 0,
            "successful_count": 0,
            "failed_count": 0,
        }

    processed_count = 0
    successful_count = 0

    for file_info in csv_files:
        processed_count += 1

        print(f"\nProcessing file {processed_count}/{len(csv_files)}: {file_info['csv_filename']}")

        # Set up paths for this scenario if we have map folder
        if config.base_map_folder:
            temp_config = SimulationConfig()
            temp_config.__dict__.update(config.__dict__)  # Copy all settings
            temp_config.set_paths_from_scenario(
                config.base_map_folder,
                scenario_name,
            )

            # Configure buildings for this specific file
            temp_config.configure_buildings(
                file_info["building"],
                file_info["csv_filename"],
                verbose_mode,
            )

            if verbose_mode:
                print(f"  Building mode: {temp_config.building_mode}")
                print(f"  Buildings enabled: {'No' if temp_config.poly_file is None else 'Yes'}")
                print(f"  Force buildings: {temp_config.force_buildings}")
                print(f"  Base map folder: {temp_config.base_map_folder}")
                print(f"  Mobility file: {temp_config.mobility_file}")
                print(f"  Poly file: {temp_config.poly_file}")
        else:
            temp_config = config

        # Validate paths for this file
        errors = temp_config.validate_paths()
        if errors:
            print(f"Skipping file due to missing required files:")
            for error in errors:
                print(f"  - {error}")
            continue

        # Generate output path - use detected scenario name for proper structure
        show_nodes = ""
        if hasattr(config, "show_nodes") and config.show_nodes:
            show_nodes = "-show-nodes"

        file_info_copy = file_info.copy()
        file_info_copy["scenario"] = scenario_name
        output_path = generate_output_path(
            file_info_copy, config.output_base, show_nodes, output_subfolder
        )

        if verbose_mode:
            print(f"  Output path: {output_path}")

        # Call the plotting function
        if plot_function(
            file_info["csv_path"],
            output_path,
            temp_config,
        ):
            successful_count += 1

    failed_count = processed_count - successful_count

    print(f"\nBatch processing completed.")
    print(f"Processed: {processed_count} files")
    print(f"Successful: {successful_count} files")
    print(f"Failed: {failed_count} files")

    return {
        "processed_count": processed_count,
        "successful_count": successful_count,
        "failed_count": failed_count,
    }


def generic_main(script_config):
    """
    Generic main function to handle command line arguments and execute appropriate actions.

    Args:
        script_config (dict): Configuration dictionary containing:
            - description (str): Script description for argument parser
            - tool_name (str): Name to display when running
            - output_subfolder (str): Default output subfolder name
            - single_output_subfolder (str): Single file output subfolder name
            - default_base_map_folder (str): Default map folder path
            - plot_function (callable): Function to call for plotting
            - additional_args (list, optional): Additional arguments for argument parser
    """

    # Set up argument parser with common parameters
    parser = setup_common_argument_parser(description=script_config["description"])

    # Add any script-specific arguments
    if "additional_args" in script_config:
        add_script_specific_arguments(
            parser,
            script_config["additional_args"],
        )

    # Parse arguments
    args = parser.parse_args()

    # Process common arguments
    additional_args = script_config.get("additional_args", None)
    config = process_common_arguments(args, additional_args)

    # Set default map folder if not provided
    if not config.base_map_folder and not args.mobility:
        config.base_map_folder = script_config.get("default_base_map_folder")

    print(script_config["tool_name"])
    print(f"Transmission radius: {config.circ_radius}m")
    print(f"Force buildings: {'Yes' if config.force_buildings else 'No'}")

    if args.verbose:
        print(f"Configuration:")
        print(f"  Base folder: {config.base_folder}")
        print(f"  Folder: {config.folder}")
        print(f"  Base map folder: {config.base_map_folder}")
        print(f"  Mobility file: {config.mobility_file}")
        print(f"  Poly file: {config.poly_file}")
        print(f"  Output base: {config.output_base}")
        print(f"  Force buildings: {config.force_buildings}")

    # Determine mode of operation
    if args.file:
        # Single file mode
        output_single = getattr(args, "output_single", None)
        success = generic_process_single_file(
            args.file,
            config,
            output_single,
            script_config["plot_function"],
            script_config["output_subfolder"],
            script_config["single_output_subfolder"],
        )
        if not success:
            sys.exit(1)

    elif args.folder:
        # Folder mode (non-recursive)
        if not config.base_map_folder and not config.mobility_file:
            print(
                "Error: Either map folder or explicit mobility file is required for folder processing"
            )
            print("Use --mapfolder or -m/--mobility option")
            sys.exit(2)

        stats = generic_process_folder(
            config,
            script_config["plot_function"],
            script_config["output_subfolder"],
            args.verbose,
        )

        # Exit with error code if any files failed
        if stats["failed_count"] > 0:
            sys.exit(1)

    elif args.basefolder:
        # Batch mode (recursive)
        if not config.base_map_folder and not config.mobility_file:
            print(
                "Error: Either map folder or explicit mobility file is required for batch processing"
            )
            print("Use --mapfolder or -m/--mobility option")
            sys.exit(2)

        stats = generic_process_batch(
            config,
            script_config["plot_function"],
            script_config["output_subfolder"],
            args.verbose,
        )

        # Exit with error code if any files failed
        if stats["failed_count"] > 0:
            sys.exit(1)

    else:
        # No arguments provided
        print(
            "Error: Please specify either a single file (-f), folder (-d), or base folder (-b) for processing"
        )
        print("Use -h/--help for usage information")
        sys.exit(2)
