from pygame import Surface, Color, draw
from vector import Vector2
from typing import List, Dict, Set
from tilemap import Tilemap
import math

class Collider:
    '''A generic unshaped collider that can detect collisions, do not instance.'''
    
    colliders : Set["Collider"] = set()

    def collide_all():
        for collider in Collider.colliders:
            for collider2 in Collider.colliders:
                if collider == collider2:
                    continue
                if isinstance(collider2, RectCollider):
                    collider.collide_rect(collider2)
                else:
                    collider.collide_circle(collider2)

    def add(collider : "Collider") -> "Collider":
        Collider.colliders.add(collider)
        return collider

    def __init__(self, x : float = 0, y : float = 0, is_visible : bool = False, is_area = True, color : Color = (255, 0, 0)):
        self.position : Vector2 = Vector2(x, y)
        self.is_visible = is_visible
        self.color = color
        self.is_colliding = False
        self.is_area = is_area
        self.parent : Entity = None

    def __del__(self):
        if self in Collider.colliders:
            Collider.colliders.remove(self)

    def draw(self, surface : Surface):
        pass

    def collide_point(self, point : Vector2):
        pass

    def collide_rect(self, collider : "Collider"):
        pass

    def collide_circle(self, collider : "Collider"):
        pass

    def get_collisions(self) -> List["Collider"]:
        collisions = []
        for collider in Collider.colliders:
            if collider == self:
                continue #Don't return self-collisions
            if isinstance(collider, RectCollider):
                if self.collide_rect(collider):    
                    collisions.append(collider)
            else:
                if self.collide_circle(collider):    
                    collisions.append(collider)
        return collisions

    def get_body_collisions(self) -> List["Collider"]:
        collisions = []
        for collider in Collider.colliders:
            if collider == self:
                continue #Don't return self-collisions
            if collider.is_area:
                continue #Don't return any area collisions
            if isinstance(collider, RectCollider):
                if self.collide_rect(collider):    
                    collisions.append(collider)
            else:
                if self.collide_circle(collider):    
                    collisions.append(collider)
        return collisions
    
    def get_area_collisions(self) -> List["Collider"]:
        collisions = []
        for collider in Collider.colliders:
            if collider == self:
                continue #Don't return self-collisions
            if not collider.is_area:
                continue #Don't return any body collisions
            if isinstance(collider, RectCollider):
                if self.collide_rect(collider):    
                    collisions.append(collider)
            else:
                if self.collide_circle(collider):    
                    collisions.append(collider)
        return collisions
    
    def get_tile_collisions(self, tilemap : Tilemap) -> List["Collider"]:
        pass

class RectCollider (Collider):
    '''A rectangular collider which can detect collisions'''
    def __init__(self, x : float = 0, y : float = 0, width : float = 1, height : float = 1, 
                 is_visible : bool = False, is_area = True, color : Color = Color(255, 0, 0)):
        super().__init__(x, y, is_visible, is_area, color)
        self.size = Vector2(width, height)
    
    def draw(self, surface : Surface):
        color = self.color.grayscale()
        if self.is_colliding:
            color = self.color
        self.is_colliding = False

        if self.is_visible:
            draw.rect(surface, color, (self.position.x, self.position.y, self.size.x, self.size.y))

    def collide_point(self, point : Vector2) -> bool:
        colliding_x = False
        colliding_y = False
        if point.x > self.position.x and point.x < self.position.x + self.size.x:
            colliding_x = True
        if point.y > self.position.y and point.y < self.position.y + self.size.y:
            colliding_y = True

        if colliding_x and colliding_y:
            self.is_colliding = True
        return colliding_x and colliding_y

    def collide_rect(self, collider : "Collider") -> bool:
        if not isinstance(collider, RectCollider):
            return False #This should only take rects
        #Horizontal axis
        colliding_x = False
        if (self.position.x < collider.position.x + collider.size.x and 
        self.position.x + self.size.x > collider.position.x):
            colliding_x = True
        #Vertical axis
        colliding_y = False
        if (self.position.y < collider.position.y + collider.size.y and 
        self.position.y + self.size.y > collider.position.y):
            colliding_y = True
        
        if colliding_x and colliding_y:
            self.is_colliding = True
        return colliding_x and colliding_y

    def collide_circle(self, collider : "Collider") -> bool:
        if not isinstance(collider, CircleCollider):
            return False #This should only take circles
        test_x = collider.position.x
        test_y = collider.position.y

        #Horizontal axis
        #If circle is to the left of the left edge
        if collider.position.x < self.position.x:
            test_x = self.position.x
        #If the circle is to the right of the right edge
        elif collider.position.x > self.position.x + self.size.x:
            test_x = self.position.x + self.size.x
        
        #Vertical axis
        #If circle is below the bottom edge
        if collider.position.y < self.position.y:
            test_y = self.position.y
        #If the circle is above the top edge
        elif collider.position.y > self.position.y + self.size.y:
            test_y = self.position.y + self.size.y
        
        #Check if that point is in the range
        dist = (collider.position - Vector2(test_x, test_y)).length()
        if dist < collider.size:
            self.is_colliding = True
            return True
        return False
    
    def get_tile_collisions(self, tilemap) -> List[Collider]:
        #Get tiles that are likely to intersect this collider
        intersecting_tiles = []
        topleft_tile = tilemap.world_to_tile(Vector2(self.position.x, self.position.y))
        bottomright_tile = tilemap.world_to_tile(Vector2(self.position.x + self.size.x, self.position.y + self.size.y))
        for x in range(int(topleft_tile.x), int(bottomright_tile.x + 1)):
            for y in range(int(topleft_tile.y), int(bottomright_tile.y + 1)):
                if tilemap.get_tile_type(Vector2(x, y)) == None:
                    continue
                tile_collider = RectCollider(x * tilemap.tile_size, y * tilemap.tile_size, tilemap.tile_size, tilemap.tile_size, True, False, Color(255, 255, 255, 50))
                if tilemap.get_tile_type(Vector2(x, y)).has_collision and self.collide_rect(tile_collider):
                    intersecting_tiles.append(tile_collider)
        return intersecting_tiles


