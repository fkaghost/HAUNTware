# game/menu.py
import os
import pygame
import time

from game.assets import load_and_scale_font, load_and_scale_image
from game.ui import UI
from game.world import Character, Camera

# --- Bettercap modules ---
from bettercap.client import BettercapWifiClient
from bettercap.control import start_bettercap, stop_bettercap, bettercap_is_running

# --- HAUNTware config ---
from config import (
    BASE_WIDTH, BASE_HEIGHT,
    WIDTH, HEIGHT, SCALE_Y,
    RED, WHITE, GREEN,
    BACKGROUND_PATH, CURSOR_IMAGE_PATH,
    FONT_SLIMESPOOKY, FONT_PIXEL,
    MAP_IMAGE_PATH,
)


class Game:
    def __init__(self):
        # Basic resolution metrics
        self.BASE_WIDTH, self.BASE_HEIGHT = BASE_WIDTH, BASE_HEIGHT

        pygame.init()
        pygame.display.set_caption("HAUNTware")

        # --- Fullscreen for Raspberry Pi ---
        info = pygame.display.Info()
        self.WIDTH  = info.current_w
        self.HEIGHT = info.current_h
        self.scale_x = self.WIDTH / BASE_WIDTH
        self.scale_y = self.HEIGHT / BASE_HEIGHT

        self.screen = pygame.display.set_mode(
            (self.WIDTH, self.HEIGHT),
            pygame.FULLSCREEN | pygame.NOFRAME
        )
        pygame.mouse.set_visible(False)

        # ---- Bettercap WiFi client ----
        self.wifi_client = BettercapWifiClient(poll_interval=1.0)

        # ---- Cursor image ----
        self.cursor_image = load_and_scale_image(CURSOR_IMAGE_PATH, (64, 64), use_alpha=True)

    # -------------------------------------------------------------------------
    #                          BETTERCAP CONTROL
    # -------------------------------------------------------------------------
    def start_bettercap_wifi(self):
        if bettercap_is_running():
            self.wifi_client.start()
            return

        success = start_bettercap()
        if success:
            print("[BETTERCAP] Started successfully.")
            self.wifi_client.start()
        else:
            print("[BETTERCAP] Could not start. Is bettercap running?")

    def stop_bettercap_wifi(self):
        self.wifi_client.stop()
        if bettercap_is_running():
            stop_bettercap()

    # -------------------------------------------------------------------------
    #                            MAIN MENU LOOP
    # -------------------------------------------------------------------------
    def game_loop(self):
        self.background = load_and_scale_image(
            BACKGROUND_PATH,
            (self.WIDTH, self.HEIGHT),
            use_alpha=False
        )

        slimespooky = load_and_scale_font(FONT_SLIMESPOOKY, 40, self.scale_y)
        pixel = load_and_scale_font(FONT_PIXEL, 12, self.scale_y)

        hauntware_srf = slimespooky.render("HAUNTware", True, RED)
        start_srf     = pixel.render("Start Game", True, WHITE)
        wifi_srf      = pixel.render("Bettercap WiFi", True, WHITE)
        adapter_srf   = pixel.render("WiFi Adapter", True, WHITE)
        options_srf   = pixel.render("Options", True, WHITE)
        exit_srf      = pixel.render("Exit", True, WHITE)

        # (surface, base_y, label)
        texts = [
            (hauntware_srf, 120, "TITLE"),
            (start_srf,     173, "START"),
            (wifi_srf,      198, "WIFI"),
            (adapter_srf,   223, "ADAPTER"),
            (options_srf,   248, "OPTIONS"),
            (exit_srf,      273, "EXIT"),
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

                        elif label == "ADAPTER":
                            print("[MENU] WiFi Adapter settings selected")
                            self.wifi_adapter_screen()

                        elif label == "OPTIONS":
                            print("[MENU] Options selected")

                        elif label == "EXIT":
                            running = False

                    elif event.key == pygame.K_ESCAPE:
                        if bettercap_is_running():
                            self.stop_bettercap_wifi()
                        running = False

            # --- Running badge next to Bettercap WiFi ---
            if bettercap_is_running():
                wifi_surface, base_y, _ = texts[2]
                x = (self.WIDTH - wifi_surface.get_width()) // 2
                y = int(base_y * self.scale_y)
                ui.badge_overlay = (
                    status_font.render("[RUNNING]", True, GREEN),
                    (x + wifi_surface.get_width() + 12, y)
                )
            else:
                ui.badge_overlay = None

            # --- Cursor position ---
            focus_srf, base_y, _ = texts[menu_index]
            text_w, text_h = focus_srf.get_size()
            cursor_pos = (
                (self.WIDTH - text_w) // 2 - self.cursor_image.get_width() - 10,
                int(base_y * self.scale_y) + (text_h - self.cursor_image.get_height()) // 2,
            )

            ui.draw_menu([(s, y) for s, y, _ in texts], menu_index, cursor_pos)
            pygame.display.flip()
            clock.tick(60)

        if bettercap_is_running():
            self.stop_bettercap_wifi()
        pygame.quit()

    # -------------------------------------------------------------------------
    #                       WIFI ADAPTER MODE SCREEN
    # -------------------------------------------------------------------------
    def wifi_adapter_screen(self):
        pixel = load_and_scale_font(FONT_PIXEL, 12, self.scale_y)
    
        options = [
            ("Set wlan1 → Monitor", pixel.render("Set wlan1 → Monitor", True, WHITE), "MONITOR"),
            ("Set wlan1 → Managed", pixel.render("Set wlan1 → Managed", True, WHITE), "MANAGED"),
            ("Back",                pixel.render("Back", True, WHITE),                "BACK"),
        ]
    
        index = 0
        clock = pygame.time.Clock()
    
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        index = (index - 1) % len(options)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        index = (index + 1) % len(options)
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        text, surf, label = options[index]
                        if label == "MONITOR":
                            os.system("sudo ip link set wlan1 down")
                            os.system("sudo iwconfig wlan1 mode monitor")
                            os.system("sudo ip link set wlan1 up")
                        elif label == "MANAGED":
                            os.system("sudo ip link set wlan1 down")
                            os.system("sudo iwconfig wlan1 mode managed")
                            os.system("sudo ip link set wlan1 up")
                        elif label == "BACK":
                            return
                    elif event.key == pygame.K_ESCAPE:
                        return
    
            # Render screen
            self.screen.fill((10, 10, 10))
    
            y = 140
            for i, (text, surf, label) in enumerate(options):
                color = GREEN if i == index else WHITE
                render = pixel.render(text, True, color)
                x = (self.WIDTH - render.get_width()) // 2
                self.screen.blit(render, (x, y))
                y += 40
    
            pygame.display.flip()
            clock.tick(60)

    # -------------------------------------------------------------------------
    #                  WIFI DEVICE LIST — BETTERCAP SCAN
    # -------------------------------------------------------------------------
    def wifi_devices_screen(self):
        """
        Displays APs discovered by Bettercap WiFi module.
        """
        bg = pygame.Surface((self.WIDTH, self.HEIGHT))
        bg.fill((10, 10, 10))

        title_font = load_and_scale_font(FONT_SLIMESPOOKY, 20, self.scale_y)
        row_font   = load_and_scale_font(FONT_PIXEL,       10, self.scale_y)
        hint_font  = load_and_scale_font(FONT_PIXEL,        9, self.scale_y)

        title_surf = title_font.render("Bettercap — WiFi APs", True, RED)

        # Layout
        left_margin  = 20
        right_margin = 20
        col_padding  = 24

        def text_width(font, text):
            return font.size(text)[0]

        def ellipsize(font, text, limit):
            if text_width(font, text) <= limit:
                return text
            ell = "…"
            ell_w = text_width(font, ell)
            lo, hi, best = 0, len(text), ""
            while lo <= hi:
                mid = (lo + hi) // 2
                if text_width(font, text[:mid]) + ell_w <= limit:
                    best = text[:mid]
                    lo += 1
                else:
                    hi -= 1
            return best + ell

        BSSID_SAMPLE = "AA:BB:CC:DD:EE:FF"
        SIGNAL_SAMPLE = "-100 dBm"
        BSSID_COL_W = text_width(row_font, BSSID_SAMPLE)
        SIGNAL_COL_W = text_width(row_font, SIGNAL_SAMPLE)

        top_idx = 0
        clock = pygame.time.Clock()
        running = True

        while running:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.stop_bettercap_wifi()
                    pygame.quit()
                    return

                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        return
                    elif e.key in (pygame.K_DOWN, pygame.K_s):
                        top_idx += 1
                    elif e.key in (pygame.K_UP, pygame.K_w):
                        top_idx -= 1
                        if top_idx < 0:
                            top_idx = 0
                    elif e.key == pygame.K_PAGEDOWN:
                        top_idx += 8
                    elif e.key == pygame.K_PAGEUP:
                        top_idx = max(0, top_idx - 8)

            devices, last_t = self.wifi_client.get_snapshot()

            self.screen.blit(bg, (0, 0))
            self.screen.blit(title_surf, (20, 16))

            age = int(time.time() - last_t) if last_t else None
            age_surf = hint_font.render(
                f"Updated: {age}s ago" if last_t else "Updating…",
                True,
                WHITE
            )
            self.screen.blit(age_surf, (20, 54))

            # Column positions
            signal_right_x = self.WIDTH - right_margin
            bssid_right_x  = signal_right_x - SIGNAL_COL_W - col_padding
            ssid_left_x    = left_margin
            ssid_right_x   = bssid_right_x - col_padding
            ssid_col_w     = max(50, ssid_right_x - ssid_left_x)

            # Headers
            self.screen.blit(row_font.render("SSID", True, WHITE), (ssid_left_x, 80))
            self.screen.blit(row_font.render("BSSID", True, WHITE), (bssid_right_x - BSSID_COL_W, 80))
            self.screen.blit(row_font.render("SIGNAL", True, WHITE),
                             (signal_right_x - text_width(row_font, "SIGNAL"), 80))

            pygame.draw.line(
                self.screen, (60, 60, 60),
                (left_margin, 100), (self.WIDTH - right_margin, 100), 1
            )

            # Rows
            line_y = 110
            line_h = int(18 * self.scale_y)

            visible = devices[top_idx: top_idx + ((self.HEIGHT - 140) // line_h)]

            for dev in visible:
                ssid  = dev.get("ssid") or "<hidden>"
                bssid = dev.get("bssid") or "??:??:??:??:??:??"
                sig   = dev.get("signal", -100)

                ssid_txt = ellipsize(row_font, ssid, ssid_col_w)
                sig_txt  = f"{sig} dBm"

                self.screen.blit(
                    row_font.render(ssid_txt, True, WHITE),
                    (ssid_left_x, line_y)
                )
                self.screen.blit(
                    row_font.render(bssid, True, WHITE),
                    (bssid_right_x - BSSID_COL_W, line_y)
                )
                self.screen.blit(
                    row_font.render(sig_txt, True, WHITE),
                    (signal_right_x - text_width(row_font, sig_txt), line_y)
                )

                line_y += line_h
                if line_y > self.HEIGHT - 40:
                    break

            pygame.display.flip()
            clock.tick(60)

    # -------------------------------------------------------------------------
    #                          GAME WORLD (MAP)
    # -------------------------------------------------------------------------
    def game_screen(self):
        print("[GAME] Loading map...")

        world_w, world_h = 1500, 1000
        try:
            self.background = load_and_scale_image(
                MAP_IMAGE_PATH, (world_w, world_h), use_alpha=False
            )
        except Exception as e:
            print(f"[GAME] Failed to load map: {e}")
            self.background = pygame.Surface((world_w, world_h))
            self.background.fill((20, 20, 20))

        character = Character([self.WIDTH // 2, self.HEIGHT // 2])
        camera = Camera(
            pygame.Rect(0, 0, self.WIDTH, self.HEIGHT),
            world_w, world_h
        )
        ui = UI(self.screen, self.background, self.cursor_image)

        running = True
        clock = pygame.time.Clock()

        while running:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return
                elif e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                    return

            keys = pygame.key.get_pressed()
            character.move(keys)
            camera.update(character.pos)

            cursor_pos = (
                character.pos[0] - camera.rect.left,
                character.pos[1] - camera.rect.top
            )
            ui.draw_world(character.pos, camera.rect, cursor_pos)
            clock.tick(60)


def game_main_menu():
    Game().game_loop()
