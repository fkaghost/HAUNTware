# game/menu.py
import pygame
import time

from game.assets import load_and_scale_font, load_and_scale_image
from game.ui import UI
from game.world import Character, Camera
from bettercap.client_wifi import BettercapWifiClient
from bettercap.control import start_bettercap, stop_bettercap, bettercap_is_running
from config import (
    BASE_WIDTH, BASE_HEIGHT, WIDTH, HEIGHT, SCALE_Y,
    RED, WHITE, GREEN,
    BACKGROUND_PATH, CURSOR_IMAGE_PATH, FONT_SLIMESPOOKY, FONT_PIXEL,
    MAP_IMAGE_PATH,
)


class Game:
    def __init__(self):
        self.BASE_WIDTH, self.BASE_HEIGHT = BASE_WIDTH, BASE_HEIGHT
        self.WIDTH, self.HEIGHT = WIDTH, HEIGHT
        self.scale_y = SCALE_Y

        pygame.init()
        pygame.display.set_caption("HAUNTware")
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.mouse.set_visible(False)

        self.wifi_client = BettercapWifiClient(poll_interval=1.0)
        self.cursor_image = load_and_scale_image(CURSOR_IMAGE_PATH, (64, 64), use_alpha=True)

    # ---------- Bettercap control ----------
    def start_bettercap_wifi(self):
        if bettercap_is_running():
            self.wifi_client.start()
            return

        ok = start_bettercap()
        if ok:
            self.wifi_client.start()
        else:
            print("[BETTERCAP] Failed to start or API not reachable")

    def stop_bettercap_wifi(self):
        self.wifi_client.stop()
        if bettercap_is_running():
            stop_bettercap()

    # ---------- Main menu ----------
    def game_loop(self):
        self.background = load_and_scale_image(BACKGROUND_PATH, (self.WIDTH, self.HEIGHT), use_alpha=False)

        slimespooky = load_and_scale_font(FONT_SLIMESPOOKY, 40, self.scale_y)
        pixel       = load_and_scale_font(FONT_PIXEL,       12, self.scale_y)

        hauntware_text = slimespooky.render("HAUNTware", True, RED)
        start_game_srf = pixel.render("Start Game", True, WHITE)
        wifi_srf       = pixel.render("Bettercap WiFi", True, WHITE)
        options_srf    = pixel.render("Options", True, WHITE)
        exit_srf       = pixel.render("Exit", True, WHITE)

        # (surface, base_y, label)
        texts = [
            (hauntware_text, 120, "TITLE"),
            (start_game_srf, 173, "START"),
            (wifi_srf,       198, "WIFI"),
            (options_srf,    223, "OPTIONS"),
            (exit_srf,       248, "EXIT"),
        ]

        menu_index = 1
        ui = UI(self.screen, self.background, self.cursor_image)
        status_font = load_and_scale_font(FONT_PIXEL, 10, self.scale_y)

        running = True
        clock = pygame.time.Clock()

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        menu_index = max(1, menu_index - 1)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        menu_index = min(len(texts) - 1, menu_index + 1)
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        label = texts[menu_index][2]
                        if label == "START":
                            print("[MENU] Start Game selected")
                            self.game_screen()
                        elif label == "WIFI":
                            print("[MENU] Bettercap WiFi selected")
                            self.start_bettercap_wifi()
                            self.wifi_devices_screen()
                        elif label == "OPTIONS":
                            print("[MENU] Options selected")
                        elif label == "EXIT":
                            print("[MENU] Exit selected")
                            running = False
                    elif event.key == pygame.K_ESCAPE:
                        if bettercap_is_running():
                            self.stop_bettercap_wifi()
                        else:
                            running = False

            # Badge next to Bettercap WiFi
            if bettercap_is_running():
                wifi_surface, base_y, _ = texts[2]
                text_w, text_h = wifi_surface.get_size()
                x = (self.WIDTH - text_w) // 2
                y = int(base_y * self.scale_y)
                ui.badge_overlay = (
                    status_font.render("[RUNNING]", True, GREEN),
                    (x + text_w + 12, y),
                )
            else:
                ui.badge_overlay = None

            # cursor
            focus_surface, base_y, _ = texts[menu_index]
            text_w, text_h = focus_surface.get_size()
            cursor_pos = (
                (self.WIDTH - text_w) // 2 - self.cursor_image.get_width() - 10,
                int(base_y * self.scale_y) + (text_h - self.cursor_image.get_height()) // 2,
            )

            # ui expects list of (surface, base_y)
            ui.draw_menu([(t[0], t[1]) for t in texts], menu_index, cursor_pos)
            pygame.display.flip()
            clock.tick(60)

        if bettercap_is_running():
            self.stop_bettercap_wifi()
        pygame.quit()

    # ---------- Bettercap WiFi devices screen ----------
    def wifi_devices_screen(self):
        """Full-screen WiFi AP view using Bettercap."""
        bg = pygame.Surface((self.WIDTH, self.HEIGHT))
        bg.fill((10, 10, 10))

        title_font = load_and_scale_font(FONT_SLIMESPOOKY, 20, self.scale_y)
        row_font   = load_and_scale_font(FONT_PIXEL,       10, self.scale_y)
        hint_font  = load_and_scale_font(FONT_PIXEL,        9, self.scale_y)

        title_surf = title_font.render("Bettercap — WiFi APs", True, RED)

        # layout
        left_margin  = 20
        right_margin = 20
        col_padding  = 24

        def text_width(f, s):
            return f.size(s)[0]

        def ellipsize_to_width(f, s, max_px):
            if text_width(f, s) <= max_px:
                return s
            ell = "…"
            ell_w = text_width(f, ell)
            lo, hi = 0, len(s)
            best = ""
            while lo <= hi:
                mid = (lo + hi) // 2
                cand = s[:mid]
                if text_width(f, cand) + ell_w <= max_px:
                    best = cand
                    lo = mid + 1
                else:
                    hi = mid - 1
            return best + ell

        BSSID_SAMPLE  = "AA:BB:CC:DD:EE:FF"
        BSSID_COL_W   = text_width(row_font, BSSID_SAMPLE)
        SIGNAL_SAMPLE = "-100 dBm"
        SIGNAL_COL_W  = text_width(row_font, SIGNAL_SAMPLE)

        top_idx = 0
        running = True
        clock = pygame.time.Clock()

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop_bettercap_wifi()
                    pygame.quit()
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.stop_bettercap_wifi()
                        return
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        top_idx += 1
                    elif event.key in (pygame.K_UP, pygame.K_w):
                        top_idx = max(0, top_idx - 1)
                    elif event.key == pygame.K_PAGEDOWN:
                        top_idx += 10
                    elif event.key == pygame.K_PAGEUP:
                        top_idx = max(0, top_idx - 10)

            self.screen.blit(bg, (0, 0))

            # title + update age
            self.screen.blit(title_surf, (20, 16))
            devices, last_t = self.wifi_client.get_snapshot()
            age = int(time.time() - last_t) if last_t else None
            age_text = f"Updated: {age}s ago" if age is not None else "Updating…"
            self.screen.blit(hint_font.render(age_text, True, (180, 180, 180)), (20, 54))

            # dynamic column positions
            signal_right_x = self.WIDTH - right_margin
            bssid_right_x  = signal_right_x - SIGNAL_COL_W - col_padding
            ssid_left_x    = left_margin
            ssid_right_x   = bssid_right_x - col_padding
            ssid_col_w     = max(50, ssid_right_x - ssid_left_x)

            # headers
            ssid_hdr  = row_font.render("SSID",   True, (200, 200, 200))
            bssid_hdr = row_font.render("BSSID",  True, (200, 200, 200))
            sig_hdr   = row_font.render("SIGNAL", True, (200, 200, 200))

            self.screen.blit(ssid_hdr,  (ssid_left_x, 80))
            self.screen.blit(bssid_hdr, (bssid_right_x - BSSID_COL_W, 80))
            self.screen.blit(sig_hdr,   (signal_right_x - text_width(row_font, "SIGNAL"), 80))

            pygame.draw.line(
                self.screen, (60, 60, 60),
                (left_margin, 100), (self.WIDTH - right_margin, 100), 1
            )

            # rows
            line_y  = 110
            line_h  = int(18 * self.scale_y)
            max_top = max(0, len(devices) - 1)
            top_idx = max(0, min(top_idx, max_top))
            max_rows = (self.HEIGHT - line_y - 30) // line_h

            for dev in devices[top_idx: top_idx + max_rows]:
                ssid  = dev["ssid"] or "<hidden>"
                bssid = dev["bssid"]
                sig   = int(dev["signal"])

                ssid_txt = ellipsize_to_width(row_font, ssid, ssid_col_w)
                sig_txt  = f"{sig} dBm"

                self.screen.blit(row_font.render(ssid_txt, True, WHITE),
                                 (ssid_left_x, line_y))
                self.screen.blit(row_font.render(bssid, True, WHITE),
                                 (bssid_right_x - BSSID_COL_W, line_y))
                self.screen.blit(row_font.render(sig_txt, True, WHITE),
                                 (signal_right_x - text_width(row_font, sig_txt), line_y))

                line_y += line_h
                if line_y > self.HEIGHT - 30:
                    break

            hint = "↑/↓ PgUp/PgDn to scroll  •  ESC to stop Bettercap & return"
            self.screen.blit(hint_font.render(hint, True, (160, 160, 160)),
                             (20, self.HEIGHT - 26))

            pygame.display.flip()
            clock.tick(60)

    # ---------- Game world (haunted map) ----------
    def game_screen(self):
        print("[GAME] Entering game_screen (map)")
        world_w, world_h = 1500, 1000

        try:
            self.background = load_and_scale_image(
                MAP_IMAGE_PATH, (world_w, world_h), use_alpha=False
            )
            print(f"[GAME] Loaded map: {MAP_IMAGE_PATH}")
        except Exception as e:
            print(f"[GAME] Failed to load map at {MAP_IMAGE_PATH}: {e}")
            self.background = pygame.Surface((world_w, world_h))
            self.background.fill((20, 20, 20))

        character = Character([self.WIDTH // 2, self.HEIGHT // 2])
        camera = Camera(pygame.Rect(0, 0, self.WIDTH, self.HEIGHT), world_w, world_h)
        ui = UI(self.screen, self.background, self.cursor_image)

        running = True
        clock = pygame.time.Clock()

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if bettercap_is_running():
                        self.stop_bettercap_wifi()
                    print("[GAME] QUIT in map -> leaving")
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if bettercap_is_running():
                        self.stop_bettercap_wifi()
                    print("[GAME] ESC in map -> return to menu")
                    running = False

            keys = pygame.key.get_pressed()
            character.move(keys)
            camera.update(character.pos)

            cursor_pos = (
                character.pos[0] - camera.rect.left,
                character.pos[1] - camera.rect.top,
            )

            ui.draw_world(character.pos, camera.rect, cursor_pos)
            clock.tick(60)

        print("[GAME] Exiting game_screen (map)")


def game_main_menu():
    Game().game_loop()
