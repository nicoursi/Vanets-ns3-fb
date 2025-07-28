# Docker container and related scripts (Deprecated)
This project initially used Docker for local development and testing, but was later ported to Singularity for deployment on HPC clusters.

Docker remains available but it is no longer mantained. All  docker scripts have been moved to the `build-env` folder without testing as they are deprecated. In case you need them, please test or move them back to the project's root folder. There is high chance they still work.

## Docker Commands 

**Initial setup** (build the Docker image):

```bash
COMPOSE_BAKE=true docker compose build
```

**Build NS-3 project:**

```bash
docker compose run --rm build
```

**Build without cleaning** (faster incremental builds):

```bash
docker compose run --rm dirty-build
```

**Get a shell** (for debugging):

```bash
docker compose run --rm shell
```

**Run simulations:**

```bash
SIMULATION_CMD="your-command-with-parameters" docker compose run --rm simulation
```

> **Tip:** You can set the `SIMULATION_CMD` environment variable in a `.env` file for convenience.

Or you can use the script:

```bash
# From within the ns-3 directory
../build-env/singlerun-docker.sh ../scheduledJobs/urban-Grid-300-highBuildings0-drones0-d25-cw-32-1024-b0-e0-j0-Fast-Broadcast-500-.job 14
```

This example runs the specified simulation with run 14 (executing the same run multiple times returns same results).

**Automated Simulation Runs**

For automated simulations you can use `../build-env/batch1-simulations-with-docker.sh`. Make sure you `cd ns-3` before running. Check `--help` for accurate instructions.

> **Note:** While Docker commands remain functional, Singularity is now the recommended approach for both local development and cluster deployment due to its universal compatibility.
