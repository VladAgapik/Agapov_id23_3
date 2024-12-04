import sys
import random
import math
from PyQt5.QtCore import Qt, QTimer, QRectF
from PyQt5.QtGui import QBrush, QColor, QPainter
from PyQt5.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsItem, QMainWindow, QApplication,
    QVBoxLayout, QWidget, QPushButton, QSpinBox, QLabel, QHBoxLayout
)

# Константы
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GROUND_LEVEL = WINDOW_HEIGHT
BIRD_SPEED = 4
SIT_TIME_MIN = 50
SIT_TIME_MAX = 120
DISAPPEAR_PROBABILITY = 0.2
BIRD_RADIUS = 15
POLE_TOP_PADDING = 0


# Класс Птицы
class Bird(QGraphicsItem):
    def __init__(self, poles):
        super().__init__()
        self.position = [random.randint(0, WINDOW_WIDTH), random.randint(0, GROUND_LEVEL - BIRD_RADIUS)]
        self.target_pole = random.choice(poles) if poles else None
        self.sit_time = random.randint(SIT_TIME_MIN, SIT_TIME_MAX)
        self.time_sitting = 0
        self.state = "flying"
        self.target_position = None
        self.radius = BIRD_RADIUS
        self.color = QColor("gray")
        self.sitting_point = None  # Точка посадки на столбе

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
            self.position = list(target)  # Достигли цели
        self.setPos(self.position[0], self.position[1])


# Класс Столба
class Pole(QGraphicsItem):
    def __init__(self, x, strength):
        super().__init__()
        self.position = (x, GROUND_LEVEL)
        self.strength = strength
        self.birds = []
        self.width = 30
        self.height = 100
        self.color = QColor("black")
        self.sitting_point = None  # Точка посадки для всех птиц

    def boundingRect(self):
        return QRectF(-self.width / 2, -self.height, self.width, self.height)

    def paint(self, painter, option, widget=None):
        painter.setBrush(QBrush(self.color))
        painter.drawRect(self.boundingRect())

    def is_overloaded(self):
        return len(self.birds) > self.strength

    def set_sitting_point(self):
        # Определяем точку посадки на верхушке столба
        self.sitting_point = (self.position[0], self.position[1] - self.height - BIRD_RADIUS - POLE_TOP_PADDING)


# Главное окно приложения
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Птицы и столбы")
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)

        # Сцена и вид
        self.scene = QGraphicsScene(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.view = QGraphicsView(self.scene)
        self.setCentralWidget(self.view)

        # Поля и птицы
        self.poles = []
        self.birds = []

        # Таймер
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_scene)
        self.timer.start(16)  # ~60 FPS

        # Панель управления
        self.control_panel = QWidget()
        self.control_layout = QHBoxLayout()
        self.control_panel.setLayout(self.control_layout)
        self.scene.addWidget(self.control_panel)

        # Кнопки и слайдеры
        self.add_pole_button = QPushButton("Добавить столб")
        self.add_pole_button.clicked.connect(self.add_pole)

        self.add_bird_button = QPushButton("Добавить птицу")
        self.add_bird_button.clicked.connect(self.add_bird)

        self.pole_strength_label = QLabel("Прочность столба:")
        self.pole_strength_spinbox = QSpinBox()
        self.pole_strength_spinbox.setRange(1, 10)
        self.pole_strength_spinbox.setValue(5)

        self.control_layout.addWidget(self.add_pole_button)
        self.control_layout.addWidget(self.pole_strength_label)
        self.control_layout.addWidget(self.pole_strength_spinbox)
        self.control_layout.addWidget(self.add_bird_button)

        # Добавить стартовые столбы
        for x in range(100, WINDOW_WIDTH, 200):
            self.add_pole(x)

    def add_pole(self, x=None):
        if not x:
            # Ищем уникальное место для нового столба
            while True:
                x = random.randint(50, WINDOW_WIDTH - 50)
                if not any(abs(x - pole.position[0]) < 100 for pole in self.poles):  # Уникальность
                    break
        strength = self.pole_strength_spinbox.value()
        pole = Pole(x, strength)
        self.poles.append(pole)
        self.scene.addItem(pole)
        pole.setPos(x, GROUND_LEVEL)

        # Устанавливаем единственную точку посадки на столбе
        pole.set_sitting_point()

    def add_bird(self):
        bird = Bird(self.poles)
        self.birds.append(bird)
        self.scene.addItem(bird)
        bird.setPos(*bird.position)

    def update_scene(self):
        for bird in self.birds[:]:  # Копия списка для удаления
            if bird.state == "flying" and bird.target_pole:
                # Птица летит к точке посадки на столбе
                bird.move_towards(bird.target_pole.sitting_point, BIRD_SPEED)
                if bird.position == list(bird.target_pole.sitting_point):  # Птица достигла точки посадки
                    bird.state = "sitting"
                    bird.time_sitting = 0
                    bird.target_pole.birds.append(bird)
                    bird.setPos(*bird.target_pole.sitting_point)  # Садится на точку

            elif bird.state == "sitting":
                bird.time_sitting += 1
                if bird.time_sitting >= bird.sit_time:  # Закончил сидеть
                    bird.state = "leaving"
                    if bird.target_pole:
                        bird.target_pole.birds.remove(bird)
                    bird.target_pole = None
            elif bird.state == "leaving":
                if not bird.target_position:
                    bird.target_position = [random.randint(0, WINDOW_WIDTH), random.randint(0, GROUND_LEVEL - BIRD_RADIUS)]
                bird.move_towards(bird.target_position, BIRD_SPEED)
                if bird.position == bird.target_position:
                    if random.random() < DISAPPEAR_PROBABILITY:
                        self.birds.remove(bird)
                        self.scene.removeItem(bird)
                    else:
                        bird.state = "flying"
                        bird.target_position = None
                        bird.target_pole = random.choice(self.poles)

        # Удаление перегруженных столбов
        for pole in self.poles[:]:
            if pole.is_overloaded():
                # Убираем столб
                self.poles.remove(pole)
                self.scene.removeItem(pole)
                # Птицы с удаленного столба начинают летать
                for bird in pole.birds[:]:
                    bird.state = "flying"
                    bird.target_pole = None
                    bird.target_position = None
                pole.birds.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
