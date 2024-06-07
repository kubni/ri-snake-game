#!/usr/bin/env python3
from math import ceil
from ga import Population, crossover, mutation, tournament_selection
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

        self.mutation_prob = 0.05
        self.tournament_size = 5
        self.num_rows = 10
        self.num_columns = 10

        self.old_body = None  # NOTE: Placeholder

        self.population_size = 5
        self.population = Population(
            population_size=self.population_size,
            board_size=(self.num_rows, self.num_columns),
        )
        self.chosen_snake = self.population.get_random_snake()
        self.grid = self.initialize_grid(self.num_rows, self.num_columns, "gray")

        self.elitism_size = ceil(0.30 * self.population_size)

        timer = QTimer(self)
        timer.timeout.connect(self.update_on_timeout)
        timer.start(250)

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
                label = QLabel()
                label.setStyleSheet(f"background-color: {grid_color}")
                grid.addWidget(label, i, j)
        return grid

    def reset_grid(self, grid_color: str):
        # TODO: Reset only the ones that are painted.
        for i in range(0, self.num_rows):
            for j in range(0, self.num_columns):
                label = QLabel()
                label.setStyleSheet(f"background-color: {grid_color}")
                self.grid.addWidget(label, i, j)




    def create_new_population(self) -> Population:
        # NOTE: Here, initial snakes of the new population are pointlessly created, as they will be replaced with genetically modified children
        old_pop_size = len(self.population.snakes)
        num_of_genetic_procedures = ceil(old_pop_size / 2)

        # NOTE: If the length of population was odd, the number of genetic procedures will produce 1 snake more than we need.
        #       We don't need this extra snake, so we will let the procedures finish, and then clamp the new population to the old population's size.
        new_pop_size = old_pop_size if old_pop_size % 2 == 0 else old_pop_size + 1
        new_population = Population(population_size=new_pop_size, board_size=(self.num_rows, self.num_columns));

        for i in range(num_of_genetic_procedures):
            parent1, parent2 = tournament_selection(
                self.population, tournament_size=self.tournament_size, num_individuals=2
            )

            child1_model, child2_model = crossover(parent1.model, parent2.model)

            # Mutation
            mutation(child1_model, mutation_probability=self.mutation_prob)
            mutation(child2_model, mutation_probability=self.mutation_prob)

            child1 = Snake(
                board_size=(self.num_rows, self.num_columns), model=child1_model
            )
            child2 = Snake(
                board_size=(self.num_rows, self.num_columns), model=child2_model
            )


            new_population.snakes[i] = child1
            new_population.snakes[i+1] = child2

        # Potentially clamp the new pop to the old pop size
        new_population.snakes = new_population.snakes[:old_pop_size]
        new_population.population_size = len(new_population.snakes)

        print('Old population: ')
        for s in self.population.snakes:
            print(s)

        print('New population: ')
        for s in new_population.snakes:
            print(s)
        return new_population


    @Slot()
    def update_on_timeout(self):
        if self.chosen_snake.is_alive:  # Color the apple
            label = QLabel()
            label.setStyleSheet("background-color: red;")
            self.grid.addWidget(
                label, self.chosen_snake.apple.y, self.chosen_snake.apple.x
            )
            # Color new snake positions with green:
            # TODO: Color only the new cell
            for p in self.chosen_snake.body:
                label = QLabel()
                label.setStyleSheet("background-color: green")
                self.grid.addWidget(label, p.y, p.x)

            # Color old snake positions with gray:
            if self.old_body != None:
                old_cells = list(
                    filter(lambda p: p not in self.chosen_snake.body, self.old_body)
                )

                for p in old_cells:
                    label = QLabel()
                    label.setStyleSheet("background-color: blue")
                    self.grid.addWidget(label, p.y, p.x)

            self.old_body = copy.deepcopy(self.chosen_snake.body)  # TODO: copy?

        # Move the whole population
        # TODO: Should this be at the beginning?
        for s in self.population:
            if s.is_alive:
                s.update()
                s.move()

        if self.population.is_dead():
            print("The entire generation is dead. Goodbye cruel world...")
            self.population = self.create_new_population()

            # TODO: Pick a new chosen snake to draw
            # TODO: Reset the grid
            self.reset_grid('gray')
            self.old_body = None
            self.chosen_snake = self.population.get_random_snake() # FIXME: Fails occasionally due to index out of range

            # FIXME: This probably only resets the grid visually. Check if snake still gains score by passing cells that had apples before the reset.
            # sys.exit(1)  # NOTE: Placeholder


if __name__ == "__main__":
    app = QApplication([])

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


