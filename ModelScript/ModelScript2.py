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

def ParseInitFile():
    if (args.init_file != None):
        init_code = []
        try:
            f = open(args.init_file, "r")
        except (FileNotFoundError):
            print(f"Init file \'{args.init_file}\' not found, exiting.")
            exit()

        for line in f:
                init_code.append(line)
    else:
        init_code = None

    return init_code

def Constants():
    output = f"\n\n" + \
    f"const grid_size = {args.grid_size};\n" + \
    f"const num_robots = {args.num_robots};\n"

    return output

def Obstacles(init_code):

    obstacle_locations = []
    output = ""

    if init_code != None:
        get_obs = False
        for line in init_code:
            l = line.strip().replace(" ","")
            if l == "":
                continue
            if not get_obs and l == "obstacles":
                get_obs = True
                continue
            elif get_obs and l == "endobstacles":
                get_obs = False
                break
            elif get_obs:
                obstacle_locations.append([int(l[0]), int(l[1])])

    for i in range(1, args.grid_size+1):
        for j in range(1, args.grid_size+1):
            obs = 'false'
            if ([i,j] in obstacle_locations):
                obs = 'true'
            output += f"\nconst bool X{i}Y{j}_Occupied = {obs};"

    return output


# returns string representing robot
def RobotModule(id):
    output = f"\n\n" + \
    f"formula obstacleLeftR{id} = (x{id} = 2 & y{id} = 1 & X1Y1_Occupied = true)|(x{id} = 2 & y{id} = 2 & X1Y2_Occupied = true)|(x{id} = 2 & y{id} = 3 & X1Y3_Occupied = true)|(x{id} = 3 & y{id} = 1 & X2Y1_Occupied = true)|(x{id} = 3 & y{id} = 2 & X2Y2_Occupied = true)|(x{id} = 3 & y{id} = 3 & X2Y3_Occupied = true); \n" + \
    f"formula obstacleRightR{id} = (x{id} = 1 & y{id} = 1 & X2Y1_Occupied = true)|(x{id} = 1 & y{id} = 2 & X2Y2_Occupied = true)|(x{id} = 1 & y{id} = 3 & X2Y3_Occupied = true)|(x{id} = 2 & y{id} = 1 & X3Y1_Occupied = true)|(x{id} = 2 & y{id} = 2 & X3Y2_Occupied = true)|(x{id} = 2 & y{id} = 3 & X3Y3_Occupied = true); \n" + \
    f"formula obstacleDownR{id} = (x{id} = 1 & y{id} = 2 & X1Y1_Occupied = true)|(x{id} = 1 & y{id} = 3 & X1Y2_Occupied = true)|(x{id} = 2 & y{id} = 2 & X2Y1_Occupied = true)|(x{id} = 2 & y{id} = 3 & X2Y2_Occupied = true)|(x{id} = 3 & y{id} = 2 & X3Y1_Occupied = true)|(x{id} = 3 & y{id} = 3 & X3Y2_Occupied = true); \n" + \
    f"formula obstacleUpR{id} = (x{id} = 1 & y{id} = 1 & X1Y2_Occupied = true)|(x{id} = 1 & y{id} = 2 & X1Y3_Occupied = true)|(x{id} = 2 & y{id} = 1 & X2Y2_Occupied = true)|(x{id} = 2 & y{id} = 2 & X2Y3_Occupied = true)|(x{id} = 3 & y{id} = 1 & X3Y2_Occupied = true)|(x{id} = 3 & y{id} = 2 & X3Y3_Occupied = true);\n\n" + \
    f"module robot{id}\n\n" + \
    f"\tR{id}Lock : bool; // lock for clock sync\n" + \
    f"\tx{id} : [1..grid_size]; // location variables\n" + \
    f"\ty{id} : [1..grid_size];\n\n" + \
    f"\t[release] R{id}Lock = true -> (R{id}Lock'=false); // release lock according to the sync module\n" + \
    f"\t[R{id}Move] active_bot = {id} & !R{id}Lock & x{id}>1 & !obstacleLeftR{id}-> (x{id}'=x{id}-1) & (R{id}Lock' = true); // left \n" + \
    f"\t[R{id}Move] active_bot = {id} & !R{id}Lock & x{id}<grid_size & !obstacleRightR{id}-> (x{id}'=x{id}+1) & (R{id}Lock' = true); // right \n" + \
    f"\t[R{id}Move] active_bot = {id} & !R{id}Lock & y{id}>1 & !obstacleDownR{id}-> (y{id}'=y{id}-1) & (R{id}Lock' = true); // down \n" + \
    f"\t[R{id}Move] active_bot = {id} & !R{id}Lock & y{id}<grid_size & !obstacleUpR{id}-> (y{id}'=y{id}+1) & (R{id}Lock' = true); // up \n\n" + \
    f"\t[R{id}Wait] active_bot = {id} & !R{id}Lock -> (R{id}Lock' = true); // wait\n"

    for i in range(0, args.num_tasks):
        output += f'\n\t[T{i}R{id}Complete] active_bot = {id} & !R{id}Lock & T{i}Active=true & x{id}=tx{i} & y{id}=ty{i}-> (R{id}Lock\' = true);'

    output += '''\n\nendmodule'''

    return output


