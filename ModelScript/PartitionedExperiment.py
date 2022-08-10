import numpy as np
import subprocess
import argparse

from Partitioning import *
from ModelCodeSpecified import *
import matplotlib.pyplot as plt

"""

This script runs an experiment on the change in model checking time and the change in optimality caused by partitioning.

Steps of operation:

1. Generate a random distribution of locales
2. Distribute tasks between locales
3. Run prob. model checking to get time and team_rewards values
4. Partition
5. For each partition in sequence, run prob. model checking to get time and team_rewards again
6. Output pre/post-partition values of time and team_rewards

inputs (cmd): number of repetitions, number of tasks, number of locales, mean_group_size
outputs: log file containing: pre/post-partition values of time and team_rewards, avg. values before and avg. values after

Notes:
- the prism argument will be hardcoded here
- Nr = Nt for all scenarios to simulate an inexhaustable inventory of robots

"""

def ParsePrismOutput(output):

	output = str(output)
	text_b_index = output.find("Time for model checking:")
	text_e_index = output.find("seconds.", text_b_index, len(output))
	t = float(output[text_b_index+len("Time for model checking:"):text_e_index])
	#times.append(t)

	text_b_index = output.find("Value in the initial state:")
	text_e_index = output.find("Time for model checking:")
	r = float((output[text_b_index+len("Value in the initial state:"):text_e_index-4]))
	#results.append(r)

	return t,r

def CreatePrismArgument(reward_threshold, Nt):

	prism_argument = "multi(R{\"team_reward\"}min=? [C]"
	for i in range(Nt): 
		prism_argument += ", R{\"rewards_R"+str(i)+"\"}<="+str(12000) +" [C]"

	prism_argument += ")"

	return prism_argument

def stop_cond(assignments, point_sizes):
    group_totals = GetTasksPerGroup(assignments, point_sizes)
    mean_group_size = np.mean(group_totals)
    if mean_group_size < tpg:
        return True
    else:
        return False

parser = argparse.ArgumentParser()

parser.add_argument("num_repetitions", type=int, help="Number of models that should be generated and tested")
parser.add_argument("Nt", type=int, help="number tasks in whole model")
parser.add_argument("Nl", type=int, help="number of locales in whole model")
parser.add_argument("mean_tasks_per_group", type=int, help="mean group size at which the partitioning terminates")
parser.add_argument("skip_unpartitioned", nargs = "?", type = int, help = "If 1, don't run prism on the unpartitioned system (useful for when it would run out of memory)")

args = parser.parse_args();



# generate the unpartitioned model; test



# generate Nl locale points:

repetitions = args.num_repetitions
Nt = args.Nt
Nl = args.Nl
tpg = args.mean_tasks_per_group
skip_unpartitioned = args.skip_unpartitioned
if(skip_unpartitioned is not None):
	skip_unpartitioned = bool(skip_unpartitioned == 1)

locale_points = np.zeros((Nl,2))
tasks_per_locale = np.ones(Nl) # all locales have at least 1 task.

space_range = 10000

unpart_times = np.empty(repetitions)
unpart_results = np.empty(repetitions)
part_times = np.empty(repetitions)
part_results = np.empty(repetitions)
time_change = np.empty(repetitions)
result_change = np.empty(repetitions)

