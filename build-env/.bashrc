cd ~/storage/Vanets-ns3-fb/
export TZ=/usr/share/zoneinfo/Europe/Rome
alias printcsv='head -n 1 $(ls *.csv | head -n 1) && tail -n +2 -q *.csv'
alias squeue-long='squeue -h -u nursino -o "%18i %9P %j %8u %10M %T"'
alias tesi='cd ~/storage/Vanets-ns3-fb/'
alias simulations='cd ~/storage/Vanets-ns3-fb/simulations'
alias scheduledjobs='cd ~/storage/Vanets-ns3-fb/scheduledJobs'
alias generateMapsAndJobsTemplate='~/storage/Vanets-ns3-fb/scripts/createJobsAndMaps/generateMapsAndJobsTemplate.py'
