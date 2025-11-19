import pygame

class UI:
    def __init__(self, screen, background, cursor_image):
        self.screen = screen
        self.background = background
        self.cursor_image = cursor_image
        self.badge_overlay = None

    def draw_menu(self, texts, selected_index, cursor_pos):
        self.screen.blit(self.background, (0, 0))

        for i, (surface, base_y) in enumerate(texts):
            text_w, text_h = surface.get_size()
            x = (self.screen.get_width() - text_w) // 2
            y = int(base_y * (self.screen.get_height() / 320))

            if i == selected_index:
                padding = int(6 * (self.screen.get_height() / 320))
                rect = pygame.Rect(
                    x - padding, y - padding,
                    text_w + padding * 2, text_h + padding * 2
                )
                pygame.draw.rect(self.screen, (40, 40, 40), rect, border_radius=6)

            self.screen.blit(surface, (x, y))

        self.screen.blit(self.cursor_image, cursor_pos)

        if self.badge_overlay:
            badge_surf, badge_pos = self.badge_overlay
            self.screen.blit(badge_surf, badge_pos)

    def draw_world(self, character_pos, camera_rect, cursor_pos):
        self.screen.blit(self.background, (0, 0), camera_rect)
        self.screen.blit(self.cursor_image, cursor_pos)
        pygame.display.flip()  # <-- add this line
