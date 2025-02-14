import pygame
import random
from entity import Entity, Potion
from fov_functions import initialize_fov, recompute_fov
from input_handlers import handle_keys
from map_objects.game_map import GameMap
from render_functions import render_all
import util
import sys
from start_screen import show_start_screen
from game_over_screen import show_game_over_screen

pygame.init()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)


def draw_health_bar(surface, x, y, current_hp, max_hp, width=100, height=10):
    pygame.draw.rect(surface, RED, (x, y, width, height))
    hp_width = int((current_hp / max_hp) * width)
    pygame.draw.rect(surface, WHITE, (x, y, hp_width, height))


def is_occupied(x, y, enemies):
    return any(enemy.x == x and enemy.y == y for enemy in enemies)


def check_damage_to_player(player, enemies, window):
    for enemy in enemies:
        if player.x == enemy.x and player.y == enemy.y:
            player.hp -= 20
            print(f"Игрок получил урон при столкновении! HP: {player.hp}")
            if player.hp <= 0:
                print("Игрок погиб!")
                return show_game_over_screen(window)
        elif abs(player.x - enemy.x) <= 1 and abs(player.y - enemy.y) <= 1:
            player.hp -= 10
            print(f"Игрок получил урон от близкого врага! HP: {player.hp}")
            if player.hp <= 0:
                print("Игрок погиб!")
                return show_game_over_screen(window)
    return False


def spawn_enemies(game_map, rooms, num_enemies, player, occupied_positions):
    enemies = []
    potential_positions = []

    for room in rooms[1:]:  # Пропускаем стартовую комнату
        for x in range(room.x1 + 1, room.x2 - 1):
            for y in range(room.y1 + 1, room.y2 - 1):
                if not game_map.is_blocked(x, y) and is_position_free(x, y, occupied_positions):
                    potential_positions.append((x, y))

    random.shuffle(potential_positions)
    for _ in range(min(num_enemies, len(potential_positions))):
        x, y = potential_positions.pop()
        enemy = Entity(x, y, "enemy", is_enemy=True)
        enemies.append(enemy)
        occupied_positions.add((x, y))  # Добавляем координаты в список занятых

    return enemies


def place_stair(rooms, occupied_positions):
    possible_rooms = [room for room in rooms[1:] if room.center() not in occupied_positions]

    if not possible_rooms:
        return None  # Если все комнаты заняты, не создаём лестницу

    chosen_room = random.choice(possible_rooms)
    stair_x, stair_y = chosen_room.center()

    occupied_positions.add((stair_x, stair_y))  # Помечаем место занятым
    return Entity(stair_x, stair_y, "stair")


def spawn_potions(rooms, max_potions, occupied_positions):
    potions = []
    potential_positions = []

    for room in rooms[1:]:
        for x in range(room.x1 + 1, room.x2 - 1):
            for y in range(room.y1 + 1, room.y2 - 1):
                if is_position_free(x, y, occupied_positions):
                    potential_positions.append((x, y))

    random.shuffle(potential_positions)
    num_potions = random.randint(0, max_potions)

    for _ in range(min(num_potions, len(potential_positions))):
        x, y = potential_positions.pop()
        effect = "heal" if random.random() < 0.5 else "harm"
        potions.append(Potion(x, y, effect))
        occupied_positions.add((x, y))  # Помечаем место занятым

    return potions


def is_position_free(x, y, occupied_positions):
    """ Проверяет, свободна ли позиция (x, y). """
    return (x, y) not in occupied_positions


def main():
    screen_width, screen_height = 80, 45
    map_width, map_height = 80, 45
    size = (util.to_pixel(screen_width), util.to_pixel(screen_height))
    window = pygame.display.set_mode(size)
    pygame.display.set_caption("Лабиринт вечной ночи")

    if not show_start_screen(window):
        pygame.quit()
        sys.exit()

    running = True
    while running:
        colors = {
            "dark_wall": Entity(0, 0, "dark_wall"),
            "dark_ground": Entity(0, 0, "dark_ground"),
            "light_wall": Entity(0, 0, "light_wall"),
            "light_ground": Entity(0, 0, "light_ground"),
        }
        occupied_positions = set()
        player = Entity(int(screen_width / 2), int(screen_height / 2), "character")
        player.hp = 100
        player.max_hp = 100
        occupied_positions.add((player.x, player.y))

        game_map = GameMap(map_width, map_height)
        rooms = game_map.make_map(30, 6, 10, map_width, map_height, player)

        enemies = spawn_enemies(game_map, rooms, random.randint(15, 55), player, occupied_positions)
        entities = [player] + enemies

        stair = place_stair(rooms, occupied_positions)
        entities.append(stair)
        potions = spawn_potions(rooms, 10, occupied_positions)  # Создаём зелья (от 0 до 3 штук)
        entities.extend(potions)
        entities = [player] + enemies + ([stair] if stair else []) + potions

        fov_map = initialize_fov(game_map)

        game_running = True
        while game_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:  # Обработка закрытия окна
                    running = False
                    game_running = False
                    break
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
                        if check_damage_to_player(player, enemies, window):
                            game_running = False
                            restart_game = show_game_over_screen(window)
                            if not restart_game:  # Если нет, завершаем игру
                                running = False
                            break
                        continue

                    if player.x == stair.x and player.y == stair.y:
                        print("Игрок перешёл на новый уровень!")
                        game_map = GameMap(map_width, map_height)
                        rooms = game_map.make_map(30, 6, 10, map_width, map_height, player)
                        enemies = spawn_enemies(game_map, rooms, 20, player, occupied_positions)
                        stair = place_stair(rooms, occupied_positions)
                        entities = [player] + enemies + [stair]
                        fov_map = initialize_fov(game_map)
                    for potion in potions[:]:
                        if player.x == potion.x and player.y == potion.y:
                            potions.remove(potion)
                            entities.remove(potion)
                            if potion.effect == "heal":
                                player.hp = min(player.max_hp, player.hp + random.choice([10, 20, 30, 40]))
                                print("Вы выпили лечебное зелье! +30 HP")
                            else:
                                player.hp -= random.choice([10, 20, 30, 40])
                                print("Вы выпили проклятое зелье! -20 HP")
                            break

                    player.move(move_x, move_y)
                    fov_map = recompute_fov(game_map, player.x, player.y, 10, True)

            if not game_running:
                break

            window.fill(BLACK)
            render_all(window, entities, game_map, fov_map, colors, stair)
            draw_health_bar(window, 10, 10, player.hp, player.max_hp)
            pygame.display.update()

        if not running:
            break

    pygame.quit()


if __name__ == "__main__":
    main()
