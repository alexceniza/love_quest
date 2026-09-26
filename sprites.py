"""
Pixel-art sprites for Love Quest.

Every sprite is a small grid of letters. Each letter is one pixel and its
colour comes from a palette. A dark outline is added automatically, then the
sprite is scaled up with no smoothing so the edges stay crisp.

Want to recolour something? Change the RGB numbers in the palettes below.
Want to redraw something? Change the letters in a grid. Keep every row of a
grid the same length, and use "." for see-through pixels.
"""
import math

import pygame

OUTLINE = (35, 25, 40)
SCALE = 3

# ---------------------------------------------------------------------
#  Palettes  (CHANGE ME: hat colours, hair, outfits...)
# ---------------------------------------------------------------------
HERO_PALETTE = {
    "H": (60, 90, 170),     # bucket hat
    "h": (40, 65, 135),     # hat brim (shade)
    "p": (235, 60, 90),     # little heart patch on the hat
    "B": (30, 25, 30),      # hair
    "S": (250, 215, 185),   # skin
    "G": (160, 170, 185),   # clear glasses frames
    "E": (20, 20, 25),      # eyes
    "W": (248, 248, 248),   # white t-shirt
    "w": (210, 215, 225),   # t-shirt shade
    "T": (25, 25, 30),      # watch
    "J": (95, 135, 200),    # jeans
    "j": (70, 105, 170),    # jeans shade
    "O": (25, 25, 30),      # black shoes
}

PARTNER_PALETTE = {
    "H": (255, 165, 200),   # bucket hat
    "h": (225, 125, 165),   # hat brim (shade)
    "F": (255, 225, 90),    # flower on the hat
    "B": (25, 20, 28),      # long black hair
    "b": (60, 50, 70),      # hair shine
    "S": (250, 218, 190),   # skin
    "L": (20, 20, 25),      # lashes
    "E": (20, 20, 25),      # eyes
    "c": (255, 170, 180),   # blush
    "W": (250, 248, 245),   # lace blouse
    "d": (245, 130, 170),   # pink dots on the blouse
    "J": (150, 185, 225),   # light jeans
    "j": (120, 155, 200),   # jeans shade
    "N": (250, 250, 250),   # white sneakers
    "n": (30, 30, 35),      # sneaker detail
}

WALKER_PALETTE = {"P": (130, 70, 180), "l": (175, 125, 220), "K": (25, 15, 30),
                  "W": (255, 255, 255), "E": (20, 15, 25)}
CLOUD_PALETTE = {"C": (95, 95, 110), "c": (125, 125, 140), "Y": (255, 225, 80),
                 "K": (25, 25, 30), "Z": (255, 225, 80)}
PLANE_PALETTE = {"R": (210, 45, 65), "W": (240, 240, 248), "w": (200, 205, 220),
                 "b": (90, 150, 220), "G": (165, 170, 190), "X": (255, 255, 255),
                 "E": (15, 15, 20), "K": (15, 15, 20)}
BAT_PALETTE = {"B": (120, 60, 140), "b": (205, 130, 200), "R": (255, 70, 90), "W": (255, 255, 255)}
BOSS_PALETTE = {"A": (230, 220, 200), "D": (55, 25, 45), "d": (80, 40, 65),
                "R": (240, 50, 60), "Y": (255, 225, 110), "F": (245, 245, 235),
                "C": (130, 15, 35), "h": (215, 35, 70), "K": (25, 10, 20)}

# ---------------------------------------------------------------------
#  Hero (12 x 17)
# ---------------------------------------------------------------------
HERO_HEAD = [
    "..HHHHHHHH..",
    ".HHHHHHHpHH.",
    "hhhhhhhhhhhh",
    ".BBBBBBBBBB.",
    ".BSSSSSSSSB.",
    ".GGGGSSGGGG.",
    ".GEEGGGGEEG.",
    ".GEEGSSGEEG.",
    ".GGGGSSGGGG.",
    "..SSSSSSSS..",
]
HERO_BLINK = [  # replaces rows 6-7 when blinking
    ".GSSGGGGSSG.",
    ".GEEGSSGEEG.",
]
HERO_BODY = {
    "stand": [
        "...wWWWWWw..",
        "..WWWWWWWW..",
        "..SWWWWWWS..",
        "..SwWWWWwT..",
        "...JJJJJJ...",
        "...JJjjJJ...",
        "...OO..OO...",
    ],
    "walk1": [
        "...wWWWWWw..",
        "..WWWWWWWW..",
        "..SWWWWWWS..",
        "..SwWWWWwT..",
        "...JJJJJJ...",
        "..JJ....JJ..",
        ".OO......OO.",
    ],
    "walk2": [
        "...wWWWWWw..",
        "..WWWWWWWW..",
        "..SWWWWWWS..",
        "..SwWWWWwT..",
        "...JJJJJJ...",
        "....JJJJ....",
        "....OOOO....",
    ],
    "jump": [
        "S..wWWWWWw.S",
        "SWWWWWWWWWWS",
        "..WWWWWWWW..",
        "..wWWWWWWw..",
        "...JJJJJJ...",
        "..JJ...JJ...",
        "..OO...OO...",
    ],
    "shoot": [
        "...wWWWWWw..",
        "..WWWWWWWWWS",
        "..SWWWWWW..T",
        "..SwWWWWw...",
        "...JJJJJJ...",
        "...JJjjJJ...",
        "...OO..OO...",
    ],
}

