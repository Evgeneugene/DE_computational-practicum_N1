from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
import math
from matplotlib.backends.backend_qt5agg import (NavigationToolbar2QT  as  NavigationToolbar)
from abc import ABCMeta, abstractmethod, ABC

_eulerColor = "#d9138a"
_exactColor = "#12a4d9"
_improvedEulerColor = "#e2d810"
_rungeKuttaColor = "#322e2f"


# Initial equation, derivative of Y
def dy(x, y):
    return math.exp(y) - 2 / x


def C(xi, yi):
    return (math.exp(-yi) - xi) / xi / xi


# Exact solution of the equation
def f(x, c):
    return -math.log(c * x * x + x)


class IncorrectInput(Exception):
    pass


# Abstract class for Solution Methods
class Solution(metaclass=ABCMeta):
    def __init__(self, grid):
        self.x_points = grid.x_points
        self.y_points = []
        self.grid = grid

    @abstractmethod
    def Calculate_points(self):
        pass


# Abstract class for Numerical Solutions
class NumericalSolution(Solution, metaclass=ABCMeta):
    def __init__(self, grid):
        super().__init__(grid)
        self.max_error = None

    def GetMaxError(self, exact):
        max_error = 0
        for i in range(0, len(exact.x_points)):
            max_error = max(abs(self.y_points[i] - exact.y_points[i]), max_error)
        self.max_error = max_error
        return max_error


class ExactSolution(Solution):
    def Calculate_points(self):
        self.y_points = []
        self.x_points = self.grid.x_points
        print("CALCULATE POINTS: x_points =", self.grid.xi)
        c = C(self.grid.xi, self.grid.yi)
        for i in range(0, self.grid.n):
            x = self.grid.x_points[i]
            print("C:", c)
            if min(0, -1 / c) <= x <= max(0, -1 / c):
                error = "Error: function is undefined in x = " + str(x)
                raise IncorrectInput(error)
            y = f(self.grid.x_points[i], c)
            self.y_points.append(y)
        return self.y_points


class EulerSolution(NumericalSolution):
    def Calculate_points(self):
        self.y_points = []
        self.x_points = self.grid.x_points
        y = self.grid.yi
        self.y_points.append(y)
        for i in range(1, self.grid.n):
            y = y + dy(self.grid.x_points[i - 1], y) * self.grid.h
            self.y_points.append(y)
        return self.y_points


class ImprovedEulerSolution(NumericalSolution):
    def Calculate_points(self):
        self.y_points = []
        self.x_points = self.grid.x_points
        y = self.grid.yi
        self.y_points.append(y)
        for i in range(1, self.grid.n):
            x = self.grid.x_points[i - 1]
            h = self.grid.h
            y = y + (dy(x, y) + dy(x + h, y + h * dy(x, y))) / 2 * h
            self.y_points.append(y)
        return self.y_points


class RungeKuttaSolution(NumericalSolution):
    def Calculate_points(self):
        self.y_points = []
        self.x_points = self.grid.x_points
        y = self.grid.yi
        self.y_points.append(y)
        for i in range(1, self.grid.n):
            x = self.grid.x_points[i - 1]
            h = self.grid.h
            k1 = h * dy(x, y)
            k2 = h * dy(x + h / 2, y + k1 / 2)
            k3 = h * dy(x + h / 2, y + k2 / 2)
            k4 = h * dy(x + h, y + k3)
            y = y + (k1 + 2 * k2 + 2 * k3 + k4) / 6
            self.y_points.append(y)
        print("RungeKutta: ", self.y_points)
        print("XS: ", self.x_points)
        return self.y_points


class Grid:
    def __init__(self, mpl_widget=None):
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
        if self.xi <= 0 <= self.n:
            raise IncorrectInput(
                "Error: Since numerical methods work only for smooth equations, x domain should not include 0 "
                "values")
        if self.xi > self.xf:
            raise IncorrectInput("Error: x0 is greater that X")
        if self.h > 1:
            raise IncorrectInput("Error: the size of steps should not be more than 1")
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
        self.y_runge_kutta = []

    def Calculate_LTE(self, exact, euler, improved_euler, runge_kutta):
        self.x_points = exact.x_points
        self.y_euler = []
        self.y_improved_euler = []
        self.y_runge_kutta = []
        self.y_euler.append(exact.y_points[0] - euler.y_points[0])
        self.y_improved_euler.append(exact.y_points[0] - improved_euler.y_points[0])
        self.y_runge_kutta.append(exact.y_points[0] - runge_kutta.y_points[0])
        n = len(self.x_points)
        for i in range(1, n):
            y_euler = abs(exact.y_points[i] - euler.y_points[i])
            y_improved_euler = abs(exact.y_points[i] - improved_euler.y_points[i])
            y_runge_kutta = abs(exact.y_points[i] - runge_kutta.y_points[i])
            self.y_euler.append(y_euler)
            self.y_improved_euler.append(y_improved_euler)
            self.y_runge_kutta.append(y_runge_kutta)
        return self.y_euler, self.y_improved_euler, self.y_runge_kutta


