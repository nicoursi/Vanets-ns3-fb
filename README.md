# VANET Simulation Project with NS-3
This repository contains my thesis project, which continues the work previously developed by Marco Barichello, Marco Simonelli and Jordan Gottardo. It focuses on VANET (Vehicular Ad‑hoc Network) simulations using NS‑3. It includes custom modifications to NS‑3 and various simulation scripts. The [ns-3](https://github.com/nicoursi/ns-3) folder is managed as a Git submodule and contains the original NS‑3.26 source code along with my modifications.

## Repository Structure
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

## Getting Started

See the [Getting Started](docs/GETTING_STARTED.md) section for detailed setup and usage instructions.

### Cluster Access Setup
See the [Cluster Access Setup](docs/CLUSTER_ACCESS_SETUP.md) section for detailed instructions.

### Cluster Commands Cheat Sheet

If you are running simulations on the cluster or need quick references for Slurm and related commands, check the [Cluster Cheat Sheet](docs/CLUSTER_CHEAT_SHEET.md).

## Working with simulation outputs
See the [Simulation Outputs](docs/SIMULATIONS_OUTPUTS.md) document for details on how to generate comparison graphs, network visualizations and general info on the simulation outputs.

## Creating Maps

Generate mobility and polygon files for simulations. Generated files are placed in the `maps` folder. For detailed instructions see [Maps](docs/MAPS.md)
****

## NS-3 Modifications

To see the modifications applied the to NS-3 code refer to th dedicated NS-3 [README](https://github.com/nicoursi/ns-3) file from the NS-3 submodule.

## Key Features

- **Submodule Management**: Clean separation between official NS-3 and custom modifications
- **Docker Environment**: Consistent simulation environment across platforms (deprecated)
- **Cluster Support**: Singularity container for HPC cluster deployment
- **Automated Testing**: Scripts for running multiple simulation iterations locally
- **Custom Protocols**: Implementation of VANET-specific protocols (ROFF, Fast Broadcast)

## Contributing

1. Always work on the appropriate branch in the NS-3 submodule
2. Commit changes to NS-3 first, then update the main repository
3. Test modifications using the Docker environment before pushing
4. Use the provided scripts for consistent simulation runs

## Support

For questions about NS-3 modifications or simulation setup, refer to the code documentation in the respective source files.
