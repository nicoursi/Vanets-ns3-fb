<!-- omit in toc -->
# 1. VANETs Simulation Project with NS-3
This repository contains my thesis project, which continues the work previously developed by Marco Barichello, Marco Simonelli and Jordan Gottardo. It focuses on VANET (Vehicular Ad‑hoc Network) simulations using NS‑3. It includes custom modifications to NS‑3 and various simulation scripts. The [ns-3](https://github.com/nicoursi/ns-3) folder is managed as a Git submodule and contains the original NS‑3.26 source code along with my modifications.

## 1. Repository Structure
Simplified repository structure

```
├── build_env                         # Scripts for running and building NS-3 simulations
│   ├── container/
│   │   ├── singularity-ns3.def       # Singularity container definition
│   │   └── singularity-ns3-image.sif # Singularity container image (to be built!)
│   ├── batch2_simulations_with_singularity.sh
│   ├── singularity_ns3_runner.sh
│   └── ...
├── docs                    # Documentation folder
├── maps/                   # Mobility and polygon files needed to run simulations
├── ns-3/                   # NS-3 submodule (official repo + modifications)
├── scheduled_jobs/         # Advised folder for slurm jobs to be executed
├── scripts/
│   ├── create_maps_and_jobs/
│   ├── draw_coords/        # Scripts for generating Network visualization graphs
│   └── graphs/             # Scripts for generating comparison graphs
├── simulations/            # Simulation outputs in csv format
└── README.md               # This file

```

## 2. Getting Started

Start from the [Getting Started](docs/GETTING_STARTED.md) section for detailed setup and usage instructions.

### 2.1. Cluster Access Setup

Some useful info about [Cluster Access Setup](docs/CLUSTER_ACCESS_SETUP.md).

### 2.2. Cluster Commands Cheat Sheet

Handy collection of frequently used commands: [Cluster Cheat Sheet](docs/CLUSTER_CHEAT_SHEET.md).

## 3. Working with Simulation Outputs

See the [Simulation Outputs](docs/SIMULATIONS_OUTPUTS.md) document for details on how to generate comparison graphs, network visualizations and general info on the simulation outputs.

## 4. Creating Maps and Jobs

For instructions about generating mobility and polygon `xml` files or `.slurm` jobs for executing the NS-3 simulations, check [Creating Jobs and Maps](/docs/CREATING_MAPS_AND_JOBS.md).

## 5. NS-3 Modifications

To see the modifications applied to the NS-3 code refer to th dedicated NS-3 [README](https://github.com/nicoursi/ns-3) file from the NS-3 submodule.

## 6. Contributing

1. Always work on the appropriate branch in the NS-3 submodule
2. Commit changes to NS-3 first, then update the main repository
3. Test modifications before pushing
4. Use the provided scripts for consistent simulation runs
