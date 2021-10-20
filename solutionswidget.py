from PyQt5.QtWidgets import *

from matplotlib.backends.backend_qt5agg import FigureCanvas

from matplotlib.figure import Figure


class SolutionsWidget(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.canvas = FigureCanvas(Figure())

        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.canvas)

        self.canvas.axe_1 = self.canvas.figure.add_subplot(2, 2, 1)
        self.canvas.axe_2 = self.canvas.figure.add_subplot(2, 2, 2)
        self.canvas.axe_3 = self.canvas.figure.add_subplot(2, 1, 2)
        self.setLayout(vertical_layout)
