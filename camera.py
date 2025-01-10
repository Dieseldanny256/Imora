from pygame import Surface
from typing import List
from vector import Vector2
import math

class Drawable:
    def __init__(self, surface : Surface, x : float, y : float, y_offset : float):
        self.surface = surface
        self.x = math.floor(x)
        self.y = math.floor(y)
        self.y_offset = math.floor(y_offset)

class Camera:
    def __init__(self, x : float, y : float):
        self.x : int = math.floor(x)
        self.y : int = math.floor(y)
        self.drawables : List[Drawable] = []
        self.sorted_drawables : List[Drawable] = []
        self.ceilings : List[Drawable] = []
        self.overlays : List[Drawable] = []
    
    def screen_to_world(self, vector : Vector2):
        return vector + Vector2(self.x, self.y)

    def world_to_screen(self, vector : Vector2):
        return vector - Vector2(self.x, self.y)

    def set_position(self, new_position : Vector2):
        self.x = math.floor(new_position.x)
        self.y = math.floor(new_position.y)

    def add_to_unsorted(self, surface : Surface, x : float, y : float):
        drawable = Drawable(surface, x, y, 0)
        self.drawables.append(drawable)

    def add_to_sorted(self, surface : Surface, x : float, y : float, y_offset : float):
        drawable = Drawable(surface, x, y, y_offset)
        self.sorted_drawables.append(drawable)
    
    def add_to_ceiling(self, surface : Surface, x : float, y : float):
        drawable = Drawable(surface, x, y, 0)
        self.ceilings.append(drawable)

    def add_to_overlay(self, surface : Surface, x : float, y : float):
        drawable = Drawable(surface, x, y, 0)
        self.overlays.append(drawable)

    def draw(self, dest : Surface):
        #Draw non-sorted drawables first
        for drawable in self.drawables:
            dest.blit(drawable.surface, (drawable.x - self.x, drawable.y - self.y))
        #Draw sorted drawables overtop
        self.sorted_drawables.sort(key=lambda drawable: drawable.y + drawable.y_offset)
        for drawable in self.sorted_drawables:
            dest.blit(drawable.surface, (drawable.x - self.x, drawable.y - self.y))
        #Draw overlays above that
        for drawable in self.overlays:
            dest.blit(drawable.surface, (drawable.x - self.x, drawable.y - self.y))
        #Clear drawables arrays for next frame
        self.drawables.clear()
        self.sorted_drawables.clear()
        self.overlays.clear()