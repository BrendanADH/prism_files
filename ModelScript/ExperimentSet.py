import numpy as np
import subprocess
import argparse
import datetime

import ModelScript_NoClock as script

parser = argparse.ArgumentParser()

#parser.add_argument("target_script", type=, help = "Name of script from which to generate the models")

parser.add_argument("filename", type = str, help = "Base filename for models (seperate files will be numbered in sequence)")
parser.add_argument("robots_range", type = str, help = "Range of robots, format 'max min step' ")
parser.add_argument("tasks_range", type = str, help = "Range of tasks, format 'max min step' ")
parser.add_argument("locales_range", type = str, help = "Range of locales, format 'max min step' ")
parser.add_argument("repetitions", type=int, help="Number of models that should be generated and tested for each parameter combination")
parser.add_argument("prism_args", type = str, help = "Arguments to be passed to prism")

def ParseRange(arg_string):

	arg_string = arg_string.split(" ")
	a_min = int(arg_string[0])
	a_max = int(arg_string[1])
	if(len(arg_string)==3):
		a_step = int(arg_string[2])

	return a_min, a_max, a_step

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



args = parser.parse_args();

reps, filename = args.repetitions, args.filename
CheckOverwrite(filename)
f = open(filename, "w")

r_min, r_max, r_step = ParseRange(args.robots_range)
t_min, t_max, t_step = ParseRange(args.tasks_range)
l_min, l_max, l_step = ParseRange(args.locales_range)

import datetime

f.write(f"# Experiment {datetime.datetime.now()}\n# r_min = {r_min} r_max = {r_max} r_step = {r_step}\n# t_min = {t_min} t_max = {t_max} t_step = {t_step}\n# l_min = {l_min} l_max = {l_max} l_slep = {l_step}\n# {reps} repetitions per parameter combination\n\n")

print(f"Running experiment:\nAspect|Min|Max|Step\nRobots {r_min} {r_max} {r_step}\nTasks {t_min} {t_max} {t_step}\nLocales {l_min} {l_max} {l_step}")

for r in range(r_min, r_max, r_step):
	for t in range(t_min, t_max, t_step):
		for l in range(l_min, l_max, l_step):
			print(f"Running parameters: {r} robots {t} tasks {l} locales...")
			file_output = "{r} {t} {l}"
			times = []
			for rep in range(0, reps):
				print(f"Iteration {rep}/{reps}:")
				modelCode = script.CreateModelCode(r, t, l);
				filename = f"experiment{r}{l}{t}{reps}temp{np.random.randint(1000,9999)}.prism"
				print("Creating Model...")
				script.WriteFile(filename, modelCode, r, t, l, bulk = True)
				print("Running PRISM...")
				output = subprocess.run(["prism", filename, "-pf",  args.prism_args], capture_output = True).stdout
				
				output = str(output)
				text_b_index = output.find("Time for model checking:")
				text_e_index = output.find("seconds.", text_b_index, len(output))
				print("writing")
				if text_b_index == -1 or text_e_index == -1:
					if(output.find("Killed.")!=-1):
						print("PRISM ran out of memory")
					continue
				else: 
					t = float(output[text_b_index+len("Time for model checking:"):text_e_index])
					times.append(t)
					print(f"Time: {t}s (Expected remaining for these parameters: {np.mean(times)* (reps - i)}s)\n\n\n")
					f.write(f"{times} {np.mean(times)} {np.std(times)}")

print(f"Times: {times}\nMean: {np.mean(times)}s\nSTD: {np.std(times)}s")

