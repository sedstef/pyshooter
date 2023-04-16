from pygame.event import Event
from pygame.locals import (
    KEYDOWN,
    KEYUP,
    K_a,
    K_d,
    K_q,
    K_w,
    K_SPACE
)

from pyshooter.main import Player


def handle(event: Event, player: Player):
    # keyboard presses
    if event.type == KEYDOWN:
        if event.key == K_a:
            player.moving_left = True
        if event.key == K_d:
            player.moving_right = True
        if event.key == K_SPACE:
            player.shooting = True
        if event.key == K_q:
            player.grenade = True
        if event.key == K_w and player.alive:
            player.jump()

    # keyboard button released
    if event.type == KEYUP:
        if event.key == K_a:
            player.moving_left = False
        if event.key == K_d:
            player.moving_right = False
        if event.key == K_SPACE:
            player.shooting = False
        if event.key == K_q:
            player.grenade = False
            player.grenade_thrown = False
