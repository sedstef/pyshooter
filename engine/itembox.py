import pygame
from pygame.sprite import collide_rect

from engine.view import View


class ItemBox(pygame.sprite.Sprite):
    def __init__(self, img, img_rect, item_type):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = img_rect
        self.item_type = item_type

    def update(self, view: View, world):
        # scroll
        self.rect.x += view.screen_scroll
        player = world.player
        # check if the player has picked up the box
        if collide_rect(self, player):
            # check what kind of box it was
            if self.item_type == 'Health':
                player.health += 25
                if player.health > player.max_health:
                    player.health = player.max_health
            elif self.item_type == 'Ammo':
                player.ammo += 15
            elif self.item_type == 'Grenade':
                player.grenades = 3
            # delete the item box
            self.kill()
