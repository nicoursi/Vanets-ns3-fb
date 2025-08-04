#!/usr/bin/python

#Invocation:
#   ./drawJunctions.py netFilePath ns2MobilityFile [polyFilePath]




import os
import sys
import getopt
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import coord_utils
import xml.etree.ElementTree as ET

startingNodeId = "310"

def main():
    polyFilePath = None
    netFilePath = sys.argv[1]
    ns2MobilityFile = sys.argv[2]
    if (len(sys.argv) > 3):
        polyFilePath = sys.argv[3]
    print(netFilePath)
    print("Main!!")
    color1 = "#840000"
    color2 = "#677a04"
    color3 = "#000000"

    coord_utils.plotBuildings(polyFilePath)
    coord_utils.plotJunctions(netFilePath)
    coord_utils.plotNodeList(ns2MobilityFile)
    coord_utils.plotStartingNode(startingNodeId, ns2MobilityFile)
    plt.legend(loc='best')
    plt.show()




if __name__ == "__main__":
    main()
