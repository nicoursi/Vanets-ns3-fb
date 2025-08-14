#!/bin/bash
# Submit all .slurm files in the current directory
mkdir -p completed
mkdir -p logs

for job in *.slurm; do
    if [[ -f "$job" ]]; then
        if [[ "$job" == *losses* ]]; then
            read -t 10 -p "Are you sure you want to submit the file '$job'? (y/n): " confirm
            if [[ "$confirm" != "y" ]]; then
                echo "Skipping $job."
                continue
            fi
        fi

        echo "Submitting $job..."
        if sbatch "$job"; then
            echo "Successfully submitted $job. Moving to completed folder."
            mv "$job" completed/
        else
            echo "Failed to submit $job. Keeping file in current directory."
        fi

        sleep 1
    fi
done
