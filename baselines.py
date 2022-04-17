# Rep la llista d'objectes i el nombre de caixes i els assigna segons el quantil al qual pertanyen en base a una mètrica
def compute_baseline(objects, num_boxes, method):
    assignments = np.array([None] * len(objects))
    vec = np.array([None] * len(objects))
    quantiles = np.array([None] * num_boxes)

    if method == "volume":
        for i in range(NUM_OBJECTS):
            vec[i] = objects[i][0] * objects[i][1] * objects[i][2]
    
    elif method == "diagonal":
        for i in range(NUM_OBJECTS):
            vec[i] = 0
            for xi in objects[i]:
                vec[i] += xi*xi

    for j in range(num_boxes):
        quantiles[j] = np.quantile(vec, (j+1)/num_boxes)

    for i in range(NUM_OBJECTS):
        j = 0;
        while j < num_boxes and assignments[i] == None:
            #print(i, j)
            if vec[i] > quantiles[j]:
                j+=1
            else:
                assignments[i] = j

    # Per a calcular l'espai ocupat
    sizes = compute_sizes(objects, assignments, num_boxes)
    boxes = np.zeros(num_boxes, dtype=int)
    for i in range(NUM_OBJECTS):
        boxes[assignments[i]] +=1 
    space = 0.0  
    for j in range(num_boxes):
        space = space + boxes[j] * sizes[j][0] * sizes[j][1] * sizes[j][2]
    NEW_SPACE = space

    return sizes, assignments, NEW_SPACE


# Creació d'un baseline
baseline_sizes, baseline_assignments, baseline_new_space = compute_baseline(OBJECTS, NUM_BOXES, "volume")
print_solution_stats(baseline_sizes, NUM_BOXES, baseline_assignments, baseline_new_space)

print("----------------------------------------------------------------------------------------------")

baseline_sizes, baseline_assignments, baseline_new_space = compute_baseline(OBJECTS, NUM_BOXES, "diagonal")
print_solution_stats(baseline_sizes, NUM_BOXES, baseline_assignments, baseline_new_space)
