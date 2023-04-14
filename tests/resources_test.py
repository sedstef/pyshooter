import unittest

from pyshooter import resources


class ResourcesTest(unittest.TestCase):
    def test_bullet_loadable(self):
        bullet = resources.gfx('icons/bullet.png')
        self.assertTrue(bullet)

    def test_grenade_loadable(self):
        grenade = resources.gfx('icons/grenade.png')
        self.assertTrue(grenade)


if __name__ == '__main__':
    unittest.main()
