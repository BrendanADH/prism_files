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

def Durations():

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

    return output


# returns string representing robot
def RobotModule(id):
    output = f"\n\n" + \
    f"module robot{id}\n\n" + \
    f"\tR{id}_locale: [1..{args.num_locales}] init {np.random.randint(1,args.num_locales)};\n" + \
    f"\tR{id}_lock : bool init false;\n" + \
    f"\t[release] true -> (R{id}_lock' = false);\n" + \
    f"\t[R{id}_wait] !R{id}_lock -> (R{id}_lock' = true);\n" 

    for i in range(0, args.num_tasks):
        output += f"\t[R{id}T{i}_complete] !R{id}_lock & T{i}_active = true -> (R{id}_lock' = true) & (R{id}_locale' = T{i}_locale);\n"

    output += '''\n\nendmodule'''

    return output


def TaskModule(id):
    output = f"\n\n" + \
    f"module task{id}\n\n" + \
    f"\tT{id}_active : bool init true;\n" + \
    f"\tT{id}_locale : [1..{args.num_locales}] init {np.random.randint(1,args.num_locales)};\n" 

    for i in range(0, args.num_robots):
        output+=f"\t[R{i}T{id}_complete] true -> (T{id}_active' = false);\n"


    output += "\nendmodule"

    return output


def ClockModule():

    output = f"\n\n" + \
    f"formula all_robots_complete = ("

    for i in range(0, args.num_robots):
        output += f"R{i}_lock"
        if(i!=args.num_robots-1):
            output += " & "
        else:
            output += ");\n\n" 

    output+= f"module sync\n\n" + \
    f"\t[release] all_robots_complete -> true;\n\n" + \
    f"endmodule"

    return output

def Rewards():
    output = "\n\n" + \
    "rewards \"energy_expense\"\n\n"
    
    for i in range(0, args.num_robots):
        for j in range(0, args.num_tasks):
            for k in range(0, args.num_locales):
                for l in range(0, args.num_locales):

                    if(k==l):
                        output += f"\t[R{i}T{j}_complete] R{i}_locale = {k} & T{j}_locale = {l} : T{j}_duration;\n"
                    else:
                        output += f"\t[R{i}T{j}_complete] R{i}_locale = {k} & T{j}_locale = {l} : dist_L{k}L{l} + T{j}_duration;\n"

        output += f"\t[R{i}_wait] true : 1;\n\n"

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

modelCode += Durations()

for i in range(0, args.num_robots):
    modelCode+=RobotModule(i)

for i in range(0, args.num_tasks):
    modelCode+=TaskModule(i)

modelCode+=ClockModule()
modelCode+=Rewards()


f.write(modelCode)
print(f"Model {filename} created.\n{len(modelCode)} characters.\n")
print(f"Model parameters:\nLocales = {args.num_locales}\n"+\
    f"Robots: {args.num_robots}\nTasks: {args.num_tasks}")
if(args.init_file != None):
    print(f"Init file: {args.init_file}")