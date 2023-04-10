from pygame.image import load
from pygame.transform import scale

from const import TILE_SIZE, TILE_TYPES

# store tiles in a list
img_list = []
for x in range(TILE_TYPES):
    img = load(f'img/Tile/{x}.png')
    img = scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)


def get_tiles(tile):
    return img_list[tile]


def get_bullet():
    return load('img/icons/bullet.png').convert_alpha()


def get_grenade():
    return load('img/icons/grenade.png').convert_alpha()
