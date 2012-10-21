# -*- coding: utf-8 -*-

import numpy as n
import random as r
import pylab as p
import copy
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.cm as cm

#from cluster import kmeans, Point

# Parameters ##################################################################

# how many cities?
CITIES = 25
# max number of generations
GENERATIONS = 200
# total population size
POP_SIZE = 200
# crossover and mutation rate
CROSSOVER_RATE = 1.0
MUTATION_RATE = 0.3
# how many neighbors to change in each cluster?
TO_CHANGE_RATE = 0.1
# how many representatives to vote on? (=K in Kmeans)
NUM_REPRESENTATIVES = 20
# dna: [ ELITE_RATE | OP_RATE | RANDOM ]
ELITE_RATE = 0.2
OP_RATE = 0.4
# abertura da gaussiana
SIGMA = .12

# Operators ###################################################################

def crossover(i_mom, i_dad):
    """ Crossover by edge recombination. Based on
    http://en.wikipedia.org/wiki/Edge_recombination_operator and Pyevolve's
    Crossovers.G1DListCrossoverEdge method
    """
    g_mom = i_mom.copy()
    g_dad = i_dad.copy()
    sisterl = []
    brotherl = []

    def get_edges(ind):
        edg = {}
        ind_list = ind['dna']
        
        for i in xrange(len(ind_list)):
            a, b = ind_list[i], ind_list[i-1]
            if a not in edg:
                edg[a] = []
            else:
                edg[a].append(b)
            if b not in edg:
                edg[b] = []
            else:
                edg[b].append(a)
        return edg
    
    def merge_edges(edge_a, edge_b):
        edges = {}
        for value, near in edge_a.items():
            for adj in near:
                if (value in edge_b) and (adj in edge_b[value]):
                    edges.setdefault(value, []).append(adj)
        return edges
    
    def get_edges_composite(mom, dad):
        mom_edges = get_edges(mom)
        dad_edges = get_edges(dad)
        return (mom_edges, dad_edges, merge_edges(mom_edges, dad_edges))
    
    mom_edges, dad_edges, merged_edges = get_edges_composite(g_mom, g_dad)

    for c, u in (sisterl, set(g_mom['dna'])), (brotherl, set(g_dad['dna'])):
        curr = None
        for i in xrange(len(g_mom['dna'])):
            curr = r.choice(tuple(u)) if not curr else curr
            c.append(curr)
            u.remove(curr)
            d = [v for v in merged_edges.get(curr, []) if v in u]
            if d:
                curr = r.choice(d)
            else:
                s = [v for v in mom_edges.get(curr, []) if v in u]
                s += [v for v in dad_edges.get(curr, []) if v in u]
                curr = r.choice(s) if s else None
    # garante que sempre haverá um 0 no início do dna
    pos0sister = sisterl.index(0)
    sisterl[pos0sister] = sisterl[0]
    sisterl[0] = 0
    pos0brother = brotherl.index(0)
    brotherl[pos0brother] = brotherl[0]
    brotherl[0] = 0
    
    sister = g_mom.copy()
    brother = g_dad.copy()
    sister['dna'] = sisterl
    brother['dna'] = brotherl
    
    return (sister, brother)

def mutate(guy):
    """ Mutation by sublist reversing """
    inicio = r.choice(range(1,len(guy['dna'])-1))
    fim = r.choice(range(inicio, len(guy['dna'])-1))
    # invertemos a ordem dessa sublista
    aux = guy.copy()
    foo = aux['dna'][inicio:fim+1]
    foo.reverse()
    # trocamos a sublista antiga pela invertida
    aux['dna'][inicio:fim+1] = foo[:]
    return aux

def fitness(guy):
    s = guy['score']
    #if s == 0:
    #    return 0.
    return 1. / s

def distances(guy):
    def dist(c1, c2):
        p1 = cities[c1]
        p2 = cities[c2]
        return n.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
        #return n.abs(p2 - p1)

    dists = []
    for i in xrange(len(guy['dna'])-1):
        c1 = guy['dna'][i]
        c2 = guy['dna'][i+1]
        dists.append(dist(c1, c2))
    
    return dists

# def score(guy):
#     """ Scoring based on the sum of distances of all valid paths """
#     return sum(distances(guy))

def score(guy):
    return sum(distances(guy))

    

def new_guy():
    dna = range(1,CITIES)
    r.shuffle(dna)
    
    d = {'dna': [0]+dna,
         'fitness': .0,
         'score': .0,
         'parents': []}
    return d.copy()

# PCA #########################################################################

