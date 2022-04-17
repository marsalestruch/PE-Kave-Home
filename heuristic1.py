def find_biggest_objects(best_assignment, objects, best_sizes):
    # Per tots els objectes d'un mateix assignment, retornar el que tingui norma + petita en relació a la mida de la caixa corresponent
    # Pensar un bucle que no sigui una merda com aquest
    biggest_object = []
    for i in range(NUM_BOXES):
        norms = []
        for j in range(NUM_OBJECTS):
            if best_assignment[j] == i:
                aux = objects[j] - best_sizes[i]
                norms.append((j, best_assignment[j], np.linalg.norm(aux)))
      
        norms = sorted(norms, key=lambda tup: tup[2])
        if len(norms) > 0:  # Per casos on hi hagi una caixa de mida 0,0,0 sense cap assignació
            biggest_object.append(norms[0])
    return biggest_object

  

def predict_alternative_box(biggest_obj, best_assignment, objects, best_sizes):
    
    obj = tuple(objects[biggest_obj[0]])
    #assert (((isinstance(obj,list) or isinstance(obj,tuple)) and len(obj)==3))
    x1, x2, x3 = sorted(list(obj))

    current_assig = biggest_obj[1]
    min_space = float("inf")
    predicted_size = None
    assigned_box = None

    for box, size in enumerate(best_sizes):
        
        if box != current_assig:

          if None in size:
              continue
      
          if x1<=size[0] and x2<=size[1] and x3<=size[2]:
              space = size[0]*size[1]*size[2]

              if space < min_space:
                  min_space = space
                  predicted_size = size
                  assigned_box = box
        
    if assigned_box == None: # No s'ha pogut trobar una solució alternativa!
        assigned_box = current_assig

    return assigned_box, predicted_size

  
def compute_new_sizes(best_sizes, new_assignment, objects):
    NEW_SIZES = np.zeros((len(best_sizes), 3), dtype=int)
    NEW_SIZES[0] = best_sizes[0]
    
    for i in range(1, NUM_BOXES):
      max_x1 = 0
      max_x2 = 0
      max_x3 = 0
      for j in range(NUM_OBJECTS):
          if new_assignment[j] == i:
              #print("Assignment for object", j, ":", BEST_ASSIGNMENT[j], "  |  ", i)
              #print(OBJECTS[j])
              max_x1 = max(objects[j][0], max_x1)
              max_x2 = max(objects[j][1], max_x2)
              max_x3 = max(objects[j][2], max_x3)
      
      NEW_SIZES[i] = [max_x1, max_x2, max_x3]
    
    return NEW_SIZES

  
 def print_solution_stats(NEW_SIZES, NUM_BOXES, NEW_ASSIGNMENT, NEW_SPACE):
      print("####   NEW SOLUTION   ####")
      print("NEW_SIZES = ", NEW_SIZES[:10])
      print("Filled Space[%] = ", round(TOTAL_SPACE/NEW_SPACE*100, 2),"%")
      if len(OBJECTS[0])==3:
          unused_boxes = sum([(box==(0,0,0)).all() for box in NEW_SIZES])
      else:
          unused_boxes = sum([(box==(0,0)).all() for box in NEW_SIZES])
      print("Unused boxes = {} ({})".format(unused_boxes, NUM_BOXES))
      print("####                   ####")

      print("Num objects = ", NUM_OBJECTS)
      for i in range(NUM_BOXES):
          print("box", i, ":", np.sum( np.array(NEW_ASSIGNMENT)==i), "objects;   size = ", NEW_SIZES[i])
   
 
def heuristic1():
    biggest_obj = find_biggest_objects(BEST_ASSIGNMENT,OBJECTS,BEST_SIZES)
    print("The biggest objects for each assignment are (index, assignment, distance to the box size):")
    print(biggest_obj)
    print("---------------------------------------------------------------")

    NEW_ASSIGNMENT = list(BEST_ASSIGNMENT)
    for i in range(0, len(biggest_obj)):
        obj = biggest_obj[i]
        old_assig = obj[1]
        old_size = BEST_SIZES[old_assig]
        new_assig, new_size = predict_alternative_box(obj, BEST_ASSIGNMENT, OBJECTS, BEST_SIZES)
        if new_assig == old_assig:
            new_size = old_size
        print("Current box for object", i+1, ":" , old_size, "| New box for object", i+1, ": ", new_size )
        NEW_ASSIGNMENT[obj[0]] = new_assig
    NEW_ASSIGNMENT = tuple(NEW_ASSIGNMENT)

    print("---------------------------------------------------------------")

    NEW_SIZES = compute_new_sizes(BEST_SIZES, NEW_ASSIGNMENT, OBJECTS)

    boxes = np.zeros(NUM_BOXES, dtype=int)
    
    for i in range(NUM_OBJECTS):
        boxes[NEW_ASSIGNMENT[i]] +=1
        
    space = 0.0  #espai buit en el total de caixes

    for j in range(NUM_BOXES):
        space = space + boxes[j] * NEW_SIZES[j][0] * NEW_SIZES[j][1] * NEW_SIZES[j][2]
        
    NEW_SPACE = space

    
print(heuristic1())

    print_solution_stats(NEW_SIZES, NUM_BOXES, NEW_ASSIGNMENT, NEW_SPACE)
