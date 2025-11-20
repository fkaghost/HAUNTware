# game/menu.py
import pygame

from game.assets import load_and_scale_font, load_and_scale_image
from game.ui import UI
from game.world import Character, Camera

# --- HAUNTware config ---
from config import (
    BASE_WIDTH, BASE_HEIGHT,
    RED, WHITE,
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
        self.WIDTH = info.current_w
        self.HEIGHT = info.current_h
        self.scale_x = self.WIDTH / BASE_WIDTH
        self.scale_y = self.HEIGHT / BASE_HEIGHT

        self.screen = pygame.display.set_mode(
            (self.WIDTH, self.HEIGHT),
            pygame.FULLSCREEN | pygame.NOFRAME
        )
        pygame.mouse.set_visible(False)

        # ---- Cursor image ----
        self.cursor_image = load_and_scale_image(CURSOR_IMAGE_PATH, (64, 64), use_alpha=True)

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
        start_srf = pixel.render("Start Game", True, WHITE)
        exit_srf = pixel.render("Exit", True, WHITE)

        # (surface, base_y, label)
        texts = [
            (hauntware_srf, 140, "TITLE"),
            (start_srf, 200, "START"),
            (exit_srf, 240, "EXIT"),
        ]

        menu_index = 1
        ui = UI(self.screen, self.background, self.cursor_image)

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

                        elif label == "EXIT":
                            running = False

                    elif event.key == pygame.K_ESCAPE:
                        running = False

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

        pygame.quit()

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
