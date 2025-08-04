#!/bin/bash
# Setup a conda environment on the cluster front-end to be able to 
# execute python script. This is needed only one time.

cd
which conda
conda create --name generate_graphs
conda init bash
grep -A 13 '>>> conda initialize' .bashrc >> .bash_profile
echo -e "Exiting the shell... \nPlease connect again and run:\n"
echo -e "conda activate generate_graphs"
echo -e "conda install numpy matplotlib"
exit