# =======================
# HAUNTware Configuration
# =======================

from pathlib import Path

# ---------- Screen Dimensions ----------
BASE_WIDTH  = 480
BASE_HEIGHT = 320
WIDTH       = 960
HEIGHT      = 640

SCALE_X = WIDTH / BASE_WIDTH
SCALE_Y = HEIGHT / BASE_HEIGHT

# ---------- Kismet Settings ----------
KISMET_SCRIPT     = "/usr/local/bin/kismet_start_wlx.sh"  # wrapper you created
KISMET_API_BASE   = "http://127.0.0.1:2501"
KISMET_VIEW       = "phy-IEEE802.11"
KISMET_DEVICES_URL = f"{KISMET_API_BASE}/devices/views/{KISMET_VIEW}/last-time/-10/devices.json"
KISMET_TOKEN      = "F097C5D3D0D9CDAEEC585654B871D325"

# ---------- Asset Paths (resolve from repo root) ----------
ROOT = Path(__file__).resolve().parent

BACKGROUND_PATH     = ROOT / "resources/backgrounds/GreyStoneBorderOnBlackBackground.png"
CURSOR_IMAGE_PATH   = ROOT / "Ghostie/Ghostie_64x64.png"
MAP_IMAGE_PATH      = ROOT / "resources/maps/hauntedMap1500x1000.png"
FONT_SLIMESPOOKY    = ROOT / "resources/fonts/Slimespooky.ttf"
FONT_PIXEL          = ROOT / "resources/fonts/PixelEmulator.otf"

# ---------- UI Colors ----------
RED   = (255,  94,  94)
WHITE = (255, 255, 255)
BLACK = (0,     0,   0)
GRAY  = (40,   40,  40)
GREEN = (100, 220, 100)
PANEL_BG = (18, 18, 18)

# ---------- Helpers ----------
def clamp(v, lo, hi):
    return max(lo, min(v, hi))