#!/usr/bin/python3

import os
import sys
import getopt
import argparse
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import csv
import xml.etree.ElementTree as ET
import re


# ============================================================================
# COORDINATES RELATED FUNCTIONS
# ============================================================================

#3D coordinate class
class Vector:
    def __init__(self, x, y, z):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __hash__(self):
        return hash((self.x, self.y, self.z))

    def __eq__(self, other):
        return (self.x, self.y, self.z) == (other.x, other.y, other.z)

    def __ne__(self, other):
        return not(self == other)

    def __repr__(self):
        return "({0}, {1}, {2})\n".format(self.x, self.y, self.z)

    def __str__(self):
        return "Vector({0},{1},{2})".format(self.x, self.y, self.z)

class Edge:
    def __init__(self, x, y, z):
        self.source = int(x)
        self.destination = int(y)
        self.phase = int(z)

    def __repr__(self):
        return "({0}, {1}, {2})".format(self.source, self.destination, self.phase)

    def __str__(self):
        return "Edge({0},{1},{2})".format(self.source, self.destination, self.phase)



def isFileComplete(filePath):
    with open(filePath) as f:
        for i, l in enumerate(f):
            pass
    return (i == 1)


def plotTxRange(txRange, starterCoordX, starterCoordY, vehicleDistance, color="black", plotInterval=True, coordBounds=None):
    color = "black"

    # If coordBounds is provided, use it; otherwise use default 5000x5000
    if coordBounds is not None:
        xMin, xMax, yMin, yMax = coordBounds
        # Add some padding around the bounds
        padding = max(txRange * 1.2, 200)  # Use transmission range or minimum 200m padding
        xMin -= padding
        xMax += padding
        yMin -= padding
        yMax += padding
    else:
        xMin, xMax, yMin, yMax = 0, 5000, 0, 5000

    x = np.linspace(xMin, xMax, 100)
    y = np.linspace(yMin, yMax, 100)
    X, Y = np.meshgrid(x, y)
    realTxRange = (X - starterCoordX) ** 2 + (Y - starterCoordY) ** 2 - txRange ** 2
    CS = plt.contour(X, Y, realTxRange, [0], colors = color)

    if (plotInterval):
        outerTxRange = (X - starterCoordX) ** 2 + (Y - starterCoordY) ** 2 - (txRange + vehicleDistance) ** 2
        innerTxRange = (X - starterCoordX) ** 2 + (Y - starterCoordY) ** 2 - (txRange - vehicleDistance) ** 2
        plt.contour(X, Y, outerTxRange, [0], colors = color, linestyles = "dashed")
        plt.contour(X, Y, innerTxRange, [0], colors = color, linestyles = "dashed")

def findCoordsFromFile(nodeId, ns2MobilityFile):
    nodeId = str(nodeId)
    with open(ns2MobilityFile, "r") as file:
        lines = file.readlines()
        numLines = len(lines)
        count = 0
        while(count < numLines):
            line = lines[count]
            splitLine = line.split(" ")
            if (len(splitLine) != 4):
                count = count + 1
                continue
            id = splitLine[0].split("_")
            id = id[1].replace("(", "")
            id = id.replace(")", "")
            if (id == nodeId):
                x = splitLine[3].strip()
                y = lines[count + 1].split(" ")[3].strip()
                z = lines[count + 2].split(" ")[3].strip()
                return Vector(x, y, z)
            count = count + 1
    print("error: coordinate not found for node")
    print(nodeId)
    return None

def findNodeIdsFromCoords(circumference_candidates, ns2MobilityFilePath):
    """
    Given a list of (x,y) tuples (circumference_candidates)
    and a path to an ns2 mobility file,
    return a list of node IDs whose coordinates match any (x,y) in the list.
    """
    coordDict = parseNodeList(ns2MobilityFilePath)
    result_ids = []

    # Build a set for fast lookup
    candidate_set = set((float(x), float(y)) for x, y in circumference_candidates)

    for node_id, vector in coordDict.items():
        node_coords = (vector.x, vector.y)
        if node_coords in candidate_set:
            result_ids.append(node_id)

    return result_ids

def retrieveCoords(ids, ns2MobilityFile):
    xCoords = []
    yCoords = []
    splitIds = ids.split("_")

    for id in splitIds:
        if (len(id) == 0):
            continue
        coords = findCoordsFromFile(id, ns2MobilityFile)
        if coords is not None:
            xCoords.append(coords.x)
            yCoords.append(coords.y)
    return xCoords, yCoords

def retrieveCoordsAsVector(ids, ns2MobilityFile):
    coords = []
    splitIds = ids.split("_")
    for id in splitIds:
        if (len(id) == 0):
            continue
        coord = findCoordsFromFile(id, ns2MobilityFile)
        if coord is not None:
            coords.append(coord)
    return coords

def buildVectorFromCoords(coords):
    splitCoords = coords.split(":")
    vector = Vector(splitCoords[0], splitCoords[1], splitCoords[2])
    return vector

def parseTransmissionMap(rawTransmissionMap):
    count = 0
    afterCloseCurlyRemove = rawTransmissionMap.split("}")
    transmissionMap = {}
    for s in afterCloseCurlyRemove:
        if(len(s) == 0):
            continue
        afterOpenCurlyRemove = s.split("{")
        keyNode = afterOpenCurlyRemove[0].split(":")[0]
        destinations = afterOpenCurlyRemove[1]
        splitDestinations = destinations.split(";")
        transmissionMap[keyNode] = []
        for dest in splitDestinations:
            if(len(dest) == 0):
                continue
            transmissionMap[keyNode].append(dest)
    return transmissionMap

def parseTransmissionVector(rawTransmissionVector):
    rawEdges = rawTransmissionVector.split("_")
    transmissionVector = []
    for rawEdge in rawEdges:
        if (len(rawEdge) > 0):
            afterDashSplit = rawEdge.split("-")
            source = afterDashSplit[0]
            afterStarSplit = afterDashSplit[1].split("*")
            destination = afterStarSplit[0]
            phase = afterStarSplit[1]
            transmissionVector.append(Edge(source, destination, phase))
    return transmissionVector

