import pygame, time
from tilemap import Tilemap
from entity import Collider, RectCollider, CircleCollider, Entity
from vector import Vector2
from sprite import Sprite
from camera import Camera

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
        self.collider2 : CircleCollider = Collider.add(CircleCollider(100, 50, 50, True, False, pygame.Color(0, 0, 255, 200)))
        self.entity : Entity = Entity(50, 50, RectCollider(8, 24, 16, 8, True, False, pygame.Color(200, 0, 200, 200)))
        self.sprite : Sprite = Sprite(0, 0, 48, pygame.image.load("Images/KarenTieflingStill.png"))
        self.walking : bool = False
        self.tilemap : Tilemap = Tilemap()
        self.camera : Camera = Camera(0, 0)

        self.sprite.add_animation("KarenWalk", "Images/KarenWalk.png", 32, 64, 12, 12, True)
        self.sprite.add_animation("KarenIdle", "Images/KarenIdle.png", 32, 64, 45, 12, True)
        self.sprite.play("KarenIdle")

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

        movement_updated = False

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
                    movement_updated = True
                if event.key == pygame.K_a:
                    self.sprite.flip_x = True
                    self.movement.x -= 1
                    movement_updated = True
                if event.key == pygame.K_s:
                    self.movement.y += 1
                    movement_updated = True
                if event.key == pygame.K_d:
                    self.sprite.flip_x = False
                    self.movement.x += 1
                    movement_updated = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    self.movement.y += 1
                    movement_updated = True
                if event.key == pygame.K_a:
                    self.movement.x += 1
                    movement_updated = True
                if event.key == pygame.K_s:
                    self.movement.y -= 1
                    movement_updated = True
                if event.key == pygame.K_d:
                    self.movement.x -= 1
                    movement_updated = True

        if movement_updated:
            if self.movement.x == 0 and self.movement.y == 0 and self.walking == True:
                self.walking = False
                self.sprite.play("KarenIdle")
            elif self.walking == False:
                self.walking = True
                self.sprite.play("KarenWalk")

        self.entity.velocity = self.movement.normalized() * 10 * 16
        self.entity.move_and_collide(self.delta, self.tilemap)
        self.sprite.position = self.entity.position + Vector2(0, -16)
        self.camera.set_position(self.entity.position - (Vector2.from_tuple(self.screen.get_size()) * 0.5) + Vector2(16, 16))

        if (self.mouse_down):
            world_pos = self.camera.screen_to_world(Vector2.from_tuple(pygame.mouse.get_pos()))
            self.tilemap.set_tile(self.tilemap.world_to_tile(world_pos), 3)

        # Draw graphics
        self.screen.fill((0, 255, 0))
        self.tilemap.draw(self.camera)
        self.collider.draw(self.camera)
        self.collider2.draw(self.camera)
        self.sprite.draw(self.camera, self.delta)
        self.entity.collider.draw(self.camera)
        
        self.camera.draw(self.screen)

        # flip() the display to put your work on screen
        pygame.display.flip()

        self.clock.tick(60)  # limits FPS to 60
        return True

main = Main()

while main.update():
    pass