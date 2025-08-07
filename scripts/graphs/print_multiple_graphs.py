#!/usr/bin/python

import os

import matplotlib
import numpy as np

matplotlib.use("TKAGG")
import math
import warnings

import graph_utils
import matplotlib.pyplot as plt

# Uncomment to treat warnings as errors
warnings.filterwarnings("error", category=RuntimeWarning)


def lists_to_list(list_of_lists, protocols):
    """Convert list of lists to a single list based on protocols."""
    to_return = []
    for protocol in protocols:
        to_return.append(list_of_lists[protocol][0])
    return to_return


def print_single_graph_line_comparison():
    """Print a single graph for line comparison."""
    fig, ax = plt.subplots()
    rects = []
    count = 0
    colors = ["0.3", "0.5"]
    rects.append(ax.bar([10, 20]))
    plt.show()


def print_single_graph_distance(
    out_folder,
    graph_title,
    compound_data,
    distances,
    protocol,
    cw,
    tx_range,
    junctions,
    metric,
    x_label,
    y_label,
    z_label,
    min_z,
    max_z,
    tx_ranges,
    color,
):
    """Print a 3D surface plot showing distance vs transmission range."""
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")

    n = len(distances)
    ind = np.arange(n)

    bar_width = float((float(1) / float(4)) * 0.6)
    # fig, ax = plt.subplots()

    rects = []
    count = 0
    X1 = list(map(int, tx_ranges))
    Y1 = list(map(int, distances))
    X, Y = np.meshgrid(X1, Y1)
    Z = []

    junction = "0"
    metric_mean = metric + "Mean"
    metric_conf_int = metric + "ConfInt"
    for distance in distances:
        result_list = []
        for tx_range in tx_ranges:
            result_list.append(compound_data[distance][junction][tx_range][protocol][metric_mean])
        Z.append(result_list)

    Z = np.array(Z)
    ax.set_xticks(X1)
    ax.set_yticks(Y1)
    ax.set_xticklabels(X1, fontsize=22)
    ax.set_yticklabels(Y1, fontsize=22)
    # fig.zticks(fontsize=23)
    ax.zaxis.set_tick_params(labelsize=22)

    ax.set_xlabel("\n" + x_label, fontsize=25, linespacing=3.2)
    ax.set_ylabel("\n" + y_label, fontsize=25, linespacing=3.2)
    ax.set_zlabel("\n" + z_label, fontsize=25, linespacing=3.2)
    ax.set_title(graph_title, fontsize=20)

    if "cov" in metric or "Cov" in metric:
        max_z = max_z * 1.05
    else:
        max_z = max_z * 1.1
    ax.set_zlim(min_z, max_z)

    surf = ax.plot_surface(X, Y, Z, color=color, alpha=0.7)

    plt.show()

    # colors = ["0.3", "0.5", "0.7"]
    # colors = ["0.1", "0.3", "0.5", "0.7","0.9"]

    # width_distance = [-1, 1]
    # width_distance = [-1.5, -0.5, 0.5, 1.5]
    # width_distance = [-1, 0, 1]

    # protocols_list = ["Fast-Broadcast", "SJ Fast-Broadcast", "ROFF",
    #                   "SJ ROFF"]
    '''
    protocols_list = ["Fast-Broadcast", "ROFF"]
    protocols_list_map = {
        "Fast-Broadcast": "Fast-Broadcast",
        "SJ Fast-Broadcast": "Fast-Broadcast",
        "ROFF": "ROFF",
        "SJ ROFF": "ROFF"
    }

    for prot in protocols_list:
        protocol = protocols_list_map[prot]
        metric_mean_list = []
        metric_conf_int_list = []
        for distance in distances:
            junction = None
            if ("SJ" in prot):
                junction = "1"
            else:
                junction = "0"
            metric_mean = metric + "Mean"
            metric_conf_int = metric + "ConfInt"
            metric_mean_list.append(
                compound_data[distance][junction][tx_range][protocol][
                    metric_mean] + count
            )
            metric_conf_int_list.append(
                compound_data[distance][junction][tx_range][protocol][
                    metric_conf_int]
            )
        plt.plot(
            ind + width_distance[count] * bar_width,
            metric_mean_list,
            bar_width,
            color=colors[count],
            label=prot
        )
        count = count + 1

    ax.set_xlabel(x_label, fontsize=15)
    ax.set_ylabel(y_label, fontsize=15)
    if ("cov" in metric or "Cov" in metric):
        max_y = max_y * 1.05
    else:
        max_y = max_y * 1.1
    ax.set_ylim(min_y, max_y)
    # ax.set_title(graph_title, fontsize=20)
    ax.set_xticks(ind)
    ax.set_xticklabels(distances)
    # ax.set_xticklabels(["15m", "25m", "35m", "45m"])

    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=15)
    # ax.legend(loc="upper right")

    def autolabel(rects, xpos='center'):
        """
        Attach a text label above each bar in *rects*, displaying its height.

        *xpos* indicates which side to place the text w.r.t. the center of
        the bar. It can be one of the following {'center', 'right', 'left'}.
        """

        xpos = xpos.lower()  # normalize the case of the parameter
        ha = {'center': 'center', 'right': 'left', 'left': 'right'}
        offset = {'center': 0.5, 'right': 0.57, 'left': 0.43}
        # x_txt = x + w*off

        for rect in rects:
            height = rect.get_height()
            ax.text(
                rect.get_x() + rect.get_width() * offset[xpos],
                1.01 * height,
                '{}'.format(height),
                ha=ha[xpos],
                va='bottom'
            )

    for rect in rects:
        autolabel(rect)
    # plt.savefig('a1.png')
    # plt.savefig('a2.png', bbox_inches='tight')

    out_path_directory = os.path.join("out", out_folder + "-" + cw)
    out_path = os.path.join(out_path_directory, metric)  # todo fix
    if (not os.path.exists(out_path_directory)):
        os.makedirs(out_path_directory)

    plt.savefig(out_path + ".pdf")
    plt.close()  # This releases the memory
    # plt.savefig('b2.pdf', bbox_inches='tight')
    # plt.show()
    '''


