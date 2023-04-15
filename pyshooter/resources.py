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


def sfx(snd, volume=0.0) -> pygame.mixer.Sound:
    """
    Load and return a sound effect from the sound directory.
    :param snd:
    :param volume:
    :return: The sound.
    """
    sfx_key = snd
    if sfx_key in _SFX_CACHE:
        asound = _SFX_CACHE[sfx_key]
    else:
        path = os.path.join(assets_path(), "sounds", snd)
        asound = pygame.mixer.Sound(path)
        _SFX_CACHE[sfx_key] = asound

    if volume:
        asound.set_volume(volume)
    return asound


def _gfx(image, key: str, converter) -> Surface:
    """
    Load and return an image surface from the image data directory.
    :param image: image file name.
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
    animation_key = (name, scale)
    if animation_key in _ANIMATION_CACHE:
        return _ANIMATION_CACHE[animation_key]

    path = os.path.join("animations", name)
    images = []
    frames = len(os.listdir(os.path.join(assets_path(), path)))
    for i in range(frames):
        img = gfx_scaled_factor(os.path.join(path, f'{i}.png'), scale)
        images.append(img)
    _ANIMATION_CACHE[animation_key] = images
    return images
