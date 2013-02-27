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
        should_crossover = rng.random() <= 0.7
        if not should_crossover:
            return first.child_copy(child_gen), second.child_copy(child_gen)
        cut = rng.randint(1, len(first.data)-1)
        return (
            RealVectorGenotype(child_gen, first.data[:cut]  + second.data[cut:]),
            RealVectorGenotype(child_gen, second.data[:cut] + first.data[cut:]),
        )


class RealVectorMutationOperator(MutationOperator):
    def __call__(self, genotype, child_gen, rng):
        mutated_data = genotype.data[:]
        p_muta = rng.choice([0.02, 0.1, 0.2])
        if child_gen > 100:
            p_muta = rng.choice([0.1, 0.3])
        for k in range(len(mutated_data)):
            if rng.random() < p_muta:
                mutated_data[k] += rng.gauss(0, rng.choice([0.001, 0.1, 0.2,
                    0.5, 1E-4]))
                mutated_data[k] = max(0, min(1, mutated_data[k]))
        return RealVectorGenotype(child_gen, mutated_data)


def unit_to_range(u, a, b):
    assert b > a
    assert -1e-6 <= u <= 1+1e-6
    res = a + u*(b-a)
    assert a-1e-6 < res and res < b+1e-6
    res = max(a, min(res, b))
    return res

