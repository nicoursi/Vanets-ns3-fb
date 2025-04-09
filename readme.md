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

# When you pull, outside of ns-3, do it this way:
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

To build
```sh
./dccompose.sh build
```
Dirty building (without cleaning the build folder)
```sh
./dccompose.sh dirty-build
```

Running a simulation with parameters
```sh
./dccompose.sh simulation file_with_command_and_parameters
```

Getting a shell into the containers
```sh
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
