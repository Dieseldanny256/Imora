import pygame, sys
from tilemap import Tilemap
from vector import Vector2

pygame.init()

class Main:
    """The entry point of the program"""
    def __init__(self):
        self.screen = pygame.display.set_mode((640, 360))
        pygame.display.set_caption("Imora")
        self.clock = pygame.time.Clock()
        self.delta = 0
        self.mouse_down = False

        self.tilemap : Tilemap = Tilemap()
        for x in range(10):
            for y in range(10):
                self.tilemap.set_tile(Vector2(x, y), 0)
        
        for x in range(1):
            self.tilemap.set_tile(Vector2(x, 5), 3)
            #self.tilemap.set_tile(Vector2(x, 9), 3)

    def update(self) -> bool:
        """Runs once every frame and returns False when it should exit the program"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.mouse_down = True
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.mouse_down = False

        if (self.mouse_down):
            self.tilemap.set_tile(self.tilemap.world_to_tile(Vector2.from_tuple(pygame.mouse.get_pos())), 2)

        # Draw graphics
        self.screen.fill((0, 255, 0))
        self.tilemap.draw(self.screen)

        # flip() the display to put your work on screen
        pygame.display.flip()

        self.clock.tick(60)  # limits FPS to 60
        return True

main = Main()

while main.update():
    pass