<!-- omit in toc -->
# Getting Started
- [1. Repository Setup](#1-repository-setup)
  - [1.1. Clone the Repository](#11-clone-the-repository)
  - [1.2. Working with the NS-3 Git Submodule](#12-working-with-the-ns-3-git-submodule)
- [2. Container Setup](#2-container-setup)
  - [2.1. Building the Singularity Container Image](#21-building-the-singularity-container-image)
    - [2.1.1. Build the image locally](#211-build-the-image-locally)
    - [2.1.2. Build the image on the cluster front-end host](#212-build-the-image-on-the-cluster-front-end-host)
- [3. Generating .slurm or .job files](#3-generating-slurm-or-job-files)
  - [3.1. Losses files](#31-losses-files)
- [4. Working Locally](#4-working-locally)
  - [4.1. Building and Running Simulations](#41-building-and-running-simulations)
    - [4.1.1. Full build](#411-full-build)
    - [4.1.2. Dirty build](#412-dirty-build)
    - [4.1.3. Running simulations](#413-running-simulations)
    - [4.1.4. Logging configuration](#414-logging-configuration)
  - [4.2. Batch Processing](#42-batch-processing)
  - [4.3. Development Environment Setup (VSCodium)](#43-development-environment-setup-vscodium)
- [5. Working on the Cluster](#5-working-on-the-cluster)
  - [5.1. Building the Project](#51-building-the-project)
  - [5.2. Submitting slurm jobs](#52-submitting-slurm-jobs)
- [6. Important Notes](#6-important-notes)
  - [6.1. Reproducibility](#61-reproducibility)
  - [6.2. Legacy Information](#62-legacy-information)

<!--- cSpell:words fakeroot,dumpmachine, libboost, submitall,-->

## 1. Repository Setup

### 1.1. Clone the Repository

To clone with the NS-3 submodule:

```bash
git clone --recurse-submodules <repo-url>
```

If you've already cloned without submodules:

```bash
git submodule update --init --recursive
```

### 1.2. Working with the NS-3 Git Submodule 

When pulling updates:

```bash
git pull --recurse-submodules
```

**Workflow for NS-3 modifications:**

When you work on the ns-3 folder I advise to always checkout a branch before applying modifications. Do not clone and just `cd ns-3`. Checkout a branch first, apply modifications, pull and push! After pushing you also need to commit it in the main repo (Vanets-ns3-fb).

**Example:**

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

## 2. Container Setup

### 2.1. Building the Singularity Container Image

#### 2.1.1. Build the image locally

Install [Singularity](https://sylabs.io/docs/) on your local system if you haven't already. Then build the image:

```bash
cd build_env/container
singularity build --fakeroot singularity-ns3-image.sif singularity-ns3.def
```

Once you created your container on your PC you can transfer the `singularity-ns3-image.sif` file on the submit host of the cluster for execution (make sure you copy it in the `build_env/container` folder). You can do it by using `sftp` or `sshfs`. (More in the [Working on the Cluster](#4-working-on-the-cluster) section below.)

#### 2.1.2. Build the image on the cluster front-end host

Alternatively you can use the remote build service for singularity (account required) available at the URL: [https://cloud.sylabs.io/builder](https://cloud.sylabs.io/builder).  
From the cluster front end machine:

```bash
# Build on cluster front-end host
cd build_env/container
singularity-remote-build singularity-ns3-image.sif singularity-ns3.def singularity-ns3.log
```

> **Note** Do not change the name of the **`.sif`** image!

## 3. Generating .slurm or .job files

`.slurm` files are bash scripts to be submitted to the cluster for running the NS-3 simulations. `.job` files, contain just the simulation command, and are used locally to run the simulations.

To generate both, `.slurm` or `.jobs` files,  you can use the `generate_maps_and_jobs` script. For all the options:

```bash
scripts/create_maps_and_jobs/generate_maps_and_jobs.py --help
``` 

**Example:** 

```bash
cd scheduled_jobs
# For local execution (.job files)
../scripts/create_maps_and_jobs/generate_maps_and_jobs.py -s "LA-25" --buildings "1" --jobArray "1-3" --protocols "1,6" --only-command

# For cluster execution (.slurm files) 
../scripts/create_maps_and_jobs/generate_maps_and_jobs.py -s "LA-25" --buildings "1" --jobArray "1-3" --protocols "1,6"
```

This will create jobs for the scenario "LA-25" with *buildings*, using the protocols *Fast-Broadcast* and *Roff*, across all supported transmission ranges. The files will be saved in the current folder.

It is recommended to run this in the `scheduled_jobs` directory or one of its subdirectories. You can specify a different target folder using the `--jobsPath` parameter.

The `--jobArray "1-3"` option means that each `slurm` file, once submitted on the cluster,  will be executed three times with **RNG** (Random Number Generator) run numbers 1, 2, and 3. The run number is important because it ensures reproducibility — each run with the same parameters should always produce the same results. See also the [reproducibility](#61-reproducibility) note.

### 3.1. Losses files

For every scenario with buildings, as the one in the example above, you need a `*.losses` file that will be saved in the `maps/scenario/` folder. The losses file for each scenario needs to be generated only once, regardless of the transmission range or protocol used.

To generate a job that will create a `losses` file you can use the `--genLossFile` parameter. 

**Example:**

```bash
cd scheduled_jobs
# create a loss file for the LA-25 scenario
../scripts/create_maps_and_jobs/generate_maps_and_jobs.py -s "La-25" --genLossFile
```

**⚠️ Important:** Losses file generation is extremely time-consuming - city scenarios (like Padova, LA) can take up to **two full days** to complete. You cannot run any simulations with buildings for that scenario until the losses file generation is finished, otherwise you will end up with inconsistent simulations and possibly corrupted losses file.

## 4. Working Locally

### 4.1. Building and Running Simulations

The `singularity_ns3_runner.sh` script automatically builds in **debug mode** locally and **release mode** on cluster hosts. Release mode runs faster but without logging capability.

#### 4.1.1. Full build

This builds the whole project. This is usually needed just the first time you build, if you change building profile (e.g from debug to release)  or if there is something wrong during compilation and you need a clean build.

```bash
# Cleans build folder and builds from scratch
build_env/singularity_ns3_runner.sh build [debug|release|optimized]

# Example
./build_env/singularity_ns3_runner.sh build
```

#### 4.1.2. Dirty build

If you just want to compile without running any simulation, you can simply dirty-build, which will configure and build only the modified files:

```bash
./build_env/singularity_ns3_runner.sh dirty-build
```

#### 4.1.3. Running simulations

After modifying the code, you don't need a full or a dirty build — the script will auto-compile your changes when running locally (not on the cluster).

```bash
# no need to build again, it will be held by the script, just run!
./build_env/singularity_ns3_runner.sh run <simulation_command_file.job> [rng_run_value]
```

For generating the `<simulation_command_file.job>` see the [Generating and submitting jobs](#3-generating-slurm-or-job-files) section. Since `singularity_ns3_runner` expects `.job` files instead of `.slurm`, generate them with the `--only-command` option:

**Example:**

```bash
cd scheduled_jobs
# Generate the simulation command to execute
../scripts/create_maps_and_jobs/generate_maps_and_jobs.py -s "Grid-300" --buildings "0" --protocols "2" --txRanges "300" --jobArray "1" --only-command

# Run the simulation
../build_env/singularity_ns3_runner.sh run urban-Grid-300-highBuildings0-drones0-d25-cw-32-1024-b0-e0-j0-STATIC-100-300-.job
```

#### 4.1.4. Logging configuration

By default, logging is set to `warn` level. You can override it by using the `$LOG_LEVEL` environment variable:

```bash
# usage
LOG_LEVEL=[error|warn|info|debug|function|logic] ../build_env/singularity_ns3_runner.sh run <simulation_command_file> [rng_run_value]

# example
LOG_LEVEL='error' ../build_env/singularity_ns3_runner.sh run urban-Grid-300-highBuildings0-drones0-d25-cw-32-1024-b0-e0-j0-STATIC-100-300-.job

```

### 4.2. Batch Processing

Locally you can also run multiple simulations concurrently by processing all `.jobs` files from inside a folder:

```bash
cd scheduled_jobs
build_env/batch2_simulations_with_singularity.sh # for help
```
This script uses parallel processing to run up to 4 simulations concurrently. Before starting, it will prompt you to run a dirty build. If you have made code modifications, you should answer yes to avoid build conflicts—otherwise, all parallel processes will attempt to build simultaneously, potentially resulting in corrupted or unreliable binaries.

### 4.3. Development Environment Setup (VSCodium)

To enable proper syntax highlighting and IntelliSense for the NS-3.26 project in VSCodium:

1. **Install the `clangd` extension**:
   ```bash
   codium --install-extension llvm-vs-code-extensions.vscode-clangd
   ```

2. **Build the project locally** at least once, so that a `compile_commands.json` will be automatically saved in the `./ns-3/build` folder.

3. **Open the project folder** with VSCodium and wait until the caching and indexing is done.

4. **Test and configure `clangd`**
   
   Open a `.cc` or `.h` file and see if you get any weird errors. If so, probably clangd cannot find the C++ includes or some other libraries and you need to provide them by updating the `.clangd` file. Here's a reference one that works on my system:

      ```yaml
      CompileFlags:
          CompilationDatabase: ./ns-3/build
          Add:
              - --gcc-toolchain=/usr/lib/gcc/x86_64-linux-gnu/11
              - -I/usr/include/c++/11
              - -I/usr/include/c++/11/x86_64-linux-gnu
              - -I/usr/include/x86_64-linux-gnu/c++/11
              - -I/usr/include/x86_64-linux-gnu
              - -I/usr/include
              - -I/usr/local/include
      ```

      To find the right paths for your system:

      ```bash
      gcc --version                                    # Check GCC version
      find /usr -name "iostream" 2>/dev/null | head -5 # Find C++ headers
      gcc -dumpmachine                                 # Check architecture
      ls /usr/include/c++/                             # List available C++ versions
      ```

      After updating the `.clangd` file, delete the `.cache` (from `./ns-3/build/`) folder and restart VSCodium.  
      
      After indexing is completed, you should see no red squiggles under `#include <iostream>` and you should be able to get autocomplete for `std::`. If you get other imports that are not recognized you might need to install some missing libraries. For example you might need these ones:

      ```bash
      sudo apt install build-essential libboost-all-dev
      # For ns-3 specifically:
      sudo apt install libgtk-3-dev libxml2-dev
      ```

      If you modify the `.clangd` as suggested above, please prevent git from tracking it as it contains system specific configurations that should not be pushed:

      ```bash
       git update-index --assume-unchanged .clangd
       # To revert: git update-index --no-assume-unchanged .clangd
      ```

## 5. Working on the Cluster

On the Cluster you run simulations through Slurm. You do not have access to the cluster machines directly but you connect to some front-end servers (submit hosts) from which you can submit jobs and setup your github account. For detailed info about setting up the cluster access see the dedicated [Cluster Access Setup](CLUSTER_ACCESS_SETUP.md) section.

In order to run simulations you need to build the NS-3 project first, then create slurm jobs to be submitted. 

### 5.1. Building the Project

On the cluster you need to build the NS3 project **every time** you apply modifications to the code (NS-3 folder).

The first time you build, or if you have changed the build profile (make sure you have already built the container image — see [Container Setup](#2-container-setup)):

```bash
# Builds NS-3 project in debug mode (local) or release mode (cluster)
singularity_ns3_runner.sh build
```

For subsequent modifications to the code:

```bash
singularity_ns3_runner.sh dirty-build
```

### 5.2. Submitting slurm jobs

After having generated the `.slurm` files as explained in [generating maps and jobs](#3-generating-slurm-or-job-files), you can submit them on the cluster by using the command `sbatch` from inside the folder where the jobs are saved. Keep in mind the slurm jobs will fail if there is not a `logs` folder next to the files that are going to be submitted.

To make things easier you can use the `scheduled_jobs/submitall.sh` script that will take care of that and it will submit all jobs from the folder it is executed from. 

You can also schedule job submissions, to be queued later, by using the `scheduled_jobs/schedule_slurm_jobs.sh` script.

**Example:**

```bash
cd scheduled_jobs
../scripts/create_maps_and_jobs/generate_maps_and_jobs.py -s "Grid-300" --buildings "0" --protocols "2" --txRanges "300" --jobArray "1"

# Submit all the .slurm jobs in the current folder
./submitall.sh

# Schedule for submission of all the .slurm jobs in 4 hours
./schedule_slurm_jobs.sh -t 4h
```

## 6. Important Notes

### 6.1. Reproducibility

The simulations are reproducible. Running a simulation with the same parameters and the same `rng_run` (Random Number Generator) value will always produce *identical* results.

Before starting large‑scale production runs, first generate a few test simulations with different scenarios using the `generate_maps_and_jobs` script and the `--jobArray 1` parameter (or any other run number you want to check). Then, compare the outputs with the reference simulations in the simulation folder.

The field `Run id` in the produced `csv` file contains the rng run number. Existing files will not be overwritten, as each simulation filename includes a random string.

### 6.2. Legacy Information

For information about Docker container and related scripts (deprecated), see the [Docker Setup](DOCKER_SETUP.md) section for detailed instructions.