# game/menu.py
import pygame
import time

from game.assets import load_and_scale_font, load_and_scale_image
from game.ui import UI
from game.world import Character, Camera
from kismet.client import KismetClient
from kismet.client_probes import KismetProbesClient
from kismet.control import start_kismet, stop_kismet, kismet_running
from config import (
    BASE_WIDTH, BASE_HEIGHT, WIDTH, HEIGHT, SCALE_Y,
    RED, WHITE, GREEN, KISMET_DEVICES_URL, KISMET_TOKEN,
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

        # Kismet clients
        self.kismet = KismetClient(KISMET_DEVICES_URL, token=KISMET_TOKEN, poll_interval=1.0)
        self.kismet_probes = KismetProbesClient(KISMET_DEVICES_URL, token=KISMET_TOKEN, poll_interval=2.0)

        self.cursor_image = load_and_scale_image(CURSOR_IMAGE_PATH, (64, 64), use_alpha=True)

    # ---------- Kismet controls ----------
    def start_kismet(self):
        if kismet_running():
            self.kismet.start()
            return
        start_kismet()
        self.kismet.start()

    def stop_kismet(self):
        # stop pollers first
        self.kismet.stop()
        self.kismet_probes.stop()
        if kismet_running():
            stop_kismet()

    # ---------- Main menu ----------
    def game_loop(self):
        self.background = load_and_scale_image(BACKGROUND_PATH, (self.WIDTH, self.HEIGHT), use_alpha=False)

        slimespooky = load_and_scale_font(FONT_SLIMESPOOKY, 40, self.scale_y)
        pixel       = load_and_scale_font(FONT_PIXEL,       12, self.scale_y)

        hauntware_text = slimespooky.render("HAUNTware", True, RED)
        start_game_srf = pixel.render("Start Game", True, WHITE)
        kismet_srf     = pixel.render("Kismet", True, WHITE)
        options_srf    = pixel.render("Options", True, WHITE)
        exit_srf       = pixel.render("Exit", True, WHITE)

        # (surface, base_y, label)
        texts = [
            (hauntware_text, 120, "TITLE"),
            (start_game_srf, 173, "START"),
            (kismet_srf,     198, "KISMET"),
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
                        elif label == "KISMET":
                            print("[MENU] Kismet selected → submenu")
                            # Ensure Kismet is running when entering submenu
                            self.start_kismet()
                            self.kismet_menu_screen()
                        elif label == "OPTIONS":
                            print("[MENU] Options selected")
                        elif label == "EXIT":
                            print("[MENU] Exit selected")
                            running = False
                    elif event.key == pygame.K_ESCAPE:
                        if kismet_running():
                            self.stop_kismet()
                        else:
                            running = False

            # running badge next to "Kismet"
            if kismet_running():
                kismet_surface, base_y, _ = texts[2]
                text_w, text_h = kismet_surface.get_size()
                x = (self.WIDTH - text_w) // 2
                y = int(base_y * self.scale_y)
                ui.badge_overlay = (status_font.render("[RUNNING]", True, GREEN), (x + text_w + 12, y))
            else:
                ui.badge_overlay = None

            # cursor
            focus_surface, base_y, _ = texts[menu_index]
            text_w, text_h = focus_surface.get_size()
            cursor_pos = (
                (self.WIDTH - text_w) // 2 - self.cursor_image.get_width() - 10,
                int(base_y * self.scale_y) + (text_h - self.cursor_image.get_height()) // 2
            )

            # ui expects list of (surface, base_y)
            ui.draw_menu([(t[0], t[1]) for t in texts], menu_index, cursor_pos)
            pygame.display.flip()
            clock.tick(60)

        if kismet_running():
            self.stop_kismet()
        pygame.quit()

    # ---------- Kismet submenu ----------
    def kismet_menu_screen(self):
        """Kismet → submenu with 'Live Devices' and 'Seance'."""
        bg = load_and_scale_image(BACKGROUND_PATH, (self.WIDTH, self.HEIGHT), use_alpha=False)
        ui = UI(self.screen, bg, self.cursor_image)

        title_font = load_and_scale_font(FONT_SLIMESPOOKY, 34, self.scale_y)
        pixel      = load_and_scale_font(FONT_PIXEL,       12, self.scale_y)

        title_srf   = title_font.render("Kismet", True, RED)
        live_srf    = pixel.render("Live Devices", True, WHITE)
        seance_srf  = pixel.render("Seance", True, WHITE)
        back_srf    = pixel.render("Back", True, WHITE)

        items = [
            (title_srf, 120, "TITLE"),
            (live_srf,  173, "LIVE"),
            (seance_srf,198, "SEANCE"),
            (back_srf,  223, "BACK"),
        ]
        idx = 1

        running = True
        clock = pygame.time.Clock()

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # Leaving the whole app; stop Kismet too
                    self.stop_kismet()
                    pygame.quit()
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        idx = max(1, idx - 1)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        idx = min(len(items) - 1, idx + 1)
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        label = items[idx][2]
                        if label == "LIVE":
                            # Use existing live devices screen; Kismet is already running
                            self.devices_screen()
                        elif label == "SEANCE":
                            # Start probes poller, open probes screen, stop poller when done
                            self.kismet_probes.start()
                            self.probes_screen()
                            self.kismet_probes.stop()
                        elif label == "BACK":
                            # Stop Kismet on leaving submenu (tweak if you prefer it to keep running)
                            self.stop_kismet()
                            return
                    elif event.key == pygame.K_ESCAPE:
                        # ESC acts like Back
                        self.stop_kismet()
                        return

            # cursor positioning like other screens
            focus_surface, base_y, _ = items[idx]
            text_w, text_h = focus_surface.get_size()
            cursor_pos = (
                (self.WIDTH - text_w) // 2 - self.cursor_image.get_width() - 10,
                int(base_y * self.scale_y) + (text_h - self.cursor_image.get_height()) // 2
            )

            ui.draw_menu([(t[0], t[1]) for t in items], idx, cursor_pos)
            pygame.display.flip()
            clock.tick(60)

    # ---------- Devices full-screen ----------
    def devices_screen(self):
        """Full-screen live devices view; ESC returns to Kismet submenu."""
        bg = pygame.Surface((self.WIDTH, self.HEIGHT))
        bg.fill((10, 10, 10))

        title_font = load_and_scale_font(FONT_SLIMESPOOKY, 20, self.scale_y)
        row_font   = load_and_scale_font(FONT_PIXEL,       10, self.scale_y)
        hint_font  = load_and_scale_font(FONT_PIXEL,        9, self.scale_y)

        title_surf = title_font.render("KISMET  Live Devices", True, RED)

        # scrolling state
        top_idx = 0
        running = True
        clock = pygame.time.Clock()

        # ---- layout helpers ----
        left_margin  = 20
        right_margin = 20
        col_padding  = 24

        def text_width(f, s): return f.size(s)[0]

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

        # measure fixed column widths once
        BSSID_SAMPLE  = "AA:BB:CC:DD:EE:FF"
        BSSID_COL_W   = text_width(row_font, BSSID_SAMPLE)
        SIGNAL_SAMPLE = "-100 dBm"
        SIGNAL_COL_W  = text_width(row_font, SIGNAL_SAMPLE)

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop_kismet()
                    pygame.quit()
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # Return to submenu, keep Kismet running
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
            devices, last_t = self.kismet.get_snapshot()
            age = int(time.time() - last_t) if last_t else None
            age_text = f"Updated: {age}s ago" if age is not None else "Updating…"
            self.screen.blit(hint_font.render(age_text, True, (180,180,180)), (20,54))

            # compute dynamic column positions
            signal_right_x = self.WIDTH - right_margin
            bssid_right_x  = signal_right_x - SIGNAL_COL_W - col_padding
            ssid_left_x    = left_margin
            ssid_right_x   = bssid_right_x - col_padding
            ssid_col_w     = max(50, ssid_right_x - ssid_left_x)

            # headers
            ssid_hdr = row_font.render("SSID",   True, (200,200,200))
            bssid_hdr= row_font.render("BSSID",  True, (200,200,200))
            sig_hdr  = row_font.render("SIGNAL", True, (200,200,200))

            self.screen.blit(ssid_hdr, (ssid_left_x, 80))
            self.screen.blit(bssid_hdr, (bssid_right_x - BSSID_COL_W, 80))
            self.screen.blit(sig_hdr,   (signal_right_x - text_width(row_font, "SIGNAL"), 80))

            pygame.draw.line(self.screen, (60,60,60),
                             (left_margin, 100), (self.WIDTH - right_margin, 100), 1)

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

            hint = "↑/↓ PgUp/PgDn to scroll  •  ESC to return"
            self.screen.blit(hint_font.render(hint, True, (160,160,160)),
                             (20, self.HEIGHT - 26))

            pygame.display.flip()
            clock.tick(60)

    # ---------- Seance (Probes) screen ----------
    def probes_screen(self):
        """List clients and the SSIDs they are probing for."""
        bg = pygame.Surface((self.WIDTH, self.HEIGHT))
        bg.fill((10, 10, 10))

        title_font = load_and_scale_font(FONT_SLIMESPOOKY, 20, self.scale_y)
        row_font   = load_and_scale_font(FONT_PIXEL,       10, self.scale_y)
        hint_font  = load_and_scale_font(FONT_PIXEL,        9, self.scale_y)

        title_surf = title_font.render("KISMET  Seance (Probe Requests)", True, RED)

        left_margin, right_margin, padding = 20, 20, 24
        top_idx = 0
        running = True
        clock = pygame.time.Clock()

        def ellipsize_to_width(f, s, max_px):
            w = f.size(s)[0]
            if w <= max_px: return s
            ell = "…"; ell_w = f.size(ell)[0]
            lo, hi, best = 0, len(s), ""
            while lo <= hi:
                mid = (lo + hi)//2
                cand = s[:mid]
                if f.size(cand)[0] + ell_w <= max_px:
                    best = cand; lo = mid+1
                else:
                    hi = mid-1
            return best + ell

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop_kismet()
                    pygame.quit()
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # Back to submenu (keep Kismet running)
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
            self.screen.blit(title_surf, (20, 16))

            items, last_t = self.kismet_probes.get_snapshot()
            age = int(time.time() - last_t) if last_t else None
            age_text = f"Updated: {age}s ago" if age is not None else "Updating…"
            self.screen.blit(hint_font.render(age_text, True, (180,180,180)), (20,54))

            # Columns: CLIENT (MAC) | PROBES (comma-separated)
            client_col_w = row_font.size("AA:BB:CC:DD:EE:FF")[0]
            client_left_x = left_margin
            probes_left_x = client_left_x + client_col_w + padding
            probes_right_x = self.WIDTH - right_margin
            probes_width = max(100, probes_right_x - probes_left_x)

            # Headers
            self.screen.blit(row_font.render("CLIENT", True, (200,200,200)), (client_left_x, 80))
            self.screen.blit(row_font.render("PROBES", True, (200,200,200)), (probes_left_x, 80))
            pygame.draw.line(self.screen, (60,60,60), (left_margin, 100), (self.WIDTH - right_margin, 100), 1)

            # Rows
            line_y = 110
            line_h = int(18 * self.scale_y)
            top_idx = max(0, min(top_idx, max(0, len(items)-1)))
            max_rows = (self.HEIGHT - line_y - 30) // line_h

            for item in items[top_idx: top_idx + max_rows]:
                mac = item["mac"]
                probes = ", ".join(item["ssids"])
                probes_txt = ellipsize_to_width(row_font, probes, probes_width)

                self.screen.blit(row_font.render(mac, True, WHITE), (client_left_x, line_y))
                self.screen.blit(row_font.render(probes_txt, True, WHITE), (probes_left_x, line_y))

                line_y += line_h
                if line_y > self.HEIGHT - 30: break

            hint = "↑/↓ PgUp/PgDn to scroll  •  ESC to return"
            self.screen.blit(hint_font.render(hint, True, (160,160,160)),
                             (20, self.HEIGHT - 26))

            pygame.display.flip()
            clock.tick(60)

    # ---------- In-game (unchanged) ----------
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
                    if kismet_running():
                        self.stop_kismet()
                    print("[GAME] QUIT in map -> leaving")
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if kismet_running():
                        self.stop_kismet()
                    print("[GAME] ESC in map -> return to menu")
                    running = False

            keys = pygame.key.get_pressed()
            character.move(keys)
            camera.update(character.pos)

            cursor_pos = (character.pos[0] - camera.rect.left,
                          character.pos[1] - camera.rect.top)

            ui.draw_world(character.pos, camera.rect, cursor_pos)
            clock.tick(60)

        print("[GAME] Exiting game_screen (map)")


def game_main_menu():
    Game().game_loop()
