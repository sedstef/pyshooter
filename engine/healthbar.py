import pygame
from pygame.sysfont import SysFont

from engine import images
from engine.player import Player

RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
PINK = (235, 65, 54)


class HealthBar:
    def __init__(self, x, y, player: Player):
        self.x = x
        self.y = y
        self.player = player
        self.max_health = player.health
        self.font = SysFont('Futura', 30)

    def draw(self, screen: pygame.Surface):
        # calculate health ratio
        ratio = self.player.health / self.max_health
        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))

        # show ammo
        self.draw_text(screen, 'AMMO: ', self.font, WHITE, 10, 35)
        for x in range(self.player.ammo):
            screen.blit(images.get_bullet(), (90 + (x * 10), 40))

        # show grenades
        self.draw_text(screen, 'GRENADES: ', self.font, WHITE, 10, 60)
        for x in range(self.player.grenades):
            screen.blit(images.get_grenade(), (135 + (x * 15), 60))

    @staticmethod
    def draw_text(screen: pygame.Surface, text, font, text_col, x, y):
        txt_img = font.render(text, True, text_col)
        screen.blit(txt_img, (x, y))
