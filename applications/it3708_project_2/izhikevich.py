# vim: ts=4:sw=4


import random
from subprocess import (Popen, PIPE)
from ewolver.core import *
from ewolver.real import *
from ewolver.selection import *
from ewolver.utils.logging import StdoutLogger


PARAM_RANGES = {
    'a': (0.001, 0.2),
    'b': (0.01, 0.3),
    'c': (-80, -30),
    'd': (0.1, 10),
    'k': (0.01, 1.0),
}
PARAM_SEQ = ('a', 'b', 'c', 'd', 'k',)


class NeuronFitnessEvaluator(LocalFitnessEvaluator):
    EVALUATOR = 'test_neurons'

    def __init__(self, ref_file_path, diff_metric):
        self._ref_file_path = ref_file_path
        self._diff_metric = diff_metric

    def fitness_many(self, phenotypes):
        cmd = ' '.join(map(str, [
            './' + NeuronFitnessEvaluator.EVALUATOR,
            self._ref_file_path,
            len(phenotypes),
            self._diff_metric
        ]))

        evaluator_proc = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE)
        evaluator_input = '\n'.join([p.repr_ for p in phenotypes])

        evaluator_output, _ = evaluator_proc.communicate(evaluator_input)
        fitness_list = map(float, evaluator_output.strip().split('\n'))
        assert len(fitness_list) == len(phenotypes)

        return fitness_list


class Neuron(Phenotype):
    def __init__(self, genotype, params):
        super(Neuron, self).__init__(genotype)
        assert set(params.keys()) == set(PARAM_SEQ)
        for pn in PARAM_SEQ:
            assert PARAM_RANGES[pn][0] <= params[pn] <= PARAM_RANGES[pn][1]
        self.params = params
        self.repr_ = ' '.join('%f' % self.params[pn] for pn in PARAM_SEQ)

    def __str__(self):
        return ' '.join('%s=%.2f' % (pn, self.params[pn],)
                        for pn in PARAM_SEQ)


class NeuronDevMethod(DevelopmentMethod):
    def develop_phenotype_from(self, genotype):
        assert len(genotype.data) == len(PARAM_SEQ)
        params = {}
        for i, param_name in enumerate(PARAM_SEQ):
            param_range = PARAM_RANGES[param_name]
            params[param_name] = unit_to_range(genotype.data[i],
                                               param_range[0], param_range[1])
        return Neuron(genotype, params)


def main():
    genotype_factory = RealVectorGenotype.factory_for_length(len(PARAM_SEQ))
    dev_method = NeuronDevMethod()
    fitness_evaluator = NeuronFitnessEvaluator('data/izzy-train3.dat',
                                               'waveform')

    adult_sel_strategy = SelectionStrategy(
        SelectChildrenSelectionProtocol(),
        RankSelectionMechanism()
    )
    adult_pop_size = 100

    parent_sel_strategy = SelectionStrategy(
       SelectAllSelectionProtocol(),
       TournamentSelectionMechanism(k=20, p_lucky=0.1)
    )
    parent_pop_size = 200

    reproduction_strategy = ReproductionStrategy(
        0.9, RealVectorCrossoverOperator(),
        0.1, RealVectorMutationOperator()
    )

    initial_pop_size = 100
    generation_cnt = 100

    listeners = [StdoutLogger()]
    rng = random.Random()

    problem = ECProblem(**locals())
    problem.run()


if __name__ == '__main__':
    main()
