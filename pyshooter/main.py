import pygame
from pygame import mixer, Surface

from pyshooter import resources
from pyshooter.button import Button
from pyshooter.colors import BG
from pyshooter.level_scene import LevelScene
from pyshooter.scene import Scene
from pyshooter.settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS


class TitleScene(Scene):

    def __init__(self) -> None:
        super().__init__()
        self.start_button = Button.create('buttons/start.png', 130, -150, 1)
        self.start_game = False

        self.exit_button = Button.create('buttons/exit.png', 110, 50, 1)

    def next(self):
        if self.start_game is True:
            return LevelScene()
        else:
            return super().next()

    def draw(self, screen: Surface):
        # draw menu
        screen.fill(BG)
        # add buttons
        if self.start_button.draw(screen):
            self.start_game = True
            self.start_intro = True
        if self.exit_button.draw(screen):
            self.running = False


class SceneIterator:
    def __iter__(self):
        self.scene = TitleScene()

        return self

    def __next__(self):
        self.scene = self.scene.next()
        if self.scene.running is True:
            return self.scene
        else:
            raise StopIteration


def main():
    mixer.init()
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Shooter')

    resources.music_play('music2.mp3', 0.3, -1, 0.0, 5000)

    clock = pygame.time.Clock()
    for scene in iter(SceneIterator()):
        clock.tick(FPS)

        for event in pygame.event.get():
            scene.handle_event(event)

        scene.draw(screen)
        pygame.display.update()

    pygame.quit()


if __name__ == '__main__':
    main()