def pca(data):
    data = n.array(data, dtype=float)
    
    # normalizamos a matriz de dados (X = X - mean) e dividimos pelo d.p.
    #     X = (X - mean) / dp
    for i in xrange(data.shape[1]):
        # adiciono um valor irrisorio 0.001 no denominador para nao
        # dar divisao por zero
        data[:,i] = (data[:,i] - data[:,i].mean())/(data[:,i].std()+0.001)
    
    # calculamos a matriz de covariância de X
    matriz_cov = n.cov(data, bias=1, rowvar=0)
    
    # calculamos os autovetores e autovalores e ordenamos em ordem decresc.
    autovalores, autovetores = n.linalg.eig(matriz_cov)
    args = n.argsort(autovalores)[::-1]
    autovalores = autovalores[args]
    autovetores = autovetores[args]
    
    # calculamos os componentes principais para todos os dados
    dados_finais = n.dot(autovetores.T, data.T)
    principais = dados_finais.T

    #return [principais, autovetores]
    return principais

# City Maps ###################################################################

def ellipse(x, y, a, b, angle, steps):
    """ Returns the points for an ellipse centered in x, y with size a, b """
    beta = -angle * (n.pi / 180)
    sinbeta = n.sin(beta)
    cosbeta = n.cos(beta)

    alpha = n.linspace(0, 360, steps).T * (n.pi / 180)
    sinalpha = n.sin(alpha)
    cosalpha = n.cos(alpha)

    X = x + (a * cosalpha * cosbeta - b * sinalpha * sinbeta)
    Y = y + (a * cosalpha * sinbeta + b * sinalpha * cosbeta)

    ell = []
    for i in xrange(steps):
        ell.append([X[i], Y[i]])

    return n.array(ell)

def random_walk(steps):
    thetas = n.random.uniform(0, 2*p.pi, steps)

    real = [n.cos(t) for t in thetas]
    imag = [n.sin(t) for t in thetas]

    xs = p.cumsum(real)
    ys = p.cumsum(imag)

    ell = []
    for i in xrange(steps):
        ell.append([xs[i], ys[i]])

    return n.array(ell)

def grid(qtd):
    pontos = []
    for y in range(int(n.sqrt(qtd))):
        for x in range(int(n.sqrt(qtd))):
            pontos.append([x,y])
    return n.array(pontos)

# plota os pontos e as linhas do grid
def plot_grid(coords, chromo, gen, dist, fi):
    p.clf()
    # pontos
    p.axis('off')
    p.xlim((-1.0, 5.0))
    p.ylim((-1.0, 5.0))
    p.plot(coords[:,0], coords[:,1], 'ro')
    # linhas
    for i in range(len(chromo)-1):
        c1 = coords[chromo[i]]
        c2 = coords[chromo[i+1]]
        p.plot([c1[0], c2[0]], [c1[1], c2[1]], 'b-')
    p.title('fitness: ' + str(fi) + '. metric: ' + str(dist))
    p.savefig("anim/grid" + str(gen))
    

###############################################################################
# Main loop ###################################################################
###############################################################################

num_elite = int(POP_SIZE * ELITE_RATE)
num_op = int(POP_SIZE * OP_RATE)
num_rand = int(POP_SIZE - num_elite - num_op)

#cities = ellipse(0, 0, 1, 1, 0, CITIES+1)
cities = grid(CITIES)
#cities = random_walk(CITIES)
metrics = []
fits = []
scores = []
clusters = []
FIT_APROX_MAIOR = 0
FIT_MAIOR = 0
# inicializa a população com novos indivíduos aleatórios
pops = []
pop = []
for i in xrange(POP_SIZE):
    pop.append(new_guy())

