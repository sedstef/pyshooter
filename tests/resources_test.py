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
        resources.sfx_play('grenade.wav',0.5)

    def test_animation_loaded_twice(self):
        # arrange + act
        result = resources.animation('explosion',0.5)

        # assert
        expected = resources.animation('explosion', 0.5)
        self.assertListEqual(result, expected)

    def test_scene_loadable(self):
        scene = resources.scene(1, 16, 180)
        self.assertTrue(scene)

if __name__ == '__main__':
    unittest.main()
