# Working with simulation outputs
Simulation results are saved in the `simulations` folder. The folder contains multiple subfolders according to the different scenarios and parameters used for running the simulations. Each specific combination of parameters is run multiple times with progressive run numbers (id field in the csv file). As simulations are reproducible, if a simulation is run twice with the same run number (id) it should give the same results.

## Comparison Graphs
In the folder `scripts/graphs` there are multiple scripts for generating graphs. Currently only `printProtocolComparison.py` has been tested. It needs refactoring to support parameters. At the moment it needs changing the code to change scenarios, tx-ranges and so on. [TODO]

## Network visualization tool
In order to use the network visualization script you need to run simulations with  `--printCoords=1`. You can easily generate such jobs to be submitted to the cluster by using the `generateMapsAndJobsTemplate.py` script.

Example:

```
../scripts/createJobsAndMaps/generateMapsAndJobsTemplate.py -s "LA-25" --buildings "1" --jobArray "1-3" --printCoords --protocols "1,6"
```

After having produced the csv files with coordinates, you can generate different visualizations:

1. **Alert Paths**: shows, starting from the source node all the path the alert message takes to reach all nodes.
2. **Single Hops**: shows, for each hop, all the forwarders and the reached nodes
3. **Network coverage**: Shows a map with red and green nodes. The first are nodes that never received the alert, the latter are the ones that received it.
4. **Multiple Trasmissions**: shows for each transmission the node reached but a specific forwarder generating as many image files as the forwarders.

The scripts able to produce visualizations all share the same common parameters except some exception. They can process a single csv file, or a whole folder recursively. The outputs are released by default in the `./out/` folder from the executing path using the same folder structure as the source files.

The scripts able to produce the above mentioned network visualization graps are located in `scripts/draw_coords/ and are:

```plaintext
scripts/
├── draw_coords
│   ├── draw_multiple_transmissions.py
│   ├── draw_alert_paths.py
│   ├── draw_coverage.py
│   ├── draw_single_hops.py
└───└── draw_all.py
```


Example:

```
cd scripts/draw_coords
./draw_alert_paths.py -b ../../simulations/scenario-urbano-con-coord/LA-25/ --mapfolder ../../maps
```

The command above will generate in the `.out` folder, unless specified otherwise, an Alert Path graph showing all the forwarders of an alert message for all  simulation configurations found for the LA-25 scenario. Maximum 3 simulations per configuration, unless specifically specified by the `--maxfiles` parameters.

# Cluster Execution

If you need to process many CSV files, you can generate and submit jobs on the cluster. Here's how to do it:

1. **Set up the Conda environment** (Python) on the cluster if you haven’t already:
   Use the setup script:

   ```bash
   ../build-env/setup_conda_on_cluster.sh
   ```

2. **Generate job scripts** for the CSV files:

   ```bash
   ../scripts/createJobsAndMaps/generateDrawCoordsJobs.py
   ```

3. **Submit all jobs** using the following script:

   ```bash
   ../scheduledJobs/submitall.sh
   ```

> ⚠️ These graph files can be quite large. **Do not push them to the Git repository** or leave them on the cluster’s storage. Move them to your local disk when done.

You can use `rsync` for the transfer:

```bash
# Run this on your local machine
rsync -avz --progress --partial --append-verify --remove-source-files cluster:/storage/username/Vanets-ns3-fb/scripts/draw_coords/out/ /path/to/your/local/disk
```

> **Note**: `cluster` is just a proxy jump (SSH alias) defined in your SSH config.
See the [Cluster Access Setup](CLUSTER_ACCESS_SETUP.md) guide for details.