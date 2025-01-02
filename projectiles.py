from entity import Collider, CircleCollider, RectCollider, Entity
from vector import Vector2
from typing import Set
from pygame import Color
from camera import Camera
from tilemap import Tilemap

class Projectile:
    projectiles : Set["Projectile"] = set()

    def __init__(self, x, y, size : float, init_velocity = Vector2(0, 0), init_accel = Vector2(0, 0), lifetime = 1.0):
        self.position = Vector2(x, y)
        self.size = size
        self.collider : CircleCollider = Collider.add(CircleCollider(x, y, size, True, True, Color(255, 255, 0, 200)))
        self.collider.parent = self
        self.velocity = init_velocity
        self.accel = init_accel
        self.lifetime = lifetime
        self.timer = 0.0
        self.areas : Set[Collider] = set()
        self.dead : bool = False
    
    def spawn_projectile(x, y, size : float, init_velocity = Vector2(0, 0), init_accel = Vector2(0, 0), lifetime = 1.0):
        Projectile.projectiles.add(Projectile(x, y, size, init_velocity, init_accel, lifetime))
    
    def update_projectiles(delta : float, tilemap : Tilemap, draw_colliders : bool, camera : Camera = None):
        for projectile in Projectile.projectiles.copy():
            projectile.physics_update(delta, tilemap)
            if not projectile.dead and draw_colliders and projectile.collider.is_visible:
                projectile.collider.draw(camera)
    
    def _on_area_entered(self, area : Collider):
        pass

    def _on_area_exited(self, area : Collider):
        pass

    def _on_projectile_collision(self, body : Collider):
        pass

    def kill(self):
        if self.dead:
            return
        Projectile.projectiles.remove(self)
        Collider.remove(self.collider)
        self.dead = True

    def physics_update(self, delta : float, tilemap : Tilemap):
        '''Moves this projectile according to it's velocity and acceleration. On a collision with a body,
        the _on_projectile_collision() method is called. On a collision with an area, the _on_area_entered() 
        method is called.'''

        self.timer += delta
        self.velocity += self.accel * delta
        self.last_velocity = self.velocity
        self.position += self.velocity * delta
        self.collider.position = self.position
        collided_areas = set()

        collisions = self.collider.get_collisions() + self.collider.get_tile_collisions(tilemap)
        for collider in collisions:
            if collider.is_area:
                collided_areas.add(collider)
                collider.is_colliding = True
                if collider not in self.areas:
                    self._on_area_entered(collider)
                    self.areas.add(collider)
            else:
                self._on_projectile_collision(collider)
        
        for area in self.areas.copy():
            if area not in collided_areas:
                self.areas.remove(area)
                self._on_area_exited(area)
        
        if self.timer > self.lifetime:
            self.kill()

class BouncyProjectile (Projectile):
    '''A basic projectile which is designed to bounce off of bodies.'''
    def __init__(self, x, y, size : float, init_velocity = Vector2(0, 0), init_accel = Vector2(0, 0), lifetime = 1.0):
        super().__init__(x, y, size, init_velocity, init_accel, lifetime)
        self.bounciness : float = 1.0
    
    def spawn_projectile(x, y, size : float, init_velocity = Vector2(0, 0), init_accel = Vector2(0, 0), bounciness = 1.0, lifetime = 1.0):
        projectile = BouncyProjectile(x, y, size, init_velocity, init_accel, lifetime)
        projectile.bounciness = bounciness
        Projectile.projectiles.add(projectile)

    def _on_area_entered(self, area : Collider):
        pass

    def _on_area_exited(self, area : Collider):
        pass

    def _on_projectile_collision(self, body : Collider, normal : Vector2):
        self.position += normal
        self.collider.position += normal
        self.velocity = self.velocity.bounce(normal)

    def physics_update(self, delta : float, tilemap : Tilemap):
        '''Moves this projectile according to it's velocity and acceleration. On a collision with a body,
        the _on_projectile_collision() method is called. On a collision with an area, the _on_area_entered() 
        method is called.'''

        self.timer += delta
        self.velocity += self.accel * delta
        self.last_velocity = self.velocity
        self.position.x += self.velocity.x * delta
        self.collider.position.x = self.position.x
        collided_areas = set()

        #Handle x axis
        collisions = self.collider.get_collisions() + self.collider.get_tile_collisions(tilemap)
        for collider in collisions:
            if collider.is_area:
                collided_areas.add(collider)
                collider.is_colliding = True
                if collider not in self.areas:
                    self._on_area_entered(collider)
                    self.areas.add(collider)
            else:
                if isinstance(collider, RectCollider):
                    if self.last_velocity.x < 0:
                        normal = Vector2(collider.position.x + collider.size.x - self.collider.position.x + self.collider.size, 0)
                    elif self.last_velocity.x > 0:
                        normal = Vector2(collider.position.x - self.collider.position.x - self.collider.size, 0)
                else:
                    vector = self.collider.position - collider.position
                    normal = vector.normalized() * (collider.size - vector.length() + self.collider.size)
                self._on_projectile_collision(collider, normal)
        
        self.position.y += self.velocity.y * delta
        self.collider.position.y = self.position.y

        collisions = self.collider.get_collisions() + self.collider.get_tile_collisions(tilemap)
        for collider in collisions:
            if collider.is_area:
                collided_areas.add(collider)
                collider.is_colliding = True
                if collider not in self.areas:
                    self._on_area_entered(collider)
                    self.areas.add(collider)
            else:
                if isinstance(collider, RectCollider):
                    if self.last_velocity.y < 0:
                        normal = Vector2(0, collider.position.y + collider.size.y - self.collider.position.y + self.collider.size)
                    elif self.last_velocity.y > 0:
                        normal = Vector2(0, collider.position.y - self.collider.position.y - self.collider.size)
                else:
                    vector = self.collider.position - collider.position
                    normal = vector.normalized() * (collider.size - vector.length() + self.collider.size)
                self._on_projectile_collision(collider, normal)
        
        for area in self.areas.copy():
            if area not in collided_areas:
                self.areas.remove(area)
                self._on_area_exited(area)
        
        if self.timer > self.lifetime:
            self.kill()