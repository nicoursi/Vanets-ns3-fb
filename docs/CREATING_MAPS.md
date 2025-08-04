# Creating Maps

## Simplified Forlder structure

```plaintext
scripts/
├── create_maps_and_jobs
│   ├── create_simple_scenarios/
│   ├── jobs_templates/
│   ├── generate_maps_and_jobs.py
│   ├── fixed_positions.py
│   ├── polyconvert_ench.py
│   ├── generate-sumo-files.py
│   └── ...
│
```

## Generating city maps 
> ⚠️  Most of these scripts have not been tested and might need refactoring.

Various bash and python scripts, mainly for OSM data manipulation using SUMO utilities and libs. 

* _fixed_positions.py_: use it to generate a trace file where vehicle are placed at a fixed distance
* _generate-sumo-files.sh_: generate a polygon file and a ns2mobility file from a OSM data file.
* _polyconvert_ench.py_: generate a polygon data file with heights.
* _generate_maps_and_jobs.py_*: Other than creating NS3 simulation jobs to be submitted on the cluster, it generates sumo files by executing the generate-sumo-files.sh`. 

### Usage
#### _fixed_positions.py_
This script takes as input a netfile and (optionally) a distance and produces a trace file.

Example:

```
python fixed_positions.py -n map.net.xml -d 25 -o map.trace.xml
```

#### _generate-sumo-files.sh_
Given a OSM data file produces two files needed to run simulations with ns-3.

```
bash generate-sumo-files.sh map.osm.xml
```
####  _generate_maps_and_jobs.py_
Same as `generate-sumo-files.sh`. Note that the maps generating ability of this script has been disabled as it needs testing:

```
    # Uncomment to generate sumoFiles again
    # os.system(sumo_file_generator)
```

Example:

```
./generate_maps_and_jobs.py map.osm.xml 25
```

#### _polyconvert_ench.py_
Enhance a polygon data file with heights, given a osm data file and a poly file

```
python polyconvert_ench.py -i map.osm.xml -p map.poly.xml -o map.3Dpoly.xml
```

#### _sensors_fixed_positions.py_
Generate positions for devices like sensors at each intersection at a give height.

```
python sensors_fixed_positions.py -n map.net.xml -o map.ns2mobility.xml -z 10
```

__N.B.__:
Some of the above python scripts use sumolib, so make sure it is installed before running them.

## Generating simple scenarios maps
These scripts create scenarios like platoon, grids and cubes. 