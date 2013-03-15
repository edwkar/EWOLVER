import random
import multiprocessing
from subprocess import (Popen, PIPE)
from ewolver import selection
from ewolver.core import *
from ewolver.binary import *
from ewolver.real import *
from ewolver.utils.logging import StdoutLogger
from ewolver.utils.math_ import mean as _mean, stddev as _stddev
import plotting


BITS_PER_GENE = 12
SEEDER = random.Random(0x42)


PARAM_RANGES = {
    'a': (0.001, 0.2),
    'b': ( 0.01, 0.3),
    'c': (  -80, -30),
    'd': (  0.1,  10),
    'k': ( 0.01, 1.0)
}
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


class NeuronDevMethod(DevelopmentMethod):
    @staticmethod
    def develop_phenotype_from(genotype):
        assert len(genotype.data) == BITS_PER_GENE*len(PARAM_SEQ)
        params = {}
        for i, param_name in enumerate(PARAM_SEQ):
            v = sum([2**k for k in range(BITS_PER_GENE)
                    if genotype.data[i*BITS_PER_GENE+k]])
            v /= float(2**BITS_PER_GENE)
            param_range = PARAM_RANGES[param_name]
            params[param_name] = unit_to_range(v,
                                               param_range[0], param_range[1])
            assert param_range[0] <= params[param_name] <= param_range[1]
        return Neuron(genotype, params)

    @staticmethod
    def ___develop_phenotype_from(genotype):
        assert len(genotype.data) == len(PARAM_SEQ)
        params = {}
        for i, param_name in enumerate(PARAM_SEQ):
            param_range = PARAM_RANGES[param_name]
            params[param_name] = unit_to_range(genotype.data[i],
                                               param_range[0], param_range[1])
            assert param_range[0] <= params[param_name] <= param_range[1]
        return Neuron(genotype, params)



def run_experiment(_ref_file, _diff_measure, rng, num_generations,
                   _adult_pop_size, _parent_pop_size, _crossover_rate,
                   _mutation_rate, _batch_mode=True, _round_num=-1):

    genotype_factory = BitVectorGenotype.factory_for_length(
            BITS_PER_GENE * len(PARAM_SEQ))

    dev_method = NeuronDevMethod()
    fitness_evaluator = NeuronFitnessEvaluator(_ref_file, _diff_measure)

    adult_sel_scheme = selection.SelectionScheme(
            selection.UniqueFilter(),
            selection.ElitismSieve(elite_size=10),
            selection.Truncater(_adult_pop_size))

    parent_sel_scheme = selection.SelectionScheme(
       selection.RouletteWheel(selection.RankScaler(0.5, 1.8),
                               _parent_pop_size))

    reproduction_scheme = ReproductionScheme(
        BitVectorCrossoverOperator(),
        BitVectorMutationOperator(),
        FixedRateController(_crossover_rate, _mutation_rate)
    )

    initial_pop_size = 5 * _adult_pop_size

    if not _batch_mode:
        listeners = [plotting.setup_live_plotting_listener(
                             fitness_evaluator.ref_potentials,
                             fitness_evaluator.ref_spike_times,
                             '%s_%s_%d.png' % (_ref_file, _diff_measure,
                                               _round_num,))]
    else:
        listeners = []

    problem = ECProblem(**{ k: v for k,v in locals().items() if not k[0]=='_'})

    return problem.run()