def print_single_graph_error_rate(
    out_folder,
    graph_title,
    compound_data,
    error_rates,
    protocols,
    cw,
    tx_range,
    junctions,
    metric,
    x_label,
    y_label,
    min_y,
    max_y,
    colors=None,
):
    """Print a single graph showing error rate comparison."""
    if colors is None:
        colors = ["0.3", "0.5"]
    n = len(error_rates)
    ind = np.arange(n)

    bar_width = float((float(1) / float(4)) * 0.7)
    fig, ax = plt.subplots()

    rects = []
    count = 0

    width_distance = [-1, 1]
    # width_distance = [-1.5, -0.5, 0.5, 1.5]
    # width_distance = [-1, 0, 1]

    # protocols_list = ["Fast-Broadcast", "SJ Fast-Broadcast", "ROFF",
    #                   "SJ ROFF"]
    protocols_list = ["Fast-Broadcast", "ROFF"]
    protocols_list_map = {
        "Fast-Broadcast": "Fast-Broadcast",
        "SJ Fast-Broadcast": "Fast-Broadcast",
        "ROFF": "ROFF",
        "SJ ROFF": "ROFF",
    }

    for prot in protocols_list:
        protocol = protocols_list_map[prot]
        metric_mean_list = []
        metric_conf_int_list = []
        for error_rate in error_rates:
            junction = None
            junction = "1" if "SJ" in prot else "0"
            metric_mean = metric + "Mean"
            metric_conf_int = metric + "ConfInt"
            metric_mean_list.append(
                compound_data[error_rate][junction][tx_range][protocol][metric_mean],
            )
            metric_conf_int_list.append(
                compound_data[error_rate][junction][tx_range][protocol][metric_conf_int],
            )
        rects.append(
            ax.bar(
                ind + width_distance[count] * bar_width,
                metric_mean_list,
                bar_width,
                color=colors[count],
                label=prot,
                yerr=metric_conf_int_list,
                capsize=4,
            ),
        )
        count = count + 1

    ax.set_xlabel(x_label, fontsize=35)
    ax.set_ylabel(y_label, fontsize=28)
    max_y = max_y * 1.05 if "cov" in metric or "Cov" in metric else max_y * 1.1
    ax.set_ylim(min_y, max_y)
    ax.set_title(graph_title, fontsize=20)
    ax.set_xticks(ind)
    ax.set_xticklabels(error_rates, fontsize=28)
    plt.yticks(fontsize=23)
    # ax.set_xticklabels(["15m", "25m", "35m", "45m"])

    ax.legend(loc="center left", bbox_to_anchor=(1, 0.5), fontsize=15)
    # ax.legend(loc="upper right")

    def autolabel(rects, xpos="center") -> None:
        """Attach a text label above each bar in *rects*, displaying its height.

        *xpos* indicates which side to place the text w.r.t. the center of
        the bar. It can be one of the following {'center', 'right', 'left'}.
        """
        xpos = xpos.lower()  # normalize the case of the parameter
        ha = {"center": "center", "right": "left", "left": "right"}
        offset = {"center": 0.5, "right": 0.57, "left": 0.43}
        # x_txt = x + w*off

        for rect in rects:
            height = rect.get_height()
            if hasattr(height, "is_integer") and height.is_integer():
                height = int(height)
            ax.text(
                rect.get_x() + rect.get_width() * offset[xpos],
                height,
                f"{height}",
                ha=ha[xpos],
                va="bottom",
                fontsize=28,
            )

    for rect in rects:
        autolabel(rect)
    # plt.savefig('a1.png')
    # plt.savefig('a2.png', bbox_inches='tight')

    out_path_directory = os.path.join("out", out_folder + "-" + cw)
    out_path = os.path.join(out_path_directory, metric)  # TODO: fix
    if not os.path.exists(out_path_directory):
        os.makedirs(out_path_directory)

    plt.savefig(out_path + ".pdf", bbox_inches="tight")
    plt.close()  # This releases the memory
    # plt.savefig('b2.pdf', bbox_inches='tight')
    # plt.show()


def print_single_graph(
    out_folder,
    graph_title,
    compound_data,
    tx_ranges,
    protocols,
    cw,
    junction,
    metric,
    y_label,
    min_y,
    max_y,
    show_legend="true",
    file_type="png",
    root_out_folder="out",
    colors=None,
):
    """Print a single bar chart comparing protocols across transmission ranges."""
    if colors is None:
        colors = ["0.3", "0.5", "0.7"]
    n_protocols = len(protocols)
    n_ranges = len(tx_ranges)

    autolabel_fontsize = 10 if n_ranges > 3 else 12
    bar_width_percent = 0.85 if n_ranges > 3 else 0.70
    # bar_width = 0.25
    # This means: n_ranges bars per group, in total they take bar_width_percent
    # of total space
    bar_width = float((float(1) / float(n_ranges)) * float(bar_width_percent))

    group_centers = np.arange(n_protocols)  # evenly spaced protocol groups
    offsets = np.linspace(-bar_width * (n_ranges - 1) / 2, bar_width * (n_ranges - 1) / 2, n_ranges)

    rects = []
    fig, ax = plt.subplots()
    ax.set_axisbelow(True)

    for i, tx_range in enumerate(tx_ranges):
        bar_positions = group_centers + offsets[i]
        metric_mean_list = []
        metric_conf_int_list = []

        for protocol in protocols:
            metric_mean = metric + "Mean"
            metric_conf_int = metric + "ConfInt"
            metric_mean_list.append(compound_data[tx_range][protocol][metric_mean])
            conf_int = compound_data[tx_range][protocol][metric_conf_int]
            if math.isnan(conf_int):
                conf_int = 0.35
            metric_conf_int_list.append(conf_int)

        # bars = ax.bar(bar_positions, metric_mean_list, bar_width,
        #               color=colors[i], label=tx_range + "m",
        #               yerr=metric_conf_int_list, capsize=4)
        hatch = "oo" if i == n_ranges - 1 else None
        bars = ax.bar(
            bar_positions,
            metric_mean_list,
            bar_width,
            color=colors[i],
            label=tx_range + "m",
            yerr=metric_conf_int_list,
            capsize=4,
            hatch=hatch,
        )

        rects.append(bars)

    ax.set_xlim(-0.5, n_protocols - 0.5)
    ax.yaxis.grid(alpha=0.25, color="black")
    ax.set_xlabel("Protocols", fontsize=12)
    ax.set_ylabel(y_label, fontsize=15)

    if "cov" in metric or "Cov" in metric:
        max_y *= 1.07
    else:
        max_y *= 1.1

    ax.set_ylim(min_y - 0.1, max_y)
    ax.set_title(graph_title, fontsize=18)
    ax.set_xticks(group_centers)

    my_protocols = protocols
    if junction == "1":
        my_protocols = ["SJ-" + p for p in protocols]

    ax.set_xticklabels(my_protocols, fontsize=15)
    plt.yticks(fontsize=12)
    if show_legend:
        ax.legend(loc="center left", bbox_to_anchor=(1, 0.5), fontsize=12)

    def autolabel(rects_group, xpos="center"):
        """Add value labels on top of bars."""
        ha = {"center": "center", "right": "left", "left": "right"}
        offset = {"center": 0.5, "right": 0.57, "left": 0.43}
        for rect in rects_group:
            height = rect.get_height()
            if hasattr(height, "is_integer") and height.is_integer():
                height = int(height)
            ax.text(
                rect.get_x() + rect.get_width() * offset[xpos],
                height,
                f"{height}",
                ha=ha[xpos],
                va="bottom",
                fontsize=autolabel_fontsize,
            )

    for group in rects:
        autolabel(group)

    scenario_name = out_folder.split(os.sep)[0]
    metric = scenario_name + "_" + metric
    out_path_directory = os.path.join(root_out_folder, out_folder + "-" + cw)
    # out_path_directory = os.path.join("out-gottardo", out_folder + "-" + cw)
    out_path = os.path.join(out_path_directory, metric)
    if not os.path.exists(out_path_directory):
        os.makedirs(out_path_directory)

    plt.tight_layout(pad=4.0)
    print(f"Saving file in {out_path}.{file_type}")
    plt.savefig(f"{out_path}.{file_type}", dpi=150, bbox_inches="tight")

    plt.close()  # This releases the memory


