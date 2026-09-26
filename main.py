"""
LOVE QUEST  -  a tiny 5-minute platformer made with love.

Run on your computer:
    pip install pygame-ce        (or: pip install pygame)
    python main.py

Play it in a web browser:
    pip install pygbag
    pygbag love_quest            (run from the folder that CONTAINS love_quest/)
    then open http://localhost:8000
    Build output in love_quest/build/web can be uploaded to itch.io or GitHub Pages.

Controls:  Left/Right or A/D = move   Space/W/Up = jump   J/X/F = shoot hearts
           Stomp on enemies too.  Enter = start / continue.
"""
import asyncio
import math
import random

import pygame

import backgrounds
import sprites
import touch

# =====================================================================
#  PERSONALIZE ME  <3
# =====================================================================
HERO_NAME = "Alex"
PARTNER_NAME = "Pooka"
HERO_COLOR = (215, 40, 60)          # hero's cap and shirt
PARTNER_COLOR = (255, 120, 190)     # princess dress

# One message pops up for each love letter collected (8 in the game).
MEMORIES = [
    "Okay... I know you've been waiting a while.",
    "And I know you were hungry the whole time.",
    "I'm sorry for making you wait, my love.",
    "Your tummy deserved better. So did you.",
    "Thank you for being so patient with me.",
    "I promise I'll make it up to you.",
    "Next time, the snacks will be ready before you are.",
    "Now that you're fed, I'm all yours.",
]

# Shown on the final screen after the rescue.
ENDING_LINES = [
    "Sorry I kept my hungry princess waiting.",
    "You were so patient (mostly),",
    "and now that your tummy is happy,",
    "",
    "I'm all yours. I love you.",
]

TOTAL_TIME = 300                    # seconds (5 minutes)
# =====================================================================

W, H = 960, 520
TILE = 40
FPS = 60
TOUCH = touch.TouchControls(W, H)   # on-screen buttons for phones
GRAVITY = 0.6
MAX_FALL = 14
RUN_SPEED = 4.6
JUMP_SPEED = 14.0

# Map legend:
#  #  ground / wall        =  brick platform     ^  spikes (minor obstacle)
#  -  moving platform      E  Grumpy Monday      F  Bad Vibes cloud (flyer)
#  M  love letter          X  exit door          S  hero start
#  B  The Heartbreaker     c  cage bars          P  the princess
LEVELS = [
    {
        "name": "World 1: The Meadow of First Dates",
        "sub": "Grumpy Mondays are blocking the path. Jump on them or shoot hearts!",
        "sky": ((120, 190, 255), (220, 240, 255)),
        "ground": (95, 170, 70), "dirt": (140, 95, 60),
        "map": [
            "                                                                                                    ",
            "                                                                                                    ",
            "                                                                                                    ",
            "                                                                                                    ",
            "                                                                                                    ",      
            "                                           M                                                        ",
            "                                         =====                                  F                   ",
            "           M                                                 M                                      ",
            "          ====                     =====                    ====                                    ",
            "                                                                                               X    ",
            "  S            E              ^^      E                  E    ^^    E               ^^    E         ",
            "######################   #######################   #######################   #######################",
            "######################   #######################   #######################   #######################",
        ],
    },
    {
        "name": "World 2: The Long Distance Skies",
        "sub": "Watch out for Bad Vibes clouds and ride the moving platforms.",
        "sky": ((40, 30, 70), (95, 70, 130)),
        "ground": (185, 180, 172), "dirt": (135, 128, 120),
        "map": [
            "##############################################################################################################",
            "                                                                                                              ",
            "                                                                                                              ",
            "                                                                                                              ",
            "                                                                                                              ",
            "                                F                                                                   F         ",
            "                                                       F                        F                             ",
            "                            M                            M                                                    ",
            "                          =====              -          ====            M                                     ",
            "                                                                                                          X   ",
            "  S       E       -           E   ^^    E                   E   ^^                   E  ^^^    E              ",
            "##################      #####################      ####################   ####################################",
            "##################      #####################      ####################   ####################################",
        ],
    },
    {
        "name": "World 3: Castle of the Heartbreaker",
        "sub": "The Heartbreaker has locked her in a cage. Defeat him!",
        "sky": ((60, 15, 25), (150, 60, 50)),
        "ground": (110, 100, 105), "dirt": (70, 60, 65),
        "map": [
            "############################################################",
            "                                                      c    #",
            "                                                      c    #",
            "                                                      c    #",
            "                                                      c    #",
            "                                                      c    #",
            "                  F                                   c    #",
            "                          M                           c    #",
            "             M           ====         ====  B         c    #",
            "                                                      c P  #",
            "  S     E                                             c    #",
            "############   #############################################",
            "############   #############################################",
        ],
    },
]


