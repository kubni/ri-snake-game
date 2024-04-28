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

        # self.signal_snake_moved.connect(self.on_snake_move)
        # self.emit_snake_moved()

        timer = QTimer(self)
        timer.timeout.connect(self.update_on_timeout)
        timer.start(500)

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

    # def emit_snake_moved(self):
    #     self.signal_snake_moved.emit()

    @Slot()
    def update_on_timeout(self):
        # Color new snake positions with green:
        # TODO: Color only the new cell
        for p in self.snake.body:
            label = QLabel()
            label.setStyleSheet("background-color: green")
            self.grid.addWidget(label, p.x, p.y)

        # Color old snake positions with gray:
        if self.old_body != None:
            # print("Old body:")
            # for c in self.old_body:
            #     print(c)

            # print("New body:")
            # for c in self.snake.body:
            #     print(c)

            old_cells = list(filter(lambda p: p not in self.snake.body, self.old_body))

            # print("Old cells:")
            # for c in old_cells:
            #     print(c)

            for p in old_cells:
                label = QLabel()
                label.setStyleSheet("background-color: blue")
                self.grid.addWidget(label, p.x, p.y)

        self.old_body = copy.copy(self.snake.body)  # TODO: deepcopy?
        # self.old_body = self.snake.body

        self.snake.move()
        print("Snake moved")


if __name__ == "__main__":
    app = QApplication([])

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
