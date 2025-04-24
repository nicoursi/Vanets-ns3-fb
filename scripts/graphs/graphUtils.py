#!/usr/bin/python

import os
import sys
import getopt
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import string
import shutil
import csv
import scipy.stats as st
import math

def countLinesInCsv(csv):
	return sum(1 for row in csv)

def calculateMeanAndConfInt(list, static=False, castToInt=False):
	npArray = np.array(list)
	print(npArray)
	mean = round(np.mean(npArray), 2)
	if (static is True):
		mean *= 1.1
		mean = round(mean, 2)
	if (castToInt is True):
		mean = (int) (round(mean))
	confInt = st.t.interval(0.95, len(npArray)-1, loc=np.mean(npArray), scale=st.sem(npArray))
	confIntAmplitude = confInt[1] - confInt[0]
	return mean, confIntAmplitude / 4;

#def readCsvFromDirectory(path, roff=False, static=False):
#	totalNodes = []
#	nodesOnCirc = []
#	totalCoverage = []
#	covOnCirc = []
#	hops = []
#	slots = []
#	messageSent = []
#	totalCoveragePercent = []
#	covOnCircPercent = []
#	for fileName in os.listdir(path):
#		#deleteBecauseEmpty = False
#		fullPath = os.path.join(path, fileName)
#		if not os.path.isfile(fullPath) or not fileName.endswith(".csv"):
#			continue  # Skip directories and non-CSV files
#		with open(fullPath, "r") as file:
#			csvFile = csv.reader(file, delimiter=",")
#			firstLine = True
#			if (countLinesInCsv(csvFile) != 2):
#				#deleteBecauseEmpty = True
#				continue
#			else:
#				file.seek(0)
#				firstLineRef = 0
#				for row in csvFile:
#					if (firstLine):
#						firstLine = False
#						firstLineRef = row
#						continue
#					totalNodes.append(int(row[5]))
#					nodesOnCirc.append(int(row[6]))
#					totalCoverage.append(int(row[7]))
#					covOnCirc.append(int(row[8]))
#					if (not math.isnan(float(row[10]))):
#						hops.append(float(row[10]))
#					if (not math.isnan(float(row[11]))):
#						slots.append(float(row[11]))
#					messageSent.append(int(row[12]))
#					totalCoveragePercent.append(((float(totalCoverage[-1]) / float(totalNodes[-1])) * 100))
#					covOnCircPercent.append(((float(covOnCirc[-1]) / float(nodesOnCirc[-1])) * 100))
#		#if (deleteBecauseEmpty == True):
#			#os.remove(fullPath)
#	print(path)
#	totalCovMean , totalCovConfInt = calculateMeanAndConfInt(totalCoveragePercent)
#	covOnCircMean, covOnCircConfInt = calculateMeanAndConfInt(covOnCircPercent)
#	hopsMean, hopsConfInt = calculateMeanAndConfInt(hops, static)
#	messageSentMean, messageSentConfInt = calculateMeanAndConfInt(messageSent, False, True)
#	slotsWaitedMean, slotsWaitedConfInt = calculateMeanAndConfInt(slots, False, True)
#
#	#print(slotsWaitedMean)
#	#if (roff is True):
#		#slotsWaitedMean = (int) (round(slotsWaitedMean - hopsMean))
#
#	return {"totCoverageMean": totalCovMean,
#			"totCoverageConfInt": totalCovConfInt,
#			"covOnCircMean": covOnCircMean,
#			"covOnCircConfInt": covOnCircConfInt,
#			"hopsMean": hopsMean,
#			"hopsConfInt": hopsConfInt,
#			"messageSentMean": messageSentMean,
#			"messageSentConfInt": messageSentConfInt,
#			"slotsWaitedMean": slotsWaitedMean,
#			"slotsWaitedConfInt": slotsWaitedConfInt
#	}

def readCsvFromDirectory(path, roff=False, static=False):
    totalNodes = []
    nodesOnCirc = []
    totalCoverage = []
    covOnCirc = []
    hops = []
    slots = []
    messageSent = []
    totalCoveragePercent = []
    covOnCircPercent = []

    for fileName in os.listdir(path):
        fullPath = os.path.join(path, fileName)
        if not os.path.isfile(fullPath) or not fileName.endswith(".csv"):
            continue

        with open(fullPath, "r") as file:
            rows = list(csv.reader(file, delimiter=","))
            if len(rows) <= 1:
                print(f"Skipping empty or malformed file: {fileName}")
                continue

            for i, row in enumerate(rows[1:]):
                try:
                    # Skip if critical fields are NaN or empty
                    if any([
                        not row[5] or not row[6] or not row[7] or not row[8],
                        row[10] in ("", "-nan", "nan"),
                        row[11] in ("", "-nan", "nan"),
                        row[12] in ("", "-nan", "nan"),
                    ]):
                        print(f"Skipping incomplete row in {fileName} line {i + 2}: {row}")
                        continue

                    totalNodes.append(int(row[5]))
                    nodesOnCirc.append(int(row[6]))
                    totalCoverage.append(int(row[7]))
                    covOnCirc.append(int(row[8]))

                    hops.append(float(row[10]))
                    slots.append(float(row[11]))
                    messageSent.append(int(row[12]))

                    totalCoveragePercent.append(
                        (float(totalCoverage[-1]) / float(totalNodes[-1])) * 100
                    )
                    covOnCircPercent.append(
                        (float(covOnCirc[-1]) / float(nodesOnCirc[-1])) * 100
                    )

                except Exception as e:
                    print(f"Skipping bad row in {fileName} line {i + 2}: {row}")
                    print(f" -> {e}")
                    continue

    print(f"Finished reading: {path}")

    totalCovMean, totalCovConfInt = calculateMeanAndConfInt(totalCoveragePercent)
    covOnCircMean, covOnCircConfInt = calculateMeanAndConfInt(covOnCircPercent)
    hopsMean, hopsConfInt = calculateMeanAndConfInt(hops, static)
    messageSentMean, messageSentConfInt = calculateMeanAndConfInt(messageSent, False, True)
    slotsWaitedMean, slotsWaitedConfInt = calculateMeanAndConfInt(slots, False, True)

    return {
        "totCoverageMean": totalCovMean,
        "totCoverageConfInt": totalCovConfInt,
        "covOnCircMean": covOnCircMean,
        "covOnCircConfInt": covOnCircConfInt,
        "hopsMean": hopsMean,
        "hopsConfInt": hopsConfInt,
        "messageSentMean": messageSentMean,
        "messageSentConfInt": messageSentConfInt,
        "slotsWaitedMean": slotsWaitedMean,
        "slotsWaitedConfInt": slotsWaitedConfInt
    }
