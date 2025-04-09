#!/bin/bash

if [ $# -lt 1 ]; then
  echo "Usage: $0 <command> [args...]"
  exit 1
fi

# Record the start time
start_time=$(date +%s)
start_time_readable=$(date +"%Y-%m-%d %H:%M:%S")
echo "Starting at: $start_time_readable"

# Run the given command
"$@"
exit_code=$?

# Record the end time
end_time=$(date +%s)
end_time_readable=$(date +"%Y-%m-%d %H:%M:%S")

# Calculate elapsed time
elapsed=$((end_time - start_time))

# Format elapsed time nicely
mins=$((elapsed / 60))
secs=$((elapsed % 60))

echo "Finished at: $end_time_readable"
echo "Elapsed time: ${mins}m ${secs}s"

# Exit with the same code as the executed command
exit $exit_code
