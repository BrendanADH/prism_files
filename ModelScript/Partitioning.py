import numpy as np
import subprocess
import argparse

def euclid_dist(A, B):
    
    s = 0
    for i in range(0, len(A)):
        s += (A[i] - B[i])**2
    return np.sqrt(s)
            

def k_means(points, num_groups, centroids = [], max_its = 1000):
    
    #e_points = np.column_stack((np.zeros((len(points))), points))
    points = np.array(points)
    # pick initial cluster centres
    group_means = np.array([])
    old_means = np.zeros((num_groups,2))
    
    if len(centroids) == 0:
        #randomly choose cluster centres:
        group_means = UniqueRandomChoices(points, num_groups)
    else:
        group_means = centroids
        
    its = 0
    while(True):
        its += 1
        
        # assignment of points to groups
        assignments = AssignToCentroid(points, group_means)
        group_means = CalculateGroupMeans(points, assignments, num_groups)

        # check if the groups have changed
        allIdentical = True
        for i in range(num_groups):
            if old_means[i,0] != group_means[i,0] or old_means[i,1] != group_means[i,1] :
                allIdentical = False
                
        # exit if no change
        if allIdentical:
            return assignments
        
        # store the means for the next iteration
        old_means = group_means
        
        # exit if too much
        if(its == max_its):
            print("Max iterations reached")
            return assignments
     
    
def CalculateGroupMeans(points, assignments, num_groups):

    group_means = np.zeros((num_groups,2))
    for i in range(len(group_means)): # for each group index...
        point_ids_in_groups = np.where(assignments == i) # get point ids in this group
        points_in_groups  = np.array(points)[point_ids_in_groups]
        mean_x = np.mean(points_in_groups[:,0])
        mean_y = np.mean(points_in_groups[:,1])
        group_means[i] = [mean_x, mean_y]

    return group_means

def UniqueRandomChoices(array, num_selections):
    
    #randomly choose cluster centres:
    choices = []
    for i in range(0, num_selections):
        rand_index = np.random.randint(len(array))
        while(rand_index in choices):
            rand_index = np.random.randint(len(array))
        choices.append(rand_index)

    return np.array(array)[choices]

            
def AssignToCentroid(points, centroids):
    
    assignments = np.ones(len(points)) * -1

    for i in range(0, len(points)):
        closest_k = -1
        min_dist = np.inf
        for j in range(0, len(centroids)):
            dist = euclid_dist(points[i], centroids[j])
            if dist < min_dist:
                min_dist = dist
                closest_group_id = j
       
        assignments[i] = closest_group_id

    return np.array(assignments)

def global_k_means(points, num_groups, point_sizes,
                   stop_condition = lambda x: False, max_its = 1000):
    
    
    # find the centroid of the dataset (k=1)
    
    mean_x = np.mean(points[:,0])
    mean_y = np.mean(points[:,1])
    
    centroids = [[mean_x, mean_y]]
    
    for i in range(2, num_groups+1):
        assignments, centroids = k_find_optimal(points, i, centroids = centroids, max_its = max_its)
        #centroids = np.vstack((centroids, optimal_init))
        if(stop_condition(assignments, point_sizes)):
            return assignments
    
    return assignments

    
def k_find_optimal(points, num_groups, centroids, max_its = 1000):
    
    # find the optimal placement of the nth centroid given n-1 centroids
    
    # run k means for all possible inits and find the best one
    min_err = np.inf
    best_init_index = -1
    assignments = np.ones_like(points) * -1
    for i in range(0, len(points)):
        
        # check if the point is at a centroid. if so, skip (avoids duplicate, forever-empty groups)
        skip = False
        for c in centroids:
            if c[0] == points[i,0] and c[1] == points[i,1]:
                skip = True
        if(skip):
            continue
        
        assignments = k_means(points, num_groups, np.vstack((centroids, points[i])), max_its = max_its)
        
        err_sum = 0
        group_centres = CalculateGroupMeans(points, assignments, num_groups)
        
        # get clustering error:
        for j in range(num_groups):
            point_ids_in_group = np.where(assignments == i) # get point ids in this group
            group_points  = np.array(points)[point_ids_in_group]
            group_cent = group_centres[j]

            sos = 0 # sum of squares in group
            for k in range(len(group_points)):
                sos += np.sqrt((group_points[k,0] - group_cent[0])**2 + (group_points[k,1] - group_cent[1])**2)
        
            err_sum += sos # add it to global clustering error
    
        # check if this init gave the minimum error
        if (err_sum < min_err):
            min_err = err_sum
            best_init_index = i #this currently just selects the last computed group mean
            # how do i select the new centroid point?
    
    optimal_assignments = k_means(points, num_groups, np.vstack((centroids, points[best_init_index])))
    optimal_centroids = CalculateGroupMeans(points, optimal_assignments, int(max(optimal_assignments)+1))
    return optimal_assignments, optimal_centroids


def GetTasksPerGroup(assignments, point_sizes):
    n_groups = int(max(assignments)+1)
    # loop through groups and count points
    group_totals = np.zeros(n_groups)
    for i in range(0,n_groups):
        for j in range(0,len(assignments)):
            if i == assignments[j]: # if the point is in the group, add 'point_size' to group total
                group_totals[i] += point_sizes[j]
    
    return group_totals