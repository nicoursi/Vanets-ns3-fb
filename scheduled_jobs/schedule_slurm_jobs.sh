#!/bin/bash

# spell:enableCompoundWords

# Script to schedule SLURM job submissions using 'at' command
# Usage: ./schedule_slurm_jobs.sh [OPTIONS]
#
# Options:
#   -w, --wildcard PATTERN    Wildcard pattern to move files from source folder (e.g., *STATIC*, *ROFF*)
#   -t, --time TIME          Time to wait before execution with unit (default: 1h)
#                           Supported units: m/min/minutes, h/hour/hours, d/day/days
#   -s, --source-folder PATH Source folder to move files from (default: tosubmitlater)
#   -h, --help               Show this help message
#
# Examples:
#   ./schedule_slurm_jobs.sh                           # Submit all jobs in 1 hour
#   ./schedule_slurm_jobs.sh -t 4h                     # Submit all jobs in 4 hours
#   ./schedule_slurm_jobs.sh -t 30m                    # Submit all jobs in 30 minutes
#   ./schedule_slurm_jobs.sh -w "*STATIC*" -t 10h      # Move *STATIC* files and submit in 10 hours
#   ./schedule_slurm_jobs.sh -w "*ROFF*" -t 90min      # Move *ROFF* files and submit in 90 minutes
#   ./schedule_slurm_jobs.sh -w "*TEST*" -s pending    # Move *TEST* files from 'pending' folder

# Default values
WILDCARD=""
TIME_SPEC="1h"
SOURCE_FOLDER="tosubmitlater"
SUBMITALL_SCRIPT="/home/nursino/storage/Vanets-ns3-fb/scheduled_jobs/submitall.sh"

# Function to display help
show_help() {
    cat <<EOF
Schedule SLURM Job Submission Script

USAGE:
    $0 [OPTIONS]

OPTIONS:
    -w, --wildcard PATTERN       Wildcard pattern to move files from source folder
                                (e.g., "*STATIC*", "*ROFF*")
    -t, --time TIME             Time to wait before execution with unit (default: 1h)
                               Supported units: m/min/minutes, h/hour/hours, d/day/days
    -s, --source-folder PATH    Source folder to move files from (default: tosubmitlater)
    -h, --help                  Show this help message

EXAMPLES:
    $0                           # Submit all jobs in current folder in 1 hour
    $0 -t 4h                     # Submit all jobs in 4 hours
    $0 -t 30m                    # Submit all jobs in 30 minutes
    $0 -w "*STATIC*" -t 10h      # Move *STATIC* files and submit in 10 hours
    $0 -w "*ROFF*" -t 90min      # Move *ROFF* files and submit in 90 minutes
    $0 -w "*TEST*" -s pending    # Move *TEST* files from 'pending' folder

DESCRIPTION:
    This script schedules SLURM job submissions using the 'at' command.
    
    Mode 1 (default): Submits all jobs found in the current folder
    Mode 2: Moves files matching wildcard pattern from source folder to current 
            directory, then submits all jobs
            
    All output is logged to logs/submitall.log
EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
    -w | --wildcard)
        WILDCARD="$2"
        shift 2
        ;;
    -t | --time)
        TIME_SPEC="$2"
        shift 2
        ;;
    -s | --source-folder)
        SOURCE_FOLDER="$2"
        shift 2
        ;;
    -h | --help)
        show_help
        exit 0
        ;;
    *)
        echo "Error: Unknown option '$1'"
        echo "Use -h or --help for usage information"
        exit 1
        ;;
    esac
done

# Function to parse and validate time specification
parse_time() {
    local time_spec="$1"
    local number=""
    local unit=""

    # Extract number and unit using regex
    if [[ "$time_spec" =~ ^([0-9]+)([a-zA-Z]*)$ ]]; then
        number="${BASH_REMATCH[1]}"
        unit="${BASH_REMATCH[2]}"
    else
        echo "Error: Invalid time format '$time_spec'"
        echo "Use format like: 30m, 2h, 1d (number + unit)"
        echo "Supported units: m/min/minutes, h/hour/hours, d/day/days"
        exit 1
    fi

    # Validate number
    if [ "$number" -lt 1 ]; then
        echo "Error: Time must be a positive integer"
        exit 1
    fi

    # Normalize unit and validate
    case "$unit" in
    "" | "h" | "hour" | "hours")
        AT_TIME_UNIT="hours"
        ;;
    "m" | "min" | "minutes")
        AT_TIME_UNIT="minutes"
        ;;
    "d" | "day" | "days")
        AT_TIME_UNIT="days"
        ;;
    *)
        echo "Error: Unsupported time unit '$unit'"
        echo "Supported units: m/min/minutes, h/hour/hours, d/day/days"
        exit 1
        ;;
    esac

    TIME_NUMBER="$number"
}

# Validate time parameter
parse_time "$TIME_SPEC"

# Check if submitall.sh exists
if [ ! -f "$SUBMITALL_SCRIPT" ]; then
    echo "Error: submitall.sh not found at $SUBMITALL_SCRIPT"
    exit 1
fi

# Create logs directory
mkdir -p logs

# Build the command to be executed
if [ -z "$WILDCARD" ]; then
    # Mode 1: Submit all jobs in current folder
    CMD="cd $PWD && $SUBMITALL_SCRIPT > logs/submitall.log 2>&1"
    echo "Scheduling job submission for all files in current directory in $TIME_NUMBER $AT_TIME_UNIT..."
else
    # Mode 2: Move files with wildcard pattern, then submit
    CMD="cd $PWD && mv $SOURCE_FOLDER/$WILDCARD . && $SUBMITALL_SCRIPT > logs/submitall.log 2>&1"
    echo "Scheduling job submission with wildcard '$WILDCARD' from '$SOURCE_FOLDER' in $TIME_NUMBER $AT_TIME_UNIT..."

    # Check if source folder exists
    if [ ! -d "$SOURCE_FOLDER" ]; then
        echo "Warning: Source folder '$SOURCE_FOLDER' does not exist"
        read -p "Create the folder '$SOURCE_FOLDER'? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            mkdir -p "$SOURCE_FOLDER"
            echo "Created folder: $SOURCE_FOLDER"
            echo "Note: The folder is empty, so the wildcard move operation may fail during execution."
        else
            echo "Aborted."
            exit 1
        fi
    fi
fi

# Schedule the job using 'at'
echo "$CMD" | at now + $TIME_NUMBER $AT_TIME_UNIT

if [ $? -eq 0 ]; then
    echo "Successfully scheduled job for execution in $TIME_NUMBER $AT_TIME_UNIT"
    echo "Command scheduled: $CMD"
    echo "Logs will be written to: logs/submitall.log"
    echo
    echo "Scheduled jobs: "
    atq
    echo
    echo "To see the exact command that has been queued: at -c <job_number>"
    echo "To cancel a scheduled job: atrm <job_number>"
else
    echo "Error: Failed to schedule job"
    exit 1
fi