class CircleCollider (Collider):
    '''A circular collider which can detect collisions'''
    def __init__(self, x : float = 0, y : float = 0, diameter : float = 1, 
                 is_visible : bool = False, is_area = True, color : Color = Color(255, 0, 0)):
        super().__init__(x, y, is_visible, is_area, color)
        self.size = diameter / 2
    
    def draw(self, surface : Surface):
        color = self.color.grayscale()
        if self.is_colliding:
            color = self.color
        self.is_colliding = False
        if self.is_visible:
              draw.circle(surface, color, (self.position.x, self.position.y), self.size)

    def collide_point(self, point : Vector2) -> bool:
        self.is_colliding = False
        if (self.position - point).length() < self.size:
            self.is_colliding = True
        return self.is_colliding

    def collide_rect(self, collider : "Collider"):
        if not isinstance(collider, RectCollider):
            return False #This should only take rects
        test_x = self.position.x
        test_y = self.position.y

        #Horizontal axis
        #If circle is to the left of the left edge
        if self.position.x < collider.position.x:
            test_x = collider.position.x
        #If the circle is to the right of the right edge
        elif self.position.x > collider.position.x + collider.size.x:
            test_x = collider.position.x + collider.size.x
        
        #Vertical axis
        #If circle is below the bottom edge
        if self.position.y < collider.position.y:
            test_y = collider.position.y
        #If the circle is above the top edge
        elif self.position.y > collider.position.y + collider.size.y:
            test_y = collider.position.y + collider.size.y
        
        #Check if that point is in the range
        dist = (self.position - Vector2(test_x, test_y)).length()
        if dist - self.size < -0.001:
            self.is_colliding = True
            return True
        return False

    def collide_circle(self, collider : "Collider"):
        if not isinstance(collider, CircleCollider):
            return False #This should only take circles
        #Calculate the distance between the centers of the two circles
        dist = (self.position - collider.position).length()
        if dist < collider.size + self.size:
            self.is_colliding = True
            return True
        return False
    
    def get_tile_collisions(self, tilemap) -> List[Collider]:
        #Get tiles that are likely to intersect this collider
        intersecting_tiles = []
        topleft_tile = tilemap.world_to_tile(Vector2(self.position.x - self.size, self.position.y - self.size))
        bottomright_tile = tilemap.world_to_tile(Vector2(self.position.x + self.size, self.position.y + self.size))
        for x in range(int(topleft_tile.x), int(bottomright_tile.x) + 1):
            for y in range(int(topleft_tile.y), int(bottomright_tile.y) + 1):
                if tilemap.get_tile_type(Vector2(x, y)) == None:
                    continue
                tile_collider = RectCollider(x * tilemap.tile_size, y * tilemap.tile_size, tilemap.tile_size, tilemap.tile_size, True, False, Color(255, 255, 255, 50))
                if tilemap.get_tile_type(Vector2(x, y)).has_collision and self.collide_rect(tile_collider):
                    intersecting_tiles.append(tile_collider)
        return intersecting_tiles

