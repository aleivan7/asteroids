import pygame


def point_in_polygon(point: pygame.Vector2, polygon: list[pygame.Vector2]) -> bool:
    inside = False
    j = len(polygon) - 1

    for i in range(len(polygon)):
        a = polygon[i]
        b = polygon[j]

        if ((a.y > point.y) != (b.y > point.y)) and (
            point.x < (b.x - a.x) * (point.y - a.y) / (b.y - a.y) + a.x
        ):
            inside = not inside

        j = i

    return inside


def point_in_triangle(
    point: pygame.Vector2, triangle: list[pygame.Vector2]
) -> bool:
    a, b, c = triangle
    d1 = _triangle_sign(point, a, b)
    d2 = _triangle_sign(point, b, c)
    d3 = _triangle_sign(point, c, a)

    has_negative = d1 < 0 or d2 < 0 or d3 < 0
    has_positive = d1 > 0 or d2 > 0 or d3 > 0
    return not (has_negative and has_positive)


def _triangle_sign(
    point: pygame.Vector2, start: pygame.Vector2, end: pygame.Vector2
) -> float:
    return (point.x - end.x) * (start.y - end.y) - (
        start.x - end.x
    ) * (point.y - end.y)


def distance_point_to_segment(
    point: pygame.Vector2,
    segment_start: pygame.Vector2,
    segment_end: pygame.Vector2,
) -> float:
    segment = segment_end - segment_start
    segment_length_squared = segment.length_squared()
    if segment_length_squared == 0:
        return point.distance_to(segment_start)

    t = (point - segment_start).dot(segment) / segment_length_squared
    t = max(0, min(1, t))
    closest_point = segment_start + segment * t
    return point.distance_to(closest_point)


def segments_intersect(
    a1: pygame.Vector2,
    a2: pygame.Vector2,
    b1: pygame.Vector2,
    b2: pygame.Vector2,
) -> bool:
    def orientation(p: pygame.Vector2, q: pygame.Vector2, r: pygame.Vector2) -> float:
        return (q.y - p.y) * (r.x - q.x) - (q.x - p.x) * (r.y - q.y)

    def on_segment(p: pygame.Vector2, q: pygame.Vector2, r: pygame.Vector2) -> bool:
        return (
            min(p.x, r.x) <= q.x <= max(p.x, r.x)
            and min(p.y, r.y) <= q.y <= max(p.y, r.y)
        )

    o1 = orientation(a1, a2, b1)
    o2 = orientation(a1, a2, b2)
    o3 = orientation(b1, b2, a1)
    o4 = orientation(b1, b2, a2)

    if o1 * o2 < 0 and o3 * o4 < 0:
        return True

    if o1 == 0 and on_segment(a1, b1, a2):
        return True
    if o2 == 0 and on_segment(a1, b2, a2):
        return True
    if o3 == 0 and on_segment(b1, a1, b2):
        return True
    if o4 == 0 and on_segment(b1, a2, b2):
        return True

    return False
