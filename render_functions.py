import util


def render_all(screen, entities, game_map, fov_map, colors):
    for y in range(game_map.height):
        for x in range(game_map.width):
            visible = fov_map[x][y]
            wall = game_map.tiles[x][y].block_sight

            color = None
            if visible:
                color = colors["light_wall"].surface if wall else colors["light_ground"].surface
                game_map.tiles[x][y].explored = True  # Запоминаем виденные клетки
            elif game_map.tiles[x][y].explored:
                color = colors["dark_wall"].surface if wall else colors["dark_ground"].surface
            else:
                continue

            screen.blit(color, (util.to_pixel(x), util.to_pixel(y)))

    # draw all entities in the list
    for entity in entities:
        draw_entity(screen, entity, fov_map)


def draw_entity(screen, entity, fov_map, bypass_fov=False):
    """ Отрисовка сущности, если она в поле зрения или враг """
    if bypass_fov or (0 <= entity.x < len(fov_map) and 0 <= entity.y < len(fov_map[0]) and fov_map[entity.x][entity.y]):
        screen.blit(entity.surface, (util.to_pixel(entity.x), util.to_pixel(entity.y)))
