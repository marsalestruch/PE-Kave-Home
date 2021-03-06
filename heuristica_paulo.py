"""
EXPLICACIÓ DE LA HEURÍSTICA: basada en quantils

El primer de tot és tenir la llista d'objectes ordenada per diagonal (la llista
obj_quants igualment ordenada). Després es calculen els quantils segons el nombre
de caixes que es seleccioni. Diuem 'quantils' als indexos dels objectes que
marquen cada quantil (tenint en compte les quantitats de cada objecte).

    · GEBERACIÓ DE SOLUCIONS
L'algorisme genera solucions a partir de la llista de quantils. El que fa és
"desplaçar" cada quantil (index d'objete) endavant o enrere i crear noves solucions.
Millor veure-ho en un exemple: si tenim 30 objectes i 4 caixes i els quantils
son [8,15,24,29] (l'ultim quantil sempre és l'index de l'últim objecte).
Tindrem: l'index 8 el podrem moure en el rang [0,11]. L'index 15 entre [12,19],
l'index 24 entre [20,28]. És a dir, mai un index avança al seu posterior. Es
calculen els punts migs d'un index i els seus veins (esquerra i dreta), per a
limitar el rang de "desplaçament" (shift). Per exemple:

Si tenim tres indexos consecutius [...,13,18,31,...] i ens fixem en el 18. Per
l'esquerra es podrá moure 2 posicions fins el 16 (ja que el 13 podrà moure's 2
posicions cap a la dreta fins el 15, no volem que xoquin) i el 18 cap a la dreta
es podrá moure 6 (resultat de (31-18)//2). És a dir, el 18 es mourà entre els
indexos [16,24]. OBS// Per a abarcar tot l'espai de cerca, el primer index sempre
és podrà moure fins el 0 cap a l'esquerra, l'últim index no es mou mai, el
penultim podrà moures cap a la dreta fins l'index 'ultim-1'.

    · CALCUL MIDES DE CAIXES
Un cop generada aquesta llista d'indexos (de nom 'limit_obj_idxs', es calculen
les mides de les caixes. Si la llista és L = [0,5,11,19]. La primera caixa
tindrà els objectes [0,4], la segona caixa els objectes [5,10], i la última els
objectes [11,19]. És a dir, la caixa[i] contindrà els objectes entre L[i] (inclòs)
i L[i+1] (no inclòs, a execpció de l'últim index que sí s'inclou).

    · MUTACIONS
Amb certa probabilitat o quan portem moltes iteracions sense millorar la solució,
es farà una "mutació". Consisteix basicament en permutar una mica l'ordre dels
objectes. Es defineix una mida de finestra (w=5 per defecte) i cada 'w' objectes,
els permutem. Això ajuda a l'algorisme a explorar noves opcions.


No sé si s'acaba de entendre, segurament la explicació és una mica incompleta.
"""


import numpy as np
import time
import pandas as pd
import plotly.graph_objs as go


def diagonal(x):
    """
    :param x: (x1,x2,x3). mides de caixa o objecte
    :return: quadrat de la diagonal de x
    """
    diag2 = 0
    for xi in x:
        diag2 += xi*xi
    return diag2


def fits(obj, box):
    """
    :param obj: (x1,x2,x3) mides d'un objecte
    :param box: (x1,x2,x3) mides d'una caixa
    :return: (bool) True si obj cap dins box
    """
    b = True
    for oi, bi in zip(obj, box):
        b = b and oi<=bi
    return b


def total_space_obj(objects, obj_quants):
    """
    :param objects: llista de mides (x1,x2,x3) d'objectes
    :param obj_quants: llista de quantitats d'objecte.
    :return: suma de tot el volum total d'objectes.
    """
    return sum( [q*np.prod(obj) for q, obj in zip(obj_quants, objects)] )