# def print_single_graph(out_folder, graph_title, compound_data, tx_ranges,
#                        protocols, cw, junction, metric, y_label, min_y,
#                        max_y, colors=["0.3", "0.5", "0.7"]):
#     n = len(protocols)
#     ind = np.arange(n)
#     # ind = np.linspace(0, n - 1, n)  # evenly spaced values
#     # ind = [0.1, 0.1, 0.1, 0.1]
#     ind = np.array(ind)
#     # print(ind)
#
#     # bar_width = float((float(1)/float(4)) * float(0.90))
#     bar_width = 0.2
#     fig, ax = plt.subplots()
#     # fig, ax = plt.subplots(figsize=(10, 4))  # Increased figure size
#     rects = []
#     count = 0
#     # colors = ["0.3", "0.7"]
#
#     # width_distance = [-1, 1]
#     # width_distance = [-1.5, -0.5, 0.5, 1.5]
#     width_distance = [-1.5, -0.5, 0.5, 1.5]
#     # width_distance = [-1.025, 0, 1.025]
#     ax.set_axisbelow(True)
#
#     for tx_range in tx_ranges:
#         metric_mean_list = []
#         metric_conf_int_list = []
#         for protocol in protocols:
#             metric_mean = metric + "Mean"
#             metric_conf_int = metric + "ConfInt"
#             metric_mean_list.append(
#                 compound_data[tx_range][protocol][metric_mean]
#             )
#             conf_int = compound_data[tx_range][protocol][metric_conf_int]
#             if (math.isnan(conf_int)):
#                 conf_int = 0.35
#             metric_conf_int_list.append(conf_int)
#         # print(ind + width_distance[count] * bar_width)
#         rects.append((ax.bar(
#             ind + width_distance[count] * bar_width,
#             metric_mean_list,
#             bar_width,
#             color=colors[count],
#             label=tx_range + "m",
#             yerr=metric_conf_int_list,
#             capsize=4
#         )))
#         count = count + 1
#
#     # ax.set_xlim(-0.35, 1.35)
#     # Adjust x-axis limit based on the number of protocols
#     ax.set_xlim(-0.5, len(protocols) - 0.5)  # Dynamic x-axis limits
#     ax.yaxis.grid(alpha=0.25, color="black")
#
#     ax.set_xlabel("Protocols", fontsize=18)
#     ax.set_ylabel(y_label, fontsize=18)
#     if ("cov" in metric or "Cov" in metric):
#         max_y = max_y * 1.07
#     else:
#         max_y = max_y * 1.1
#     ax.set_ylim(min_y - 0.1, max_y)
#     ax.set_title(graph_title, fontsize=20)
#     ax.set_xticks(ind)
#     plt.xticks(fontsize=18)
#     plt.yticks(fontsize=18)
#     my_protocols = protocols
#     if junction == "1":
#         my_protocols = list(map(lambda x: "SJ-" + x, protocols))
#     ax.set_xticklabels(my_protocols)
#     # ax.set_xticklabels(["15m", "25m", "35m", "45m"])
#
#     ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=18)
#     # ax.legend(loc="upper right")
#
#     def autolabel(rects, xpos='center'):
#         """
#         Attach a text label above each bar in *rects*, displaying its height.
#
#         *xpos* indicates which side to place the text w.r.t. the center of
#         the bar. It can be one of the following {'center', 'right', 'left'}.
#         """
#
#         xpos = xpos.lower()  # normalize the case of the parameter
#         ha = {'center': 'center', 'right': 'left', 'left': 'right'}
#         offset = {'center': 0.5, 'right': 0.57, 'left': 0.43}
#         # x_txt = x + w*off
#
#         for rect in rects:
#             height = rect.get_height()
#             if (hasattr(height, "is_integer") and height.is_integer()):
#                 height = int(height)
#             ax.text(
#                 rect.get_x() + rect.get_width() * offset[xpos],
#                 height,
#                 '{}'.format(height),
#                 ha=ha[xpos],
#                 va='bottom',
#                 fontsize=14
#             )
#
#     for rect in rects:
#         autolabel(rect)
#     # plt.savefig('a1.png')
#     # plt.savefig('a2.png', bbox_inches='tight')
#
#     out_path_directory = os.path.join("out", out_folder + "-" + cw)
#     out_path = os.path.join(out_path_directory, metric)  # TODO fix
#     if (not os.path.exists(out_path_directory)):
#         os.makedirs(out_path_directory)
#
#     plt.tight_layout(pad=4.0)
#
#     # plt.tight_layout()  # Added for better spacing
#     plt.savefig(out_path + ".pdf")
#     plt.close()  # This releases the memory
#     # plt.savefig('b2.pdf', bbox_inches='tight')
#     # plt.show()


def init_compound_data(tx_ranges, protocols, metrics):
    """Initialize compound data structure for storing metrics."""
    compound_data = {}
    for tx_range in tx_ranges:
        compound_data[tx_range] = {}
        for protocol in protocols:
            for metric in metrics:
                metric_mean = metric + "Mean"
                metric_conf_int = metric + "ConfInt"
                compound_data[tx_range][protocol] = {}
                compound_data[tx_range][protocol][metric_mean] = 0
                compound_data[tx_range][protocol][metric_conf_int] = 0
    return compound_data


def append_compound_data(
    base_path,
    tx_ranges,
    protocols,
    cw,
    junction,
    error_rate,
    compound_data,
    metrics,
    alternative_base_path="",
):
    """Append data to compound data structure from CSV files."""
    for tx_range in tx_ranges:
        for protocol in protocols:
            path = None
            roff = False
            static = False
            real_base_path = base_path
            protocol_path = protocol
            if "TD" in protocol:
                real_base_path = alternative_base_path
                protocol_path = protocol.replace("TD-", "")
            # if ("STATIC" in protocol and tx_range not in protocol):
            #     static = True
            if protocol != "ROFF":
                path = os.path.join(
                    real_base_path,
                    error_rate,
                    "r" + tx_range,
                    "j" + junction,
                    cw,
                    protocol_path,
                )
            else:
                roff = True
                path = os.path.join(
                    real_base_path,
                    error_rate,
                    "r" + tx_range,
                    "j" + junction,
                    protocol_path,
                )
            data = graph_utils.read_csv_from_directory(path, roff, static)
            entry = compound_data[tx_range][protocol]
            for metric in metrics:
                metric_mean = metric + "Mean"
                metric_conf_int = metric + "ConfInt"
                compound_data[tx_range][protocol][metric_mean] = data[metric_mean]
                compound_data[tx_range][protocol][metric_conf_int] = data[metric_conf_int]


def print_line_comparison():
    """Print line comparison graphs."""
    protocols = ["fast-broadcast", "roff"]
    compound_data = init_compound_data(protocols)
    base_path = "../../simulations/line"
    append_compound_data(base_path, protocols, compound_data)
    print_single_graph_line_comparison()


def print_grid_comparison():
    """Print grid comparison graphs."""
    print("PrintGridComparison")
    protocols = ["fast-broadcast", "roff"]
    compound_data_b0 = init_compound_data(protocols)
    compound_data_b1 = init_compound_data(protocols)
    base_path_b0 = "../../simulations/Grid/b0"
    base_path_b1 = "../../simulations/Grid/b1"
    append_compound_data(base_path_b0, protocols, compound_data_b0)
    append_compound_data(base_path_b1, protocols, compound_data_b1)

    # print_single_graph_line_comparison()


# Given a scenario path and buildings/no-buildings, prints graphs for all
# txRanges and protocols
# Grid-300: contentionWindows = [{"cwMin": 16, "cwMax": 128}], buildings = ["0"],
# junctions = ["0"], txRanges = ["100", "300", "500"]


