# Вариант №2

import sys
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QSpinBox, QPushButton, QWidget
)
from PyQt5.QtCore import Qt, QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

g = 9.81

class ProjectileSimulation(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Симуляция полета снаряда")
        self.setGeometry(100, 100, 800, 600)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)

        self.time_elapsed = 0
        self.x_data = []
        self.y_data = []

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        controls_layout = QHBoxLayout()

        controls_layout.addWidget(QLabel("Начальная скорость (м/с):"))
        self.v0_spinbox = QSpinBox()
        self.v0_spinbox.setRange(1, 100)
        self.v0_spinbox.setValue(20)
        controls_layout.addWidget(self.v0_spinbox)

        controls_layout.addWidget(QLabel("Угол запуска (°):"))
        self.angle_slider = QSlider(Qt.Horizontal)
        self.angle_slider.setRange(0, 90)
        self.angle_slider.setValue(45)
        controls_layout.addWidget(self.angle_slider)

        controls_layout.addWidget(QLabel("Масса (кг):"))
        self.mass_spinbox = QSpinBox()
        self.mass_spinbox.setRange(1, 50)
        self.mass_spinbox.setValue(1)
        controls_layout.addWidget(self.mass_spinbox)

        self.start_button = QPushButton("Запуск")
        self.start_button.clicked.connect(self.start_animation)
        controls_layout.addWidget(self.start_button)

        self.reset_button = QPushButton("Сброс")
        self.reset_button.clicked.connect(self.reset_simulation)
        controls_layout.addWidget(self.reset_button)

        layout.addLayout(controls_layout)

    def calculate_trajectory(self):
        v0 = self.v0_spinbox.value()
        angle = np.radians(self.angle_slider.value())
        t_flight = 2 * v0 * np.sin(angle) / g  # Время полета
        t = np.linspace(0, t_flight, num=500)

        x = v0 * np.cos(angle) * t
        y = v0 * np.sin(angle) * t - 0.5 * g * t**2
        return x, y

    def start_animation(self):
        self.x_data, self.y_data = self.calculate_trajectory()

        if len(self.x_data) == 0 or len(self.y_data) == 0:
            return

        self.ax.clear()
        self.ax.set_xlim(0, max(self.x_data) * 1.1)
        self.ax.set_ylim(0, max(self.y_data) * 1.1)
        self.ax.set_xlabel("Расстояние (м)")
        self.ax.set_ylabel("Высота (м)")
        self.canvas.draw()

        self.time_elapsed = 0
        self.timer.start(20)

    def update_animation(self):
        if self.time_elapsed < len(self.x_data):
            x = self.x_data[: self.time_elapsed + 1]
            y = self.y_data[: self.time_elapsed + 1]
            self.ax.clear()
            self.ax.plot(x, y, "r-", label="Траектория")
            self.ax.scatter(x[-1], y[-1], color="blue", label="Снаряд")
            self.ax.set_xlim(0, max(self.x_data) * 1.1)
            self.ax.set_ylim(0, max(self.y_data) * 1.1)
            self.ax.set_xlabel("Расстояние (м)")
            self.ax.set_ylabel("Высота (м)")
            self.ax.legend()
            self.canvas.draw()
            self.time_elapsed += 1
        else:
            self.timer.stop()

    def reset_simulation(self):
        self.timer.stop()
        self.v0_spinbox.setValue(20)
        self.angle_slider.setValue(45)
        self.mass_spinbox.setValue(1)
        self.ax.clear()
        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(0, 10)
        self.ax.set_xlabel("Расстояние (м)")
        self.ax.set_ylabel("Высота (м)")
        self.canvas.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProjectileSimulation()
    window.show()
    sys.exit(app.exec_())


