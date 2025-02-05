import random
from .rectangle import Rect
from .tile import Tile


class GameMap:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()
        self.teleport_pad = None  # Атрибут для хранения координат телепорта

    def initialize_tiles(self):
        tiles = [[Tile(True) for y in range(self.height)] for x in range(self.width)]
        return tiles

    def make_map(self, max_rooms, room_min_size, room_max_size, map_width, map_height, player):
        rooms = []
        for r in range(max_rooms):
            width = random.randint(room_min_size, room_max_size)
            height = random.randint(room_min_size, room_max_size)
            x = random.randint(0, map_width - width - 1)
            y = random.randint(0, map_height - height - 1)
            new_room = Rect(x, y, width, height)

            # Проверяем пересечение с существующими комнатами
            for other in rooms:
                if new_room.intersect(other):
                    break
            else:
                self.create_room(new_room)
                center = new_room.center()
                if len(rooms) == 0:
                    player.x = center[0]
                    player.y = center[1]
                else:
                    prev_center = rooms[-1].center()
                    if random.randint(0, 1) == 0:
                        self.create_h_tunnel(prev_center[0], center[0], prev_center[1])
                        self.create_v_tunnel(prev_center[1], center[1], center[0])
                    else:
                        self.create_v_tunnel(prev_center[1], center[1], prev_center[0])
                        self.create_h_tunnel(prev_center[0], center[0], center[1])
                rooms.append(new_room)

        self.spawn_teleport_pad(rooms, player)  # Случайно размещаем телепорт
        return rooms

    def spawn_teleport_pad(self, rooms, player):
        """Создает телепортационную клетку в случайной комнате (кроме комнаты спавна игрока)"""
        # Отфильтруем комнаты, исключая ту, где находится игрок
        available_rooms = [room for room in rooms if not room.contains(player.x, player.y)]

        if not available_rooms:
            self.teleport_pad = None  # Если нет доступных комнат, телепорт не создаётся
            return

        teleport_room = random.choice(available_rooms)
        potential_positions = [
            (x, y)
            for x in range(teleport_room.x1 + 1, teleport_room.x2)
            for y in range(teleport_room.y1 + 1, teleport_room.y2)
            if not self.tiles[x][y].blocked
        ]

        if not potential_positions:
            self.teleport_pad = None  # Если нет доступных позиций, телепорт не создаётся
            return

        x, y = random.choice(potential_positions)
        self.teleport_pad = (x, y)  # Сохраняем координаты телепорта

    def create_room(self, rect):
        for x in range(rect.x1 + 1, rect.x2):
            for y in range(rect.y1 + 1, rect.y2):
                self.tiles[x][y].blocked = False
                self.tiles[x][y].block_sight = False

    def create_h_tunnel(self, x1, x2, y):
        min_x = min(x1, x2)
        max_x = max(x1, x2)
        for x in range(min_x, max_x + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def create_v_tunnel(self, y1, y2, x):
        min_y = min(y1, y2)
        max_y = max(y1, y2)
        for y in range(min_y, max_y + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def is_blocked(self, x, y):
        return self.tiles[x][y].blocked