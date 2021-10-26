from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
import math
from matplotlib.backends.backend_qt5agg import (NavigationToolbar2QT  as  NavigationToolbar)
from abc import ABCMeta, abstractmethod, ABC

_eulerColor = "#d9138a"
_exactColor = "#12a4d9"
_improvedEulerColor = "#e2d810"


def dy(x, y):
    return math.exp(y) - 2 / x


def f(x):
    return -math.log((math.exp(2) - 1) * x * x + x)


class Solution(metaclass=ABCMeta):
    def __init__(self, grid):
        self.x_points = grid.x_points
        self.y_points = []
        self.grid = grid

    @abstractmethod
    def Calculate_points(self):
        pass


class ExactSolution(Solution):
    def Calculate_points(self):
        self.y_points = []
        self.x_points = self.grid.x_points
        for i in range(0, self.grid.n):
            y = f(self.grid.x_points[i])
            self.y_points.append(y)
        return self.y_points


class EulerSolution(Solution):
    def Calculate_points(self):
        self.y_points = []
        self.x_points = self.grid.x_points
        y = self.grid.yi
        self.y_points.append(y)
        for i in range(1, self.grid.n):
            y = y + dy(self.grid.x_points[i - 1], y) * self.grid.h
            self.y_points.append(y)
        return self.y_points


class ImprovedEulerSolution(Solution):
    def Calculate_points(self):
        self.y_points = []
        self.x_points = self.grid.x_points
        y = self.grid.yi
        self.y_points.append(y)
        for i in range(1, self.grid.n):
            x = self.grid.x_points[i - 1]
            h = self.grid.h
            y = y + (dy(x, y) + dy(x + h, y + h * dy(x, y))) / 2 * h
            print("x,y : ", x, ",", y, h)
            print("dy(x,y):", dy(x, y))
            print("ÿ:", dy(x + h, y + h * dy(x, y)))
            print("y:", y)
            self.y_points.append(y)
        print("IMPROVED: ", self.y_points)
        print("XS: ", self.x_points)
        return self.y_points


class Grid:
    def __init__(self, mpl_widget):
        self.xi = None
        self.xf = None
        self.n = None
        self.h = None
        self.yi = None
        self.x_points = []
        self.mpl_widget = mpl_widget

    def Update(self):
        mpl_widget = self.mpl_widget
        self.x_points = []
        self.xi = float(mpl_widget.lineEdit.text())
        self.xf = float(mpl_widget.lineEdit_3.text()) + 1
        self.h = float(mpl_widget.lineEdit_4.text())
        self.n = int(((self.xf - self.xi) / self.h))
        self.yi = float(mpl_widget.lineEdit_2.text())
        x = self.xi
        self.x_points.append(x)
        for i in range(0, self.n - 1):
            x = x + self.h
            self.x_points.append(x)


class LTE_Grid:
    def __init__(self):
        self.x_points = []
        self.y_euler = []
        self.y_improved_euler = []

    def Calculate_LTE(self, exact, euler, improved_euler):
        self.x_points = exact.x_points
        self.y_euler = []
        self.y_improved_euler = []
        self.y_euler.append(exact.y_points[0] - euler.y_points[0])
        self.y_improved_euler.append(exact.y_points[0] - improved_euler.y_points[0])
        n = len(self.x_points)
        for i in range(1, n):
            y_euler = abs(exact.y_points[i] - euler.y_points[i])
            y_improved_euler = abs(exact.y_points[i] - improved_euler.y_points[i])
            self.y_euler.append(y_euler)
            self.y_improved_euler.append(y_improved_euler)
        return self.y_euler, self.y_improved_euler


