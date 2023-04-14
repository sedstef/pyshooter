import csv
import os
import random

import pygame
from pygame import mixer, Surface, Rect
from pygame.image import load
from pygame.mixer import Sound, music
from pygame.sprite import Sprite

from pyshooter import resources

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

# set framerate
FPS = 60

# define game variables
GRAVITY = 0.75
SCROLL_THRESH = 200
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 21
MAX_LEVELS = 3

# define colours
BG = (144, 201, 120)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
PINK = (235, 65, 54)


class Assets:

    @staticmethod
    def load_animation_soldier(char_type: str, scale: int) -> []:
        animation_list = []

        # load all images for the players
        animation_types = ['Idle', 'Run', 'Jump', 'Death']
        for animation in animation_types:
            # reset temporary list of images
            temp_list = []
            # count number of files in the folder
            num_of_frames = len(os.listdir(f'img/{char_type}/{animation}'))
            for i in range(num_of_frames):
                img = Assets.load_image_alpha(f'img/{char_type}/{animation}/{i}.png')
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            animation_list.append(temp_list)
        return animation_list

    @staticmethod
    def load_animation_explosions(scale: int) -> []:
        images = []
        for num in range(1, 6):
            img = Assets.load_image_alpha(f'img/explosion/exp{num}.png')
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            images.append(img)
        return images

    @staticmethod
    def load_image_alpha(name: str) -> Surface:
        return load(name).convert_alpha()

    @staticmethod
    def load_sound(name: str, volume: float) -> Sound:
        sound = Sound(name)
        sound.set_volume(volume)
        return sound


class Background:

    def __init__(self) -> None:
        self._sky_img = Assets.load_image_alpha('img/Background/sky_cloud.png')
        self._mountain_img = Assets.load_image_alpha('img/Background/mountain.png')
        self._pine1_img = Assets.load_image_alpha('img/Background/pine1.png')
        self._pine2_img = Assets.load_image_alpha('img/Background/pine2.png')

    def play_music(self):
        # load music and sounds
        music.load('audio/music2.mp3')
        music.set_volume(0.3)
        music.play(-1, 0.0, 5000)

    def draw(self, screen: Surface):
        screen.fill(BG)
        width = self._sky_img.get_width()
        for x in range(5):
            screen.blit(self._sky_img, ((x * width) - bg_scroll * 0.5, 0))
            screen.blit(self._mountain_img,
                        ((x * width) - bg_scroll * 0.6, SCREEN_HEIGHT - self._mountain_img.get_height() - 300))
            screen.blit(self._pine1_img,
                        ((x * width) - bg_scroll * 0.7, SCREEN_HEIGHT - self._pine1_img.get_height() - 150))
            screen.blit(self._pine2_img, ((x * width) - bg_scroll * 0.8, SCREEN_HEIGHT - self._pine2_img.get_height()))


class ScrollSprite(Sprite):

    def __init__(self, image: Surface, rect: Rect):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = rect

    def update(self):
        self.rect.x += screen_scroll


class Tile(ScrollSprite):
    def __init__(self, image: Surface, rect: Rect):
        super().__init__(image, rect)


class CollectBox(ScrollSprite):
    def __init__(self, image: Surface, rect: Rect, collector):
        super().__init__(image, rect)
        self._collector = collector

    def update(self):
        super().update()

        # check if the player has picked up the box
        if pygame.sprite.collide_rect(self, player):
            # collect the item
            self._collector(player)

            # delete the item box
            self.kill()


