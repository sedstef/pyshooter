import pygame

from const import GRAVITY, TILE_SIZE
from engine import images
from engine.explosion import Explosion
from engine.view import View


class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.vel_y = -11
        self.speed = 7
        self.image = images.get_grenade()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.direction = direction
        self.grenade_fx = pygame.mixer.Sound('audio/grenade.wav')
        self.grenade_fx.set_volume(0.05)

    def update(self, view: View, world):
        self.vel_y += GRAVITY
        dx = self.direction * self.speed
        dy = self.vel_y

        # check for collision with level
        for tile in world.platform:
            # check collision with walls
            if tile.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                self.direction *= -1
                dx = self.direction * self.speed
            # check for collision in the y direction
            if tile.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                self.speed = 0
                # check if below the ground, i.e. thrown up
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile.rect.bottom - self.rect.top
                # check if above the ground, i.e. falling
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    dy = tile.rect.top - self.rect.bottom

        # update grenade position
        self.rect.x += dx + view.screen_scroll
        self.rect.y += dy

        # countdown timer
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            self.grenade_fx.play()
            world.add_explosion(Explosion(self.rect.x, self.rect.y, 0.5))
            # do damage to anyone that is nearby
            if abs(self.rect.centerx - world.player.rect.centerx) < TILE_SIZE * 2 and \
                    abs(self.rect.centery - world.player.rect.centery) < TILE_SIZE * 2:
                world.player.health -= 50
            for enemy in world.enemy_group:
                if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and \
                        abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2:
                    enemy.health -= 50
