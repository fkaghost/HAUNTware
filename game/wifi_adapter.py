import pygame
import subprocess
from game.assets import load_and_scale_font, load_and_scale_image
from config import WIDTH, HEIGHT, SCALE_Y, FONT_PIXEL, RED, WHITE, BACKGROUND_PATH, CURSOR_IMAGE_PATH

class WifiAdapterScreen:
    def __init__(self, screen):
        self.screen = screen
        self.bg = load_and_scale_image(BACKGROUND_PATH, (WIDTH, HEIGHT))
        self.cursor = load_and_scale_image(CURSOR_IMAGE_PATH, (64, 64), use_alpha=True)

        self.pixel = load_and_scale_font(FONT_PIXEL, 12, SCALE_Y)

        self.items = [
            ("Set wlan1 → Monitor Mode", "MONITOR"),
            ("Set wlan1 → Managed Mode", "MANAGED"),
            ("Back", "BACK")
        ]

        self.index = 0

    def run(self):
        running = True
        clock = pygame.time.Clock()

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        self.index = max(0, self.index - 1)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self.index = min(len(self.items) - 1, self.index + 1)
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        label = self.items[self.index][1]
                        if label == "MONITOR":
                            subprocess.call(["bash", "scripts/set_monitor_wlan1.sh"])
                        elif label == "MANAGED":
                            subprocess.call(["bash", "scripts/set_managed_wlan1.sh"])
                        elif label == "BACK":
                            return
                    elif event.key == pygame.K_ESCAPE:
                        return

            self.draw()
            pygame.display.flip()
            clock.tick(60)

    def draw(self):
        self.screen.blit(self.bg, (0, 0))

        y = 150
        for i, (text, _) in enumerate(self.items):
            surf = self.pixel.render(text, True, WHITE)
            x = (WIDTH - surf.get_width()) // 2
            self.screen.blit(surf, (x, y))

            if i == self.index:
                self.screen.blit(self.cursor, (x - 50, y))

            y += 40
