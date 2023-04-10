import csv
import random
import string

import pygame
from pygame import mixer

import button
from engine.animations import Action
from engine.animations import ActionAnimation
from engine.explosion import Explosion
from engine.screenfade import ScreenFade
from engine.view import View
from engine.tile import Tile

mixer.init()
pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
view = View(screen)

pygame.display.set_caption('Shooter')

# set framerate
clock = pygame.time.Clock()
FPS = 60

# define game variables
GRAVITY = 0.75
SCROLL_THRESH = 200
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 21
MAX_LEVELS = 3

bg_scroll = 0
level = 1
start_game = False
start_intro = False

# define player action variables
moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False

# load music and sounds
# pygame.mixer.music.load('audio/music2.mp3')
# pygame.mixer.music.set_volume(0.3)
# pygame.mixer.music.play(-1, 0.0, 5000)
jump_fx = pygame.mixer.Sound('audio/jump.wav')
jump_fx.set_volume(0.05)
shot_fx = pygame.mixer.Sound('audio/shot.wav')
shot_fx.set_volume(0.05)
grenade_fx = pygame.mixer.Sound('audio/grenade.wav')
grenade_fx.set_volume(0.05)

# load images
# button images
start_img = pygame.image.load('img/start_btn.png').convert_alpha()
exit_img = pygame.image.load('img/exit_btn.png').convert_alpha()
restart_img = pygame.image.load('img/restart_btn.png').convert_alpha()
# background
pine1_img = pygame.image.load('img/Background/pine1.png').convert_alpha()
pine2_img = pygame.image.load('img/Background/pine2.png').convert_alpha()
mountain_img = pygame.image.load('img/Background/mountain.png').convert_alpha()
sky_img = pygame.image.load('img/Background/sky_cloud.png').convert_alpha()
# store tiles in a list
img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'img/Tile/{x}.png')
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)
# bullet
bullet_img = pygame.image.load('img/icons/bullet.png').convert_alpha()
# grenade
grenade_img = pygame.image.load('img/icons/grenade.png').convert_alpha()
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
BG = (144, 201, 120)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
PINK = (235, 65, 54)

# define font
font = pygame.font.SysFont('Futura', 30)


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def draw_bg(screen: pygame.Surface):
    screen.fill(BG)
    width = sky_img.get_width()
    for x in range(5):
        screen.blit(sky_img, ((x * width) - bg_scroll * 0.5, 0))
        screen.blit(mountain_img,
                    ((x * width) - bg_scroll * 0.6, screen.get_height() - mountain_img.get_height() - 300))
        screen.blit(pine1_img, ((x * width) - bg_scroll * 0.7, screen.get_height() - pine1_img.get_height() - 150))
        screen.blit(pine2_img, ((x * width) - bg_scroll * 0.8, screen.get_height() - pine2_img.get_height()))


# function to reset level
def reset_level():
    bullet_group.empty()
    grenade_group.empty()
    explosion_group.empty()


class Soldier(pygame.sprite.Sprite):
    def __init__(self, char_type: string, x, y, scale, speed, ammo):
        pygame.sprite.Sprite.__init__(self)
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.health = 100
        self.max_health = self.health
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False

        self.action = Action.IDLE

        # load all images for the players
        self.animation = ActionAnimation.load_animations(self.char_type, scale)
        self.image = self.animation.image(self.action)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self, view: View):
        self.check_alive()
        # update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, view: View, moving_left, moving_right):
        # reset movement variables
        dx = 0
        dy = 0

        # assign movement variables if moving left or right
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        # jump
        if self.jump is True and self.in_air is False:
            self.vel_y = -12
            self.jump = False
            self.in_air = True

        # apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y
        dy += self.vel_y

        # check for collision
        for tile in world.platform:
            # check collision in the x direction
            if tile.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
                self.collision_x()
            # check for collision in the y direction
            if tile.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                # check if below the ground, i.e. jumping
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile.rect.bottom - self.rect.top
                # check if above the ground, i.e. falling
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile.rect.top - self.rect.bottom

        # check for collision with water
        if pygame.sprite.spritecollide(self, world.water_group, False):
            self.health = 0

        # check if fallen off the map
        if self.rect.bottom > view.screen_height:
            self.health = 0

        # check if going off the edges of the screen
        if self.char_type == 'player':
            if self.rect.left + dx < 0 or self.rect.right + dx > view.screen_width:
                dx = 0

        # update rectangle position
        self.rect.x += dx
        self.rect.y += dy
        return dx, dy

    @property
    def level_complete(self):
        # check for collision with exit
        return pygame.sprite.spritecollide(self, world.exit_group, False)

    def collision_x(self):
        pass

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20
            bullet = Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), self.rect.centery,
                            self.direction)
            bullet_group.add(bullet)
            # reduce ammo
            self.ammo -= 1
            shot_fx.play()

    def update_action(self, new_action: Action):
        # check if the new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            self.animation.reset(new_action)

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.update_action(Action.DEATH)

    @property
    def alive(self) -> bool:
        return self.health > 0

    def draw(self, screen: pygame.Surface):
        image = self.animation.update_animation(self.action)
        screen.blit(pygame.transform.flip(image, self.flip, False), self.rect)


