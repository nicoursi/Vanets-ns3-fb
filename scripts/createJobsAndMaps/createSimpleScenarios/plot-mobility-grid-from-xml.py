#!/usr/bin/env python3
"""
NS2 Mobility File Visualizer
Processes NS2 mobility XML files and plots exactly what it finds for verification.
Usage: python ns2_visualizer.py Grid-300.ns2mobility.xml [-c | --show-coords]
"""

import sys
import re
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from collections import defaultdict
from matplotlib.ticker import MultipleLocator
import numpy as np


def parse_ns2_file(filename):
    """Parse NS2 mobility file and extract node positions."""
    nodes = {}
    try:
        with open(filename, 'r') as file:
            content = file.read()

        position_pattern = r'\$node_\((\d+)\) set ([XYZ])_ ([\d.]+)'
        position_matches = re.findall(position_pattern, content)

        for node_id, coord, value in position_matches:
            node_id = int(node_id)
            if node_id not in nodes:
                nodes[node_id] = {'X': 0, 'Y': 0, 'Z': 0}
            nodes[node_id][coord] = float(value)

    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error parsing file: {e}")
        sys.exit(1)

    return nodes

def detect_overlapping_nodes(nodes, tolerance=0.001):
    """Detect nodes that are within a very close proximity (default 1cm)."""
    overlapping = []
    node_list = list(nodes.items())
    seen_pairs = set()

    for i in range(len(node_list)):
        id1, pos1 = node_list[i]
        for j in range(i + 1, len(node_list)):
            id2, pos2 = node_list[j]
            dx = pos1['X'] - pos2['X']
            dy = pos1['Y'] - pos2['Y']
            dz = pos1['Z'] - pos2['Z']
            dist_sq = dx * dx + dy * dy + dz * dz
            if dist_sq <= tolerance * tolerance:
                if (id1, id2) not in seen_pairs and (id2, id1) not in seen_pairs:
                    overlapping.append((id1, pos1))
                    overlapping.append((id2, pos2))
                    seen_pairs.add((id1, id2))

    return overlapping


def detect_grid_pattern(nodes, tolerance=1.0):
    """Detect if nodes follow a regular grid pattern."""
    if len(nodes) < 9:  # Need at least 3x3 grid to detect pattern
        return False, None, None

    # Extract unique X and Y coordinates (with tolerance for floating point)
    x_coords = sorted(set(pos['X'] for pos in nodes.values()))
    y_coords = sorted(set(pos['Y'] for pos in nodes.values()))

    # Check if we have regular spacing in X direction
    x_spacings = []
    for i in range(1, len(x_coords)):
        x_spacings.append(x_coords[i] - x_coords[i-1])

    # Check if we have regular spacing in Y direction
    y_spacings = []
    for i in range(1, len(y_coords)):
        y_spacings.append(y_coords[i] - y_coords[i-1])

    # Check if spacings are consistent (within tolerance)
    def is_consistent_spacing(spacings, tolerance=1.0):
        if len(spacings) < 2:
            return False, None
        avg_spacing = np.mean(spacings)
        return all(abs(s - avg_spacing) <= tolerance for s in spacings), avg_spacing

    x_is_grid, x_spacing = is_consistent_spacing(x_spacings, tolerance)
    y_is_grid, y_spacing = is_consistent_spacing(y_spacings, tolerance)

    # Consider it a grid if both X and Y have regular spacing
    is_grid = x_is_grid and y_is_grid

    if is_grid:
        print(f"Grid pattern detected: {len(x_coords)} x {len(y_coords)} grid")
        print(f"X spacing: {x_spacing:.2f}m, Y spacing: {y_spacing:.2f}m")

    return is_grid, x_spacing, y_spacing


