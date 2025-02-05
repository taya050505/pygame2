import util

def render_all(screen, entities, game_map, fov_map, colors, stair=None):
    for y in range(game_map.height):
        for x in range(game_map.width):
            visible = fov_map[x][y]
            wall = game_map.tiles[x][y].block_sight
            color = None
            if visible:
                color = colors["light_wall"].surface if wall else colors["light_ground"].surface
                game_map.tiles[x][y].explored = True
            elif game_map.tiles[x][y].explored:
                color = colors["dark_wall"].surface if wall else colors["dark_ground"].surface
            else:
                continue
            screen.blit(color, (util.to_pixel(x), util.to_pixel(y)))

    # Отрисовываем телепортационную клетку
    if game_map.teleport_pad is not None:  # Добавляем проверку на None
        x, y = game_map.teleport_pad
        if 0 <= x < len(fov_map) and 0 <= y < len(fov_map[0]) and fov_map[x][y]:
            screen.blit(colors["teleport"].surface, (util.to_pixel(x), util.to_pixel(y)))

    # Отрисовываем все сущности
    for entity in entities:
        draw_entity(screen, entity, fov_map)

def draw_entity(screen, entity, fov_map):
    """ Отрисовка сущности, если она в поле зрения или враг """
    if (0 <= entity.x < len(fov_map) and 0 <= entity.y < len(fov_map[0]) and
        (fov_map[entity.x][entity.y] or entity.is_enemy)):
        screen.blit(entity.surface, (util.to_pixel(entity.x), util.to_pixel(entity.y)))