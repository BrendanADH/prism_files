
from Partitioning import *

def WriteFile(filename, modelCode):
	f = open(filename, "w")
	f.write(modelCode)

def CreateModel(locale_points, tasks_per_locale):

	num_tasks = int(np.sum(tasks_per_locale))


	output = "mdp\n\n"

	output += Constants(locale_points, tasks_per_locale)
	for i in range(num_tasks):
		output += RobotModule(i, num_tasks, len(locale_points)+1)
	for i in range(num_tasks):
		output += TaskModule(i, num_tasks)
	output += Rewards(num_tasks, len(locale_points)+1)


	WriteFile("testing_partition", output)

def Constants(locale_points, tasks_per_locale):

	output = ""
	num_tasks = int(np.sum(tasks_per_locale))

	for i in range(len(locale_points)):
			output += f"const int dist_L{0}L{i+1} = 8000;\n" # 8 cost to enter system
			output += f"const int dist_L{i+1}L{0} = 8000;\n" # 8 cost to enter system

	output += "\n"

	for i in range(len(locale_points)):
		for j in range(len(locale_points)):
			if (i==j):
				continue
			output += f"const int dist_L{i+1}L{j+1} = {int(euclid_dist(locale_points[i], locale_points[j]))};\n"
	
	output += "\n"

	for i in range(0,num_tasks):
		output += f"const int T{i}_duration = {5000};\n"

	output += "\n"

	locale = 0
	counter = 0
	for i in range(0, num_tasks):        
		output += f"const int T{i}_locale = {locale+1};\n"
		counter+=1
		if(tasks_per_locale[locale]==counter):
			locale += 1
			counter = 0 

	return output

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

def Rewards(num_tasks, num_locales):
    output = ""
    for i in range(0, num_tasks):
        output += f"\n\nrewards \"rewards_R{i}\"\n\n"
        for j in range(0, num_tasks):
            for k in range(0, num_locales):
                for l in range(0, num_locales):

                    if(k==l):
                        output += f"\t[R{i}T{j}_complete] R{i}_locale = {k} & T{j}_locale = {l} : T{j}_duration;\n"
                    else:
                        output += f"\t[R{i}T{j}_complete] R{i}_locale = {k} & T{j}_locale = {l} : dist_L{k}L{l} + T{j}_duration;\n"

        output += "\nendrewards"


    output += f"\n\nrewards \"team_reward\"\n\n"
    for i in range(0, num_tasks):
        for j in range(0, num_tasks):
            for k in range(0, num_locales):
                for l in range(0, num_locales):

                    if(k==l):
                        output += f"\t[R{i}T{j}_complete] R{i}_locale = {k} & T{j}_locale = {l} : T{j}_duration;\n"
                    else:
                        output += f"\t[R{i}T{j}_complete] R{i}_locale = {k} & T{j}_locale = {l} : dist_L{k}L{l} + T{j}_duration;\n"

    output += "\nendrewards"

    return output
