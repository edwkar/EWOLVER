# vim: ts=4:sw=4


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
            #print mr_a
            a = self._mutation_operator(a, child_gen, mr_a, rng)

            mr_b = self._rate_controller.mutation_rate_for(b,
                    parent_phenotypes)
            #print mr_b
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


class FooAdaptiveRateController(RateController):
    def __init__(self):
        self._last_pop = None

    def crossover_rate_for(self, parent_a, parent_b, population):
        if population != self._last_pop:
            self.gen = max([p.birth_generation for p in population])
            FooAdaptiveRateController.report = False
        import math
        v = max(0.1, 0.7*math.sqrt(1.0/(1.0+self.gen/20.0)))
        if FooAdaptiveRateController.report:
            print self.gen, v
        return max(0.1, v)

    def mutation_rate_for(self, genotype, population):
        import math
        v = max(0.02, 0.3*math.sqrt(1/(1.0+self.gen)))
        if FooAdaptiveRateController.report:
            print self.gen, v
            FooAdaptiveRateController.report = False
        #print self.gen, v
        return v


class AdaptiveRateController(RateController):
    def __init__(self, dev_method, fitness_evaluator,
                 k1=1.0, k2=0.08, k3=1.0, k4=0.5):
        self._dev_method = dev_method
        self._fitness_evaluator = fitness_evaluator
        self._k1 = k1
        self._k2 = k2
        self._k3 = k3
        self._k4 = k4
        self._last_pop = None

    def _gen_f(self, genotype):
        return self._fitness_evaluator.fitness_many([
                self._dev_method.develop_phenotype_from(genotype)])[0]

    def crossover_rate_for(self, parent_a, parent_b, population):
        if population != self._last_pop:
            self.f_max = max([p.fitness for p in population])
            self.f_avg = sum([p.fitness for p in population])/len(population)
            self._last_pop = population
            print self.f_max, self.f_avg
        f_best = max(parent_a.phenotype.fitness, parent_b.phenotype.fitness)

        if f_best >= self.f_avg:
            return self._k1 * (self.f_max - f_best) / (self.f_max - self.f_avg)
        else:
            return self._k3

    def mutation_rate_for(self, genotype, population):
        f = self._gen_f(genotype)
        if f >= self.f_avg:
            return max(0.05,
                       self._k2 * (self.f_max - f) / (self.f_max - self.f_avg))
        else:
            return self._k4


class CrossoverOperator(object):
    def __call__(self, first, second, crossover_rate, rng):
        pass


class MutationOperator(object):
    def before_reproduction(self, phenotypes):
        pass

    def __call__(self, genotype, mutation_rate, rng):
        raise NotImplementedError