def parseFile(filePath, ns2MobilityFile):
    startingVehicle = 0
    vehicleDistance = 0
    txRange = 0
    xReceivedCoords = []
    yReceivedCoords = []
    xNodeCoords = []
    yNodeCoords = []
    rawNodeIds = []
    receivedIds = []
    receivedCoordsOnCirc = []
    startingX = 0
    startingY = 0
    with open(filePath, "r") as file:
        csvFile = csv.reader(file, delimiter=",")
        next(csvFile)
        line = next(csvFile)
        txRange = int(line[2])
        startingX = float(line[14])
        startingY = float(line[15])
        startingVehicle = int(line[16])
        vehicleDistance = int(line[17])
        receivedIds = line[18]
        rawNodeIds = line[19]
        nodeIds = [x for x in rawNodeIds.split("_") if x]  # Python 3 compatible filter
        xReceivedCoords, yReceivedCoords = retrieveCoords(receivedIds, ns2MobilityFile)
        xNodeCoords, yNodeCoords = retrieveCoords(rawNodeIds, ns2MobilityFile)
        rawTransmissionMap = line[20]
        receivedOnCircIds = line[21]
        rawTransmissionVector = line[22]
        receivedCoordsOnCirc = retrieveCoordsAsVector(receivedOnCircIds, ns2MobilityFile)
        receivedOnCircIds = [x for x in receivedOnCircIds.split("_") if x]  # Python 3 compatible filter
        transmissionMap = parseTransmissionMap(rawTransmissionMap)
        transmissionVector = parseTransmissionVector(rawTransmissionVector)
    return txRange, startingX, startingY, startingVehicle, vehicleDistance, xReceivedCoords, yReceivedCoords, xNodeCoords, yNodeCoords, transmissionMap, receivedCoordsOnCirc, receivedOnCircIds, transmissionVector, nodeIds

def plotShape(shape, pColor="red", pAlpha=0.15):
    splitCoords = shape.split()
    xShapeCoords = []
    yShapeCoords = []
    for coord in splitCoords:
        splitCoords2 = coord.split(",")
        xShapeCoords.append(float(splitCoords2[0]))
        yShapeCoords.append(float(splitCoords2[1]))
    plt.fill(xShapeCoords, yShapeCoords, color=pColor, alpha=pAlpha)

def getBoundingBox(shape, extension=10):
    splitCoords = shape.split()
    xShapeCoords = []
    yShapeCoords = []
    for coord in splitCoords:
        splitCoords2 = coord.split(",")
        xShapeCoords.append(float(splitCoords2[0]))
        yShapeCoords.append(float(splitCoords2[1]))
    xMin, xMax = min(xShapeCoords) - extension, max(xShapeCoords) + extension
    yMin, yMax = min(yShapeCoords) - extension, max(yShapeCoords) + extension
    return xMin, xMax, yMin, yMax

def plotBoundingBox(shape, extension=10, pColor="yellow", pAlpha=0.45):
    xMin, xMax, yMin, yMax = getBoundingBox(shape, extension)
    boundingBoxX = [xMin, xMax, xMax, xMin]
    bounbingBoxY = [yMax, yMax, yMin, yMin]
    plt.fill(boundingBoxX, bounbingBoxY, color=pColor, alpha=pAlpha)

def plotBuildings(polyFilePath, plotBuildingIds=False, ax=None):
    if (polyFilePath is None):
        return
    print("coordUtils::plotBuildings")
    tree = ET.parse(polyFilePath)
    root = tree.getroot()
    polyList = list(root.iter("poly"))
    count = 0
    print("coordUtils::plotBuildings found " + str(len(polyList)) + " buildings")
    for poly in polyList:
        polyId = poly.get("id")
        polyType = poly.get("type")
        if (polyType != "building" and polyType != "unknown"):
            continue
        count = count + 1
        coords = poly.get("shape")
        splitCoords = coords.split()
        xShapeCoords = []
        yShapeCoords = []
        sumX = 0
        sumY = 0
        for coord in splitCoords:
            splitCoords2 = coord.split(",")
            xShapeCoords.append(float(splitCoords2[0]))
            yShapeCoords.append(float(splitCoords2[1]))
            sumX += xShapeCoords[-1]
            sumY += yShapeCoords[-1]
        plt.fill(xShapeCoords, yShapeCoords, color="red", alpha=0.15)

        if (plotBuildingIds):
            xCenter = sumX / len(xShapeCoords)
            yCenter = sumY / len(yShapeCoords)
            ax.annotate(polyId, xy=(xCenter, yCenter), size=8)

def parseNodeList(ns2MobilityFilePath):
    coordDict = {}
    with open(ns2MobilityFilePath) as f:
        lines = f.readlines()
        numLines = len(lines)
        count = 0
        while(count < numLines):
            line = lines[count].strip()
            splitLine = line.split(" ")
            if (len(splitLine) != 4):
                count = count + 1
                continue
            id = splitLine[0].split("_")
            id = id[1].replace("(", "")
            id = id.replace(")", "")
            x = splitLine[3].strip()
            y = lines[count + 1].split(" ")[3].strip()
            z = lines[count + 2].split(" ")[3].strip()
            coords = Vector(x, y, z)
            count = count + 3
            coordDict[id] = coords
    return coordDict

def plotNodeList(ns2MobilityFilePath):
    coordDict = parseNodeList(ns2MobilityFilePath)
    xCoord = []
    yCoord = []
    for key, coord in coordDict.items():  # Python 3 compatible items()
        xCoord.append(coord.x)
        yCoord.append(coord.y)
    plt.plot(xCoord, yCoord, ".", color="#32DC32")

def plotStartingNode(startingNodeId, ns2MobilityFile):
    coordDict = parseNodeList(ns2MobilityFile)
    startingX = coordDict[startingNodeId].x
    startingY = coordDict[startingNodeId].y
    plt.plot(startingX, startingY, "ro", color="yellow", markeredgecolor="blue", markersize=5, label="Source of Alert Message")
    plotTxRange(1000, startingX, startingY, 25)

def parseJunctionList(netFilePath):
    tree = ET.parse(netFilePath)
    root = tree.getroot()
    junctionList = list(root.iter("junction"))
    return junctionList

def calculateCoordBounds(xNodeCoords, yNodeCoords, startingX, startingY, circRadius):
    """Calculate coordinate bounds ensuring circular transmission range remains circular."""
    # Get bounds from all node coordinates
    allX = list(xNodeCoords) + [startingX]
    allY = list(yNodeCoords) + [startingY]

    xMin, xMax = min(allX), max(allX)
    yMin, yMax = min(allY), max(allY)

    # Calculate margin: 5% of transmission range or 100m minimum
    margin = max(circRadius * 0.05, 100)

    # Extend bounds with margin
    xMin -= margin
    xMax += margin
    yMin -= margin
    yMax += margin

    # Ensure equal scaling (square aspect ratio) to keep circles circular
    xRange = xMax - xMin
    yRange = yMax - yMin

    if xRange > yRange:
        # Extend y range to match x range
        yCenter = (yMin + yMax) / 2
        yMin = yCenter - xRange / 2
        yMax = yCenter + xRange / 2
    elif yRange > xRange:
        # Extend x range to match y range
        xCenter = (xMin + xMax) / 2
        xMin = xCenter - yRange / 2
        xMax = xCenter + yRange / 2

    return xMin, xMax, yMin, yMax

