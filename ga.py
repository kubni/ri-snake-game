#!/usr/bin/env python3
from typing import List, Tuple
import random

import numpy as np
from torch import tensor, stack, zeros
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

    def get_best_n_models(self, n: int) -> List[NeuralNetwork]:
        sorted_snakes = sorted(self.snakes, key=lambda s: s.fitness, reverse=True)
        # print("Sorted snakes: ")
        # for s in sorted_snakes:
        #     print(s, s.fitness)
        return list(map(lambda s: s.model, sorted_snakes[:n]))

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
        return not any([s.is_alive for s in self.snakes])


def tournament_selection(
    population: Population, tournament_size: int, num_individuals: int
) -> List[Snake]:
    # TODO: It is possible to get same snake every time, but it isn't too important in the long run.

    selected_snakes = []
    for _ in range(num_individuals):
        pool = random.sample(population.snakes, tournament_size)
        selected_snakes.append(max(pool, key=lambda s: s.fitness))

    return selected_snakes


def roulette_selection(
        population: Population, num_individuals: int
) -> List[Snake]:
    selected_snakes = []
    wheel = sum(s.fitness for s in population.snakes)
    for _ in range(num_individuals):
        pick = random.uniform(0, wheel)
        current = 0
        for s in population.snakes:
            current += s.fitness
            if current > pick:
                selected_snakes.append(s)
                break

    return selected_snakes


# def crossover(
#     parent1: NeuralNetwork, parent2: NeuralNetwork
# ) -> Tuple[NeuralNetwork, NeuralNetwork]:

#     # NOTE: WIP #
#     p1_params, p2_params = parent1.state_dict(), parent2.state_dict()

#     # NOTE: We can also try separate lists for weights and biases in the future maybe...
#     child1 = NeuralNetwork()
#     child2 = NeuralNetwork()

#     child1_params = child1.state_dict()
#     child2_params = child2.state_dict()

#     for param in p1_params:  # NOTE: Their layers and biases (params) have same names
#         p1_layer = p1_params[param]
#         p2_layer = p2_params[param]

#         p1_layer_flattened = p1_layer.flatten()
#         p2_layer_flattened = p2_layer.flatten()

#         # NOTE: For now, we are doing the simplest crossover possible: single point split
#         # TODO: We can do separate split points by row, or by columns, or completely different crossover algorithm in the future
#         split_pos = random.randrange(0, len(p1_layer_flattened))

#         tmp_child_1_layer = tensor(np.zeros(len(p1_layer_flattened)))
#         tmp_child_2_layer = tensor(np.zeros(len(p2_layer_flattened)))

#         tmp_child_1_layer[:split_pos] = p1_layer_flattened[:split_pos]
#         tmp_child_1_layer[split_pos:] = p2_layer_flattened[split_pos:]
#         tmp_child_2_layer[:split_pos] = p2_layer_flattened[:split_pos]
#         tmp_child_2_layer[split_pos:] = p1_layer_flattened[split_pos:]


#         # Unflatten the values to the original shape of the layer
#         child1_params[param] = tmp_child_1_layer.view_as(p1_layer)
#         child2_params[param] = tmp_child_2_layer.view_as(p2_layer)

#     # Change the state dict
#     child1.load_state_dict(child1_params)
#     child2.load_state_dict(child2_params)


#     return (child1, child2)



# TODO: Separate weights and biases
def crossover_no_flatten(
    parent1: NeuralNetwork, parent2: NeuralNetwork
) -> Tuple[NeuralNetwork, NeuralNetwork]:

    p1_params, p2_params = parent1.state_dict(), parent2.state_dict()

    # NOTE: We can also try separate lists for weights and biases in the future maybe...
    child1 = NeuralNetwork()
    child2 = NeuralNetwork()
    child1_params = child1.state_dict()
    child2_params = child2.state_dict()

    for param in p1_params:  # NOTE: Their layers and biases (params) have same names
        p1_layer = p1_params[param]
        p2_layer = p2_params[param]

        # Loop through the rows of the layer
        n = -1;
        if len(p1_layer.shape) == 1:
            n = 1
        else:
            (n, _) = p1_layer.shape
        child1_layer = []
        child2_layer = []
        for i in range(n):

            # If we have a bias array, p1_row should be equal to it
            # If we have a weights matrix, it should go through them
            p1_row = tensor([])
            p2_row = tensor([])
            if n == 1:
                p1_row = p1_layer
                p2_row = p2_layer
            else:
                p1_row = p1_layer[i]
                p2_row = p2_layer[i]

            # We will split each row by its own split position.
            split_pos = random.randrange(0, len(p1_row))

            child1_row = zeros(len(p1_row))
            child2_row = zeros(len(p2_row))

            child1_row[:split_pos] = p1_row[:split_pos]
            child1_row[split_pos:] = p2_row[split_pos:]
            child2_row[:split_pos] = p2_row[:split_pos]
            child2_row[split_pos:] = p1_row[split_pos:]

            # Append the row to the matrix/layer
            child1_layer.append(child1_row)
            child2_layer.append(child2_row)

        # We have a list of tensors, and we want a tensor matrix.
        # Except that we don't want it if we have biases, which the load_state_dict expects to come with for example shape [20] and not [1, 20]
        if param.endswith('.bias'):
           # We don't need to create a tensor matrix from a list of tensors in this case, since we have only one row in this list, we can just interpret it as a simple tensor array
           child1_params[param] = child1_layer[0]
           child2_params[param] = child2_layer[0]
        else:
            child1_params[param] = stack(child1_layer)
            child2_params[param] = stack(child2_layer)

    # Change the state dict
    child1.load_state_dict(child1_params)
    child2.load_state_dict(child2_params)

    return (child1, child2)

# def crossover2(parent1: NeuralNetwork, parent2: NeuralNetwork) -> Tuple[NeuralNetwork, NeuralNetwork]:

#     p1_params, p2_params = parent1.state_dict(), parent2.state_dict()

#     child1, child2 = NeuralNetwork(), NeuralNetwork();
#     child1_params, child2_params = child1.state_dict(), child2.state_dict()

#     for param in p1_params:
#         p1_layer = p1_params[param]
#         p2_layer = p2_params[param]

#         p1_layer_flattened = p1_layer.flatten()
#         p2_layer_flattened = p2_layer.flatten()

#         tmp_child_1_layer = np.zeros(len(p1_layer_flattened))
#         tmp_child_2_layer = np.zeros(len(p2_layer_flattened))

#         mask = np.random.uniform(0, 1, size=tmp_child_1_layer.shape)

#         tmp_child_1_layer[mask > 0.5] = p1_layer_flattened[mask > 0.5]
#         tmp_child_2_layer[mask > 0.5] = p2_layer_flattened[mask > 0.5]

#         child1_params[param] = tensor(tmp_child_1_layer).view_as(p1_layer)
#         child2_params[param] = tensor(tmp_child_2_layer).view_as(p2_layer)


#     child1.load_state_dict(child1_params)
#     child2.load_state_dict(child2_params)

#     return (child1, child2)

def mutation(model: NeuralNetwork, mutation_probability: float):
    params = model.state_dict()

    for param in params:
        flattened_layer = params[param].flatten()
        for i, _ in enumerate(flattened_layer):
            # If the mutation happens, the value becomes a random value from the [-1, 1] range
            if random.random() < mutation_probability:
                flattened_layer[i] = np.random.uniform(-1, 1)

        params[param] = flattened_layer.view_as(params[param])

    # We can't directly do model.state_dict()[param] =, instead we have to use load_state_dict
    model.load_state_dict(params)
