# My Project with ns-3 Submodule

This repository contains my Thesis project with modifications to ns-3 and various scripts. For the ns-3 folder I use a submodule that tracksthe official `ns-3` repo and my changes to it. It is also possible to rebase to a different ns-3 version.

## Clone the Repository

To clone this repository with the submodule, run the following commands:

```sh
# Clone the repository along with the submodule
git clone --recurse-submodules <repo-url>

# Or if you've already cloned the repository without the submodule, run this:
git submodule update --init --recursive

# When you pull, do it this way:
git pull --recurse-submodules
```


## Environment setup

You need a whole OS setup to be able to get the expected results. So to make this easy we can use docker. Running `docker compose` without services that need to stay up, it gets a little messy, because as soon as a service is executed it leaves orphans that need to be cleaned. So I used a script to automatize it:

### Commands

```sh
# Build
./dccompose.sh build

# Dirty build (without cleaning the build folder)
./dccompose.sh dirty-build

# Running a simulation with parameters
./dccompose.sh simulation file_with_command_and_parameters

# Getting a shell into the containers
../dccompose.sh shell
```

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
└── mobility/
    └── helper/
        ├── ns2-mobility-helper.cc
        └── ns2-mobility-helper.h
```