def plotJunctions(netFilePath):
    print("coordUtils::plotJunctions")
    count = 0
    junctionList = parseJunctionList(netFilePath)
    for junction in junctionList:
        count += 1
        shape = junction.get("shape")
        if (shape is None or shape == ""):
            continue
        plotShape(shape)
        plotBoundingBox(shape)
    print("Plotted " + str(count) + " junctions")

# ============================================================================
# FOLDER STRUCTURE AND COMMON PARAMETER HANDLING
# ============================================================================

class SimulationConfig:
    """Configuration class for simulation parameters and paths."""
    
    def __init__(self):
        self.base_folder = None
        self.folder = None  # New parameter for non-recursive folder processing
        self.base_map_folder = None
        self.scenario = None
        self.mobility_file = None
        self.poly_file = None
        self.original_poly_file = None  # Store original poly file path for restoration
        self.circ_radius = 1000
        self.output_base = "./out"
        self.dpi = 150
        self.bbox_inches = 'tight'
        self.force_buildings = False  # New parameter to force building plotting
        self.building_mode = None  # Track detected building mode (b0/b1)
    
    def set_paths_from_scenario(self, base_map_folder, scenario):
        """
        Set mobility and poly file paths based on scenario name.
        
        Args:
            base_map_folder (str): Base folder containing map files
            scenario (str): Scenario name (e.g., 'Padova-25')
        """
        self.base_map_folder = base_map_folder
        self.scenario = scenario
        self.mobility_file = os.path.join(base_map_folder, scenario, scenario + ".ns2mobility.xml")
        self.original_poly_file = os.path.join(base_map_folder, scenario, scenario + ".poly.xml")
        self.poly_file = self.original_poly_file  # Set initial value
    
    def configure_buildings(self, building_mode, filename=None, verbose=False):
        """
        Configure building plotting based on building mode detection.
        
        Args:
            building_mode (str): Building mode from folder structure ('b0' or 'b1')
            filename (str, optional): Filename to check for additional building indicators
            verbose (bool): Enable verbose output
        """
        self.building_mode = building_mode
        
        # Check if buildings should be disabled
        should_disable_buildings = False
        
        if building_mode == 'b0':
            should_disable_buildings = True
            if verbose:
                print(f"Building mode 'b0' detected from folder structure - buildings disabled")
        
        # Additional check in filename if provided
        if filename and 'b0' in filename.lower():
            should_disable_buildings = True
            if verbose:
                print(f"'b0' detected in filename '{filename}' - buildings disabled")
        
        # Apply building configuration unless forced
        if should_disable_buildings and not self.force_buildings:
            if verbose:
                print("Setting poly_file to None (no buildings will be plotted)")
            self.poly_file = None
        elif self.force_buildings and self.original_poly_file:
            if verbose:
                print("Force buildings enabled - using original poly file")
            self.poly_file = self.original_poly_file
        elif building_mode == 'b1' or (filename and 'b1' in filename.lower()):
            if verbose:
                print("Building mode 'b1' detected - buildings enabled")
            self.poly_file = self.original_poly_file
    
    def validate_paths(self):
        """Validate that required files exist."""
        errors = []
        
        if self.mobility_file and not os.path.exists(self.mobility_file):
            errors.append(f"Mobility file not found: {self.mobility_file}")
        
        if self.poly_file and not os.path.exists(self.poly_file):
            # Poly file is optional, just warn
            print(f"Warning: Poly file not found: {self.poly_file}")
            self.poly_file = None
        
        if self.base_folder and not os.path.exists(self.base_folder):
            errors.append(f"Base folder not found: {self.base_folder}")
            
        if self.folder and not os.path.exists(self.folder):
            errors.append(f"Folder not found: {self.folder}")
        
        return errors

def parse_csv_path_structure(csv_path):
    """
    Parse CSV file path to extract scenario and folder structure information.
    Enhanced to handle sub-branch detection, scenario reconstruction, and optional cw level.
    
    Expected structures:
    - Standard: scenario/building/errorRate/txRange/junction/cw/Protocol/csv_filename
    - No CW: scenario/building/errorRate/txRange/junction/Protocol/csv_filename (e.g., ROFF)
    
    Examples: 
    - Padova-25/b0/e0/r300/j0/cw[32-1024]/Fast-Broadcast/filename.csv
    - Padova-25/b1/e0/r700/j0/ROFF/filename.csv
    
    Args:
        csv_path (str): Path to CSV file
        
    Returns:
        dict: Dictionary with extracted components or None if parsing fails
    """
    try:
        # Normalize path separators
        normalized_path = csv_path.replace('\\', '/')
        
        # Get directory path (remove filename)
        dir_path = os.path.dirname(normalized_path)
        csv_filename = os.path.basename(normalized_path)
        
        if not csv_filename.endswith('.csv'):
            return None
        
        # Try to extract scenario from filename first
        filename_parts = csv_filename.replace('.csv', '').split('-')
        potential_scenario = None
        
        # Look for scenario pattern in filename (e.g., "Padova-25")
        for i in range(len(filename_parts) - 1):
            potential_scenario_part = '-'.join(filename_parts[:i+2])
            if re.match(r'^[A-Za-z]+-\d+$', potential_scenario_part):
                potential_scenario = potential_scenario_part
                break
        
        # Use scenario detection to find the proper structure
        detection_result = detect_scenario_from_basepath(dir_path)
        
        # If we found a valid structure, use it
        if detection_result['structure_valid']:
            scenario_name = detection_result['scenario_name']
            
            # Parse the relative path from scenario to get components
            if detection_result['sub_path']:
                path_parts = detection_result['sub_path'].split('/')
            else:
                path_parts = []
            
            # Initialize with defaults
            components = {
                'scenario': scenario_name,
                'building': 'unknown',
                'error_rate': 'unknown',
                'txRange': 'unknown',
                'junction': 'unknown',
                'cw': 'unknown',
                'protocol': 'unknown',
                'csv_filename': csv_filename,
                'csv_path': csv_path
            }
            
            # Determine structure type by checking path patterns
            has_cw_level = False
            if len(path_parts) >= 5:
                # Check if 5th element matches cw pattern
                if re.match(r'^cw\[.*\]$', path_parts[4]):
                    has_cw_level = True
            
            # Map path parts to components based on structure type
            if len(path_parts) >= 1 and path_parts[0]:
                components['building'] = path_parts[0]
            if len(path_parts) >= 2:
                components['error_rate'] = path_parts[1]
            if len(path_parts) >= 3:
                components['txRange'] = path_parts[2]
            if len(path_parts) >= 4:
                components['junction'] = path_parts[3]
            
            if has_cw_level:
                # Standard structure with cw level
                if len(path_parts) >= 5:
                    components['cw'] = path_parts[4]
                if len(path_parts) >= 6:
                    components['protocol'] = path_parts[5]
            else:
                # Structure without cw level (e.g., ROFF)
                components['cw'] = 'none'  # Indicate no cw level
                if len(path_parts) >= 5:
                    components['protocol'] = path_parts[4]
            
            return components
        
        # Fallback to original parsing method with enhanced cw detection
        path_parts = normalized_path.split('/')
        
        # Try both structures:
        # Standard: filename, Protocol, cw, junction, txRange, errorRate, building, scenario (8 parts minimum)
        # No CW: filename, Protocol, junction, txRange, errorRate, building, scenario (7 parts minimum)
        
        if len(path_parts) >= 8:
            # Try standard structure first
            potential_cw = path_parts[-3]
            if re.match(r'^cw\[.*\]$', potential_cw):
                # Standard structure with cw
                protocol = path_parts[-2]
                cw = potential_cw
                junction = path_parts[-4]
                txRange = path_parts[-5]
                error_rate = path_parts[-6]
                building = path_parts[-7]
                scenario = path_parts[-8]
                
                return {
                    'scenario': scenario,
                    'building': building,
                    'error_rate': error_rate,
                    'txRange': txRange,
                    'junction': junction,
                    'cw': cw,
                    'protocol': protocol,
                    'csv_filename': csv_filename,
                    'csv_path': csv_path
                }
        
        if len(path_parts) >= 7:
            # Try structure without cw
            protocol = path_parts[-2]
            junction = path_parts[-3]
            txRange = path_parts[-4]
            error_rate = path_parts[-5]
            building = path_parts[-6]
            scenario = path_parts[-7]
            
            return {
                'scenario': scenario,
                'building': building,
                'error_rate': error_rate,
                'txRange': txRange,
                'junction': junction,
                'cw': 'none',  # No cw level
                'protocol': protocol,
                'csv_filename': csv_filename,
                'csv_path': csv_path
            }
        
        return None
        
    except (IndexError, ValueError):
        return None