# ---------------------------------------------------------------------
#  Partner (12 x 17)
# ---------------------------------------------------------------------
PARTNER_HEAD = [
    "..HHHHHHHH..",
    ".HHFHHHHHHH.",
    "hhhhhhhhhhhh",
    "BBBBBBBBBBBB",
    "BbBBSSSSSBBB",
    "BBSSSSSSSSBB",
    "BBSLLSSLLSBB",
    "BBSEESSEESBB",
    "BBSEESSEESBB",
    "BBScSSSScSBB",
]
PARTNER_BLINK = [
    "BBSSSSSSSSBB",
    "BBSLLSSLLSBB",
]
PARTNER_BODY = [
    "BBBSWWWWSBBB",
    "BBWWdWWWdWBB",
    "BbSWWWdWWSBB",
    "B.SWdWWWdSbB",
    ".B.JJJJJJ.B.",
    "...JJjjJJ...",
    "...NN..NN...",
]

# ---------------------------------------------------------------------
#  Enemies
# ---------------------------------------------------------------------
WALKER = [
    [
        "...PPPPP...",
        ".PPPPPPPPP.",
        "PlKPPPPPKPP",
        "PPWKPPPKWPP",
        "PPWEPPPEWPP",
        "PPPPPPPPPPP",
        "PPPPKKKPPPP",
        "PPPKPPPKPPP",
        ".PPPPPPPPP.",
    ],
    [
        "...........",
        "..PPPPPPP..",
        "PPlKPPPKPPP",
        "PPWKPPPKWPP",
        "PPWEPPPEWPP",
        "PPPPPPPPPPP",
        "PPPPKKKPPPP",
        "PPPKPPPKPPP",
        "PP.PPPPP.PP",
    ],
]

CLOUD = [
    [
        "....ccc.......",
        "..cCCCCCc.cc..",
        ".cCCCCCCCCCCc.",
        "CCCKCCCCCKCCCC",
        "CCCYCCCCCYCCCC",
        "CCCCCKKKKCCCCC",
        ".CCCKCCCCKCCC.",
        "..CCCCCCCCCC..",
        "......Z.......",
        ".....Z........",
    ],
    [
        "....ccc.......",
        "..cCCCCCc.cc..",
        ".cCCCCCCCCCCc.",
        "CCCKCCCCCKCCCC",
        "CCCYCCCCCYCCCC",
        "CCCCCKKKKCCCCC",
        ".CCCKCCCCKCCC.",
        "..CCCCCCCCCC..",
        "..............",
        "..............",
    ],
]

PLANE = [
    "RR................",
    "RRR...........K...",
    "RRRWWWWWWWWWWWWK..",
    "WWWWWbWbWbWbWWXEW.",
    "WWWWWWWWWWWWWWWWWW",
    ".wwwwwwGGGwwwwwww.",
    ".......GGGG.......",
    "........GG........",
]

BAT = [
    [
        "B..............B",
        "BB............BB",
        "BbB..B....B..BbB",
        "BbbB.BBBBBB.BbbB",
        "BBBBBBRBBRBBBBBB",
        ".BBBBBBBBBBBBBB.",
        "..BB.BBBBBB.BB..",
        ".....B.WW.B.....",
    ],
    [
        "................",
        ".....B....B.....",
        ".....BBBBBB.....",
        "...BBBRBBRBBB...",
        "..BbBBBBBBBBbB..",
        ".BbbBBBBBBBBbbB.",
        "BBB..BBBBBB..BBB",
        "BB...B.WW.B...BB",
    ],
]

BOSS = [
    "..A..................A..",
    "..AA................AA..",
    "...AA..............AA...",
    "...AAA..DDDDDDDD..AAA...",
    "....AADDDDDDDDDDDDAA....",
    ".....DDDDDDDDDDDDDD.....",
    "....DDDDDDDDDDDDDDDD....",
    "...DDRRDDDDDDDDDDRRDD...",
    "...DDDRRRDDDDDDRRRDDD...",
    "...DDDYYRDDDDDDRYYDDD...",
    "...DDDYYDDDDDDDDYYDDD...",
    "...DDDDDDDDDDDDDDDDDD...",
    "...DDDDDFKFKFKFKDDDDD...",
    "...DDDDDDDDDDDDDDDDDD...",
    "..CCDDDDDDDDDDDDDDDDCC..",
    ".CCCDDDDhhDDDhhDDDDDCCC.",
    ".CCCDDDhhhhDhhhhDDDDCCC.",
    "CCCCDDDhhhhKhhhhDDDDCCCC",
    "CCCCDDDDhhhhKhhDDDDDCCCC",
    "CCCCDDDDDhhKhhDDDDDDCCCC",
    "CCCCDDDDDDhhhDDDDDDDCCCC",
    "CCCCdDDDDDDhDDDDDDDdCCCC",
    "CCC..dDDDDDDDDDDDDd..CCC",
    "......KKK......KKK......",
]

