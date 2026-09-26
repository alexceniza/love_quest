"""
Pixel-art parallax backgrounds for Love Quest, one theme per world.

World 1  The Meadow of First Dates: sunny park, trees, a bench and heart balloons
World 2  Long Distance Skies:       inside the airport: big windows, departure boards, seats
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
    return [(sky, 0), (sun, 0.02, "once"), (clouds, 0.08), (far, 0.2), (near, 0.45)]


# ---------------------------------------------------------------------
#  World 2: Long Distance Skies (inside the airport terminal)
# ---------------------------------------------------------------------
WIN_TOP, WIN_BOTTOM = 30, 112     # the big terminal windows (low-res y)
HORIZON = 96                      # where the tarmac starts outside


def _plane_outside(s, x, y, col=(248, 248, 252), tail=(240, 150, 170)):
    """A parked plane seen through the window. (x, y) is its bottom-left."""
    pygame.draw.ellipse(s, col, (x, y - 9, 40, 8))
    pygame.draw.polygon(s, tail, [(x + 2, y - 7), (x + 2, y - 16), (x + 10, y - 7)])
    _heart(s, x + 2, y - 14, (255, 255, 255))
    for wx in range(x + 12, x + 34, 4):
        s.set_at((wx, y - 6), (120, 160, 200))
    pygame.draw.polygon(s, (205, 210, 225), [(x + 16, y - 3), (x + 25, y - 3), (x + 20, y)])


def _pixel_text(s, text, x, y, col):
    f = pygame.font.Font(None, 11)
    img = f.render(text, False, col)
    s.blit(img, (x, y))
    return img.get_width()


def _world2():
    rnd = random.Random(2)
    # --- outside, seen through the windows ---
    sky = _sky((150, 190, 232), (222, 234, 248), bands=10)
    outside = _new()
    for x, y, w in ((10, 40, 26), (120, 52, 20), (210, 36, 30)):
        _cloud(outside, x, y, w, (252, 253, 255), (230, 236, 248))
    pygame.draw.rect(outside, (150, 156, 168), (0, HORIZON, LW, WIN_BOTTOM - HORIZON))      # tarmac
    pygame.draw.rect(outside, (140, 180, 120), (0, HORIZON, LW, 2))                         # grass edge
    for x in range(0, LW, 16):
        pygame.draw.rect(outside, (240, 240, 240), (x, HORIZON + 9, 8, 1))                  # runway dashes
    tx = 150                                                                                 # control tower
    pygame.draw.rect(outside, (175, 188, 210), (tx, HORIZON - 40, 5, 40))
    pygame.draw.rect(outside, (175, 188, 210), (tx - 5, HORIZON - 49, 15, 9))
    pygame.draw.rect(outside, (210, 230, 244), (tx - 3, HORIZON - 47, 11, 3))
    for px in (20, 200):
        _plane_outside(outside, px, HORIZON + 6)
    pygame.draw.rect(outside, (255, 255, 255), (262, 44, 12, 3))                            # plane taking off
    pygame.draw.rect(outside, (240, 150, 170), (262, 42, 2, 3))
    pygame.draw.rect(outside, (255, 255, 255), (267, 47, 3, 2))

    # --- the terminal wall, with see-through windows ---
    wall = _new()
    wall_col, wall_shade = (230, 226, 218), (208, 203, 195)
    ceil_col, beam = (95, 105, 128), (80, 88, 110)
    frame = (115, 125, 145)
    pygame.draw.rect(wall, ceil_col, (0, 0, LW, WIN_TOP))                                   # ceiling
    for x in range(0, LW, 32):
        pygame.draw.rect(wall, beam, (x, 0, 3, WIN_TOP))                                    # ceiling beams
    for x in range(16, LW, 32):                                                             # pendant lights
        pygame.draw.line(wall, (150, 150, 150), (x, 0), (x, 10))
        pygame.draw.rect(wall, (90, 95, 105), (x - 3, 10, 7, 2))
        pygame.draw.rect(wall, (255, 238, 180), (x - 2, 12, 5, 1))
    pygame.draw.rect(wall, wall_col, (0, WIN_BOTTOM, LW, LH - WIN_BOTTOM))                  # lower wall
    pygame.draw.rect(wall, wall_shade, (0, WIN_BOTTOM, LW, 2))
    for x in range(0, LW, 64):                                                              # window frames
        pygame.draw.rect(wall, frame, (x, WIN_TOP - 2, LW, 2))
        pygame.draw.rect(wall, frame, (x, WIN_BOTTOM - 1, 64, 2))
        pygame.draw.rect(wall, frame, (x, WIN_TOP, 3, WIN_BOTTOM - WIN_TOP))
        pygame.draw.rect(wall, frame, (x + 32, WIN_TOP, 1, WIN_BOTTOM - WIN_TOP))
    # hanging departures boards and gate signs
    f = pygame.font.Font(None, 11)
    for bx, gate in ((34, "GATE 5"), (194, "GATE 14")):
        bw = f.size("DEPARTURES")[0] + 6
        pygame.draw.line(wall, (140, 140, 140), (bx + 6, WIN_TOP - 2), (bx + 6, WIN_TOP + 6))
        pygame.draw.line(wall, (140, 140, 140), (bx + bw - 6, WIN_TOP - 2), (bx + bw - 6, WIN_TOP + 6))
        pygame.draw.rect(wall, (40, 45, 60), (bx, WIN_TOP + 6, bw, 19))
        _pixel_text(wall, "DEPARTURES", bx + 3, WIN_TOP + 7, (255, 255, 255))
        for yy in range(WIN_TOP + 16, WIN_TOP + 24, 3):
            pygame.draw.line(wall, (255, 215, 110), (bx + 3, yy), (bx + 3 + rnd.randint(bw // 2, bw - 8), yy))
        gx = bx + bw + 20
        gw = f.size(gate)[0] + 5
        pygame.draw.line(wall, (140, 140, 140), (gx + gw // 2, WIN_TOP - 2), (gx + gw // 2, WIN_TOP + 4))
        pygame.draw.rect(wall, (60, 110, 180), (gx, WIN_TOP + 4, gw, 10))
        _pixel_text(wall, gate, gx + 3, WIN_TOP + 5, (255, 255, 255))

    # --- the waiting area: seats, plants and a suitcase ---
    lounge = _new()
    seat, seat_dark, metal = (95, 135, 195), (70, 105, 160), (150, 155, 165)
    for sx in (20, 180):
        pygame.draw.rect(lounge, metal, (sx, GROUND - 4, 30, 1))
        for c in range(4):
            x = sx + c * 8
            pygame.draw.rect(lounge, seat_dark, (x, GROUND - 13, 6, 6))                     # back
            pygame.draw.rect(lounge, seat, (x, GROUND - 7, 6, 2))                           # seat
        pygame.draw.rect(lounge, metal, (sx + 2, GROUND - 4, 1, 4))
        pygame.draw.rect(lounge, metal, (sx + 27, GROUND - 4, 1, 4))
    for px in (100, 280):                                                                    # plants
        pygame.draw.polygon(lounge, (170, 110, 80), [(px, GROUND - 8), (px + 8, GROUND - 8), (px + 7, GROUND), (px + 1, GROUND)])
        for lx, ly in ((px - 2, GROUND - 16), (px + 4, GROUND - 20), (px + 7, GROUND - 15), (px + 1, GROUND - 12)):
            pygame.draw.ellipse(lounge, (80, 150, 90), (lx, ly, 6, 8))
    cx = 140                                                                                 # suitcase with a heart sticker
    pygame.draw.rect(lounge, (240, 150, 175), (cx, GROUND - 12, 10, 12))
    pygame.draw.rect(lounge, (200, 110, 140), (cx + 3, GROUND - 15, 4, 3), 1)
    _heart(lounge, cx + 2, GROUND - 9, (255, 255, 255))
    return [(sky, 0), (outside, 0.1), (wall, 0.35), (lounge, 0.35)]


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
    return [(sky, 0), (moon, 0.02, "once"), (castle, 0.15), (wall, 0.4)]


BUILDERS = [_world1, _world2, _world3]


def _layers(world):
    world = min(world, len(BUILDERS) - 1)
    if world not in _cache:
        _cache[world] = [(pygame.transform.scale(layer[0], (LW * PX, LH * PX)),) + tuple(layer[1:]) for layer in BUILDERS[world]()]
    return _cache[world]


# ---------------------------------------------------------------------
#  Called by main.py every frame
# ---------------------------------------------------------------------
def draw(surf, world, cam, t):
    width = LW * PX
    wall_off = 0
    for layer in _layers(world):
        img, factor = layer[0], layer[1]
        off = (int(cam * factor) // PX * PX) % width   # snap to the pixel grid = crisp scrolling
        if len(layer) > 2:  # "once": the sun and moon should not repeat on wide screens
            surf.blit(img, (-(int(cam * factor) // PX * PX), 0))
            continue
        x = -off
        while x < surf.get_width():      # repeat the layer across the whole screen
            surf.blit(img, (x, 0))
            x += width
        wall_off = off
    if world == 2:  # flickering torch flames
        for tx in TORCHES:
            flick = (t // 6 + tx) % 3
            for dx in (-width, 0, width, 2 * width):
                x = tx * PX - wall_off + dx
                if -20 < x < surf.get_width() + 20:
                    y = (WALL_TOP + 7) * PX
                    pygame.draw.rect(surf, (255, 120, 40), (x - PX, y - (4 + flick) * PX, 4 * PX, (4 + flick) * PX))
                    pygame.draw.rect(surf, (255, 225, 90), (x, y - (3 + flick) * PX, 2 * PX, (2 + flick) * PX))