def find_csv_files(base_folder, max_files_per_protocol=3):
    """
    Find all CSV files in the folder structure and return them organized.
    
    Args:
        base_folder (str): Base folder to search
        max_files_per_protocol (int): Maximum files to process per protocol
        
    Returns:
        list: List of dictionaries with CSV file information
    """
    csv_files = []
    
    if not os.path.exists(base_folder):
        print(f"Error: Base folder does not exist: {base_folder}")
        return csv_files
    
    print(f"Scanning folder structure in: {base_folder}")
    
    for root, dirs, files in os.walk(base_folder):
        protocol_file_count = 0
        for filename in files:
            if not filename.endswith('.csv'):
                continue
            
            if protocol_file_count >= max_files_per_protocol:
                break
                
            csv_path = os.path.join(root, filename)
            
            # Check if file is complete
            if not isFileComplete(csv_path):
                continue
            
            # Parse the path structure
            path_info = parse_csv_path_structure(csv_path)
            if path_info:
                csv_files.append(path_info)
                protocol_file_count += 1
    
    print(f"Found {len(csv_files)} valid CSV files")
    return csv_files

def find_csv_files_in_folder(folder_path, max_files=None):
    """
    Find all CSV files directly in the specified folder (non-recursive).
    
    Args:
        folder_path (str): Folder to search for CSV files
        max_files (int, optional): Maximum number of files to process
        
    Returns:
        list: List of dictionaries with CSV file information
    """
    csv_files = []
    
    if not os.path.exists(folder_path):
        print(f"Error: Folder does not exist: {folder_path}")
        return csv_files
    
    print(f"Scanning CSV files in folder: {folder_path}")
    
    # Get all files directly in the folder (non-recursive)
    try:
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    except OSError as e:
        print(f"Error reading folder {folder_path}: {e}")
        return csv_files
    
    file_count = 0
    for filename in sorted(files):  # Sort for consistent processing order
        if not filename.endswith('.csv'):
            continue
        
        if max_files is not None and file_count >= max_files:
            break
            
        csv_path = os.path.join(folder_path, filename)
        
        # Check if file is complete
        if not isFileComplete(csv_path):
            print(f"Skipping incomplete file: {filename}")
            continue
        
        # Try to parse the path structure - this might fail for files not following the expected structure
        path_info = parse_csv_path_structure(csv_path)
        if path_info:
            csv_files.append(path_info)
        else:
            # If parsing fails, create a basic structure
            csv_files.append({
                'scenario': 'unknown',
                'building': 'unknown',
                'error_rate': 'unknown', 
                'txRange': 'unknown',
                'junction': 'unknown',
                'cw': 'unknown',
                'protocol': 'unknown',
                'csv_filename': filename,
                'csv_path': csv_path
            })
        
        file_count += 1
    
    print(f"Found {len(csv_files)} valid CSV files")
    return csv_files

def setup_common_argument_parser(description="Simulation analysis tool"):
    """
    Create an argument parser with common parameters used by multiple scripts.
    Implements mandatory argument groups as specified.
    
    Args:
        description (str): Description for the argument parser
        
    Returns:
        argparse.ArgumentParser: Configured argument parser
    """
    parser = argparse.ArgumentParser(description=description, 
                                   formatter_class=argparse.RawDescriptionHelpFormatter)
    
    # Create mutually exclusive group for file processing options (one is mandatory)
    file_group = parser.add_mutually_exclusive_group(required=True)
    file_group.add_argument('-f', '--file', 
                           help='Single CSV file to process')
    file_group.add_argument('-d', '--folder',
                           help='Folder containing CSV files to process (non-recursive)')
    file_group.add_argument('-b', '--basefolder', 
                           help='Base folder for batch processing (recursive)')
    
    # Create mutually exclusive group for mobility source (one is mandatory)  
    mobility_group = parser.add_mutually_exclusive_group(required=True)
    mobility_group.add_argument('-m', '--mobility', 
                               help='NS2 mobility file path')
    mobility_group.add_argument('--mapfolder', 
                               help='Base map folder containing scenario subdirectories')
    
    # Optional arguments
    parser.add_argument('-p', '--poly', 
                       help='Polygon/building file path (optional)')
    parser.add_argument('-r', '--radius', type=int, 
                       help='Transmission radius in meters (default: 1000 for non-Grid scenarios, 2000 for Grid scenarios)')
    parser.add_argument('-o', '--output', default='./out',
                       help='Output base directory (default: ./out)')
    parser.add_argument('--maxfiles', type=int, default=3,
                       help='Maximum files to process per protocol for -b, or total files for -d (default: 3)')
    parser.add_argument('--dpi', type=int, default=150,
                       help='DPI for output images (default: 150)')
    parser.add_argument('--force-buildings', action='store_true',
                       help='Force building plotting regardless of b0/b1 detection')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Enable verbose output')
    
    return parser

