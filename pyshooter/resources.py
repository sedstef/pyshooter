import os

import pygame
from pygame.transform import scale

_ASSETS_PATH = "assets"

_SFX_CACHE = {}
_GFX_CACHE = {}


def assets_path():
    """
    Get the path for the data directory.
    :return: The path.
    """
    if os.path.exists(_ASSETS_PATH):
        path = _ASSETS_PATH
    else:
        path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            _ASSETS_PATH,
        )
    return path


def gfx_alpha(image):
    return _gfx(image, 'alpha', lambda surface: surface.convert_alpha())


def gfx_scaled(image, size):
    return _gfx(image, 'scaled', lambda surface: scale(surface, size))


def _gfx(image, key: str, converter):
    """
    Load and return an image surface from the image data directory.
    :param image: image file name.
    :param convert:
    :param convert_alpha:
    :return: Image surface.
    """
    gfx_key = (image, key)
    if gfx_key in _GFX_CACHE:
        return _GFX_CACHE[gfx_key]

    path = os.path.join(assets_path(), image)
    img = pygame.image.load(path)
    if converter is not None:
        img = converter(img)
    _GFX_CACHE[gfx_key] = img
    return img
