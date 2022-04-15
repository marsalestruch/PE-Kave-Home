# Rep la llista d'objectes i el nombre de caixes i els assigna segons el quantil al qual pertanyen en base a una mètrica
# Mètode: volum
def compute_baseline_vol(objects, num_boxes):
    assignments = np.array([None] * len(objects))
    volume = np.array([None] * len(objects))
    volume_quantiles = np.array([None] * num_boxes)
    
    for i in range(NUM_OBJECTS):
        volume[i] = objects[i][0] * objects[i][1] * objects[i][2]

    for j in range(num_boxes):
        volume_quantiles[j] = np.quantile(volume, (j+1)/num_boxes)

    for i in range(NUM_OBJECTS):
        j = 0;
        while j < num_boxes and assignments[i] == None:
            #print(i, j)
            if volume[i] > volume_quantiles[j]:
                j+=1
            else:
                assignments[i] = j

    sizes = compute_sizes(objects, assignments, num_boxes)

    boxes = np.zeros(num_boxes, dtype=int)
    
    for i in range(NUM_OBJECTS):
        boxes[assignments[i]] +=1
            
    space = 0.0  #espai buit en el total de caixes

    for j in range(num_boxes):
        space = space + boxes[j] * sizes[j][0] * sizes[j][1] * sizes[j][2]
            
    NEW_SPACE = space

    return sizes, assignments, NEW_SPACE


# Rep la llista d'objectes i el nombre de caixes i els assigna segons el quantil al qual pertanyen en base a una mètrica
# Mètode: diagonal
def compute_baseline_diag(objects, num_boxes):
    assignments = np.array([None] * len(objects))
    diagonal = np.array([None] * len(objects))
    diag_quantiles = np.array([None] * num_boxes)
    
    for i in range(NUM_OBJECTS):
        diagonal[i] = 0
        for xi in objects[i]:
            diagonal[i] += xi*xi

    for j in range(num_boxes):
        diag_quantiles[j] = np.quantile(diagonal, (j+1)/num_boxes)

    for i in range(NUM_OBJECTS):
        j = 0;
        while j < num_boxes and assignments[i] == None:
            #print(i, j)
            if diagonal[i] > diag_quantiles[j]:
                j+=1
            else:
                assignments[i] = j

    sizes = compute_sizes(objects, assignments, num_boxes)

    boxes = np.zeros(num_boxes, dtype=int)
    
    for i in range(NUM_OBJECTS):
        boxes[assignments[i]] +=1
            
    space = 0.0  #espai buit en el total de caixes

    for j in range(num_boxes):
        space = space + boxes[j] * sizes[j][0] * sizes[j][1] * sizes[j][2]
            
    NEW_SPACE = space

    return sizes, assignments, NEW_SPACE


# Creació d'un baseline
baseline_sizes, baseline_assignments, baseline_new_space = compute_baseline_vol(OBJECTS, NUM_BOXES)
print_solution_stats(baseline_sizes, NUM_BOXES, baseline_assignments, baseline_new_space)

print("----------------------------------------------------------------------------------------------")

baseline_sizes, baseline_assignments, baseline_new_space = compute_baseline_diag(OBJECTS, NUM_BOXES)
print_solution_stats(baseline_sizes, NUM_BOXES, baseline_assignments, baseline_new_space)
