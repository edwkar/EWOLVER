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
        should_crossover = rng.random() <= 1
        if not should_crossover:
            return first.child_copy(child_gen), second.child_copy(child_gen)
        else:
            cut = rng.randint(0, len(first.data))
            first_child_data = []
            second_child_data = []
            lala = []
            for da, db in zip(first.data, second.data):
                if rng.random() < .5:
                    first_child_data.append(da)
                    second_child_data.append(db)
                else:
                    first_child_data.append(db)
                    second_child_data.append(da)
                lala.append(rng.uniform(min(da, db), max(da, db)))

            return (
                RealVectorGenotype(child_gen, lala),
                RealVectorGenotype(child_gen, second_child_data),
            )


class RealVectorMutationOperator(MutationOperator):
    def __call__(self, genotype, child_gen, rng):
        mutated_data = genotype.data[:]
        for k in range(len(mutated_data)):
            if rng.random() < 0.05:
                mutated_data[k] += rng.gauss(0, .05)
                mutated_data[k] = max(0, min(1, mutated_data[k]))
        return RealVectorGenotype(child_gen, mutated_data)


def unit_to_range(u, a, b):
    assert b > a
    assert 0 <= u <= 1
    res = a + u*(b-a)
    assert a-1e-6 < res and res < b+1e-6
    res = max(a, min(res, b))
    return res

