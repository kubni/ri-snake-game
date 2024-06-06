#!/usr/bin/env python3
from snake import Snake
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QMainWindow,
    QGridLayout,
    QLabel,
)
from PySide6.QtCore import Slot, QTimer

import sys, copy


class MainWindow(QMainWindow):

    # signal_snake_moved = Signal()

    def __init__(self):
        super(MainWindow, self).__init__()

        self.num_rows = 10
        self.num_columns = 10

        self.old_body = None  # NOTE: Placeholder
        self.snake = Snake(board_size=(self.num_rows, self.num_columns))
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
        if self.snake.is_alive:  # Color the apple
            label = QLabel()
            label.setStyleSheet("background-color: red;")
            self.grid.addWidget(label, self.snake.apple.y, self.snake.apple.x)
            # Color new snake positions with green:
            # TODO: Color only the new cell
            for p in self.snake.body:
                label = QLabel()
                label.setStyleSheet("background-color: green")
                self.grid.addWidget(label, p.y, p.x)

            # Color old snake positions with gray:
            if self.old_body != None:
                old_cells = list(
                    filter(lambda p: p not in self.snake.body, self.old_body)
                )

                for p in old_cells:
                    label = QLabel()
                    label.setStyleSheet("background-color: blue")
                    self.grid.addWidget(label, p.y, p.x)

            self.old_body = copy.deepcopy(self.snake.body)  # TODO: copy?
            self.snake.update()
            # TODO: Place this in if()
            self.snake.move()
            print("Snake moved")
        if not self.snake.is_alive:
            # TODO: Get the model parameters and run them through genetic algorithms
            print("MODEL PARAMETERS: \n")

            weights_and_biases = []  # TODO: Are separate lists needed?
            for param_tensor in self.snake.model.state_dict():
                weights_and_biases.append(
                    self.snake.model.state_dict()[param_tensor].clone()
                )
                print("PARAM_TENSOR: ", param_tensor)
                print("CLONE: ", self.snake.model.state_dict()[param_tensor])

            sys.exit(1)  # NOTE: Placeholder


if __name__ == "__main__":
    app = QApplication([])

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
