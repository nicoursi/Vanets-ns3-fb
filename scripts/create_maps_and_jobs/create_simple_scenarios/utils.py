#!/usr/bin/python

import sys, os
import string
import shutil


def writeNodeToFile(f, nodeId, x, y, z=0):
    f.write("$node_(" + str(nodeId) + ") set X_ " + str(x) + "\n")
    f.write("$node_(" + str(nodeId) + ") set Y_ " + str(y) + "\n")
    f.write("$node_(" + str(nodeId) + ") set Z_ " + str(z) + "\n")
    f.write('$ns_ at 0.0 "$node_(' + str(nodeId) + ') setdest 0 0 0.00"\n')


def createPolyFile(filePath, roadNumber, roadDistance, roadSize, initialX=0, initialY=0):
    buildingsPerRow = roadNumber - 1
    buildingWidth = roadDistance - roadSize
    id = 0

    fileIntro = '<?xml version="1.0" encoding="UTF-8"?>\n\n<additional xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/additional_file.xsd">'

    with open(filePath, "w+") as f:
        f.writelines(fileIntro)
        for row in range(buildingsPerRow):
            for col in range(buildingsPerRow):
                bottomLeftX = int(initialX + roadDistance * col + roadSize / 2)
                bottomLeftY = int(initialY + roadDistance * row + roadSize / 2)

                bottomRightX = int(bottomLeftX + buildingWidth)
                bottomRightY = int(bottomLeftY)

                topRightX = int(bottomLeftX + buildingWidth)
                topRightY = int(bottomLeftY + buildingWidth)

                topLeftX = int(bottomLeftX)
                topLeftY = int(bottomLeftY + buildingWidth)

                line = '<poly id="b'
                line += str(id)
                id += 1
                line += '" type="building" color="90,102,171" fill="1" layer="-1.00" shape="'
                line += (
                    str(bottomLeftX)
                    + ","
                    + str(bottomLeftY)
                    + " "
                    + str(bottomRightX)
                    + ","
                    + str(bottomRightY)
                    + " "
                    + str(topRightX)
                    + ","
                    + str(topRightY)
                    + " "
                    + str(topLeftX)
                    + ","
                    + str(topLeftY)
                    + " "
                    + str(bottomLeftX)
                    + ","
                    + str(bottomLeftY)
                    + '"/>\n'
                )
                f.writelines(line)
        f.writelines("</additional>")


def createPolyFileWithVariation(
    filePath, roadNumber, verticalRoadDistances, horizontalRoadDistances, roadSize
):
    """
    Create poly file with variable road distances
    """
    buildingsPerRow = roadNumber - 1
    id = 0

    fileIntro = '<?xml version="1.0" encoding="UTF-8"?>\n\n<additional xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/additional_file.xsd">'

    with open(filePath, "w+") as f:
        f.writelines(fileIntro)
        for row in range(buildingsPerRow):
            for col in range(buildingsPerRow):
                # Use actual road positions instead of calculated positions
                leftRoadX = verticalRoadDistances[col]
                rightRoadX = verticalRoadDistances[col + 1]
                bottomRoadY = horizontalRoadDistances[row]
                topRoadY = horizontalRoadDistances[row + 1]

                # Calculate building position between roads
                bottomLeftX = int(leftRoadX + roadSize / 2)
                bottomLeftY = int(bottomRoadY + roadSize / 2)

                # Calculate building dimensions based on actual road spacing
                buildingWidth = int(rightRoadX - leftRoadX - roadSize)
                buildingHeight = int(topRoadY - bottomRoadY - roadSize)

                bottomRightX = int(bottomLeftX + buildingWidth)
                bottomRightY = int(bottomLeftY)

                topRightX = int(bottomLeftX + buildingWidth)
                topRightY = int(bottomLeftY + buildingHeight)

                topLeftX = int(bottomLeftX)
                topLeftY = int(bottomLeftY + buildingHeight)

                line = '<poly id="b'
                line += str(id)
                id += 1
                line += '" type="building" color="90,102,171" fill="1" layer="-1.00" shape="'
                line += (
                    str(bottomLeftX)
                    + ","
                    + str(bottomLeftY)
                    + " "
                    + str(bottomRightX)
                    + ","
                    + str(bottomRightY)
                    + " "
                    + str(topRightX)
                    + ","
                    + str(topRightY)
                    + " "
                    + str(topLeftX)
                    + ","
                    + str(topLeftY)
                    + " "
                    + str(bottomLeftX)
                    + ","
                    + str(bottomLeftY)
                    + '"/>\n'
                )
                f.writelines(line)
        f.writelines("</additional>")


def createNetFile(filePath, roadNumber, verticalRoadDistances, horizontalRoadDistances, roadSize):
    """
    Create .net.xml file with junctions at road intersections
    """
    fileIntro = """<?xml version="1.0" encoding="UTF-8"?>

<net version="1.16" junctionCornerDetail="5" limitTurnSpeed="5.50" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/net_file.xsd">

    <location netOffset="0.00,0.00" convBoundary="0.00,0.00,5000.00,5000.00" origBoundary="-10000000000.00,-10000000000.00,10000000000.00,10000000000.00" projParameter="!"/>

"""

    with open(filePath, "w+") as f:
        f.write(fileIntro)

        junctionId = 1

        # Generate junctions at every intersection
        for row in range(roadNumber):
            for col in range(roadNumber):
                x = verticalRoadDistances[col]
                y = horizontalRoadDistances[row]

                # Calculate junction shape (approximate square around intersection)
                halfRoadSize = roadSize / 2

                # Junction shape coordinates (clockwise from top-right)
                shape_coords = [
                    (x + halfRoadSize, y + halfRoadSize),  # top-right
                    (x + halfRoadSize, y - halfRoadSize),  # bottom-right
                    (x - halfRoadSize, y - halfRoadSize),  # bottom-left
                    (x - halfRoadSize, y + halfRoadSize),  # top-left
                ]

                # Convert to shape string
                shape = " ".join([f"{coord[0]:.2f},{coord[1]:.2f}" for coord in shape_coords])

                # Generate internal lanes (simplified version)
                intLanes = (
                    f":{junctionId}_0_0 :{junctionId}_1_0 :{junctionId}_2_0 :{junctionId}_3_0"
                )

                # Write junction
                junction_line = f'    <junction id="{junctionId}" type="priority" x="{x:.2f}" y="{y:.2f}" incLanes="" intLanes="{intLanes}" shape="{shape}"/>\n'
                f.write(junction_line)

                junctionId += 1

        f.write("\n</net>\n")


def createNetFileRegular(filePath, roadNumber, roadDistance, roadSize, initialX, initialY):
    """
    Create .net.xml file with regular grid spacing
    """
    # Generate regular road positions
    verticalRoadDistances = [initialX + i * roadDistance for i in range(roadNumber)]
    horizontalRoadDistances = [initialY + i * roadDistance for i in range(roadNumber)]

    # Use the main function
    createNetFile(filePath, roadNumber, verticalRoadDistances, horizontalRoadDistances, roadSize)
