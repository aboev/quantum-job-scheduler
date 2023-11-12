import numpy as np
from pulp import *

from dwave.system.samplers import DWaveSampler
from dwave.system.composites import EmbeddingComposite

def solve_qubo(Q, engine = "pulp", **kwargs):
  if engine == "pulp":
    model = LpProblem("QUBO", LpMinimize)
    size = len(Q)
    x = pulp.LpVariable.dicts("spins", (i for i in range(size)),
      lowBound=0, cat='Binary')
    y = pulp.LpVariable.dicts("couplings",
      ((i, j) for i in range(size) for j in range(size)),
      lowBound=0, cat='Binary')

    obj1 = 0
    obj2 = 0
    for i in range(size):
      for j in range(size):
        if i != j:
          model += y[i,j] >= x[i] + x[j] - 1
          model += y[i,j] <= x[i]
          model += y[i,j] <= x[j]
          obj1 += Q[i,j] * y[i,j]
        else:
          obj2 += Q[i,j] * x[i]
    model += lpSum([obj1, obj2])
    model.solve()

    total_cost = value(model.objective)
    print ('min cost:',total_cost)
    result_vec = [0] * size
    for i in range(size):
      result_vec[i] = x[i].varValue
    print(result_vec)
    return result_vec, result_vec @ Q @ result_vec
  elif engine == "bruteforce":
    min_vec = [0] * len(Q)
    min_energy = min_vec @ Q @ min_vec
    for i in range(2**len(Q)):
      x = list(map(int,('{0:0%db}'%(len(Q))).format(i)))
      e = np.dot(x, np.dot(Q, x))
      if e < min_energy:
        min_energy = e
        min_vec = x
    print(min_vec)
    return min_vec, min_energy
  elif engine == "dwave":
    q = {}
    size = len(Q)
    for i in range(size):
        for j in range(size):
            q[(i,j)] = Q[i][j]
            
    sampler = EmbeddingComposite(DWaveSampler(token=kwargs["API_KEY"]))
    response = sampler.sample_qubo(q, num_reads=200)

    min_energy = np.inf
    min_spins = None
    for sample, energy in response.data(['sample', 'energy']): 
        if energy < min_energy:
          min_spins = sample
          min_energy = energy
    
    return [min_spins[i] for i in range(len(min_spins))], min_energy
