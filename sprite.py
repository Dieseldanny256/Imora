from pygame import Surface
from vector import Vector2
from typing import Dict
from camera import Camera
import math

class Animation:
    pass

class Sprite:
    def __init__(self, x : float, y : float, y_offset : float, surface : Surface = None):
        self.surface = surface
        self.position = Vector2(x, y)
        self.y_offset = y_offset
        self.animations : Dict[str, Animation]
    
    def draw(self, camera : Camera):
        if self.surface == None:
            return
        
        camera.add_to_sorted(self.surface, self.position.x, self.position.y, self.y_offset)