import tkinter
import math


class MovingPointApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Движущаяся точка по окружности")

        # размеры окна и окружности
        self.canvas_size = 600
        self.radius = 200

        # область для рисования
        self.canvas = tk.Canvas(self.root, width=self.canvas_size, height=self.canvas_size, bg="white")
        self.canvas.pack()

        # центр окружности
        self.center_x = self.canvas_size // 2
        self.center_y = self.canvas_size // 2

        # параметры движения
        self.angular_speed = 0.05  # угловая скорость
        self.angle = 0  # начальный угол

        # запуск анимации
        self.update_point()

    def update_point(self):
        # координаты точки на окружности
        x = self.center_x + self.radius * math.cos(self.angle)
        y = self.center_y + self.radius * math.sin(self.angle)

        # очищаем холст и рисуем окружность и точку
        self.canvas.delete("all")

        # рисуем окружность
        self.canvas.create_oval(self.center_x - self.radius, self.center_y - self.radius,
                                self.center_x + self.radius, self.center_y + self.radius,
                                outline="black")

        # рисуем движущуюся точку
        self.canvas.create_oval(x - 10, y - 10, x + 10, y + 10, fill="blue")

        # обновляем угол для следующего кадра
        self.angle += self.angular_speed

        # повторяем анимацию через 20 миллисекунд
        self.root.after(20, self.update_point)

    # функция для изменения скорости и направления движения точки
    def set_speed(self, speed):
        self.angular_speed = speed


# создание окна
root = tkinter.Tk()

# создание объекта приложения
app = MovingPointApp(root)

# возможность изменить скорость
app.set_speed(0.08)

# запуск главного окна
root.mainloop()