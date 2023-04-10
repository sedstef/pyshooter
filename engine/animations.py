from enum import IntEnum

import pygame
import os
import string


class Action(IntEnum):
    IDLE = 0,
    RUN = 1,
    JUMP = 2,
    DEATH = 3,


ANIMATION_COOLDOWN = 100


class ActionAnimation:
    @staticmethod
    def load_animations(char_type: string, scale: int):
        animation_list = []
        animation_types = ['Idle', 'Run', 'Jump', 'Death']
        for animation in animation_types:
            # reset temporary list of images
            temp_list = []
            # count number of files in the folder
            num_of_frames = len(os.listdir(f'img/{char_type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'img/{char_type}/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            animation_list.append(temp_list)
        return ActionAnimation(animation_list)


    def __init__(self, animation_list: []):
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        self.animation_list = animation_list

    def image(self, action: Action):
        return self.animation_list[action.value][0]

    def update_animation(self, action: Action):
        # update image depending on current frame
        image = self.animation_list[action.value][self.frame_index]
        # check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        # if the animation has run out the reset back to the start
        if self.frame_index >= len(self.animation_list[action.value]):
            if Action.DEATH == action:
                self.frame_index = len(self.animation_list[action.value]) - 1
            else:
                self.frame_index = 0
        return image

    def reset(self, action: Action):
        # update the animation settings
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
