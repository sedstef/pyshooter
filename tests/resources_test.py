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

    def test_bullet_loadable(self):
        bullet = resources.gfx_alpha('icons/bullet.png')
        self.assertTrue(bullet)

    def test_grenade_loadable(self):
        grenade = resources.gfx_alpha('icons/grenade.png')
        self.assertTrue(grenade)

    def test_tile_loadable(self):
        tile = resources.gfx_scaled(f'tile/0.png', (10, 10))
        self.assertTrue(tile)


if __name__ == '__main__':
    unittest.main()
