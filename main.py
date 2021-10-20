from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
import math
from matplotlib.backends.backend_qt5agg import (NavigationToolbar2QT  as  NavigationToolbar)


def dy(x, y):
    return 2 * y


def f(x):
    return math.exp(2 * x)


class MatplotlibWidget(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        loadUi("DE.ui", self)
        self.setWindowTitle("Computational practicum")
        self.pushButton_plot.clicked.connect(self.update_graph)
        self.checkBox.setChecked(True)
        self.checkBox.clicked.connect(self.show_analytical)
        self.checkBox_2.setChecked(True)
        self.checkBox_2.clicked.connect(self.show_euler)
        self.addToolBar(NavigationToolbar(self.SolutionsWidget.canvas, self))
        self.analytical_line = None
        self.euler_line = None
        self.euler_line_error = None
        self.update_graph()

    def show_euler(self):
        self.euler_line.set_visible(self.checkBox_2.isChecked())
        self.euler_line_error.set_visible(self.checkBox_2.isChecked())
        self.checkBox_2.setChecked(self.checkBox_2.isChecked())
        self.SolutionsWidget.canvas.draw()

    def show_analytical(self):
        self.analytical_line.set_visible(self.checkBox.isChecked())
        self.checkBox.setChecked(self.checkBox.isChecked())
        self.SolutionsWidget.canvas.draw()

    def update_graph(self):
        # Initializing
        dy(1, 2)
        xi = float(self.lineEdit.text())
        xf = float(self.lineEdit_3.text())
        n = int(self.lineEdit_4.text())
        h = float(((xf - xi) / n))
        x = xi
        y = float(self.lineEdit_2.text())
        x_plot, y_euler, y_analytical, y_euler_error = [], [], [], []
        x_plot.append(x)
        y_euler.append(y)
        y_euler_error.append(0)
        y_analytical.append(y)
        for i in range(1, n + 1):
            y = y + dy(x, y) * h
            x = x + h
            x_plot.append(x)
            y_euler.append(y)
            func = f(x)
            y_analytical.append(func)
            y_euler_error.append(abs(func - y))
            print(i, "\t%f \t %f" % (x, y))

        self.SolutionsWidget.canvas.axe_1.clear()
        self.SolutionsWidget.canvas.axe_2.clear()
        self.analytical_line, = self.SolutionsWidget.canvas.axe_1.plot(x_plot, y_analytical, label="Analytical")
        self.euler_line, = self.SolutionsWidget.canvas.axe_1.plot(x_plot, y_euler, "r.", markersize=4, label="Euler")
        self.SolutionsWidget.canvas.axe_1.legend(loc='upper right')
        self.SolutionsWidget.canvas.axe_1.set_title('Solutions')
        self.euler_line_error, = self.SolutionsWidget.canvas.axe_2.plot(x_plot, y_euler_error, "r.", markersize=4,
                                                                  label="Euler")
        self.SolutionsWidget.canvas.axe_2.legend(loc='upper right')
        self.SolutionsWidget.canvas.axe_2.set_title('Local errors')
        self.show_euler()
        self.show_analytical()
        self.SolutionsWidget.canvas.draw()


app = QApplication([])
window = MatplotlibWidget()
window.show()
app.exec_()
