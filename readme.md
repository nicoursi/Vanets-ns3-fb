# My Project with ns-3 Submodule

This repository contains my Thesis project with modifications to ns-3 and various scripts. For the ns-3 folder I use a submodule that tracksthe official `ns-3` repo and my changes to it. It is also possible to rebase to a different ns-3 version.

## Clone the Repository

To clone this repository with the submodule, run the following commands:
Clone the repository along with the submodule:
```sh
git clone --recurse-submodules <repo-url>
```

Or if you've already cloned the repository without the submodule, run this:
```sh
git submodule update --init --recursive
```

When you pull, outside of ns-3, do it this way:
```sh
git pull --recurse-submodules
```

When you made modifications to the ns-3 folder, after pulling and pushing the modifications inside the submodule ns-3 folder, you also need to commit it in the main repo.
Something like this:
```sh
cd ns-3
git add .
git commit -m 'my last modifications'
git pull
git push
cd ..
git add ns-3
git commit -m "my last modifications to the ns-3 master branch"
git push
```


## Environment setup

You need a whole OS setup to be able to get the expected results. So to make this easy we can use docker. Running `docker compose` without services that need to stay up gets a little messy, because as soon as a service is executed it leaves orphans behind that need to be cleaned. So I used a script to automate it:

### Commands

To build the image the first time:
```sh
COMPOSE_BAKE=true docker compose build
```

To build the ns3 project:
```sh
docker compose run --rm build
```

To build without cleaning the build folder:
```sh
docker compose run --rm dirty-build
```

To get a shell into the docker image, just for troubleshooting:
```sh
docker compose run --rm shell
```

To run the simulation (and automatically build modifications to existing files). For this command you need to fill the `$SIMULATION_CMD` environment variable with the exact command and parameters. You can put this variable in the `.env` file or provide it at runtime.
```
SIMULATION_CMD="command  with parameters" "docker compose run --rm simulation
```

To make running simulations easier and more automated you can use the following script from within the ns-3 folder:
```sh
../runsimulations.sh ../jobsTemplate/script-to-run/urban-Grid-300-highBuildings0-drones0-d25-cw-32-1024-b0-e0-j0-Fast-Broadcast-500-.job 14
```
In the example above, the simulation command and parameters will be executed 14 times

# Creating Maps

You create mobility and poly files, that will be placed in the `maps` folder, by using the scripts in `create simple scenario`

# NS-3 modifications

```plaintext
src/
├── vanets-utils/
│   ├── Edge.cc
│   └── Edge.h
├── roff/
├── fast-broadcast/
├── obstacle/
├── mobility/
│   └── helper/
│       ├── ns2-mobility-helper.cc
│       └── ns2-mobility-helper.h
scratch/
├── fb-vanet-urban/
└── roff-test/
```
