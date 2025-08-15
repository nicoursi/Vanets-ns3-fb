<!-- omit in toc -->
# Useful commands executed on the front-end servers
- [1. More general commands](#1-more-general-commands)
  - [1.1. Regular expression to search nodes in the ns2mobility.xml files (not cluster related)](#11-regular-expression-to-search-nodes-in-the-ns2mobilityxml-files-not-cluster-related)
  - [1.2. Paste selected text in terminal:](#12-paste-selected-text-in-terminal)
  - [1.3. Execute the command later on the cluster (not slurm!](#13-execute-the-command-later-on-the-cluster-not-slurm)
  - [1.4. Search just for the line and print it (to see how much time a simulation took):](#14-search-just-for-the-line-and-print-it-to-see-how-much-time-a-simulation-took)
  - [1.5. Print on screen all lines of csv files in current directory](#15-print-on-screen-all-lines-of-csv-files-in-current-directory)
  - [1.6. Git clean recursively just one folder](#16-git-clean-recursively-just-one-folder)
- [2. Slurm commands](#2-slurm-commands)
  - [2.1. Show queue status:](#21-show-queue-status)
  - [2.2. Show cluster queues and status:](#22-show-cluster-queues-and-status)
  - [2.3. Show nodes (computing machines):](#23-show-nodes-computing-machines)
  - [2.4. Cancel slurm jobs.](#24-cancel-slurm-jobs)
  - [2.5. Change time limit of queued job (not running)](#25-change-time-limit-of-queued-job-not-running)
  - [2.6. Show a particular node:](#26-show-a-particular-node)
  - [2.7. Submit a job:](#27-submit-a-job)
  - [2.8. Move a folder from the cluster to your local machine. Add -n for dry run (just test no transfer)](#28-move-a-folder-from-the-cluster-to-your-local-machine-add--n-for-dry-run-just-test-no-transfer)

<!--- cSpell:words submitall, tosubmitlater, atrm, squeue, scontrol, scancel, sinfo --->
## 1. More general commands

### 1.1. Regular expression to search nodes in the ns2mobility.xml files (not cluster related)

```regex
\$node_\(\d+\)\s+set\s+X_\s+4900\b\s*\n\$node_\(\d+\)\s+set\s+Y_\s+4900\b

\$node_\(\d+\)\s+set\s+X_\s+1600\b\s*\n\$node_\(\d+\)\s+set\s+Y_\s+1600\b\s*\n\$node_\(\d+\)\s+set\s+Z_\s+1600\b
```

### 1.2. Paste selected text in terminal:

```
Shift+Insert
```

### 1.3. Execute the command later on the cluster (not slurm! 
The cluster machine will submit the slurm jobs later at the chosen time

```bash
# submit all the slurm jobs found in the current folder in 4 hours
mkdir -p logs && echo "cd $PWD && /home/nursino/storage/Vanets-ns3-fb/scheduled_jobs/submitall.sh > logs/submitall.log 2>&1" | at now + 4 hours

# move the jobs you want to submit (*STATIC*) and them submit them all in 10 hours
mkdir -p logs && echo "cd $PWD && mv tosubmitlater/*STATIC* . && /home/nursino/storage/Vanets-ns3-fb/scheduled_jobs/submitall.sh > logs/submitall.log 2>&1" | at now + 10 hours

# move the jobs you want to submit (*ROFF*) and them submit them all in 11 hours
mkdir -p logs && echo "cd $PWD && mv tosubmitlater/*ROFF* . && /home/nursino/storage/Vanets-ns3-fb/scheduled_jobs/submitall.sh > logs/submitall.log 2>&1" | at now + 11 hours
```

To see the list of jobs scheduled with the `at` command

```bash
at -l
```

To see the queued command

```bash
at -c 5
```

To cancel a queued command

```bash
atrm 5 #5 is just an example
```

### 1.4. Search just for the line and print it (to see how much time a simulation took):

```bash
grep '^Whole simulation Elapsed wall-clock time:' *.out
```

### 1.5. Print on screen all lines of csv files in current directory

```bash
(head -n 1 *.csv | head -n 1) && tail -n +2 -q *.csv
head -n 1 $(ls *.csv | head -n 1) && tail -n +2 -q *.csv # with header

```
### 1.6. Git clean recursively just one folder

```bash
# Remove the --dry-run if it is the expected result
find . -type d -name "ROFF" -exec git clean -fd --dry-run {} \;

# with escaping characters
find . -type d -name "cw\[16-128\]" -exec git clean -fd --dry-run {} \;
```

## 2. Slurm commands

### 2.1. Show queue status:

```bash
squeue
```

### 2.2. Show cluster queues and status:

```bash
sinfo -l -v
```

### 2.3. Show nodes (computing machines):

```bash
scontrol show node
```

### 2.4. Cancel slurm jobs. 
As `job_id` you can use either the whole array (######) or a single element (######_##)

```bash
scancel job_id
```

### 2.5. Change time limit of queued job (not running)

```bash
scontrol update JobId=<job_id> TimeLimit=15:30:00
```

### 2.6. Show a particular node:

```bash
scontrol show node <node_name>
```

### 2.7. Submit a job:

```bash
sbatch file.slurm
```

### 2.8. Move a folder from the cluster to your local machine. Add -n for dry run (just test no transfer)

```bash
rsync -avz --progress --partial --append-verify --remove-source-files cluster:/storage/nursino/Vanets-ns3-fb/scripts/draw_coords/out/ /media/Dati-2/tesi/network-visual/from-cluster/
```

Then, after you’ve confirmed files transferred and source files were removed, clean up empty directories with:

```bash
ssh cluster 'find /storage/nursino/Vanets-ns3-fb/scripts/draw_coords/out -type d -empty -delete'
```