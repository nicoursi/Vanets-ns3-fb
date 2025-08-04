#!/usr/bin/python

import csv
import os

import numpy as np
import scipy.stats as st


def count_lines_in_csv(csv_file):
    """Count the number of lines in a CSV file."""
    return sum(1 for row in csv_file)


def calculate_mean_and_conf_int(data_list, static=False, cast_to_int=False):
    """Calculate mean and confidence interval for a list of data.

    Args:
        data_list: List of numerical data
        static: If True, multiply mean by 1.1
        cast_to_int: If True, cast mean to integer

    Returns:
        tuple: (mean, confidence_interval_amplitude)

    """
    if len(data_list) == 0:
        return 0, 0  # Return zero mean and zero error for empty data

    np_array = np.array(data_list)
    mean = np.mean(np_array)

    if static:
        mean *= 1.1

    if len(np_array) <= 1:
        conf_int_amplitude = 0  # Can't compute CI reliably with 1 or fewer points
    else:
        sem = st.sem(np_array)
        if np.isnan(sem) or sem == 0:
            conf_int_amplitude = 0  # No variation, no confidence interval
        else:
            conf_int = st.t.interval(0.95, len(np_array) - 1, loc=mean, scale=sem)
            conf_int_amplitude = conf_int[1] - conf_int[0]

    if cast_to_int:
        mean = round(mean)
    else:
        mean = round(mean, 2)

    return mean, conf_int_amplitude


"""oldcode
def calculate_mean_and_conf_int(data_list, static=False, cast_to_int=False):
    if len(data_list) == 0:
        return 0, 0  # Return zero mean and zero error for empty data
    np_array = np.array(data_list)
    # print(np_array)
    # mean = round(np.mean(np_array), 2)

    # Calculate mean without early rounding
    mean = np.mean(np_array)

    if static is True:
        mean *= 1.1
        mean = round(mean, 2)
    # if cast_to_int is True:
    #     mean = int(round(mean))

    sem = st.sem(np_array)

    if np.isnan(sem) or sem == 0:
        # Standard error is zero or NaN -> no variability
        conf_int_amplitude = 0.0
    else:
        conf_int = st.t.interval(0.95, len(np_array)-1,
                               loc=np.mean(np_array), scale=sem)
        conf_int_amplitude = conf_int[1] - conf_int[0]

    # Apply rounding at the end
    if cast_to_int:
        mean = int(round(mean))
    else:
        mean = round(mean, 2)

    return mean, conf_int_amplitude  # / 4
"""


# def read_csv_from_directory(path, roff=False, static=False):
#     total_nodes = []
#     nodes_on_circ = []
#     total_coverage = []
#     cov_on_circ = []
#     hops = []
#     slots = []
#     message_sent = []
#     total_coverage_percent = []
#     cov_on_circ_percent = []
#     for file_name in os.listdir(path):
#         # delete_because_empty = False
#         full_path = os.path.join(path, file_name)
#         if not os.path.isfile(full_path) or not file_name.endswith(".csv"):
#             continue  # Skip directories and non-CSV files
#         with open(full_path, "r") as file:
#             csv_file = csv.reader(file, delimiter=",")
#             first_line = True
#             if count_lines_in_csv(csv_file) != 2:
#                 # delete_because_empty = True
#                 continue
#             else:
#                 file.seek(0)
#                 first_line_ref = 0
#                 for row in csv_file:
#                     if first_line:
#                         first_line = False
#                         first_line_ref = row
#                         continue
#                     total_nodes.append(int(row[5]))
#                     nodes_on_circ.append(int(row[6]))
#                     total_coverage.append(int(row[7]))
#                     cov_on_circ.append(int(row[8]))
#                     if not math.isnan(float(row[10])):
#                         hops.append(float(row[10]))
#                     if not math.isnan(float(row[11])):
#                         slots.append(float(row[11]))
#                     message_sent.append(int(row[12]))
#                     total_coverage_percent.append(
#                         ((float(total_coverage[-1]) / float(total_nodes[-1])) * 100)
#                     )
#                     cov_on_circ_percent.append(
#                         ((float(cov_on_circ[-1]) / float(nodes_on_circ[-1])) * 100)
#                     )
#                 # if delete_because_empty == True:
#                 #     os.remove(full_path)
#     print(path)
#     total_cov_mean, total_cov_conf_int = calculate_mean_and_conf_int(
#         total_coverage_percent
#     )
#     cov_on_circ_mean, cov_on_circ_conf_int = calculate_mean_and_conf_int(
#         cov_on_circ_percent
#     )
#     hops_mean, hops_conf_int = calculate_mean_and_conf_int(hops, static)
#     message_sent_mean, message_sent_conf_int = calculate_mean_and_conf_int(
#         message_sent, False, True
#     )
#     slots_waited_mean, slots_waited_conf_int = calculate_mean_and_conf_int(
#         slots, False, True
#     )
#
#     # print(slots_waited_mean)
#     # if roff is True:
#     #     slots_waited_mean = int(round(slots_waited_mean - hops_mean))
#
#     return {
#         "totCoverageMean": total_cov_mean,
#         "totCoverageConfInt": total_cov_conf_int,
#         "covOnCircMean": cov_on_circ_mean,
#         "covOnCircConfInt": cov_on_circ_conf_int,
#         "hopsMean": hops_mean,
#         "hopsConfInt": hops_conf_int,
#         "messageSentMean": message_sent_mean,
#         "messageSentConfInt": message_sent_conf_int,
#         "slotsWaitedMean": slots_waited_mean,
#         "slotsWaitedConfInt": slots_waited_conf_int
#     }


