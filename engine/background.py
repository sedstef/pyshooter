import pygame

from engine.view import View

BG = (144, 201, 120)


class Background:

    def __init__(self) -> None:
        self._sky = pygame.image.load('img/background/sky_cloud.png').convert_alpha()
        self._mountain = pygame.image.load('img/background/mountain.png').convert_alpha()
        self._pine1 = pygame.image.load('img/background/pine1.png').convert_alpha()
        self._pine2 = pygame.image.load('img/background/pine2.png').convert_alpha()

    def draw(self, screen: pygame.Surface, view: View):
        screen.fill(BG)
        width = self._sky.get_width()
        for x in range(5):
            screen.blit(self._sky, ((x * width) - view.bg_scroll * 0.5, 0))
            screen.blit(self._mountain, (
                (x * width) - view.bg_scroll * 0.6, view.screen_height - self._mountain.get_height() - 300))
            screen.blit(self._pine1,
                        ((x * width) - view.bg_scroll * 0.7, view.screen_height - self._pine1.get_height() - 150))
            screen.blit(self._pine2,
                        ((x * width) - view.bg_scroll * 0.8, view.screen_height - self._pine2.get_height()))