class GTE_Grid:
    def __init__(self, mpl_widget):
        self.x_points = []
        self.y_euler = []
        self.n0 = int(mpl_widget.lineEdit_GE_from.text())
        self.N = int(mpl_widget.lineEdit_GE_to.text())
        self.xi = mpl_widget.grid.xi
        self.xf = mpl_widget.grid.xf
        self.yi = mpl_widget.grid.yi
        self.mpl_widget = mpl_widget

    def Calculate_GTE(self):
        self.n0 = int(self.mpl_widget.lineEdit_GE_from.text())
        self.N = int(self.mpl_widget.lineEdit_GE_to.text())
        n0 = self.n0
        N = self.N
        xi = self.mpl_widget.grid.xi
        xf = self.mpl_widget.grid.xf
        yi = self.mpl_widget.grid.yi
        x_points, y_euler_error, y_improved_euler_error = [], [], []
        for i in range(n0, N + 1):
            h = float(((xf - xi) / i))
            y = yi
            y_imp = yi
            x = xi
            max_y_euler_error = 0
            max_y_improved_euler_error = 0
            for j in range(1, i):
                y = y + dy(x, y) * h
                y_imp = y_imp + (dy(x, y_imp) + dy(x + h, y_imp + h * dy(x, y_imp))) / 2 * h
                x = x + h
                func = f(x)
                max_y_euler_error = max(abs(func - y), max_y_euler_error)
                max_y_improved_euler_error = max(abs(func - y_imp), max_y_improved_euler_error)
            y_euler_error.append(max_y_euler_error)
            y_improved_euler_error.append(max_y_improved_euler_error)
            x_points.append(i)
        self.x_points = x_points
        self.y_euler = y_euler_error
        return x_points, y_euler_error, y_improved_euler_error


