import string

import pygame
from pygame.sprite import spritecollide

from const import GRAVITY
from engine.animations import Action, ActionAnimation
from engine.bullet import Bullet
from engine.view import View


class Soldier(pygame.sprite.Sprite):
    def __init__(self, char_type: string, x, y, scale, speed, ammo):
        pygame.sprite.Sprite.__init__(self)
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.health = 100
        self.max_health = self.health
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False

        self.action = Action.IDLE

        # load all images for the players
        self.animation = ActionAnimation.load_animations(self.char_type, scale)
        self.image = self.animation.image(self.action)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

        self.shot_fx = pygame.mixer.Sound('audio/shot.wav')
        self.shot_fx.set_volume(0.05)

    def update(self, view: View, world):
        self.check_alive()
        # update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, view: View, world, moving_left, moving_right):
        # reset movement variables
        dx = 0
        dy = 0

        # assign movement variables if moving left or right
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        # jump
        if self.jump is True and self.in_air is False:
            self.vel_y = -12
            self.jump = False
            self.in_air = True

        # apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y
        dy += self.vel_y

        # check for collision
        for tile in world.platform:
            # check collision in the x direction
            if tile.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
                self.collision_x()
            # check for collision in the y direction
            if tile.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                # check if below the ground, i.e. jumping
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile.rect.bottom - self.rect.top
                # check if above the ground, i.e. falling
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile.rect.top - self.rect.bottom

        # check for collision with water
        if spritecollide(self, world.water_group, False):
            self.health = 0

        # check if fallen off the map
        if self.rect.bottom > view.screen_height:
            self.health = 0

        # check if going off the edges of the screen
        if self.char_type == 'player':
            if self.rect.left + dx < 0 or self.rect.right + dx > view.screen_width:
                dx = 0

        # update rectangle position
        self.rect.x += dx
        self.rect.y += dy
        return dx, dy

    def level_complete(self, world):
        # check for collision with exit
        return spritecollide(self, world.exit_group, False)

    def collision_x(self):
        pass

    def shoot(self, world):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20
            bullet = Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), self.rect.centery,
                            self.direction)
            world.add_bullet(bullet)
            # reduce ammo
            self.ammo -= 1
            self.shot_fx.play()

    def update_action(self, new_action: Action):
        # check if the new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            self.animation.reset(new_action)

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.update_action(Action.DEATH)

    @property
    def alive(self) -> bool:
        return self.health > 0

    def draw(self, screen: pygame.Surface):
        image = self.animation.update_animation(self.action)
        screen.blit(pygame.transform.flip(image, self.flip, False), self.rect)
