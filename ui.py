#!/usr/bin/env python3
from ga import Population, crossover, tournament_selection
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

        #### TESTING ZONE ####
        # Move the whole population
        # TODO: Should this be at the beginning?
        for s in self.population:
            if s.is_alive:
                s.update()
                s.move()
        ######################

        # FIXME: Other snakes don't update if the one that we are drawing is dead.

        if self.population.is_dead():
            print("The entire generation is dead. Goodbye cruel world...")

            # Necromancy
            # pop_weights_and_biases = self.population.extract_parameters()

            parent1, parent2 = tournament_selection(
                self.population, tournament_size=self.tournament_size, num_individuals=2
            )

            # TODO: Refactor crossover to accept and return a Snake instead of NeuralNetwork
            child1_model, child2_model = crossover(parent1.model, parent2.model)
            child1 = Snake(board_size=(self.num_rows, self.num_columns))
            child2 = Snake(board_size=(self.num_rows, self.num_columns))
            child1.model = child1_model
            child2.model = child2_model

            sys.exit(1)  # NOTE: Placeholder


if __name__ == "__main__":
    app = QApplication([])

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