def print_protocol_comparison(
    initial_base_path,
    scenarios,
    buildings,
    error_rate,
    tx_ranges,
    protocols,
    cws,
    junctions,
    metrics,
    show_legend,
    file_type,
    root_out_folder,
):
    """Print protocol comparison graphs for different scenarios."""
    print("print_protocol_comparison")
    plt.rcParams["figure.figsize"] = [14, 6]

    metric_y_labels = {}
    metric_y_labels["totCoverage"] = "Total Delivery Ratio (%)"
    metric_y_labels["covOnCirc"] = "Total Delivery Ratio On Circ. (%)"
    metric_y_labels["hops"] = "Number Of Hops"
    metric_y_labels["slotsWaited"] = "Number Of Slots"
    metric_y_labels["messageSent"] = "Forwarding Node Number"

    graph_titles = {}
    graph_titles["totCoverage"] = "Total Delivery Ratio"
    graph_titles["covOnCirc"] = "Total Delivery Ratio On Circumference"
    graph_titles["hops"] = "Number Of Hops"
    graph_titles["slotsWaited"] = "Number Of Slots"
    graph_titles["messageSent"] = "Forwarding Node Number"

    additional_title = {}
    additional_title["0"] = {}  # no buildings
    additional_title["0"]["0"] = " (without buildings)"
    additional_title["0"]["1"] = " (without buildings, with junctions)"

    additional_title["1"] = {}  # with buildings
    additional_title["1"]["0"] = " (with buildings)"
    additional_title["1"]["1"] = " (with buildings, with junctions)"

    max_metric_values = {}
    for metric in metrics:
        max_metric_values[metric] = -1

    colors = {}
    colors["0"] = {}
    colors["0"]["0"] = ["#B5B7FF", "#5155D5", "#00034D", "#DCE0FF"]  # comparison for palazzi
    colors["0"]["1"] = ["#EDD1ED", "#B46CB4", "#662066", "#1E001F"]

    colors["1"] = {}  # 1=buildings
    colors["1"]["0"] = [
        "#FFA6A6",
        "#BD2525",
        "#510000",
        "#FFD8A8",
    ]  # comparison with gottardo for palazzi
    colors["1"]["1"] = ["#FFE0BF", "#E49453", "#A5521A", "#3B1A00"]

    for scenario in scenarios:
        if "Platoon" in scenario:
            current_buildings = ["0"]
        else:
            current_buildings = buildings

        for building in current_buildings:
            for cw in cws:
                for junction in junctions:
                    base_path = os.path.join(initial_base_path, scenario, "b" + building)
                    compound_data = init_compound_data(tx_ranges, protocols, metrics)
                    append_compound_data(
                        base_path,
                        tx_ranges,
                        protocols,
                        cw,
                        junction,
                        error_rate,
                        compound_data,
                        metrics,
                    )
                    graph_out_folder = os.path.join(scenario, "b" + building, "j" + junction)
                    for metric in metrics:
                        y_label = metric_y_labels[metric]
                        if metric in {"totCoverage", "covOnCirc"}:
                            max_metric_values[metric] = 100
                        else:
                            for tx_range in tx_ranges:
                                for protocol in protocols:
                                    metric_mean = metric + "Mean"
                                    value = compound_data[tx_range][protocol][metric_mean]
                                    max_metric_values[metric] = max(
                                        max_metric_values[metric],
                                        value,
                                    )

    for scenario in scenarios:
        if "Platoon" in scenario:
            current_buildings = ["0"]
        else:
            current_buildings = buildings

        for building in current_buildings:
            for cw in cws:
                for junction in junctions:
                    base_path = os.path.join(initial_base_path, scenario, "b" + building)
                    compound_data = init_compound_data(tx_ranges, protocols, metrics)
                    append_compound_data(
                        base_path,
                        tx_ranges,
                        protocols,
                        cw,
                        junction,
                        error_rate,
                        compound_data,
                        metrics,
                    )
                    graph_out_folder = os.path.join(scenario, "b" + building, "j" + junction)
                    for metric in metrics:
                        y_label = metric_y_labels[metric]
                        additional_title_str = additional_title[building][junction]

                        print_single_graph(
                            graph_out_folder,
                            graph_titles[metric] + additional_title_str,
                            compound_data,
                            tx_ranges,
                            protocols,
                            cw,
                            junction,
                            metric,
                            y_label,
                            0,
                            max_metric_values[metric],
                            show_legend,
                            file_type,
                            root_out_folder,
                            colors[building][junction],
                        )


def print_drone_comparison():
    """Print drone comparison graphs for different scenarios."""
    print("print_drone_comparison")
    plt.rcParams["figure.figsize"] = [18, 14]
    initial_base_path = "../../simulations/scenario-droni"
    # scenarios = ["Grid-200", "Grid-300", "Grid-400", "LA-15", "LA-25", "LA-35",
    #              "LA-45", "Padova-15", "Padova-25", "Padova-35", "Padova-45"]
    scenarios = ["LA-25"]
    high_buildings = ["0", "1"]
    buildings = ["0", "1"]
    error_rate = "e0"
    # tx_ranges = ["100", "300", "500"]
    tx_ranges = ["100", "300", "500"]
    # protocols = ["Fast-Broadcast", "STATIC-100", "STATIC-300", "STATIC-500",
    #              "ROFF"]
    protocols = ["Fast-Broadcast", "ROFF"]
    # cws = ["cw[32-1024]"]
    cws = ["cw[32-1024]"]
    # junctions = ["0", "1"]
    junctions = ["0"]
    metrics = ["totCoverage", "covOnCirc", "hops", "slotsWaited", "messageSent"]

    metric_y_labels = {}
    metric_y_labels["totCoverage"] = "Total Delivery Ratio (%)"
    metric_y_labels["covOnCirc"] = "Total Delivery Ratio On Circ. (%)"
    metric_y_labels["hops"] = "Number Of Hops"
    metric_y_labels["slotsWaited"] = "Number Of Slots"
    metric_y_labels["messageSent"] = "Forwarding Node Number"

    graph_titles = {}
    graph_titles["totCoverage"] = "Total Delivery Ratio"
    graph_titles["covOnCirc"] = "Total Delivery Ratio On Circumference"
    graph_titles["hops"] = "Number Of Hops"
    graph_titles["slotsWaited"] = "Number Of Slots"
    graph_titles["messageSent"] = "Forwarding Node Number"

    additional_title = {}
    additional_title["0"] = {}  # no buildings
    additional_title["0"]["0"] = " (without buildings)"  # no buildings, no high_buildings

    additional_title["1"] = {}  # with buildings
    additional_title["1"]["0"] = " (with buildings, real heights)"
    additional_title["1"]["1"] = " (with buildings, 100m heights)"

    colors = {}
    colors["0"] = {}
    colors["0"]["0"] = ["#B5B7FF", "#5155D5", "#00034D"]  # buildings=0, high_buildings=0 blu

    colors["1"] = {}  # 1=buildings
    colors["1"]["0"] = ["#FFA6A6", "#BD2525", "#510000"]  # buildings=1, high_buildings=0 rosso
    colors["1"]["1"] = ["#D1AFD1", "#864A89", "#3C003F"]  # buildings=1, high_buildings=1 viola

    max_metric_values = {}
    for metric in metrics:
        max_metric_values[metric] = -1

    for scenario in scenarios:
        my_buildings = buildings
        my_initial_base_path = initial_base_path
        if "Platoon" in scenario:
            my_buildings = ["0"]
        for high_building in high_buildings:
            if high_building == "1":
                my_initial_base_path += "-high"
                my_buildings = ["1"]
            for building in my_buildings:
                for cw in cws:
                    for junction in junctions:
                        base_path = os.path.join(my_initial_base_path, scenario, "b" + building)
                        compound_data = init_compound_data(tx_ranges, protocols, metrics)
                        append_compound_data(
                            base_path,
                            tx_ranges,
                            protocols,
                            cw,
                            junction,
                            error_rate,
                            compound_data,
                            metrics,
                        )
                        graph_out_folder = os.path.join(scenario, "b" + building, "j" + junction)
                        for metric in metrics:
                            y_label = metric_y_labels[metric]
                            if metric in {"totCoverage", "covOnCirc"}:
                                max_metric_values[metric] = 100
                            else:
                                for tx_range in tx_ranges:
                                    for protocol in protocols:
                                        metric_mean = metric + "Mean"
                                        value = compound_data[tx_range][protocol][metric_mean]
                                        max_metric_values[metric] = max(
                                            max_metric_values[metric], value
                                        )

    for scenario in scenarios:
        my_buildings = buildings
        my_initial_base_path = initial_base_path
        for high_building in high_buildings:
            if high_building == "1":
                my_initial_base_path += "-high"
                my_buildings = ["1"]
            for building in my_buildings:
                for cw in cws:
                    for junction in junctions:
                        base_path = os.path.join(my_initial_base_path, scenario, "b" + building)
                        compound_data = init_compound_data(tx_ranges, protocols, metrics)
                        append_compound_data(
                            base_path,
                            tx_ranges,
                            protocols,
                            cw,
                            junction,
                            error_rate,
                            compound_data,
                            metrics,
                        )
                        graph_out_folder = os.path.join(
                            scenario,
                            "drones",
                            "b" + building + "-h" + high_building,
                        )
                        for metric in metrics:
                            y_label = metric_y_labels[metric]
                            print("before printSingleGraph h=" + high_building + " b=" + building)
                            print_single_graph(
                                graph_out_folder,
                                graph_titles[metric] + additional_title[building][high_building],
                                compound_data,
                                tx_ranges,
                                protocols,
                                cw,
                                junction,
                                metric,
                                y_label,
                                0,
                                max_metric_values[metric],
                                colors[building][high_building],
                            )


