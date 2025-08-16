<!-- omit in toc -->
# Creating Maps and Jobs
- [1. Simplified Folder structure](#1-simplified-folder-structure)
- [2. Generating jobs](#2-generating-jobs)
  - [2.1. *generate\_maps\_and\_jobs.py*](#21-generate_maps_and_jobspy)
  - [2.2. *generate\_draw\_coords\_jobs.py*](#22-generate_draw_coords_jobspy)
- [3. Generating simple scenarios maps](#3-generating-simple-scenarios-maps)
- [4. Generating city maps](#4-generating-city-maps)
  - [4.1. Usage](#41-usage)
    - [4.1.1. _fixed\_positions.py_](#411-fixed_positionspy)
    - [4.1.2. _generate-sumo-files.sh_](#412-generate-sumo-filessh)
    - [4.1.3. _generate\_maps\_and\_jobs.py_](#413-generate_maps_and_jobspy)
    - [4.1.4. _polyconvert\_ench.py_](#414-polyconvert_enchpy)
    - [4.1.5. _sensors\_fixed\_positions.py_](#415-sensors_fixed_positionspy)

<!--- cSpell:words sumolib, --->

## 1. Simplified Folder structure

```plaintext
scripts/
├── create_maps_and_jobs
│   ├── generate_draw_coords_jobs
│   ├── generate_maps_and_jobs.py
│   ├── create_simple_scenarios/
│   ├── jobs_templates/
│   ├── fixed_positions.py
│   ├── polyconvert_ench.py
│   ├── generate-sumo-files.py
│   └── ...
│
```

## 2. Generating jobs
### 2.1. *generate_maps_and_jobs.py*
This script generates `.slurm` jobs for different simulation configurations to be submitted on the cluster or `.job` files containing just the command with all the parameters to be executed locally. See also the Getting Started [Generating slurm or job files](/docs/GETTING_STARTED.md#3-generating-slurm-or-job-files) section for more.

**Usage**:
<!--- cSpell:disable --->
```bash
usage: generate_maps_and_jobs.py [-h] [--genLossFile] [--printCoords] [--only-command] [--jobArray JOBARRAY]
                                 [--scenarios SCENARIOS] [--contentionWindows CONTENTIONWINDOWS]
                                 [--highBuildings HIGHBUILDINGS] [--drones DRONES] [--buildings BUILDINGS]
                                 [--errorRates ERRORRATES] [--forgedCoordRates FORGEDCOORDRATES]
                                 [--junctions JUNCTIONS] [--protocols PROTOCOLS] [--txRanges TXRANGES]
                                 [--neededTime NEEDEDTIME] [--ram RAM] [--jobsPath JOBSPATH]
                                 [--jobTemplate JOBTEMPLATE] [--jobTemplateOnlyCommand JOBTEMPLATEONLYCOMMAND]
                                 [mapPath] [vehicleDistance]

```
<!--- cSpell:enable --->
If executed without parameters it will generate `.slurm` files for the default scenarios, transmission ranges, etc. For the default values check the `--help` parameter.

### 2.2. *generate_draw_coords_jobs.py*
It generates `.slurm` jobs to execute [network visualization scripts](/docs/SIMULATIONS_OUTPUTS.md#2-network-visualization-tool) on the cluster. 

Usage:

```bash
usage: generate_draw_coords_jobs.py [-h] [--template TEMPLATE] [--scripts SCRIPTS] [--scenarios SCENARIOS]
                                    [--time TIME] [--additional-args [ADDITIONAL_ARGS]]
                                    [--output-dir OUTPUT_DIR]
```

## 3. Generating simple scenarios maps
These scripts generate mobility and polygon `xml` file foe simple scenarios like platoon, grids and cubes. 

## 4. Generating city maps 
> ⚠️  Most of these scripts have not been tested and might need refactoring.

Various bash and python scripts, mainly for OSM data manipulation using SUMO utilities and libs. 

* __fixed_positions.py__: use it to generate a trace file where vehicle are placed at a fixed distance
* __generate-sumo-files.sh__: generate a polygon file and a ns2mobility file from a OSM data file.
* __polyconvert_ench.py__: generate a polygon data file with heights.
* __generate_maps_and_jobs.py__: Other than creating NS3 simulation jobs to be submitted on the cluster, it could also generate sumo files by executing the `generate-sumo-files.sh`. This ability is currently disabled.

### 4.1. Usage
#### 4.1.1. _fixed_positions.py_
This script takes as input a netfile and (optionally) a distance and produces a trace file.

Example:

```
python fixed_positions.py -n map.net.xml -d 25 -o map.trace.xml
```

#### 4.1.2. _generate-sumo-files.sh_
Given a OSM data file produces two files needed to run simulations with ns-3.

```
bash generate-sumo-files.sh map.osm.xml
```
####  4.1.3. _generate_maps_and_jobs.py_
Same as `generate-sumo-files.sh`. Note that the maps generating ability of this script has been disabled as it needs testing:

```
    # Uncomment to generate sumoFiles again
    # os.system(sumo_file_generator)
```

Example:

```
./generate_maps_and_jobs.py map.osm.xml 25
```

#### 4.1.4. _polyconvert_ench.py_
Enhance a polygon data file with heights, given a osm data file and a poly file

```
python polyconvert_ench.py -i map.osm.xml -p map.poly.xml -o map.3Dpoly.xml
```

#### 4.1.5. _sensors_fixed_positions.py_
Generate positions for devices like sensors at each intersection at a give height.

```
python sensors_fixed_positions.py -n map.net.xml -o map.ns2mobility.xml -z 10
```

__N.B.__:
Some of the above python scripts use sumolib, so make sure it is installed before running them.