class MatplotlibWidget(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        loadUi("DE.ui", self)
        self.setWindowTitle("Computational practicum")
        self.checkBox.setChecked(True)
        self.checkBox_2.setChecked(True)
        self.checkBox_3.setChecked(True)
        self.addToolBar(NavigationToolbar(self.SolutionsWidget.canvas, self))
        self.exact_line = None
        self.euler_line = None
        self.improved_euler_line = None
        self.euler_lte_line = None
        self.improved_euler_lte_line = None
        self.euler_gte_line = None
        self.improved_euler_gte_line = None
        self.grid = Grid(self)
        self.exactSolution = ExactSolution(self.grid)
        self.eulerSolution = EulerSolution(self.grid)
        self.improvedEulerSolution = ImprovedEulerSolution(self.grid)
        self.LTE_grid = LTE_Grid()
        self.GTE_grid = GTE_Grid(self)
        self.controller = Controller(self)
        self.pushButton_plot.clicked.connect(self.controller.update_graph)
        self.pushButton_global_error.clicked.connect(self.controller.update_GTE)
        self.checkBox.clicked.connect(self.controller.show_exact)
        self.checkBox_2.clicked.connect(self.controller.show_euler)
        self.checkBox_3.clicked.connect(self.controller.show_improved_euler)
        self.controller.update_graph()


class Controller:
    def __init__(self, mpl_widget):
        self.mpl_widget = mpl_widget

    def show_exact(self):
        self.mpl_widget.exact_line.set_visible(self.mpl_widget.checkBox.isChecked())
        self.mpl_widget.checkBox.setChecked(self.mpl_widget.checkBox.isChecked())
        self.mpl_widget.SolutionsWidget.canvas.draw()

    def show_euler(self):
        self.mpl_widget.euler_line.set_visible(self.mpl_widget.checkBox_2.isChecked())
        self.mpl_widget.euler_lte_line.set_visible(self.mpl_widget.checkBox_2.isChecked())
        self.mpl_widget.euler_gte_line.set_visible(self.mpl_widget.checkBox_2.isChecked())
        self.mpl_widget.checkBox_2.setChecked(self.mpl_widget.checkBox_2.isChecked())
        self.mpl_widget.SolutionsWidget.canvas.draw()

    def show_improved_euler(self):
        self.mpl_widget.improved_euler_line.set_visible(self.mpl_widget.checkBox_3.isChecked())
        self.mpl_widget.improved_euler_lte_line.set_visible(self.mpl_widget.checkBox_3.isChecked())
        self.mpl_widget.improved_euler_gte_line.set_visible(self.mpl_widget.checkBox_3.isChecked())
        self.mpl_widget.checkBox_3.setChecked(self.mpl_widget.checkBox_3.isChecked())
        self.mpl_widget.SolutionsWidget.canvas.draw()

    def update_graph(self):
        mpl_widget = self.mpl_widget
        mpl_widget.grid.Update()
        x_points = mpl_widget.grid.x_points
        y_exact = mpl_widget.exactSolution.Calculate_points()
        y_euler = mpl_widget.eulerSolution.Calculate_points()
        y_improved_euler = mpl_widget.improvedEulerSolution.Calculate_points()
        y_euler_lte, y_improved_euler_lte = mpl_widget.LTE_grid.Calculate_LTE(mpl_widget.exactSolution,
                                                                              mpl_widget.eulerSolution,
                                                                              mpl_widget.improvedEulerSolution)
        mpl_widget.SolutionsWidget.canvas.axe_1.clear()
        mpl_widget.SolutionsWidget.canvas.axe_2.clear()
        mpl_widget.SolutionsWidget.canvas.axe_3.clear()
        mpl_widget.exact_line, = mpl_widget.SolutionsWidget.canvas.axe_1.plot(x_points, y_exact,
                                                                              color=_exactColor,
                                                                              label="Analytical",
                                                                              markersize=6)
        mpl_widget.euler_line, = mpl_widget.SolutionsWidget.canvas.axe_1.plot(x_points, y_euler, ".",
                                                                              color=_eulerColor,
                                                                              label="Euler",
                                                                              markersize=4)
        mpl_widget.improved_euler_line, = mpl_widget.SolutionsWidget.canvas.axe_1.plot(x_points, y_improved_euler, ".",
                                                                                       color=_improvedEulerColor,
                                                                                       label="Improved Euler",
                                                                                       markersize=4)
        mpl_widget.euler_lte_line, = mpl_widget.SolutionsWidget.canvas.axe_2.plot(x_points, y_euler_lte,
                                                                                  color=_eulerColor,
                                                                                  label="Euler",
                                                                                  markersize=4)
        mpl_widget.improved_euler_lte_line, = mpl_widget.SolutionsWidget.canvas.axe_2.plot(x_points,
                                                                                           y_improved_euler_lte,
                                                                                           ".",
                                                                                           color=_improvedEulerColor,
                                                                                           label="Improved Euler",
                                                                                           markersize=4)
        mpl_widget.SolutionsWidget.canvas.axe_1.legend(loc='upper right')
        mpl_widget.SolutionsWidget.canvas.axe_1.set_title('Solutions')
        mpl_widget.SolutionsWidget.canvas.axe_2.legend(loc='upper left')
        mpl_widget.SolutionsWidget.canvas.axe_2.set_title('LTEs')
        self.update_GTE()
        self.show_euler()
        self.show_exact()
        mpl_widget.SolutionsWidget.canvas.draw()

    def update_GTE(self):
        mpl_widget = self.mpl_widget
        mpl_widget.grid.Update()
        x_points, y_euler, y_improved_euler = mpl_widget.GTE_grid.Calculate_GTE()
        mpl_widget.SolutionsWidget.canvas.axe_3.clear()
        mpl_widget.euler_gte_line, = mpl_widget.SolutionsWidget.canvas.axe_3.plot(x_points,
                                                                                  y_euler,
                                                                                  ".",
                                                                                  color=_eulerColor,
                                                                                  label="Euler",
                                                                                  markersize=4)
        mpl_widget.improved_euler_gte_line, = mpl_widget.SolutionsWidget.canvas.axe_3.plot(x_points,
                                                                                           y_improved_euler,
                                                                                           ".",
                                                                                           color=_improvedEulerColor,
                                                                                           label="Improved Euler",
                                                                                           markersize=4)
        mpl_widget.SolutionsWidget.canvas.axe_3.legend(loc='upper left')
        mpl_widget.SolutionsWidget.canvas.axe_3.set_title('GTEs')
        mpl_widget.euler_gte_line.set_visible(mpl_widget.checkBox_2.isChecked())
        mpl_widget.SolutionsWidget.canvas.draw()


app = QApplication([])
window = MatplotlibWidget()
window.show()
app.exec_()