def determine_default_radius(scenario_name):
    """
    Determine default radius based on scenario name.
    
    Args:
        scenario_name (str): Name of the scenario
        
    Returns:
        int: Default radius (2000 for Grid scenarios, 1000 for others)
    """
    if scenario_name and "Grid" in scenario_name:
        return 2000
    return 1000

def process_common_arguments(args, additional_args=None):
    """
    Process common arguments and return a SimulationConfig object.
    
    Args:
        args: Parsed arguments from argparse
        additional_args: Additional arguments configuration
        
    Returns:
        SimulationConfig: Configured simulation config object
    """
    config = SimulationConfig()
    
    # Determine scenario name for radius calculation
    scenario_name = None
    
    # Try to extract scenario from file path if single file provided
    if args.file:
        path_info = parse_csv_path_structure(args.file)
        if path_info:
            scenario_name = path_info['scenario']
    
    # Try to extract scenario from folder name if folder provided
    elif args.folder:
        # Use folder name as scenario name
        scenario_name = os.path.basename(args.folder.rstrip('/\\'))
    
    # Try to detect scenario from base folder if batch processing
    elif args.basefolder:
        detection_result = detect_scenario_from_basepath(args.basefolder)
        if detection_result['structure_valid']:
            scenario_name = detection_result['scenario_name']
        else:
            # Fallback to folder name
            scenario_name = os.path.basename(args.basefolder.rstrip('/\\'))
    
    # Set radius with conditional default
    if args.radius is not None:
        config.circ_radius = args.radius
    else:
        config.circ_radius = determine_default_radius(scenario_name)
    
    # Set basic parameters
    config.base_folder = args.basefolder
    config.folder = args.folder
    config.output_base = args.output
    config.base_map_folder = args.mapfolder
    config.dpi = args.dpi
    config.verbose = args.verbose
    config.force_buildings = args.force_buildings
    
    # Handle script-specific arguments dynamically
    if additional_args:
        for arg_config in additional_args:
            arg_name = arg_config['name'].lstrip('-').replace('-', '_')  # Convert --show-nodes to show_nodes
            if hasattr(args, arg_name):
                setattr(config, arg_name, getattr(args, arg_name))
    
    # Handle legacy script-specific arguments that might be present
    if hasattr(args, 'maxfiles'):
        config.max_files_per_protocol = args.maxfiles
    
    # Handle mobility and poly files
    if args.mobility:
        config.mobility_file = args.mobility
    if args.poly:
        config.poly_file = args.poly
        config.original_poly_file = args.poly
    
    # If map folder is provided and we have a single file, try to extract scenario
    if args.mapfolder and args.file:
        path_info = parse_csv_path_structure(args.file)
        if path_info:
            config.set_paths_from_scenario(args.mapfolder, path_info['scenario'])
            # Configure buildings for single file
            config.configure_buildings(path_info['building'], path_info['csv_filename'], args.verbose)
    
    return config

def add_script_specific_arguments(parser, additional_args):
    """
    Add script-specific arguments to the parser.
    
    Args:
        parser: ArgumentParser instance
        additional_args: List of argument configurations
    """
    if not additional_args:
        return
        
    for arg_config in additional_args:
        # Make a copy to avoid modifying the original
        arg_config_copy = arg_config.copy()
        arg_name = arg_config_copy.pop('name')
        parser.add_argument(arg_name, **arg_config_copy)
        
def validate_folder_structure_from_scenario_enhanced(scenario_path, target_path):
    """
    Validate that the folder structure from scenario to target follows the expected pattern.
    Enhanced to handle optional cw level and better structure validation.
    
    Args:
        scenario_path (str): Path to the scenario root
        target_path (str): Path to validate against
        
    Returns:
        bool: True if structure is valid
    """
    if not os.path.exists(scenario_path):
        return False
    
    try:
        rel_path = os.path.relpath(target_path, scenario_path)
        if rel_path == '.':
            return True  # target_path is the scenario_path itself
        
        path_parts = rel_path.split(os.sep)
        
        # Structure patterns for validation
        patterns = {
            'building': r'^b[01]$',          # "b0" or "b1"
            'error_rate': r'^e\d+$',         # e.g., "e0"
            'txRange': r'^r\d+$',            # e.g., "r300"
            'junction': r'^j\d+$',           # e.g., "j0"
            'cw': r'^cw\[.*\]$',            # e.g., "cw[32-1024]"
            'protocol': r'^[A-Za-z-]+$',     # e.g., "Fast-Broadcast" or "ROFF"
        }
        
        return validate_structure_parts(path_parts, patterns)
        
    except (ValueError, OSError):
        return False

def generate_output_path(path_info, output_base, suffix):
    """
    Generate output file path based on CSV path structure.
    Enhanced to handle optional cw level.
    
    Creates structure:
    - Standard: scenario/building/error_rate/txRange/junction/cw/protocol/filename/filename.ext
    - No CW: scenario/building/error_rate/txRange/junction/protocol/filename/filename.ext
    
    Args:
        path_info (dict): Path information from parse_csv_path_structure
        output_base (str): Base output directory
        suffix (str): File suffix (default: ".png")
        
    Returns:
        str: Generated output path
    """
    filename_no_ext = os.path.splitext(path_info['csv_filename'])[0]
    output_filename = filename_no_ext + suffix + ".png"
    
    # Build path components
    path_components = [
        output_base,
        path_info['scenario'],
        path_info['building'],
        path_info['error_rate'],
        path_info['txRange'],
        path_info['junction']
    ]
    
    # Add cw level only if it exists (not 'none')
    if path_info['cw'] != 'none':
        path_components.append(path_info['cw'])
    
    # Add protocol, filename directory, and final filename
    path_components.extend([
        path_info['protocol'],
        filename_no_ext,  # Add filename as directory
        output_filename
    ])
    
    output_path = os.path.join(*path_components)
    return output_path

def ensure_output_directory(file_path):
    """
    Ensure that the directory for the given file path exists.
    Includes protection against race conditions when used with multiprocessing.
    
    Args:
        file_path (str): Full path to the output file
        
    Returns:
        bool: True if directory exists or was created successfully, False otherwise
    """
    directory = os.path.dirname(file_path)
    
    if not directory:  # Handle case where file_path has no directory component
        return True
        
    try:
        os.makedirs(directory, exist_ok=True)
        return True
    except OSError as exc:  # Guard against race condition
        if exc.errno != errno.EEXIST:
            print(f"Error creating directory {directory}: {exc}")
            return False
        # If errno is EEXIST, directory already exists (race condition), which is fine
        return True

