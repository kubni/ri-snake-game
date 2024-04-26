#!/usr/bin/env python3
import sys
from snake import Snake

from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QGridLayout, QLabel
from PySide6.QtCore import Slot


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.num_rows = 10
        self.num_columns = 10

        self.old_body = None  # NOTE: Placeholder
        self.snake = Snake()  # TODO: Snake(self.num_rows, self.num_columns)
        self.grid = self.initialize_grid(self.num_rows, self.num_columns, "gray")

        # Connect the signal to the slot
        self.snake.signal_snake_moved.connect(self.on_snake_move)

        # Test signal-slot interaction
        # TODO: In the future, this can be called from some Snake method.
        self.snake.emit_snake_moved()

        self.snake.placeholder_change_body()
        self.snake.emit_snake_moved()

        widget = QWidget()
        widget.setLayout(self.grid)
        self.setCentralWidget(widget)

    def initialize_grid(self, n_rows: int, n_columns: int, grid_color) -> QGridLayout:
        self.grid = QGridLayout()
        for i in range(0, n_rows):
            for j in range(0, n_columns):
                label = QLabel()
                label.setStyleSheet(f"background-color: {grid_color}")
                self.grid.addWidget(label, i, j)
        return self.grid

    @Slot(list)
    def on_snake_move(self, new_body):
        # Color new snake positions with green:
        for p in new_body:
            label = QLabel()
            label.setStyleSheet("background-color: green")
            self.grid.addWidget(label, p.x, p.y)

        # Color old snake positions with gray:
        if self.old_body != None:
            old_cells = list(filter(lambda p: p not in new_body, self.old_body))

            for p in old_cells:
                label = QLabel()
                label.setStyleSheet(
                    "background-color: blue"
                )  # TODO: Will be gray, blue for debugging purposes
                self.grid.addWidget(
                    label, p.x, p.y
                )  # TODO: False LSP error? This works.

        self.old_body = new_body


if __name__ == "__main__":
    app = QApplication([])

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
