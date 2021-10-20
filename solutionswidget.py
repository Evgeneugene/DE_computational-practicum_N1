from PyQt5.QtWidgets import *

from matplotlib.backends.backend_qt5agg import FigureCanvas

from matplotlib.figure import Figure


class SolutionsWidget(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.canvas = FigureCanvas(Figure())

        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.canvas)

        self.canvas.axe_1 = self.canvas.figure.add_subplot(121)
        self.canvas.axe_2 = self.canvas.figure.add_subplot(122)
        self.setLayout(vertical_layout)