# ---------------------------------------------------------------------
#  Building the images
# ---------------------------------------------------------------------
_cache = {}


def build(grid, palette, scale=SCALE, flip=False, white=False):
    """Turn a letter grid into a crisp, outlined, scaled-up Surface."""
    key = (id(grid), tuple(grid), scale, flip, white)
    if key in _cache:
        return _cache[key]
    w = max(len(r) for r in grid) + 2
    h = len(grid) + 2
    small = pygame.Surface((w, h), pygame.SRCALPHA)
    solid = set()
    for y, row in enumerate(grid):
        for x, ch in enumerate(row):
            if ch != "." and ch in palette:
                small.set_at((x + 1, y + 1), (255, 255, 255) if white else palette[ch])
                solid.add((x + 1, y + 1))
    for (x, y) in list(solid):  # auto outline
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if n not in solid:
                small.set_at(n, (255, 255, 255) if white else OUTLINE)
    if flip:
        small = pygame.transform.flip(small, True, False)
    big = pygame.transform.scale(small, (w * scale, h * scale))  # no smoothing = crisp
    _cache[key] = big
    return big


def blit_bottom_center(surf, img, cx, bottom):
    surf.blit(img, (int(cx - img.get_width() / 2), int(bottom - img.get_height() + SCALE)))


# ---------------------------------------------------------------------
#  Draw functions used by main.py
# ---------------------------------------------------------------------
def draw_hero(surf, p, cam, t=None):
    """p is the Player. Chooses a pose from how he is moving."""
    if p.invuln and (p.invuln // 4) % 2:
        return
    ticks = pygame.time.get_ticks() if t is None else t
    head = list(HERO_HEAD)
    if (ticks // 16) % 200 < 8:  # blink every few seconds
        head[6:8] = HERO_BLINK
    if not p.on_ground and p.coyote == 0:  # really in the air (not just a 1-frame physics wobble)
        body = HERO_BODY["jump"]
    elif p.shoot_cd > 6:
        body = HERO_BODY["shoot"]
    elif abs(p.vx) > 0.5:
        body = [HERO_BODY["walk1"], HERO_BODY["stand"], HERO_BODY["walk2"], HERO_BODY["stand"]][int(p.anim / 1.5) % 4]
    else:
        body = HERO_BODY["stand"]
    img = build(tuple(head + body), HERO_PALETTE, flip=p.facing < 0)
    r = p.rect
    blit_bottom_center(surf, img, r.centerx - cam, r.bottom)


def draw_partner(surf, x, y, t, happy=False):
    """x, y is the top-left of her 28 x 48 spot (same as the old draw_princess)."""
    head = list(PARTNER_HEAD)
    if int(t * 60) % 190 < 8:
        head[6:8] = PARTNER_BLINK
    bob = int(abs(math.sin(t * 4)) * -6) if happy else 0
    img = build(tuple(head + PARTNER_BODY), PARTNER_PALETTE, flip=True)
    blit_bottom_center(surf, img, x + 14, y + 48 + bob)


def draw_walker(surf, e, cam):
    img = build(tuple(WALKER[int(e.t / 2) % 2]), WALKER_PALETTE, flip=e.vx > 0)
    r = e.rect
    blit_bottom_center(surf, img, r.centerx - cam, r.bottom)


def draw_cloud(surf, e, cam):
    frame = 0 if int(e.t * 20) % 8 < 4 else 1
    img = build(tuple(CLOUD[frame]), CLOUD_PALETTE)
    r = e.rect
    surf.blit(img, (int(r.centerx - cam - img.get_width() / 2), int(r.y - 6)))


def draw_plane(surf, e, cam):
    img = build(tuple(PLANE), PLANE_PALETTE, flip=e.vx < 0)
    r = e.rect
    surf.blit(img, (int(r.centerx - cam - img.get_width() / 2), int(r.y - 3)))


def draw_bat(surf, e, cam):
    frame = int(e.t * 25) % 2
    img = build(tuple(BAT[frame]), BAT_PALETTE)
    r = e.rect
    surf.blit(img, (int(r.centerx - cam - img.get_width() / 2), int(r.centery - img.get_height() / 2)))


def draw_boss(surf, b, cam):
    if b.hp <= 0:
        return
    white = b.flash % 4 >= 2
    img = build(tuple(BOSS), BOSS_PALETTE, scale=4, flip=b.facing > 0, white=white)
    r = b.rect
    bob = int(math.sin(b.t) * 2)
    blit_bottom_center(surf, img, r.centerx - cam, r.bottom + bob)
