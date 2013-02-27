# vim: ts=4:sw=4


import random
import multiprocessing
from subprocess import (Popen, PIPE)
from ewolver.core import *
from ewolver.binary import *
from ewolver.real import *
from ewolver.selection import *
from ewolver.utils.logging import StdoutLogger
from ewolver.utils.math_ import mean as _mean, stddev as _stddev
import plotting


PARAM_RANGES = {
    'a': (0.00001, 0.2),
    'b': (0.00001, 0.3),
    'c': (-80, -30),
    'd': (0.1, 10),
    'k': (0.01, 1)
}
"""
PARAM_RANGES = {
    'a': (0.01, 0.04),
    'b': (0.2, 0.3),
    'c': (-50, -49),
    'd': (2, 3),
    'k': (0.01, 0.05),
}
"""
PARAM_SEQ = ('a', 'b', 'c', 'd', 'k',)


def _evaluator_communicate(args_str, input_):
    p = Popen('./test_neurons '+args_str, shell=True,
              stdin=PIPE, stdout=PIPE)
    out, err = p.communicate(input_)
    return out


class NeuronFitnessEvaluator(FitnessEvaluator):
    def __init__(self, ref_file_path, diff_metric):
        self._ref_file_path = ref_file_path
        self._diff_metric = diff_metric
        self._mins = []
        self.ref_potentials

    def fitness_many(self, phenotypes):
        eval_args = '%s %d %s' % (self._ref_file_path, len(phenotypes),
                self._diff_metric,)
        eval_input = '\n'.join([p.repr_ for p in phenotypes])
        eval_output = _evaluator_communicate(eval_args, eval_input)

        fitness_list_max = map(float, eval_output.strip().split('\n'))
        return [-f_raw for f_raw in fitness_list_max]
        return fitness_list_max

    @property
    def ref_potentials(self):
        self._load_description()
        return self._ref_potentials

    @property
    def ref_spike_times(self):
        self._load_description()
        return self._ref_spike_times

    def _load_description(self):
        if hasattr(self, '_ref_potentials'):
            return

        descr_raw = _evaluator_communicate('--describe ' +
                                           self._ref_file_path, '')
        pot_raw, st_raw = [s.strip().split(' ')
                           for s in descr_raw.split('\n')[:2]]
        self._ref_potentials = map(float, pot_raw)
        self._ref_spike_times = []
        if st_raw != ['']:
            self._ref_spike_times = map(int, st_raw)


class Neuron(Phenotype):
    def __init__(self, genotype, params):
        super(Neuron, self).__init__(genotype)
        assert set(params.keys()) == set(PARAM_SEQ)
        for pn in PARAM_SEQ:
            assert PARAM_RANGES[pn][0] <= params[pn] <= PARAM_RANGES[pn][1]
        self.params = params
        self.repr_ = ' '.join('%.12e' % self.params[pn] for pn in PARAM_SEQ)

    @property
    def potentials(self):
        self._load_description()
        return self._potentials

    @property
    def spike_times(self):
        self._load_description()
        return self._spike_times

    def _load_description(self):
        if hasattr(self, '_potentials'):
            return

        descr_raw = _evaluator_communicate('--describe', self.repr_)
        pot_raw, st_raw = [s.strip().split(' ')
                           for s in descr_raw.split('\n')[:2]]
        self._potentials = map(float, pot_raw)
        self._spike_times = []
        if st_raw != ['']:
            self._spike_times = map(int, st_raw)

    def __str__(self):
        ps = ' '.join('%s=%.9e' % (pn, self.params[pn],)
                      for pn in PARAM_SEQ)
        return ps


BITS_PER_GENE = 10

class NeuronDevMethod(DevelopmentMethod):
    @staticmethod
    def develop_phenotype_from(genotype):
        assert len(genotype.data) == BITS_PER_GENE*len(PARAM_SEQ)
        params = {}
        for i, param_name in enumerate(PARAM_SEQ):
            v = sum([2**k for k in range(BITS_PER_GENE)
                    if genotype.data[i*BITS_PER_GENE+k]])
            # Convert to gray coding (formula from WP, Gray_code)
            v = (v >> 1) ^ v
            v /= float(2**BITS_PER_GENE)
            param_range = PARAM_RANGES[param_name]
            params[param_name] = unit_to_range(v,
                                               param_range[0], param_range[1])
            assert param_range[0] <= params[param_name] <= param_range[1]
        return Neuron(genotype, params)


