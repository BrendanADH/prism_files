import numpy as np
import subprocess
import argparse

import ModelScript_NoClock as modelGen
import Partitioning as part

parser = argparse.ArgumentParser()

#parser.add_argument("target_script", type=, help = "Name of script from which to generate the models")
parser.add_argument("num_repetitions", type=int, help="Number of models that should be generated and tested")
parser.add_argument("filename_base", type = str, help = "Base filename for models (seperate files will be numbered in sequence)")
parser.add_argument("prism_args", type = str, help = "Arguments to be passed to prism")
parser.add_argument("parameters", nargs = "+", const = None, type=int, help="Arguments for the model generator")


prism_directory = "~/Downloads/Installers/prism-4.7-linux64/bin"


args = parser.parse_args();

reps, fnb, params = args.num_repetitions, args.filename_base, args.parameters

print(f"Experiment parameters: {reps} {fnb} {params}\n")
times= []
results = []

for i in range(0, reps):
	print(f"Iteration {i}:")
	modelCode = modelGen.CreateModelCode(*params);
	filename = f"{fnb}_{i}.prism"
	print("Creating Model...")
	modelGen.WriteFile(filename, modelCode, *params, bulk = True)
	print("Running PRISM...")
	output = subprocess.run(["prism", filename, "-pf",  args.prism_args], capture_output = True).stdout
	
	output = str(output)
	text_b_index = output.find("Time for model checking:")
	text_e_index = output.find("seconds.", text_b_index, len(output))
	t = float(output[text_b_index+len("Time for model checking:"):text_e_index])
	times.append(t)

	text_b_index = output.find("Value in the initial state:")
	text_e_index = output.find("Time for model checking:")
	r = float((output[text_b_index+len("Value in the initial state:"):text_e_index-4]))
	results.append(r)

	print(f"Result: {r}\nTime: {t}s (Expected remaining for experiment: {np.mean(times)* (reps - i)}s)\n")

print(f"Robots|Tasks|Locales: {params[0]} {params[1]} {params[2]}\nTimes: {times}\nMean | STD: {np.mean(times)} {np.std(times)}\nResults: {results}\nMean | STD: {np.mean(results)} {np.std(results)}")

