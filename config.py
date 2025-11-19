# =======================
# HAUNTware Configuration
# =======================

# config.py
from pathlib import Path

# ---------- Screen Dimensions ----------
BASE_WIDTH = 480
BASE_HEIGHT = 320
WIDTH = 960
HEIGHT = 640
SCALE_X = WIDTH / BASE_WIDTH
SCALE_Y = HEIGHT / BASE_HEIGHT

# ---------- Project root ----------
ROOT = Path(__file__).resolve().parent

# ---------- Asset Paths ----------
BACKGROUND_PATH    = ROOT / "resources/backgrounds/GreyStoneBorderOnBlackBackground.png"
CURSOR_IMAGE_PATH  = ROOT / "resources/ghostie/Ghostie_64x64.png"
MAP_IMAGE_PATH     = ROOT / "resources/maps/hauntedMap1500x1000.png"

# Fonts
FONT_SLIMESPOOKY   = ROOT / "resources/fonts/Slimespooky.ttf"
FONT_PIXEL         = ROOT / "resources/fonts/PixelEmulator.otf"

# ---------- UI Colors ----------
RED   = (255, 94, 94)
WHITE = (255, 255, 255)
BLACK = (0,   0,   0)
GRAY  = (40,  40,  40)
GREEN = (100, 220, 100)
PANEL_BG = (18, 18, 18)
