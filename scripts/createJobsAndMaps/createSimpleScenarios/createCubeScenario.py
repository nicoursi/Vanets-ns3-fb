#!/usr/bin/python

# Invocation:
#	./createCubeScenario.py nodesPerRoad nodeDistance
# e.g.

#	./createCubeScenario.py 30 75 Cube-75			edgeLength: 2250     middle:1225.0   nodes:27001
#	./createCubeScenario.py 20 150 Cube-150			edgeLength: 3000     middle:1600.0   nodes:8000

#   ./createCubeScenario.py 40 25 Cube-small-25     edgeLength: 1000     middle:600.0    nodes:64001
#   ./createCubeScenario.py 28 35 Cube-small-35     edgeLength: 980      middle:590.0    nodes:21953

#   ./createCubeScenario.py 25 40 Cube-small-40     edgeLength: 1000     middle:600.0    nodes:15626
#   ./createCubeScenario.py 13 75 Cube-small-75     edgeLength: 975;     middle:587.5;   nodes:2198
#   ./createCubeScenario.py 7 150 Cube-small-150    edgeLength: 1050;    middle:625.0;   nodes:344

#   ./createCubeScenario.py 26 40 Cube-small-40     edgeLength: 1040     middle:600.0    nodes:15626
#   ./createCubeScenario.py 13 75 Cube-small-75     edgeLength: 975;     middle:587.5;   nodes:2198
#   ./createCubeScenario.py 7 150 Cube-small-150    edgeLength: 1050;    middle:625.0;   nodes:344


# ./createCubeScenario.py 24 125 Cube-125-3000
#edge of cube is long 3000
#middle in 1600.0
#starting node:7212
#nodes:13825
#area-of-interest:1300

#./createCubeScenario.py 20 150 Cube-150
#edgeLength: 3000
#middle:1600.0
#starting node: 4210
#nodes:8000
#area-of-interest:1300

#./createCubeScenario.py 16 200 Cube-200-3000
#edge of cube is long 3200
#middle in 1700.0
#starting node:2184
#nodes:4097
#area-of-interest:1300

import sys, os
import string
import shutil
import utils



def main():
	roadNumber = int(os.sys.argv[1])
	nodeDistance = int(os.sys.argv[2])
	cubeScenario = os.sys.argv[3]


	initialX = 100
	initialY = 100
	initialZ = 100
	nodeId = 0

	edgeLength = roadNumber * nodeDistance
	print("edge of cube is long " + str(edgeLength))
	print("middle in " + (str(edgeLength / 2 + initialX)))

	with open("./cube/" + cubeScenario + ".ns2mobility.xml", "w+") as f:
		for z in range(roadNumber):
			for y in range(roadNumber):
				for x in range(roadNumber):
					#print ("x= " + str(x) + " y= " + str(y) + " z= " + str(z))
					utils.writeNodeToFile(f, nodeId, initialX + x * nodeDistance, initialY + y * nodeDistance, initialZ + z * nodeDistance)
					nodeId += 1

	print("Created grid with " + str(nodeId + 1) + " nodes")

if __name__ == "__main__":
	main()