def validate_folder_structure_from_scenario(scenario_path, target_path):
    """
    Validate that the folder structure from scenario to target follows the expected pattern.
    
    Args:
        scenario_path (str): Path to the scenario root
        target_path (str): Path to validate against
        
    Returns:
        bool: True if structure is valid
    """
    if not os.path.exists(scenario_path):
        return False
    
    try:
        rel_path = os.path.relpath(target_path, scenario_path)
        if rel_path == '.':
            return True  # target_path is the scenario_path itself
        
        path_parts = rel_path.split(os.sep)
        
        # Structure patterns (same as in detect_scenario_from_basepath)
        structure_patterns = [
            r'^b[01]$',          # building: "b0" or "b1"
            r'^e\d+$',           # errorRate: e.g., "e0"
            r'^r\d+$',           # txRange: e.g., "r300"
            r'^j\d+$',           # junction: e.g., "j0"
            r'^cw\[.*\]$',       # cw: e.g., "cw[32-1024]"
            r'^[A-Za-z-]+$',     # protocol: e.g., "Fast-Broadcast"
        ]
        
        # Validate each part against expected pattern
        for i, part in enumerate(path_parts):
            if i >= len(structure_patterns):
                break  # More levels than expected, but still valid
            if not re.match(structure_patterns[i], part):
                return False
        
        return True
        
    except (ValueError, OSError):
        return False
def detect_scenario_from_basepath(base_folder):
    """
    Detect if the provided base folder is a sub-branch of the expected structure
    and try to reconstruct the full scenario path by going backwards.
    Enhanced to handle optional cw level and better scenario detection.
    
    Expected structures:
    - Standard: scenario/building/errorRate/txRange/junction/cw/Protocol/
    - No CW: scenario/building/errorRate/txRange/junction/Protocol/
    
    Args:
        base_folder (str): Base folder path that might be a sub-branch
        
    Returns:
        dict: Dictionary containing:
            - 'scenario_path': Full path to scenario root
            - 'scenario_name': Name of the scenario
            - 'sub_path': Relative path from scenario to base_folder
            - 'is_sub_branch': Whether base_folder is a sub-branch
            - 'structure_valid': Whether the detected structure is valid
    """
    result = {
        'scenario_path': base_folder,
        'scenario_name': os.path.basename(base_folder.rstrip('/\\')),
        'sub_path': '',
        'is_sub_branch': False,
        'structure_valid': False
    }
    
    # Normalize path
    normalized_path = os.path.normpath(base_folder.rstrip('/\\'))
    path_parts = normalized_path.split(os.sep)
    
    if len(path_parts) == 0:
        return result
    
    # Structure patterns for validation
    structure_patterns = {
        'scenario': r'^[A-Za-z]+-\d+$',  # e.g., "Padova-25", "Grid-100"
        'building': r'^b[01]$',          # "b0" or "b1"
        'error_rate': r'^e\d+$',         # e.g., "e0"
        'txRange': r'^r\d+$',            # e.g., "r300"
        'junction': r'^j\d+$',           # e.g., "j0"
        'cw': r'^cw\[.*\]$',            # e.g., "cw[32-1024]" (optional)
        'protocol': r'^[A-Za-z-]+$',     # e.g., "Fast-Broadcast" or "ROFF"
    }
    
    # Try to find the scenario by going backwards through the path
    current_path = normalized_path
    levels_back = 0
    
    while current_path and levels_back < 10:  # Max 10 levels to prevent infinite loops
        current_basename = os.path.basename(current_path)
        
        # Check if current basename matches scenario pattern
        if re.match(structure_patterns['scenario'], current_basename):
            # Found potential scenario, now validate the structure from scenario to original path
            try:
                rel_path = os.path.relpath(normalized_path, current_path)
                
                # If the relative path is just '.', we're at the scenario level
                if rel_path == '.':
                    result['scenario_path'] = current_path
                    result['scenario_name'] = current_basename
                    result['sub_path'] = ''
                    result['is_sub_branch'] = False
                    result['structure_valid'] = True
                    break
                
                # Parse the relative path to validate structure
                rel_path_parts = rel_path.split(os.sep)
                
                # Check if the structure is valid
                if validate_structure_parts(rel_path_parts, structure_patterns):
                    result['scenario_path'] = current_path
                    result['scenario_name'] = current_basename
                    result['sub_path'] = rel_path
                    result['is_sub_branch'] = levels_back > 0
                    result['structure_valid'] = True
                    break
                    
            except (ValueError, OSError):
                pass  # Continue searching
        
        # Move up one level
        parent_path = os.path.dirname(current_path)
        if parent_path == current_path:  # Reached root
            break
        current_path = parent_path
        levels_back += 1
    
    return result

def validate_structure_parts(path_parts, patterns):
    """
    Validate that path parts follow the expected structure.
    
    Args:
        path_parts (list): List of path components from scenario to target
        patterns (dict): Dictionary of regex patterns for validation
        
    Returns:
        bool: True if structure is valid
    """
    if not path_parts:
        return True  # Empty path is valid (we're at scenario level)
    
    # Define the expected order of components
    expected_order = ['building', 'error_rate', 'txRange', 'junction', 'cw', 'protocol']
    
    # Check if we have cw level by looking at the appropriate position
    has_cw_level = False
    if len(path_parts) >= 5:
        # Check if the 5th element (index 4) matches cw pattern
        if re.match(patterns['cw'], path_parts[4]):
            has_cw_level = True
    
    # Define expected patterns based on structure type
    if has_cw_level:
        # Standard structure: building/errorRate/txRange/junction/cw/protocol
        expected_patterns = [
            patterns['building'],
            patterns['error_rate'],
            patterns['txRange'],
            patterns['junction'],
            patterns['cw'],
            patterns['protocol']
        ]
    else:
        # Structure without cw: building/errorRate/txRange/junction/protocol
        expected_patterns = [
            patterns['building'],
            patterns['error_rate'],
            patterns['txRange'],
            patterns['junction'],
            patterns['protocol']
        ]
    
    # Validate each part against expected pattern
    min_required_parts = min(len(path_parts), len(expected_patterns))
    
    for i in range(min_required_parts):
        if not re.match(expected_patterns[i], path_parts[i]):
            return False
    
    # If we have more parts than expected patterns, that's also invalid
    # (unless it's just filename-level stuff which we can ignore)
    if len(path_parts) > len(expected_patterns):
        # Allow additional levels for files/directories beyond the expected structure
        pass
    
    return True
    
