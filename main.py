import pygame
from pygame import mixer

import button
from const import SCREEN_WIDTH,SCREEN_HEIGHT,TILE_TYPES,TILE_SIZE, MAX_LEVELS
from engine.background import Background
from engine.background import BG
from engine.animations import Action
from engine.screenfade import ScreenFade
from engine.view import View
from engine.world import World

mixer.init()
pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
view = View(screen)

pygame.display.set_caption('Shooter')

# set framerate
clock = pygame.time.Clock()
FPS = 60

# define game variables

level = 1
start_game = False

# define player action variables
moving_left = False
moving_right = False

# load music and sounds
# pygame.mixer.music.load('audio/music2.mp3')
# pygame.mixer.music.set_volume(0.3)
# pygame.mixer.music.play(-1, 0.0, 5000)
jump_fx = pygame.mixer.Sound('audio/jump.wav')
jump_fx.set_volume(0.05)

# load images
# button images
start_img = pygame.image.load('img/start_btn.png').convert_alpha()
exit_img = pygame.image.load('img/exit_btn.png').convert_alpha()
restart_img = pygame.image.load('img/restart_btn.png').convert_alpha()

# bullet

# grenade

# pick up boxes
health_box_img = pygame.image.load('img/icons/health_box.png').convert_alpha()
ammo_box_img = pygame.image.load('img/icons/ammo_box.png').convert_alpha()
grenade_box_img = pygame.image.load('img/icons/grenade_box.png').convert_alpha()
item_boxes = {
    'Health': health_box_img,
    'Ammo': ammo_box_img,
    'Grenade': grenade_box_img
}

# define colours
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
PINK = (235, 65, 54)

# define font
font = pygame.font.SysFont('Futura', 30)


# create screen fades
def create_intro_fade():
    return ScreenFade(1, BLACK, 4)

death_fade = ScreenFade(2, PINK, 4)

# create buttons
start_button = button.Button(view.screen_width // 2 - 130, view.screen_height // 2 - 150, start_img, 1)
exit_button = button.Button(view.screen_width // 2 - 110, view.screen_height // 2 + 50, exit_img, 1)
restart_button = button.Button(view.screen_width // 2 - 100, view.screen_height // 2 - 50, restart_img, 2)

background = Background()
world = World.load_world(level)

run = True
while run:

    clock.tick(FPS)

    if start_game is False:
        # draw menu
        screen.fill(BG)
        # add buttons
        if start_button.draw(screen):
            start_game = True
            intro_fade = create_intro_fade()
        if exit_button.draw(screen):
            run = False
    else:
        # update and draw background
        background.draw(screen, view)

        for enemy in world.enemy_group:
            enemy.update(view,world)
            enemy.draw(screen)

        world.update(view)

        # draw world map
        world.draw(screen)

        # show intro
        if intro_fade is not None:
            if intro_fade.fade(screen):
                intro_fade = None

        # update player actions
        if world.player.alive:
            if world.player.in_air:
                world.player.update_action(Action.JUMP)
            elif moving_left or moving_right:
                world.player.update_action(Action.RUN)
            else:
                world.player.update_action(Action.IDLE)
            world.player.move(view, world, moving_left, moving_right)
            view.bg_scroll -= view.screen_scroll

            # check if player has completed the level
            if world.player.level_complete(world):
                intro_fade = create_intro_fade()
                level += 1
                view.bg_scroll = 0
                if level <= MAX_LEVELS:
                    world = World.load_world(level)
        else:
            view.screen_scroll = 0
            if death_fade.fade(screen):
                if restart_button.draw(screen):
                    death_fade.fade_counter = 0
                    intro_fade = create_intro_fade()
                    view.bg_scroll = 0
                    world = World.load_world(level)

    for event in pygame.event.get():
        # quit game
        if event.type == pygame.QUIT or \
                (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            run = False
        elif world.player.alive:
            # keyboard presses
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    moving_left = True
                if event.key == pygame.K_d:
                    moving_right = True
                if event.key == pygame.K_SPACE:
                    # shoot bullets
                    world.player.shoot(world)
                if event.key == pygame.K_q and world.player.has_grenades:
                    # throw grenades
                    new_grenade = world.player.create_grenade()
                    world.add_grenade(new_grenade)
                if event.key == pygame.K_w and world.player.alive:
                    world.player.jump = True
                    jump_fx.play()

            # keyboard button released
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    moving_left = False
                if event.key == pygame.K_d:
                    moving_right = False

    pygame.display.update()

pygame.quit()
