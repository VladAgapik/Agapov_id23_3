import sys
import random
import math
from PyQt5.QtCore import Qt, QTimer, QRectF
from PyQt5.QtGui import QBrush, QColor, QPainter
from PyQt5.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsItem, QMainWindow, QApplication,
    QVBoxLayout, QWidget, QPushButton, QSpinBox, QLabel, QHBoxLayout, QGraphicsProxyWidget, QScrollBar
)

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GROUND_LEVEL = WINDOW_HEIGHT
BIRD_SPEED = 2
SIT_TIME_MIN = 50
SIT_TIME_MAX = 120
DISAPPEAR_PROBABILITY = 0.2
BIRD_RADIUS = 15
POLE_TOP_PADDING = 0
SCENE_WIDTH = 2000


class Bird(QGraphicsItem):
    def __init__(self, poles):
        super().__init__()
        self.position = [random.randint(0, SCENE_WIDTH), random.randint(0, GROUND_LEVEL - BIRD_RADIUS)]
        self.target_pole = random.choice(poles) if poles else None
        self.sit_time = random.randint(SIT_TIME_MIN, SIT_TIME_MAX)
        self.time_sitting = 0
        self.state = "flying"
        self.target_position = None
        self.radius = BIRD_RADIUS
        self.color = QColor("gray")
        self.sitting_point = None

    def boundingRect(self):
        return QRectF(-self.radius, -self.radius, self.radius * 2, self.radius * 2)

    def paint(self, painter, option, widget=None):
        painter.setBrush(QBrush(self.color))
        painter.drawEllipse(self.boundingRect())

    def move_towards(self, target, speed):
        bx, by = self.position
        tx, ty = target
        distance = math.hypot(tx - bx, ty - by)
        if distance > speed:
            self.position[0] += speed * (tx - bx) / distance
            self.position[1] += speed * (ty - by) / distance
        else:
            self.position = list(target)
        self.setPos(self.position[0], self.position[1])


class Pole(QGraphicsItem):
    def __init__(self, x, strength, main_window):
        super().__init__()
        self.position = (x, GROUND_LEVEL)
        self.strength = strength
        self.birds = []
        self.width = 30
        self.height = 100
        self.color = QColor("black")
        self.main_window = main_window
        self.sitting_point = None
        self.create_strength_controls()

    def boundingRect(self):
        return QRectF(-self.width / 2, -self.height, self.width, self.height)

    def paint(self, painter, option, widget=None):
        painter.setBrush(QBrush(self.color))
        painter.drawRect(self.boundingRect())

    def create_strength_controls(self):
        self.widget = QWidget()
        self.layout = QVBoxLayout()
        self.widget.setLayout(self.layout)

        self.label = QLabel(f"Прочность: {self.strength}")
        self.spinbox = QSpinBox()
        self.spinbox.setRange(1, 10)
        self.spinbox.setValue(self.strength)
        self.spinbox.valueChanged.connect(self.update_strength)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.spinbox)

        self.proxy_widget = QGraphicsProxyWidget()
        self.proxy_widget.setWidget(self.widget)
        self.main_window.scene.addItem(self.proxy_widget)
        self.update_widget_position()

    def update_strength(self, value):
        self.strength = value
        self.label.setText(f"Прочность: {self.strength}")

    def update_widget_position(self):
        if self.proxy_widget:
            self.proxy_widget.setPos(self.position[0] - 20, self.position[1] - self.height - 60)

    def remove_strength_controls(self):
        if self.proxy_widget:
            self.main_window.scene.removeItem(self.proxy_widget)
            self.proxy_widget = None

    def is_overloaded(self):
        return len(self.birds) > self.strength

    def set_sitting_point(self):
        self.sitting_point = (self.position[0], self.position[1] - self.height - BIRD_RADIUS - POLE_TOP_PADDING)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Птицы и столбы")
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)

        self.scene = QGraphicsScene(0, 0, SCENE_WIDTH, WINDOW_HEIGHT)
        self.view = QGraphicsView(self.scene)
        self.setCentralWidget(self.view)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        self.poles = []
        self.birds = []

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_scene)
        self.timer.start(12)

        self.control_panel = QWidget()
        self.control_layout = QHBoxLayout()
        self.control_panel.setLayout(self.control_layout)
        self.scene.addWidget(self.control_panel)

        self.add_pole_button = QPushButton("Добавить столб")
        self.add_pole_button.clicked.connect(self.add_pole)

        self.add_bird_button = QPushButton("Добавить птицу")
        self.add_bird_button.clicked.connect(self.add_bird)

        self.control_layout.addWidget(self.add_pole_button)
        self.control_layout.addWidget(self.add_bird_button)

        for x in range(100, WINDOW_WIDTH, 200):
            self.add_pole(x)

    def add_pole(self, x=None):
        if not x:
            while True:
                x = random.randint(50, SCENE_WIDTH - 50)
                if not any(abs(x - pole.position[0]) < 100 for pole in self.poles):
                    break
        strength = 5
        pole = Pole(x, strength, self)
        self.poles.append(pole)
        self.scene.addItem(pole)
        pole.setPos(x, GROUND_LEVEL)
        pole.set_sitting_point()

    def add_bird(self):
        bird = Bird(self.poles)
        self.birds.append(bird)
        self.scene.addItem(bird)
        bird.setPos(*bird.position)

    def update_scene(self):
        for bird in self.birds[:]:
            if bird.state == "flying" and bird.target_pole:
                bird.move_towards(bird.target_pole.sitting_point, BIRD_SPEED)
                if bird.position == list(bird.target_pole.sitting_point):
                    bird.state = "sitting"
                    bird.time_sitting = 0
                    bird.target_pole.birds.append(bird)
                    bird.setPos(*bird.target_pole.sitting_point)

            elif bird.state == "sitting":
                bird.time_sitting += 1
                if bird.time_sitting >= bird.sit_time:
                    bird.state = "leaving"
                    if bird.target_pole:
                        bird.target_pole.birds.remove(bird)
                    bird.target_pole = None
            elif bird.state == "leaving":
                if not bird.target_position:
                    bird.target_position = [random.randint(0, SCENE_WIDTH),
                                            random.randint(0, GROUND_LEVEL - BIRD_RADIUS)]
                bird.move_towards(bird.target_position, BIRD_SPEED)
                if bird.position == bird.target_position:
                    if random.random() < DISAPPEAR_PROBABILITY:
                        self.birds.remove(bird)
                        self.scene.removeItem(bird)
                    else:
                        bird.state = "flying"
                        bird.target_position = None
                        bird.target_pole = random.choice(self.poles)

        for pole in self.poles[:]:
            if pole.is_overloaded():
                self.poles.remove(pole)
                self.scene.removeItem(pole)

                for bird in pole.birds[:]:
                    bird.state = "leaving" if random.random() > DISAPPEAR_PROBABILITY else None
                    if bird.state is None:
                        self.birds.remove(bird)
                        self.scene.removeItem(bird)
                    else:
                        bird.target_pole = None
                        bird.target_position = None
                pole.birds.clear()
                pole.remove_strength_controls()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
