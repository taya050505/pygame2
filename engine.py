import pygame
import random
from entity import Entity
from fov_functions import initialize_fov, recompute_fov
from input_handlers import handle_keys
from map_objects.game_map import GameMap
from render_functions import render_all
import util
import sys
from start_screen import show_start_screen
from game_over_screen import show_game_over_screen  # Импортируем экран проигрыша

pygame.init()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)


def draw_health_bar(surface, x, y, current_hp, max_hp, width=100, height=10):
    pygame.draw.rect(surface, RED, (x, y, width, height))  # Фон (красный)
    hp_width = int((current_hp / max_hp) * width)
    pygame.draw.rect(surface, WHITE, (x, y, hp_width, height))  # Белая часть (текущее здоровье)


def is_occupied(x, y, enemies):
    return any(enemy.x == x and enemy.y == y for enemy in enemies)


# Проверка урона игроку
def check_damage_to_player(player, enemies, window):
    for enemy in enemies:
        if player.x == enemy.x and player.y == enemy.y:  # Столкновение
            player.hp -= 20
            print(f"Игрок получил урон при столкновении! HP: {player.hp}")
            if player.hp <= 0:
                print("Игрок погиб!")
                return show_game_over_screen(window)  # Показываем экран проигрыша
        elif abs(player.x - enemy.x) <= 1 and abs(player.y - enemy.y) <= 1:  # Монстр рядом
            player.hp -= 10
            print(f"Игрок получил урон от близкого врага! HP: {player.hp}")
            if player.hp <= 0:
                print("Игрок погиб!")
                return show_game_over_screen(window)  # Показываем экран проигрыша
    return False


# Генерация врагов
def spawn_enemies(game_map, rooms, num_enemies, player):
    enemies = []
    potential_positions = []
    start_room = rooms[0]
    for room in rooms[1:]:
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                if not game_map.is_blocked(x, y):
                    potential_positions.append((x, y))
    random.shuffle(potential_positions)
    for i in range(min(num_enemies, len(potential_positions))):
        x, y = potential_positions[i]
        enemies.append(Entity(x, y, "enemy", is_enemy=True))
    return enemies


# Размещение лестницы
def place_stair(rooms, player):
    possible_rooms = rooms[1:]
    chosen_room = random.choice(possible_rooms)
    stair_x, stair_y = chosen_room.center()
    return Entity(stair_x, stair_y, "stair")


# Основная функция игры
def main():
    screen_width, screen_height = 80, 45
    map_width, map_height = 80, 45
    size = (util.to_pixel(screen_width), util.to_pixel(screen_height))
    window = pygame.display.set_mode(size)
    pygame.display.set_caption("Roguelike Pygame Tutorial")

    # Показываем стартовый экран
    if not show_start_screen(window):
        pygame.quit()
        sys.exit()

    running = True
    while running:
        # Инициализация карты, игрока, врагов и т.д.
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

        # Создание лестницы
        stair = place_stair(rooms, player)
        entities.append(stair)

        fov_map = initialize_fov(game_map)
        player_moved = False

        game_running = True
        while game_running:
            for event in pygame.event.get():
                action = handle_keys(event)
                if action.get("exit"):
                    game_running = False
                elif "move" in action:
                    move_x, move_y = action["move"]
                    new_x = player.x + move_x
                    new_y = player.y + move_y

                    if game_map.is_blocked(new_x, new_y):
                        continue
                    if is_occupied(new_x, new_y, enemies):
                        if check_damage_to_player(player, enemies, window):  # Если игрок погиб
                            game_running = False  # Завершаем текущий игровой цикл
                            if not show_game_over_screen(window):  # Если игрок выбрал "Выйти"
                                running = False  # Выходим из главного цикла
                            break  # Выходим из внутреннего цикла
                        continue
                    if player.x == stair.x and player.y == stair.y:
                        print("Игрок перешёл на новый уровень!")
                        game_map = GameMap(map_width, map_height)
                        rooms = game_map.make_map(30, 6, 10, map_width, map_height, player)
                        enemies = spawn_enemies(game_map, rooms, 20, player)
                        stair = place_stair(rooms, player)
                        entities = [player] + enemies + [stair]
                        fov_map = initialize_fov(game_map)

                    player.move(move_x, move_y)
                    fov_map = recompute_fov(game_map, player.x, player.y, 10, True)
                    player_moved = True

            window.fill(BLACK)
            render_all(window, entities, game_map, fov_map, colors, stair)
            draw_health_bar(window, 10, 10, player.hp, player.max_hp)
            pygame.display.update()

        if not running:  # Если игрок выбрал "Выйти" на экране проигрыша
            break  # Выходим из главного цикла

    pygame.quit()


if __name__ == "__main__":
    main()
