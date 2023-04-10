import pygame
from pygame.sprite import spritecollide

from engine import images
from engine.view import View


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = images.get_bullet()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self, view: View, world):
        # move bullet
        self.rect.x += (self.direction * self.speed) + view.screen_scroll
        # check if bullet has gone off screen
        if self.rect.right < 0 or self.rect.left > view.screen_width:
            self.kill()

        # check for collision with level
        if spritecollide(self, world.platform, False):
            self.kill()

        # check collision with characters
        if spritecollide(world.player, world.bullet_group, False):
            if world.player.alive:
                world.player.health -= 5
                self.kill()
        for enemy in world.enemy_group:
            if spritecollide(enemy, world.bullet_group, False):
                if enemy.alive:
                    enemy.health -= 25
                    self.kill()
