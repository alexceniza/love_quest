"""
Pixel-art parallax backgrounds for Love Quest, one theme per world.

World 1  The Meadow of First Dates: sunny park, trees, a bench and heart balloons
World 2  Long Distance Skies:       a calm airport with a terminal, gates and a control tower
World 3  Castle of the Heartbreaker: blood-red moon, castle towers, flickering torches

Each layer is drawn small (320 x 174) and scaled up 3x with no smoothing,
so it matches the crisp pixel sprites. Layers further away scroll slower
(the "factor"), which is what makes the scene feel deep.
"""
import math
import random

import pygame

PX = 3                      # size of one background pixel on screen
LW, LH = 320, 174           # low-res layer size (320 * 3 = 960 wide)
GROUND = LH - 27            # where the level's ground tiles start (low-res y)

_cache = {}


# ---------------------------------------------------------------------
#  Small drawing helpers (all in low-res pixels)
# ---------------------------------------------------------------------
def _new():
    return pygame.Surface((LW, LH), pygame.SRCALPHA)


def _mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _sky(top, bottom, bands=14):
    s = pygame.Surface((LW, LH))
    bh = LH / bands
    for i in range(bands):
        pygame.draw.rect(s, _mix(top, bottom, i / (bands - 1)), (0, int(i * bh), LW, int(bh) + 1))
    return s


def _wrap(fn, x, *args):
    """Draw something at x, and again one layer-width left/right so it tiles."""
    for dx in (-LW, 0, LW):
        fn(x + dx, *args)


