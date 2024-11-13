import pygame
import random
import json
import math

# Инициализация pygame и настройка окна
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Параметры птиц и столбов
BIRD_SPEED = 2  # скорость перемещения птицы
SIT_TIME_MIN = 70  # минимальное время сидения в кадрах
SIT_TIME_MAX = 180  # максимальное время сидения в кадрах
NEW_BIRD_INTERVAL_MIN = 300  # минимальный интервал для появления новой птицы
NEW_BIRD_INTERVAL_MAX = 600  # максимальный интервал для появления новой птицы
DISAPPEAR_PROBABILITY = 0.1  # Вероятность улететь "с концами" (10%)

# Загрузка или инициализация данных
def load_initial_state():
    try:
        with open("initial_state.json") as f:
            data = json.load(f)
    except FileNotFoundError:
        # Если файл не найден, создаем начальные значения
        data = {
            "poles": [{"position": (x, HEIGHT - 100), "strength": random.randint(1, 5), "birds": []}
                      for x in range(100, WIDTH, 200)],
            "birds": [{"position": [random.randint(0, WIDTH), random.randint(0, HEIGHT)],
                       "target_pole": random.randint(0, len(range(100, WIDTH, 200)) - 1),
                       "state": "flying",
                       "sit_time": random.randint(SIT_TIME_MIN, SIT_TIME_MAX),
                       "time_sitting": 0} for _ in range(random.randint(5, 10))]  # случайное начальное число птиц
        }
        with open("initial_state.json", "w") as f:
            json.dump(data, f)

    # Проверка и инициализация всех ключей в столбах и птицах
    for pole in data.get("poles", []):
        pole.setdefault("position", (random.randint(100, WIDTH - 100), HEIGHT - 100))
        pole.setdefault("strength", random.randint(1, 5))
        pole.setdefault("birds", [])

    for bird in data.get("birds", []):
        bird.setdefault("position", [random.randint(0, WIDTH), random.randint(0, HEIGHT)])
        bird.setdefault("target_pole", random.randint(0, len(data["poles"]) - 1))
        bird.setdefault("state", "flying")
        bird.setdefault("sit_time", random.randint(SIT_TIME_MIN, SIT_TIME_MAX))
        bird.setdefault("time_sitting", 0)

    return data

state = load_initial_state()

# Функция для плавного перемещения птицы к цели
def move_towards(bird, target, speed):
    bx, by = bird["position"]
    tx, ty = target
    distance = math.hypot(tx - bx, ty - by)
    if distance > speed:
        bird["position"][0] += speed * (tx - bx) / distance
        bird["position"][1] += speed * (ty - by) / distance
    else:
        bird["position"] = list(target)  # Птица достигла цели

# Функция для добавления новой птицы
def add_new_bird(state):
    new_bird = {
        "position": [random.randint(0, WIDTH), random.randint(0, HEIGHT)],
        "target_pole": random.randint(0, len(state["poles"]) - 1),
        "state": "flying",
        "sit_time": random.randint(SIT_TIME_MIN, SIT_TIME_MAX),
        "time_sitting": 0
    }
    state["birds"].append(new_bird)

# Основной игровой цикл
next_bird_time = random.randint(NEW_BIRD_INTERVAL_MIN, NEW_BIRD_INTERVAL_MAX)  # случайное время для следующей птицы
frame_count = 0  # счётчик кадров для отслеживания времени
running = True
while running:
    screen.fill((255, 255, 255))  # Очистка экрана

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Появление новой птицы через случайный интервал времени
    if frame_count >= next_bird_time:
        add_new_bird(state)
        next_bird_time = frame_count + random.randint(NEW_BIRD_INTERVAL_MIN, NEW_BIRD_INTERVAL_MAX)

    # Обновление состояния птиц
    for bird in state["birds"][:]:  # Копия списка для безопасного удаления
        # Проверка, что target_pole находится в пределах списка poles
        pole_index = bird.get("target_pole", 0)
        if pole_index >= len(state["poles"]):
            pole_index = random.randint(0, len(state["poles"]) - 1)
            bird["target_pole"] = pole_index

        pole = state["poles"][pole_index]

        if bird["state"] == "flying":
            # Птица летит к столбу
            move_towards(bird, pole["position"], BIRD_SPEED)
            if bird["position"] == list(pole["position"]):  # Птица достигла столба
                bird["state"] = "sitting"
                bird["time_sitting"] = 0  # Сбрасываем таймер времени сидения
                pole["birds"].append(bird)  # Добавляем птицу на столб

        elif bird["state"] == "sitting":
            # Птица сидит на столбе и отсчитывает время
            bird["time_sitting"] += 1
            if bird["time_sitting"] >= bird["sit_time"]:  # Время сидения вышло
                bird["state"] = "leaving"
                if bird in pole["birds"]:
                    pole["birds"].remove(bird)  # Убираем птицу со столба

        elif bird["state"] == "leaving":
            # Птица улетает в случайную точку экрана
            if "target_position" not in bird:
                bird["target_position"] = [random.randint(0, WIDTH), random.randint(0, HEIGHT)]
            move_towards(bird, bird["target_position"], BIRD_SPEED)
            if bird["position"] == bird["target_position"]:
                # Проверка вероятности улета с концами
                if random.random() < DISAPPEAR_PROBABILITY:
                    state["birds"].remove(bird)  # Удаляем птицу из симуляции
                else:
                    bird["state"] = "flying"  # Птица снова ищет столб
                    bird["target_pole"] = random.randint(0, len(state["poles"]) - 1)
                    bird.pop("target_position", None)  # Убираем цель, чтобы установить новую позже

    # Отрисовка столбов и птиц
    for pole in state["poles"]:
        pygame.draw.rect(screen, (0, 0, 0), (*pole["position"], 30, 100))  # Отрисовка столба

    for bird in state["birds"]:
        pygame.draw.circle(screen, (120, 120, 120), (int(bird["position"][0]), int(bird["position"][1])), 15)  # Отрисовка птицы

    pygame.display.flip()  # Обновление экрана
    clock.tick(60)  # Ограничение FPS
    frame_count += 1  # Увеличиваем счётчик кадров

pygame.quit()