def print_error_comparison():
    """Print error comparison graphs for different scenarios."""
    print("print_error_comparison")
    plt.rcParams["figure.figsize"] = [18, 10]
    initial_base_path = "../../simulations/scenario-urbano"
    # scenarios = ["Grid-200", "Grid-300", "Grid-400", "LA-15", "LA-25", "LA-35",
    #              "LA-45", "Padova-15", "Padova-25", "Padova-35", "Padova-45"]
    scenarios = ["Padova-25"]
    buildings = ["0", "1"]
    tx_ranges = ["100", "300", "500"]
    protocols = ["Fast-Broadcast", "ROFF"]
    # cws = ["cw[16-128]", "cw[32-1024]"]
    cws = ["cw[16-128]"]
    error_rates = ["0", "10", "20", "30", "40", "50", "100"]
    junctions = ["0", "1"]
    x_label = "Error in scheduling (%)"
    metrics = ["totCoverage", "covOnCirc", "hops", "slotsWaited", "messageSent"]

    metric_y_labels = {}
    metric_y_labels["totCoverage"] = "Total Coverage (%)"
    metric_y_labels["covOnCirc"] = "Coverage on circumference (%)"
    metric_y_labels["hops"] = "Number of hops to reach circumference"
    metric_y_labels["slotsWaited"] = "Number of slots waited to reach circumference"
    metric_y_labels["messageSent"] = "Number of alert messages sent"

    max_metric_values = {}
    for metric in metrics:
        max_metric_values[metric] = -1

    for scenario in scenarios:
        for building in buildings:
            for cw in cws:
                error_rate_compound_data = {}
                for error_rate in error_rates:
                    error_rate_compound_data[error_rate] = {}
                for junction in junctions:
                    for error_rate in error_rates:
                        base_path = os.path.join(initial_base_path, scenario, "b" + building)
                        # print("base_path= " + base_path)
                        compound_data = init_compound_data(tx_ranges, protocols, metrics)
                        append_compound_data(
                            base_path,
                            tx_ranges,
                            protocols,
                            cw,
                            junction,
                            "e" + error_rate,
                            compound_data,
                            metrics,
                        )
                        error_rate_compound_data[error_rate][junction] = compound_data
                for metric in metrics:
                    y_label = metric_y_labels[metric]
                    if metric in {"totCoverage", "covOnCirc"}:
                        max_metric_values[metric] = 100
                    else:
                        for junction in junctions:
                            for error_rate in error_rates:
                                for tx_range in tx_ranges:
                                    for protocol in protocols:
                                        metric_mean = metric + "Mean"
                                        value = error_rate_compound_data[error_rate][junction][
                                            tx_range
                                        ][protocol][metric_mean]
                                        max_metric_values[metric] = max(
                                            max_metric_values[metric],
                                            value,
                                        )

    for scenario in scenarios:
        for building in buildings:
            for cw in cws:
                error_rate_compound_data = {}
                for error_rate in error_rates:
                    error_rate_compound_data[error_rate] = {}
                for junction in junctions:
                    for error_rate in error_rates:
                        base_path = os.path.join(initial_base_path, scenario, "b" + building)
                        # print("base_path= " + base_path)
                        compound_data = init_compound_data(tx_ranges, protocols, metrics)
                        append_compound_data(
                            base_path,
                            tx_ranges,
                            protocols,
                            cw,
                            junction,
                            "e" + error_rate,
                            compound_data,
                            metrics,
                        )
                        error_rate_compound_data[error_rate][junction] = compound_data
                graph_out_folder = os.path.join(scenario, "error", "b" + building)
                for metric in metrics:
                    y_label = metric_y_labels[metric]
                    print_single_graph_error_rate(
                        graph_out_folder,
                        "graphTitle",
                        error_rate_compound_data,
                        error_rates,
                        protocols,
                        cw,
                        "100",
                        junctions,
                        metric,
                        x_label,
                        y_label,
                        0,
                        max_metric_values[metric],
                    )


def print_forged_comparison():
    """Print forged comparison graphs for different scenarios."""
    print("print_forged_comparison")
    plt.rcParams["figure.figsize"] = [18, 10]
    initial_base_path = "../../simulations/scenario-urbano"
    # scenarios = ["Grid-200", "Grid-300", "Grid-400", "LA-15", "LA-25", "LA-35",
    #              "LA-45", "Padova-15", "Padova-25", "Padova-35", "Padova-45"]
    scenarios = ["LA-25"]
    buildings = ["0"]
    # tx_ranges = ["100", "300", "500"]
    tx_ranges = ["300"]
    protocols = ["Fast-Broadcast", "ROFF"]
    cws = ["cw[32-1024]"]
    # cws = ["cw[16-128]"]
    forged_rates = ["0", "10", "20", "30", "40", "50"]
    junctions = ["0"]
    x_label = "% of vehicles affected by forging"
    metrics = ["totCoverage", "covOnCirc", "hops", "slotsWaited", "messageSent"]

    metric_y_labels = {}
    metric_y_labels["totCoverage"] = "Total Delivery Ratio (%)"
    metric_y_labels["covOnCirc"] = "Total Delivery Ratio On Circ. (%)"
    metric_y_labels["hops"] = "Number Of Hops"
    metric_y_labels["slotsWaited"] = "Number Of Slots"
    metric_y_labels["messageSent"] = "Forwarding Node Number"

    graph_titles = {}
    graph_titles["totCoverage"] = "Total Delivery Ratio"
    graph_titles["covOnCirc"] = "Total Delivery Ratio On Circumference"
    graph_titles["hops"] = "Number Of Hops"
    graph_titles["slotsWaited"] = "Number Of Slots"
    graph_titles["messageSent"] = "Forwarding Node Number"

    colors = ["#B5B7FF", "#5155D5"]

    max_metric_values = {}
    for metric in metrics:
        max_metric_values[metric] = -1

    for scenario in scenarios:
        for building in buildings:
            for cw in cws:
                forged_rate_compound_data = {}
                for forged_rate in forged_rates:
                    forged_rate_compound_data[forged_rate] = {}
                for junction in junctions:
                    for forged_rate in forged_rates:
                        base_path = os.path.join(initial_base_path, scenario, "b" + building)
                        compound_data = init_compound_data(tx_ranges, protocols, metrics)
                        append_compound_data(
                            base_path,
                            tx_ranges,
                            protocols,
                            cw,
                            junction,
                            "f" + forged_rate,
                            compound_data,
                            metrics,
                        )
                        forged_rate_compound_data[forged_rate][junction] = compound_data
                for metric in metrics:
                    y_label = metric_y_labels[metric]
                    if metric in {"totCoverage", "covOnCirc"}:
                        max_metric_values[metric] = 100
                    else:
                        for junction in junctions:
                            for forged_rate in forged_rates:
                                for tx_range in tx_ranges:
                                    for protocol in protocols:
                                        metric_mean = metric + "Mean"
                                        value = forged_rate_compound_data[forged_rate][junction][
                                            tx_range
                                        ][protocol][metric_mean]
                                        max_metric_values[metric] = max(
                                            max_metric_values[metric], value
                                        )

    for scenario in scenarios:
        for building in buildings:
            for cw in cws:
                forged_rate_compound_data = {}
                for forged_rate in forged_rates:
                    forged_rate_compound_data[forged_rate] = {}
                for junction in junctions:
                    for forged_rate in forged_rates:
                        base_path = os.path.join(initial_base_path, scenario, "b" + building)
                        # print("base_path= " + base_path)
                        compound_data = init_compound_data(tx_ranges, protocols, metrics)
                        append_compound_data(
                            base_path,
                            tx_ranges,
                            protocols,
                            cw,
                            junction,
                            "f" + forged_rate,
                            compound_data,
                            metrics,
                        )
                        forged_rate_compound_data[forged_rate][junction] = compound_data
                graph_out_folder = os.path.join(scenario, "forged", "b" + building)
                for metric in metrics:
                    y_label = metric_y_labels[metric]
                    print_single_graph_error_rate(
                        graph_out_folder,
                        graph_titles[metric],
                        forged_rate_compound_data,
                        forged_rates,
                        protocols,
                        cw,
                        "300",
                        junctions,
                        metric,
                        x_label,
                        y_label,
                        0,
                        max_metric_values[metric],
                        colors,
                    )


