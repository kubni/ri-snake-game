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
        # Color the apple
        label = QLabel()
        label.setStyleSheet("background-color: red;")
        self.grid.addWidget(label, self.snake.apple.x, self.snake.apple.y)
        # Color new snake positions with green:
        # TODO: Color only the new cell
        for p in self.snake.body:
            label = QLabel()
            label.setStyleSheet("background-color: green")
            self.grid.addWidget(label, p.x, p.y)

        # Color old snake positions with gray:
        if self.old_body != None:
            old_cells = list(filter(lambda p: p not in self.snake.body, self.old_body))

            for p in old_cells:
                label = QLabel()
                label.setStyleSheet("background-color: blue")
                self.grid.addWidget(label, p.x, p.y)

        self.old_body = copy.deepcopy(self.snake.body)  # TODO: copy?

        self.snake.move()
        print("Snake moved")


if __name__ == "__main__":
    app = QApplication([])

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
