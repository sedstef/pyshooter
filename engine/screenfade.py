import pygame


class ScreenFade:

    def __init__(self, direction, colour, speed):
        self.direction = direction
        self.colour = colour
        self.speed = speed
        self.fade_counter = 0

    def fade(self, screen: pygame.Surface):
        fade_complete = False
        self.fade_counter += self.speed
        if self.direction == 1:  # whole screen fade
            pygame.draw.rect(screen, self.colour, (0 - self.fade_counter, 0, screen.get_width() // 2, screen.get_height()))
            pygame.draw.rect(screen, self.colour,
                             (screen.get_width() // 2 + self.fade_counter, 0, screen.get_width(), screen.get_height()))
            pygame.draw.rect(screen, self.colour, (0, 0 - self.fade_counter, screen.get_width(), screen.get_height() // 2))
            pygame.draw.rect(screen, self.colour,
                             (0, screen.get_height() // 2 + self.fade_counter, screen.get_width(), screen.get_height()))
        if self.direction == 2:  # vertical screen fade down
            pygame.draw.rect(screen, self.colour, (0, 0, screen.get_width(), 0 + self.fade_counter))
        if self.fade_counter >= screen.get_width():
            fade_complete = True

        return fade_complete
