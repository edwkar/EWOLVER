import math
import time
from izhikevich import *

def dist(a, b):
    v = []
    for pn in PARAM_SEQ:
        rlow, rhigh = PARAM_RANGES[pn]
        ua = range_to_unit(a.params[pn], rlow, rhigh)
        ub = range_to_unit(b.params[pn], rlow, rhigh)
        v.append((ua-ub)**2)
    res = math.sqrt(sum(v))
    assert res <= math.sqrt(5)
    return res



res_str = ''

for ref_file in ['data/izzy-train1.dat',
        'data/izzy-train2.dat', 'data/izzy-train3.dat',
        'data/izzy-train4.dat']:
    for diff_measure in ['spike-time', 'spike-interval', 'waveform']:
        res = []
        for k in range(5):
            print ref_file, diff_measure, k
            rng = random.Random(seeder.randint(0, 80000))
            res.append(run_experiment(
                ref_file,
                diff_measure,
                rng,
                num_generations=250,
                _adult_pop_size=100,
                _parent_pop_size=170,
                _crossover_rate=0.6,
                _mutation_rate=0.06,
                _batch_mode=True
            ))

        res.sort(lambda a, b: cmp(b.fitness, a.fitness))
        res_str += r'{ \footnotesize' '\n'
        res_str += r'\textsc{%s - %s} \\' % (ref_file.replace('data/', '')
                                                     .replace('.dat', '').upper(),
                                                diff_measure.replace('-', ' ').upper(),)
        res_str += '\n'

        res_str += r'\begin{tabular}{c|c|c|c|c|c||c}' '\n'
        res_str += r'\textbf{\#} & \textbf{a} & \textbf{b} & \textbf{c} & ' '\n'
        res_str += r'  \textbf{d} & \textbf{k} & \textbf{Fitness} \\ \hline' '\n'
        for i, p in enumerate(res, start=1):
            res_str += ((r'%d & %.3f & %.3f & %.3f & %.3f & %.3f &'
                         r'\textbf{%.3f} \\ \hline') % (
                           i,
                           p.params['a'],
                           p.params['b'],
                           p.params['c'],
                           p.params['d'],
                           p.params['k'],
                           p.fitness,))
            res_str += '\n'
        res_str += r'\end{tabular}' '\n'
        res_str += r'}\\' '\n'

        dists = [dist(a, b) for a in res for b in res]
        res_str += r'\textsc{MAX-SOL-SPACE DIAMETER:} %.4f \\' % max(dists)
        res_str += '\n\n'

print res_str