for rep in range(repetitions):

	print(f"\n\nRep {rep}/{repetitions}")

	locale_points = np.zeros((Nl,2))
	if(Nl <= Nt):
		tasks_per_locale = np.ones(Nl) # all locales have at least 1 task if possible
	else:
		tasks_per_locale = np.zeros(Nl)

	for i in range(0, Nl):
	    locale_points[i] = [np.random.random() * space_range, np.random.random() * space_range]
	    
	for i in range(0, Nt - int(np.sum(tasks_per_locale))):
	    tasks_per_locale[np.random.randint(len(locale_points))] += 1

	if skip_unpartitioned == False:
	# make this into prism code
		print(f"Creating PRISM file for the unpartitioned system\nParameters:\nlocale points = {locale_points}\ntasks_per_locale = {tasks_per_locale}")
		modelCode = CreateModelCode(locale_points, tasks_per_locale)
		filename = f"experiment_unpart_{Nl}_{Nt}.prism"
		WriteFile(filename, modelCode)

		# make the prism argument
		print("Writing PRISM argument...")
		prism_argument = CreatePrismArgument(12000, Nt)

		# run prism and parse

		print("Running PRISM...\n")
		output = subprocess.run(["prism", filename, "-pf",  prism_argument], capture_output = True).stdout
		time, result = ParsePrismOutput(output)
		unpart_times[rep] = time
		unpart_results[rep] = result

		print(f"Robots|Tasks|Locales: {Nt} {Nt} {Nl}\nTime: {time}\nResult: {result}")
	else:
		print("Skipping unpartitioned model checking...")
		unpart_times[rep] = "-1"
		unpart_results[rep] = "-1"

	# plt.figure(figsize = (7,7))
	# plt.title("Locale Distribution")
	# plt.scatter(locale_points[:,0], locale_points[:,1], color = "dodgerblue")
	# for i in range(0, len(tasks_per_locale)):
	# 	plt.text(locale_points[i,0], locale_points[i,1], int(tasks_per_locale[i]))
	# plt.show(block = False)    

	# partition:
	max_groups = Nl
	assignments = global_k_means(locale_points, max_groups, point_sizes=tasks_per_locale, stop_condition = stop_cond, max_its=100)


	#identify number of groups:
	num_groups = int(max(assignments)+1)

	sum_times = 0
	sum_results = 0 

	for i in range(num_groups):
		#identify points in group:
		locales_in_group = []
		tasks_per_locale_in_group = []
		for j in range(len(assignments)):
			if i == assignments[j]:
				locales_in_group.append(locale_points[j])
				tasks_per_locale_in_group.append(tasks_per_locale[j])


		print("#locales|#tasks: ", len(locales_in_group), " | ", int(sum(tasks_per_locale_in_group)))

		modelCode = CreateModelCode(locales_in_group, tasks_per_locale_in_group)
		filename = f"experiment_part_{Nl}_{Nt}.prism"
		WriteFile(filename, modelCode)

		# make the prism argument
		prism_argument = CreatePrismArgument(12000, int(sum(tasks_per_locale_in_group)))

		# run prism and parse
		output = subprocess.run(["prism", filename, "-pf",  prism_argument], capture_output = True).stdout
		time, result = ParsePrismOutput(output)

		sum_times += time
		sum_results += result

		print(f"Robots|Tasks|Locales: {Nt} {Nt} {Nl}\nTime: {time}\nResult: {result}")

	part_times[rep] = sum_times
	part_results[rep] = sum_results
	if skip_unpartitioned == True:
		time_change[rep] = "-1"
		result_change[rep] = "-1"
	else:
		time_change[rep] = sum_times - unpart_times[rep]
		result_change[rep] = sum_results - unpart_results[rep]



	# plt.figure(figsize = (7,7))
	# # print("assignments: ", assignments)
	# # print("num groups: ", max(assignments)+1)
	# # print("tasks per group: ", GetTasksPerGroup(assignments, tasks_per_locale), "\nmean: ", np.mean(GetTasksPerGroup(assignments, tasks_per_locale)))

	# for i in range(0,int(max(assignments)+1)):
	#     point_ids_in_groups = np.where(assignments == i) # get point ids in this group
	#     points_in_groups  = np.array(locale_points)[point_ids_in_groups]
	#     plt.scatter(points_in_groups[:,0], points_in_groups[:,1])

	# plt.show(block = False)

	# construct a model file for each partition
	# run prism for each and print results

print(f"Input parameters: {repetitions} {Nt} {Nl} {tpg}")

print(f"\nUnpartitioned system:\nTime (mean|std): {np.mean(unpart_times)} {np.std(unpart_times)}\nResults (mean|std): {np.mean(unpart_results)} {np.std(unpart_results)}" + \
	f"\n\nPartitioned system:\nTime (mean|std): {np.mean(part_times)} {np.std(part_times)}\nResults (mean|std): {np.mean(part_results)} {np.std(part_results)}" + \
	f"\nMean time change (mean|std): {np.mean(time_change)}{np.std(time_change)}\nMean result change (mean|std): {np.mean(result_change)} {np.std(result_change)} ")

print(f"Formatted: {np.mean(unpart_times)} {np.std(unpart_times)} {np.mean(part_times)} {np.std(part_times)} {np.mean(unpart_results)} {np.std(unpart_results)} {np.mean(part_results)} {np.std(part_results)} {np.mean(time_change)} {np.std(time_change)} {np.mean(result_change)} {np.std(result_change)}")

f = open(f"experiment_results_{repetitions}_{Nt}_{Nl}_{tpg}", "w")
f.write(f"unpart_times: {str(list(unpart_times))}\n")
f.write(f"unpart_results: {str(list(unpart_results))}\n")
f.write(f"part_times: {str(list(part_times))}\n")
f.write(f"part_results: {str(list(part_results))}\n")
f.write(f"time_change: {str(list(time_change))}\n")
f.write(f"result_change: {str(list(result_change))}\n")

print(f"Results written to file 'experiment_results_{repetitions}_{Nt}_{Nl}_{tpg}'")

