class ReproductionScheme(object):
    def __init__(self, crossover_operator, mutation_operator,
                 rate_controller):
        self._crossover_operator = crossover_operator
        self._mutation_operator = mutation_operator
        self._rate_controller = rate_controller

    def reproduce(self, parent_genotypes, parent_phenotypes, child_gen, rng):
        assert len(parent_genotypes)%2 == 0

        res = []
        for i in range(0, len(parent_genotypes), 2):
            pa, pb = parent_genotypes[i:i+2]
            cr = self._rate_controller.crossover_rate_for(pa, pb,
                    parent_phenotypes)

            a, b = self._crossover_operator(pa, pb, child_gen, cr, rng)

            mr_a = self._rate_controller.mutation_rate_for(a,
                    parent_phenotypes)
            a = self._mutation_operator(a, child_gen, mr_a, rng)

            mr_b = self._rate_controller.mutation_rate_for(b,
                    parent_phenotypes)
            b = self._mutation_operator(b, child_gen, mr_b, rng)

            res.append(a)
            res.append(b)
        return res


class RateController(object):
    def crossover_rate_for(self, parent_a, parent_b, population):
        return self._rates

    def mutation_rate_for(self, genotype, population):
        return self._rates


class FixedRateController(RateController):
    def __init__(self, crossover_rate, mutation_rate):
        self._crossover_rate = crossover_rate
        self._mutation_rate = mutation_rate

    def crossover_rate_for(self, parent_a, parent_b, population):
        return self._crossover_rate

    def mutation_rate_for(self, genotype, population):
        return self._mutation_rate


class CrossoverOperator(object):
    def __call__(self, first, second, crossover_rate, rng):
        pass


class MutationOperator(object):
    def before_reproduction(self, phenotypes):
        pass

    def __call__(self, genotype, mutation_rate, rng):
        raise NotImplementedError
