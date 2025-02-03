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
MONSTER_MOVE_DELAY = 500  # Время в миллисекундах (500 мс = 0.5 сек)


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
    """Игрок получает урон только после первого движения"""
    if not player_moved:
        return False  # Не атакуем игрока, пока он не сделает первый шаг

    for enemy in enemies:
        if abs(player.x - enemy.x) <= 1 and abs(player.y - enemy.y) <= 1:
            player.hp -= 10
            print(f"Игрок получил урон! HP: {player.hp}")
            if player.hp <= 0:
                print("Игрок погиб!")
                return True
    return False


def spawn_enemies(game_map, rooms, num_enemies, player):
    """Создаёт врагов только в комнатах, избегая позиции игрока"""
    enemies = []
    potential_positions = []

    for room in rooms:
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                if not game_map.is_blocked(x, y) and (abs(player.x - x) > 2 or abs(player.y - y) > 2):
                    potential_positions.append((x, y))

    random.shuffle(potential_positions)
    for i in range(min(num_enemies, len(potential_positions))):
        x, y = potential_positions[i]
        enemies.append(Entity(x, y, "enemy", is_enemy=True))

    return enemies


def move_enemy(enemy, room, game_map, enemies):
    move_x, move_y = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
    new_x = enemy.x + move_x
    new_y = enemy.y + move_y

    if room.x1 < new_x < room.x2 and room.y1 < new_y < room.y2:
        if not game_map.is_blocked(new_x, new_y) and not is_occupied(new_x, new_y, enemies):
            enemy.move(move_x, move_y)
            print(f"Монстр {enemy} переместился на ({enemy.x}, {enemy.y})")



def main():
    screen_width, screen_height = 80, 45
    map_width, map_height = 80, 45
    size = (util.to_pixel(screen_width), util.to_pixel(screen_height))
    window = pygame.display.set_mode(size)
    pygame.display.set_caption("roguelike pygame tutorial")

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

    # Теперь монстры будут появляться только в комнатах
    enemies = spawn_enemies(game_map, rooms, 20, player)

    entities = [player] + enemies
    fov_map = initialize_fov(game_map)
    last_monster_move = pygame.time.get_ticks()

    running = True
    while running:
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            action = handle_keys(event)
            if action.get("exit"):
                running = False
            elif "move" in action:
                move_x, move_y = action["move"]
                new_x = player.x + move_x
                new_y = player.y + move_y

                if not game_map.is_blocked(new_x, new_y) and not is_occupied(new_x, new_y, enemies):
                    player.move(move_x, move_y)
                    fov_map = recompute_fov(game_map, player.x, player.y, 10, True)
                    player_moved = True  # Теперь игрок может получать урон

        if current_time - last_monster_move >= MONSTER_MOVE_DELAY:
            for enemy, room in zip(enemies, rooms):
                move_enemy(enemy, room, game_map, enemies)

            last_monster_move = current_time

        if check_damage_to_player(player, enemies):
            running = False

        window.fill(BLACK)
        render_all(window, entities, game_map, fov_map, colors)
        draw_health_bar(window, 10, 10, player.hp, player.max_hp)
        pygame.display.update()
        print(f"Текущее время: {current_time}, Последнее движение монстров: {last_monster_move}")

    pygame.quit()


if __name__ == "__main__":
    main()