def print_distance_comparison():
    """Print distance comparison graphs for various scenarios."""
    print("print_distance_comparison")
    plt.rcParams["figure.figsize"] = [18, 10]
    initial_base_path = "../../simulations/scenario-urbano"
    # scenarios = ["Grid-200", "Grid-300", "Grid-400", "LA-15", "LA-25",
    #              "LA-35", "LA-45", "Padova-15", "Padova-25", "Padova-35",
    #              "Padova-45"]
    scenarios = ["Padova"]
    # distances = ["15", "25", "35", "45"]
    distances = ["5", "15", "25", "35", "45"]
    buildings = ["0"]
    tx_ranges = ["100", "300", "500"]
    protocols = ["Fast-Broadcast", "ROFF"]
    error_rate = "e0"
    # cws = ["cw[16-128]", "cw[32-1024]"]
    cws = ["cw[32-1024]"]
    junctions = ["0"]
    x_label = "Vehicle distance (m)"
    y_orig_label = "Transmission range (m)"
    metrics = ["totCoverage", "covOnCirc", "hops", "slotsWaited", "messageSent"]

    metric_y_labels = {}
    metric_y_labels["totCoverage"] = "Total Delivery Ratio (%)"
    metric_y_labels["covOnCirc"] = "Total Delivery Ratio On Circ. (%)"
    metric_y_labels["hops"] = "Number Of Hops"
    metric_y_labels["slotsWaited"] = "Number Of Slots"
    metric_y_labels["messageSent"] = "Forwarding Node Number"

    colors = {}
    colors["Fast-Broadcast"] = "#5155D5"
    colors["ROFF"] = "#BD2525"

    # chiari
    # colors["Fast-Broadcast"] = "#B5B7FF"
    # colors["ROFF"] = "#FFA6A6"

    max_metric_values = {}

    for scenario in scenarios:
        for building in buildings:
            for cw in cws:
                distance_compound_data = {}
                for distance in distances:
                    distance_compound_data[distance] = {}
                for junction in junctions:
                    for distance in distances:
                        base_path = os.path.join(
                            initial_base_path,
                            scenario + "-" + distance,
                            "b" + building,
                        )
                        compound_data = init_compound_data(tx_ranges, protocols, metrics)
                        append_compound_data(
                            base_path,
                            tx_ranges,
                            protocols,
                            cw,
                            junction,
                            error_rate,
                            compound_data,
                            metrics,
                        )
                        distance_compound_data[distance][junction] = compound_data

                for metric in metrics:
                    y_label = metric_y_labels[metric]
                    max_metric_values[metric] = -1
                    if metric in {"totCoverage", "covOnCirc"}:
                        max_metric_values[metric] = 100
                    else:
                        for junction in junctions:
                            for distance in distances:
                                for tx_range in tx_ranges:
                                    for protocol in protocols:
                                        metric_mean = metric + "Mean"
                                        value = distance_compound_data[distance][junction][
                                            tx_range
                                        ][protocol][metric_mean]
                                        max_metric_values[metric] = max(
                                            max_metric_values[metric], value
                                        )

    for scenario in scenarios:
        for building in buildings:
            for cw in cws:
                distance_compound_data = {}
                for distance in distances:
                    distance_compound_data[distance] = {}
                for junction in junctions:
                    for distance in distances:
                        base_path = os.path.join(
                            initial_base_path,
                            scenario + "-" + distance,
                            "b" + building,
                        )
                        compound_data = init_compound_data(tx_ranges, protocols, metrics)
                        append_compound_data(
                            base_path,
                            tx_ranges,
                            protocols,
                            cw,
                            junction,
                            error_rate,
                            compound_data,
                            metrics,
                        )
                        distance_compound_data[distance][junction] = compound_data

                graph_out_folder = os.path.join(
                    scenario,
                    "distance",
                    "b" + building,
                )  # TODO aggiungere cw nel out path?

                for protocol in protocols:
                    for metric in metrics:
                        y_label = metric_y_labels[metric]
                        # print(distance_compound_data)
                        graph_title = metric_y_labels[metric] + " (" + protocol + " )"
                        print_single_graph_distance(
                            graph_out_folder,
                            graph_title,
                            distance_compound_data,
                            distances,
                            protocol,
                            cw,
                            "500",
                            junctions,
                            metric,
                            y_orig_label,
                            x_label,
                            metric_y_labels[metric],
                            0,
                            max_metric_values[metric],
                            tx_ranges,
                            colors[protocol],
                        )


