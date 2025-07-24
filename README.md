# VANET Simulation Project with NS-3
This repository contains my thesis project, which continues the work previously developed by Marco Barichello, Marco Simonelli and Jordan Gottardo. It focuses on VANET (Vehicular Ad‑hoc Network) simulations using NS‑3. It includes custom modifications to NS‑3 and various simulation scripts. The [ns-3](https://github.com/nicoursi/ns-3) folder is managed as a Git submodule and contains the original NS‑3.26 source code along with my modifications.

## Repository Structure
Simplified repository structure

```plaintext
├── ns-3/						# NS-3 submodule (official repo + modifications)
├── maps/						# Mobility and poly files neede to run simulations
├── simulations/					# simulation outputs in csv format
├── scripts/
├───── graphs/					# Scripts for generating comparison graphs
├───── drawCoords/				# Scripts for generating Network visualization graphs
├───── createSimpleScenarios/		# Scripts for generating mobility and polygon files for simple scenarios
├── jobsTemplate/					# Default folder for slurm jobs to be executed
├── run_singularity_local.sh		# Script for running simulations through the singularity container locally
├── run_singularity_cluster-host.sh
├── singularity-ns3.def			# Singularity container definition
└── README.md                   # This file
```

## Getting Started

See the [Getting Started](docs/GETTING_STARTED.md) section for detailed setup and usage instructions.

## Working with simulation outputs
See the [Simulation Outputs](docs/SIMULATIONS_OUTPUTS.md) document for details on how to generate comparison graphs, network visualization and general info on the simulation outputs.

## Creating Maps

Generate mobility and polygon files for simulations. Generated files are placed in the `maps` folder. For detailed instructions see [Maps](docs/MAPS.md)


## NS-3 Modifications

Two VANET protocols have been added: Fast-Broadcast (FB) and ROFF (for comparison purposes).
In addition, an obstacle shadowing model module has been integrated.
The mobility helper has been updated to support 3D coordinates.
The vanets-utils module provides utility classes shared among different VANET components.
Finally, the scratch folder contains test code for the ROFF and FB protocols under different scenarios.

```plaintext
src/
├── vanets-utils/
│   ├── command-logger.cc
│   ├── command-logger.h
│   ├── csv-manager.cc
│   ├── csv-manager.h
│   ├── Edge.cc
│   └── Edge.h
├── roff/
├── fast-broadcast/
├── obstacle/
├── mobility/
│   └── helper/
│       ├── ns2-mobility-helper.cc
│       └── ns2-mobility-helper.h
scratch/
├── fb-vanet-urban/
└── roff-test/
```


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
