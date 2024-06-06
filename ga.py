#!/usr/bin/env python3
from typing import List, Tuple
from torch import Tensor
import random

from numpy import zeros
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

    def extract_parameters(self) -> List[List[Tensor]]:
        pop_weights_and_biases = []
        for s in self.snakes:
            weights_and_biases = []
            for param_tensor in s.model.state_dict():
                weights_and_biases.append(s.model.state_dict()[param_tensor].clone())
                # print("PARAM_TENSOR: ", param_tensor)
                # print("CLONE: ", s.model.state_dict()[param_tensor])

            print("Weights and biases:", weights_and_biases)
            pop_weights_and_biases.append(weights_and_biases)

        return pop_weights_and_biases


def tournament_selection(population: Population, tournament_size: int) -> Snake:
    pool = random.sample(population.snakes, tournament_size)
    return max(pool, key=lambda s: s.fitness)


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

        # NOTE: For now, we are doing the simplest crossover possible: single point split
        # TODO: We can do separate split points by row, or by columns, or completely different crossover algorithm in the future
        split_pos = random.randrange(0, len(p1_layer_flattened))

        tmp_child_1_layer = tensor(zeros(len(p1_layer_flattened)))
        tmp_child_2_layer = tensor(zeros(len(p2_layer_flattened)))

        tmp_child_1_layer[:split_pos] = p1_layer_flattened[:split_pos]
        tmp_child_1_layer[split_pos:] = p2_layer_flattened[split_pos:]
        tmp_child_2_layer[:split_pos] = p2_layer_flattened[:split_pos]
        tmp_child_2_layer[split_pos:] = p1_layer_flattened[split_pos:]

        # Unflatten the values to the original shape of the layer
        child1.state_dict()[param] = tmp_child_1_layer.view_as(p1_layer)
        child2.state_dict()[param] = tmp_child_2_layer.view_as(p2_layer)

    return (child1, child2)


def mutation(snake: Snake, mutation_probability: float):
    code_len = len(snake.code)
    for i in range(code_len):
        if random.random() < mutation_probability:
            snake.code[i] = -snake.code[i]  # NOTE: Placeholder
