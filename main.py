import csv

import pygame
from pygame import mixer
from pygame.sprite import Group
from pygame.sprite import collide_rect

import button
from const import SCREEN_WIDTH,SCREEN_HEIGHT,TILE_TYPES,TILE_SIZE, ROWS,COLS,MAX_LEVELS
from engine.enemy import Enemy
from engine import images
from engine.background import Background
from engine.background import BG
from engine.animations import Action
from engine.screenfade import ScreenFade
from engine.view import View
from engine.tile import Tile
from engine.player import Player

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
# store tiles in a list
img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'img/Tile/{x}.png')
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)
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


class World:

    @staticmethod
    def load_world(level: int):
        # create empty tile list
        data = []
        for row in range(ROWS):
            r = [-1] * COLS
            data.append(r)

        # load in level data and create world
        with open(f'level{level}_data.csv', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for x, row in enumerate(reader):
                for y, tile in enumerate(row):
                    data[x][y] = int(tile)

        new_world = World()
        new_world.process_data(data)
        return new_world

    def __init__(self):
        self._player = None
        self._health_bar = None
        self._platform = Group()
        self._decoration_group = Group()
        self._water_group = Group()
        self._exit_group = Group()
        self._item_box_group = Group()
        self._enemy_group = Group()
        # dynamic stuff
        self._bullet_group = Group()
        self._grenade_group = Group()
        self._explosion_group = Group()

    def process_data(self, data):
        self.level_length = len(data[0])
        # iterate through each value in level data file
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile >= 0 and tile <= 8:
                        self._platform.add(Tile(img, img_rect))
                    elif tile >= 9 and tile <= 10:
                        self._water_group.add(Tile(img, img_rect))
                    elif tile >= 11 and tile <= 14:
                        self._decoration_group.add(Tile(img, img_rect))
                    elif tile == 15:  # create player
                        self._player = Player(x * TILE_SIZE, y * TILE_SIZE, 1.65, 5, 20, 5)
                        self._health_bar = HealthBar(10, 10, self.player)
                    elif tile == 16:  # create enemies
                        self._enemy_group.add(Enemy(x * TILE_SIZE, y * TILE_SIZE, 1.65, 2, 20))
                    elif tile == 17:  # create ammo box
                        self._item_box_group.add(ItemBox(img, img_rect, 'Ammo'))
                    elif tile == 18:  # create grenade box
                        self._item_box_group.add(ItemBox(img, img_rect, 'Grenade'))
                    elif tile == 19:  # create health box
                        self._item_box_group.add(ItemBox(img, img_rect, 'Health'))
                    elif tile == 20:  # create exit
                        self._exit_group.add(Tile(img, img_rect))

    @property
    def platform(self) -> Group:
        return self._platform

    @property
    def decoration_group(self) -> Group:
        return self._decoration_group

    @property
    def water_group(self) -> Group:
        return self._water_group

    @property
    def exit_group(self) -> Group:
        return self._exit_group

    @property
    def item_box_group(self) -> Group:
        return self._item_box_group

    @property
    def enemy_group(self) -> Group:
        return self._enemy_group

    @property
    def bullet_group(self) -> Group:
        return self._bullet_group

    @property
    def health_bar(self):
        return self._health_bar

    @property
    def player(self):
        return self._player

    def add_bullet(self, bullet):
        self._bullet_group.add(bullet)

    def add_grenade(self, grenade):
        self._grenade_group.add(grenade)

    def add_explosion(self, explosion):
        self._explosion_group.add(explosion)

    def update(self, view: View):
        self._platform.update(view)
        self._water_group.update(view)
        self._decoration_group.update(view)
        self._exit_group.update(view)
        self._item_box_group.update(view, self)

        self._player.update(view, self)

        self._bullet_group.update(view, self)
        self._grenade_group.update(view, self)
        self._explosion_group.update(view)

    def draw(self, screen: pygame.Surface):
        self._platform.draw(screen)
        self._water_group.draw(screen)
        self._decoration_group.draw(screen)
        self._exit_group.draw(screen)
        self._item_box_group.draw(screen)

        # TODO self._enemy_group.draw(screen)
        self._player.draw(screen)

        self._bullet_group.draw(screen)
        self._grenade_group.draw(screen)
        self._explosion_group.draw(screen)

        # show player health
        self.health_bar.draw(screen)


class ItemBox(pygame.sprite.Sprite):
    def __init__(self, img, img_rect, item_type):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = img_rect
        self.item_type = item_type

    def update(self, view: View, world: World):
        # scroll
        self.rect.x += view.screen_scroll
        player = world.player
        # check if the player has picked up the box
        if collide_rect(self, player):
            # check what kind of box it was
            if self.item_type == 'Health':
                player.health += 25
                if player.health > player.max_health:
                    player.health = player.max_health
            elif self.item_type == 'Ammo':
                player.ammo += 15
            elif self.item_type == 'Grenade':
                player.grenades = 3
            # delete the item box
            self.kill()


class HealthBar:
    def __init__(self, x, y, player: Player):
        self.x = x
        self.y = y
        self.player = player
        self.max_health = player.health

    def draw(self, screen: pygame.Surface):
        # calculate health ratio
        ratio = self.player.health / self.max_health
        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))

        # show ammo
        self.draw_text(screen, 'AMMO: ', font, WHITE, 10, 35)
        for x in range(self.player.ammo):
            screen.blit(images.get_bullet(), (90 + (x * 10), 40))

        # show grenades
        self.draw_text(screen, 'GRENADES: ', font, WHITE, 10, 60)
        for x in range(self.player.grenades):
            screen.blit(images.get_grenade(), (135 + (x * 15), 60))

    def draw_text(self, screen: pygame.Surface, text, font, text_col, x, y):
        txt_img = font.render(text, True, text_col)
        screen.blit(txt_img, (x, y))


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