def print_old_fb_comparison():
    """Print old Fast-Broadcast comparison graphs."""
    print("print_old_fb_comparison")
    plt.rcParams["figure.figsize"] = [18, 6]
    initial_base_path = "../../simulations/scenario-urbano"
    alternative_initial_base_path = "../../simulations/scenario-urbano-oldFB"
    # scenarios = ["Grid-200", "Grid-300", "Grid-400", "LA-15", "LA-25",
    #              "LA-35", "LA-45", "Padova-15", "Padova-25", "Padova-35",
    #              "Padova-45"]
    scenarios = ["LA-25"]
    buildings = ["1"]
    error_rate = "e0"
    # tx_ranges = ["100", "300", "500"]
    tx_ranges = ["100", "300", "500"]
    # protocols = ["Fast-Broadcast", "STATIC-100", "STATIC-300", "STATIC-500",
    #              "ROFF"]
    protocols = [
        "Fast-Broadcast",
        "STATIC-100",
        "STATIC-300",
        "STATIC-500",
        "TD-Fast-Broadcast",
        "TD-STATIC-100",
        "TD-STATIC-300",
        "TD-STATIC-500",
    ]
    cws = ["cw[32-1024]"]
    # cws = ["cw[16-128]", "cw[32-1024]"]
    junctions = ["0"]
    tds = ["0", "1"]
    # junctions = ["0"]
    metrics = ["totCoverage", "covOnCirc", "hops", "slotsWaited", "messageSent"]

    metric_y_labels = {}
    metric_y_labels["totCoverage"] = "Total Delivery Ratio (%)"
    metric_y_labels["covOnCirc"] = "Total Delivery Ratio On Circ. (%)"
    metric_y_labels["hops"] = "Number Of Hops"
    metric_y_labels["slotsWaited"] = "Number Of Slots"
    metric_y_labels["messageSent"] = "Forwarding Node Number"

    graph_titles = {}
    graph_titles["totCoverage"] = "Total Delivery Ratio"
    graph_titles["covOnCirc"] = "Total Delivery Ratio On Circumference"
    graph_titles["hops"] = "Number Of Hops"
    graph_titles["slotsWaited"] = "Number Of Slots"
    graph_titles["messageSent"] = "Forwarding Node Number"

    additional_title = {}
    additional_title["0"] = {}  # no buildings
    additional_title["0"]["0"] = " (without buildings)"
    additional_title["0"]["1"] = " (without buildings)"

    additional_title["1"] = {}  # with buildings
    additional_title["1"]["0"] = " (with buildings)"
    additional_title["1"]["1"] = " (with buildings)"

    max_metric_values = {}
    for metric in metrics:
        max_metric_values[metric] = -1

    colors = {}
    colors["0"] = ["#B5B7FF", "#5155D5", "#00034D"]  # td0 blu
    colors["1"] = ["#FFA6A6", "#BD2525", "#510000"]  # td1 rosso

    for scenario in scenarios:
        if "Platoon" in scenario:
            buildings = ["0"]
        for building in buildings:
            for cw in cws:
                for junction in junctions:
                    base_path = os.path.join(initial_base_path, scenario, "b" + building)
                    alternative_base_path = os.path.join(
                        alternative_initial_base_path,
                        scenario,
                        "b" + building,
                    )
                    compound_data = init_compound_data(tx_ranges, protocols, metrics)
                    append_compound_data(
                        base_path,
                        tx_ranges,
                        protocols,
                        cw,
                        junction,
                        error_rate,
                        compound_data,
                        metrics,
                        alternative_base_path,
                    )
                    graph_out_folder = os.path.join(scenario, "b" + building, "j" + junction)
                    for metric in metrics:
                        y_label = metric_y_labels[metric]
                        if metric in {"totCoverage", "covOnCirc"}:
                            max_metric_values[metric] = 100
                        else:
                            for tx_range in tx_ranges:
                                for protocol in protocols:
                                    metric_mean = metric + "Mean"
                                    value = compound_data[tx_range][protocol][metric_mean]
                                    max_metric_values[metric] = max(
                                        max_metric_values[metric],
                                        value,
                                    )

    for scenario in scenarios:
        for building in buildings:
            for cw in cws:
                for junction in junctions:
                    base_path = os.path.join(initial_base_path, scenario, "b" + building)
                    alternative_base_path = os.path.join(
                        alternative_initial_base_path,
                        scenario,
                        "b" + building,
                    )
                    compound_data = init_compound_data(tx_ranges, protocols, metrics)
                    append_compound_data(
                        base_path,
                        tx_ranges,
                        protocols,
                        cw,
                        junction,
                        error_rate,
                        compound_data,
                        metrics,
                        alternative_base_path,
                    )
                    for metric in metrics:
                        for td in tds:
                            graph_out_folder = os.path.join(scenario + "-old-fb", "td-" + td)
                            my_protocols = filter(
                                lambda x: (
                                    (td == "0" and "TD" not in x) or (td == "1" and "TD" in x)
                                ),
                                protocols,
                            )
                            y_label = metric_y_labels[metric]
                            print_single_graph(
                                graph_out_folder,
                                (graph_titles[metric] + additional_title[building][junction]),
                                compound_data,
                                tx_ranges,
                                my_protocols,
                                cw,
                                junction,
                                metric,
                                y_label,
                                0,
                                max_metric_values[metric],
                                colors[td],
                            )


if __name__ == "__main__":
    main()


