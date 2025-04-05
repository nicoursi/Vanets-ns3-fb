# My Project with ns-3 Submodule

This repository contains my Thesis project with modifications to ns-3 and various scripts. For the ns-3 folder I use a submodule that tracksthe official `ns-3` repo and my changes to it. It is also possible to rebase to a different ns-3 version.

## Clone the Repository

To clone this repository with the submodule, run the following commands:

```sh
# Clone the repository along with the submodule
git clone --recurse-submodules <repo-url>

# Or if you've already cloned the repository without the submodule, run this:
git submodule update --init --recursive
```

## Libraries needed

- gmp
- libmpfr
- libboost-thread
- libboost-system
- libboost-filesystem
- libboost-serialization
- CGAL-4.13

CGAL is an old version and needs to be compliled and installed with make install. Alternatively linked in the `LINKFLAGS` in the wscript located in the obstacle module. [https://www.cgal.org/releases.html].
The other libraries can be installed by:
```sh
sudo apt-get install libgmp-dev libmpfr-dev libboost-thread-dev libboost-system-dev libboost-filesystem-dev libboost-serialization-dev
```

# Creating Maps
You create mobility and poly files, that will be placed in the `maps` folder, by using the scripts in `create simple scenario`

# NS-3 modifications

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
