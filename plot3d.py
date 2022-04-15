### PLOT 3D d'objectes i caixes  ###
# Se li passa la llista d'objectes (llista de tripletes) i llista de mides de caixes (llista de tripletes)
# Els objectes es representen com a punts amb la seva cantonada superior contrara a la cantonada (0,0,0).
# Les caixes es representen com a linies resseguint el seu contorn.

import plotly.express as px
import plotly.graph_objs as go


def plot3d(objects, box_sizes):
    
    obj2box = [predict(obj, box_sizes) for obj in objects]  #caixa assignada per a cada objecte
    co = [obj2box[o] for o in range(len(OBJECTS))]  #object colors
    xb, yb, zb, cb = [], [], [], []  #box sizes(x,y,z) + box colors

    # La gràfica de linies la fa unint punts consecutius.
    # Per a construir un cub 3d cal passar-li 16 punts (per caixa) en el format que s'indica
    for i, b in enumerate(BEST_SIZES):
        xb.extend([0,b[0],b[0],0,0,0,b[0],b[0],b[0],b[0],b[0],b[0],0,0,0,0])
        yb.extend([0,0,b[1],b[1],0,0,0,0,0,b[1],b[1],b[1],b[1],b[1],b[1],0])
        zb.extend([0,0,0,0,0,b[2],b[2],0,b[2],b[2],0,b[2],b[2],0,b[2],b[2]])
        cb.extend(16*[i])

    fig = go.Figure()
    point_size, line_width = 4, 6
    # Add objects (points)
    fig.add_trace(go.Scatter3d(x=OBJECTS[:,0], y=OBJECTS[:,1], z=OBJECTS[:,2],
                        mode='markers',
                        name='objects',
                        marker=dict(color=co, size=point_size)))
    # Add boxes (lines)
    fig.add_trace(go.Scatter3d(x=xb, y=yb, z=zb,
                        mode='lines',
                        name='boxes',
                        line=dict(color=cb, width=line_width)))

    fig.show()
    #fig.write_html("eee.html")
    
    

### FUNCIONS AUXILIARS ###

def predict(obj, box_sizes):
    # Input: objecte (mides) i mides de caixes (llista de mides)
    # Output: id de la caixa assignada (minimitza empty space) 
    
    min_space = float("inf")
    assigned_box = None

    for box_id, box in enumerate(box_sizes):

        space = np.prod(box)

        if fits(obj,box) and space < min_space:
            min_space = space
            assigned_box = box_id

    return assigned_box
