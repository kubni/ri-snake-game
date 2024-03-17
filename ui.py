#!/usr/bin/env python3
import sys
import random
from PySide6 import QtCore, QtWidgets, QtGui

class HelloWorldWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.hello = ["Zdravo svete!", "Hallo Walt!"]
        # self.text = QtWidgets.QLabel("Hello World", alignment=QtCore.Qt.AlignCenter) #FIXME
        # self.text = QtWidgets.QLabel("Hello World", alignment=QtCore.Qt.AlignmentFlag.AlignCenter) #FIXME

        self.button = QtWidgets.QPushButton("Click me!")
        self.text = QtWidgets.QLabel("Hello World!")
        self.text.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        layout = QtWidgets.QVBoxLayout(self) # self.layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.text)
        layout.addWidget(self.button)

        self.button.clicked.connect(self.magic)

    @QtCore.Slot()
    def magic(self):
        self.text.setText(random.choice(self.hello))

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = HelloWorldWidget()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec())
