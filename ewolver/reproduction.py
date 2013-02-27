# vim: ts=4:sw=4


class ReproductionStrategy(object):
    def __init__(self, crossover_operator, mutation_operator):
        self._crossover_operator = crossover_operator
        self._mutation_operator = mutation_operator

    def reproduce(self, parent_genotypes, parent_phenotypes, child_gen, rng):
        assert len(parent_genotypes)%2 == 0
        cr, mr = self._compute_rates(parent_phenotypes)

        res = []
        for i in range(0, len(parent_genotypes), 2):
            pa, pb = parent_genotypes[i:i+2]
            a, b = self._crossover_operator(pa, pb, child_gen, cr, rng)

            a = self._mutation_operator(a, child_gen, mr, rng)
            b = self._mutation_operator(b, child_gen, mr, rng)

            res.append(a)
            res.append(b)
        return res

    def _compute_rates(self, parent_genotypes):
        return NotImplementedError


class FixedReproductionStrategy(ReproductionStrategy):
    def __init__(self, crossover_rate, crossover_operator, mutation_rate,
                 mutation_operator):
        super(FixedReproductionStrategy, self).__init__(crossover_operator,
                                                   mutation_operator)
        self._rates = (crossover_rate, mutation_rate,)

    def _compute_rates(self, _):
        return self._rates


class AdaptiveReproductionStrategy(ReproductionStrategy):
    def __init__(self, crossover_operator, mutation_operator):
        super(AdaptiveReproductionStrategy, self).__init__(crossover_operator,
                                                   mutation_operator)

    def _compute_rates(self, parent_phenotypes):
        return self._rates


class CrossoverOperator(object):
    def __call__(self, first, second, child_gen, crossover_rate, rng):
        raise NotImplementedError

class MutationOperator(object):
    def before_reproduction(self, phenotypes):
        pass

    def __call__(self, genotype, child_gen, mutation_rate, rng):
        raise NotImplementedError