class Soldier(ScrollSprite):
    def __init__(self, char_type, x, y, scale, speed, ammo, grenades):
        # TODO init ScrollSprite
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.grenades = grenades
        self.health = 100
        self.max_health = self.health
        self.direction = 1
        self.vel_y = 0
        self._jumping = False
        self.in_air = True
        self.flip = False
        self.animation_list = Assets.load_animation_soldier(char_type, scale)
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        # ai specific variables
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 150, 20)
        self.idling = False
        self.idling_counter = 0

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self._shot_fx = Assets.load_sound('audio/shot.wav', 0.5)

    def update(self):
        self.update_animation()
        self.check_alive()
        # update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, moving_left, moving_right):
        # reset movement variables
        screen_scroll = 0
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
        if self._jumping == True and self.in_air == False:
            self.vel_y = -12
            self._jumping = False
            self.in_air = True

        # apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y
        dy += self.vel_y

        # check for collision
        for tile in platform_group:
            # check collision in the x direction
            if tile.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
                # if the ai has hit a wall then make it turn around
                if self.char_type == 'enemy':
                    self.direction *= -1
                    self.move_counter = 0
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
        if pygame.sprite.spritecollide(self, water_group, False):
            self.health = 0

        # check for collision with exit
        level_complete = False
        if pygame.sprite.spritecollide(self, exit_group, False):
            level_complete = True

        # check if fallen off the map
        if self.rect.bottom > SCREEN_HEIGHT:
            self.health = 0

        # check if going off the edges of the screen
        if self.char_type == 'player':
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0

        # update rectangle position
        self.rect.x += dx
        self.rect.y += dy

        # update scroll based on player position
        if self.char_type == 'player':
            if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll < (
                    level_length * TILE_SIZE) - SCREEN_WIDTH) \
                    or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx

        return screen_scroll, level_complete

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20
            bullet = Bullet.create(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction),
                                   self.rect.centery,
                                   self.direction)
            bullet_group.add(bullet)
            # reduce ammo
            self.ammo -= 1
            self._shot_fx.play()

    def ai(self):
        if self.alive and player.alive:
            if self.idling == False and random.randint(1, 200) == 1:
                self.update_action(0)  # 0: idle
                self.idling = True
                self.idling_counter = 50
            # check if the ai in near the player
            if self.vision.colliderect(player.rect):
                # stop running and face the player
                self.update_action(0)  # 0: idle
                # shoot
                self.shoot()
            else:
                if self.idling == False:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)  # 1: run
                    self.move_counter += 1
                    # update ai vision as the enemy moves
                    self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)

                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False

        # scroll
        self.rect.x += screen_scroll

    def update_animation(self):
        # update animation
        ANIMATION_COOLDOWN = 100
        # update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]
        # check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        # if the animation has run out the reset back to the start
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

    def update_action(self, new_action):
        # check if the new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            # update the animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)

    def draw(self, screen: Surface):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


class Player(Soldier):

    def __init__(self, char_type, x, y, scale, speed, ammo, grenades):
        super().__init__(char_type, x, y, scale, speed, ammo, grenades)
        self._jump_fx = Assets.load_sound('audio/jump.wav', 0.25)

    def add_health(self):
        self.health += 25
        if self.health > self.max_health:
            self.health = self.max_health

    def add_ammo(self):
        self.ammo += 15

    def add_grenade(self):
        self.grenades += 3

    def jump(self):
        self._jumping = True
        self._jump_fx.play()


# function to reset level
def reset_level():
    platform_group.empty()
    enemy_group.empty()
    bullet_group.empty()
    grenade_group.empty()
    explosion_group.empty()
    item_box_group.empty()
    decoration_group.empty()
    water_group.empty()
    exit_group.empty()


