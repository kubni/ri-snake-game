#!/usr/bin/env python3
from typing import List, Tuple
import random

import numpy as np
from torch import tensor
from neural_network import NeuralNetwork

from snake import Snake


class Population:
    def __init__(self, population_size: int, board_size: Tuple[int, int]):
        self.population_size = population_size
        self.snakes = []

        for _ in range(self.population_size):
            snake = Snake(board_size=board_size)
            self.snakes.append(snake)

    def __iter__(self):
        return iter(self.snakes)

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

    # We don't follow the best snake, just a random snake from the population
    def get_random_snake(self) -> Snake:
        return self.snakes[random.randrange(0, self.population_size)]

    def is_dead(self) -> bool:
        test = [s.is_alive for s in self.snakes]
        print(test)
        return not any(
            test
        )  # not any <==> not (at least one True) <===> everything is False <===> They are all dead


def tournament_selection(
    population: Population, tournament_size: int, num_individuals: int
) -> List[Snake]:
    # TODO: It is possible to get same snake every time, but it isn't too important in the long run.

    selected_snakes = []
    for _ in range(num_individuals):
        pool = random.sample(population.snakes, tournament_size)
        selected_snakes.append(max(pool, key=lambda s: s.fitness))

    return selected_snakes


def crossover(
    parent1: NeuralNetwork, parent2: NeuralNetwork
) -> Tuple[NeuralNetwork, NeuralNetwork]:

    # NOTE: WIP #
    p1_params, p2_params = parent1.state_dict(), parent2.state_dict()

    # NOTE: We can also try separate lists for weights and biases in the future maybe...
    child1 = NeuralNetwork()
    child2 = NeuralNetwork()
    for param in p1_params:  # NOTE: Their layers and biases (params) have same names
        p1_layer = p1_params[param]
        p2_layer = p2_params[param]

        p1_layer_flattened = p1_layer.flatten()
        p2_layer_flattened = p2_layer.flatten()

        print("P1_layer: ", p1_layer)
        print("P1_layer_flattened: ", p1_layer_flattened)
        # NOTE: For now, we are doing the simplest crossover possible: single point split
        # TODO: We can do separate split points by row, or by columns, or completely different crossover algorithm in the future
        split_pos = random.randrange(0, len(p1_layer_flattened))

        tmp_child_1_layer = tensor(np.zeros(len(p1_layer_flattened)))
        tmp_child_2_layer = tensor(np.zeros(len(p2_layer_flattened)))

        tmp_child_1_layer[:split_pos] = p1_layer_flattened[:split_pos]
        tmp_child_1_layer[split_pos:] = p2_layer_flattened[split_pos:]
        tmp_child_2_layer[:split_pos] = p2_layer_flattened[:split_pos]
        tmp_child_2_layer[split_pos:] = p1_layer_flattened[split_pos:]


        print("########## CROSSOVER ################")
        print("Split pos: ", split_pos);
        print("p1_layer_flattened: ", p1_layer_flattened)
        print("p2_layer_flattened: ", p2_layer_flattened)
        print("tmp_child_1_layer: ", tmp_child_1_layer)
        print("tmp_child_2_layer: ", tmp_child_2_layer)
        print("#####################################")


        # Unflatten the values to the original shape of the layer
        child1.state_dict()[param] = tmp_child_1_layer.view_as(p1_layer)
        child2.state_dict()[param] = tmp_child_2_layer.view_as(p2_layer)




    return (child1, child2)


def mutation(model: NeuralNetwork, mutation_probability: float):
    params = model.state_dict()

    for param in params:
        flattened_layer = params[param].flatten()
        for i, _ in enumerate(flattened_layer):
            # If the mutation happens, the value becomes a random value from the [-1, 1] range
            if random.random() < mutation_probability:
                flattened_layer[i] = np.random.uniform(-1, 1)

        model.state_dict()[param] = flattened_layer.view_as(params[param])