class Enemy(Soldier):
    def __init__(self, x, y, scale, speed, ammo):
        Soldier.__init__(self, 'enemy', x, y, scale, speed, ammo)

        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 150, 20)
        self.idling = False
        self.idling_counter = 0

    def update(self, view: View):
        self.ai(view)
        super().update(view)

    def collision_x(self):
        # if the AI has hit a wall then make it turn around
        self.direction *= -1
        self.move_counter = 0

    def ai(self, view: View):
        if self.alive and world.player.alive:
            if self.idling is False and random.randint(1, 200) == 1:
                self.update_action(Action.IDLE)
                self.idling = True
                self.idling_counter = 50
            # check if the AI in near the player
            if self.vision.colliderect(world.player.rect):
                # stop running and face the player
                self.update_action(Action.IDLE)
                # shoot
                self.shoot()
            else:
                if self.idling is False:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(view, ai_moving_left, ai_moving_right)
                    self.update_action(Action.RUN)
                    self.move_counter += 1
                    # update AI vision as the enemy moves
                    self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)

                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False

        # scroll
        self.rect.x += view.screen_scroll


class Player(Soldier):
    def __init__(self, x, y, scale, speed, ammo, grenades):
        Soldier.__init__(self, 'player', x, y, scale, speed, ammo)
        self.grenades = grenades

    def move(self, view: View, moving_left, moving_right):
        dx, dy = super().move(view, moving_left, moving_right)

        # update scroll based on player position
        scroll = 0
        if (self.rect.right > view.screen_width - SCROLL_THRESH and bg_scroll < (
                world.level_length * TILE_SIZE) - view.screen_width) \
                or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
            self.rect.x -= dx
            scroll = -dx

        return scroll

    def create_grenade(self):
        # reduce grenades
        self.grenades -= 1

        return Grenade(self.rect.centerx + (0.5 * self.rect.size[0] * self.direction), self.rect.top, self.direction)


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
        self._platform = pygame.sprite.Group()
        self._decoration_group = pygame.sprite.Group()
        self._water_group = pygame.sprite.Group()
        self._exit_group = pygame.sprite.Group()
        self._item_box_group = pygame.sprite.Group()
        self._enemy_group = pygame.sprite.Group()

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
                        self._platform.add(Tile(img,img_rect))
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
    def platform(self):
        return self._platform

    @property
    def decoration_group(self):
        return self._decoration_group

    @property
    def water_group(self):
        return self._water_group

    @property
    def exit_group(self):
        return self._exit_group

    @property
    def item_box_group(self):
        return self._item_box_group

    @property
    def enemy_group(self):
        return self._enemy_group

    @property
    def health_bar(self):
        return self._health_bar

    @property
    def player(self):
        return self._player

    def draw(self, screen: pygame.Surface):
        for tile in self.platform:
            tile.rect[0] += view.screen_scroll
            screen.blit(tile.image, tile.rect)

        # show player health
        self.health_bar.draw(screen)

        # show ammo
        draw_text('AMMO: ', font, WHITE, 10, 35)
        for x in range(self.player.ammo):
            screen.blit(bullet_img, (90 + (x * 10), 40))
        # show grenades
        draw_text('GRENADES: ', font, WHITE, 10, 60)
        for x in range(self.player.grenades):
            screen.blit(grenade_img, (135 + (x * 15), 60))

        self.player.update(view)
        self.player.draw(screen)


class ItemBox(pygame.sprite.Sprite):
    def __init__(self, img, img_rect, item_type):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = img_rect
        self.item_type = item_type

    def update(self, view: View):
        # scroll
        self.rect.x += view.screen_scroll
        # check if the player has picked up the box
        if pygame.sprite.collide_rect(self, world.player):
            # check what kind of box it was
            if self.item_type == 'Health':
                world.player.health += 25
                if world.player.health > world.player.max_health:
                    world.player.health = world.player.max_health
            elif self.item_type == 'Ammo':
                world.player.ammo += 15
            elif self.item_type == 'Grenade':
                world.player.grenades += 3
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


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self, view: View):
        # move bullet
        self.rect.x += (self.direction * self.speed) + view.screen_scroll
        # check if bullet has gone off screen
        if self.rect.right < 0 or self.rect.left > view.screen_width:
            self.kill()

        # check for collision with level
        if pygame.sprite.spritecollide(self, world.platform, False):
            self.kill()

        # check collision with characters
        if pygame.sprite.spritecollide(world.player, bullet_group, False):
            if world.player.alive:
                world.player.health -= 5
                self.kill()
        for enemy in world.enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    enemy.health -= 25
                    self.kill()