def load_level(level: int):
    # create empty tile list
    _data = []
    for row in range(ROWS):
        r = [-1] * COLS
        _data.append(r)

    # load in level data and create world
    with open(f'level{level}_data.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for x, row in enumerate(reader):
            for y, tile in enumerate(row):
                _data[x][y] = int(tile)

    global level_length
    level_length = len(_data[0])
    # iterate through each value in level data file
    for y, row in enumerate(_data):
        for x, tile in enumerate(row):
            if tile >= 0:
                img = resources.gfx_scaled(f'tile/{tile}.png', (TILE_SIZE, TILE_SIZE))
                img_rect = img.get_rect()
                img_rect.x = x * TILE_SIZE
                img_rect.y = y * TILE_SIZE
                if tile >= 0 and tile <= 8:
                    platform_group.add(Tile(img, img_rect))
                elif tile >= 9 and tile <= 10:
                    water_group.add(Tile(img, img_rect))
                elif tile >= 11 and tile <= 14:
                    decoration_group.add(Tile(img, img_rect))
                elif tile == 15:  # create player
                    player = Player('player', x * TILE_SIZE, y * TILE_SIZE, 1.65, 5, 20, 5)
                    health_bar = HealthBar(10, 10, player.health)
                elif tile == 16:  # create enemies
                    enemy = Soldier('enemy', x * TILE_SIZE, y * TILE_SIZE, 1.65, 2, 20, 0)
                    enemy_group.add(enemy)
                elif tile == 17:  # create ammo box
                    item_box_group.add(CollectBox(img, img_rect, lambda player: player.add_ammo()))
                elif tile == 18:  # create grenade box
                    item_box_group.add(CollectBox(img, img_rect, lambda player: player.add_grenade()))
                elif tile == 19:  # create health box
                    item_box_group.add(CollectBox(img, img_rect, lambda player: player.add_health()))
                elif tile == 20:  # create exit
                    exit_group.add(Tile(img, img_rect))

    return player, health_bar


def draw_world(screen: Surface):
    for tile in platform_group:
        tile.rect[0] += screen_scroll
        screen.blit(tile.image, tile.rect)


class HealthBar():
    def __init__(self, x, y, max_health):
        self.x = x
        self.y = y
        self.max_health = max_health

    def draw(self, screen: Surface, player: Player):
        # calculate health ratio
        ratio = player.health / self.max_health
        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))

        # show ammo
        self.draw_text(screen, 'AMMO: ', font, WHITE, 10, 35)
        for x in range(player.ammo):
            screen.blit(resources.gfx_alpha('icons/bullet.png'), (90 + (x * 10), 40))
        # show grenades
        self.draw_text(screen, 'GRENADES: ', font, WHITE, 10, 60)
        for x in range(player.grenades):
            screen.blit(resources.gfx_alpha('icons/grenade.png'), (135 + (x * 15), 60))

    @staticmethod
    def draw_text(screen: Surface, text, font, text_col, x, y):
        img = font.render(text, True, text_col)
        screen.blit(img, (x, y))


class Bullet(ScrollSprite):

    @staticmethod
    def create(x, y, direction):
        return Bullet(resources.gfx_alpha('icons/bullet.png'), x, y, direction)

    def __init__(self, image, x, y, direction):
        super().__init__(image, image.get_rect())
        self.speed = 10
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        super().update()
        # move bullet
        self.rect.x += (self.direction * self.speed)
        # check if bullet has gone off screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()
        # check for collision with level
        for tile in platform_group:
            if tile.rect.colliderect(self.rect):
                self.kill()

        # check collision with characters
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 5
                self.kill()
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    enemy.health -= 25
                    self.kill()


class Grenade(ScrollSprite):
    @staticmethod
    def create(x, y, direction):
        return Grenade(resources.gfx_alpha('icons/grenade.png'), x, y, direction)

    def __init__(self, image, x, y, direction):
        super().__init__(image, image.get_rect())
        self.timer = 100
        self.vel_y = -11
        self.speed = 7
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.direction = direction
        self._grenade_fx = Assets.load_sound('audio/grenade.wav', 0.5)

    def update(self):
        super().update()
        self.vel_y += GRAVITY
        dx = self.direction * self.speed
        dy = self.vel_y

        # check for collision with level
        for tile in platform_group:
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
        self.rect.x += dx
        self.rect.y += dy

        # countdown timer
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            self._grenade_fx.play()
            explosion = Explosion(self.rect.x, self.rect.y, 0.5)
            explosion_group.add(explosion)
            # do damage to anyone that is nearby
            if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and \
                    abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2:
                player.health -= 50
            for enemy in enemy_group:
                if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and \
                        abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2:
                    enemy.health -= 50


class Explosion(ScrollSprite):
    def __init__(self, x, y, scale):
        # TODO init ScrollSprite
        pygame.sprite.Sprite.__init__(self)
        self.images = Assets.load_animation_explosions(scale)
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0

    def update(self):
        super().update()

        EXPLOSION_SPEED = 4
        # update explosion amimation
        self.counter += 1

        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0
            self.frame_index += 1
            # if the animation is complete then delete the explosion
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]


