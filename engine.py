import pygame
import random
from entity import Entity
from fov_functions import initialize_fov, recompute_fov
from input_handlers import handle_keys
from map_objects.game_map import GameMap
from render_functions import render_all
import util

pygame.init()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)


def draw_health_bar(surface, x, y, current_hp, max_hp, width=100, height=10):
    """ Отрисовка полоски здоровья """
    pygame.draw.rect(surface, RED, (x, y, width, height))  # Фон (красный)
    hp_width = int((current_hp / max_hp) * width)
    pygame.draw.rect(surface, WHITE, (x, y, hp_width, height))  # Белая часть (текущее здоровье)


def is_occupied(x, y, enemies):
    """Проверяет, занята ли клетка монстром"""
    return any(enemy.x == x and enemy.y == y for enemy in enemies)


player_moved = False  # Флаг, который отслеживает движение игрока


def check_damage_to_player(player, enemies):
    """Проверяет, есть ли столкновение игрока с врагами, и наносит урон"""
    for enemy in enemies:
        if player.x == enemy.x and player.y == enemy.y:  # Столкновение
            player.hp -= 20
            print(f"Игрок получил урон при столкновении! HP: {player.hp}")
            if player.hp <= 0:
                print("Игрок погиб!")
                return True
        elif abs(player.x - enemy.x) <= 1 and abs(player.y - enemy.y) <= 1:  # Монстр рядом
            player.hp -= 10
            print(f"Игрок получил урон от близкого врага! HP: {player.hp}")
            if player.hp <= 0:
                print("Игрок погиб!")
                return True
    return False


def spawn_enemies(game_map, rooms, num_enemies, player):
    """Создаёт врагов только в комнатах, избегая стартовой комнаты игрока"""
    enemies = []
    potential_positions = []

    start_room = rooms[0]  # Первая комната — это комната игрока

    for room in rooms[1:]:  # Пропускаем стартовую комнату
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                if not game_map.is_blocked(x, y):
                    potential_positions.append((x, y))

    random.shuffle(potential_positions)
    for i in range(min(num_enemies, len(potential_positions))):
        x, y = potential_positions[i]
        enemies.append(Entity(x, y, "enemy", is_enemy=True))

    return enemies


def place_stair(rooms, player):
    """Создаёт клетку перехода в случайной комнате (кроме стартовой)"""
    possible_rooms = rooms[1:]  # Исключаем стартовую комнату
    chosen_room = random.choice(possible_rooms)  # Выбираем случайную комнату
    stair_x, stair_y = chosen_room.center()  # Клетка в центре комнаты
    return Entity(stair_x, stair_y, "stair")  # Создаём клетку перехода


def main():
    screen_width, screen_height = 80, 45
    map_width, map_height = 80, 45
    size = (util.to_pixel(screen_width), util.to_pixel(screen_height))
    window = pygame.display.set_mode(size)
    pygame.display.set_caption("Roguelike Pygame Tutorial")

    colors = {
        "dark_wall": Entity(0, 0, "dark_wall"),
        "dark_ground": Entity(0, 0, "dark_ground"),
        "light_wall": Entity(0, 0, "light_wall"),
        "light_ground": Entity(0, 0, "light_ground"),
    }

    player = Entity(int(screen_width / 2), int(screen_height / 2), "character")
    player.hp = 100
    player.max_hp = 100

    game_map = GameMap(map_width, map_height)
    rooms = game_map.make_map(30, 6, 10, map_width, map_height, player)

    # Создание врагов
    enemies = spawn_enemies(game_map, rooms, 20, player)
    entities = [player] + enemies
    stair = place_stair(rooms, player)
    entities.append(stair)  # Добавляем в список сущностей для рендера

    fov_map = initialize_fov(game_map)

    # Инициализация флага player_moved
    player_moved = False  # Игрок еще не двигался
    running = True

    while running:
        for event in pygame.event.get():
            action = handle_keys(event)
            if action.get("exit"):
                running = False
            elif "move" in action:
                move_x, move_y = action["move"]
                new_x = player.x + move_x
                new_y = player.y + move_y

                # Проверяем, является ли новая клетка стеной
                if game_map.is_blocked(new_x, new_y):
                    continue  # Не двигаемся, если клетка является стеной

                # Проверяем, занята ли клетка монстром
                if is_occupied(new_x, new_y, enemies):
                    # Наносим урон игроку за попытку зайти на монстра
                    if check_damage_to_player(player, enemies):
                        running = False  # Завершаем игру, если игрок погиб
                    continue  # Отменяем движение

                if player.x == stair.x and player.y == stair.y:
                    print("Игрок перешёл на новый уровень!")
                    game_map = GameMap(map_width, map_height)
                    rooms = game_map.make_map(30, 6, 10, map_width, map_height, player)
                    enemies = spawn_enemies(game_map, rooms, 20, player)
                    stair = place_stair(rooms, player)  # Создаём новую лестницу
                    entities = [player] + enemies + [stair]
                    fov_map = initialize_fov(game_map)

                # Если клетка свободна, выполняем движение
                player.move(move_x, move_y)
                fov_map = recompute_fov(game_map, player.x, player.y, 10, True)
                player_moved = True  # Игрок сделал шаг

        # Отрисовка
        window.fill(BLACK)
        render_all(window, entities, game_map, fov_map, colors, stair)
        draw_health_bar(window, 10, 10, player.hp, player.max_hp)  # Обновляем полоску здоровья
        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()
