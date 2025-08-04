#!/usr/bin/env python3
"""
SLURM Template Processor

This script processes a SLURM template file and generates multiple SLURM files
for different script and scenario combinations. The template file is not modified.

Replacements:
- {**jobName} -> {script}-{scenario_name} (slashes replaced with hyphens, additional_args appended if provided)
- {**script} -> provided script value
- {**scenario} -> provided scenario value (full path)
- {**neededTime} -> provided time value (default: 5:00:00)
- {**Additional_args} -> provided additional arguments or empty string
"""

import argparse
import sys
from pathlib import Path
import os

# Default values for all parameters
DEFAULT_TEMPLATE = "draw_coords_template.slurm"
DEFAULT_TIME = "5:00:00"
DEFAULT_OUTPUT_DIR = "."
DEFAULT_ADDITIONAL_ARGS = ""
DEFAULT_SCRIPTS = "draw_coverage,draw_single_hops,drawSingleTransmission,draw_alert_paths"
DEFAULT_SCENARIOS = "Grid-300,Padova-25,LA-25"


def extract_scenario_name(scenario):
    """
    Extract the scenario name from a scenario path.
    For 'Grid-300/b1', returns 'Grid-300-b1'
    For 'LA-25', returns 'LA-25'

    Args:
        scenario (str): Scenario path

    Returns:
        str: Scenario name (replace slashes with hyphens)
    """
    return scenario.replace("/", "-")


def process_template(
    template_file,
    script,
    scenario,
    needed_time=DEFAULT_TIME,
    additional_args=DEFAULT_ADDITIONAL_ARGS,
    output_dir=DEFAULT_OUTPUT_DIR,
):
    """
    Process the SLURM template file and create a new file for the given script/scenario combination.

    Args:
        template_file (str): Path to the template file
        script (str): Script value for replacement
        scenario (str): Scenario value for replacement (can include subfolder)
        needed_time (str): Time value for replacement
        additional_args (str): Additional arguments for replacement
        output_dir (str): Output directory for generated files

    Returns:
        str: Path to the generated file
    """
    try:
        # Read the template file
        template_path = Path(template_file)
        if not template_path.exists():
            raise FileNotFoundError(f"Template file not found: {template_file}")

        with open(template_path, "r") as f:
            content = f.read()

        # Extract scenario name (replace slashes with hyphens)
        scenario_name = extract_scenario_name(scenario)

        # Create the job name from script and scenario name
        job_name = f"{script}-{scenario_name}"

        # If additional_args is provided, append it to job name (clean up dashes)
        if additional_args.strip():
            # Remove leading dashes, replace spaces and remaining dashes with single hyphens
            args_suffix = additional_args.strip().lstrip("-").replace(" ", "-").replace("--", "-")
            job_name = f"{job_name}-{args_suffix}"

        # Perform replacements
        replacements = {
            "{**jobName}": job_name,
            "{**script}": script,
            "{**scenario}": scenario,
            "{**neededTime}": needed_time,
            "{**Additional_args}": additional_args,
        }

        processed_content = content
        for placeholder, value in replacements.items():
            processed_content = processed_content.replace(placeholder, value)

        # Create output directory if it doesn't exist
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Generate output filename (include additional args if provided)
        if additional_args.strip():
            args_suffix = additional_args.strip().lstrip("-").replace(" ", "-").replace("--", "-")
            output_filename = f"{script}_{scenario_name}_{args_suffix}.slurm"
        else:
            output_filename = f"{script}_{scenario_name}.slurm"
        output_file_path = output_path / output_filename

        # Write the processed content to the output file
        with open(output_file_path, "w") as f:
            f.write(processed_content)

        print(f"Generated: {output_file_path}")
        return str(output_file_path)

    except Exception as e:
        print(
            f"Error processing template for script '{script}' and scenario '{scenario}': {e}",
            file=sys.stderr,
        )
        return None


def parse_list_string(list_str):
    """
    Parse a comma-separated string into a list.

    Args:
        list_str (str): Comma-separated string

    Returns:
        list: List of strings with whitespace stripped
    """
    return [item.strip() for item in list_str.split(",") if item.strip()]


def main():
    # Get the directory where this script is located
    script_dir = Path(__file__).resolve().parent
    default_template = script_dir / "jobs_templates" / DEFAULT_TEMPLATE

    parser = argparse.ArgumentParser(
        description="Process SLURM template file and generate multiple SLURM files for different script and scenario combinations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s  # Uses all default values
  %(prog)s --scripts "script1, script2" --scenarios "Grid-300, LA-25"
  %(prog)s --scripts "simulation" --scenarios "Grid-300/b1, LA-25/test" --template custom.slurm
  %(prog)s --scripts "analysis" --scenarios "exp1" --additional-args="--verbose --debug" --output-dir results/
        """,
    )

    parser.add_argument(
        "--template",
        "-t",
        default=str(default_template),
        help=f"Template file to process (default: {default_template})",
    )

    parser.add_argument(
        "--scripts",
        "-s",
        default=DEFAULT_SCRIPTS,
        help=f'Comma-separated list of scripts (default: "{DEFAULT_SCRIPTS}")',
    )

    parser.add_argument(
        "--scenarios",
        "-c",
        default=DEFAULT_SCENARIOS,
        help=f'Comma-separated list of scenarios (default: "{DEFAULT_SCENARIOS}")',
    )

    parser.add_argument(
        "--time",
        "-time",
        default=DEFAULT_TIME,
        help=f"Time value for replacement (default: {DEFAULT_TIME})",
    )

    parser.add_argument(
        "--additional-args",
        "-a",
        default=DEFAULT_ADDITIONAL_ARGS,
        nargs="?",
        const=DEFAULT_ADDITIONAL_ARGS,
        help=f'Additional arguments for replacement (default: "{DEFAULT_ADDITIONAL_ARGS}" - empty string). Use = syntax for arguments starting with --: --additional-args="--show-nodes"',
    )

    parser.add_argument(
        "--output-dir",
        "-o",
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory for generated SLURM files (default: {DEFAULT_OUTPUT_DIR})",
    )

    args = parser.parse_args()

    # Parse scripts and scenarios
    script_list = parse_list_string(args.scripts)
    scenario_list = parse_list_string(args.scenarios)

    if not script_list:
        print("Error: No valid scripts provided", file=sys.stderr)
        sys.exit(1)

    if not scenario_list:
        print("Error: No valid scenarios provided", file=sys.stderr)
        sys.exit(1)

    total_combinations = len(script_list) * len(scenario_list)

    print(f"Processing {len(script_list)} script(s) and {len(scenario_list)} scenario(s)")
    print(f"Total combinations: {total_combinations}")
    print(f"Scripts: {', '.join(script_list)}")
    print(f"Scenarios: {', '.join(scenario_list)}")
    print(f"Template: {args.template}")
    print(f"Output directory: {args.output_dir}")
    print(f"Time: {args.time}")
    print(f"Additional args: '{args.additional_args}'")
    print()

    # Process each script-scenario combination
    generated_files = []
    failed_combinations = []

    for script in script_list:
        for scenario in scenario_list:
            result = process_template(
                args.template, script, scenario, args.time, args.additional_args, args.output_dir
            )
            if result:
                generated_files.append(result)
            else:
                failed_combinations.append(f"{script}-{scenario}")

    # Summary
    print(f"\nSummary:")
    print(f"Successfully generated: {len(generated_files)} files")
    if failed_combinations:
        print(f"Failed combinations: {len(failed_combinations)} ({', '.join(failed_combinations)})")

    if failed_combinations:
        sys.exit(1)


if __name__ == "__main__":
    main()
