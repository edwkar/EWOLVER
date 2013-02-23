# vim: ts=4:sw=4


import random
from subprocess import (Popen, PIPE)
from ewolver.core import *
from ewolver.binary import *
from ewolver.real import *
from ewolver.selection import *
from ewolver.utils.logging import StdoutLogger
try:
    import plotting
except:
    pass


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


BITS_PER_GENE = 8

class NeuronDevMethod(DevelopmentMethod):
    @staticmethod
    def develop_phenotype_from(genotype):
        assert len(genotype.data) == len(PARAM_SEQ)
        params = {}
        for i, param_name in enumerate(PARAM_SEQ):
            param_range = PARAM_RANGES[param_name]
            params[param_name] = unit_to_range(genotype.data[i],
                                               param_range[0], param_range[1])
            assert param_range[0] <= params[param_name] <= param_range[1]
        return Neuron(genotype, params)


class DebugStepper(Listener):
    def after_reproduction(self, _):
        import time
        time.sleep(.1)
        #raw_input()


def create(birth_generation, rng):
    print 'yo'
    fac = RealVectorGenotype.factory_for_length(len(PARAM_SEQ))
    while True:
        x = fac(birth_generation, rng)
        if 1 < len(NeuronDevMethod().develop_phenotype_from(x).spike_times) < 250:
            return x

POP_SIZE = 160
def main():
    genotype_factory = create
    dev_method = NeuronDevMethod()
    fitness_evaluator = NeuronFitnessEvaluator('data/izzy-train1.dat',
                                               'spike-time')

    adult_sel_strategy = SelectionStrategy(
        SelectAllSelectionProtocol(),
        RankSelectionMechanism() #XXX
        #RouletteWheelSelectionMechanism(new_rank_scaler(0.5, 1.5))
    )
    adult_pop_size = POP_SIZE

    parent_sel_strategy = SelectionStrategy(
       SelectAllSelectionProtocol(),
       TournamentSelectionMechanism(k=3, p_lucky=0.2)
       #RouletteWheelSelectionMechanism(new_rank_scaler(0.5, 1.8))
    )
    parent_pop_size = POP_SIZE

    reproduction_strategy = ReproductionStrategy(
        0.9, RealVectorCrossoverOperator(),
        0.1, RealVectorMutationOperator()
    )

    initial_pop_size = POP_SIZE
    generation_cnt = 3000

    listeners = [DebugStepper(), StdoutLogger(), plotting.setup_live_plotting_listener(
        fitness_evaluator.ref_potentials,
        fitness_evaluator.ref_spike_times)]
    rng = random.Random()

    problem = ECProblem(**locals())
    problem.run()


if __name__ == '__main__':
    main()
