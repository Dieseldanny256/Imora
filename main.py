import pygame, time
from tilemap import Tilemap
from entity import Collider, RectCollider, CircleCollider, Entity
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
        self.movement : Vector2 = Vector2(0, 0)
        self.previous_time : float = time.time()
        self.delta : float

        self.collider : CircleCollider = Collider.add(CircleCollider(100, 100, 50, True, False))
        self.collider2 : CircleCollider = Collider.add(CircleCollider(100, 50, 50, True, False, pygame.Color(0, 0, 255)))
        self.entity : Entity = Entity(0, 0, RectCollider(50, 50, 8, 10, True, False, pygame.Color(200, 0, 200)))
        self.tilemap : Tilemap = Tilemap()
        for x in range(10):
            for y in range(10):
                self.tilemap.set_tile(Vector2(x, y), 1)
        
        for x in range(1, 10):
            self.tilemap.set_tile(Vector2(x, 1), 4)
            self.tilemap.set_tile(Vector2(x, 9), 4)
            self.tilemap.set_tile(Vector2(1, x), 4)
            self.tilemap.set_tile(Vector2(9, x), 4)
        
        self.tilemap.set_tile(Vector2(9, 5), 1)

    def update(self) -> bool:
        """Runs once every frame and returns False when it should exit the program"""
        self.delta = time.time() - self.previous_time
        self.previous_time = time.time()
        #print(1/self.delta)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.mouse_down = True
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.mouse_down = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    self.movement.y -= 1
                if event.key == pygame.K_a:
                    self.movement.x -= 1
                if event.key == pygame.K_s:
                    self.movement.y += 1
                if event.key == pygame.K_d:
                    self.movement.x += 1
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    self.movement.y += 1
                if event.key == pygame.K_a:
                    self.movement.x += 1
                if event.key == pygame.K_s:
                    self.movement.y -= 1
                if event.key == pygame.K_d:
                    self.movement.x -= 1

        self.entity.velocity = self.movement * 10 * 16
        self.entity.move_and_collide(self.delta, self.tilemap)

        if (self.mouse_down):
            pass
            #self.tilemap.set_tile(self.tilemap.world_to_tile(Vector2.from_tuple(pygame.mouse.get_pos())), 3)

        # Draw graphics
        self.screen.fill((0, 255, 0))
        self.tilemap.draw(self.screen)
        self.collider.draw(self.screen)
        self.collider2.draw(self.screen)
        self.entity.collider.draw(self.screen)

        # flip() the display to put your work on screen
        pygame.display.flip()

        self.clock.tick(60)  # limits FPS to 60
        return True

main = Main()

while main.update():
    pass