def generic_process_single_file(csv_file, config, output_file, plot_function, output_subfolder="plots", single_output_subfolder="singlefile"):
    """
    Generic function to process a single CSV file.
    
    Args:
        csv_file (str): Path to CSV file
        config (SimulationConfig): Configuration object
        output_file (str, optional): Custom output file path
        plot_function (callable): Function to call for plotting
        output_subfolder (str): Subfolder name for organized batch outputs
        single_output_subfolder (str): Subfolder name for single file outputs
        
    Returns:
        bool: True if successful, False otherwise
    """
    print(f"Processing single file: {csv_file}")
    
    if not os.path.exists(csv_file):
        print(f"Error: CSV file does not exist: {csv_file}")
        return False
    
    # Check if file is complete
    if not isFileComplete(csv_file):
        print(f"Error: CSV file appears incomplete: {csv_file}")
        return False
    
    # Configure buildings if not already done
    path_info = parse_csv_path_structure(csv_file)
    if path_info and not hasattr(config, 'building_mode'):
        config.configure_buildings(path_info['building'], path_info['csv_filename'], config.verbose)
    
    if config.verbose:
        print(f"Building configuration: mode='{config.building_mode}', "
              f"poly_file={'None' if config.poly_file is None else 'enabled'}, "
              f"force_buildings={config.force_buildings}")
    
    # Generate output path
    show_nodes=""
    if hasattr(config, 'show_nodes') and config.show_nodes:
        show_nodes = "-show-nodes"
    
    if output_file:
        output_path = output_file
    else:
        # Try to parse path structure for organized output
        if path_info:
            output_path = generate_output_path(path_info, 
                                             os.path.join(config.output_base, output_subfolder), show_nodes)
        else:
            # Fallback to simple output
            csv_filename = os.path.basename(csv_file)
            output_filename = os.path.splitext(csv_filename)[0] + show_nodes + ".png"
            output_path = os.path.join(config.output_base, single_output_subfolder, output_filename)
    
    # Call the plotting function
    return plot_function(csv_file, output_path, config)

def generic_process_folder(config, plot_function, output_subfolder="plots", verbose_mode=False):
    """
    Generic function to process all CSV files in a single folder (non-recursive).
    
    Args:
        config (SimulationConfig): Configuration object
        plot_function (callable): Function to call for plotting
        output_subfolder (str): Subfolder name for organized batch outputs
        verbose_mode (bool): Enable verbose output
        
    Returns:
        dict: Statistics about processing
    """
    print(f"Processing CSV files from folder: {config.folder}")
    
    # Find all CSV files in the folder
    max_files = getattr(config, 'max_files_per_protocol', None)
    csv_files = find_csv_files_in_folder(config.folder, max_files=max_files)
    
    if not csv_files:
        print("No valid CSV files found in the specified folder")
        return {'processed_count': 0, 'successful_count': 0, 'failed_count': 0}
    
    processed_count = 0
    successful_count = 0
    
    # Try to determine scenario from the first file that has proper structure
    scenario_name = None
    for file_info in csv_files:
        if file_info['scenario'] != 'unknown':
            scenario_name = file_info['scenario']
            break
    
    # If no scenario found from file structure, use folder name as fallback
    if not scenario_name:
        scenario_name = os.path.basename(config.folder.rstrip('/\\'))
    
    print(f"Detected/using scenario: {scenario_name}")
    
    # Set up scenario paths if we have a map folder and detected a valid scenario
    if config.base_map_folder and scenario_name != 'unknown':
        config.set_paths_from_scenario(config.base_map_folder, scenario_name)
    
    for file_info in csv_files:
        processed_count += 1
        
        print(f"\nProcessing file {processed_count}/{len(csv_files)}: {file_info['csv_filename']}")
        
        # Configure buildings for this specific file
        if file_info['building'] != 'unknown':
            config.configure_buildings(file_info['building'], file_info['csv_filename'], verbose_mode)
            
            if verbose_mode:
                print(f"  Building mode: {config.building_mode}")
                print(f"  Buildings enabled: {'No' if config.poly_file is None else 'Yes'}")
                print(f"  Force buildings: {config.force_buildings}")
        
        if verbose_mode:
            print(f"  Base map folder: {config.base_map_folder}")
            print(f"  Mobility file: {config.mobility_file}")
            print(f"  Poly file: {config.poly_file}")
        
        # Validate paths for this file
        errors = config.validate_paths()
        if errors:
            print(f"Skipping file due to missing required files:")
            for error in errors:
                print(f"  - {error}")
            continue
        
        # Generate output path        
        show_nodes=""
        if hasattr(config, 'show_nodes') and config.show_nodes:
            show_nodes = "-show-nodes" 
                   
        if file_info['scenario'] != 'unknown':
            # Use proper structure if available
            file_info_copy = file_info.copy()
            file_info_copy['scenario'] = scenario_name
            output_path = generate_output_path(file_info_copy, 
                                             os.path.join(config.output_base, output_subfolder), show_nodes)
        else:
            # Fallback to simple structure for files without proper path structure
            filename_no_ext = os.path.splitext(file_info['csv_filename'])[0]
            output_filename = filename_no_ext + show_nodes + ".png"
            output_path = os.path.join(config.output_base, output_subfolder, 
                                     scenario_name, "unknown", filename_no_ext, output_filename)
        
        # Call the plotting function
        if plot_function(file_info['csv_path'], output_path, config):
            successful_count += 1
    
    failed_count = processed_count - successful_count
    
    print(f"\nFolder processing completed.")
    print(f"Processed: {processed_count} files")
    print(f"Successful: {successful_count} files")
    print(f"Failed: {failed_count} files")
    
    return {
        'processed_count': processed_count,
        'successful_count': successful_count,
        'failed_count': failed_count
    }

