import pygame, time
from tilemap import Tilemap
from entity import Collider, RectCollider, CircleCollider, Entity
from vector import Vector2
from sprite import Sprite
from camera import Camera
from projectiles import Projectile, BouncyProjectile

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

        self.collider : CircleCollider = Collider.add(CircleCollider(100, 100, 50, True, False, color=pygame.Color(255, 0, 0, 200)))
        self.entity : Entity = Entity(50, 50, RectCollider(8, 24, 16, 8, False, False))
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
        self.delta = min(time.time() - self.previous_time, 0.5)
        self.previous_time = time.time()
        if 1/self.delta < 40:
            print(1/self.delta)
            print(len(Projectile.projectiles))

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
                if event.key == pygame.K_SPACE:
                    self.entity.velocity = Vector2.vector_to(self.entity.position, self.camera.screen_to_world(Vector2.from_tuple(pygame.mouse.get_pos())), 35 * 16)
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

        Projectile.update_projectiles(self.delta, self.tilemap, True, self.camera)
        movement_dir = self.movement.normalized()
        #If the player is attempting to accelerate beyond the max velocity of 10 tiles/s
        if (movement_dir.x != 0 or movement_dir.y != 0) and self.entity.velocity.length() > 10 * 16:
            #Set their acceleration to be the dot product of the opposite of their velocity, 
            #normalized between 0 and 1, times their ordinary acceleration
            #This has the effect of reducing the acceleration the more in line it is with their velocity
            self.entity.accel = (movement_dir.dot(-self.entity.velocity.normalized()) * 0.5 + 0.5) * movement_dir * 80 * 16
        else:
            self.entity.accel = movement_dir * 80 * 16
        self.entity.physics_update(self.delta, self.tilemap)
        if self.entity.velocity.length() > 30 * 16 * self.delta:
            self.entity.velocity -= self.entity.velocity.normalized() * 40 * 16 * self.delta
        else:
            self.entity.velocity = Vector2(0, 0)
        self.sprite.position = self.entity.position + Vector2(0, -16)
        self.camera.set_position(self.entity.position - (Vector2.from_tuple(self.screen.get_size()) * 0.5) + Vector2(16, 16))
        
        if (self.mouse_down):
            world_pos = self.camera.screen_to_world(Vector2.from_tuple(pygame.mouse.get_pos()))
            BouncyProjectile.spawn_projectile(world_pos.x, world_pos.y, 10, Vector2.vector_to(self.entity.position + Vector2(16, 24), world_pos, 30 * 16), lifetime=2.0, bounciness=1.0)
            pass

        # Draw graphics
        self.screen.fill((0, 255, 0))
        self.tilemap.draw(self.camera)
        self.collider.draw(self.camera)
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