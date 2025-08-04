#!/usr/bin/python3

# Invocation:
# ./create_grid_scenario.py roadLength roadNumber roadDistance roadSize nodeDistance scenarioName [roadVariation] [nodeVariation]
# e.g.

# ./create_grid_scenario.py 4800 25 200 10 25 Grid-200
#   ./create_grid_scenario.py 4800 17 300 10 25 Grid-300
#   ./create_grid_scenario.py 4800 13 400 10 25 Grid-400

#   With road distance variation (±5):
#   ./create_grid_scenario.py 4800 17 300 10 25 Grid-300+-5 5

#   With both road and node distance variation:
#   ./create_grid_scenario.py 4800 17 300 10 25 Grid-300+-5-node+-5 5 5

import sys, os
import string
import shutil
import random
import utils


def main():
    roadLength = int(os.sys.argv[1])
    roadNumber = int(os.sys.argv[2])
    roadDistance = int(os.sys.argv[3])
    roadSize = int(os.sys.argv[4])
    nodeDistance = int(os.sys.argv[5])
    scenarioName = os.sys.argv[6]

    # Optional parameters for variations
    roadVariation = 0
    nodeVariation = 0

    print("args: " + str(len(os.sys.argv)))

    if len(os.sys.argv) > 7:
        roadVariation = int(os.sys.argv[7])
        print("Using road distance variation: ±" + str(roadVariation))

    if len(os.sys.argv) > 8:
        nodeVariation = int(os.sys.argv[8])
        print("Using node distance variation: ±" + str(nodeVariation))

    if roadVariation > 0 or nodeVariation > 0:
        # Set random seed for reproducibility when using variation
        random.seed(42)

    if roadVariation == 0 and nodeVariation == 0:
        print("No variation parameters provided")

    # Calculate nodes per road to cover the full road length including endpoints
    nodesPerRoad = (roadLength // nodeDistance) + 1
    initialX = 100
    initialY = 100
    nodeId = 0
    polyFilePath = "./grid/" + scenarioName + ".poly.xml"

    with open("./grid/" + scenarioName + ".ns2mobility.xml", "w+") as f:
        # Generate road positions (with or without variation)
        if roadVariation > 0:
            print("Generating random road distances with variation ±" + str(roadVariation))
            # Generate random road distances for vertical roads
            verticalRoadDistances = []
            currentX = initialX
            for x in range(roadNumber):
                if x == 0:
                    verticalRoadDistances.append(currentX)
                else:
                    # Add random variation to road distance
                    randomDistance = roadDistance + random.randint(-roadVariation, roadVariation)
                    currentX += randomDistance
                    verticalRoadDistances.append(currentX)
                    print(f"Vertical road {x}: X={currentX}, distance used: {randomDistance}")

            # Generate random road distances for horizontal roads
            horizontalRoadDistances = []
            currentY = initialY
            for y in range(roadNumber):
                if y == 0:
                    horizontalRoadDistances.append(currentY)
                else:
                    # Add random variation to road distance
                    randomDistance = roadDistance + random.randint(-roadVariation, roadVariation)
                    currentY += randomDistance
                    horizontalRoadDistances.append(currentY)
                    print(f"Horizontal road {y}: Y={currentY}, distance used: {randomDistance}")
        else:
            print("Using regular grid spacing for roads (no road variation)")
            # Use regular grid spacing (original behavior)
            verticalRoadDistances = []
            horizontalRoadDistances = []

            for x in range(roadNumber):
                currentX = initialX + x * roadDistance
                verticalRoadDistances.append(currentX)
                print(f"Vertical road {x}: X={currentX}, distance used: {roadDistance}")

            for y in range(roadNumber):
                currentY = initialY + y * roadDistance
                horizontalRoadDistances.append(currentY)
                print(f"Horizontal road {y}: Y={currentY}, distance used: {roadDistance}")

        # Generate all node positions
        all_positions = []

        if nodeVariation > 0:
            print(f"Generating nodes with variable spacing (±{nodeVariation})")

            # Add nodes along vertical roads with variable spacing
            for x_idx in range(roadNumber):
                road_x = verticalRoadDistances[x_idx]
                current_y = initialY

                # Always add the first node at the start of the road
                all_positions.append((road_x, current_y))
                print(f"Vertical road {x_idx}: Node at ({road_x}, {current_y})")

                # Generate subsequent nodes with variable spacing
                while True:
                    varied_distance = nodeDistance + random.randint(-nodeVariation, nodeVariation)
                    varied_distance = max(1, varied_distance)  # Ensure minimum distance
                    current_y += varied_distance

                    if current_y <= initialY + roadLength:
                        all_positions.append((road_x, current_y))
                        print(
                            f"Vertical road {x_idx}: Node at ({road_x}, {current_y}), distance: {varied_distance}"
                        )
                    else:
                        break

            # Add nodes along horizontal roads with variable spacing (avoid duplicates at intersections)
            for y_idx in range(roadNumber):
                road_y = horizontalRoadDistances[y_idx]
                current_x = initialX

                # Always add the first node at the start of the road (if not already exists)
                if (current_x, road_y) not in all_positions:
                    all_positions.append((current_x, road_y))
                    print(f"Horizontal road {y_idx}: Node at ({current_x}, {road_y})")

                # Generate subsequent nodes with variable spacing
                while True:
                    varied_distance = nodeDistance + random.randint(-nodeVariation, nodeVariation)
                    varied_distance = max(1, varied_distance)  # Ensure minimum distance
                    current_x += varied_distance

                    if current_x <= initialX + roadLength:
                        if (current_x, road_y) not in all_positions:
                            all_positions.append((current_x, road_y))
                            print(
                                f"Horizontal road {y_idx}: Node at ({current_x}, {road_y}), distance: {varied_distance}"
                            )
                    else:
                        break
        else:
            print("Using regular node spacing (no node variation)")
            # Original logic without variation - use set to avoid duplicates
            unique_positions = set()

            # Add nodes along vertical roads
            for x_idx in range(roadNumber):
                road_x = verticalRoadDistances[x_idx]
                for y in range(nodesPerRoad):
                    pos_y = initialY + y * nodeDistance
                    if pos_y <= initialY + roadLength:
                        unique_positions.add((road_x, pos_y))

            # Add nodes along horizontal roads
            for y_idx in range(roadNumber):
                road_y = horizontalRoadDistances[y_idx]
                for x in range(nodesPerRoad):
                    pos_x = initialX + x * nodeDistance
                    if pos_x <= initialX + roadLength:
                        unique_positions.add((pos_x, road_y))

            all_positions = list(unique_positions)

        print(
            f"Grid bounds: X=[{initialX}, {initialX + roadLength}], Y=[{initialY}, {initialY + roadLength}]"
        )
        print(
            f"Last road positions: X={verticalRoadDistances[-1]}, Y={horizontalRoadDistances[-1]}"
        )

        # Sort and write all positions to file
        all_positions.sort()
        for pos_x, pos_y in all_positions:
            utils.writeNodeToFile(f, nodeId, pos_x, pos_y, 0)
            nodeId += 1

    print("Created grid with " + str(nodeId) + " unique nodes")

    # Check if corner node exists
    corner_x = verticalRoadDistances[-1]
    corner_y = horizontalRoadDistances[-1]
    if (corner_x, corner_y) in all_positions:
        print(f"✓ Corner node exists at ({corner_x}, {corner_y})")
    else:
        print(f"✗ Corner node MISSING at ({corner_x}, {corner_y})")

    # For the poly file, pass the actual road distances when variation is used
    if roadVariation > 0:
        utils.createPolyFileWithVariation(
            polyFilePath, roadNumber, verticalRoadDistances, horizontalRoadDistances, roadSize
        )
    else:
        utils.createPolyFile(
            polyFilePath,
            int(roadNumber),
            int(roadDistance),
            int(roadSize),
            int(initialX),
            int(initialY),
        )


if __name__ == "__main__":
    main()