class DebugStepper(Listener):
    def after_reproduction(self, _):
        import time
        time.sleep(.1)
        #raw_input()


def old_create(birth_generation, rng):
    print 'yo'
    fac = RealVectorGenotype.factory_for_length(len(PARAM_SEQ))
    while True:
        x = fac(birth_generation, rng)
        return x
        if 1 < len(NeuronDevMethod().develop_phenotype_from(x).spike_times) < 70:
            return x

def create(birth_generation, rng):
    import os; os.system('clear')
    print 'yo'
    fac = BitVectorGenotype.factory_for_length(BITS_PER_GENE*len(PARAM_SEQ))
    while True:
        x = fac(birth_generation, rng)
        return x

        n = len(NeuronDevMethod().develop_phenotype_from(x).spike_times)
        return x
        print n
        if 10 < len(NeuronDevMethod().develop_phenotype_from(x).spike_times) < 300:
            return x
        if rng.random() < .5:
            return x

def run_experiment(
    _ref_file,
    _diff_measure,
    rng,
    generation_cnt,
    _pop_size,
    _batch_mode=True
):
    genotype_factory = create
    dev_method = NeuronDevMethod()
    fitness_evaluator = NeuronFitnessEvaluator(_ref_file, _diff_measure)

    adult_sel_strategy = SelectionStrategy(
        SelectAllSelectionProtocol(),
        RankSelectionMechanism() #XXX
    )
    adult_pop_size = _pop_size

    parent_sel_strategy = SelectionStrategy(
       SelectAllSelectionProtocol(),
       #TournamentSelectionMechanism(k=5, p_lucky=0.2)
       RouletteWheelSelectionMechanism(new_rank_scaler(0.5, 1.5))
    )
    parent_pop_size = 2*_pop_size

    reproduction_strategy = FixedReproductionStrategy(
        0.6, BitVectorCrossoverOperator(),
        0.05, BitVectorMutationOperator()
    )

    initial_pop_size = _pop_size

    listeners = []
    if not _batch_mode:
        listeners += [DebugStepper(), StdoutLogger(),
                                plotting.setup_live_plotting_listener(
                                    fitness_evaluator.ref_potentials,
                                    fitness_evaluator.ref_spike_times)]

    problem = ECProblem(**{ k:v for k, v in locals().items() if not k[0]=='_'})
    return problem.run()


def _run_experiment_with_dict(dict_):
    return run_experiment(**dict_)


if __name__ == '__main__':
    multiprocessing.freeze_support()

    seeder = random.Random(0x42)

    all_res_str = ''

    num_rounds_per_conf = 8
    pool = multiprocessing.Pool(processes=num_rounds_per_conf)

    #for ref_file_id in [1, 2, 3, 4]:
    for ref_file_id in [1]:#, 2, 3, 4]:
        ref_file = 'data/izzy-train%d.dat' % ref_file_id
        for diff_measure in ['spike-time', 'spike-interval', 'waveform']:
            #for crossover_rate in [0.6, 0.7, 0.8]:
            for crossover_rate in [0.6]:#, 0.7, 0.8]:
                for mutation_rate in [0.02, 0.03, 0.05, 0.1]:
                    import time
                    tpre = time.time()
                    proc_inputs = [dict(
                        _ref_file=ref_file,
                        _diff_measure=diff_measure,
                        rng=random.Random(seeder.randint(0, 0x81549300)),
                        #generation_cnt=300,
                        generation_cnt=300,
                        #_pop_size=120,
                        _pop_size=2,
                    ) for _ in range(num_rounds_per_conf)]
                    pool.map(_run_experiment_with_dict, proc_inputs)

                    print time.time() - tpre

    print len(all_res_str.split('\n'))
    with open('res.txt', 'w') as f:
        f.write(all_res_str)

