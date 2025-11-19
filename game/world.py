import pygame
from config import WIDTH, HEIGHT, MAP_IMAGE_PATH
from .assets import load_and_scale_image, load_and_scale_font


class Character:
    def __init__(self, pos):
        self.pos = pos
        self.speed = 3

    def move(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.pos[0] -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.pos[0] += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.pos[1] -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.pos[1] += self.speed


class Camera:
    def __init__(self, rect, world_w, world_h):
        self.rect = rect
        self.world_w = world_w
        self.world_h = world_h

    def update(self, pos):
        half_w = self.rect.width // 2
        half_h = self.rect.height // 2
        self.rect.centerx = max(half_w, min(pos[0], self.world_w - half_w))
        self.rect.centery = max(half_h, min(pos[1], self.world_h - half_h))


def game_screen(screen, scale_y):
    print("[GAME] Entering real game world")

    world_w, world_h = 1500, 1000
    background = load_and_scale_image(MAP_IMAGE_PATH, (world_w, world_h))

    character = Character([WIDTH // 2, HEIGHT // 2])
    camera = Camera(pygame.Rect(0, 0, WIDTH, HEIGHT), world_w, world_h)

    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                print("[GAME] ESC -> Return to menu")
                return

        keys = pygame.key.get_pressed()
        character.move(keys)
        camera.update(character.pos)

        # Draw map + character ghost cursor overlay
        screen.blit(background, (0, 0), camera.rect)

        cursor_x = character.pos[0] - camera.rect.left
        cursor_y = character.pos[1] - camera.rect.top
        pygame.draw.rect(screen, (200, 80, 80),
                         (cursor_x - 8, cursor_y - 8, 16, 16))

        pygame.display.flip()
        clock.tick(60)

    print("[GAME] Exiting game world")
