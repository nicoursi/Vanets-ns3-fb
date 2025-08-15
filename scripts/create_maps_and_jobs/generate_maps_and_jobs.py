#!/usr/bin/python3

# Invocation:
#     ./generate_maps_and_jobs.py ../maps/testMap/osm.osm.xml 25
# if you want to specify map and distance by hand, otherwise:
#     ./generate_maps_and_jobs.py
# if you want to automatically generate jobs for the scenarios and distances set in the main

# cspell:words jtoc jgottard jobarray
import sys
import shutil
import argparse
import json
from pathlib import Path
from jobs_utils import find_project_root


def parse_arguments():
    """Parse command line arguments with comprehensive help and examples."""
    # Define default values as variables so they reflect in help
    default_print_coords = False
    default_gen_loss_file = False
    default_only_command = False
    default_job_array = "1-50"
    default_scenarios = ["Padova-25"]
    default_contention_windows = [{"cwMin": 32, "cwMax": 1024}]
    default_high_buildings = ["0"]
    default_drones = ["0"]
    default_buildings = ["0", "1"]
    default_error_rates = ["0"]
    default_forged_coord_rates = ["0"]
    default_junctions = ["0"]
    default_protocols = ["1", "2", "3", "4", "5", "6"]
    default_tx_ranges = ["100", "300", "500", "700"]
    default_tx_powers = ""
    default_job_template = "job_template.slurm"
    default_job_template_only_command = "job_template_only_command.job"
    project_root = find_project_root()
    # default_jobs_path = Path(project_root) / "scheduled_jobs"
    default_jobs_path = Path(".")

    # Protocol mapping for help display
    protocols_map = {
        "1": "Fast-Broadcast",
        "2": "STATIC-100",
        "3": "STATIC-300",
        "4": "STATIC-500",
        "5": "STATIC-700",
        "6": "ROFF",
    }

    # Create protocol help string
    protocols_help = (
        "Comma-separated list of protocol IDs. Available protocols: "
        + ", ".join([f"{k}={v}" for k, v in protocols_map.items()])
        + f" (default: {','.join(default_protocols)})"
    )

    parser = argparse.ArgumentParser(
        description="Generate SLURM job templates for VANET simulations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f'''
Examples:
  # Use default parameters
  ./generate_maps_and_jobs.py

  # Use only-command template
  ./generate_maps_and_jobs.py --only-command

  # Override specific scenarios and protocols
  ./generate_maps_and_jobs.py --scenarios "{",".join(default_scenarios[:2] if len(default_scenarios) > 1 else default_scenarios)}" --protocols "{",".join(default_protocols[:3])}"

  # Custom job array and enable coordinate printing
  ./generate_maps_and_jobs.py --jobArray "1-100" --printCoords

  # Custom contention windows (JSON format)
  ./generate_maps_and_jobs.py --contentionWindows '[{{"cwMin": 16, "cwMax": 128}}, {{"cwMin": 32, "cwMax": 1024}}]'

  # Enable buildings and drones with custom transmission ranges
  ./generate_maps_and_jobs.py --buildings "{",".join([*default_buildings, "0"])}" --drones "{",".join([*default_drones, "1"])}" --txRanges "{",".join(default_tx_ranges[:3])}"

  # Custom error rates and forged coordinate rates
  ./generate_maps_and_jobs.py --errorRates "{",".join([*default_error_rates, "10", "20"])}" --forgedCoordRates "{",".join([*default_forged_coord_rates, "10", "20"])}"

  # Override resource requirements
  ./generate_maps_and_jobs.py --ram "4G" --neededTime "02:30:00"

  # Specify custom jobs output path
  ./generate_maps_and_jobs.py --jobsPath "/path/to/custom/jobs/directory"

  # Use custom job templates
  ./generate_maps_and_jobs.py --jobTemplate "custom-template.slurm" --jobTemplateOnlyCommand "custom-only-command.job"
        ''',
    )

    # Optional parameters
    parser.add_argument(
        "--genLossFile",
        "-l",
        action="store_true",
        help=f"Creates a Obstacle shadowing loss file (default: {default_gen_loss_file})",
    )
    parser.add_argument(
        "--printCoords",
        "-pc",
        action="store_true",
        help=f"Enable coordinate printing in simulations (default: {default_print_coords})",
    )

    parser.add_argument(
        "--only-command",
        "-oc",
        action="store_true",
        help=f"Use only-command job template instead of standard SLURM template (default: {default_only_command})",
    )

    parser.add_argument(
        "--jobArray",
        "-ja",
        type=str,
        default=default_job_array,
        help=f"SLURM job array specification (default: {default_job_array})",
    )

    parser.add_argument(
        "--scenarios",
        "-s",
        type=str,
        default=",".join(default_scenarios),
        help=f"Comma-separated list of scenarios (default: {','.join(default_scenarios)})",
    )

    parser.add_argument(
        "--contentionWindows",
        "-cw",
        type=str,
        default=json.dumps(default_contention_windows),
        help=f"JSON array of contention window configurations (default: {json.dumps(default_contention_windows)})",
    )

    parser.add_argument(
        "--highBuildings",
        "-hb",
        type=str,
        default=",".join(default_high_buildings),
        help=f"Comma-separated list of high buildings settings (default: {','.join(default_high_buildings)})",
    )

    parser.add_argument(
        "--drones",
        "-d",
        type=str,
        default=",".join(default_drones),
        help=f"Comma-separated list of drone settings (default: {','.join(default_drones)})",
    )

    parser.add_argument(
        "--buildings",
        "-b",
        type=str,
        default=",".join(default_buildings),
        help=f"Comma-separated list of building settings (default: {','.join(default_buildings)})",
    )

    parser.add_argument(
        "--errorRates",
        "-e",
        type=str,
        default=",".join(default_error_rates),
        help=f"Comma-separated list of error rates (default: {','.join(default_error_rates)})",
    )

    parser.add_argument(
        "--forgedCoordRates",
        "-fc",
        type=str,
        default=",".join(default_forged_coord_rates),
        help=f"Comma-separated list of forged coordinate rates (default: {','.join(default_forged_coord_rates)})",
    )

    parser.add_argument(
        "--junctions",
        "-j",
        type=str,
        default=",".join(default_junctions),
        help=f"Comma-separated list of junction settings (default: {','.join(default_junctions)})",
    )

    parser.add_argument(
        "--protocols", "-p", type=str, default=",".join(default_protocols), help=protocols_help
    )

    parser.add_argument(
        "--txRanges",
        "-tx",
        type=str,
        default=",".join(default_tx_ranges),
        help=f"Comma-separated list of transmission ranges (default: {','.join(default_tx_ranges)})",
    )
    parser.add_argument(
        "--txPowers",
        "-tp",
        type=str,
        default=",".join(default_tx_powers),
        help=f"Comma-separated list of transmission powers per transfer ranges (format: (tx_range:tx_power) default: {','.join(default_tx_powers)})",
    )
    parser.add_argument(
        "--neededTime",
        "-nt",
        type=str,
        default=None,
        help="Override default time allocation for all jobs (format: HH:MM:SS)",
    )

    parser.add_argument(
        "--ram",
        "-r",
        type=str,
        default=None,
        help='Override default RAM allocation for all jobs (e.g., "4G", "8G")',
    )

    parser.add_argument(
        "--jobsPath",
        "-jp",
        type=str,
        default=str(default_jobs_path),
        help=f"Custom path for job templates output directory (default: {default_jobs_path})",
    )

    parser.add_argument(
        "--jobTemplate",
        "-jt",
        type=str,
        default=default_job_template,
        help=f"Standard job template filename (default: {default_job_template})",
    )

    parser.add_argument(
        "--jobTemplateOnlyCommand",
        "-jtoc",
        type=str,
        default=default_job_template_only_command,
        help=f"Only-command job template filename (default: {default_job_template_only_command})",
    )

    # Positional arguments (for backward compatibility)
    parser.add_argument(
        "mapPath", nargs="?", default=None, help="Path to the map file (optional, for manual mode)"
    )
    parser.add_argument(
        "vehicleDistance",
        nargs="?",
        default=None,
        help="Vehicle distance (optional, for manual mode)",
    )

    return parser.parse_args()


def find_num_nodes(mobility_file_path):
    """Find the maximum number of nodes from mobility file."""
    print(mobility_file_path)
    mobility_path = Path(mobility_file_path)

    with mobility_path.open("r") as file:
        max_id = -sys.maxsize - 1
        for line in file:
            split_line = line.split(" ")
            if len(split_line) == 4:
                node_id = int(split_line[0].split("_")[1].replace("(", "").replace(")", ""))
                max_id = max(max_id, node_id)
    return max_id + 1


def create_job_file(
    new_job_name,
    command,
    jobs_path,
    job_template_path,
    temp_new_job_path,
    ram,
    needed_time,
    job_array,
):
    """Create a SLURM job file from template with specified parameters."""
    jobs_path = Path(jobs_path)
    job_template_path = Path(job_template_path)
    temp_new_job_path = Path(temp_new_job_path)

    # Get file extension from template
    template_extension = job_template_path.suffix
    new_job_filename = f"{new_job_name}-{template_extension}"
    new_job_path = jobs_path / new_job_filename
    simulation = command.split()[0]

    # Copy template and rename
    shutil.copy(str(job_template_path), str(jobs_path))
    temp_new_job_path.rename(new_job_path)

    # Read template content and perform substitutions
    content = new_job_path.read_text()

    content = content.replace("{**jobName}", new_job_name)
    content = content.replace("{**command}", command)
    content = content.replace("{**ram}", ram)
    content = content.replace("{**neededTime}", needed_time)
    content = content.replace("{**jobarray}", job_array)

    if simulation == "fb-vanet-urban":
        content = content.replace("{**sim_folder}", "fb-vanet-urban")
    elif simulation == "roff-test":
        content = content.replace("{**sim_folder}", "roff-test")

    # Write modified content back to file
    new_job_path.write_text(content)


def run_scenario(
    cw, scenario, distance, starting_node, vehicles_number, job_array, print_coords, area, config
):
    """Generate job files for a specific scenario configuration."""
    print(f"Processing scenario: {scenario}")

    # Extract configuration values
    high_buildings = config["highBuildings"]
    drones = config["drones"]
    buildings = config["buildings"]
    error_rates = config["errorRates"]
    forged_coord_rates = config["forgedCoordRates"]
    junctions = config["junctions"]
    protocols = config["protocols"]
    tx_ranges = config["txRanges"]
    tx_powers = config["txPowers"]
    jobs_path = Path(config["jobsPath"])
    gen_loss_file = config["genLossFile"]
    only_command = config["onlyCommand"]
    job_template_filename = (
        config["jobTemplateOnlyCommand"] if only_command else config["jobTemplate"]
    )

    create_obstacle_shadowing_loss_file = int(gen_loss_file)
    use_obstacle_shadowing_loss_file = int(not gen_loss_file)

    protocols_map = {
        "1": "Fast-Broadcast",
        "2": "STATIC-100",
        "3": "STATIC-300",
        "4": "STATIC-500",
        "5": "STATIC-700",
        "6": "ROFF",
    }

    cw_min = cw["cwMin"]
    cw_max = cw["cwMax"]

    # Some necessary paths
    this_script_path = Path(__file__).resolve()
    this_script_parent_path = this_script_path.parent
    root_project_path = Path(find_project_root())
    ns_path = root_project_path / "ns-3.26"

    job_template_path = this_script_parent_path / "jobs_templates" / job_template_filename
    temp_new_job_path = jobs_path / job_template_filename

    # Input parameters
    if scenario is None or distance is None:
        map_path = Path(sys.argv[1])
        vehicle_distance = sys.argv[2]
    else:
        map_path = Path(f"../maps/{scenario}/{scenario}.osm.xml")
        vehicle_distance = distance

    # Calculate directories and filenames
    abs_map_path = map_path.resolve()
    abs_map_parent_path = abs_map_path.parent

    map_base_name = map_path.name.split(".")[0]
    map_base_name_with_distance = map_base_name
    map_path_without_extension = map_path.parent / map_base_name_with_distance

    print(f"    mapBasePath: {map_path_without_extension}")

    # Define paths of files necessary for ns3
    mobility_file_path = abs_map_parent_path / f"{map_base_name_with_distance}.ns2mobility.xml"
    polygon_file_path = abs_map_parent_path / f"{map_base_name_with_distance}.poly.xml"
    polygon_file_path_3d = abs_map_parent_path / f"{map_base_name_with_distance}.3D.poly.xml"

    # Run generate sumo files
    sumo_file_generator = (
        f"{this_script_parent_path / 'generate-sumo-files.sh'} {map_path} {vehicle_distance}"
    )
    # Uncomment to generate sumoFiles again
    # os.system(sumo_file_generator)

    # Use config values for ram if provided, otherwise use default logic
    ram = config["ram"] if config["ram"] else "2G"

    # Create job templates inside jobTemplates/
    for high_building in high_buildings:
        for drone in drones:
            for b in buildings:
                if b == "1" and not config["ram"]:  # Only apply default logic if ram not overridden
                    ram = "8G"
                elif not config["ram"]:
                    ram = "2G"

                for tx_range in tx_ranges:
                    for protocol in protocols:
                        # Use config needed_time if provided, otherwise use scenario-specific logic
                        if config["neededTime"]:
                            needed_time = config["neededTime"]
                        # Scenario-based time allocation logic
                        elif "Grid" in scenario:
                            if protocol in {"2", "3", "4", "5"}:
                                needed_time = "02:00:00"
                            else:
                                needed_time = "10:00:00"
                        elif "Padova" in scenario or "LA-" in scenario:
                            if gen_loss_file:
                                needed_time = "48:00:00"
                            elif protocol in {"2", "3", "4", "5"}:
                                needed_time = "02:00:00"
                            else:
                                needed_time = "10:00:00"
                        elif "Cube" in scenario:
                            needed_time = "48:00:00"
                        # Fallback to original logic for unknown scenarios
                        elif protocol in {"2", "3", "4", "5"}:
                            needed_time = "04:45:00"
                        elif protocol in {"6"}:
                            needed_time = "48:30:00"
                        else:
                            needed_time = "48:30:00"

                        for junction in junctions:
                            for error_rate in error_rates:
                                protocol_name = protocols_map[protocol]
                                # Skip job generation for error rates > 0 with STATIC protocols
                                if error_rate != "0" and "STATIC" in protocol_name:
                                    continue

                                propagation_loss = "1"
                                if "Cube" in scenario:
                                    propagation_loss = "0"

                                if protocol == "6":  # ROFF
                                    command = (
                                        f"roff-test \\"
                                        f"\n  --buildings={b} \\"
                                        f"\n  --actualRange={tx_range} \\"
                                        f"\n  --mapBasePath={map_path_without_extension} \\"
                                        f"\n  --vehicleDistance={distance} \\"
                                        f"\n  --startingNode={starting_node} \\"
                                        f"\n  --propagationLoss={propagation_loss} \\"
                                        f"\n  --area={area} \\"
                                        f"\n  --smartJunctionMode={junction} \\"
                                        f"\n  --errorRate={error_rate} \\"
                                        f"\n  --nVehicles={vehicles_number} \\"
                                        f"\n  --droneTest={drone} \\"
                                        f"\n  --highBuildings={high_building} \\"
                                        f"\n  --printToFile=1 \\"
                                        f"\n  --printCoords={print_coords} \\"
                                        f"\n  --createObstacleShadowingLossFile={create_obstacle_shadowing_loss_file} \\"
                                        f"\n  --useObstacleShadowingLossFile={use_obstacle_shadowing_loss_file} \\"
                                        f"\n  --beaconInterval=100 \\"
                                        f"\n  --distanceRange=1 \\"
                                        f"\n  --forgedCoordTest=0 \\"
                                        f"\n  --forgedCoordRate=0 \\"
                                        f"\n  --maxRun=1 \\"
                                        f"\n  {f'--txPower={tx_powers[int(tx_range)]}' if int(tx_range) in tx_powers else ''}"
                                    )
                                else:
                                    command = (
                                        f"fb-vanet-urban \\"
                                        f"\n  --buildings={b} \\"
                                        f"\n  --actualRange={tx_range} \\"
                                        f"\n  --mapBasePath={map_path_without_extension} \\"
                                        f"\n  --cwMin={cw_min} \\"
                                        f"\n  --cwMax={cw_max} \\"
                                        f"\n  --vehicleDistance={distance} \\"
                                        f"\n  --startingNode={starting_node} \\"
                                        f"\n  --propagationLoss={propagation_loss} \\"
                                        f"\n  --protocol={protocol} \\"
                                        f"\n  --area={area} \\"
                                        f"\n  --smartJunctionMode={junction} \\"
                                        f"\n  --errorRate={error_rate} \\"
                                        f"\n  --nVehicles={vehicles_number} \\"
                                        f"\n  --droneTest={drone} \\"
                                        f"\n  --highBuildings={high_building} \\"
                                        f"\n  --flooding=0 \\"
                                        f"\n  --printToFile=1 \\"
                                        f"\n  --printCoords={print_coords} \\"
                                        f"\n  --createObstacleShadowingLossFile={create_obstacle_shadowing_loss_file} \\"
                                        f"\n  --useObstacleShadowingLossFile={use_obstacle_shadowing_loss_file} \\"
                                        f"\n  --forgedCoordTest=0 \\"
                                        f"\n  --forgedCoordRate=0 \\"
                                        f"\n  --maxRun=1 \\"
                                        f"\n  {f'--txPower={tx_powers[int(tx_range)]}' if int(tx_range) in tx_powers else ''}"
                                    )

                                new_job_name = (
                                    f"urban-{map_base_name}"
                                    f"{'-losses' if create_obstacle_shadowing_loss_file == 1 else ''}"
                                    f"-highBuildings{high_building}"
                                    f"-drones{drone}"
                                    f"-d{vehicle_distance}"
                                    f"-cw-{cw_min}-{cw_max}"
                                    f"-b{b}"
                                    f"-e{error_rate}"
                                    f"-j{junction}"
                                    f"-{protocols_map[protocol]}"
                                    f"-{tx_range}"
                                    f"{'-with-coords' if print_coords == 1 else ''}"
                                    f"{f'-txPower={tx_powers[int(tx_range)]}' if int(tx_range) in tx_powers else ''}"
                                )

                                create_job_file(
                                    new_job_name,
                                    command,
                                    str(jobs_path),
                                    str(job_template_path),
                                    str(temp_new_job_path),
                                    ram,
                                    needed_time,
                                    job_array,
                                )

                            """
                            # FORGED COORD SCENARIO
                            if (scenario == "LA-25" and distance == "25"):
                                for forgedCoordRate in forgedCoordRates:
                                    propagationLoss = "1"
                                    if (protocol == "5"): #ROFF
                                        command = "NS_GLOBAL_VALUE=\"RngRun=1\" /home/jgottard/ns-3/ns-3.26/build/scratch/roff-test/roff-test --buildings={0} --actualRange={1} --mapBasePath={2} --vehicleDistance={3} --startingNode={4} --propagationLoss={5} --area={6} --smartJunctionMode={7} --errorRate=0 --printToFile=1 --printCoords=0  --createObstacleShadowingLossFile=0 --useObstacleShadowingLossFile=1  --beaconInterval=100 --distanceRange=1 --forgedCoordTest=1 --forgedCoordRate={8}".format(b, txRange, mapPathWithoutExtension, distance, startingNode, propagationLoss, area, junction, forgedCoordRate)
                                    else:
                                        command = "NS_GLOBAL_VALUE=\"RngRun=1\" /home/jgottard/ns-3/ns-3.26/build/scratch/fb-vanet-urban/fb-vanet-urban --buildings={0} --actualRange={1} --mapBasePath={2} --cwMin={3} --cwMax={4} --vehicleDistance={5} --startingNode={6} --propagationLoss={7} --protocol={8} --area={9} --smartJunctionMode={10} --errorRate=0 --flooding=0  --printToFile=1 --printCoords=0 --createObstacleShadowingLossFile=0 --useObstacleShadowingLossFile=1 --forgedCoordTest=1 --forgedCoordRate={11}".format(b, txRange, mapPathWithoutExtension, cwMin, cwMax, distance, startingNode, propagationLoss, protocol, area, junction, forgedCoordRate)
                                    newJobName = "urban-" + mapBaseName + "-d" + str(vehicleDistance) + "-cw-" +str(cwMin) + "-" + str(cwMax) + "-b" + b + "-f" + forgedCoordRate + "-j" + junction + "-" + protocolsMap[protocol] + "-" + txRange
                                    createJobFile(newJobName, command, jobsPath, jobTemplatePath, tempNewJobPath)
                            """

    print("\n")


def parse_tx_power_string(tx_power_str=""):
    """
    Parse a transmission power string into a dictionary.

    Args:
        tx_power_str (str): String in format "range1:power1,range2:power2,..." or empty string

    Returns:
        dict: Dictionary with transmission ranges as keys and dB values as values
    """
    tx_power_dict = {}

    if not tx_power_str:  # Handle empty string default
        return tx_power_dict

    # Split by comma to get individual range:power pairs
    pairs = tx_power_str.split(",")

    for pair in pairs:
        # Split each pair by colon to get range and power
        range_str, power_str = pair.split(":")
        tx_range = int(range_str.strip())
        tx_power = float(power_str.strip())
        tx_power_dict[tx_range] = tx_power

    return tx_power_dict


def main():
    """Main function to parse arguments and execute scenario generation."""
    args = parse_arguments()
    # You only need one job for a loss file
    job_array = "1" if args.genLossFile else args.jobArray
    # Always print coords for losses files
    print_coords = int(args.genLossFile or args.printCoords)
    only_command = getattr(args, "only_command", False)

    # Parse scenarios
    scenarios = [s.strip() for s in args.scenarios.split(",") if s.strip()]

    # Parse contention windows (JSON format)
    try:
        contention_windows = json.loads(args.contentionWindows)
    except json.JSONDecodeError as e:
        print(f"Error parsing contentionWindows JSON: {e}")
        sys.exit(1)

    # Parse comma-separated lists
    high_buildings = [s.strip() for s in args.highBuildings.split(",") if s.strip()]
    drones = [s.strip() for s in args.drones.split(",") if s.strip()]
    # if generating a loss file use only buildings
    if args.genLossFile:
        buildings = ["1"]
        tx_ranges = ["500"]
        protocols = ["1"]
    else:
        buildings = [s.strip() for s in args.buildings.split(",") if s.strip()]
        tx_ranges = [s.strip() for s in args.txRanges.split(",") if s.strip()]
        protocols = [s.strip() for s in args.protocols.split(",") if s.strip()]

    error_rates = [s.strip() for s in args.errorRates.split(",") if s.strip()]
    forged_coord_rates = [s.strip() for s in args.forgedCoordRates.split(",") if s.strip()]
    junctions = [s.strip() for s in args.junctions.split(",") if s.strip()]

    tx_powers = parse_tx_power_string(args.txPowers)
    print(f"tx_powers chosen:  {tx_powers}")
    # Create configuration dictionary
    config = {
        "highBuildings": high_buildings,
        "drones": drones,
        "buildings": buildings,
        "errorRates": error_rates,
        "forgedCoordRates": forged_coord_rates,
        "junctions": junctions,
        "protocols": protocols,
        "txRanges": tx_ranges,
        "txPowers": tx_powers,
        "neededTime": args.neededTime,
        "ram": args.ram,
        "jobsPath": args.jobsPath,
        "genLossFile": args.genLossFile,
        "onlyCommand": only_command,
        "jobTemplate": args.jobTemplate,
        "jobTemplateOnlyCommand": args.jobTemplateOnlyCommand,
    }

    # Original hardcoded values for reference (commented options preserved)
    # scenarios = ["Grid-300-node+-5"]
    # scenarios = ["LA-25"]
    # scenarios = ["Padova-5", "Padova-15", "Padova-25", "Padova-35", "Padova-45"]
    # scenarios = ["Padova-15", "Padova-25", "Padova-35", "Padova-45", "LA-15", "LA-25", "LA-35", "LA-45"]
    # contention_windows = [{"cwMin": 32, "cwMax": 1024}, {"cwMin": 16, "cwMax": 128}]
    # contention_windows = [{"cwMin": 16, "cwMax": 128}]
    # distances = ["15", "25", "35", "45"]
    # scenarios = ["Padova"]

    starting_node_map = {
        "Padova-5": 1212,
        "Padova-15": 1182,
        "Padova-25": 310,
        "Padova-35": 1273,
        "Padova-45": 824,
        "LA-5": 124,
        "LA-15": 2355,
        "LA-25": 1009,
        "LA-35": 459,
        "LA-45": 354,
        "Grid-200": 2024,
        "Grid-300": 3136,
        "Grid-300+-5": 4896,
        "Grid-300-node+-5": 3366,
        "Grid-400": 1248,
        "Platoon": 0,
        "Platoon-15km": 0,
        # "Cube-75": 13965,
        "Cube-150": 4210,  # modified, original was wrongly 4209
        "Cube-200": 2184,
        "Cube-125": 7212,
    }

    vehicles_number = {
        "LA-5": 2984,
        "LA-15": 2396,
        "LA-25": 1465,
        "LA-35": 1083,
        "LA-45": 861,
        "Padova-5": 0,
        "Padova-15": 0,
        "Padova-25": 0,
        "Padova-35": 0,
        "Padova-45": 0,
        "Platoon-15km": 0,
        "Grid-200": 0,
        "Grid-300": 0,
        "Grid-300+-5": 0,
        "Grid-300-node+-5": 0,
        "Grid-400": 0,
        "Cube-75": 0,
        "Cube-125": 0,
        "Cube-150": 0,
        "Cube-200": 0,
    }

    area = 1000

    # Use custom jobs_path if provided
    jobs_path = Path(config["jobsPath"])
    # Create directory if it doesn't exist
    if not jobs_path.exists():
        jobs_path.mkdir(parents=True, exist_ok=True)

    """
    # Remove all previous job templates in output directory
    if jobs_path.exists():
        files_to_remove = [f for f in jobs_path.iterdir() if f.is_file()]
        for file_path in files_to_remove:
            file_path.unlink()
    """

    # Check if manual mode (positional arguments provided)
    if args.mapPath and args.vehicleDistance:
        run_scenario(None, None, None, None, None, job_array, print_coords, area, config)
    else:
        for cw in contention_windows:
            for scenario in scenarios:
                if "Platoon" in scenario:
                    area = 14000
                if "Grid" in scenario:
                    area = 2000
                if "Cube" in scenario and scenario != "Cube-75":
                    area = 1300
                if "Grid" in scenario or "Platoon" in scenario:
                    run_scenario(
                        cw,
                        scenario,
                        "25",
                        starting_node_map[scenario],
                        vehicles_number[scenario],
                        job_array,
                        print_coords,
                        area,
                        config,
                    )
                else:
                    distance = scenario.split("-")[1]
                    run_scenario(
                        cw,
                        scenario,
                        distance,
                        starting_node_map[scenario],
                        vehicles_number[scenario],
                        job_array,
                        print_coords,
                        area,
                        config,
                    )


if __name__ == "__main__":
    main()
