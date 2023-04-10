import pygame
import os
import string


def load_animations(char_type: string, scale: int) -> []:
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
    return animation_list