for generation in xrange(GENERATIONS):
    # copia a elite ('num_elite' primeiros) para a nova população
    elite = []
    new_pop = []

    for i in xrange(num_elite):
        elite.append(copy.deepcopy(pop[i]))
        new_pop.append(copy.deepcopy(pop[i]))

    # aplica operadores de crossover e mutação apenas na elite, criando novos
    for i in xrange(num_op/2):
        # crossover: aplicado a dois elementos da elite, escolhidos ao acaso
        mom = r.choice(elite)
        dad = r.choice(elite)
        sis = None
        bro = None
        if r.random() < CROSSOVER_RATE:
            (sis, bro) = crossover(mom, dad)
        else:
            sis = copy.deepcopy(mom)
            bro = copy.deepcopy(dad)

        # mutation
        if r.random() < MUTATION_RATE:
            sis = mutate(sis)
            bro = mutate(bro)

        # store parents
        #sis['parents'] = [dad, mom]
        #bro['parents'] = [mom, dad]
        
        # store new guys in the new pop
        new_pop.append(sis)
        new_pop.append(bro)

    # o restante de new pop é obtido criando-se novos aleatórios
    for i in xrange(num_rand):
        ne = new_guy()
        new_pop.append(ne)

    # calcula o custo de cada indivíduo
    for i in xrange(POP_SIZE):
        sc = score(new_pop[i])
        new_pop[i]['score'] = sc

    # atualiza o fitness de cada indivíduo
    for i in xrange(POP_SIZE):
        fi = fitness(new_pop[i])
        new_pop[i]['fitness'] = fi

    # sobrescreve a população antiga pela nova
    pop = new_pop[:]

    pop.sort(key=lambda x: x['fitness'], reverse=True)
    #pop.sort(key=lambda x: x['score'])

    # apenas analisa a dialética

    if generation == 10:
        # protótipo 1, zigue-zague
        ia = new_guy()
        ia['dna'] = [0,1,2,3,4,9,8,7,6,5,10,11,12,13,
                     14,19,18,17,16,15,20,21,22,23,24]
        a = n.array(ia['dna'], dtype=float)
        # protótipo 2, espiral
        ib = new_guy()
        ib['dna'] = [0,1,2,3,4,9,14,19,24,23,22,21,20,
                     15,10,5,6,7,8,13,18,17,16,11,12]
        b = n.array(ib['dna'], dtype=float)
        # síntese (o melhor da geração)
        _metrics = []
        bar = 0
        for foo in pop:
            c = n.array(foo['dna'], dtype=float)
            
            t1 = n.sum((b-a)*c)
            t2 = n.sum(-((b**2 - a**2)/2))
            t3 = n.sum((b-a)**2)
            dist = n.abs(t1 + t2) / n.sqrt(t3)
            
            _metrics.append(dist)

            plot_grid(cities, foo['dna'], bar, dist, fitness(foo))

            bar += 1
        p.clf()
        x = range(len(pop))
        metrics = n.array(_metrics)
        fits = n.array([fitness(foo) for foo in pop])
        p.plot(x, metrics / metrics.max())
        p.plot(x, fits / fits.max())
        p.legend(('Metric', 'Fitness'), 'best')
        p.savefig('anim/meg.png')


    pops.append({'generation': generation,
                 #'pop': pop,
                 #'clusters': clusters,
                 #'best': pop[0],
                 #'best fitness': pop[0]['fitness'],
                 'fitness real max': FIT_MAIOR,
                 'fitness avg': sum([x['fitness'] for x in pop]) / len(pop),
                 'fitness min': min([x['fitness'] for x in pop]),
                 'fitness max': max([x['fitness'] for x in pop])})

    print 'generation:             ', generation
    print 'best                    ', pop[0]['dna']
    print 'fitness                 ', fitness(pop[0])
    #print 'best fitness:           ', pop[0]['fitness']
    #print 'max fitness:            ', max([x['fitness'] for x in pop])

    # print 'maior fitness encontrado (real)', FIT_MAIOR
    # FIT_APROX_MAIOR = max([x['fitness'] for x in pop])
    # print 'max fitness (aprox)', FIT_APROX_MAIOR

p.figure()

#p.subplot(1,2,1)
# x = []
# yavg = []
# ymin = []
# ymax = []
# for po in pops:
#     x.append(po['generation'])
#     yavg.append(po['fitness avg'])
#     ymin.append(po['fitness min'])
#     ymax.append(po['fitness max'])

# p.plot(x, ymin, 'g-')
# p.plot(x, ymax, 'r-')
# p.plot(x, yavg, '-')
# p.xlabel('Generation')
# p.ylabel('Fitness Min/Avg/Max')
# p.title('Fitness (aprox.)')
# p.grid(True)

# p.subplot(1,2,2)
# x = []
# yreal = []
# for po in pops:
#     x.append(po['generation'])
#     yreal.append(po['fitness real max'])

# p.plot(x, yreal, '--')
# p.xlabel('Generation')
# p.ylabel('Real Fitness')
# p.title('Fitness (real)')
# p.grid(True)
#p.savefig('anim/me' + str(generation) + '.png')

x = range(GENERATIONS)
metrics = n.array(metrics)
fits = n.array(fits)
p.plot(x, metrics / metrics.max())
p.plot(x, fits / fits.max())
#p.plot(x, scores)
print metrics / metrics.max()
print fits
p.legend(('Metric', 'Fitness'), 'best')
p.savefig('anim/me.png')

#plot_grid(cities, pop[0]['dna'])
