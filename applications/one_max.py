# vim: ts=4:sw=4


import random
from ewolver.core import ECProblem
from ewolver.binary import *
from ewolver.selection import *
from ewolver.utils.logging import StdoutLogger


class OneMaxFitnessEvaluator(FitnessEvaluator):
    def fitness_of(self, phenotype, _):
        return sum(1 for v in phenotype.data if v)


def main():
    N = 400

    problem = ECProblem(
        genotype_factory=BitVectorGenotype.factory_for_length(N),
        dev_method=IdentityBitVectorDevelopmentMethod(),
        fitness_evaluator=OneMaxFitnessEvaluator(),

        adult_sel_strategy=SelectionStrategy(
            SelectChildrenSelectionProtocol(),
            RankSelectionMechanism()
        ),
        adult_pop_size=100,

        parent_sel_strategy=SelectionStrategy(
            SelectAllSelectionProtocol(),
            TournamentSelectionMechanism(k=20, p_lucky=0.1)
        ),
        parent_pop_size=400,

        reproduction_strategy=ReproductionStrategy(
             0.9, BitVectorCrossoverOperator(),
             0.1, BitVectorMutationOperator()
        ),

        initial_pop_size=100,
        generation_cnt=500,

        listeners=[StdoutLogger()],
        rng=random.Random()
    )

    problem.run()


if __name__ == '__main__':
    main()
