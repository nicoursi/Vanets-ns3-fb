#!/usr/bin/env python3
"""
3D Grid Neighbor Counter with Variable Spacing

This script calculates how many neighbors a node can have in a 3D grid
with potentially different spacing in x, y, and z directions.
"""

import math
import argparse

def count_neighbors_3d(transmission_range, dx, dy, dz):
    """
    Count the number of neighbors within transmission range in a 3D grid.
    
    Args:
        transmission_range (float): Maximum transmission distance
        dx (float): Distance between adjacent nodes in x direction
        dy (float): Distance between adjacent nodes in y direction
        dz (float): Distance between adjacent nodes in z direction
        
    Returns:
        int: Number of neighbors within range
        list: List of neighbor positions (i, j, k) for visualization
    """
    # Calculate maximum possible coordinate values in each direction
    max_i = int(math.floor(transmission_range / dx))
    max_j = int(math.floor(transmission_range / dy))
    max_k = int(math.floor(transmission_range / dz))
    
    neighbors = []
    count = 0
    
    # Check all possible grid positions
    for i in range(-max_i, max_i + 1):
        for j in range(-max_j, max_j + 1):
            for k in range(-max_k, max_k + 1):
                # Skip the origin (the node itself)
                if i == 0 and j == 0 and k == 0:
                    continue
                
                # Calculate actual distance in 3D space
                distance = math.sqrt((i * dx)**2 + (j * dy)**2 + (k * dz)**2)
                
                if distance <= transmission_range:
                    neighbors.append((i, j, k))
                    count += 1
    
    return count, neighbors

def analyze_neighbors(neighbors, dx, dy, dz):
    """
    Analyze the neighbor distribution by distance shells.
    
    Args:
        neighbors (list): List of neighbor positions
        dx, dy, dz (float): Distance between adjacent nodes in each direction
        
    Returns:
        dict: Dictionary with distance as key and neighbor info as value
    """
    distance_groups = {}
    
    for i, j, k in neighbors:
        # Calculate actual distance
        distance = math.sqrt((i * dx)**2 + (j * dy)**2 + (k * dz)**2)
        distance = round(distance, 6)  # Round to avoid floating point issues
        
        if distance not in distance_groups:
            distance_groups[distance] = []
        distance_groups[distance].append((i, j, k))
    
    return distance_groups

def analyze_by_layer(neighbors, dz):
    """
    Analyze neighbors by z-layer (height level).
    
    Args:
        neighbors (list): List of neighbor positions
        dz (float): Distance between adjacent nodes in z direction
        
    Returns:
        dict: Dictionary with z-layer as key and neighbor count as value
    """
    layer_groups = {}
    
    for i, j, k in neighbors:
        if k not in layer_groups:
            layer_groups[k] = []
        layer_groups[k].append((i, j, k))
    
    return layer_groups

def print_results(transmission_range, dx, dy, dz, neighbor_count, neighbors, verbose=False):
    """
    Print the results in a formatted way.
    """
    print(f"\n=== 3D Grid Neighbor Analysis ===")
    print(f"Transmission Range: {transmission_range}")
    print(f"Node Spacing - X: {dx}, Y: {dy}, Z: {dz}")
    print(f"Total neighbors: {neighbor_count}")
    
    if verbose and neighbors:
        print(f"\n--- Neighbor Distribution by Distance ---")
        distance_groups = analyze_neighbors(neighbors, dx, dy, dz)
        
        for distance in sorted(distance_groups.keys()):
            positions = distance_groups[distance]
            print(f"Distance {distance:.3f}: {len(positions)} neighbors")
            if len(positions) <= 8:  # Only show positions for small groups
                for pos in positions:
                    actual_pos = (pos[0] * dx, pos[1] * dy, pos[2] * dz)
                    print(f"  Grid {pos} -> Real {actual_pos}")
            else:
                print(f"  (showing first 5): {positions[:5]}")
        
        print(f"\n--- Neighbor Distribution by Z-Layer ---")
        layer_groups = analyze_by_layer(neighbors, dz)
        
        for k in sorted(layer_groups.keys()):
            height = k * dz
            neighbors_in_layer = layer_groups[k]
            if k == 0:
                print(f"Same level (z={height}): {len(neighbors_in_layer)} neighbors")
            elif k > 0:
                print(f"Level +{k} (z={height}): {len(neighbors_in_layer)} neighbors")
            else:
                print(f"Level {k} (z={height}): {len(neighbors_in_layer)} neighbors")

def main():
    parser = argparse.ArgumentParser(description='Calculate neighbors in 3D grid with variable spacing')
    parser.add_argument('transmission_range', type=float, 
                       help='Maximum transmission distance')
    parser.add_argument('dx', type=float, 
                       help='Distance between adjacent nodes in X direction')
    parser.add_argument('dy', type=float, nargs='?', default=None,
                       help='Distance between adjacent nodes in Y direction (defaults to dx)')
    parser.add_argument('dz', type=float, nargs='?', default=None,
                       help='Distance between adjacent nodes in Z direction (defaults to dx)')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Show detailed neighbor analysis')
    parser.add_argument('-e', '--examples', action='store_true',
                       help='Show common examples')
    
    args = parser.parse_args()
    
    # Set default values
    if args.dy is None:
        args.dy = args.dx
    if args.dz is None:
        args.dz = args.dx
    
    if args.examples:
        print("=== Common Examples ===")
        examples = [
            (2.0, 1.0, 1.0, 1.0, "Cubic grid - equal spacing"),
            (2.0, 1.0, 1.0, 2.0, "Taller layers - double Z spacing"),
            (2.0, 1.0, 1.0, 0.5, "Compressed layers - half Z spacing"),
            (3.0, 1.0, 1.0, 3.0, "Sparse vertical - triple Z spacing"),
            (1.5, 0.5, 0.5, 1.0, "Dense XY, normal Z"),
        ]
        
        for r, dx, dy, dz, desc in examples:
            count, _ = count_neighbors_3d(r, dx, dy, dz)
            print(f"R={r}, dx={dx}, dy={dy}, dz={dz} ({desc}): {count} neighbors")
        return
    
    # Calculate neighbors
    neighbor_count, neighbors = count_neighbors_3d(args.transmission_range, args.dx, args.dy, args.dz)
    
    # Print results
    print_results(args.transmission_range, args.dx, args.dy, args.dz, 
                 neighbor_count, neighbors, args.verbose)

if __name__ == "__main__":
    main()