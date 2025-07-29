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
cd build-env
singularity build --fakeroot singularity-ns3-image.sif singularity-ns3.def
```
Once you created your container on your PC you can transfer the ‘container.sif’ file on the submit host of the cluster for execution. You can do it by using `sftp` or `sshfs`. (more on the next sections)

**Build the image on the cluster front-end host:**

Alternatively you can use the remote build service for singularity (account required) available at the URL: [https://cloud.sylabs.io/builder](https://cloud.sylabs.io/builder). From the cluster front end machine:

```bash
# Build on cluster front-end host
cd build-env
singularity-remote-build singularity-ns3-image.sif singularity-ns3.def singularity-ns3.log
```


## 4. Working On the Cluster
On the Cluster you run simulations through Slurm. You do not have access to the cluster machines directly but you connect to some front-end servers (submit hosts) from which you can submit jobs and setup your github account. For detailed info about setting up the cluster access see the dedicated [Cluster Access Setup](CLUSTER_ACCESS_SETUP.md) section.

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

To generate jobs to submit you can use the `scripts/createJobsAndMaps/generateMapsAndJobsTemplate.py` script. For all the options:

```
scripts/createJobsAndMaps/generateMapsAndJobsTemplate.py --help
``` 

Example: 

```
cd scheduledJobs
../scripts/createJobsAndMaps/generateMapsAndJobsTemplate.py -s "LA-25" --buildings "1" --jobArray "1-3" --protocols "1,6"
```
This will create .job files for the scenario "LA-25" with buildings, for the protocols Fast-Broadcast and Roff, with all supported transmission ranges and it will save them in the folder `jobstemplate` in the root folder. You can use a different folder using the `--jobsPath` parameter. `--jobArray "1-3"` means that for each simulation there will be executed run 1,2,3. The run rumber is important as it garantees reproducibility. Each run, with same parameters, should always return same results. 

**Submitting slurm jobs**

You can submit the jobs on the cluster by using the command `sbatch` from inside the folder where the jobs are saved. Keep in mind the jobs will fail if there is not a `logs` folder next to the files that are going to be submitted.
To make things easier you can use the `scheduledJobs/submitall.sh` script that will take care of that and it will submit all jobs from the folder it is executed from.  

For every scenario with buildings you need a `*.losses` file that will be saved in the `maps\scenario\` folder. The losses file for each scenario needs to be generated only once, regardless of the transmission range used.

To generate a job that will create a `losses` file you can use the `--genLossFile` parameter. 

Example:

```
cd scheduledJobs
../scripts/createJobsAndMaps/generateMapsAndJobsTemplate.py -s "Grid-300" -p "1"  --txRanges "300" --genLossFile --jobArray "1-1"
```
## 5. Working Locally

Just the first time, or if you change profile(debug, optimized, etc.) or you apply substantial modifications:

```bash
./build-env/run_singularity_local.sh build
```

For subsequent code modifications it is enough to just run the simulation:

```
./build-env/run_singularity_local.sh run [simulation_command_file] [rng_run_value]
```

As the `run_singularity_local` script takes as input a `.job` file instead of a `slurm` one, you need to generate the job to run with the `--only-command` parameter passed to `generateMapsAndJobsTemplate.py`.

**Example:**

```
scripts/createJobsAndMaps/generateMapsAndJobsTemplate.py -s "Grid-300" --buildings "0" --protocols "2" --txRanges "300" --jobArray "1-1" --only-command

# Run the simulation
cd ../scheduledJobs
../build-env/run_singularity_local.sh run urban-Grid-300-highBuildings0-drones0-d25-cw-32-1024-b0-e0-j0-STATIC-100-300-.job
```

Locally you can also run  multiple simulations cuncurrently by processing all .jobs files from inside a folder:

```
build-env/batch2-simulations-with--singularity.sh --help

```
## Reproducibility
The simulations are reproducible.
Running a simulation with the same parameters and the same `rng_run` value will always produce *identical* results.

Before starting large‑scale production runs, first generate a few test simulations with different scenarios using the `generateMapsAndJobsTemplates` script and the `--jobArray 1-1` parameter.
Then, compare the outputs with the reference simulations in the simulation folder. The field `id` in the produced `csv` file contains the run number.
Existing files will not be overwritten, as each simulation filename includes a random string.


## Docker container and related scripts (Deprecated)
See the [Docker Setup](DOCKER_SETUP.md) section for detailed  instructions.
