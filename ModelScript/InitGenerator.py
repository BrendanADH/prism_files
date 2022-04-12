import numpy as np
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("num_robots", type=int, help="Number of robots to be included in the model")
parser.add_argument("num_tasks", type=int, help="Number of tasks to be included in the model")
parser.add_argument("grid_size", type=int, help="Size of grid axis")
parser.add_argument("output_name", type=str, help="Filename for output")

args = parser.parse_args();

filename = args.output_name
grid_size = args.grid_size

try:
    f = open(filename, "x")
except (FileExistsError):
    chosen = False
    while(chosen == False):
        ans = input(f"File \'{filename}\' already exists, overwrite? y/n\n")
        if(ans == "Y" or ans == "y"):
            chosen = True;
            print(f"Overwriting \'{filename}\'...")
            f = open(args.output_name, "w")
        elif(ans == "N" or ans == "n"):
            chosen = True 
            print("Exiting.")
            exit()

output = "init\n\n"

for i in range(0,args.num_robots):
	output += f"x{i} = {np.random.randint(1,grid_size)} &\n"
	output += f"y{i} = {np.random.randint(1,grid_size)} &\n"

for i in range(0, args.num_tasks):
	output += f"tx{i} = {np.random.randint(1,grid_size)} &\n"
	output += f"ty{i} = {np.random.randint(1,grid_size)} &\n"

output = output[:-2]
output += "\n\nendinit"

f.write(output)

print(f"Init file {filename} created.\n{len(output)} characters.\n")
print(f"Parameters:\nGrid = {args.grid_size}x{args.grid_size} ({args.grid_size**2} tiles)\n"+\
    f"Robots: {args.num_robots}\nTasks: {args.num_tasks}")
