# jobs_utils.py
import os
import sys


def find_project_root(start_path=None):
    """Find the project root by walking up from a starting path.

    Walk up from `start_path` (or the current working directory) until a directory
    containing both 'ns-3' and 'simulations' subdirectories is found.

    Returns the absolute path if found, otherwise raises RuntimeError.
    """
    current_dir = os.getcwd() if start_path is None else os.path.abspath(start_path)

    while True:
        ns3_path = os.path.join(current_dir, "ns-3")
        sim_path = os.path.join(current_dir, "simulations")

        if os.path.isdir(ns3_path) and os.path.isdir(sim_path):
            return current_dir

        parent = os.path.dirname(current_dir)
        if parent == current_dir:  # reached filesystem root
            break
        current_dir = parent

    msg = f"Could not find project root (looking for ns-3/ and simulations/)\nSearched from: {os.getcwd()}"
    raise RuntimeError(
        msg,
    )


# For testing standalone:
if __name__ == "__main__":
    try:
        root = find_project_root()
        print(f"Project root: {root}")
    except RuntimeError as e:
        print(str(e))
        sys.exit(1)
