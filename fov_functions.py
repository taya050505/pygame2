import util


def initialize_fov(game_map):
    return [[None for y in range(game_map.height)] for x in range(game_map.width)]


def recompute_fov(game_map, player_x, player_y, radius, light_walls=True):
    fov_map = initialize_fov(game_map)

    min_x = player_x - radius
    max_x = player_x + radius
    min_y = player_y - radius
    max_y = player_y + radius
    for x in range(len(fov_map)):
        for y in range(len(fov_map[x])):
            if fov_map[x][y] is None:
                # can't see outside the radius
                if x < min_x or x > max_x:
                    fov_map[x][y] = False
                    continue
                if y < min_y or y > max_y:
                    fov_map[x][y] = False
                    continue

                points = cast_ray((player_x, player_y), (x, y))
                distances = {}
                for p1, p2 in points:
                    distances[(p1, p2)] = distance_between_points(
                        player_x, player_y, p1, p2
                    )

                points.sort(key=lambda p: distances[(p[0], p[1])])
                tile_is_visible = True
                for p1, p2 in points:
                    if radius < distances[(p1, p2)]:
                        fov_map[p1][p2] = False
                    else:
                        if game_map.tiles[p1][p2].block_sight:
                            tile_is_visible = False
                        fov_map[p1][p2] = tile_is_visible
    return fov_map


def distance_between_points(x1, y1, x2, y2):
    x_dist = x1 - x2
    y_dist = y1 - y2
    distance = ((x_dist ** 2) + (y_dist ** 2)) ** 0.5
    return distance


def cast_ray(start, end):
    start_x, start_y = start
    end_x, end_y = end

    x_diff = start_x - end_x + 0.01
    slope = (start_y - end_y) / x_diff
    y_intercept = start_y - (slope * start_x)

    points = set()
    min_x = min(start_x, end_x)
    max_x = max(start_x, end_x)
    for x in range(min_x, max_x):
        y = (slope * x) + y_intercept
        points.add((x, round(y)))

    min_y = min(start_y, end_y)
    max_y = max(start_y, end_y)
    for y in range(min_y, max_y):
        x = (y - y_intercept) / slope
        points.add((round(x), y))

    return list(points)
