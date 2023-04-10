import random

import pygame

from engine.animations import Action
from engine.soldier import Soldier
from engine.view import View
from const import GRAVITY,SCREEN_WIDTH,SCREEN_HEIGHT,TILE_TYPES,TILE_SIZE, ROWS,COLS,MAX_LEVELS


class Enemy(Soldier):
    def __init__(self, x, y, scale, speed, ammo):
        Soldier.__init__(self, 'enemy', x, y, scale, speed, ammo)

        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 150, 20)
        self.idling = False
        self.idling_counter = 0

    def update(self, view: View,world):
        self.ai(view,world)
        super().update(view, world)

    def collision_x(self):
        # if the AI has hit a wall then make it turn around
        self.direction *= -1
        self.move_counter = 0

    def ai(self, view: View, world):
        if self.alive and world.player.alive:
            if self.idling is False and random.randint(1, 200) == 1:
                self.update_action(Action.IDLE)
                self.idling = True
                self.idling_counter = 50
            # check if the AI in near the player
            if self.vision.colliderect(world.player.rect):
                # stop running and face the player
                self.update_action(Action.IDLE)
                # shoot
                self.shoot(world)
            else:
                if self.idling is False:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(view,world,  ai_moving_left, ai_moving_right)
                    self.update_action(Action.RUN)
                    self.move_counter += 1
                    # update AI vision as the enemy moves
                    self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)

                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False

        # scroll
        self.rect.x += view.screen_scroll
