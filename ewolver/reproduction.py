# vim: ts=4:sw=4


class ReproductionStrategy(object):
    def __init__(self, crossover_rate, crossover_operator, mutation_rate,
                 mutation_operator):
        self._crossover_rate = crossover_rate
        self._crossover_operator = crossover_operator
        self._mutation_rate = mutation_rate
        self._mutation_operator = mutation_operator

    def reproduce(self, parent_genotypes, child_gen, rng):
        assert len(parent_genotypes)%2 == 0
        res = []
        for i in range(0, len(parent_genotypes), 2):
            left, right = parent_genotypes[i:i+2]
            if rng.random() <= self._crossover_rate:
                x = self._crossover_operator(left, right, child_gen, rng)
            else:
                x = rng.choice([left, right])

            if rng.random() <= self._mutation_rate:
                x = self._mutation_operator(x, child_gen, rng)
            if x == left or x == right:
                x = x.child_copy(child_gen)
            res.append(x)
        return res


class CrossoverOperator(object):
    def __call__(self, first, second, child_gen, rng):
        raise NotImplementedError

class MutationOperator(object):
    def __call__(self, genotype, child_gen, rng):
        raise NotImplementedError
