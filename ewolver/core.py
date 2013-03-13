from ewolver.utils import Multiplexer


class Genotype(object):
    def __init__(self, birth_generation):
        self._birth_generation = birth_generation
        self._phenotype = None

    birth_generation = property(lambda self: self._birth_generation)

    def _get_phenotype(self):
        assert not self._phenotype is None
        return self._phenotype

    def _set_phenotype(self, new_val):
        self._phenotype = new_val

    phenotype = property(_get_phenotype, _set_phenotype)

    def child_copy(self, birth_generation):
        raise NotImplementedError


class Phenotype(object):
    def __init__(self, genotype):
        self._genotype = genotype
        self.birth_generation = self.genotype.birth_generation
        self._fitness = None

    genotype = property(lambda self: self._genotype)

    def _get_fitness(self):
        assert not self._fitness is None
        return self._fitness

    def _set_fitness(self, new_val):
        self._fitness = new_val

    fitness = property(_get_fitness, _set_fitness)


class DevelopmentMethod(object):
    def develop_phenotype_from(self, genotype):
        raise NotImplementedError


class FitnessEvaluator(object):
    def fitness_many(self, all_phenotypes):
        raise NotImplementedError


class LocalFitnessEvaluator(FitnessEvaluator):
    def fitness_many(self, all_phenotypes):
        return map(self.fitness_one, all_phenotypes)

    def fitness_one(self, phenotype):
        raise NotImplementedError


class ECProblem(object):
    def __init__(self, genotype_factory, dev_method, fitness_evaluator,
                 adult_sel_scheme, parent_sel_scheme,
                 reproduction_scheme,
                 initial_pop_size, num_generations,
                 listeners, rng):
        self._genotype_factory = genotype_factory
        self._dev_method = dev_method

        self._fitness_evaluator = fitness_evaluator

        self._adult_sel_scheme = adult_sel_scheme
        self._parent_sel_scheme = parent_sel_scheme

        self._reproduction_scheme = reproduction_scheme

        self._initial_pop_size = initial_pop_size
        self._num_generations = num_generations

        self._listening_multiplexer = Multiplexer(listeners)
        self._rng = rng

    def run(self):
        lst = self._listening_multiplexer
        lst.before_start()

        genotypes = self._initialize_population()
        most_fit_individual = None
        child_gen = 0
        for _ in range(self._num_generations):
            print child_gen
            # Development and fitness evaluation.
            self._develop_phenotypes(genotypes)
            phenotypes = [gt.phenotype for gt in genotypes]
            self._evaluate_phenotypes(phenotypes)
            lst.after_evaluation(genotypes, phenotypes)

            # Sieve adults.
            adult_ptypes = self._select_adults(phenotypes, child_gen)
            lst.after_adult_sieving(adult_ptypes)

            local_most_fit_individual = max([p for p in adult_ptypes],
                                            key=lambda p: p.fitness)
            if local_most_fit_individual != most_fit_individual:
                most_fit_individual = local_most_fit_individual

            # Increment time.
            child_gen += 1
            lst.after_generation_step(child_gen)

            # Sieve for reproduction.
            parent_ptypes = self._select_parents(adult_ptypes, child_gen)
            parent_gtypes = [p.genotype for p in parent_ptypes]
            lst.after_parent_sieving(parent_gtypes)

            # Reproduce.
            child_gtypes = self._reproduce(parent_gtypes, parent_ptypes,
                                           child_gen)
            lst.after_reproduction(child_gtypes)

            # Update the gene pool to include both adults and child genes.
            adult_gtypes = [p.genotype for p in adult_ptypes]
            genotypes = adult_gtypes + child_gtypes

        lst.at_end()
        return most_fit_individual

    def _initialize_population(self):
        return [self._genotype_factory(birth_generation=0, rng=self._rng)
                for _ in range(self._initial_pop_size)]

    def _develop_phenotypes(self, genotypes):
        for gt in genotypes:
            gt.phenotype = self._dev_method.develop_phenotype_from(gt)

    def _evaluate_phenotypes(self, phenotypes):
        phenotypes_fitness = self._fitness_evaluator.fitness_many(phenotypes)
        for p, f in zip(phenotypes, phenotypes_fitness):
            p.fitness = f

    def _select_adults(self, phenotypes, child_gen):
        return self._adult_sel_scheme.select(phenotypes, child_gen,
                self._rng)

    def _select_parents(self, phenotypes, child_gen):
        return self._parent_sel_scheme.select(phenotypes, child_gen,
                  self._rng)

    def _extract_genotypes(self, phenotypes):
        return [pt.genotype.reproduction_copy() for pt in phenotypes]

    def _reproduce(self, parent_genotypes, parent_phenotypes, child_gen):
        return self._reproduction_scheme.reproduce(parent_genotypes,
                parent_phenotypes, child_gen, self._rng)


class Listener(object):
    def before_start(self):
        pass

    def after_generation_step(self, new_child_gen):
        pass

    def after_evaluation(self, genotypes, phenotypes):
        pass

    def after_adult_sieving(self, adult_ptypes):
        pass

    def after_parent_sieving(self, adult_ptypes):
        pass

    def after_reproduction(self, child_gtypes):
        pass

    def at_end(self):
        pass