class GTE_Grid:
    def __init__(self, mpl_widget):
        self.x_points = []
        self.y_euler = []
        self.y_improved_euler = []
        self.y_runge_kutta = []
        self.n0 = int(mpl_widget.lineEdit_GE_from.text())
        self.N = int(mpl_widget.lineEdit_GE_to.text())
        self.xi = mpl_widget.grid.xi
        self.xf = mpl_widget.grid.xf
        self.yi = mpl_widget.grid.yi
        self.mpl_widget = mpl_widget

    def Calculate_GTE(self):
        self.n0 = int(self.mpl_widget.lineEdit_GE_from.text())
        self.N = int(self.mpl_widget.lineEdit_GE_to.text())
        if self.n0 < 10 or self.N > 500:
            raise IncorrectInput("Error: n0 and N should be in range from 10 to 500")
        n0 = self.n0
        N = self.N
        xi = self.mpl_widget.grid.xi
        xf = self.mpl_widget.grid.xf
        yi = self.mpl_widget.grid.yi
        x_points, y_euler_error, y_improved_euler_error, y_runge_kutta_error = [], [], [], []
        for i in range(n0, N + 1):
            h = float(((xf - xi) / i))
            x = xi
            temp = Grid()
            temp_x_points = [xi]
            for j in range(1, i):
                x = x + h
                temp_x_points.append(x)
            temp.x_points = temp_x_points
            temp.xi = xi
            temp.yi = yi
            temp.h = h
            temp.n = i

            exact_solution = ExactSolution(temp)
            euler_solution = EulerSolution(temp)
            improved_euler_solution = ImprovedEulerSolution(temp)
            runge_kutta_solution = RungeKuttaSolution(temp)
            exact_solution.Calculate_points()
            euler_solution.Calculate_points()
            improved_euler_solution.Calculate_points()
            runge_kutta_solution.Calculate_points()

            print("GTE:", euler_solution.y_points)
            y_euler_error.append(euler_solution.GetMaxError(exact_solution))
            y_improved_euler_error.append(improved_euler_solution.GetMaxError(exact_solution))
            y_runge_kutta_error.append(runge_kutta_solution.GetMaxError(exact_solution))
            x_points.append(i)
        self.x_points = x_points
        self.y_euler = y_euler_error
        self.y_improved_euler = y_improved_euler_error
        self.y_runge_kutta = y_runge_kutta_error
        print("GTE:\n", x_points, '\n', y_euler_error, '\n', y_improved_euler_error, '\n', y_runge_kutta_error)
        return x_points, y_euler_error, y_improved_euler_error, y_runge_kutta_error


