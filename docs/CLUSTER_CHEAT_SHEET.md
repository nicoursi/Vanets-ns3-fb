# Useful commands executed on the front-end servers

## More general commands

Regular expression to search nodes in the ns2mobility.xml files (not cluster related)

```
\$node_\(\d+\)\s+set\s+X_\s+4900\b\s*\n\$node_\(\d+\)\s+set\s+Y_\s+4900\b

\$node_\(\d+\)\s+set\s+X_\s+1600\b\s*\n\$node_\(\d+\)\s+set\s+Y_\s+1600\b\s*\n\$node_\(\d+\)\s+set\s+Z_\s+1600\b
```

Paste selected text in terminal:

```
Shift+Insert
```

Execute the command later on the cluster (not slurm! The cluster machine will submit the slurm jobs later

```
mkdir -p logs && echo "cd $PWD && /home/nursino/storage/Vanets-ns3-fb/jobsTemplate/submitall.sh > logs/submitall.log 2>&1" | at now + 4 hours

mkdir -p logs && echo "cd $PWD && mv tosubmitlater/*STATIC* . && /home/nursino/storage/Vanets-ns3-fb/jobsTemplate/submitall.sh > logs/submitall.log 2>&1" | at now + 10 hours

mkdir -p logs && echo "cd $PWD && mv tosubmitlater/*ROFF* . && /home/nursino/storage/Vanets-ns3-fb/jobsTemplate/submitall.sh > logs/submitall.log 2>&1" | at now + 11 hours
```

To see the list of jobs scheduled with the `at` command

```
at -l
```

To see the queued command

```
at -c 5
```

To cancel a queued command

```
atrm 5 #5 is just an example
```

Search just for the line and print it (to see how much time a simulation took):

```
grep '^Whole simulation Elapsed wall-clock time:' *.out
```

Print on screen all lines of csvfiles in current directory

```
(head -n 1 *.csv | head -n 1) && tail -n +2 -q *.csv
head -n 1 $(ls *.csv | head -n 1) && tail -n +2 -q *.csv # con intestazione

```
# Slurm commands

Show queue status:

```
squeue
```

Show cluster queues and status:

```
sinfo -l -v
```

Show nodes (computing machines):

```
scontrol show node
```

Cancel slurm jobs. Either the whole array (######) or a single element (######_##)

```
scancel jobid
```

Change time limit

```
scontrol update JobId=<job_id> TimeLimit=15:30:00
```

Show a particular node:

```
scontrol show node <nodename>
```

Submit a job:

```
sbatch file.slurm
```

Command for building the ns3 project. You can use the `run_singularity_cluster-host.sh build` instead

```
singularity exec --bind /home/nursino/storage/Vanets-ns3-fb/ns-3:/home/nursino/storage/Vanets-ns3-fb/ns-3 $SIF_IMAGE bash -c "cd $NS3_DIR &&  ./waf configure && ./waf build
```
