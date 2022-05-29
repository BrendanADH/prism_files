import numpy as np
import sys
import argparse

def Constants(num_tasks, num_locales):

    obstacle_locations = []
    output = ""

    for i in range(0, num_locales+1):
        for j in range(0, num_locales+1):
            if(i==j):
                continue
            if(i == 0 or j == 0):
                output += f"const int dist_L{i}L{j} = 8;\n" # 8 cost to enter system
            else:
                output += f"const int dist_L{i}L{j} = {np.random.randint(1,3)};\n"

    output += "\n"

    for i in range(0,num_tasks):
        output += f"const int T{i}_duration = {np.random.randint(1,3)};\n"

    output += "\n"

    for i in range(0,num_tasks):        
        output += f"const int T{i}_locale = {np.random.randint(1,num_locales+1)};\n"

    return output


# returns string representing robot
def RobotModule(id, num_tasks, num_locales):
    output = f"\n\n" + \
    f"module robot{id}\n\n" + \
    f"\tR{id}_locale: [0..{num_locales}] init 0;\n"
    for i in range(0, num_tasks):
            output += f"\t[R{id}T{i}_complete] T{i}_active = true -> (R{id}_locale' = T{i}_locale);\n"

    output += '''\n\nendmodule'''

    return output


def TaskModule(id, num_robots):
    output = f"\n\n" + \
    f"module task{id}\n\n" + \
    f"\tT{id}_active : bool init true;\n"

    for i in range(0, num_robots):
        output+=f"\t[R{i}T{id}_complete] true -> (T{id}_active' = false);\n"


    output += "\nendmodule"

    return output


def Rewards(num_robots, num_tasks, num_locales):
    output = ""
    for i in range(0, num_robots):
        output += f"\n\nrewards \"rewards_R{i}\"\n\n"
        for j in range(0, num_tasks):
            for k in range(0, num_locales+1):
                for l in range(0, num_locales+1):

                    if(k==l):
                        output += f"\t[R{i}T{j}_complete] R{i}_locale = {k} & T{j}_locale = {l} : T{j}_duration;\n"
                    else:
                        output += f"\t[R{i}T{j}_complete] R{i}_locale = {k} & T{j}_locale = {l} : dist_L{k}L{l} + T{j}_duration;\n"

        output += "\nendrewards"


    output += f"\n\nrewards \"team_reward\"\n\n"
    for i in range(0, num_robots):
        for j in range(0, num_tasks):
            for k in range(0, num_locales+1):
                for l in range(0, num_locales+1):

                    if(k==l):
                        output += f"\t[R{i}T{j}_complete] R{i}_locale = {k} & T{j}_locale = {l} : T{j}_duration;\n"
                    else:
                        output += f"\t[R{i}T{j}_complete] R{i}_locale = {k} & T{j}_locale = {l} : dist_L{k}L{l} + T{j}_duration;\n"

    output += "\nendrewards"

    # for i in range(0, num_tasks):
    #     output += f"\n\nrewards \"T{i}_completion\"\n\n"
    #     for j in range(0, num_robots):
    #         output+=f"\t[R{j}T{i}_complete] true : 1;\n"
    #     output += "\nendrewards"


    return output


def CreateModelCode(num_robots, num_tasks, num_locales):

    modelCode = "mdp\n"

    modelCode += Constants(num_tasks, num_locales)

    for i in range(0, num_robots):
        modelCode+=RobotModule(i, num_tasks, num_locales)

    for i in range(0, num_tasks):
        modelCode+=TaskModule(i, num_robots)

    modelCode+=Rewards(num_robots, num_tasks, num_locales)

    return modelCode

def CheckOverwrite(filename, overwriteByDefault = False):
    
    try:
        f = open(filename, "x")
    except (FileExistsError):
        if(overwriteByDefault == True):
            print(f"Overwriting \'{filename}\'...")
            f = open(filename, "w")

        else:
            chosen = False
            while(chosen == False):
                ans = input(f"File \'{filename}\' already exists, overwrite? y/n\n")
                if(ans == "Y" or ans == "y"):
                    chosen = True;
                    print(f"Overwriting \'{filename}\'...")
                    #f = open(args.output_name + ".prism", "w")
                elif(ans == "N" or ans == "n"):
                    chosen = True 
                    print("Exiting.")
                    exit()

def WriteFile(filename, modelCode, num_robots, num_tasks, num_locales, bulk = False):
    
    f = open(filename, "w")
    f.write(modelCode)
    if(bulk == False):
        print(f"Model {filename} created.\n{len(modelCode)} characters.\n")
        print(f"Model parameters:\nLocales = {num_locales}\n"+\
            f"Robots: {num_robots}\nTasks: {num_tasks}")
#    if(init_file != None):
#        print(f"Init file: {init_file}")


def main(output_name, num_robots, num_tasks, num_locales):
    filename = f"{output_name}_{num_robots}_{num_tasks}_{num_locales}.prism"

    print(f"Creating model file \'{filename}\'")

    CheckOverwrite(filename);
    modelCode = CreateModelCode(num_robots, num_tasks, num_locales);
    WriteFile(filename, modelCode, num_robots, num_tasks, num_locales)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("num_robots", type=int, help="Number of robots to be included in the model")
    parser.add_argument("num_tasks", type=int, help="Number of tasks to be included in the model")
    parser.add_argument("num_locales", type=int, help="Number of locales in the abstracted space")
    parser.add_argument("output_name", type=str, help="Filename for output")
    parser.add_argument("init_file", nargs = "?", const = None, type=str, help="Optional: file containing an init/endinit block with which to initialise variables")

    args = parser.parse_args();

    main(args.output_name, args.num_robots, args.num_tasks, args.num_locales)