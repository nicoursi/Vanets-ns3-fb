## Getting Started

## 1. Clone the Repository

To clone with the NS-3 submodule:

```bash
git clone --recurse-submodules <repo-url>
```

If you've already cloned without submodules:

```bash
git submodule update --init --recursive
```

## 2. Working with the NS-3 git Submodule 

When pulling updates:

```bash
git pull --recurse-submodules
```

**Workflow for NS-3 modifications:**
When you work on the ns-3 folder I advice to always checkout a branch before applying modifications. Do not clone and just `cd ns-3`. Checkout a branch first, apply modifications, pull and push! After pushing you also need to commit it in the main repo (Vanets-ns3-fb).

Example:

```bash
# Work in the ns-3 directory
cd ns-3
git checkout master

# Make your changes, then commit
git add .
git commit -m "Description of NS-3 modifications"
git pull
git push

# Update the main repository to track the new commit
cd ..
git add ns-3
git commit -m "Updated NS-3 submodule with latest modifications"
git push
```



## 3 Building the Singularity Container image


**Build the image locally:**

```bash
singularity build --fakeroot singularity-ns3-image.sif singularity-ns3.def
```

**Build the image on the cluster frontend:**

```bash
# Build on cluster frontend
singularity-remote-build singularity-ns3-image.sif singularity-ns3.def singularity-ns3.log
```
This requires an account. Alternatively you can build the image locally and upload it to the cluster through a cloud service.

## 4. Working On the Cluster
On the Cluster you run simulations through slurm. You do not have access to the cluster machines directly but you connect to some frontend servers from which you can submit jobs and setup your github account.

In order to run simulations you need to build the NS-3 project first, then create slurm jobs to be submitted. 

### Building the project
On the cluster you need to build the NS3 project every time you apply modifications to the code (NS-3 folder).
The first time you build, or if you have created new files or modules (make sure you already build the container image):

```
run_singularity_cluster-host.sh build

```

If you applied small modification to the code:

```
run_singularity_cluster-host.sh dirty-build

```
### Generating and submitting jobs
**Generating slurm jobs**

To generate jobs to submit you can use the `scripts/generateMapsAndJobsTemplate.py` script. For all the options:

```
scripts/generateMapsAndJobsTemplate.py --help
``` 

Example: 

```
../scripts/generateMapsAndJobsTemplate.py -s "LA-25" --buildings "1" --jobArray "1-3" --printCoords --protocols "1,6"
```
It will create .job files for the scenario "LA-25" with buildings, for the protocols Fast-Broadcast and Roff, with all supported transmission ranges and it will save them in the folder `jobstemplate` in the root folder. You can use a different folder using the `--jobsPath` parameter. `--jobArray "1-3"` means that for each simulation there will be executed run 1,2,3. The run rumber is important as it garantees reproducibility. Each run, with same parameters, should always return same results. 

**Submitting slurm jobs**

You can submit the jobs to the cluster by using the command `sbatch` from inside the folder where the jobs are saved. Keep in mind the jobs will fail if there is not a `logs` folder next to the files that are going to be submitted.
To make things easier you can use the `submitall.sh` script that will take care of that and it will submit all jobs from the folder it is executed from.  

For every scenario with buildings you need a `*.losses` file that will be saved in the `maps\scenario\` folder. The losses file for each scenario needs to be generated only once, regardless of the transmission range used.

To generate a job that will create a `losses` file you can use the `--genLossFile` parameter. 

Example:

```
../scripts/generateMapsAndJobsTemplate.py -s "Grid-300" -p "1"  --txRanges "300" --genLossFile --jobArray "1-1"
```
## 5. Working Locally
If you are applying modification to the NS-3 code it is easier to test locally. The NS-3 building tool, `waf`, allows you to run the code you are working on by automatically building just the modified files. 

Just the first time, or if you change profile(debug, optimized, etc.) or you apply substantial modifications:

```bash
./run_singularity_local.sh build
```

For subsequent code modifications it is enough to just run the simulation:

```
./run_singularity_local.sh run [simulation_command_file] [rng_run_value]
```

As the `run_singularity_local` script takes as input a `.job` file instead of a `slurm` one, you need to generate the job to run with the `--only-command` parameter passed to `generateMapsAndJobsTemplate.py`.

**Example:**

```
./generateMapsAndJobsTemplate.py -s "Grid-300" --buildings "0" --protocols "2" --txRanges "300" --jobArray "1-1" --only-command

# Run the simulation
cd ../jobsTemplate
../run_singularity_local.sh run urban-Grid-300-highBuildings0-drones0-d25-cw-32-1024-b0-e0-j0-STATIC-100-300-.job
```

Locally you can also run  multiple simulations cuncurrently by processing all .jobs files from inside a folder:

```
batch2-simulations-with--singularity.sh --help

```

## Docker container and related scripts (Deprecated)
See the [Docker Setup](DOCKER_SETUP.md) section for detailed  instructions.