# ---------------------------------------------------------------------
#  Helpers
# ---------------------------------------------------------------------
def font(size):
    return pygame.font.Font(None, size)


def draw_heart(surf, cx, cy, size, color):
    r = size // 2
    pygame.draw.circle(surf, color, (cx - r // 2 - 1, cy - r // 4), r // 2 + 1)
    pygame.draw.circle(surf, color, (cx + r // 2 + 1, cy - r // 4), r // 2 + 1)
    pygame.draw.polygon(surf, color, [(cx - r - 1, cy - r // 6), (cx + r + 1, cy - r // 6), (cx, cy + r)])


def text_center(surf, txt, size, color, y, shadow=True):
    f = font(size)
    if shadow:
        s = f.render(txt, True, (0, 0, 0))
        surf.blit(s, s.get_rect(center=(W // 2 + 2, y + 2)))
    s = f.render(txt, True, color)
    surf.blit(s, s.get_rect(center=(W // 2, y)))


def make_gradient(top, bottom):
    s = pygame.Surface((W, H))
    for y in range(H):
        t = y / H
        c = [int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)]
        pygame.draw.line(s, c, (0, y), (W, y))
    return s


class Body:
    """Something with a float position and a size."""

    def __init__(self, x, y, w, h):
        self.x, self.y, self.w, self.h = float(x), float(y), w, h
        self.vx = self.vy = 0.0

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)


class Particle:
    def __init__(self, x, y, color, heart=False):
        self.x, self.y = x, y
        self.vx, self.vy = random.uniform(-3, 3), random.uniform(-5, -1)
        self.life = random.randint(25, 45)
        self.color, self.heart = color, heart


# ---------------------------------------------------------------------
#  Level
# ---------------------------------------------------------------------
class Level:
    def __init__(self, idx, memory_start):
        d = LEVELS[idx]
        self.data = d
        rows = d["map"]
        self.cols = max(len(r) for r in rows)
        self.rows = len(rows)
        self.grid = [list(r.ljust(self.cols)) for r in rows]
        self.width = self.cols * TILE
        self.sky = make_gradient(*d["sky"])
        self.spikes, self.enemies, self.memories, self.platforms = [], [], [], []
        self.door = self.princess = self.boss = None
        self.start = (80, 300)
        mem_i = memory_start
        for cy, row in enumerate(self.grid):
            for cx, ch in enumerate(row):
                x, y = cx * TILE, cy * TILE
                if ch == "S":
                    self.start = (x + 6, y)
                elif ch == "^":
                    self.spikes.append(pygame.Rect(x + 4, y + 22, TILE - 8, 18))
                elif ch == "E":
                    self.enemies.append(Walker(x + 3, y + 10))
                elif ch == "F":
                    self.enemies.append(Flyer(x, y))
                elif ch == "M":
                    self.memories.append([pygame.Rect(x + 8, y + 8, 24, 24), mem_i, random.random() * 6])
                    mem_i += 1
                elif ch == "-":
                    self.platforms.append(MovingPlatform(x, y))
                elif ch == "X":
                    self.door = pygame.Rect(x, y, TILE, TILE * 2)
                elif ch == "B":
                    self.boss = Boss(x, y - 56)
                elif ch == "P":
                    self.princess = pygame.Rect(x + 6, y + 32, 28, 48)
                if ch not in "#=c":
                    row[cx] = " "
        self.memory_end = mem_i

    def solid(self, cx, cy):
        if cx < 0 or cx >= self.cols:
            return True
        if cy < 0 or cy >= self.rows:
            return False
        ch = self.grid[cy][cx]
        if ch == "c":
            return self.boss is not None and self.boss.hp > 0
        return ch in "#="

    def solid_rects(self, r):
        out = []
        for cy in range(r.top // TILE, (r.bottom - 1) // TILE + 1):
            for cx in range(r.left // TILE, (r.right - 1) // TILE + 1):
                if self.solid(cx, cy):
                    out.append(pygame.Rect(cx * TILE, cy * TILE, TILE, TILE))
        return out

    def move(self, b, dx, dy):
        """Move a Body with tile collision. Returns (hit_wall, landed, bonked)."""
        hit_x = landed = bonk = False
        b.x += dx
        tiles = self.solid_rects(b.rect)
        if tiles:
            hit_x = True
            if dx > 0:
                b.x = min(t.left for t in tiles) - b.w
            elif dx < 0:
                b.x = max(t.right for t in tiles)
        b.y += dy
        tiles = self.solid_rects(b.rect)
        if tiles:
            if dy > 0:
                b.y = min(t.top for t in tiles) - b.h
                landed = True
            elif dy < 0:
                b.y = max(t.bottom for t in tiles)
                bonk = True
        return hit_x, landed, bonk


class MovingPlatform:
    def __init__(self, x, y):
        self.x0, self.y = x, y
        self.x = float(x)
        self.w, self.h = TILE * 3, 16
        self.t = 0.0
        self.dx = 0.0

    @property
    def rect(self):
        return pygame.Rect(int(self.x), self.y, self.w, self.h)

    def update(self):
        self.t += 0.02
        nx = self.x0 + (1 - math.cos(self.t)) / 2 * TILE * 3
        self.dx = nx - self.x
        self.x = nx


# ---------------------------------------------------------------------
#  Enemies
# ---------------------------------------------------------------------
class Walker(Body):
    """Grumpy Monday: a purple blob that patrols the ground."""

    def __init__(self, x, y):
        super().__init__(x, y, 34, 30)
        self.vx = -1.4
        self.alive = True
        self.t = random.random() * 10

    def update(self, lvl, player):
        self.t += 0.15
        self.vy = min(self.vy + GRAVITY, MAX_FALL)
        hit_x, landed, _ = lvl.move(self, self.vx, self.vy)
        if landed:
            self.vy = 0
            front = self.x + (self.w + 2 if self.vx > 0 else -2)
            if not lvl.solid(int(front // TILE), int((self.y + self.h + 2) // TILE)):
                hit_x = True
        if hit_x:
            self.vx = -self.vx
        if self.y > H + 100:
            self.alive = False

    def draw(self, s, cam):
        x, y = int(self.x - cam), int(self.y)
        sq = int(math.sin(self.t) * 2)
        pygame.draw.ellipse(s, (120, 60, 170), (x, y + sq, self.w, self.h - sq))
        pygame.draw.ellipse(s, (160, 100, 210), (x + 6, y + 4 + sq, 12, 8))
        for ex in (x + 10, x + 22):
            pygame.draw.circle(s, (255, 255, 255), (ex, y + 13), 5)
            pygame.draw.circle(s, (0, 0, 0), (ex + (1 if self.vx > 0 else -1), y + 14), 2)
        pygame.draw.line(s, (0, 0, 0), (x + 5, y + 5), (x + 14, y + 9), 3)
        pygame.draw.line(s, (0, 0, 0), (x + 29, y + 5), (x + 20, y + 9), 3)
        pygame.draw.arc(s, (0, 0, 0), (x + 11, y + 20, 12, 8), 0.2, 2.9, 2)


class Flyer(Body):
    """Bad Vibes: a little storm cloud drifting through the air."""

    def __init__(self, x, y):
        super().__init__(x, y, 40, 26)
        self.x0, self.y0 = x, y
        self.t = random.random() * 6
        self.alive = True

    def update(self, lvl, player):
        self.t += 0.03
        self.x = self.x0 + math.sin(self.t) * 90
        self.y = self.y0 + math.sin(self.t * 2.3) * 35

    def draw(self, s, cam):
        sprites.draw_plane(s, self, cam)


class Boss(Body):
    """The Heartbreaker: the major obstacle guarding the princess."""
    MAX_HP = 16

    def __init__(self, x, y):
        super().__init__(x, y, 90, 96)
        self.hp = self.MAX_HP
        self.active = False
        self.facing = -1
        self.shoot_t = 90
        self.jump_t = 150
        self.flash = 0
        self.t = 0.0

    def update(self, lvl, player, shots):
        if self.hp <= 0:
            return
        self.t += 0.1
        if not self.active:
            if player.x > 18 * TILE:
                self.active = True
            return
        angry = self.hp <= self.MAX_HP // 2
        speed = 2.2 if angry else 1.4
        self.facing = 1 if player.x > self.x + self.w / 2 else -1
        self.vx = speed * self.facing
        self.vy = min(self.vy + GRAVITY, MAX_FALL)
        _, landed, _ = lvl.move(self, self.vx, self.vy)
        self.x = max(20 * TILE, min(self.x, 54 * TILE - self.w))
        if landed:
            self.vy = 0
            self.jump_t -= 1
            if self.jump_t <= 0:
                self.vy = -13
                self.jump_t = random.randint(100, 170) - (40 if angry else 0)
        self.shoot_t -= 1
        if self.shoot_t <= 0:
            cx, cy = self.x + self.w / 2, self.y + 35
            ang = math.atan2(player.y + 20 - cy, player.x + 14 - cx)
            spread = (-0.25, 0, 0.25) if angry else (0,)
            for a in spread:
                shots.append(Shot(cx, cy, math.cos(ang + a) * 5, math.sin(ang + a) * 5, "boss"))
            self.shoot_t = 70 if angry else 100
        if self.flash:
            self.flash -= 1

    def draw(self, s, cam):
        sprites.draw_boss(s, self, cam)


class Plane(Body):
    """Goodbye Plane: flies back and forth, just like all those airport goodbyes."""

    def __init__(self, x, y):
        super().__init__(x, y + 8, 56,24)
        self.x0 = x
        self.vx = 2.2
        self.t = random.random() * 6
        self.alive = True

    def update(self, lvl, player):
        self.t += 0.08
        self.x += self.vx
        if abs(self.x - self.x0) > 4 * TILE:
            self.vx = -self.vx
        self.y += math.sin(self.t) * 0.5

    def draw(self, s, cam):
        x, y = int(self.x - cam), int(self.y)
        f = 1 if self.vx > 0 else -1
        nose = x + self.w if f > 0 else x
        tail = x if f > 0 else x + self.w
        # tail fin
        pygame.draw.polygon(s, (200, 40, 60), [(tail, y + 12), (tail, y - 6), (tail +14 * f, y + 10)])
        # body 
        pygame.draw.ellipse(s, (235, 235, 245), (x, y + 6, self.w, 14))
        # wing
        pygame.draw.polygon(s, (170, 175, 195), [(x + 22, y + 13), (x + 28 - 8 * f, y + 26), (x + 36 - 8 * f, y + 13)])
        # windows 
        for i in range(4):
            pygame.draw.circle(s, (90, 150, 220), (x + 14 + i * 8, y + 11), 2)
        # angry cockpit eye
        ex = nose - 9 * f
        pygame.draw.circle(s, (255, 255, 255), (ex, y + 12), 4)
        pygame.draw.circle(s, (0, 0, 0), (ex + f, y + 12), 2)
        pygame.draw.line(s, (0, 0, 0), (ex - 5 * y + 5), (ex + 4 * f, y + 8), 2)


class Shot(Body):
    def __init__(self, x, y, vx, vy, owner):
        super().__init__(x - 8, y - 8, 16, 16)
        self.vx, self.vy, self.owner = vx, vy, owner
        self.life = 70 if owner == "hero" else 240
        self.alive = True

    def update(self, lvl):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        r = self.rect
        if self.life <= 0 or lvl.solid(r.centerx // TILE, r.centery // TILE):
            self.alive = False

    def draw(self, s, cam):
        cx, cy = int(self.x - cam + 8), int(self.y + 8)
        if self.owner == "hero":
            draw_heart(s, cx, cy, 16, (255, 70, 120))
            draw_heart(s, cx - 2, cy - 2, 6, (255, 200, 220))
        else:
            pygame.draw.circle(s, (255, 120, 30), (cx, cy), 9)
            pygame.draw.circle(s, (255, 230, 90), (cx, cy), 5)


# ---------------------------------------------------------------------
#  Hero
# ---------------------------------------------------------------------
class Player(Body):
    def __init__(self, x, y):
        super().__init__(x, y, 28, 40)
        self.facing = 1
        self.on_ground = False
        self.platform = None
        self.coyote = 0
        self.jump_buf = 0
        self.shoot_cd = 0
        self.invuln = 0
        self.hearts = 3
        self.anim = 0.0

    def draw(self, s, cam):
        sprites.draw_hero(s, self, cam)


def draw_princess(s, x, y, t, happy=False):
    sprites.draw_partner(s, x, y, t, happy)


# ---------------------------------------------------------------------
#  Game
# ---------------------------------------------------------------------
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption("Love Quest")
        self.state = "title"
        self.t = 0
        self.title_bg = make_gradient((255, 150, 190), (120, 80, 200))
        self.clouds = [(random.randint(0, 3000), random.randint(20, 200), random.randint(30, 60)) for _ in range(25)]
        self.reset_game()

    def reset_game(self):
        self.level_idx = 0
        self.time_left = TOTAL_TIME
        self.collected = set()
        self.particles = []
        self.load_level(0)

    def load_level(self, idx):
        self.level_idx = idx
        start_mem = sum(sum(r.count("M") for r in LEVELS[i]["map"]) for i in range(idx))
        self.level = Level(idx, start_mem)
        self.player = Player(*self.level.start)
        self.shots = []
        self.cam = 0.0
        self.toast = None
        self.card_t = 150

    def respawn(self):
        """Out of hearts or fell: restart this world (enemies too), keep letters."""
        got = set(self.collected)
        self.load_level(self.level_idx)
        self.level.memories = [m for m in self.level.memories if m[1] not in got]
        self.card_t = 0

    def burst(self, x, y, color, n=14, heart=False):
        for _ in range(n):
            self.particles.append(Particle(x, y, color, heart))

    def hurt(self):
        p = self.player
        if p.invuln:
            return
        p.hearts -= 1
        p.invuln = 70
        p.vy = -8
        self.burst(p.x + 14, p.y + 20, (255, 80, 80), 10)
        if p.hearts <= 0:
            self.respawn()

    # ---------------- update ----------------
    def update(self, keys, pressed):
        self.t += 1
        if self.state == "title":
            if pressed & {pygame.K_RETURN, pygame.K_SPACE}:
                self.reset_game()
                self.state = "play"
            return
        if self.state in ("win", "timeout"):
            if self.state == "win" and self.t % 6 == 0:
                self.burst(random.randint(0, W), -10, (255, random.randint(60, 150), 160), 1, heart=True)
            self.update_particles(gravity=0.05)
            if pressed & {pygame.K_RETURN} and self.t > 90:
                self.state = "title"
            return

        lvl, p = self.level, self.player
        if self.card_t > 0:
            self.card_t -= 1
            if pressed:
                self.card_t = 0
            return

        self.time_left -= 1 / FPS
        if self.time_left <= 0:
            self.state, self.t = "timeout", 0
            return

        # --- input ---
        left = keys[pygame.K_LEFT] or keys[pygame.K_a]
        right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        jump_keys = {pygame.K_SPACE, pygame.K_w, pygame.K_UP}
        jump_held = any(keys[k] for k in jump_keys)
        target = (right - left) * RUN_SPEED
        p.vx += (target - p.vx) * (0.35 if p.on_ground else 0.15)
        if target:
            p.facing = 1 if target > 0 else -1
        p.anim += 0.3
        if pressed & jump_keys:
            p.jump_buf = 8
        if p.jump_buf:
            p.jump_buf -= 1
        if p.coyote:
            p.coyote -= 1
        if p.jump_buf and (p.on_ground or p.coyote):
            p.vy = -JUMP_SPEED
            p.jump_buf = p.coyote = 0
            p.on_ground = False
            p.platform = None
        if not jump_held and p.vy < -4:
            p.vy = -4  # short hop when jump released early

        if p.shoot_cd:
            p.shoot_cd -= 1
        if (keys[pygame.K_j] or keys[pygame.K_x] or keys[pygame.K_f]) and not p.shoot_cd:
            self.shots.append(Shot(p.x + 14 + 16 * p.facing, p.y + 21, 9 * p.facing, 0, "hero"))
            p.shoot_cd = 14

        # --- moving platforms ---
        for mp in lvl.platforms:
            mp.update()
        if p.platform:
            p.x += p.platform.dx

        # --- physics ---
        p.vy = min(p.vy + GRAVITY, MAX_FALL)
        prev_bottom = p.y + p.h
        _, landed, bonk = lvl.move(p, p.vx, p.vy)
        if bonk:
            p.vy = 0
        was_ground = p.on_ground
        p.on_ground = landed
        p.platform = None
        if p.vy >= 0:
            for mp in lvl.platforms:
                r = mp.rect
                if p.rect.right > r.left and p.rect.left < r.right and prev_bottom <= r.top + 6 and p.y + p.h >= r.top:
                    p.y = r.top - p.h
                    p.on_ground = True
                    p.platform = mp
        if p.on_ground:
            p.vy = 0
            p.coyote = 6
        if p.invuln:
            p.invuln -= 1

        # fell into a gap
        if p.y > H + 60:
            p.hearts = 3
            self.respawn()
            return

        pr = p.rect
        # spikes (minor obstacle)
        for sp in lvl.spikes:
            if pr.colliderect(sp):
                self.hurt()
                p.vy = -10

        # enemies
        for e in lvl.enemies:
            e.update(lvl, p)
            if not e.alive:
                continue
            if pr.colliderect(e.rect):
                if p.vy > 0 and prev_bottom <= e.rect.top + 10:
                    e.alive = False
                    p.vy = -9
                    self.burst(e.x + 17, e.y + 15, (170, 120, 220))
                else:
                    self.hurt()
        lvl.enemies = [e for e in lvl.enemies if e.alive]

        # boss (major obstacle)
        b = lvl.boss
        if b and b.hp > 0:
            b.update(lvl, p, self.shots)
            if b.active and pr.colliderect(b.rect):
                if p.vy > 0 and prev_bottom <= b.rect.top + 16:
                    b.hp -= 2
                    b.flash = 20
                    p.vy = -12
                else:
                    self.hurt()
                    p.vx = -8 * (1 if b.x > p.x else -1)
            if b.hp <= 0:
                for _ in range(4):
                    self.burst(b.x + 45, b.y + 48, (255, 80, 120), 20, heart=True)
                self.show_toast("The Heartbreaker is defeated! The cage is open!")

        # shots
        for s in self.shots:
            s.update(lvl)
            if not s.alive:
                continue
            if s.owner == "hero":
                for e in lvl.enemies:
                    if s.rect.colliderect(e.rect):
                        e.alive = s.alive = False
                        self.burst(e.x + 17, e.y + 15, (255, 150, 200), heart=True)
                        break
                if s.alive and b and b.hp > 0 and b.active and s.rect.colliderect(b.rect):
                    b.hp -= 1
                    b.flash = 12
                    s.alive = False
                    self.burst(s.x, s.y, (255, 120, 170), 6, heart=True)
                    if b.hp <= 0:
                        for _ in range(4):
                            self.burst(b.x + 45, b.y + 48, (255, 80, 120), 20, heart=True)
                        self.show_toast("The Heartbreaker is defeated! The cage is open!")
            elif s.rect.colliderect(pr):
                s.alive = False
                self.hurt()
        self.shots = [s for s in self.shots if s.alive]
        lvl.enemies = [e for e in lvl.enemies if e.alive]

        # love letters
        for m in lvl.memories[:]:
            if pr.colliderect(m[0]):
                lvl.memories.remove(m)
                self.collected.add(m[1])
                self.burst(m[0].centerx, m[0].centery, (255, 100, 150), 16, heart=True)
                self.show_toast(MEMORIES[(len(self.collected) - 1) % len(MEMORIES)])

        # goals
        if lvl.door and pr.colliderect(lvl.door):
            self.load_level(self.level_idx + 1)
            return
        if lvl.princess and pr.colliderect(lvl.princess.inflate(10, 0)):
            self.state, self.t = "win", 0
            self.particles = []
            return

        if self.toast:
            self.toast[1] -= 1
            if self.toast[1] <= 0:
                self.toast = None

        target_cam = p.x - W * 0.4
        self.cam += (target_cam - self.cam) * 0.12
        self.cam = max(0, min(self.cam, lvl.width - W))
        self.update_particles()

    def show_toast(self, txt):
        self.toast = [txt, 220]

    def update_particles(self, gravity=0.25):
        for pt in self.particles:
            pt.x += pt.vx
            pt.y += pt.vy
            pt.vy += gravity
            pt.life -= 1 if gravity > 0.1 else 0
            if gravity <= 0.1 and pt.y > H + 20:
                pt.life = 0
        self.particles = [pt for pt in self.particles if pt.life > 0]

    # ---------------- draw ----------------
    def draw_world(self):
        s, lvl, cam = self.screen, self.level, self.cam
        backgrounds.draw(s, self.level_idx, cam, self.t)

        dirt, grass = lvl.data["dirt"], lvl.data["ground"]
        c0, c1 = int(cam // TILE), int((cam + W) // TILE) + 1
        for cy in range(lvl.rows):
            for cx in range(max(0, c0), min(lvl.cols, c1 + 1)):
                ch = lvl.grid[cy][cx]
                x, y = cx * TILE - int(cam), cy * TILE
                if ch == "#":
                    pygame.draw.rect(s, dirt, (x, y, TILE, TILE))
                    pygame.draw.rect(s, tuple(max(0, c - 20) for c in dirt), (x + 6, y + 18, 6, 6))
                    if cy > 0 and lvl.grid[cy - 1][cx] != "#":
                        pygame.draw.rect(s, grass, (x, y, TILE, 10))
                elif ch == "=":
                    pygame.draw.rect(s, (190, 90, 50), (x, y, TILE, TILE))
                    pygame.draw.rect(s, (120, 50, 30), (x, y, TILE, TILE), 2)
                    pygame.draw.line(s, (120, 50, 30), (x, y + 20), (x + TILE, y + 20), 2)
                    pygame.draw.line(s, (120, 50, 30), (x + 20, y), (x + 20, y + 20), 2)
                elif ch == "c" and lvl.solid(cx, cy):
                    for bx in (6, 18, 30):
                        pygame.draw.rect(s, (160, 160, 175), (x + bx, y, 5, TILE))
        for sp in lvl.spikes:
            x = sp.x - int(cam) - 4
            for i in range(2):
                bx = x + i * 20
                pygame.draw.polygon(s, (200, 200, 215), [(bx + 2, sp.bottom), (bx + 10, sp.top - 6), (bx + 18, sp.bottom)])
        for mp in lvl.platforms:
            r = mp.rect.move(-int(cam), 0)
            pygame.draw.rect(s, (240, 180, 80), r, border_radius=6)
            pygame.draw.rect(s, (150, 100, 40), r, 2, border_radius=6)
        if lvl.door:
            d = lvl.door.move(-int(cam), 0)
            pygame.draw.rect(s, (130, 70, 40), d, border_radius=14)
            pygame.draw.rect(s, (80, 40, 20), d, 3, border_radius=14)
            draw_heart(s, d.centerx, d.y + 22, 18, (255, 90, 140))
        for m in lvl.memories:
            r = m[0]
            bob = math.sin(self.t * 0.08 + m[2]) * 4
            x, y = r.x - int(cam), int(r.y + bob)
            pygame.draw.rect(s, (255, 250, 235), (x, y + 4, 24, 17))
            pygame.draw.lines(s, (200, 180, 160), False, [(x, y + 4), (x + 12, y + 13), (x + 24, y + 4)], 2)
            draw_heart(s, x + 12, y + 14, 10, (230, 40, 90))
        if lvl.princess:
            pr = lvl.princess
            draw_princess(s, pr.x - int(cam), pr.y, self.t / 60)
            if lvl.boss and lvl.boss.hp > 0 and self.t % 90 < 45:
                f = font(22).render("Help!", True, (255, 255, 255))
                s.blit(f, (pr.x - int(cam) - 4, pr.y - 30))
        for e in lvl.enemies:
            e.draw(s, cam)
        if lvl.boss:
            lvl.boss.draw(s, cam)
        for sh in self.shots:
            sh.draw(s, cam)
        self.player.draw(s, cam)
        self.draw_particles(cam)

    def draw_particles(self, cam=0):
        for pt in self.particles:
            if pt.heart:
                draw_heart(self.screen, int(pt.x - cam), int(pt.y), 10, pt.color)
            else:
                pygame.draw.circle(self.screen, pt.color, (int(pt.x - cam), int(pt.y)), 3)

    def draw_hud(self):
        s = self.screen
        for i in range(3):
            col = (255, 60, 100) if i < self.player.hearts else (90, 90, 90)
            draw_heart(s, 26 + i * 30, 26, 22, col)
        mins, secs = divmod(max(0, int(self.time_left)), 60)
        tcol = (255, 255, 255) if self.time_left > 30 else (255, 90, 90)
        t = font(36).render(f"{mins}:{secs:02d}", True, tcol)
        s.blit(t, t.get_rect(midtop=(W // 2, 10)))
        total = sum(sum(r.count("M") for r in L["map"]) for L in LEVELS)
        m = font(28).render(f"Love letters {len(self.collected)}/{total}", True, (255, 255, 255))
        s.blit(m, m.get_rect(topright=(W - 16, 14)))
        b = self.level.boss
        if b and b.active and b.hp > 0:
            pygame.draw.rect(s, (40, 0, 0), (W // 2 - 200, 48, 400, 14))
            pygame.draw.rect(s, (220, 30, 60), (W // 2 - 200, 48, int(400 * b.hp / b.MAX_HP), 14))
            n = font(22).render("THE HEARTBREAKER", True, (255, 220, 220))
            s.blit(n, n.get_rect(midtop=(W // 2, 64)))
        if self.toast:
            box = pygame.Rect(0, 0, 640, 46)
            box.center = (W // 2, H - 40)
            pygame.draw.rect(s, (255, 245, 250), box, border_radius=12)
            pygame.draw.rect(s, (230, 60, 110), box, 3, border_radius=12)
            tt = font(28).render(self.toast[0], True, (120, 20, 60))
            s.blit(tt, tt.get_rect(center=box.center))

    def draw(self):
        s = self.screen
        if self.state == "title":
            s.blit(self.title_bg, (0, 0))
            for i in range(12):
                x = (i * 97 + self.t) % (W + 40) - 20
                y = 60 + (i * 53) % 400 + math.sin(self.t / 30 + i) * 10
                draw_heart(s, int(x), int(y), 18, (255, 220, 235))
            text_center(s, "LOVE QUEST", 96, (255, 255, 255), 110)
            text_center(s, f"A tiny adventure made for {PARTNER_NAME}", 34, (255, 240, 250), 175)
            p = Player(W // 2 - 70, 250)
            p.on_ground = True
            p.draw(s, 0)
            draw_princess(s, W // 2 + 40, 242, self.t / 60, happy=True)
            draw_heart(s, W // 2, 245, 22, (255, 60, 110))
            text_center(s, "Move: Arrows / A D    Jump: Space / W    Shoot hearts: J / X / F", 28, (255, 255, 255), 350)
            text_center(s, f"Help {HERO_NAME} reach the princess in under {TOTAL_TIME // 60} minutes!", 28,
                        (255, 255, 255), 385)
            if self.t % 60 < 40:
                text_center(s, "Press ENTER to start", 40, (255, 255, 120), 450)
        elif self.state == "play":
            self.draw_world()
            self.draw_hud()
            if self.card_t > 0:
                ov = pygame.Surface((W, H), pygame.SRCALPHA)
                ov.fill((0, 0, 0, 170))
                s.blit(ov, (0, 0))
                text_center(s, self.level.data["name"], 52, (255, 255, 255), H // 2 - 30)
                text_center(s, self.level.data["sub"], 30, (255, 200, 220), H // 2 + 20)
        elif self.state == "win":
            s.fill((255, 190, 215))
            self.draw_particles()
            x = W // 2
            p = Player(x - 60, 150)
            p.on_ground = True
            p.draw(s, 0)
            draw_princess(s, x + 30, 142, self.t / 60, happy=True)
            draw_heart(s, x, 120 + int(math.sin(self.t / 15) * 5), 30, (240, 40, 90))
            text_center(s, f"{HERO_NAME} rescued {PARTNER_NAME}!", 56, (255, 255, 255), 240)
            for i, line in enumerate(ENDING_LINES):
                text_center(s, line, 34, (120, 20, 60), 295 + i * 32, shadow=False)
            total = sum(sum(r.count("M") for r in L["map"]) for L in LEVELS)
            used = TOTAL_TIME - int(self.time_left)
            text_center(s, f"Time: {used // 60}:{used % 60:02d}   Love letters: {len(self.collected)}/{total}",
                        26, (90, 30, 60), H - 40, shadow=False)
        elif self.state == "timeout":
            s.fill((40, 20, 50))
            text_center(s, "Out of time!", 70, (255, 120, 150), 190)
            text_center(s, "But true love always gets another try.", 34, (255, 255, 255), 250)
            text_center(s, "Press ENTER", 34, (255, 255, 120), 320)
        if self.state == "play":
            TOUCH.draw(s)
        pygame.display.flip()


def fit_to_screen(game):
    """On a phone held sideways, widen the game so it fills the whole screen."""
    global W
    new_w = touch.best_width(H, 960)
    if new_w and abs(new_w - W) > 8:
        W = new_w
        game.screen = pygame.display.set_mode((W, H))
        game.title_bg = make_gradient((255, 150, 190), (120, 80, 200))
        TOUCH.resize(W, H)

        
async def main():
    pygame.init()
    game = Game()
    clock = pygame.time.Clock()
    running = True
    frame = 0
    while running:
        if frame % 30 == 0:  # twice a second, check if the phone was turned
            fit_to_screen(game)
        frame += 1
        pressed = set()
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            elif ev.type == pygame.KEYDOWN:
                pressed.add(ev.key)
                if ev.key == pygame.K_ESCAPE and game.state != "title":
                    game.state = "title"
            TOUCH.handle(ev)
        held, tapped, tapped_anywhere = TOUCH.poll()
        pressed |= tapped
        if tapped_anywhere:
            pressed.add(pygame.K_RETURN)  # a tap works like Enter on menus
        game.update(touch.MergedKeys(pygame.key.get_pressed(), held), pressed)
        game.draw()
        clock.tick(FPS)
        await asyncio.sleep(0)  # lets the game run in the browser via pygbag
    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