class ScreenFade():
    def __init__(self, direction, colour, speed):
        self.direction = direction
        self.colour = colour
        self.speed = speed
        self.fade_counter = 0

    def draw(self, screen: Surface):
        fade_complete = False
        self.fade_counter += self.speed
        if self.direction == 1:  # whole screen fade
            pygame.draw.rect(screen, self.colour, (0 - self.fade_counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.colour,
                             (SCREEN_WIDTH // 2 + self.fade_counter, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.colour, (0, 0 - self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
            pygame.draw.rect(screen, self.colour,
                             (0, SCREEN_HEIGHT // 2 + self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT))
        if self.direction == 2:  # vertical screen fade down
            pygame.draw.rect(screen, self.colour, (0, 0, SCREEN_WIDTH, 0 + self.fade_counter))
        if self.fade_counter >= SCREEN_WIDTH:
            fade_complete = True

        return fade_complete


# create screen fades
intro_fade = ScreenFade(1, BLACK, 4)
death_fade = ScreenFade(2, PINK, 4)


class Button():
    @staticmethod
    def create(name: str, width: int, height: int, scale: int):
        img = Assets.load_image_alpha(name)
        return Button(SCREEN_WIDTH // 2 - width, SCREEN_HEIGHT // 2 + height, img, scale)

    def __init__(self, x, y, image, scale):
        self.width = image.get_width()
        self.height = image.get_height()
        self.image = pygame.transform.scale(image, (int(self.width * scale), int(self.height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def draw(self, surface):
        action = False

        # get mouse position
        pos = pygame.mouse.get_pos()

        # check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        # draw button
        surface.blit(self.image, (self.rect.x, self.rect.y))

        return action


mixer.init()
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Shooter')

# define font
font = pygame.font.SysFont('Futura', 30)

start_button = Button.create('img/start_btn.png', 130, -150, 1)
exit_button = Button.create('img/exit_btn.png', 110, 50, 1)
restart_button = Button.create('img/restart_btn.png', 100, - 50, 2)

background = Background()
background.play_music()

screen_scroll = 0
bg_scroll = 0
level = 1
level_length = 0
start_game = False
start_intro = False

# define player action variables
moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False

# create sprite groups
platform_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

player, health_bar = load_level(level)

clock = pygame.time.Clock()

run = True
while run:

    clock.tick(FPS)

    if start_game == False:
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
        background.draw(screen)
        # draw world map
        draw_world(screen)
        # show player health
        health_bar.draw(screen, player)

        player.update()
        player.draw(screen)

        for enemy in enemy_group:
            enemy.ai()
            enemy.update()
            enemy.draw(screen)

        # recalculate positions
        bullet_group.update()
        grenade_group.update()
        explosion_group.update()
        item_box_group.update()
        decoration_group.update()
        water_group.update()
        exit_group.update()

        # draw groups
        bullet_group.draw(screen)
        grenade_group.draw(screen)
        explosion_group.draw(screen)
        item_box_group.draw(screen)
        decoration_group.draw(screen)
        water_group.draw(screen)
        exit_group.draw(screen)

        # show intro
        if start_intro == True:
            if intro_fade.draw(screen):
                start_intro = False
                intro_fade.fade_counter = 0

        # update player actions
        if player.alive:
            # shoot bullets
            if shoot:
                player.shoot()
            # throw grenades
            elif grenade and grenade_thrown == False and player.grenades > 0:
                grenade = Grenade.create(player.rect.centerx + (0.5 * player.rect.size[0] * player.direction), \
                                         player.rect.top, player.direction)
                grenade_group.add(grenade)
                # reduce grenades
                player.grenades -= 1
                grenade_thrown = True
            if player.in_air:
                player.update_action(2)  # 2: jump
            elif moving_left or moving_right:
                player.update_action(1)  # 1: run
            else:
                player.update_action(0)  # 0: idle
            screen_scroll, level_complete = player.move(moving_left, moving_right)
            bg_scroll -= screen_scroll
            # check if player has completed the level
            if level_complete:
                start_intro = True
                level += 1
                bg_scroll = 0
                reset_level()

                player, health_bar = load_level(level)
        else:
            screen_scroll = 0
            if death_fade.draw(screen):
                if restart_button.draw(screen):
                    death_fade.fade_counter = 0
                    start_intro = True
                    bg_scroll = 0
                    reset_level()

                    player, health_bar = load_level(level)

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
            if event.key == pygame.K_w and player.alive:
                player.jump()
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