"""
def print_distance_comparison(cw, vehicle_distances, protocols, x_list,
                             x_labels, figure_prefix, graph_title_extension,
                             folder, decrease_conf_ints=False):
    plt.rcParams["figure.figsize"] = [18, 10]
    base_path = os.path.join("../../simulations/scenario-urbano", cw, "Padova")
    x_label = "Vehicle distance"
    compound_data = init_compound_data(protocols)
    for distance in vehicle_distances:
        base_path_with_distance = os.path.join(base_path, "d" + str(distance),
                                             "b1")
        append_compound_data(base_path_with_distance, protocols, compound_data,
                           decrease_conf_ints)
    # Print graphs
    print_single_graph(
        cw,
        folder,
        ("Padua scenario with buildings, total coverage with varying "
         "vehicle distance (" + graph_title_extension + ")"),
        x_list,
        x_labels,
        x_label,
        "Total coverage (%)",
        figure_prefix + "DistanceVsTotalCover",
        compound_data["totCoverageMeans"],
        compound_data["totCoverageConfInts"],
        protocols
    )
    print_single_graph(
        cw,
        folder,
        ("Padua scenario with buildings, coverage on circumference with "
         "varying vehicle distance (" + graph_title_extension + ")"),
        x_list,
        x_labels,
        x_label,
        "Coverage on circumference (%)",
        figure_prefix + "DistanceVsCoverOnCircumference",
        compound_data["covOnCircMeans"],
        compound_data["covOnCircConfInts"],
        protocols
    )
    print_single_graph(
        cw,
        folder,
        ("Padua scenario with buildings, number of hops with varying "
         "vehicle distance (" + graph_title_extension + ")"),
        x_list,
        x_labels,
        x_label,
        "Number of hops",
        figure_prefix + "DistanceVsNumberOfHops",
        compound_data["hopsMeans"],
        compound_data["hopsConfInts"],
        protocols,
        False,
        0,
        20
    )
    print_single_graph(
        cw,
        folder,
        ("Padua scenario with buildings, number of alert messages sent "
         "with varying vehicle distance (" + graph_title_extension + ")"),
        x_list,
        x_labels,
        x_label,
        "Number of sent alert messages",
        figure_prefix + "DistanceVsAlertMessagesSent",
        compound_data["messageSentMeans"],
        compound_data["messageSentConfInts"],
        protocols,
        False,
        0,
        250
    )
    print_single_graph(
        cw,
        folder,
        ("Padua scenario with buildings, number of slots waited with "
         "varying vehicle distance (" + graph_title_extension + ")"),
        x_list,
        x_labels,
        x_label,
        "Number of slots waited",
        figure_prefix + "DistanceVsSlotsWaited",
        compound_data["slotsWaitedMeans"],
        compound_data["slotsWaitedConfInts"],
        protocols,
        True
    )


def print_cw_comparison(cws, vehicle_distance, protocols, x_list, x_labels,
                       figure_prefix, graph_title_extension, folder,
                       decrease_conf_ints=False):
    plt.rcParams["figure.figsize"] = [18, 10]
    base_path = "../../simulations/scenario-urbano"
    base_path2 = os.path.join("Padova", "d" + str(vehicle_distance), "b1")
    compound_data = init_compound_data(protocols)
    x_label = "Contention window"
    for cw in cws:
        base_path_with_distance = os.path.join(base_path, cw, base_path2)
        append_compound_data(base_path_with_distance, protocols, compound_data,
                           decrease_conf_ints)
    # Print graphs
    print_single_graph(
        cw,
        folder,
        ("Padua scenario with buildings, total coverage with varying "
         "contention window (" + graph_title_extension + ")"),
        x_list,
        x_labels,
        x_label,
        "Total coverage (%)",
        figure_prefix + "CwVsTotalCover",
        compound_data["totCoverageMeans"],
        compound_data["totCoverageConfInts"],
        protocols
    )
    print_single_graph(
        cw,
        folder,
        ("Padua scenario with buildings, coverage on circumference with "
         "varying contention window (" + graph_title_extension + ")"),
        x_list,
        x_labels,
        x_label,
        "Coverage on circumference (%)",
        figure_prefix + "CwVsCoverOnCircumference",
        compound_data["covOnCircMeans"],
        compound_data["covOnCircConfInts"],
        protocols
    )
    print_single_graph(
        cw,
        folder,
        ("Padua scenario with buildings, number of hops with varying "
         "contention window (" + graph_title_extension + ")"),
        x_list,
        x_labels,
        x_label,
        "Number of hops",
        figure_prefix + "CwVsNumberOfHops",
        compound_data["hopsMeans"],
        compound_data["hopsConfInts"],
        protocols,
        False,
        0,
        20
    )
    print_single_graph(
        cw,
        folder,
        ("Padua scenario with buildings, number of alert messages sent "
         "with varying contention window (" + graph_title_extension + ")"),
        x_list,
        x_labels,
        x_label,
        "Number of sent alert messages",
        figure_prefix + "CwVsAlertMessagesSent",
        compound_data["messageSentMeans"],
        compound_data["messageSentConfInts"],
        protocols,
        False,
        0,
        160
    )
    print_single_graph(
        cw,
        folder,
        ("Padua scenario with buildings, number of slots waited with "
         "varying contention window (" + graph_title_extension + ")"),
        x_list,
        x_labels,
        x_label,
        "Number of slots waited",
        figure_prefix + "CwVsSlotsWaited",
        compound_data["slotsWaitedMeans"],
        compound_data["slotsWaitedConfInts"],
        protocols,
        True
    )


def print_romanelli_comparison(cw, vehicle_distance, protocols, x_list,
                              x_labels, figure_prefix, graph_title_extension,
                              folder, base_path, decrease_conf_ints=False):
    plt.rcParams["figure.figsize"] = [18, 10]
    buildings = ["0", "1"]
    for b in buildings:
        actual_folder = os.path.join(folder, "b" + b)
        print("folder = ")
        print(folder)
        print("actual folder = ")
        print(actual_folder)
        actual_base_path = os.path.join(base_path, cw, "Padova/d25/", "b" + b)
        x_label = "Protocol-transmission range"
        compound_data = init_compound_data(protocols)
        append_compound_data(actual_base_path, protocols, compound_data,
                           decrease_conf_ints)
        rom_tot_cov = [45.49, 94.35, 47.45, 56.93, 50.30, 94.11]
        rom_cov_circ = [23.81, 94.75, 22.06, 64.80, 27.78, 93.88]
        rom_num_hops = [7.30, 2.14, 6.62, 3.41, 7.57, 2.07]
        rom_alert_sent = [219, 109, 236, 45, 253, 107]
        rom_slots_waited = [0, 0, 0, 0, 0, 0]
        # rom_tot_cov = [45.49, 94.35, 47.45, 94.11]
        # rom_cov_circ = [23.81, 94.75, 22.06, 93.88]
        # rom_num_hops = [7.30, 2.14, 6.62, 2.07]
        # rom_alert_sent = [219, 109, 236, 107]

        print(rom_tot_cov)
        print_single_graph_romanelli_comparison(
            cw,
            actual_folder,
            "Padua scenario with buildings, total coverage",
            x_list,
            x_labels,
            x_label,
            "Total coverage (%)",
            figure_prefix + "TotalCoverage",
            compound_data["totCoverageMeans"],
            compound_data["totCoverageConfInts"],
            rom_tot_cov,
            protocols,
            True
        )
        print_single_graph_romanelli_comparison(
            cw,
            actual_folder,
            "Padua scenario with buildings, coverage on circumference",
            x_list,
            x_labels,
            x_label,
            "Coverage on circumference (%)",
            figure_prefix + "CoverageOnCirc",
            compound_data["covOnCircMeans"],
            compound_data["covOnCircConfInts"],
            rom_cov_circ,
            protocols,
            True
        )
        print_single_graph_romanelli_comparison(
            cw,
            actual_folder,
            "Padua scenario with buildings, number of hops",
            x_list,
            x_labels,
            x_label,
            "Number of hops",
            figure_prefix + "NumberOfHops",
            compound_data["hopsMeans"],
            compound_data["hopsConfInts"],
            rom_num_hops,
            protocols,
            True,
            0,
            10
        )
        print_single_graph_romanelli_comparison(
            cw,
            actual_folder,
            "Padua scenario with buildings, number of alert messages sent",
            x_list,
            x_labels,
            x_label,
            "Number of sent alert messages",
            figure_prefix + "AlertMessagesSent",
            compound_data["messageSentMeans"],
            compound_data["messageSentConfInts"],
            rom_alert_sent,
            protocols,
            True,
            0,
            120
        )
        print_single_graph_romanelli_comparison(
            cw,
            actual_folder,
            "Padua scenario with buildings, number of slots waited",
            x_list,
            x_labels,
            x_label,
            "Number of slots waited",
            figure_prefix + "SlotsWaited",
            compound_data["slotsWaitedMeans"],
            compound_data["slotsWaitedConfInts"],
            rom_slots_waited,
            protocols,
            True,
            0,
            1500
        )
"""

'''
def print_single_graph_romanelli_comparison(cw, folder, graph_title, x_list,
                                          x_labels, x_label, y_label,
                                          figure_title, y_data_dictionary,
                                          conf_int_dictionary, rom_data,
                                          protocols, autoscale=False,
                                          y_bottom_lim=0, y_top_lim=100):

    y_data_dictionary = lists_to_list(y_data_dictionary, protocols)
    conf_int_dictionary = lists_to_list(conf_int_dictionary, protocols)

    ind = np.arange(len(x_labels))
    n = len(x_labels)
    # bar_width = float((float(1)/float(n)) * float(0.90))
    bar_width = 0.35
    fig, ax = plt.subplots()
    rects = []
    count = 0
    colors = ["0.3", "0.5"]
    # width_distance = [0, 1]
    # width_distance = [-1, 0, 1]
    # width_distance = [-1.5, -0.5, 0.5, 1.5]
    # for protocol in protocols:
    #     rects.append((ax.bar(ind + width_distance[count] * bar_width,
    #                         y_data_dictionary[protocol], bar_width,
    #                         color=colors[count], label=protocol,
    #                         yerr=conf_int_dictionary[protocol], capsize=4)))
    rects.append((ax.bar(ind, y_data_dictionary, bar_width, color=colors[0],
                        yerr=conf_int_dictionary, capsize=4)))
    # rects.append((ax.bar(ind + bar_width / 2, rom_data, bar_width,
    #                     color=colors[1], label="Romanelli")))

    ax.set_xlabel(x_label, fontsize=15)
    ax.set_ylabel(y_label, fontsize=15)
    if not autoscale:
        ax.set_ylim(y_bottom_lim, y_top_lim)
    # ax.set_title(graph_title, fontsize=20)
    ax.set_xticks(ind)
    ax.set_xticklabels(x_labels)
    # ax.set_xticklabels(["15m", "25m", "35m", "45m"])

    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    ax.d(loc='center left', bbox_to_anchor=(1, 0.5))

    # ax.legend(loc="upper center")

    def autolabel(rects, xpos='center'):
        """
        Attach a text label above each bar in *rects*, displaying its height.

        *xpos* indicates which side to place the text w.r.t. the center of
        the bar. It can be one of the following {'center', 'right', 'left'}.
        """

        xpos = xpos.lower()  # normalize the case of the parameter
        ha = {'center': 'center', 'right': 'left', 'left': 'right'}
        offset = {'center': 0.5, 'right': 0.57, 'left': 0.43}  # x_txt = x + w*off

        for rect in rects:
            height = rect.get_height()
            ax.text(rect.get_x() + rect.get_width()*offset[xpos], 1.01*height,
                    '{}'.format(height), ha=ha[xpos], va='bottom')

    for rect in rects:
        autolabel(rect)
    # plt.savefig('a1.png')
    # plt.savefig('a2.png', bbox_inches='tight')

    out_path_directory = os.path.join("out", folder)
    out_path = os.path.join(out_path_directory, figure_title)
    if not os.path.exists(out_path_directory):
        os.makedirs(out_path_directory)

    plt.savefig(out_path + ".pdf")
    plt.close()  # This releases the memory
    # plt.savefig('b2.pdf', bbox_inches='tight')
    # plt.show()

'''
