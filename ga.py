#!/usr/bin/env python3
from typing import Tuple
import random

from snake import Snake


class Population:
    def __init__(self, population_size: int):
        self.population_size = population_size
        self.snakes = []

        for _ in range(self.population_size):
            snake = Snake()  # TODO: Snake(grid_width, grid_height)
            self.snakes.append(snake)

    def get_best_individual_and_fitness(self) -> Tuple[Snake, float]:
        best_snake = max(self.snakes, key=lambda s: s.fitness)
        return (best_snake, best_snake.fitness)

    def calculate_fitness(self):
        for s in self.snakes:
            s.calculate_fitness()

    def get_total_pop_fitness(self) -> float:
        total_fitness = 0
        for s in self.snakes:
            total_fitness += s.fitness
        return total_fitness

    def get_avg_pop_fitness(self) -> float:
        return self.get_total_pop_fitness() / self.population_size


def tournament_selection(population: Population, tournament_size: int) -> Snake:
    pool = random.sample(population.snakes, tournament_size)
    return max(pool, key=lambda s: s.fitness)


def crossover(parent1, parent2) -> Tuple[Snake, Snake]:
    split_pos = random.randrange(0, len(parent1.code))

    child1 = Snake()
    child2 = Snake()
    child1.code[:split_pos] = parent1.code[:split_pos]
    child1.code[split_pos:] = parent2.code[split_pos:]
    child2.code[:split_pos] = parent2.code[:split_pos]
    child2.code[split_pos:] = parent1.code[split_pos:]

    return (child1, child2)


def mutation(snake: Snake, mutation_probability: float):
    code_len = len(snake.code)
    for i in range(code_len):
        if random.random() < mutation_probability:
            snake.code[i] = -snake.code[i]  # NOTE: Placeholder
