import numpy as np
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("num_robots", type=int, help="Number of robots to be included in the model")
parser.add_argument("num_tasks", type=int, help="Number of tasks to be included in the model")
parser.add_argument("grid_size", type=int, help="Size of grid axis")
parser.add_argument("output_name", type=str, help="Filename for output")
parser.add_argument("init_file", nargs = "?", const = None, type=str, help="Optional: file containing an init/endinit block with which to initialise variables")

args = parser.parse_args();
