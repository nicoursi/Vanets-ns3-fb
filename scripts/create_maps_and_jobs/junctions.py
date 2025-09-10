#!/usr/bin/python3
"""
@file    junctions.py
@author  Jordan Gottardo [jordan.gottardo@studenti.unipd.it]
@date    2019-04-19
"""
# example
# ./junctions.py ns2MobilityFilePath netFilePath

import os
import sys

sys.path.insert(0, "./draw_coords")

import coord_utils
import sumolib


def is_node_inside_junction(node_coords, junction):
    """Check if a node is inside a junction based on its shape coordinates."""
    shape = junction.get("shape")
    if shape is None or shape == "":
        return False

    x_min, x_max, y_min, y_max = coord_utils.get_bounding_box(shape, 10)
    return (
        node_coords.x >= x_min
        and node_coords.x <= x_max
        and node_coords.y >= y_min
        and node_coords.y <= y_max
    )


def main():
    """Main function to process mobility and network files."""
    ns2_mobility_file_path = sys.argv[1]
    net_file_path = sys.argv[2]

    node_list = coord_utils.parse_node_list(ns2_mobility_file_path)

    # Create output file path
    base_dir = os.path.dirname(ns2_mobility_file_path)
    base_name = os.path.basename(ns2_mobility_file_path)
    name_without_ext = os.path.splitext(os.path.splitext(base_name)[0])[0]
    out_file_path = os.path.join(base_dir, name_without_ext + ".junctions")

    nodes_inside_junctions = set()

    junction_list = coord_utils.parse_junction_list(net_file_path)
    print(f"found {len(junction_list)} junctions")

    with open(out_file_path, "w") as f:
        for node_id, node_coords in node_list.items():
            for junction in junction_list:
                if (
                    is_node_inside_junction(node_coords, junction)
                    and node_id not in nodes_inside_junctions
                ):
                    nodes_inside_junctions.add(node_id)
                    line = f"{node_id} {junction.get('id')}\n"
                    f.write(line)


if __name__ == "__main__":
    main()
