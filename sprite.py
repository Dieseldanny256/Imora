from pygame import Surface, SRCALPHA, transform, image
from vector import Vector2
from typing import Dict, List
from camera import Camera

class Animation:
    animations : Dict[str, "Animation"] = {}

    def load_animation(name : str, path : str, frame_width : int, frame_height : int, frame_count : int, framerate : float = 12.0, is_looping = True) -> "Animation":
        frames : List[Surface] = []

        if name in Animation.animations:
            print(name + " is already an animation!")
            return None

        try:
            atlas : Surface = image.load(path).convert_alpha()
        except:
            print("Err loading animation atlas from path: " + path)
            return None
        
        counter = 1
        for y in range(atlas.get_height() // frame_height):
            for x in range(atlas.get_width() // frame_width):
                if counter > frame_count:
                    animation = Animation(frames, frame_width, frame_height, frame_count, framerate, is_looping)
                    Animation.animations[name] = animation
                    return animation
                frame = Surface((frame_width, frame_height), SRCALPHA).convert_alpha()
                frame.blit(atlas, (0, 0), (x * frame_width, y * frame_height, frame_width, frame_height))
                frames.append(frame)
                counter += 1
        animation = Animation(frames, frame_width, frame_height, frame_count, framerate, is_looping)
        Animation.animations[name] = animation
        return animation

    def __init__(self, frames : List[Surface], frame_width : int, frame_height : int, frame_count : int, framerate = 12.0, is_looping = True):
        self.frames = frames
        self.framerate = framerate
        self.frame_count = frame_count
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.is_looping = is_looping
        if self.frames != None:
            self.frame_count = len(self.frames)

class Sprite:
    def __init__(self, x : float, y : float, y_offset : float, surface : Surface = None):
        self.surface = surface
        self.position = Vector2(x, y)
        self.y_offset = y_offset
        self.flip_x : bool = False
        self.is_playing : bool = False
        self.animation : Animation = None
        self.frame : int = 0
        self.timer = 0.0
    
    def add_animation(self, name : str, atlas_path : str, frame_width : int, frame_height : int, frame_count : int, framerate = 12.0, is_looping = True):
        Animation.load_animation(name, atlas_path, frame_width, frame_height, frame_count, framerate, is_looping)

    def play(self, name : str = ""):
        if name == "":
            self.is_playing = True
            return
        if name not in Animation.animations:
            self.is_playing = False
            print("Animation " + name + " does not exist!")
            return
        self.animation = Animation.animations[name]
        self.frame = 0
        self.is_playing = True

    def increment_frame(self):
        '''Increment the frame of the animation, upon reaching the end, it will loop back to the beginning
        if is_loop is true. Otherwise, it will set the current frame the last frame.'''
        if self.animation.frame_count == 0:
            return
        self.frame += 1
        if self.animation.is_looping:
            self.frame = self.frame % self.animation.frame_count
        elif self.frame > self.animation.frame_count - 1:
            self.frame = self.animation.frame_count - 1
            self.is_playing = False
    
    def set_frame(self, new_frame : int) -> int:
        '''Sets the frame of the animation to new_frame clamped between 0 and the frame count.'''
        self.frame = new_frame
        if self.frame > self.animation.frame_count - 1:
            self.frame = self.animation.frame_count - 1
        elif self.frame < 0:
            self.frame = 0
    
    def get_frame(self) -> Surface:
        if self.frame >= 0 and self.frame < self.animation.frame_count:
            return self.animation.frames[self.frame]
        return None

    def stop(self):
        self.is_playing = False

    def draw(self, camera : Camera, delta : float):
        if self.is_playing and self.animation != None:
            self.surface = self.get_frame()
            self.timer += delta
            if self.timer > 1/self.animation.framerate:
                self.timer = 0
                self.increment_frame()
        if self.surface == None:
            return
        draw_surface = self.surface
        if self.flip_x:
            draw_surface = transform.flip(draw_surface, self.flip_x, False)
        camera.add_to_sorted(draw_surface, self.position.x, self.position.y, self.y_offset)