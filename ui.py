#!/usr/bin/env python3
import sys
from PySide6 import QtWidgets
from PySide6.QtWidgets import QWidget, QMainWindow, QGridLayout
from PySide6.QtGui import QColor, QPalette

class Color(QWidget):
    def __init__(self, color):
        super(Color, self).__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(color))
        self.setPalette(palette)



class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.num_rows = 10;
        self.num_columns = 10;

        layout = QGridLayout();
        for i in range(0, self.num_rows):
            for j in range(0, self.num_columns):
                layout.addWidget(Color('gray'), i, j);

        widget = QWidget();
        widget.setLayout(layout);
        self.setCentralWidget(widget);



if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    window = MainWindow();
    window.show()

    sys.exit(app.exec())
