import pygame
import time
from bettercap.client import BettercapClient
from game.assets import load_and_scale_font, load_and_scale_image
from config import WIDTH, HEIGHT, RED, WHITE, SCALE_Y, BACKGROUND_PATH, CURSOR_IMAGE_PATH, FONT_PIXEL, FONT_SLIMESPOOKY

class BettercapProbesScreen:
    def __init__(self, screen):
        self.screen = screen
        self.bg = load_and_scale_image(BACKGROUND_PATH, (WIDTH, HEIGHT))
        self.cursor = load_and_scale_image(CURSOR_IMAGE_PATH, (64, 64), True)

        self.client = BettercapClient()
        self.client.start()

        self.title = load_and_scale_font(FONT_SLIMESPOOKY, 20, SCALE_Y)
        self.row_font = load_and_scale_font(FONT_PIXEL, 10, SCALE_Y)

    def run(self):
        running = True
        clock = pygame.time.Clock()

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.client.stop()
                    return
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.client.stop()
                    return

            self.draw()
            pygame.display.flip()
            clock.tick(60)

    def draw(self):
        self.screen.blit(self.bg, (0, 0))

        title = self.title.render("Bettercap – Probe Requests", True, RED)
        self.screen.blit(title, (20, 20))

        probes, last_t = self.client.get_snapshot()
        y = 90

        for p in probes[:20]:
            line = f"{p['station']} → {p['ssid']}"
            self.screen.blit(self.row_font.render(line, True, WHITE), (20, y))
            y += 20
