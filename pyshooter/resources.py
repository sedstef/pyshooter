import os

import pygame

_SFX_CACHE = {}
_GFX_CACHE = {}


def assets_path():
    """
    Get the path for the data directory.
    :return: The path.
    """
    if os.path.exists("assets"):
        path = "assets"
    else:
        path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "assets",
        )
    return path


def gfx(image, convert=False, convert_alpha=False):
    """
    Load and return an image surface from the image data directory.
    :param image: image file name.
    :param convert:
    :param convert_alpha:
    :return: Image surface.
    """
    gfx_key = (image, convert, convert_alpha)
    if gfx_key in _GFX_CACHE:
        return _GFX_CACHE[gfx_key]

    path = os.path.join(assets_path(), image)
    img = pygame.image.load(path)
    if convert:
        img = img.convert()
    if convert_alpha:
        img = img.convert_alpha()
    _GFX_CACHE[gfx_key] = img
    return img