def read_csv_from_directory(path, roff=False, static=False):
    """Read CSV files from a directory and calculate statistics.

    Args:
        path: Directory path containing CSV files
        roff: Boolean flag (unused in current implementation)
        static: Boolean flag passed to calculate_mean_and_conf_int

    Returns:
        dict: Dictionary containing calculated means and confidence intervals

    """
    total_nodes = []
    nodes_on_circ = []
    total_coverage = []
    cov_on_circ = []
    hops = []
    slots = []
    message_sent = []
    total_coverage_percent = []
    cov_on_circ_percent = []

    for file_name in os.listdir(path):
        full_path = os.path.join(path, file_name)
        if (
            not os.path.isfile(full_path)
            or not file_name.endswith(".csv")
            or file_name.startswith("Combined-")
        ):
            continue

        with open(full_path) as file:
            rows = list(csv.reader(file, delimiter=","))
            if len(rows) <= 1:
                print(f"Skipping empty or malformed file: {file_name}")
                continue

            for i, row in enumerate(rows[1:]):
                try:
                    # Skip if any value is invalid (None, empty, or 'nan' entries)
                    invalid_values = ("", "-nan", "nan", None)
                    if any(value in invalid_values or value == "nan" for value in row):
                        print(f"Skipping incomplete row in {file_name} line {i + 2}: {row}")
                        continue  # Skip this row if it has any invalid value

                    total_nodes.append(int(row[5]))
                    nodes_on_circ.append(int(row[6]))
                    total_coverage.append(int(row[7]))
                    cov_on_circ.append(int(row[8]))

                    hops.append(float(row[10]))
                    slots.append(float(row[11]))
                    message_sent.append(int(row[12]))

                    total_coverage_percent.append(
                        (float(total_coverage[-1]) / float(total_nodes[-1])) * 100,
                    )
                    cov_on_circ_percent.append(
                        (float(cov_on_circ[-1]) / float(nodes_on_circ[-1])) * 100,
                    )

                except Exception as e:
                    print(f"Skipping bad row in {file_name} line {i + 2}: {row}")
                    print(f" -> {e}")
                    continue

    print(f"Finished reading: {path}")

    total_cov_mean, total_cov_conf_int = calculate_mean_and_conf_int(total_coverage_percent)
    cov_on_circ_mean, cov_on_circ_conf_int = calculate_mean_and_conf_int(cov_on_circ_percent)
    hops_mean, hops_conf_int = calculate_mean_and_conf_int(hops, static)
    message_sent_mean, message_sent_conf_int = calculate_mean_and_conf_int(
        message_sent,
        False,
        True,
    )
    slots_waited_mean, slots_waited_conf_int = calculate_mean_and_conf_int(slots, False, True)

    return {
        "totCoverageMean": total_cov_mean,
        "totCoverageConfInt": total_cov_conf_int,
        "covOnCircMean": cov_on_circ_mean,
        "covOnCircConfInt": cov_on_circ_conf_int,
        "hopsMean": hops_mean,
        "hopsConfInt": hops_conf_int,
        "messageSentMean": message_sent_mean,
        "messageSentConfInt": message_sent_conf_int,
        "slotsWaitedMean": slots_waited_mean,
        "slotsWaitedConfInt": slots_waited_conf_int,
    }


def find_project_root(start_path=None):
    """Find the project root by walking up from a starting path.

    Walk up from `start_path` (or the current working directory) until a directory
    containing both 'ns-3' and 'simulations' subdirectories is found.

    Returns the absolute path if found, otherwise raises RuntimeError.
    """
    current_dir = os.getcwd() if start_path is None else os.path.abspath(start_path)

    while True:
        ns3_path = os.path.join(current_dir, "ns-3")
        sim_path = os.path.join(current_dir, "simulations")

        if os.path.isdir(ns3_path) and os.path.isdir(sim_path):
            return current_dir

        parent = os.path.dirname(current_dir)
        if parent == current_dir:  # reached filesystem root
            break
        current_dir = parent

    msg = f"Could not find project root (looking for ns-3/ and simulations/)\nSearched from: {os.getcwd()}"
    raise RuntimeError(
        msg,
    )