class Entity:
    '''An entity that has physics and handles collisions'''
    def __init__(self, x : float, y : float, collider : Collider):
        self.position : Vector2 = Vector2(x, y)
        self.collider : Collider = Collider.add(collider)
        self.velocity : Vector2 = Vector2(x, y)
        self.accel : Vector2 = Vector2(x, y)
    
    def physics_update(self, delta):
        self.velocity += self.velocity * delta

    def move_and_collide(self, delta : float, tilemap : Tilemap):
        '''Moves this entity according to its velocity and acceleration vectors, modifying them
        as appropriate to resolve collisions.'''

        #Handle horizontal collisions:
        self.position.x += self.velocity.x * delta #Update position x
        self.collider.position.x += self.velocity.x * delta #Update collider position x
        collider_offset = self.position.x - self.collider.position.x

        collisions : List[Collider] = []
        if self.velocity.x != 0:
            collisions = self.collider.get_body_collisions()
            collisions += self.collider.get_tile_collisions(tilemap)

        has_collided = False
        for collider in collisions:
            if isinstance(self.collider, RectCollider) and isinstance(collider, RectCollider):
                #Resolve the rect-rect collision
                if (self.velocity.x > 0): #Set the right side of this collider to collider's left side
                    self.collider.position.x = collider.position.x - self.collider.size.x
                    self.position.x = self.collider.position.x + collider_offset
                    has_collided = True
                elif (self.velocity.x < 0): #Set the left side of this collider to collider's right side
                    self.collider.position.x = collider.position.x + collider.size.x
                    self.position.x = self.collider.position.x + collider_offset
                    has_collided = True
            elif isinstance(self.collider, RectCollider) and isinstance(collider, CircleCollider):
                #Resolve the rect-circle collision
                #Determine delta_y
                #Top of rect is below the circle's center
                if self.collider.position.y > collider.position.y:
                    delta_y = self.collider.position.y - collider.position.y
                #Bottom of rect is above the circle's center
                elif self.collider.position.y + self.collider.size.y < collider.position.y:
                    delta_y = collider.position.y - (self.collider.position.y + self.collider.size.y)
                #Circle's center is between the rect's top and bottom
                else:
                    delta_y = 0

                delta_x = math.sqrt(collider.size * collider.size - delta_y * delta_y)
                if (self.velocity.x > 0): #Set the right side of this collider to collider's left side
                    target_x = collider.position.x - delta_x
                    self.collider.position.x = target_x - self.collider.size.x
                    self.position.x = self.collider.position.x + collider_offset
                    has_collided = True
                elif (self.velocity.x < 0): #Set the left side of this collider to collider's right side
                    target_x = collider.position.x + delta_x
                    self.collider.position.x = target_x
                    self.position.x = self.collider.position.x + collider_offset
                    has_collided = True
            elif isinstance(self.collider, CircleCollider) and isinstance(collider, RectCollider):
                #Resolve the circle-rect collision
                #Determine delta_y
                #Circle is above the rect's top edge
                if self.collider.position.y < collider.position.y:
                    delta_y = collider.position.y - self.collider.position.y
                #Circle is below the rect's bottom edge
                elif self.collider.position.y > collider.position.y + collider.size.y:
                    delta_y = self.collider.position.y - collider.position.y - collider.size.y
                #Circle is between the rect's bottom and top edges
                else:
                    delta_y = 0
                
                delta_x = math.sqrt(self.collider.size * self.collider.size - delta_y * delta_y)
                if self.velocity.x > 0: #Set the right side of this collider to the other's left side
                    #If the circle already isn't colliding, move on
                    if self.collider.position.x < collider.position.x - delta_x:
                        continue
                    self.collider.position.x = collider.position.x - delta_x
                    self.position.x = self.collider.position.x + collider_offset
                    has_collided = True
                elif self.velocity.x < 0: #Set the left side of this collider to the other's right side
                    #If the circle already isn't colliding, move on
                    if self.collider.position.x > collider.position.x + collider.size.x + delta_x:
                        continue
                    self.collider.position.x = collider.position.x + collider.size.x + delta_x
                    self.position.x = self.collider.position.x + collider_offset
                    has_collided = True

            elif isinstance(self.collider, CircleCollider) and isinstance(collider, CircleCollider):
                #Resolve the circle-circle collision
                #Determine delta_y
                delta_y = self.collider.position.y - collider.position.y
                target_dist = self.collider.size + collider.size
                delta_x = math.sqrt(target_dist * target_dist - delta_y * delta_y)
                if (self.velocity.x > 0): #Set the right side of this collider to collider's left side
                    if self.collider.position.x < collider.position.x - delta_x:
                        continue
                    self.collider.position.x = collider.position.x - delta_x
                    self.position.x = self.collider.position.x + collider_offset
                    has_collided = True
                elif (self.velocity.x < 0): #Set the left side of this collider to collider's right side
                    if self.collider.position.x > collider.position.x + delta_x:
                        continue
                    self.collider.position.x = collider.position.x + delta_x
                    self.position.x = self.collider.position.x + collider_offset
                    has_collided = True
            self.collider.position = self.collider.position.corrected()
            self.position = self.collider.position.corrected()

        if has_collided:
            self.velocity.x = 0

        #Handle vertical collisions:
        self.position.y += self.velocity.y * delta #Update position y
        self.collider.position.y += self.velocity.y * delta #Update collider position y
        collider_offset = self.position.y - self.collider.position.y

        collisions = []
        if self.velocity.y != 0:
            collisions = self.collider.get_body_collisions()
            collisions += self.collider.get_tile_collisions(tilemap)

        has_collided = False
        for collider in collisions:
            if isinstance(self.collider, RectCollider) and isinstance(collider, RectCollider):
                #Resolve the rect-rect collision
                if (self.velocity.y > 0): #Set the right side of this collider to collider's left side
                    self.collider.position.y = collider.position.y - self.collider.size.y
                    self.position.y = self.collider.position.y + collider_offset
                    has_collided = True
                elif (self.velocity.y < 0): #Set the left side of this collider to collider's right side
                    self.collider.position.y = collider.position.y + collider.size.y
                    self.position.y = self.collider.position.y + collider_offset
                    has_collided = True
            elif isinstance(self.collider, RectCollider) and isinstance(collider, CircleCollider):
                #Resolve the rect-circle collision
                #Determine delta_x
                #Left of rect is to the right of the circle's center
                if self.collider.position.x > collider.position.x:
                    delta_x = self.collider.position.x - collider.position.x
                #Right of rect is to the left of the circle's center
                elif self.collider.position.x + self.collider.size.x < collider.position.x:
                    delta_x = collider.position.x - (self.collider.position.x + self.collider.size.x)
                #Circle's center is between the rect's left and right
                else:
                    delta_x = 0

                delta_y = math.sqrt(collider.size * collider.size - delta_x * delta_x)
                if (self.velocity.y > 0): #Set the right side of this collider to collider's left side
                    target_y = collider.position.y - delta_y
                    if self.collider.position.y < target_y - self.collider.size.y:
                        continue
                    self.collider.position.y = target_y - self.collider.size.y
                    self.position.y = self.collider.position.y + collider_offset
                    has_collided = True
                elif (self.velocity.y < 0): #Set the left side of this collider to collider's right side
                    target_y = collider.position.y + delta_y
                    if self.collider.position.y > target_y:
                        continue
                    self.collider.position.y = target_y
                    self.position.y = self.collider.position.y + collider_offset
                    has_collided = True
            elif isinstance(self.collider, CircleCollider) and isinstance(collider, RectCollider):
                #Resolve the circle-rect collision
                #Determine delta_x
                #Left of rect is to the right of the circle's center
                if self.collider.position.x < collider.position.x:
                    delta_x = collider.position.x - self.collider.position.x
                #Right of rect is to the left of the circle's center
                elif collider.position.x + collider.size.x < self.collider.position.x:
                    delta_x = self.collider.position.x - (collider.position.x + collider.size.x)
                #Circle's center is between the rect's top and bottom
                else:
                    delta_x = 0

                delta_y = math.sqrt(self.collider.size * self.collider.size - delta_x * delta_x)
                if (self.velocity.y > 0): #Set the bottom side of this collider to collider's top side
                    if self.collider.position.y < collider.position.y - delta_y:
                        continue
                    self.collider.position.y = collider.position.y - delta_y
                    self.position.y = self.collider.position.y + collider_offset
                    has_collided = True
                elif (self.velocity.y < 0): #Set the top side of this collider to collider's bottom side
                    if self.collider.position.y > collider.position.y + collider.size.y + delta_y:
                        continue
                    self.collider.position.y = collider.position.y + collider.size.y + delta_y
                    self.position.y = self.collider.position.y + collider_offset
                    has_collided = True
            elif isinstance(self.collider, CircleCollider) and isinstance(collider, CircleCollider):
                #Resolve the circle-circle collision
                #Determine delta_x
                delta_x = self.collider.position.x - collider.position.x
                target_dist = self.collider.size + collider.size
                delta_y = math.sqrt(target_dist * target_dist - delta_x * delta_x)
                if (self.velocity.y > 0): #Set the right side of this collider to collider's left side
                    if self.collider.position.y < collider.position.y - delta_y:
                        continue
                    self.collider.position.y = collider.position.y - delta_y
                    self.position.y = self.collider.position.y + collider_offset
                    has_collided = True
                elif (self.velocity.y < 0): #Set the left side of this collider to collider's right side
                    if self.collider.position.y > collider.position.y + delta_y:
                        continue
                    self.collider.position.y = collider.position.y + delta_y
                    self.position.y = self.collider.position.y + collider_offset
                    has_collided = True
            self.collider.position = self.collider.position.corrected()
            self.position = self.collider.position.corrected()
        if has_collided:
            self.velocity.y = 0