def TaskModule(id):
    output = f"\n\n" + \
    f"module task{id}\n\n" + \
    f"\tT{id}Active : bool;\n" + \
    f"\ttx{id} : [1..grid_size];\n" + \
    f"\tty{id} : [1..grid_size];\n\n"

    for i in range(0, args.num_robots):
        output+=f"\t[T{id}R{i}Complete] T{id}Active=true & x{i}=tx{id} & y{i}=ty{id} -> (T{id}Active' = false);\n"


    output += "\nendmodule"

    return output


def ClockModule():

    output = f"\n\n" + \
    f"module sync\n\n" + \
    f"\tactive_bot : [0..num_robots];\n\n" + \
    f"\t[release] active_bot = num_robots -> (active_bot'=0);\n\n"

    for i in range(0, args.num_robots):
        output += f"\t[R{i}Move] true -> (active_bot' = min(active_bot+1, num_robots));\n"
        output += f"\t[R{i}Wait] true -> (active_bot' = min(active_bot+1, num_robots));\n"

    output += "\n"

    for i in range(0,args.num_tasks):
        for j in range(0, args.num_robots):
            output += f"\t[T{i}R{j}Complete] true -> (active_bot' = min(active_bot+1, num_robots));\n" 

    output += "\nendmodule"

    return output

def Rewards():
    output = "\n\n" + \
    "rewards \"time\"\n\n" + \
    "\t[release] true: 1;\n\n" + \
    "endrewards"

    return output

def InitCode(init_code):
    output = "\n\ninit\n\n"

    ender = ""
    if init_code is not None:
        ender = "&"
    
    # static parts
    for i in range(0, args.num_robots):
        output += f"\tR{i}Lock = false &\n"
    for i in range(0, args.num_tasks):
        output += f"\tT{i}Active = true &\n"
    output += f"\tactive_bot = 0 {ender}"

    #dynamic parts
    get_init = False
    if init_code is not None:
        for line in init_code:  

            l = line.strip() 
            if not get_init and l == "init":
                get_init = True
                continue
            elif get_init and l == "endinit":
                get_init = False
                break
            elif get_init:
                output += f"\t{l}\n"

    output+="\nendinit"

    return output


filename = args.output_name + ".prism"

print(f"Creating model file \'{filename}\'")

init_code = ParseInitFile()

try:
    f = open(filename, "x")
except (FileExistsError):
    chosen = False
    while(chosen == False):
        ans = input(f"File \'{filename}\' already exists, overwrite? y/n\n")
        if(ans == "Y" or ans == "y"):
            chosen = True;
            print(f"Overwriting \'{filename}\'...")
            f = open(args.output_name + ".prism", "w")
        elif(ans == "N" or ans == "n"):
            chosen = True 
            print("Exiting.")
            exit()

modelCode = "mdp"

modelCode += Constants()

modelCode += Obstacles(init_code)

for i in range(0, args.num_robots):
    modelCode+=RobotModule(i)

for i in range(0, args.num_tasks):
    modelCode+=TaskModule(i)

modelCode+=ClockModule()
modelCode+=Rewards()
modelCode+=InitCode(init_code)


f.write(modelCode)
print(f"Model {filename} created.\n{len(modelCode)} characters.\n")
print(f"Model parameters:\nGrid = {args.grid_size}x{args.grid_size} ({args.grid_size**2} tiles)\n"+\
    f"Robots: {args.num_robots}\nTasks: {args.num_tasks}")
if(args.init_file != None):
    print(f"Init file: {args.init_file}")