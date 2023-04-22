from pygame import Surface
from pygame.locals import KEYDOWN, K_ESCAPE, QUIT


class Scene:

    def __init__(self) -> None:
        self.level_nr = 1
        self.start_game = False
        self.start_intro = False
        self.running = True

    def next(self):
        return self

    def handle_event(self, event):
        if (event.type == KEYDOWN and event.key == K_ESCAPE) or event.type == QUIT:
            # quit game
            self.running = False

    def draw(self, screen: Surface):
        pass