class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.vel_y = -11
        self.speed = 7
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.direction = direction

    def update(self, view: View):
        self.vel_y += GRAVITY
        dx = self.direction * self.speed
        dy = self.vel_y

        # check for collision with level
        for tile in world.platform:
            # check collision with walls
            if tile.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                self.direction *= -1
                dx = self.direction * self.speed
            # check for collision in the y direction
            if tile.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                self.speed = 0
                # check if below the ground, i.e. thrown up
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile.rect.bottom - self.rect.top
                # check if above the ground, i.e. falling
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    dy = tile.rect.top - self.rect.bottom

        # update grenade position
        self.rect.x += dx + view.screen_scroll
        self.rect.y += dy

        # countdown timer
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            grenade_fx.play()
            explosion_group.add(Explosion(self.rect.x, self.rect.y, 0.5))
            # do damage to anyone that is nearby
            if abs(self.rect.centerx - world.player.rect.centerx) < TILE_SIZE * 2 and \
                    abs(self.rect.centery - world.player.rect.centery) < TILE_SIZE * 2:
                world.player.health -= 50
            for enemy in world.enemy_group:
                if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and \
                        abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2:
                    enemy.health -= 50


# create screen fades
intro_fade = ScreenFade(1, BLACK, 4)
death_fade = ScreenFade(2, PINK, 4)

# create buttons
start_button = button.Button(view.screen_width // 2 - 130, view.screen_height // 2 - 150, start_img, 1)
exit_button = button.Button(view.screen_width // 2 - 110, view.screen_height // 2 + 50, exit_img, 1)
restart_button = button.Button(view.screen_width // 2 - 100, view.screen_height // 2 - 50, restart_img, 2)

# create sprite groups
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()

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
            start_intro = True
        if exit_button.draw(screen):
            run = False
    else:
        # update background
        draw_bg(screen)
        # draw world map
        world.draw(screen)

        for enemy in world.enemy_group:
            enemy.update(view)
            enemy.draw(screen)

        bullet_group.update(view)
        grenade_group.update(view)
        explosion_group.update(view)
        world.item_box_group.update(view)
        world.decoration_group.update(view)
        world.water_group.update(view)
        world.exit_group.update(view)

        bullet_group.draw(screen)
        grenade_group.draw(screen)
        explosion_group.draw(screen)
        world.item_box_group.draw(screen)
        world.decoration_group.draw(screen)
        world.water_group.draw(screen)
        world.exit_group.draw(screen)

        # show intro
        if start_intro is True:
            if intro_fade.fade(screen):
                start_intro = False
                intro_fade.fade_counter = 0

        # update player actions
        if world.player.alive:
            # shoot bullets
            if shoot:
                world.player.shoot()
            # throw grenades
            elif grenade and grenade_thrown is False and world.player.grenades > 0:
                new_grenade = world.player.create_grenade()
                grenade_group.add(new_grenade)
                grenade_thrown = True
            if world.player.in_air:
                world.player.update_action(Action.JUMP)
            elif moving_left or moving_right:
                world.player.update_action(Action.RUN)
            else:
                world.player.update_action(Action.IDLE)
            view.screen_scroll = world.player.move(view, moving_left, moving_right)
            bg_scroll -= view.screen_scroll
            # check if player has completed the level
            if world.player.level_complete:
                start_intro = True
                level += 1
                bg_scroll = 0
                reset_level()
                if level <= MAX_LEVELS:
                    world = World.load_world(level)
        else:
            view.screen_scroll = 0
            if death_fade.fade(screen):
                if restart_button.draw(screen):
                    death_fade.fade_counter = 0
                    start_intro = True
                    bg_scroll = 0
                    reset_level()
                    world = World.load_world(level)

    for event in pygame.event.get():
        # quit game
        if event.type == pygame.QUIT:
            run = False
        # keyboard presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_SPACE:
                shoot = True
            if event.key == pygame.K_q:
                grenade = True
            if event.key == pygame.K_w and world.player.alive:
                world.player.jump = True
                jump_fx.play()
            if event.key == pygame.K_ESCAPE:
                run = False

        # keyboard button released
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_SPACE:
                shoot = False
            if event.key == pygame.K_q:
                grenade = False
                grenade_thrown = False

    pygame.display.update()

pygame.quit()