def smart_tick_spacing(data_min, data_max, target_ticks=8, grid_spacing=None):
    """Calculate appropriate tick spacing based on data range."""
    data_range = data_max - data_min

    # If we have grid spacing, use it or multiples of it
    if grid_spacing is not None:
        # Find the best multiple of grid_spacing for ticks
        approx_ticks = data_range / grid_spacing

        if approx_ticks <= 12:  # Grid spacing works well
            nice_step = grid_spacing
        elif approx_ticks <= 24:  # Use every 2nd grid line
            nice_step = 2 * grid_spacing
        elif approx_ticks <= 60:  # Use every 5th grid line
            nice_step = 5 * grid_spacing
        else:  # Use every 10th grid line
            nice_step = 10 * grid_spacing

        # Calculate start and end points aligned to grid
        start = np.floor(data_min / nice_step) * nice_step
        end = np.ceil(data_max / nice_step) * nice_step

        return nice_step, start, end

    # Original logic for non-grid data
    raw_step = data_range / target_ticks

    # Round to nice numbers
    magnitude = 10 ** np.floor(np.log10(raw_step))
    normalized = raw_step / magnitude

    if normalized <= 1:
        nice_step = 1 * magnitude
    elif normalized <= 2:
        nice_step = 2 * magnitude
    elif normalized <= 5:
        nice_step = 5 * magnitude
    else:
        nice_step = 10 * magnitude

    # Calculate start and end points
    start = np.floor(data_min / nice_step) * nice_step
    end = np.ceil(data_max / nice_step) * nice_step

    return nice_step, start, end


