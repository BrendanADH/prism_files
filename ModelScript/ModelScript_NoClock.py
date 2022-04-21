import numpy as np
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("num_robots", type=int, help="Number of robots to be included in the model")
parser.add_argument("num_tasks", type=int, help="Number of tasks to be included in the model")
parser.add_argument("num_locales", type=int, help="Number of locales in the abstracted space")
parser.add_argument("output_name", type=str, help="Filename for output")
parser.add_argument("init_file", nargs = "?", const = None, type=str, help="Optional: file containing an init/endinit block with which to initialise variables")

args = parser.parse_args();

def Constants():

    obstacle_locations = []
    output = ""

    for i in range(0, args.num_locales):
        for j in range(0, args.num_locales):
            if(i==j):
                continue
            output += f"const int dist_L{i}L{j} = {np.random.randint(1,5)};\n"

    output += "\n"

    for i in range(0,args.num_tasks):
        output += f"const int T{i}_duration = {np.random.randint(1,5)};\n"

    output += "\n"

    for i in range(0,args.num_tasks):        
        output += f"const int T{i}_locale = {np.random.randint(1,args.num_locales+1)};\n"

    return output


# returns string representing robot
def RobotModule(id):
    output = f"\n\n" + \
    f"module robot{id}\n\n" + \
    f"\tR{id}_locale: [0..{args.num_locales}] init 0;\n"
    for i in range(0, args.num_tasks):
        output += f"\t[R{id}T{i}_complete] T{i}_active = true -> (R{id}_locale' = T{i}_locale);\n"

    output += '''\n\nendmodule'''

    return output


def TaskModule(id):
    output = f"\n\n" + \
    f"module task{id}\n\n" + \
    f"\tT{id}_active : bool init true;\n"

    for i in range(0, args.num_robots):
        output+=f"\t[R{i}T{id}_complete] true -> (T{id}_active' = false);\n"


    output += "\nendmodule"

    return output


def Rewards():
    output = ""
    for i in range(0, args.num_robots):
        output += f"\n\nrewards \"rewards_R{i}\"\n\n"
        for j in range(0, args.num_tasks):
            for k in range(0, args.num_locales):
                for l in range(0, args.num_locales):

                    if(k==l):
                        output += f"\t[R{i}T{j}_complete] R{i}_locale = {k} & T{j}_locale = {l} : T{j}_duration;\n"
                    else:
                        output += f"\t[R{i}T{j}_complete] R{i}_locale = {k} & T{j}_locale = {l} : dist_L{k}L{l} + T{j}_duration;\n"

        output += "\nendrewards"

    return output


filename = args.output_name + ".prism"

print(f"Creating model file \'{filename}\'")

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

modelCode = "mdp\n"

modelCode += Constants()

for i in range(0, args.num_robots):
    modelCode+=RobotModule(i)

for i in range(0, args.num_tasks):
    modelCode+=TaskModule(i)

modelCode+=Rewards()


f.write(modelCode)
print(f"Model {filename} created.\n{len(modelCode)} characters.\n")
print(f"Model parameters:\nLocales = {args.num_locales}\n"+\
    f"Robots: {args.num_robots}\nTasks: {args.num_tasks}")
if(args.init_file != None):
    print(f"Init file: {args.init_file}")