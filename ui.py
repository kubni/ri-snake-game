#!/usr/bin/env python3
from math import ceil, inf
from typing import List
import matplotlib.pyplot as plt

from ga import Population, crossover_no_flatten, mutation, roulette_selection, tournament_selection
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QMainWindow,
    QGridLayout,
    QLabel,
)
from PySide6.QtCore import Slot, QTimer

import sys, copy

from snake import Snake


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.best_fitness = -inf
        self.best_score = 0
        self.generation_counter = 1;
        self.mutation_prob = 0.05
        self.tournament_size = 256
        self.fitness_values = []
        self.num_generations = 200
        self.num_rows = 5
        self.num_columns = 5
        self.old_body = None

        self.population_size = 1000
        self.population = Population(
            population_size=self.population_size,
            board_size=(self.num_rows, self.num_columns),
        )

        self.chosen_snake = self.population.get_random_snake()
        self.grid_cells = [[QLabel() for _ in range(self.num_rows)] for _ in range(self.num_columns)]
        self.grid = self.initialize_grid(self.num_rows, self.num_columns, "gray")

        self.elitism_size = ceil(0.30 * self.population_size)
        self.num_of_genetic_procedures = ceil((self.population_size - self.elitism_size) / 2)

        timer = QTimer(self)
        timer.timeout.connect(self.update_on_timeout)
        timer.start(50)

        widget = QWidget()
        widget.setLayout(self.grid)
        self.setCentralWidget(widget)

    def initialize_grid(
        self,
        n_rows: int,
        n_columns: int,
        grid_color: str,
    ) -> QGridLayout:
        grid = QGridLayout()
        for i in range(0, n_rows):
            for j in range(0, n_columns):
                # label = QLabel()
                cell = self.grid_cells[i][j]
                cell.setStyleSheet(f"background-color: {grid_color}")
                grid.addWidget(cell, i, j)
        return grid

    def reset_grid(self, grid_color: str):
        # TODO: Reset only the ones that are painted.
        for i in range(0, self.num_rows):
            for j in range(0, self.num_columns):
                # label = QLabel()
                cell = self.grid_cells[i][j]
                cell.setStyleSheet(f"background-color: {grid_color}")



    # Elitism doesn't save the Snakes, but instead their NeuralNetworks and puts them inside of new Snakes
    def elitism(self) -> List[Snake]:

        # Extract the NeuralNetworks out of best snakes from current generation:
        snake_minds = self.population.get_best_n_models(self.elitism_size)

        # Create the elite snakes by using best snake minds
        elite_snakes = []
        for i in range(self.elitism_size):
            elite_snakes.append(Snake(board_size=(self.num_rows, self.num_columns), model=copy.deepcopy(snake_minds[i])))

        return elite_snakes

    def create_new_population(self) -> Population:
        # NOTE: Here, initial snakes of the new population are pointlessly created, as they will be replaced with genetically modified children
        old_pop_size = len(self.population.snakes)

        # NOTE: If the length of population was odd, the number of genetic procedures will produce 1 snake more than we need.
        #       We don't need this extra snake, so we will let the procedures finish, and then clamp the new population to the old population's size.
        new_pop_size = old_pop_size if old_pop_size % 2 == 0 else old_pop_size + 1
        new_population = Population(population_size=new_pop_size, board_size=(self.num_rows, self.num_columns));

        # Elitism
        elite_snakes = self.elitism()
        new_population.snakes[:self.elitism_size] = elite_snakes

        # Standard genetic procedures
        for i in range(self.num_of_genetic_procedures):
            parent1, parent2 = tournament_selection(
                self.population, tournament_size=self.tournament_size, num_individuals=2
            )
            # parent1, parent2 = roulette_selection(self.population, num_individuals=2)

            # child1_model, child2_model = crossover(parent1.model, parent2.model)
            # child1_model, child2_model = crossover2(parent1.model, parent2.model)
            child1_model, child2_model = crossover_no_flatten(parent1.model, parent2.model)

            # Mutation
            mutation(child1_model, mutation_probability=self.mutation_prob)
            mutation(child2_model, mutation_probability=self.mutation_prob)

            child1 = Snake(
                board_size=(self.num_rows, self.num_columns), model=child1_model
            )
            child2 = Snake(
                board_size=(self.num_rows, self.num_columns), model=child2_model
            )

            new_population.snakes[self.elitism_size + i] = child1
            new_population.snakes[self.elitism_size + i + 1] = child2

        # Potentially clamp the new pop to the old pop size
        new_population.snakes = new_population.snakes[:old_pop_size]
        new_population.population_size = len(new_population.snakes)
        return new_population


    @Slot()
    def update_on_timeout(self):
        if self.chosen_snake.is_alive:  # Color the apple
            # label = QLabel()
            # label.setStyleSheet("background-color: red;")
            # self.grid.addWidget(
            #     label, self.chosen_snake.apple.y, self.chosen_snake.apple.x
            # )

            cell = self.grid_cells[self.chosen_snake.apple.y][self.chosen_snake.apple.x]
            cell.setStyleSheet("background-color: red;")

            # Color new snake positions with green:
            # TODO: Color only the new cell
            for p in self.chosen_snake.body:
                # label = QLabel()
                # label.setStyleSheet("background-color: green")
                # self.grid.addWidget(label, p.y, p.x)
                cell = self.grid_cells[p.y][p.x]
                cell.setStyleSheet("background-color: green")

            # Color old snake positions with gray:
            if self.old_body != None:
                old_cells = list(
                    filter(lambda p: p not in self.chosen_snake.body, self.old_body)
                )

                for p in old_cells:
                    # label = QLabel()
                    # label.setStyleSheet("background-color: gray")
                    # self.grid.addWidget(label, p.y, p.x)
                    cell = self.grid_cells[p.y][p.x]
                    cell.setStyleSheet("background-color: gray")

            self.old_body = copy.deepcopy(self.chosen_snake.body)  # TODO: copy?

        # Move the whole population
        # TODO: Should this be at the beginning?
        for s in self.population:
            if s.is_alive:
                s.update()
                s.move()

        if self.population.is_dead():
            print("The entire generation is dead. Goodbye cruel world...")
            self.population.calculate_fitness()

            print(f"#### Data for generation #{self.generation_counter} ####")
            best_individual_in_generation, best_fitness_in_generation = self.population.get_best_individual_and_fitness()
            if best_fitness_in_generation > self.best_fitness:
                self.best_fitness = best_fitness_in_generation
            if best_individual_in_generation.score > self.best_score:
                self.best_score = best_individual_in_generation.score
            self.fitness_values.append(self.best_fitness)
            print("Average generation fitness :", self.population.get_avg_pop_fitness())
            print("Best individual fitness in generation: ", best_fitness_in_generation)
            print("Best individual's score: ", best_individual_in_generation.score)
            print("#################### Global stats #######################")
            print("Best ever individual fitness: ", self.best_fitness)
            print("Best ever score: ", self.best_score)
            print("#########################################################")


            if self.generation_counter == self.num_generations:
                generations = list(range(1, self.num_generations + 1))
                plt.figure(figsize=(10, 6))
                plt.plot(generations, self.fitness_values, marker='o', linestyle='-', color='b', label='Fitness')
                plt.title('Fitness with 500 snake per generation')
                plt.xlabel('Generation')
                plt.ylabel('Fitness')
                plt.legend()
                plt.grid(True)
                plt.savefig("500_snakes.png")

                sys.exit(1)
            self.population = self.create_new_population()
            self.generation_counter += 1;

            self.reset_grid('gray')
            self.old_body = None
            # self.chosen_snake = self.population.get_random_snake()
            self.chosen_snake = self.population.snakes[0]
            # sys.exit(1)  # NOTE: Placeholder


if __name__ == "__main__":
    app = QApplication([])

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


