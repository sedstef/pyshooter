import pygame


class View:

    def __init__(self, screen: pygame.Surface):
        self._screen = screen
        self._screen_scroll = 0
        self._bg_scroll = 0

    @property
    def screen_width(self):
        return self._screen.get_width()

    @property
    def screen_height(self):
        return self._screen.get_height()

    @property
    def screen_scroll(self):
        return self._screen_scroll

    @screen_scroll.setter
    def screen_scroll(self, screen_scroll: int):
        self._screen_scroll = screen_scroll

    @property
    def bg_scroll(self):
        return self._bg_scroll

    @bg_scroll.setter
    def bg_scroll(self, bg_scroll: int):
        self._bg_scroll = bg_scroll