def _cloud(s, x, y, w, col, shade):
    def one(x):
        pygame.draw.rect(s, col, (x, y + 4, w, 6))
        pygame.draw.rect(s, col, (x + 4, y, w // 2, 6))
        pygame.draw.rect(s, col, (x + w // 2, y + 2, w // 3, 4))
        pygame.draw.rect(s, shade, (x + 2, y + 9, w - 4, 2))
    _wrap(one, x)


def _heart(s, x, y, col):
    for dx, dy in ((1, 0), (2, 0), (4, 0), (5, 0), (0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1),
                   (0, 2), (1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (1, 3), (2, 3), (3, 3), (4, 3), (5, 3),
                   (2, 4), (3, 4), (4, 4), (3, 5)):
        s.set_at((x + dx, y + dy), col)


def _hills(s, base, amp1, per1, amp2, per2, col, top_col=None):
    for x in range(LW):
        h = int(base + amp1 * math.sin(2 * math.pi * x * per1 / LW) + amp2 * math.sin(2 * math.pi * x * per2 / LW))
        pygame.draw.line(s, col, (x, h), (x, LH))
        if top_col:
            s.set_at((x, h), top_col)
    return s


def _ground_y(base, amp1, per1, amp2, per2, x):
    return int(base + amp1 * math.sin(2 * math.pi * x * per1 / LW) + amp2 * math.sin(2 * math.pi * x * per2 / LW))


# ---------------------------------------------------------------------
#  World 1: The Meadow of First Dates
# ---------------------------------------------------------------------
def _world1():
    rnd = random.Random(1)
    sky = _sky((105, 175, 255), (210, 238, 255))
    # sun
    sun = _new()
    pygame.draw.circle(sun, (255, 240, 170), (262, 30), 17)
    pygame.draw.circle(sun, (255, 225, 110), (262, 30), 13)
    # clouds
    clouds = _new()
    for x, y, w in ((20, 22, 34), (110, 40, 26), (190, 16, 40), (280, 50, 22)):
        _cloud(clouds, x, y, w, (255, 255, 255), (225, 235, 250))
    # far hills
    far = _hills(_new(), 112, 9, 2, 5, 5, (150, 205, 130), (175, 225, 150))
    # near hills with trees, a bench and heart balloons
    near = _hills(_new(), 135, 6, 3, 3, 7, (105, 180, 90), (135, 205, 110))
    for x in range(0, LW, 3):
        gy = _ground_y(135, 6, 3, 3, 7, x)
        if rnd.random() < 0.35:
            near.set_at((x, gy + rnd.randint(2, 8)), rnd.choice([(255, 255, 255), (255, 150, 190), (255, 225, 90)]))
    for tx in (28, 96, 214, 282):
        gy = _ground_y(135, 6, 3, 3, 7, tx)
        pygame.draw.rect(near, (120, 80, 50), (tx - 1, gy - 12, 3, 13))
        pygame.draw.circle(near, (60, 140, 70), (tx, gy - 17), 9)
        pygame.draw.circle(near, (85, 165, 85), (tx - 3, gy - 20), 4)
    bx = 150
    gy = _ground_y(135, 6, 3, 3, 7, bx)
    pygame.draw.rect(near, (150, 95, 55), (bx, gy - 7, 18, 2))      # seat
    pygame.draw.rect(near, (150, 95, 55), (bx, gy - 11, 18, 2))     # back
    for lx in (bx + 1, bx + 15):
        pygame.draw.rect(near, (90, 60, 40), (lx, gy - 7, 2, 7))
    for i, (hx, hy, col) in enumerate(((bx + 2, gy - 34, (240, 60, 100)), (bx + 10, gy - 40, (255, 130, 170)))):
        pygame.draw.line(near, (240, 240, 240), (hx + 3, hy + 6), (bx + 8, gy - 11))
        _heart(near, hx, hy, col)
    return [(sky, 0), (sun, 0.02), (clouds, 0.08), (far, 0.2), (near, 0.45)]


# ---------------------------------------------------------------------
#  World 2: Long Distance Skies (the airport)
# ---------------------------------------------------------------------
def _mini_plane(s, x, y, col, tail=(235, 140, 160)):
    pygame.draw.rect(s, col, (x, y + 2, 12, 3))            # body
    pygame.draw.rect(s, col, (x + 12, y + 3, 2, 1))        # nose
    pygame.draw.rect(s, tail, (x, y, 2, 3))                # tail
    pygame.draw.rect(s, col, (x + 5, y + 5, 3, 2))         # wing


def _parked_plane(s, x, col=(245, 246, 250), tail=(240, 150, 170)):
    y = GROUND - 12
    pygame.draw.ellipse(s, col, (x, y, 50, 10))                                   # fuselage
    pygame.draw.polygon(s, tail, [(x + 2, y + 2), (x + 2, y - 9), (x + 11, y + 2)])  # tail fin
    _heart(s, x + 2, y - 7, (255, 255, 255))
    for wx in range(x + 14, x + 42, 4):
        s.set_at((wx, y + 3), (120, 160, 200))                                   # windows
    pygame.draw.polygon(s, (205, 210, 225), [(x + 20, y + 7), (x + 30, y + 7), (x + 24, y + 11)])  # wing
    pygame.draw.rect(s, (90, 95, 110), (x + 12, y + 10, 2, 2))                   # wheels
    pygame.draw.rect(s, (90, 95, 110), (x + 38, y + 10, 2, 2))


def _world2():
    rnd = random.Random(2)
    sky = _sky((140, 180, 225), (218, 230, 246), bands=12)
    clouds = _new()
    for x, y, w in ((15, 22, 30), (120, 42, 22), (200, 15, 36), (285, 52, 20)):
        _cloud(clouds, x, y, w, (250, 252, 255), (226, 233, 246))
    # far: control tower and a plane taking off
    far = _new()
    col = (170, 185, 210)
    tx = 60
    pygame.draw.rect(far, col, (tx, GROUND - 75, 6, 75))
    pygame.draw.rect(far, col, (tx - 6, GROUND - 86, 18, 11))
    pygame.draw.rect(far, (205, 228, 242), (tx - 4, GROUND - 84, 14, 4))
    pygame.draw.line(far, col, (tx + 3, GROUND - 90), (tx + 3, GROUND - 86))
    far.set_at((tx + 3, GROUND - 91), (235, 100, 110))
    _mini_plane(far, 228, 38, (255, 255, 255))
    for i in range(6):
        far.set_at((216 - i * 7, 45 + i * 4), (240, 170, 190))                   # little heart trail
    # near: the terminal, big windows, a departures board and parked planes
    term = _new()
    top = GROUND - 44
    wall, frame = (208, 212, 224), (130, 145, 170)
    glass, shine = (170, 202, 226), (192, 220, 238)
    pygame.draw.rect(term, wall, (0, top, LW, LH - top))
    for x in range(LW):
        roof = top - 4 - int(3 * math.sin(2 * math.pi * x * 2 / LW))
        pygame.draw.line(term, (155, 170, 195), (x, roof), (x, top))
    for x in range(4, LW, 20):
        pygame.draw.rect(term, glass, (x, top + 6, 16, 20))
        pygame.draw.rect(term, shine, (x + 2, top + 7, 3, 18))
        pygame.draw.rect(term, frame, (x, top + 6, 16, 20), 1)
        pygame.draw.line(term, frame, (x + 8, top + 6), (x + 8, top + 25))
    board_x = 142
    pygame.draw.rect(term, (45, 50, 65), (board_x, top + 8, 36, 14))
    for yy in range(top + 10, top + 21, 3):
        pygame.draw.line(term, (255, 215, 110), (board_x + 3, yy), (board_x + 3 + rnd.randint(12, 28), yy))
    for px in (30, 220):
        pygame.draw.rect(term, (175, 180, 195), (px + 44, top + 26, 16, 6))       # jet bridge
        _parked_plane(term, px)
    for x in range(2, LW, 8):
        term.set_at((x, GROUND - 1), (255, 225, 120))                              # runway lights
    return [(sky, 0), (clouds, 0.08), (far, 0.15), (term, 0.4)]


# ---------------------------------------------------------------------
#  World 3: Castle of the Heartbreaker
# ---------------------------------------------------------------------
TORCHES = (40, 120, 200, 280)   # x positions of torches on the wall (low-res)
WALL_TOP = 118


def _world3():
    rnd = random.Random(3)
    sky = _sky((25, 8, 22), (150, 45, 40))
    for _ in range(35):
        sky.set_at((rnd.randrange(LW), rnd.randrange(70)), (255, 220, 220))
    moon = _new()
    pygame.draw.circle(moon, (255, 225, 205), (58, 36), 18)
    pygame.draw.circle(moon, (235, 190, 175), (52, 32), 4)
    pygame.draw.circle(moon, (235, 190, 175), (64, 42), 3)
    pygame.draw.circle(moon, (235, 190, 175), (62, 28), 2)
    # far castle silhouette
    castle = _new()
    col = (50, 20, 40)
    pygame.draw.rect(castle, col, (170, 70, 110, 80))                     # keep
    for tx, tw, th in ((160, 18, 95), (212, 22, 120), (272, 18, 95)):     # towers
        pygame.draw.rect(castle, col, (tx, GROUND - th, tw, th))
        pygame.draw.polygon(castle, col, [(tx - 3, GROUND - th), (tx + tw // 2, GROUND - th - 18), (tx + tw + 3, GROUND - th)])
        pygame.draw.rect(castle, (255, 200, 90), (tx + tw // 2 - 1, GROUND - th + 10, 3, 5))
    for x in range(170, 280, 6):                                          # battlements
        pygame.draw.rect(castle, col, (x, 66, 3, 4))
    for wx in (186, 200, 244, 258):
        pygame.draw.rect(castle, (255, 190, 80), (wx, 90, 3, 6))
    _heart(castle, 219, 58, (200, 30, 60))                                 # broken-heart banner
    pygame.draw.line(castle, col, (222, 58), (221, 63))
    # near castle wall with torches
    wall = _new()
    wc, dark = (80, 55, 70), (60, 40, 55)
    pygame.draw.rect(wall, wc, (0, WALL_TOP, LW, LH - WALL_TOP))
    for x in range(0, LW, 10):
        pygame.draw.rect(wall, wc, (x, WALL_TOP - 5, 6, 5))
    for row, y in enumerate(range(WALL_TOP + 5, LH, 6)):
        pygame.draw.line(wall, dark, (0, y), (LW, y))
        for x in range(row % 2 * 6, LW, 12):
            pygame.draw.line(wall, dark, (x, y - 6), (x, y))
    for tx in TORCHES:
        pygame.draw.rect(wall, (40, 30, 35), (tx, WALL_TOP + 8, 2, 7))
        pygame.draw.rect(wall, (40, 30, 35), (tx - 1, WALL_TOP + 7, 4, 2))
    return [(sky, 0), (moon, 0.02), (castle, 0.15), (wall, 0.4)]


BUILDERS = [_world1, _world2, _world3]


def _layers(world):
    world = min(world, len(BUILDERS) - 1)
    if world not in _cache:
        _cache[world] = [(pygame.transform.scale(img, (LW * PX, LH * PX)), f) for img, f in BUILDERS[world]()]
    return _cache[world]


# ---------------------------------------------------------------------
#  Called by main.py every frame
# ---------------------------------------------------------------------
def draw(surf, world, cam, t):
    width = LW * PX
    wall_off = 0
    for img, factor in _layers(world):
        off = (int(cam * factor) // PX * PX) % width   # snap to the pixel grid = crisp scrolling
        surf.blit(img, (-off, 0))
        surf.blit(img, (width - off, 0))
        wall_off = off
    if world == 2:  # flickering torch flames
        for tx in TORCHES:
            flick = (t // 6 + tx) % 3
            for dx in (-width, 0, width):
                x = tx * PX - wall_off + dx
                if -20 < x < surf.get_width() + 20:
                    y = (WALL_TOP + 7) * PX
                    pygame.draw.rect(surf, (255, 120, 40), (x - PX, y - (4 + flick) * PX, 4 * PX, (4 + flick) * PX))
                    pygame.draw.rect(surf, (255, 225, 90), (x, y - (3 + flick) * PX, 2 * PX, (2 + flick) * PX))
