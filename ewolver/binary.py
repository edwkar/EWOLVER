from ewolver.core import *
from ewolver.reproduction import *


class BitVectorGenotype(Genotype):
    def __init__(self, birth_generation, data):
        super(BitVectorGenotype, self).__init__(birth_generation)
        self.data = data
        self.length = len(data)

    @staticmethod
    def factory_for_length(length):
        def create_random(birth_generation, rng):
            data = [rng.randint(0, 1) for _ in range(length)]
            return BitVectorGenotype(birth_generation, data)
        return create_random

    def child_copy(self, birth_generation):
        return BitVectorGenotype(birth_generation=birth_generation,
                data=self.data[:])

    def __str__(self):
        return ''.join('1' if x else '0' for x in self.data)


class BitVectorPhenotype(Phenotype):
    def __init__(self, genotype):
        super(BitVectorPhenotype, self).__init__(genotype)
        self.data = genotype.data

    def __str__(self):
        return ''.join('1' if x else '0' for x in self.data)


class IdentityBitVectorDevelopmentMethod(DevelopmentMethod):
    def develop_phenotype_from(self, genotype):
        return BitVectorPhenotype(genotype)


class BitVectorCrossoverOperator(CrossoverOperator):
    def __call__(self, first, second, child_gen, crossover_rate, rng):
        left_data = []
        right_data = []

        if rng.random() < crossover_rate:
            left_data = first.data[:]
            right_data = second.data[:]
        else:
            k = rng.randint(0, len(first.data))
            left_data = first.data[:k] + second.data[k:]
            right_data = second.data[:k] + first.data[k:]
        return [
            BitVectorGenotype(child_gen, left_data),
            BitVectorGenotype(child_gen, right_data)
        ]


class BitVectorMutationOperator(MutationOperator):
    def __call__(self, genotype, child_gen, mutation_rate, rng):
        mutated_data = genotype.data[:]
        for k in range(len(mutated_data)):
            if rng.random() < mutation_rate:
                mutated_data[k] = not mutated_data[k]
        return BitVectorGenotype(child_gen, mutated_data)
