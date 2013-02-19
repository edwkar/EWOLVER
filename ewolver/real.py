from ewolver.core import *
from ewolver.reproduction import *


class RealVectorGenotype(Genotype):
    def __init__(self, birth_generation, data):
        super(RealVectorGenotype, self).__init__(birth_generation)
        for x in data:
            assert 0 <= x <= 1
        self.data = data
        self.length = len(data)

    @staticmethod
    def factory_for_length(length):
        def create_random(birth_generation, rng):
            data = [rng.random() for _ in range(length)]
            return RealVectorGenotype(birth_generation, data)
        return create_random

    def child_copy(self, birth_generation):
        return RealVectorGenotype(birth_generation=birth_generation,
                data=self.data[:])

    def __str__(self):
        return ','.join('%.2f' % x for x in self.data)


class RealVectorCrossoverOperator(CrossoverOperator):
    def __call__(self, first, second, child_gen, rng):
        num_points = rng.randint(1, max(2, first.length//10))
        points = set(rng.sample(range(first.length), num_points))

        data = []
        parent = rng.choice([first, second])
        for k in range(first.length):
            data.append(parent.data[k])
            if k in points:
                parent = first if parent == second else second

        return RealVectorGenotype(child_gen, data)


class RealVectorMutationOperator(MutationOperator):
    def __call__(self, genotype, child_gen, rng):
        mutated_data = genotype.data[:]
        for k in range(len(mutated_data)):
            if rng.random() < 5e-3:
                mutated_data[k] = not mutated_data[k]
        return RealVectorGenotype(child_gen, mutated_data)


def unit_to_range(u, a, b):
    assert 0 <= u <= 1
    return a + u*(b-a)
