"""
Makes the web build feel like a phone app. Run by GitHub Actions after pygbag builds.

- fills the whole iPhone screen (no page margins, no scrolling or zooming)
- keeps the pixel art crisp when it is scaled up to the phone's resolution
- lets "Add to Home Screen" open it full screen like an app
- shows a "turn your phone sideways" screen while the phone is upright
"""
import re
import sys

path = sys.argv[1] if len(sys.argv) > 1 else "build/web/index.html"
html = open(path, encoding="utf-8").read()

HEAD = """
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Love Quest">
<meta name="theme-color" content="#000000">
<style>
  html, body {
    margin: 0 !important; padding: 0 !important;
    width: 100%; height: 100%;
    overflow: hidden !important;
    background: #000 !important;
    touch-action: none;
    overscroll-behavior: none;
    -webkit-user-select: none; user-select: none;
    -webkit-touch-callout: none;
    -webkit-tap-highlight-color: transparent;
  }
  canvas#canvas {
    position: fixed !important;
    left: 0 !important; top: 0 !important;
    width: 100vw !important;
    height: 100vh !important;
    height: 100dvh !important;
    image-rendering: pixelated;          /* crisp pixels when scaled up */
    image-rendering: crisp-edges;
  }
  #lq-rotate {
    display: none;
    position: fixed; inset: 0; z-index: 99999;
    background: linear-gradient(#ff96be, #7850c8);
    color: #fff; font-family: -apple-system, Helvetica, sans-serif;
    flex-direction: column; align-items: center; justify-content: center;
    text-align: center; gap: 22px;
  }
  #lq-rotate .phone {
    width: 46px; height: 80px; border: 5px solid #fff; border-radius: 10px;
    animation: lq-turn 1.6s ease-in-out infinite;
  }
  #lq-rotate p { font-size: 22px; font-weight: 700; margin: 0 24px; }
  #lq-rotate small { font-size: 15px; opacity: 0.9; }
  @keyframes lq-turn { 0%, 30% { transform: rotate(0deg); } 60%, 100% { transform: rotate(-90deg); } }
  @media (orientation: portrait) and (max-width: 900px) {
    #lq-rotate { display: flex; }
  }
</style>
"""

BODY = """
<div id="lq-rotate">
  <div class="phone"></div>
  <p>Turn your phone sideways to play</p>
  <small>A tiny adventure is waiting for you &hearts;</small>
</div>
"""

# replace pygbag's own viewport tags with ours (only one should exist)
html = re.sub(r'<meta\s+name="viewport"[^>]*>\s*', "", html, flags=re.I)
html = re.sub(r"</head>", HEAD + "</head>", html, count=1, flags=re.I)
html = re.sub(r"(<body[^>]*>)", r"\1" + BODY, html, count=1, flags=re.I)
open(path, "w", encoding="utf-8").write(html)
print("mobile patch applied to", path)
