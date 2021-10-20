from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
import math
from matplotlib.backends.backend_qt5agg import (NavigationToolbar2QT  as  NavigationToolbar)

_eulerColor = "#d9138a"
_exactColor = "#12a4d9"


def dy(x, y):
    return 2 * y


def f(x):
    return math.exp(2 * x)


class Grid:
    def __init__(self, mpl_widget):
        xi = float(mpl_widget.lineEdit.text())
        xf = float(mpl_widget.lineEdit_3.text())
        n = int(mpl_widget.lineEdit_4.text())
        h = float(((xf - xi) / n))
        x = xi
        yi = float(mpl_widget.lineEdit_2.text())
        y = yi
        x_plot, y_euler, y_analytical, y_euler_error = [], [], [], []
        x_plot.append(x)
        y_euler.append(y)
        y_euler_error.append(0)
        y_analytical.append(y)
        for i in range(1, n):
            y = y + dy(x, y) * h
            x = x + h
            x_plot.append(x)
            y_euler.append(y)
            func = f(x)
            y_analytical.append(func)
            y_euler_error.append(abs(func - y))
            print(i, "\t%f \t %f" % (x, y))
        self.x_plot = x_plot
        self.y_euler = y_euler
        self.y_analytical = y_analytical
        self.y_euler_error = y_euler_error
        self.xi = xi
        self.xf = xf
        self.n = n
        self.h = h
        self.yi = yi
        self.n0 = int(mpl_widget.lineEdit_GE_from.text())
        self.N = int(mpl_widget.lineEdit_GE_to.text())


class MatplotlibWidget(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        loadUi("DE.ui", self)
        self.grid = Grid(self)
        self.setWindowTitle("Computational practicum")
        self.pushButton_plot.clicked.connect(self.update_graph)
        self.pushButton_global_error.clicked.connect(self.update_global_error)
        self.checkBox.setChecked(True)
        self.checkBox.clicked.connect(self.show_analytical)
        self.checkBox_2.setChecked(True)
        self.checkBox_2.clicked.connect(self.show_euler)
        self.addToolBar(NavigationToolbar(self.SolutionsWidget.canvas, self))
        self.analytical_line = None
        self.euler_line = None
        self.euler_line_error = None
        self.euler_line_global_error = None
        self.update_graph()

    def show_euler(self):
        self.euler_line.set_visible(self.checkBox_2.isChecked())
        self.euler_line_error.set_visible(self.checkBox_2.isChecked())
        self.euler_line_global_error.set_visible(self.checkBox_2.isChecked())
        self.checkBox_2.setChecked(self.checkBox_2.isChecked())
        self.SolutionsWidget.canvas.draw()

    def show_analytical(self):
        self.analytical_line.set_visible(self.checkBox.isChecked())
        self.checkBox.setChecked(self.checkBox.isChecked())
        self.SolutionsWidget.canvas.draw()

    def update_graph(self):
        # Initializing
        self.grid = Grid(self)
        x_plot = self.grid.x_plot
        y_analytical = self.grid.y_analytical
        y_euler = self.grid.y_euler
        y_euler_error = self.grid.y_euler_error
        self.SolutionsWidget.canvas.axe_1.clear()
        self.SolutionsWidget.canvas.axe_2.clear()
        self.SolutionsWidget.canvas.axe_3.clear()
        self.analytical_line, = self.SolutionsWidget.canvas.axe_1.plot(x_plot, y_analytical,
                                                                       color=_exactColor,
                                                                       label="Analytical",
                                                                       markersize=6)
        self.euler_line, = self.SolutionsWidget.canvas.axe_1.plot(x_plot, y_euler, ".",
                                                                  color=_eulerColor,
                                                                  label="Euler",
                                                                  markersize=4)
        self.euler_line_error, = self.SolutionsWidget.canvas.axe_2.plot(x_plot, y_euler_error, ".",
                                                                        color=_eulerColor,
                                                                        label="Euler",
                                                                        markersize=4)
        self.SolutionsWidget.canvas.axe_1.legend(loc='upper right')
        self.SolutionsWidget.canvas.axe_1.set_title('Solutions')
        self.SolutionsWidget.canvas.axe_2.legend(loc='upper right')
        self.SolutionsWidget.canvas.axe_2.set_title('LTEs')
        self.update_global_error()
        self.show_euler()
        self.show_analytical()
        self.SolutionsWidget.canvas.draw()

    def update_global_error(self):
        self.grid = Grid(self)
        n0 = self.grid.n0
        N = self.grid.N
        xi = self.grid.xi
        xf = self.grid.xf
        yi = self.grid.yi
        x_plot, y_euler_err = [], []
        for i in range(n0, N+1):
            h = float(((xf - xi) / i))
            y = yi
            x = xi
            max_y_euler_error = 0
            for j in range(1, i):
                y = y + dy(x, y) * h
                x = x + h
                func = f(x)
                max_y_euler_error = max(abs(func - y), max_y_euler_error)
            y_euler_err.append(max_y_euler_error)
            x_plot.append(i)
        print("ERR:", y_euler_err)
        print("N:", x_plot)
        self.SolutionsWidget.canvas.axe_3.clear()
        self.euler_line_global_error, = self.SolutionsWidget.canvas.axe_3.plot(x_plot, y_euler_err, ".",
                                                                               color=_eulerColor,
                                                                               label="Euler",
                                                                               markersize=4)
        self.SolutionsWidget.canvas.axe_3.legend(loc='upper right')
        self.SolutionsWidget.canvas.axe_3.set_title('GTEs')
        self.SolutionsWidget.canvas.draw()
app = QApplication([])
window = MatplotlibWidget()
window.show()
app.exec_()
