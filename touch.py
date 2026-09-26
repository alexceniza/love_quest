"""
On-screen touch controls so Love Quest works on phones (iPhone, Android).

In the browser, touches are read straight from the web page with a tiny bit
of JavaScript. That is the most reliable way on iPhone, and it supports
several fingers at once (hold "right" and tap "jump"). Pygame's own touch
and mouse events are kept as a backup.

The buttons only appear after the first touch, so on a computer with a
keyboard nothing changes.
"""
import json
import sys

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

# JavaScript that records every finger on the screen into window.lqTouchJSON
_JS = """
(function () {
  if (window.lqTouchReady) return;
  window.lqTouchReady = true;
  window.lqTouchJSON = "[]";
  function update(e) {
    var c = document.getElementById("canvas") || document.querySelector("canvas");
    var r = c ? c.getBoundingClientRect()
              : {left: 0, top: 0, width: window.innerWidth, height: window.innerHeight};
    var out = [];
    for (var i = 0; i < e.touches.length; i++) {
      var t = e.touches[i];
      out.push([t.identifier, (t.clientX - r.left) / r.width, (t.clientY - r.top) / r.height]);
    }
    window.lqTouchJSON = JSON.stringify(out);
    if (e.cancelable) e.preventDefault();   // stop Safari scrolling or zooming
  }
  ["touchstart", "touchmove", "touchend", "touchcancel"].forEach(function (name) {
    document.addEventListener(name, update, {passive: false});
  });
})();
"""


def _browser_window():
    """The web page's window object when running in the browser (pygbag), else None."""
    if sys.platform != "emscripten":
        return None
    try:
        import platform
        return platform.window
    except Exception:
        return None


def best_width(h, default_w, max_w=1200):
    """In a landscape phone browser, the game width that fills the screen exactly.

    Returns None when not in a browser or when the phone is in portrait
    (then the "turn your phone" message is showing anyway).
    """
    win = _browser_window()
    if win is None:
        return None
    try:
        vw, vh = float(win.innerWidth), float(win.innerHeight)
    except Exception:
        return None
    if vw <= 0 or vh <= 0 or vw < vh:
        return None
    return max(default_w, min(max_w, int(round(h * vw / vh))))


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
        self.js = _browser_window()
        if self.js is not None:
            try:
                self.js.eval(_JS)
            except Exception:
                self.js = None

    def resize(self, w, h):
        self.w, self.h = w, h
        y = h - 70
        self.buttons = {"left": (70, y), "right": (180, y), "shoot": (w - 180, y), "jump": (w - 70, y)}

    def _action_at(self, x, y):
        for name, (bx, by) in self.buttons.items():
            if (x - bx) ** 2 + (y - by) ** 2 <= HIT ** 2:
                return name
        return None

    def _press(self, fid, x, y, new):
        action = self._action_at(x, y)
        if new:
            self.tapped_anywhere = True
        if action and (new or self.fingers.get(fid) != action):
            self.tapped.add(action)
        self.fingers[fid] = action

    # --- reading touches straight from the web page (best on iPhone) ---
    def _read_js(self):
        try:
            touches = json.loads(str(self.js.lqTouchJSON))
        except Exception:
            return False
        now = {}
        for fid, nx, ny in touches:
            now[("js", fid)] = (nx * self.w, ny * self.h)
        if now:
            self.active = True
        for fid in list(self.fingers):
            if fid[0] == "js" and fid not in now:
                del self.fingers[fid]
        for fid, (x, y) in now.items():
            self._press(fid, x, y, new=fid not in self.fingers)
        return True

    # --- backup: pygame's own touch / mouse events ---
    def handle(self, ev):
        if ev.type in (pygame.FINGERDOWN, pygame.FINGERMOTION, pygame.FINGERUP):
            self.active = True
            fid = ("finger", ev.finger_id)
            if ev.type == pygame.FINGERUP:
                self.fingers.pop(fid, None)
            else:
                self._press(fid, ev.x * self.w, ev.y * self.h, new=ev.type == pygame.FINGERDOWN)
        elif ev.type == pygame.MOUSEBUTTONDOWN:
            self._press(("mouse",), ev.pos[0], ev.pos[1], new=True)
        elif ev.type == pygame.MOUSEMOTION and ("mouse",) in self.fingers:
            self._press(("mouse",), ev.pos[0], ev.pos[1], new=False)
        elif ev.type == pygame.MOUSEBUTTONUP:
            self.fingers.pop(("mouse",), None)

    def poll(self):
        """Returns (held keys, keys tapped this frame, tapped anywhere?) and resets taps."""
        if self.js is not None:
            self._read_js()
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
