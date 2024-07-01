
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton
import asyncio
import threading

from __init__ import YAESI

class SimpleApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Simple Qt Python App')
        layout = QVBoxLayout()

        self.button = QPushButton('Get Location', self)
        self.button.clicked.connect(self.get_location)

        layout.addWidget(self.button)
        self.setLayout(layout)

    def get_location(self):
        print(ESI.character_location())

if __name__ == '__main__':
    ESI = YAESI("client id", "client secret", ["esi-location.read_location.v1"])
    app = QApplication(sys.argv)
    ex = SimpleApp()
    ex.show()
    sys.exit(app.exec_())
