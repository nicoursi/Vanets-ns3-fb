#!/usr/bin/python

# Invocation:
# ./create_line_scenario.py numNodes nodeDistance
# e.g.
#  ./create_line_scenario.py 600 1 line
# ./create_line_scenario.py 22 700 Platoon-700
# ./create_line_scenario.py 150 300 Platoon-300-big   # area=44000
# ./create_line_scenario.py 150 500 Platoon-500-big   # area=74000
# ./create_line_scenario.py 150 700 Platoon-700-big   # area=104000

import sys, os
import string
import shutil
import utils


def main():
    numNodes = int(os.sys.argv[1])
    nodeDistance = int(os.sys.argv[2])
    scenario = os.sys.argv[3]
    initialX = 0
    y = 100
    z = 0
    with open(scenario + ".ns2mobility.xml", "w+") as f:
        for i in range(numNodes):
            utils.writeNodeToFile(f, i, initialX + i * nodeDistance, y, z)


if __name__ == "__main__":
    main()
