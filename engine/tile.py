import pygame

from engine.view import View


class Tile(pygame.sprite.Sprite):
    def __init__(self, image, rect):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = rect

    def update(self, view: View):
        self.rect.x += view.screen_scroll
