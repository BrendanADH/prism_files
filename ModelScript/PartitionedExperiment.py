import numpy as np
import subprocess
import argparse

import ModelScript_NoClock as modelGen
import Partitioning as part

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


parser = argparse.ArgumentParser()

parser.add_argument("num_repetitions", type=int, help="Number of models that should be generated and tested")
parser.add_argument("Nt", type=int, help="number tasks in whole model")
parser.add_argument("Nl", type=int, help="number of locales in whole model")
parser.add_argument("mean_tasks_per_group", type=int, help="mean group size at which the partitioning terminates")

args = parser.parse_args();

from Partitioning import *
from CreateModelCode import *
import matplotlib.pyplot as plt

# generate the unpartitioned model; test

# generate Nl locale points:

Nt = args.Nt
Nl = args.Nl
tpg = args.mean_tasks_per_group

locale_points = np.zeros((Nl,2))
tasks_per_locale = np.zeros(Nl)

space_range = 10000

for i in range(0, Nl):
    locale_points[i] = [np.random.random() * space_range, np.random.random() * space_range]
    
for i in range(0,Nt):
    tasks_per_locale[np.random.randint(len(locale_points))] += 1


# make this into prism code


CreateModel(locale_points, tasks_per_locale)




plt.figure(figsize = (7,7))
plt.title("Locale Distribution")
plt.scatter(locale_points[:,0], locale_points[:,1], color = "dodgerblue")
for i in range(0, len(tasks_per_locale)):
	plt.text(locale_points[i,0], locale_points[i,1], int(tasks_per_locale[i]))
plt.show(block = False)    
    
print(tasks_per_locale)
    
def stop_cond(assignments, point_sizes):
    group_totals = GetTasksPerGroup(assignments, point_sizes)
    mean_group_size = np.mean(group_totals)
    if mean_group_size < tpg:
        return True
    else:
        return False

max_groups = Nl
assignments = global_k_means(locale_points, max_groups, point_sizes=tasks_per_locale, stop_condition = stop_cond, max_its=100)

plt.figure(figsize = (7,7))
print("assignments: ", assignments)
print("num groups: ", max(assignments)+1)
print("tasks per group: ", GetTasksPerGroup(assignments, tasks_per_locale), "\nmean: ", np.mean(GetTasksPerGroup(assignments, tasks_per_locale)))

for i in range(0,int(max(assignments)+1)):
    point_ids_in_groups = np.where(assignments == i) # get point ids in this group
    points_in_groups  = np.array(locale_points)[point_ids_in_groups]
    plt.scatter(points_in_groups[:,0], points_in_groups[:,1])

plt.show(block = True)


# generate the partitioned models; test
# in the euclid version, tasks are just cart. points
# presume infinite robots (Nr = Nt) in each case (large cost to enter environment as before)

