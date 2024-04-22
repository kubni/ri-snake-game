#!/usr/bin/env python3
import sys
from snake import Snake,Point

# from PySide6 import QtWidgets, QtCore
from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QGridLayout, QLabel
from PySide6.QtGui import QColor, QPalette



# TODO: This should be moved probably


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.num_rows = 10
        self.num_columns = 10

        snake = Snake()
        layout = self.initialize_grid(snake, 10, 10, "gray")

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def initialize_grid(
        self,
        snake: Snake,
        n_rows: int,
        n_columns: int,
        grid_color: str,
    ) -> QGridLayout:
        layout = QGridLayout()
        print("Snek:", snake)
        for i in range(0, n_rows):
            for j in range(0, n_columns):
                label = QLabel()
                if Point(i, j) in snake.body:
                    label.setStyleSheet("background-color: green")
                    layout.addWidget(label, i, j)
                else:
                    label.setStyleSheet(f"background-color: {grid_color}")
                    layout.addWidget(label, i, j)
        return layout


if __name__ == "__main__":
    app = QApplication([])

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
