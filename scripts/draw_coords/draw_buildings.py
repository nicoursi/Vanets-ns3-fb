#!/usr/bin/env python3
# coding=utf-8
"""
Draw Buildings Visualization Tool

This script generates building visualization plots from polygon/building files.

Usage:
    ./draw_buildings.py <polygon_file> [output_file]

Arguments:
    polygon_file    Path to the polygon/building file (required)
    output_file     Output image path (optional, default: buildings.png)

Examples:
    # Plot buildings with default output
    ./draw_buildings.py buildings.xml

    # Plot buildings with custom output
    ./draw_buildings.py buildings.xml my_buildings.png
"""

import os
import sys
import matplotlib

matplotlib.use("Agg")  # Use non-interactive backend
import matplotlib.pyplot as plt
import coord_utils


def plot_buildings(poly_file_path, output_file_path):
    """
    Plot buildings visualization from polygon/building file.

    Args:
        poly_file_path (str): Path to polygon/building file
        output_file_path (str): Path where to save the output plot

    Returns:
        bool: True if successful, False otherwise
    """
    print(f"Plotting buildings from: {poly_file_path}")

    # Validate polygon file exists
    if not os.path.exists(poly_file_path):
        print(f"Error: Polygon/building file not found: {poly_file_path}")
        return False

    # Create the plot
    plt.figure(figsize=(10, 10), dpi=300)

    # Plot buildings
    try:
        coord_utils.plot_buildings(poly_file_path)
    except Exception as e:
        print(f"Error plotting buildings from {poly_file_path}: {e}")
        return False

    # Set equal aspect ratio to maintain building proportions
    plt.gca().set_aspect("equal", adjustable="box")

    # Add grid and labels
    plt.grid(True, alpha=0.3)
    plt.xlabel("X Coordinate (m)", fontsize=12)
    plt.ylabel("Y Coordinate (m)", fontsize=12)
    plt.title("Buildings Layout", fontsize=14)

    # Auto-adjust layout
    plt.tight_layout()

    # Ensure output directory exists
    output_dir = os.path.dirname(output_file_path)
    if output_dir and not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
        except Exception as e:
            print(f"Error creating output directory {output_dir}: {e}")
            return False

    # Save the figure
    try:
        plt.savefig(output_file_path, dpi=300, bbox_inches="tight")
        print(f"Buildings plot saved to: {output_file_path}")
    except Exception as e:
        print(f"Error saving plot to {output_file_path}: {e}")
        return False
    finally:
        plt.close()  # Clean up to prevent memory leaks

    return True


def main():
    """Main function to handle command line arguments."""

    # Check command line arguments
    if len(sys.argv) < 2:
        print("Usage: draw_buildings.py <polygon_file> [output_file]")
        print("\nArguments:")
        print("  polygon_file    Path to the polygon/building file (required)")
        print("  output_file     Output image path (optional, default: buildings.png)")
        print("\nExamples:")
        print("  ./draw_buildings.py buildings.xml")
        print("  ./draw_buildings.py buildings.xml my_buildings.png")
        sys.exit(1)

    # Get polygon file path
    poly_file = sys.argv[1]

    # Get output file path (default to buildings.png)
    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    else:
        output_file = "buildings.png"

    # Plot buildings
    success = plot_buildings(poly_file, output_file)

    if not success:
        sys.exit(1)

    print("Done!")


if __name__ == "__main__":
    main()
