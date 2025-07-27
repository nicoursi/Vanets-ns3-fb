#!/bin/bash
cd
which conda
conda create --name generate_graphs
conda init bash
grep -A 13 '>>> conda initialize' .bashrc >> .bash_profile
echo -e "exit the shell and enter again \n"
echo -e "Then just run:\n'conda activate generate_graphs'"
echo -e "conda install numpy matplotlib"
exit
