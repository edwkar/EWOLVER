# vim: ts=4:sw=4


import random
from izhikevich import *


def main():
    print 3


N = BITS_PER_GENE * len(PARAM_SEQ)

import plotting
evaluator = NeuronFitnessEvaluator('data/izzy-train2.dat', 'spike-time')
lst = plotting.setup_live_plotting_listener(evaluator.ref_potentials,
        evaluator.ref_spike_times)

def search():
    rng = random.Random()

    def eval_ft(*ps):
        for p, f in zip(ps, evaluator.fitness_many(ps)):
            p.fitness = f

    genotype_factory = RealVectorGenotype.factory_for_length(len(PARAM_SEQ))
    dev = NeuronDevMethod().develop_phenotype_from

    v = None
    while v is None or len(v.spike_times) < 3:
        v = dev(genotype_factory(0, rng))
    eval_ft(v)

    explored = set([str(v)])

    last_change_t = 0
    for k in range(500):
        print '          ', v, v.fitness, last_change_t
        if k-last_change_t == 60:
            break

        explored.add(str(v))
        neighbors = []
        for i in range(len(PARAM_SEQ)):
            w = 0
            effort = 0
            while w < 20 or effort < 20:
                alt_data = v.genotype.data[:]
                alt_data[i] += rng.gauss(0, rng.choice([1E-6, 1E-4, 0.1, 0.5, 0.01, .8]))
                alt_data[i] = max(0, min(alt_data[i], 1))
                p = dev(BitVectorGenotype(v.birth_generation+1, alt_data))
                if not str(p) in explored:
                    neighbors.append(p)
                    w += 1
                effort += 1
        if not neighbors:
            break

        eval_ft(*neighbors)
        bestp = v if rng.random() < .9 else neighbors[0]
        for neighbor in neighbors:
            if neighbor.fitness <= bestp.fitness:
                bestp = neighbor
        if bestp.params != v.params:
            last_change_t = k
            v = bestp
        lst.after_adult_sieving([v])


    return v


import time
best = None
for k in range(200):
    v = search()
    if best is None or v.fitness < best.fitness:
        best = v
    print
    print best, best.fitness, len(best.spike_times)
    print best, best.fitness, len(best.spike_times)
    print best, best.fitness, len(best.spike_times)
    print