def create_verification_plot(nodes, scenario_name="NS2 Mobility Verification", show_coords=False):
    """Create a plot showing all nodes."""
    if not nodes:
        print("No nodes found to visualize.")
        return

    overlapping_nodes = detect_overlapping_nodes(nodes, tolerance=0.1)
    overlapping_node_ids = set(node_id for node_id, _ in overlapping_nodes)

    print(f"Found {len(overlapping_nodes)} overlapping nodes at {len(set((pos['X'], pos['Y']) for _, pos in overlapping_nodes))} positions")
    for node_id, pos in overlapping_nodes:
        print(f"Node {node_id} at ({pos['X']:.2f}, {pos['Y']:.2f}, {pos['Z']:.2f})")

    all_x = [pos['X'] for pos in nodes.values()]
    all_y = [pos['Y'] for pos in nodes.values()]

    # Calculate data bounds
    x_data_min, x_data_max = min(all_x), max(all_x)
    y_data_min, y_data_max = min(all_y), max(all_y)

    # Add some padding for visualization
    x_padding = (x_data_max - x_data_min) * 0.05
    y_padding = (y_data_max - y_data_min) * 0.05

    x_min = x_data_min - x_padding
    x_max = x_data_max + x_padding
    y_min = y_data_min - y_padding
    y_max = y_data_max + y_padding

    fig, ax = plt.subplots(figsize=(12, 10))
    ax.set_facecolor('#f9f9f9')

    regular_nodes = 0
    for node_id, pos in nodes.items():
        is_overlap = node_id in overlapping_node_ids
        color = 'blue' if is_overlap else 'red'
        ax.plot(pos['X'], pos['Y'], 'o', color=color, markersize=0.1)

        if show_coords:
            ax.text(pos['X'], pos['Y'], f"({int(pos['X'])},{int(pos['Y'])})",
                    fontsize=1, color='black', ha='center', va='bottom', alpha=0.6)

        if not is_overlap:
            regular_nodes += 1

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.set_xlabel('X Distance (meters)', fontsize=12)
    ax.set_ylabel('Y Distance (meters)', fontsize=12)
    ax.set_title(f'{scenario_name}\nTotal Nodes: {len(nodes)} | Overlapping: {len(overlapping_nodes)}',
                 fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.2, linestyle='-', linewidth=0.3)
    ax.set_aspect('equal')

    # Detect if this is a grid pattern
    is_grid, x_grid_spacing, y_grid_spacing = detect_grid_pattern(nodes)

    # Smart tick spacing (grid-aware)
    x_step, x_start, x_end = smart_tick_spacing(x_data_min, x_data_max,
                                                grid_spacing=x_grid_spacing if is_grid else None)
    y_step, y_start, y_end = smart_tick_spacing(y_data_min, y_data_max,
                                                grid_spacing=y_grid_spacing if is_grid else None)

    # Set major ticks
    x_major_ticks = np.arange(x_start, x_end + x_step, x_step)
    y_major_ticks = np.arange(y_start, y_end + y_step, y_step)

    ax.set_xticks(x_major_ticks)
    ax.set_yticks(y_major_ticks)

    # Set minor ticks
    if is_grid:
        # For grids, minor ticks at grid intersections can be distracting
        # Only use minor ticks if major tick spacing is much larger than grid spacing
        x_minor_ratio = x_step / x_grid_spacing if x_grid_spacing else 1
        y_minor_ratio = y_step / y_grid_spacing if y_grid_spacing else 1

        if x_minor_ratio > 2:
            x_minor_ticks = np.arange(x_start, x_end + x_grid_spacing, x_grid_spacing)
            ax.set_xticks(x_minor_ticks, minor=True)

        if y_minor_ratio > 2:
            y_minor_ticks = np.arange(y_start, y_end + y_grid_spacing, y_grid_spacing)
            ax.set_yticks(y_minor_ticks, minor=True)
    else:
        # For scattered data, subdivide major ticks by 5
        x_minor_step = x_step / 5
        y_minor_step = y_step / 5

        x_minor_ticks = np.arange(x_start, x_end + x_minor_step, x_minor_step)
        y_minor_ticks = np.arange(y_start, y_end + y_minor_step, y_minor_step)

        ax.set_xticks(x_minor_ticks, minor=True)
        ax.set_yticks(y_minor_ticks, minor=True)

    # Customize tick appearance
    ax.tick_params(axis='both', which='minor', length=3, color='gray')
    ax.tick_params(axis='both', which='major', length=6, width=1.2)

    # Print tick information for debugging
    if is_grid:
        print(f"Grid mode - X-axis: range {x_data_min:.1f} to {x_data_max:.1f}, major ticks every {x_step:.1f}m")
        print(f"Grid mode - Y-axis: range {y_data_min:.1f} to {y_data_max:.1f}, major ticks every {y_step:.1f}m")
    else:
        print(f"Scatter mode - X-axis: range {x_data_min:.1f} to {x_data_max:.1f}, major ticks every {x_step:.1f}m")
        print(f"Scatter mode - Y-axis: range {y_data_min:.1f} to {y_data_max:.1f}, major ticks every {y_step:.1f}m")

    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='red',
                   markersize=4, label=f'Regular Nodes ({regular_nodes})'),
    ]
    if overlapping_nodes:
        legend_elements.append(
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='blue',
                       markersize=4, label=f'Overlapping Nodes ({len(overlapping_nodes)})')
        )
    ax.legend(handles=legend_elements, loc='upper right')

    plt.tight_layout()
    return fig

def main():
    """Main function to verify mobility file structure."""
    import argparse
    parser = argparse.ArgumentParser(description="Visualize NS2 mobility file nodes")
    parser.add_argument("filename", help="NS2 mobility file (.xml)")
    parser.add_argument("-c", "--show-coords", action="store_true", help="Show coordinates above nodes")

    args = parser.parse_args()

    filename = args.filename
    print(f"Visualizing NS2 mobility file: {filename}")

    nodes = parse_ns2_file(filename)
    print(f"Found {len(nodes)} nodes")

    scenario_name = filename.replace('.xml', '').replace('.ns2mobility', '')
    fig = create_verification_plot(nodes, scenario_name, show_coords=args.show_coords)

    if fig:
        output_filename = filename.replace('.xml', '.pdf')
        plt.savefig(output_filename, format='pdf', bbox_inches='tight')
        print(f"\nPlot saved as: {output_filename}")
        plt.close()

if __name__ == "__main__":
    main()
