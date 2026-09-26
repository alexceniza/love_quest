"""
On-screen touch controls so Love Quest works on phones (iPhone, Android).

The buttons only appear after the first touch, so on a computer with a
keyboard nothing changes. Each finger is tracked separately, so she can
hold "right" and tap "jump" at the same time.
"""
import pygame

RADIUS = 46          # button size
HIT = 64             # how far from the centre a touch still counts (a bit generous)

# action -> the keyboard key it pretends to press
KEYMAP = {
    "left": pygame.K_LEFT,
    "right": pygame.K_RIGHT,
    "jump": pygame.K_SPACE,
    "shoot": pygame.K_j,
}


class MergedKeys:
    """Acts like pygame.key.get_pressed(), but also counts touch buttons."""

    def __init__(self, real, extra):
        self.real, self.extra = real, extra

    def __getitem__(self, k):
        return bool(self.real[k]) or k in self.extra


class TouchControls:
    def __init__(self, w, h):
        self.w, self.h = w, h
        y = h - 70
        self.buttons = {
            "left": (70, y),
            "right": (180, y),
            "shoot": (w - 180, y),
            "jump": (w - 70, y),
        }
        self.active = False          # becomes True on the first real touch
        self.fingers = {}            # finger id -> action (or None)
        self.tapped = set()          # actions pressed this frame
        self.tapped_anywhere = False

    def _action_at(self, x, y):
        for name, (bx, by) in self.buttons.items():
            if (x - bx) ** 2 + (y - by) ** 2 <= HIT ** 2:
                return name
        return None

    def handle(self, ev):
        if ev.type in (pygame.FINGERDOWN, pygame.FINGERMOTION, pygame.FINGERUP):
            self.active = True
            x, y = ev.x * self.w, ev.y * self.h
            if ev.type == pygame.FINGERUP:
                self.fingers.pop(ev.finger_id, None)
                return
            action = self._action_at(x, y)
            if ev.type == pygame.FINGERDOWN:
                self.tapped_anywhere = True
                if action:
                    self.tapped.add(action)
            elif action and self.fingers.get(ev.finger_id) != action:
                self.tapped.add(action)   # slid onto a new button
            self.fingers[ev.finger_id] = action

    def poll(self):
        """Returns (held keys, keys tapped this frame, tapped anywhere?) and resets taps."""
        held = {KEYMAP[a] for a in self.fingers.values() if a}
        tapped = {KEYMAP[a] for a in self.tapped}
        anywhere = self.tapped_anywhere
        self.tapped = set()
        self.tapped_anywhere = False
        return held, tapped, anywhere

    def draw(self, surf):
        if not self.active:
            return
        layer = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        held = set(a for a in self.fingers.values() if a)
        for name, (x, y) in self.buttons.items():
            alpha = 150 if name in held else 80
            pygame.draw.circle(layer, (255, 255, 255, alpha), (x, y), RADIUS)
            pygame.draw.circle(layer, (60, 40, 70, 160), (x, y), RADIUS, 3)
            ink = (60, 40, 70, 220)
            if name == "left":
                pygame.draw.polygon(layer, ink, [(x - 18, y), (x + 12, y - 18), (x + 12, y + 18)])
            elif name == "right":
                pygame.draw.polygon(layer, ink, [(x + 18, y), (x - 12, y - 18), (x - 12, y + 18)])
            elif name == "jump":
                pygame.draw.polygon(layer, ink, [(x, y - 20), (x - 18, y + 4), (x + 18, y + 4)])
                pygame.draw.rect(layer, ink, (x - 7, y + 4, 14, 14))
            else:  # shoot: a heart
                col = (235, 60, 110, 230)
                pygame.draw.circle(layer, col, (x - 8, y - 5), 10)
                pygame.draw.circle(layer, col, (x + 8, y - 5), 10)
                pygame.draw.polygon(layer, col, [(x - 18, y - 1), (x + 18, y - 1), (x, y + 19)])
        surf.blit(layer, (0, 0))