class MatplotlibWidget(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        loadUi("DE.ui", self)
        # Setting the initial view of GUI
        self.setWindowTitle("Computational practicum")
        self.checkBox.setChecked(True)
        self.checkBox_2.setChecked(True)
        self.checkBox_3.setChecked(True)
        self.checkBox_4.setChecked(True)
        self.addToolBar(NavigationToolbar(self.SolutionsWidget.canvas, self))

        # Declaration of different lines in graphs
        self.exact_line = None
        self.euler_line = None
        self.improved_euler_line = None
        self.runge_kutta_line = None
        self.euler_lte_line = None
        self.improved_euler_lte_line = None
        self.runge_kutta_lte_line = None
        self.euler_gte_line = None
        self.improved_euler_gte_line = None
        self.runge_kutta_gte_line = None

        # Initialization of grids for 3 different charts
        self.grid = Grid(self)
        self.LTE_grid = LTE_Grid()
        self.GTE_grid = GTE_Grid(self)

        # Initialization of solution classes which are used to get Y values
        self.exactSolution = ExactSolution(self.grid)
        self.eulerSolution = EulerSolution(self.grid)
        self.improvedEulerSolution = ImprovedEulerSolution(self.grid)
        self.rungeKuttaSolution = RungeKuttaSolution(self.grid)

        # Setting the Controller of changes of the graph
        self.controller = Controller(self)
        self.pushButton_plot.clicked.connect(self.controller.update_graph)
        self.pushButton_global_error.clicked.connect(self.controller.update_GTE)
        self.checkBox.clicked.connect(self.controller.show_exact)
        self.checkBox_2.clicked.connect(self.controller.show_euler)
        self.checkBox_3.clicked.connect(self.controller.show_improved_euler)
        self.checkBox_4.clicked.connect(self.controller.show_runge_kutta)
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

    def show_runge_kutta(self):
        self.mpl_widget.runge_kutta_line.set_visible(self.mpl_widget.checkBox_4.isChecked())
        self.mpl_widget.runge_kutta_lte_line.set_visible(self.mpl_widget.checkBox_4.isChecked())
        self.mpl_widget.runge_kutta_gte_line.set_visible(self.mpl_widget.checkBox_4.isChecked())
        self.mpl_widget.checkBox_4.setChecked(self.mpl_widget.checkBox_4.isChecked())
        self.mpl_widget.SolutionsWidget.canvas.draw()

    def update_graph(self):
        mpl_widget = self.mpl_widget
        try:
            mpl_widget.grid.Update()
            y_exact = mpl_widget.exactSolution.Calculate_points()
        except IncorrectInput as error:
            self.Error_message(str(error))
            return
        x_points = mpl_widget.grid.x_points
        y_euler = mpl_widget.eulerSolution.Calculate_points()
        y_improved_euler = mpl_widget.improvedEulerSolution.Calculate_points()
        y_runge_kutta = mpl_widget.rungeKuttaSolution.Calculate_points()
        y_euler_lte, y_improved_euler_lte, y_runge_kutta_lte = mpl_widget.LTE_grid.Calculate_LTE(
            mpl_widget.exactSolution,
            mpl_widget.eulerSolution,
            mpl_widget.improvedEulerSolution,
            mpl_widget.rungeKuttaSolution)

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
        mpl_widget.runge_kutta_line, = mpl_widget.SolutionsWidget.canvas.axe_1.plot(x_points, y_runge_kutta, ".",
                                                                                    color=_rungeKuttaColor,
                                                                                    label="Runge-Kutta",
                                                                                    markersize=4)

        mpl_widget.euler_lte_line, = mpl_widget.SolutionsWidget.canvas.axe_2.plot(x_points, y_euler_lte,
                                                                                  color=_eulerColor,
                                                                                  label="Euler",
                                                                                  markersize=4)
        mpl_widget.improved_euler_lte_line, = mpl_widget.SolutionsWidget.canvas.axe_2.plot(x_points,
                                                                                           y_improved_euler_lte,
                                                                                           color=_improvedEulerColor,
                                                                                           label="Improved Euler",
                                                                                           markersize=4)
        mpl_widget.runge_kutta_lte_line, = mpl_widget.SolutionsWidget.canvas.axe_2.plot(x_points,
                                                                                        y_runge_kutta_lte,
                                                                                        color=_rungeKuttaColor,
                                                                                        label="Runge-Kutta",
                                                                                        markersize=4)
        mpl_widget.SolutionsWidget.canvas.axe_1.legend(loc='upper right')
        mpl_widget.SolutionsWidget.canvas.axe_1.set_title('Solutions')
        mpl_widget.SolutionsWidget.canvas.axe_1.grid()
        mpl_widget.SolutionsWidget.canvas.axe_1.set_xlabel("x")
        mpl_widget.SolutionsWidget.canvas.axe_1.set_ylabel("y")
        mpl_widget.SolutionsWidget.canvas.axe_2.legend(loc='upper left')
        mpl_widget.SolutionsWidget.canvas.axe_2.set_title('LTEs')
        mpl_widget.SolutionsWidget.canvas.axe_2.grid()
        mpl_widget.SolutionsWidget.canvas.axe_2.set_xlabel("x")
        mpl_widget.SolutionsWidget.canvas.axe_2.set_ylabel("y error")
        self.update_GTE()
        self.show_euler()
        self.show_exact()
        mpl_widget.SolutionsWidget.canvas.draw()

    def update_GTE(self):
        mpl_widget = self.mpl_widget
        mpl_widget.grid.Update()
        try:
            x_points, y_euler, y_improved_euler, y_runge_kutta = mpl_widget.GTE_grid.Calculate_GTE()
        except IncorrectInput as error:
            self.Error_message(str(error))
            return
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
        mpl_widget.runge_kutta_gte_line, = mpl_widget.SolutionsWidget.canvas.axe_3.plot(x_points,
                                                                                        y_runge_kutta,
                                                                                        ".",
                                                                                        color=_rungeKuttaColor,
                                                                                        label="Runge-Kutta",
                                                                                        markersize=4)
        mpl_widget.SolutionsWidget.canvas.axe_3.legend(loc='upper left')
        mpl_widget.SolutionsWidget.canvas.axe_3.set_title('GTEs')
        mpl_widget.SolutionsWidget.canvas.axe_3.grid()
        mpl_widget.SolutionsWidget.canvas.axe_3.set_xlabel("n")
        mpl_widget.SolutionsWidget.canvas.axe_3.set_ylabel("Max Error")
        mpl_widget.euler_gte_line.set_visible(mpl_widget.checkBox_2.isChecked())
        mpl_widget.SolutionsWidget.canvas.draw()

    def Error_message(self, text):
        msg = QMessageBox()
        msg.setWindowTitle("Error!")
        msg.setText(text)
        msg.exec_()


app = QApplication([])
window = MatplotlibWidget()
window.show()
app.exec_()
