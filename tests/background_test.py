import unittest

import pygame

from pyshooter.level_scene import Background


class BackgroundTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pygame.init()
        global screen
        screen = pygame.display.set_mode((800, 600))
        screen.fill((0,0,0))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_draw(self):
        # arrange
        background = Background()

        # act
        background.draw(screen)

        #assert
        # TODO add some assertations



if __name__ == '__main__':
    unittest.main()
