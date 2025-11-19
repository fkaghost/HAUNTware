import pygame

def load_and_scale_image(path, size=None, use_alpha=False):
    """Load an image from path and scale it."""
    surf = pygame.image.load(str(path))
    surf = surf.convert_alpha() if use_alpha else surf.convert()
    if size:
        surf = pygame.transform.smoothscale(surf, size)
    return surf

def load_and_scale_font(path, base_size, scale_y):
    """Scale font size relative to vertical scale."""
    scaled_size = int(base_size * scale_y)
    return pygame.font.Font(str(path), scaled_size)