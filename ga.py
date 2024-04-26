#!/usr/bin/env python3
from typing import Tuple
from random import random

from snake import Snake


class Population:
    def __init__(self, population_size: int):
        self.population_size = population_size
        self.population = []

        for _ in range(self.population_size):
            snake = Snake()  # TODO: Snake(grid_width, grid_height)
            self.population.append(snake)

    def get_best_individual_and_fitness(self) -> Tuple[Snake, float]:
        best_snake = max(self.population, key=lambda s: s.fitness)
        return (best_snake, best_snake.fitness)

    def calculate_fitness(self):
        for s in self.population:
            s.calculate_fitness()

    def get_total_pop_fitness(self) -> float:
        total_fitness = 0
        for s in self.population:
            total_fitness += s.fitness
        return total_fitness

    def get_avg_pop_fitness(self) -> float:
        return self.get_total_pop_fitness() / self.population_size


def tournament_selection(population: list[Snake], tournament_size: int) -> Snake:
    pool = random.sample(population, tournament_size)
    return max(pool, key=lambda s: s.fitness)