def total_space_box(box_sizes, obj2box, obj_quants):
    """
    :param box_sizes: llista de mides (x1,x2,x3) de caixes
    :param obj2box: mapeja obj_id -> box_id (caixa assignada per cada objecte)
    :param obj_quants: llista de quantitats d'objectes
    :return: suma de tot el volum total de caixes.
    """
    space = 0
    assert len(obj2box) == len(obj_quants)
    for box_id, obj_quant in zip(obj2box, obj_quants):
        box_space = np.prod([box_sizes[box_id]])
        space += obj_quant * box_space
    return space


def predict(obj, box_sizes):
    """
    Criteri: caixa que minimitza el % volum desaprofitat
    :param obj: (x1,x2,x3) d'un objecte
    :param box_sizes: llista de mides de caixes
    :return: box_id de la caixa assignada a l'objecte
    """
    min_space = float("inf")
    assigned_box = None
    for box_id, box in enumerate(box_sizes):
        space = np.prod(box)
        if fits(obj,box) and space < min_space:
            min_space = space
            assigned_box = box_id
    assert assigned_box is not None
    return assigned_box


def init_objects(num_objects, dim=3, min_val=10, max_val=100, min_quant=1, max_quant=10):

    #Intenta crear una distribució no-uniforme, per a crear "clusters"
    o1 = np.random.randint(min_val, min_val+(max_val-min_val)//4, size=(num_objects*3//7 * dim))
    o2 = np.random.randint(max_val//4, min_val+(max_val-min_val)*3//4, size=(num_objects//7 * dim))
    o3 = np.random.randint(max_val*3//4, max_val, size=(dim*num_objects-len(o1)-len(o2)))

    objects = np.concatenate([o1,o2,o3])  #len == num_objects*dim
    #np.random.shuffle(objects)   #si s'executa, es desfan els clusters

    objects = objects.reshape((num_objects, dim))
    objects.sort()  #ordena les mesures de cada objecte asc.
    objects = np.array( sorted(objects, key=lambda obj: diagonal(obj) ), dtype=int )  #ordenem per diagonals (ascending)

    # definim el nombre d'unitats de cada objecte entre min_quant i max_quant
    quantities = np.random.randint(min_quant, max_quant+1, num_objects)
    return objects, quantities


def compute_impact(objects, obj_quants, obj2box, box_sizes):
    """
    Kave Home ens ha donat l'area de la bossa plana, però no ens ha dit el volum
    directament. Tocarà "inferir"-lo. Les dimensions planes de les bosses son
    30x13 cm.
    De moment assumim que la bossa s'aproxima com un "cilindre". Usar les mides
    30cm de llarg i 13 de diametre donaria un volum massa alt respecte la realitat
    Per tant multiplicarem el resultat per un factor de 0.7, indicant com si la
    bossa ocupés un 80% del volum del cilindre que hem aproximat.

    :param objects: llista de mides d'objectes (x1,x2,x3)
    :param obj_quants: llista de quantitats de cada objecte
    :param obj2box: mapeja cada obj_id al box_id de la caixa que se li assigna
    :param box_sizes: llista de mides de caixes (x1,x2,x3)
    :return: nombre de bosses necessaries per omplir espai buit, cost total [€]
    """

    # TODO estaria guai poder dir "gast anual o mensual". Falta el temps.
    # D'alguna manera caldria poder dir el "temps" de la llista d'objectes.
    # Potser podriem recorrer una llista de commandes d'una setmana o un mes
    # (mirant el timestamp, encara que no sigui actual), predir per a cada
    # objecte la caixa i calcular el gasto setmanal o mensual en caixes
    # (i també caldria comparar els resultats amb un BASELINE). Idealment amb
    # les caixes de Kave però sino amb un nostre

    preu_bobina = 207.92  #euros
    cm_bobina = 128000  #centimetres (1280 metres)

    L = 30  #longitud del cilindre en cm
    r = 6.5  #radi del cilindre en cm
    volum_bossa = L * r*r * 3.1416  #volum d'un cilindre = π·r²·h [cm³]
    volum_bossa *= 0.8   #suposem que la bossa ocupa un X% del cilindre

    num_bosses = 0

    for obj_id in range(len(objects)):

        obj = objects[obj_id]
        quant = obj_quants[obj_id]

        # Calcul del espai que queda buit
        obj_space = np.prod(obj)
        box_id = obj2box[obj_id]
        box_space = np.prod( box_sizes[box_id])
        empty_space = box_space - obj_space

        # No volen omplir tot l'espai buit, només fer bulto, és a dir, només un %
        empty_space = int(empty_space * 0.6)

        num_bosses += empty_space // volum_bossa

    preu_bossa = (preu_bobina / cm_bobina) * 2*r
    cost_total = num_bosses * preu_bossa


    return int(num_bosses), round(cost_total, 2)


def display_results(objects, obj_quants, obj2box, best_sizes):

    best_space = total_space_box(best_sizes, obj2box, obj_quants)
    total_obj_space = total_space_obj(objects, obj_quants)
    num_boxes, num_objects = len(best_sizes), obj_quants.sum()
    print()
    print("####   BEST SOLUTION   ####")
    print(f"Num objects = {sum(obj_quants)}")
    print("BEST_SIZES = ", best_sizes[:5])
    print("Filled Space[%] = ", round(total_obj_space/best_space*100, 2),"%")
    num_bosses, cost = compute_impact(objects, obj_quants, obj2box, best_sizes)
    ratio = num_bosses/num_objects
    print(f"#Airbags= {num_bosses};  airbags/object = {ratio};  ", end="")
    print(f"total cost = {cost}€")
    unused_boxes = sum([(box==(0,0,0)).all() for box in best_sizes])
    print("Unused boxes = {} ({})".format(unused_boxes, num_boxes))
    box_quants = np.bincount(obj2box)
    print(f"Min box_quants = {min(box_quants)};  Max box_quants = {max(box_quants)}.")
    more = False
    if more:
        print("####                   ####")
        for i in range(num_boxes):
            print("box", i, ":", int(box_quants[i]), "objects;   size = ", best_sizes[i])


    print("####       ####        ####")


def plot_results(objects, box_sizes, obj2box, save_plot=False):

    co = [obj2box[o] for o in range(len(objects))]  #object colors
    xb, yb, zb, cb = [], [], [], []  #box sizes + box colors
    for i, b in enumerate(box_sizes):
            xb.extend([0,b[0],b[0],0,0,0,b[0],b[0],b[0],b[0],b[0],b[0],0,0,0,0])
            yb.extend([0,0,b[1],b[1],0,0,0,0,0,b[1],b[1],b[1],b[1],b[1],b[1],0])
            zb.extend([0,0,0,0,0,b[2],b[2],0,b[2],b[2],0,b[2],b[2],0,b[2],b[2]])
            cb.extend(16*[i])

    fig = go.Figure()
    point_size, line_width = 4, 6
    # Add objects (points)
    fig.add_trace(go.Scatter3d(x=objects[:,0], y=objects[:,1], z=objects[:,2],
                               mode='markers', name='objects',
                               marker=dict(color=co, size=point_size)))
    # Add boxes
    fig.add_trace(go.Scatter3d(x=xb, y=yb, z=zb, mode='lines', name='boxes',
                               line=dict(color=cb, width=line_width)))

    fig.show()

    if save_plot:
        fig.write_html("eee.html")


def compute_obj2box(objects, box_sizes):
    """
    obj2box es el que abans era box_assignment
    :param objects: llista d'objectes (x1,x2,x3)
    :param box_sizes: llista de caixes (x1,x2,x3)
    :return: array tal que obj2box[obj_id] = box_id que se li assigna
    """

    undef = -1
    obj2box = np.full(len(objects), undef)

    for obj_id, obj in enumerate(objects):
        box_id = predict(obj, box_sizes)
        obj2box[obj_id] = box_id

    assert not any([b==undef for b in obj2box])
    return obj2box


def compute_quantiles_idxs(obj_quants, num_boxes):
    """
    :param obj_quants: llista de quantitas de cada objecte
    :param num_boxes: nombre de caixes (int)
    :return: llista d'indexos d'objectes que formen tants quantils com 'num_boxes'
    Seran la base de la solució inicial de l'algorisme. Només es calculen un cop.
    """

    num_objects = obj_quants.sum()
    quantiles = [ (q*num_objects)//num_boxes for q in range(1, num_boxes+1) ]

    # primer calculem els quantils sobre el nombre total d'objectes (tenint en
    # compte les quantitats). Després caldrà passar aquests resultats als
    # indexos de la llista 'objectes' (és a dir, a quantils de la llista
    # d'objectes). El resultat bo és 'quantiles_idxs'

    quantiles_idxs = np.zeros(num_boxes, dtype=int)
    q_idx = 0  # recorre 'quantiles'
    accum_obj_quant = 0  #suma acumulada de quantitat total d'objectes.

    # Volem saber quin obj_id de la llista OBJECTS és cada quantil
    for obj_id, obj_quant in enumerate(obj_quants):
        accum_obj_quant += obj_quant
        if accum_obj_quant >= quantiles[q_idx]:
            quantiles_idxs[q_idx] = obj_id
            q_idx += 1

    return quantiles_idxs


def run_validations(limit_obj_idxs, box_sizes, obj2box, objects):
    #Executa validacions bàsiques de les variables més importants
    # Es només per a comprovar que no hi ha cap incoherencia en la solució
    # Gasta més temps, quan es comprovi que tot funciona bé es pot comentar
    # la crida d'aquesta funció en el ComputeSizes.

    # La funció no retorna res, però petarà si no es compleixen les validacions

    #######################################
    ###  Validacions de límit_obj_idxs  ###
    #######################################
    val_1 = []
    # té longitud num_boxes + 1 (ja que incorpora el primer 0)
    val_1.append( len(limit_obj_idxs) == len(box_sizes) + 1 )
    # primer element és 0
    val_1.append( limit_obj_idxs[0] == 0 )
    # últim element és l'index de l'últim objecte
    val_1.append( limit_obj_idxs[-1] == len(obj2box) - 1 )
    # hauria d'está ordenat
    val_1.append( all(sorted(limit_obj_idxs) == limit_obj_idxs) )

    if not all(val_1):
        print("val_1 = ", val_1)
        print("limit_obj_idxs = ", limit_obj_idxs)
        raise Exception("limit_obj_idxs NO és vàlid.")


    ##################################
    ###  Validacions de box_sizes  ###
    ##################################
    val_2 = []
    # es una llista de tripletes
    val_2.append( all([len(b)==3 for b in box_sizes]) )
    # llista de caixes ordenades per diagonal
    val_2.append( (sorted(box_sizes, key=lambda b: diagonal(b)) == box_sizes).all() )
    # mides de cada caixa ordenades ascendentment (i no nules)
    val_2.append( all([0<=x1<=x2<=x3 for x1,x2,x3 in box_sizes]) )

    if not all(val_2):
        print("val_2 = ", val_2)
        print("box_sizes = ", box_sizes)
        raise Exception("box_sizes NO és vàlid.")

    ################################
    ###  Validacions de obj2box  ###
    ################################
    val_3 = []

    # valor mínim és 0 i valor máxim és num_boxes-1
    val_3.append(obj2box.min()==0 and obj2box.max()==len(box_sizes)-1)
    # qualsevol objecte cab a la caixa que se li ha assignat
    all_fits = True
    for obj, box_id in zip(objects, obj2box):
        all_fits &= fits(obj, box_sizes[box_id])
    val_3.append(all_fits)

    if not all(val_3):
        print("val_3 = ", val_3)
        if not all_fits:
            print("box_quants = ", np.bincount(obj2box))
        raise Exception("obj2box NO és vàlid.")


def compute_box_sizes(objects, limit_obj_idxs):
    """
    Al principi hi ha més info sobre com es calculen les caixes a partir de
    la variable limit_obj_idxs.

    :param objects: llista de mides (x1,x2,x3) d'objectes
    :param limit_obj_idxs: llista de límits d'obj_id per calcular mides de caixes
    :return: llista amb les mides (x1,x2,x3) de totes les caixes
    """

    dim = len(objects[0])
    num_boxes = len(limit_obj_idxs) - 1
    box_sizes = np.zeros((num_boxes, dim), dtype=int)

    for box_id in range(num_boxes):
        start = limit_obj_idxs[box_id]
        end = limit_obj_idxs[box_id+1]
        if box_id == num_boxes-1:
            end += 1  #inclou ultim objecte
        box_sizes[box_id] = np.max(objects[start:end], axis=0)

    # retorna les caixes ordenades per diagonal (no es imprescindible)
    box_sizes = np.array( sorted(box_sizes, key=lambda box: diagonal(box) ), dtype=int )
    return box_sizes


def compute_shift_probs(quantiles):
    """
    Aquesta funció es bastant fumada, però al final sembla que funciona.
    Sembla poc eficient però només s'executa un cop.

    L'objectiu és crear una variable que tingui tota la informació necessaria
    sobre els quantils, per a generar solucions fent els desplaçaments dels
    indexos (tal i com s'explica al principi de tot).

    :param quantiles: llista d'indexos d'objectes que defineixen cada quantil.
    :return: diccionari shift_probs. Hi ha una key per cada valor de cada quantil.
    El value de cada key es un altre diccionari de keys 'shifts' i 'probs'. Els
    values respectius son la llista de valors de 'shifts' per al quantil donat,
    i les probabilitats de cada shift de la llista anterior.
    """

    # Per a cada quantil (index) guardem el maxim desplaçament que pot fer tant
    # a esquerra com a dreta.  min_max_shifts[q_i] = (left_dist, right_dist)
    # left_dist sempre és negatiu ja que tira cap a l'esquerre
    min_max_shifts = []
    Q = len(quantiles)
    for i in range(Q):

        if i == 0:
            #primer index pot arribar per l'esquerra fins el 0 (primer objecte)
            left_dist = -quantiles[0]
            right_dist = (quantiles[i+1] - quantiles[i]) // 2
        elif i == Q-2:
            #penultim objecte es pot moure cap a la dreta fins l'ultim objecte
            left_dist = -(quantiles[i] - quantiles[i-1]) // 2
            right_dist = quantiles[i+1] - quantiles[i]
        elif i == Q-1:  #l'ultim objecte no es mou mai, sempre es ultim quantil
            left_dist, right_dist = 0, 0
        else:  # la resta d'objectes entre mig (ni primer, ni dos ultims)
            left_dist = -(quantiles[i] - quantiles[i-1]) // 2
            right_dist = (quantiles[i+1] - quantiles[i]) // 2

        min_max_shifts.append( (left_dist, right_dist) )

    # Aquesta es la variable que es retorna, un diccionari amb tota la informació.
    shift_probs = {}
    for i in range(len(quantiles)):

        left_dist, right_dist = min_max_shifts[i]
        len_range = right_dist - left_dist + 1

        #calcul del denominador. Pensat per a que les probabilitats sumin 1
        denom = (right_dist * (right_dist+1) ) // 2
        denom += (abs(left_dist) * (abs(left_dist)+1) ) // 2

        probs = np.zeros(len_range)
        # Omplim les posicións de l'equerra amb les seves probabilitats
        for l in range(left_dist, 0):
            probs[l+abs(left_dist)] = (abs(left_dist)+l)/denom

        # Omplim les posicións de la dreta amb les seves probabilitats
        for r in range(0+1, right_dist+1):
            probs[abs(left_dist)+r] = (right_dist-r)/denom

        # Omplim la posició central (el propi quantil) amb el que hagi sobrat.
        probs[abs(left_dist)] = 1 - probs.sum()

        # comprova que totes les probs son positives i que sumen 1
        assert not (probs < 0).sum()
        assert abs(1 - probs.sum()) < 1e-5

        # per cada quantil, guardem els seus 'shifts' possibles i les 'probs'
        shift_probs[quantiles[i]] = {}
        shift_probs[quantiles[i]]['probs'] = probs
        shift_probs[quantiles[i]]['shifts'] = list(range(left_dist,right_dist+1))

    return shift_probs


def generate_limit_obj_idxs(shift_probs):
    """
    Calcula una solució a partir de tota la informació de shift_probs
    on 'solució' = llista d'indexos d'objectes que definiran les caixes.
    La funció té una component aleatoria

    :param shift_probs: diccionari amb tota la informació sobre quantils i shifts
    :return: llista de indexos d'objectes que defineixes les caixes (una solució)
    """
    num_boxes = len(shift_probs)
    limit_obj_idxs = np.zeros(num_boxes+1, dtype=int)

    for i, quantile in enumerate(shift_probs.keys()):
        probs = shift_probs[quantile]['probs']
        shifts = shift_probs[quantile]['shifts']
        quantile_shift = np.random.choice(a=shifts, size=1, p=probs)
        limit_obj_idxs[i+1] = quantile + quantile_shift

    return limit_obj_idxs


def create_mutation(objects, obj_quants, w=5):
    """
    Cada 'w' objectes, els permutem per a variar una mica l'ordre.

    :param objects: llista de mides d'objectes (x1,x2,x3).
    :param obj_quants: llista de quantitats de cada objecte
    :param w: mida de la finestra per permutar els objectes.
    :return: nous objectes i quantiats amb mutació
    """

    dim = len(objects[0])
    num_objects = len(objects)
    new_objects = np.zeros((num_objects, dim), dtype=int)
    new_quants = np.zeros(num_objects, dtype=int)

    for i in range(0, num_objects, w):
        _w = min(w, num_objects-i-1)
        perm_idxs = np.random.permutation(range(_w))
        object_window = objects[i:(i+_w)]
        quants_window = obj_quants[i:(i+_w)]
        # apliquem la mateixa permutació tant a objects com a obj_quants
        new_objects[i:(i+_w)] = object_window[perm_idxs]
        new_quants[i:(i+_w)]  = quants_window[perm_idxs]


    return new_objects, new_quants


def ComputeSizes(_objects, _obj_quants, num_boxes, num_iter=300,
                 prob_mutation=0.01, mutation_window=5, iters_to_mutation=100):
    """
    Funció principal. Calcula i retorna les mides de les caixes optimes per als
    objectes donats.

    :param _objects: llista de mides d'objectes (x1,x2,x3)
    :param _obj_quants: llista de quantitats de cada objecte.
    :param num_boxes: nombre de caixes (variable segons client)
    :param num_iter: nombre iteracions de l'algorisme (trade-off quality/time)
    :param prob_mutation: probabilitat que en una iteració hi hagi mutació
    :param mutation_window: mida de la finestra de la mutació
    :param iters_to_mutation: nombre d'iteracions sense millora per fer mutació
    :return: millors caixes trobades i millor assignació de caixa cada objecte
    """

    # crea una copia de les variables ja que seran canviades en les mutacions.
    objects = _objects.copy()
    obj_quants = _obj_quants.copy()

    # inicialitza la millor solució trobada, son les variables a retornar
    BEST_SPACE = float('inf')
    BEST_SIZES = None
    BEST_OBJ2BOX = None

    # calcula quantils i la variable shift_probs amb tota la informació sobre els
    # possibles shifts i les seves probabilitats. Aquestes funcions només
    # s'executen un cop
    quantiles_idxs = compute_quantiles_idxs(obj_quants, num_boxes)
    shift_probs = compute_shift_probs(quantiles_idxs)
    OBJECT_SPACE = total_space_obj(objects, obj_quants)

    # quantes iteracions seguides portem sense millorar la solució
    # si arriba a 'iters_to_mutation' fem mutació per a sortir del minim local
    iters_without_improvement = 0

    for ii in range(num_iter):

        if ii%100 == 0:
            print(f"{ii}/{num_iter}")
        # mirem si hi ha MUTACIÓ
        p = np.random.random(1)[0]  #valor entre 0 i 1
        if p < prob_mutation or iters_without_improvement > iters_to_mutation:

            old_space = total_space_obj(objects, obj_quants)

            iters_without_improvement = 0
            objects, obj_quants = create_mutation(_objects,
                                                  _obj_quants,
                                                  mutation_window)

            new_space = total_space_obj(objects, obj_quants)
            if new_space != old_space:
                print(f"new_space - old_space = {new_space-old_space}")
                raise Exception

        # Creem solució a partir de shift_probs, calculem mides de caixes i
        # assignacions (obj2box). Calculem score de la solució (espai)
        limit_obj_idxs = generate_limit_obj_idxs(shift_probs)
        box_sizes = compute_box_sizes(objects, limit_obj_idxs)
        obj2box = compute_obj2box(objects, box_sizes)
        space = total_space_box(box_sizes, obj2box, obj_quants)

        if space < BEST_SPACE:  #millora de la solució

            run_validations(limit_obj_idxs, box_sizes, obj2box, objects)
            iters_without_improvement = 0  #reseteja comptador
            old = round(OBJECT_SPACE/BEST_SPACE*100, 2)
            new = round(OBJECT_SPACE/space*100, 2)
            print(f" · ({ii}) Better solution found: {old}%  -->  {new}%")
            BEST_SPACE = space
            BEST_SIZES = box_sizes.copy()
            BEST_OBJ2BOX = obj2box.copy()

        else:
            iters_without_improvement += 1

    return BEST_SIZES, BEST_OBJ2BOX


def read_csv(file):
    prods = pd.read_csv(file, sep  =',')
    objects = np.array(prods[['Alto', 'Ancho', 'Fondo']])
    objects.sort()

    idx_sorted = sorted(range(len(objects)), key=lambda k: diagonal(objects[k]))
    objects = np.array(objects[idx_sorted], dtype=int)
    quantities = np.array(prods['Quantity'][idx_sorted], dtype=int)

    return objects, quantities

def create_json(file):
    import json

    df = pd.read_csv(file)
    map = {}
    for i in range(len(df)):
        product_id = df.loc[i, "Num de referencia"]
        size = df.loc[i, ["Alto", "Ancho", "Fondo"]].values
        size.sort()
        map[product_id] = size

    y = json.dumps(map)
    print(y)





def main():

    # PARAMETRES (només si dades sintetiques)
    DIM = 3
    MIN_VAL = 10
    MAX_VAL = 100
    NUM_OBJECTS = 500
    MIN_QUANT = 1
    MAX_QUANT = 10
    np.random.seed(1234)

    # PARAMETRES
    NUM_BOXES = 20
    NUM_ITER = 200
    # Mutacions
    PROB_MUT = 0.05   #[0,1]
    WINDOW_MUT = 10
    ITERS_MUT = 150


    #OBJECTS, OBJ_QUANTS = init_objects(NUM_OBJECTS, DIM, MIN_VAL, MAX_VAL, MIN_QUANT, MAX_QUANT)
    OBJECTS, OBJ_QUANTS = read_csv("Packages_Optimization_input.csv")

    ti = time.time()
    BEST_SIZES, BEST_OBJ2BOX = ComputeSizes(OBJECTS, OBJ_QUANTS, NUM_BOXES,
                                            NUM_ITER, PROB_MUT, WINDOW_MUT,
                                            ITERS_MUT)
    tf = time.time()
    print(f"TIME: {round(tf-ti, 2)} seconds;  {NUM_ITER} iterations.")

    display_results(OBJECTS, OBJ_QUANTS, BEST_OBJ2BOX, BEST_SIZES)
    #plot_results(OBJECTS, BEST_SIZES, BEST_OBJ2BOX)


# TODO crear el fitxer json que mapeja object ID -> object size
# TODO crear funció predict que retorni top N caixes, i la metrica de perdua
# la metrica de perdua pot ser tant % espai ocupat, nombre de bosses de plastic
# que caldrà afegir, i potser algo més.

if __name__ == "__main__":
    main()


# fer caixes entre 5 i 20 i fer grafica comparant els diferents % entre
# la nostra approach i el baseline (per volum o per diagonal, el que funcioni
# pitjor.
