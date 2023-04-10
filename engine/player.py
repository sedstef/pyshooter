from const import SCROLL_THRESH, TILE_SIZE
from engine.grenade import Grenade
from engine.soldier import Soldier
from engine.view import View


class Player(Soldier):
    def __init__(self, x, y, scale, speed, ammo, grenades):
        Soldier.__init__(self, 'player', x, y, scale, speed, ammo)
        self._grenades = grenades

    def move(self, view: View, world, moving_left, moving_right):
        dx, dy = super().move(view, world, moving_left, moving_right)

        # update scroll based on player position
        scroll = 0
        if (self.rect.right > view.screen_width - SCROLL_THRESH and view.bg_scroll < (
                world.level_length * TILE_SIZE) - view.screen_width) \
                or (self.rect.left < SCROLL_THRESH and view.bg_scroll > abs(dx)):
            self.rect.x -= dx
            scroll = -dx
        view.screen_scroll = scroll

    def create_grenade(self):
        # reduce grenades
        self._grenades -= 1

        return Grenade(self.rect.centerx + (0.5 * self.rect.size[0] * self.direction), self.rect.top, self.direction)

    @property
    def grenades(self):
        return self._grenades

    @grenades.setter
    def grenades(self, grenades: int):
        self._grenades += grenades

    @property
    def has_grenades(self):
        return self.grenades > 0
