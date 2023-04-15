import unittest

import pygame

from pyshooter import resources


class ResourcesTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        screen.fill((0,0,0))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_bullet_gfx_loadable(self):
        gfx = resources.gfx_alpha('icons/bullet.png')
        self.assertTrue(gfx)

    def test_grenade_gfx_loadable(self):
        gfx = resources.gfx_alpha('icons/grenade.png')
        self.assertTrue(gfx)

    def test_tile_gfx_loadable(self):
        gfx = resources.gfx_scaled(f'tile/0.png', (10, 10))
        self.assertTrue(gfx)

    def test_grenada_sfx_loadable(self):
        sfx = resources.sfx('grenade.wav',0.5)
        self.assertTrue(sfx)


if __name__ == '__main__':
    unittest.main()