def generic_process_batch(config, plot_function, output_subfolder="plots", verbose_mode=False):
    """
    Generic function to process multiple files in batch mode using the folder structure.
    Enhanced to handle sub-branch detection and proper scenario reconstruction.
    
    Args:
        config (SimulationConfig): Configuration object
        plot_function (callable): Function to call for plotting
        output_subfolder (str): Subfolder name for organized batch outputs
        verbose_mode (bool): Enable verbose output
        
    Returns:
        dict: Statistics about processing
    """
    print(f"Processing batch from base folder: {config.base_folder}")
    
    # Detect if base folder is a sub-branch and get scenario information
    detection_result = detect_scenario_from_basepath(config.base_folder)
    
    if verbose_mode:
        print(f"Folder structure detection:")
        print(f"  Is sub-branch: {detection_result['is_sub_branch']}")
        print(f"  Structure valid: {detection_result['structure_valid']}")
        print(f"  Detected scenario: {detection_result['scenario_name']}")
        print(f"  Scenario path: {detection_result['scenario_path']}")
        print(f"  Sub-path: {detection_result['sub_path']}")
    
    # Use detected scenario information
    if detection_result['structure_valid']:
        scenario_name = detection_result['scenario_name']
        scenario_path = detection_result['scenario_path']
        
        print(f"Detected scenario: {scenario_name}")
        if detection_result['is_sub_branch']:
            print(f"Processing sub-branch: {detection_result['sub_path']}")
            print(f"Full scenario path: {scenario_path}")
    else:
        # Fallback: use original behavior
        scenario_name = os.path.basename(config.base_folder.rstrip('/\\'))
        scenario_path = config.base_folder
        print(f"Using fallback scenario detection: {scenario_name}")
    
    # Find all CSV files in the folder structure
    csv_files = find_csv_files(config.base_folder, max_files_per_protocol=getattr(config, 'max_files_per_protocol', 3))
    
    if not csv_files:
        print("No valid CSV files found in the specified folder structure")
        return {'processed_count': 0, 'successful_count': 0, 'failed_count': 0}
    
    processed_count = 0
    successful_count = 0
    
    for file_info in csv_files:
        processed_count += 1
        
        print(f"\nProcessing file {processed_count}/{len(csv_files)}: {file_info['csv_filename']}")
        
        # Set up paths for this scenario if we have map folder
        if config.base_map_folder:
            temp_config = SimulationConfig()
            temp_config.__dict__.update(config.__dict__)  # Copy all settings
            temp_config.set_paths_from_scenario(config.base_map_folder, scenario_name)
            
            # Configure buildings for this specific file
            temp_config.configure_buildings(file_info['building'], file_info['csv_filename'], verbose_mode)
            
            if verbose_mode:
                print(f"  Building mode: {temp_config.building_mode}")
                print(f"  Buildings enabled: {'No' if temp_config.poly_file is None else 'Yes'}")
                print(f"  Force buildings: {temp_config.force_buildings}")
                print(f"  Base map folder: {temp_config.base_map_folder}")
                print(f"  Mobility file: {temp_config.mobility_file}")
                print(f"  Poly file: {temp_config.poly_file}")
        else:
            temp_config = config
        
        # Validate paths for this file
        errors = temp_config.validate_paths()
        if errors:
            print(f"Skipping file due to missing required files:")
            for error in errors:
                print(f"  - {error}")
            continue
        
        # Generate output path - use detected scenario name for proper structure
        show_nodes=""
        if hasattr(config, 'show_nodes') and config.show_nodes:
            show_nodes = "-show-nodes"
        
        file_info_copy = file_info.copy()
        file_info_copy['scenario'] = scenario_name
        output_path = generate_output_path(file_info_copy, 
                                         os.path.join(config.output_base, output_subfolder),show_nodes)
        
        if verbose_mode:
            print(f"  Output path: {output_path}")
        
        # Call the plotting function
        if plot_function(file_info['csv_path'], output_path, temp_config):
            successful_count += 1
    
    failed_count = processed_count - successful_count
    
    print(f"\nBatch processing completed.")
    print(f"Processed: {processed_count} files")
    print(f"Successful: {successful_count} files")
    print(f"Failed: {failed_count} files")
    
    return {
        'processed_count': processed_count,
        'successful_count': successful_count,
        'failed_count': failed_count
    }
    
def generic_main(script_config):
    """
    Generic main function to handle command line arguments and execute appropriate actions.
    
    Args:
        script_config (dict): Configuration dictionary containing:
            - description (str): Script description for argument parser
            - tool_name (str): Name to display when running
            - output_subfolder (str): Default output subfolder name
            - single_output_subfolder (str): Single file output subfolder name  
            - default_base_map_folder (str): Default map folder path
            - plot_function (callable): Function to call for plotting
            - additional_args (list, optional): Additional arguments for argument parser
    """
    
    # Set up argument parser with common parameters
    parser = setup_common_argument_parser(
        description=script_config['description']
    )
    
    # Add any script-specific arguments
    if 'additional_args' in script_config:
        add_script_specific_arguments(parser, script_config['additional_args'])
    
    # Parse arguments
    args = parser.parse_args()
    
    # Process common arguments
    additional_args = script_config.get('additional_args', None)
    config = process_common_arguments(args, additional_args)
    
    # Set default map folder if not provided
    if not config.base_map_folder and not args.mobility:
        config.base_map_folder = script_config.get('default_base_map_folder')
    
    print(script_config['tool_name'])
    print(f"Transmission radius: {config.circ_radius}m")
    print(f"Force buildings: {'Yes' if config.force_buildings else 'No'}")
    
    if args.verbose:
        print(f"Configuration:")
        print(f"  Base folder: {config.base_folder}")
        print(f"  Folder: {config.folder}")
        print(f"  Base map folder: {config.base_map_folder}")
        print(f"  Mobility file: {config.mobility_file}")
        print(f"  Poly file: {config.poly_file}")
        print(f"  Output base: {config.output_base}")
        print(f"  Force buildings: {config.force_buildings}")
    
    # Determine mode of operation
    if args.file:
        # Single file mode
        output_single = getattr(args, 'output_single', None)
        success = generic_process_single_file(
            args.file, 
            config, 
            output_single, 
            script_config['plot_function'],
            script_config['output_subfolder'],
            script_config['single_output_subfolder']
        )
        if not success:
            sys.exit(1)
            
    elif args.folder:
        # Folder mode (non-recursive)
        if not config.base_map_folder and not config.mobility_file:
            print("Error: Either map folder or explicit mobility file is required for folder processing")
            print("Use --mapfolder or -m/--mobility option")
            sys.exit(2)
        
        stats = generic_process_folder(
            config, 
            script_config['plot_function'], 
            script_config['output_subfolder'],
            args.verbose
        )
        
        # Exit with error code if any files failed
        if stats['failed_count'] > 0:
            sys.exit(1)
            
    elif args.basefolder:
        # Batch mode (recursive)
        if not config.base_map_folder and not config.mobility_file:
            print("Error: Either map folder or explicit mobility file is required for batch processing")
            print("Use --mapfolder or -m/--mobility option")
            sys.exit(2)
        
        stats = generic_process_batch(
            config, 
            script_config['plot_function'], 
            script_config['output_subfolder'],
            args.verbose
        )
        
        # Exit with error code if any files failed
        if stats['failed_count'] > 0:
            sys.exit(1)
        
    else:
        # No arguments provided
        print("Error: Please specify either a single file (-f), folder (-d), or base folder (-b) for processing")
        print("Use -h/--help for usage information")
        sys.exit(2)