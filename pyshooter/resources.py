import csv
import os

import pygame
from pygame import Surface
from pygame.mixer import music
from pygame.transform import scale

_ASSETS_PATH = "assets"

_SFX_CACHE = {}
_GFX_CACHE = {}
_ANIMATION_CACHE = {}


def assets_path():
    """
    Get the path for the assets directory.
    :return: The path.
    """
    if os.path.exists(_ASSETS_PATH):
        path = _ASSETS_PATH
    else:
        path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            _ASSETS_PATH
        )
    return path


def scene(level: int, ROWS: int, COLS: int):
    _data = []
    for row in range(ROWS):
        r = [-1] * COLS
        _data.append(r)

    # load in level data and create world
    path = os.path.join(assets_path(), "scenes", f'{level}.csv')

    with open(path, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for x, row in enumerate(reader):
            for y, tile in enumerate(row):
                _data[x][y] = int(tile)
    return _data


def music_play(snd, volume, loops=0, start=0.0, fade_ms=0):
    """
    Load and play a music file from the music directory.
    :param snd:
    :param volume:
    :param loops:
    :param start:
    :param fade_ms:
    """

    path = os.path.join(assets_path(), "music", snd)
    music.load(path)
    music.set_volume(volume)
    music.play(loops, start, fade_ms)


def sfx_play(snd, volume=0.0) -> None:
    sound = _sfx(snd)
    sound.set_volume(volume)
    sound.play()


def _sfx(name) -> pygame.mixer.Sound:
    """
    Load and return a sound effect from the sound directory.
    :param name:
    :return: The sound.
    """
    key = name
    if key in _SFX_CACHE:
        return _SFX_CACHE[key]

    path = os.path.join(assets_path(), "sounds", name)
    sound = pygame.mixer.Sound(path)
    _SFX_CACHE[key] = sound
    return sound


def _gfx(name, key: str, converter) -> Surface:
    """
    Load and return an image surface from the image data directory.
    :param name: image file name.
    :return: Image surface.
    """
    key = (name, key)
    if key in _GFX_CACHE:
        return _GFX_CACHE[key]

    path = os.path.join(assets_path(), name)
    img = pygame.image.load(path)
    if converter is not None:
        img = converter(img)
    _GFX_CACHE[key] = img
    return img


def gfx_alpha(name) -> Surface:
    """
    Load, convert alpha and return an image surface from the image data directory.
    :param name: image file name.
    :return: Image surface.
    """
    return _gfx(name, 'alpha', lambda surface: surface.convert_alpha())


def gfx_scaled(name, factor) -> Surface:
    """
    Load, scale and return an image surface from the image data directory.
    :param name: image file name.
    :param factor: desired size to scale the image.
    :return: Image surface.
    """
    return _gfx(name, 'scaled', lambda surface: scale(surface, factor))


def gfx_scaled_factor(name, factor) -> Surface:
    """
    Load, scale and return an image surface from the image data directory.
    :param name: image file name.
    :param factor: desired size to scale the image.
    :return: Image surface.
    """
    return _gfx(name, 'scaled',
                lambda img: scale(img, (int(img.get_width() * factor), int(img.get_height() * factor))))


def animation(name, scale: int) -> []:
    key = (name, scale)
    if key in _ANIMATION_CACHE:
        return _ANIMATION_CACHE[key]

    path = os.path.join("animations", name)
    images = []
    frames = len(os.listdir(os.path.join(assets_path(), path)))
    for i in range(frames):
        img = gfx_scaled_factor(os.path.join(path, f'{i}.png'), scale)
        images.append(img)
    _ANIMATION_CACHE[key] = images
    return images
