from pathlib import Path
from backward_individual import manager
import argparse
import time

parser = argparse.ArgumentParser(description="Process simulation parameters.")

# Define arguments
parser.add_argument("--phases", type=int, default=2,
                    help="Run phase 2 => 2, else 1 (integer)")
parser.add_argument("--stepc_lim", type=int, default=3_000_000,
                    help="Step count limit (integer)")
parser.add_argument("--history", type=lambda x: x.lower() in ['true', '1', 'yes', 'y'],
                    default=False,
                    help="Enable history tracking for individual machines (boolean, e.g. True/False)")
parser.add_argument("--DEPTH", type=int, default=100,
                    help="Recursion or search depth (integer, default=100)")

# Parse arguments
args = parser.parse_args()

# Assign variables
phases = args.phases
stepc_lim = args.stepc_lim
history = args.history
DEPTH = args.DEPTH

machines_file = Path(__file__).parent / "machines.txt"
results_folder = Path(__file__).parent / "results"
results_file = results_folder / "results.txt"

# Ensure folder exists
results_folder.mkdir(parents=True, exist_ok=True)

# Check for existing path issues
if results_file.exists() and not results_file.is_file():
    raise Exception(f"{results_file} exists but is not a file!")

# Read machines
with machines_file.open("r") as f:
    machines = [line.strip() for line in f if line.strip()]

# Write results safely
with results_file.open("w") as f:
    for i, machine in enumerate(machines):
        result = manager(machine, phases, stepc_lim, history, DEPTH)
        f.write(f"{machine}: {result}\n")
        print(f"Processed {i+1} machines out of {len(machines)} total")
