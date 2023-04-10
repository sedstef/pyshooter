import csv

import pygame
from pygame.sprite import Group

from const import ROWS, COLS, TILE_SIZE
from engine import images
from engine.enemy import Enemy
from engine.healthbar import HealthBar
from engine.itembox import ItemBox
from engine.player import Player
from engine.tile import Tile
from engine.view import View


class World:

    @staticmethod
    def load_world(level: int):
        # create empty tile list
        data = []
        for row in range(ROWS):
            r = [-1] * COLS
            data.append(r)

        # load in level data and create world
        with open(f'level{level}_data.csv', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for x, row in enumerate(reader):
                for y, tile in enumerate(row):
                    data[x][y] = int(tile)

        new_world = World()
        new_world.process_data(data)
        return new_world

    def __init__(self):
        self._player = None
        self._health_bar = None
        self._platform = Group()
        self._decoration_group = Group()
        self._water_group = Group()
        self._exit_group = Group()
        self._item_box_group = Group()
        self._enemy_group = Group()
        # dynamic stuff
        self._bullet_group = Group()
        self._grenade_group = Group()
        self._explosion_group = Group()

    def process_data(self, data):
        self.level_length = len(data[0])
        # iterate through each value in level data file
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = images.get_tiles(tile)
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    if tile >= 0 and tile <= 8:
                        self._platform.add(Tile(img, img_rect))
                    elif tile >= 9 and tile <= 10:
                        self._water_group.add(Tile(img, img_rect))
                    elif tile >= 11 and tile <= 14:
                        self._decoration_group.add(Tile(img, img_rect))
                    elif tile == 15:  # create player
                        self._player = Player(x * TILE_SIZE, y * TILE_SIZE, 1.65, 5, 20, 5)
                        self._health_bar = HealthBar(10, 10, self.player)
                    elif tile == 16:  # create enemies
                        self._enemy_group.add(Enemy(x * TILE_SIZE, y * TILE_SIZE, 1.65, 2, 20))
                    elif tile == 17:  # create ammo box
                        self._item_box_group.add(ItemBox(img, img_rect, 'Ammo'))
                    elif tile == 18:  # create grenade box
                        self._item_box_group.add(ItemBox(img, img_rect, 'Grenade'))
                    elif tile == 19:  # create health box
                        self._item_box_group.add(ItemBox(img, img_rect, 'Health'))
                    elif tile == 20:  # create exit
                        self._exit_group.add(Tile(img, img_rect))

    @property
    def platform(self) -> Group:
        return self._platform

    @property
    def decoration_group(self) -> Group:
        return self._decoration_group

    @property
    def water_group(self) -> Group:
        return self._water_group

    @property
    def exit_group(self) -> Group:
        return self._exit_group

    @property
    def item_box_group(self) -> Group:
        return self._item_box_group

    @property
    def enemy_group(self) -> Group:
        return self._enemy_group

    @property
    def bullet_group(self) -> Group:
        return self._bullet_group

    @property
    def health_bar(self):
        return self._health_bar

    @property
    def player(self):
        return self._player

    def add_bullet(self, bullet):
        self._bullet_group.add(bullet)

    def add_grenade(self, grenade):
        self._grenade_group.add(grenade)

    def add_explosion(self, explosion):
        self._explosion_group.add(explosion)

    def update(self, view: View):
        self._platform.update(view)
        self._water_group.update(view)
        self._decoration_group.update(view)
        self._exit_group.update(view)
        self._item_box_group.update(view, self)

        self._player.update(view, self)

        self._bullet_group.update(view, self)
        self._grenade_group.update(view, self)
        self._explosion_group.update(view)

    def draw(self, screen: pygame.Surface):
        self._platform.draw(screen)
        self._water_group.draw(screen)
        self._decoration_group.draw(screen)
        self._exit_group.draw(screen)
        self._item_box_group.draw(screen)

        # TODO self._enemy_group.draw(screen)
        self._player.draw(screen)

        self._bullet_group.draw(screen)
        self._grenade_group.draw(screen)
        self._explosion_group.draw(screen)

        # show player health
        self.health_bar.draw(screen)
