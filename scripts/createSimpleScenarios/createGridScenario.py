#!/usr/bin/python3

# Invocation:
#	./createGridScenario.py roadLength roadNumber roadDistance roadSize nodeDistance scenarioName [roadVariation]
# e.g.

#./createGridScenario.py 4800 25 200 10 25 Grid-200
#./createGridScenario.py 4800 17 300 10 25 Grid-300
#./createGridScenario.py 4800 13 400 10 25 Grid-400

# With road distance variation (±5):
#./createGridScenario.py 4800 17 300 10 25 Grid-300+-5 5

#old grids:
#  ./createGridScenario.py 2400 13 200 10 25 Grid-200small
#  ./createGridScenario.py 2400 9 300 10 25 Grid-300small
#  ./createGridScenario.py 2400 7 400 10 25 Grid-400small
# or (gridSmall)
#  ./createGridScenario.py 1200 5 300 10 25

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

	# Optional parameter for road distance variation
	variation = 0
	print("args: " + str(len(os.sys.argv)))
	if len(os.sys.argv) > 7:
		variation = int(os.sys.argv[7])
		# Set random seed for reproducibility when using variation
		random.seed(42)
		print("Using road distance variation: ±" + str(variation))
	else:
		print("No variation parameter provided")

	nodesPerRoad = roadLength // nodeDistance
	initialX = 100
	initialY = 100
	nodeId = 0
	polyFilePath = "./grid/" + scenarioName + ".poly.xml"

	with open("./grid/" + scenarioName + ".ns2mobility.xml", "w+") as f:
		# Only generate random distances if variation is specified
		if variation > 0:
			print("Generating random road distances with variation ±" + str(variation))
			# Generate random road distances for vertical roads
			verticalRoadDistances = []
			currentX = initialX
			for x in range(roadNumber):
				if x == 0:
					verticalRoadDistances.append(currentX)
				else:
					# Add random variation to road distance
					randomDistance = roadDistance + random.randint(-variation, variation)
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
					randomDistance = roadDistance + random.randint(-variation, variation)
					currentY += randomDistance
					horizontalRoadDistances.append(currentY)
					print(f"Horizontal road {y}: Y={currentY}, distance used: {randomDistance}")
		else:
			print("Using regular grid spacing (no variation)")
			# Use regular grid spacing (original behavior)
			verticalRoadDistances = [initialX + x * roadDistance for x in range(roadNumber)]
			horizontalRoadDistances = [initialY + y * roadDistance for y in range(roadNumber)]

		# vertical roads
		for x in range(roadNumber):
			print("x= " + str(x))
			for y in range(nodesPerRoad):
				utils.writeNodeToFile(f, nodeId, verticalRoadDistances[x], initialY + y * nodeDistance, 0)
				nodeId += 1

		# horizontal roads
		for y in range(roadNumber):
			for x in range(nodesPerRoad):
				utils.writeNodeToFile(f, nodeId, initialX + x * nodeDistance, horizontalRoadDistances[y], 0)
				nodeId += 1

	print("Created grid with " + str(nodeId) + " nodes")

	# For the poly file, pass the actual road distances when variation is used
	if variation > 0:
		# Create a modified version of createPolyFile that uses the actual road positions
		utils.createPolyFileWithVariation(polyFilePath, roadNumber, verticalRoadDistances, horizontalRoadDistances, roadSize)
	else:
		# Use the original function for regular grids
		utils.createPolyFile(polyFilePath, int(roadNumber), int(roadDistance), int(roadSize), int(initialX), int(initialY))

if __name__ == "__main__":
	main()
