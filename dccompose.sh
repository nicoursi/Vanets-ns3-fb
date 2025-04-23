#!/bin/bash

# Ensure two arguments are passed
if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <docker_service> [cmd_file]"
  exit 1
fi

# Get the docker service name (required)
DOCKER_SERVICE="$1"
CMD_FILE="$2"

# Record the start time
start_time=$(date +%s)
start_time_readable=$(date +"%Y-%m-%d %H:%M:%S")
echo -e "\n*************************** Starting at: $start_time_readable ***************************"

# Step 1: Clean up orphaned/stopped containers
echo "Cleaning up stopped containers..."
docker container prune -f

# Step 2: If a cmd_file is provided, export SIMULATION_CMD from it
if [ -n "$CMD_FILE" ]; then
  if [ -f "$CMD_FILE" ]; then
    echo "Exporting SIMULATION_CMD from file: $CMD_FILE"
    export SIMULATION_CMD=$(cat "$CMD_FILE")
  else
    echo "Error: File '$CMD_FILE' not found!"
    exit 1
  fi
fi

# Step 3: Run the Docker service
echo "Running docker service '$DOCKER_SERVICE'..."
docker compose run --rm "$DOCKER_SERVICE"

exit_code=$?

# Record the end time
end_time=$(date +%s)
end_time_readable=$(date +"%Y-%m-%d %H:%M:%S")

# Calculate elapsed time
elapsed=$((end_time - start_time))

# Format elapsed time nicely
mins=$((elapsed / 60))
secs=$((elapsed % 60))


echo -e "\n*************************** Finished at: $end_time_readable ***************************"
echo "*************************** Elapsed time: ${mins}m ${secs}s ****************************************"

# Exit with the same code as the executed command
exit $exit_code
