from pygame import Surface, Font, Color, SRCALPHA, KEYDOWN, KEYUP, K_BACKSPACE, mouse, MOUSEBUTTONDOWN, draw
from camera import Camera
from typing import Tuple, List
from sprite import Animation

class UIElement:
    def __init__(self, x : int, y : int):
        self.x = x
        self.y = y
        self.surface : Surface = None

    def draw_to_hud(self, dest : Surface):
        dest.blit(self.surface, (self.x, self.y))

    def draw_to_camera(self, camera : Camera):
        pass

class Field (UIElement):
    def __init__(self, x : int, y : int, width : int, height : int, back_atlas : Surface = None, margin_size = (0, 0)):
        super().__init__(x, y)
        self.back_atlas = back_atlas
        self.margin_size = margin_size
        self.set_size(width, height)

    def update_surface(self, atlas : Surface, middle_width : int, middle_height : int):
        if self.back_atlas == None:
            return

        #Generate the background surface
        self.surface = Surface((middle_width + 2 * self.margin_size[0], 
                                     middle_height + 2 * self.margin_size[1]), 
                                     SRCALPHA).convert_alpha()
        
        #Top and bottom edges
        top_strip = Surface((middle_width, self.margin_size[1]), SRCALPHA).convert_alpha()
        bottom_strip = Surface((middle_width, self.margin_size[1]), SRCALPHA).convert_alpha()
        atlas_width = self.back_atlas.get_width() - self.margin_size[0] * 2
        for x in range(middle_width // self.margin_size[0] + 1):
            top_strip.blit(atlas, (x * atlas_width, 0), (self.margin_size[0], 0, atlas_width, self.margin_size[1]))
            bottom_strip.blit(atlas, (x * atlas_width, 0), (self.margin_size[0], self.back_atlas.get_height() - self.margin_size[1], atlas_width, self.margin_size[1]))
        self.surface.blit(top_strip, (self.margin_size[0], 0))
        self.surface.blit(bottom_strip, (self.margin_size[0], self.surface.get_height() - self.margin_size[1]))

        #Left and right edges
        left_strip = Surface((self.margin_size[0], middle_height), SRCALPHA).convert_alpha()
        right_strip = Surface((self.margin_size[0], middle_height), SRCALPHA).convert_alpha()
        atlas_height = self.back_atlas.get_height() - self.margin_size[1] * 2
        for y in range(middle_height // self.margin_size[1] + 1):
            left_strip.blit(atlas, (0, y * atlas_height), (0, self.margin_size[1], self.margin_size[0], atlas_height))
            right_strip.blit(atlas, (0, y * atlas_height), (self.back_atlas.get_width() - self.margin_size[0], self.margin_size[1], self.margin_size[0], atlas_height))
        self.surface.blit(left_strip, (0, self.margin_size[1]))
        self.surface.blit(right_strip, (self.surface.get_width() - self.margin_size[0], self.margin_size[1]))

        #Middle
        mid_section = Surface((middle_width, middle_height), SRCALPHA).convert_alpha()
        for y in range(0, middle_height // atlas_height + 1):
            for x in range(0, middle_width // atlas_width + 1):
                mid_section.blit(atlas, (x * atlas_width, y * atlas_height), (self.margin_size[0], self.margin_size[1], atlas_width, atlas_height))
        self.surface.blit(mid_section, (self.margin_size[0], self.margin_size[1]))
        
        #Corners
        self.surface.blit(atlas, (0, 0), (0, 0, self.margin_size[0], self.margin_size[1]))
        self.surface.blit(atlas, (self.surface.get_width() - self.margin_size[0], 0), (self.back_atlas.get_width() - self.margin_size[0], 0, self.margin_size[0], self.margin_size[1]))
        self.surface.blit(atlas, (0, self.surface.get_height() - self.margin_size[1]), (0, self.back_atlas.get_height() - self.margin_size[1], self.margin_size[0], self.margin_size[1]))
        self.surface.blit(atlas, (self.surface.get_width() - self.margin_size[0], self.surface.get_height() - self.margin_size[1]), (self.back_atlas.get_width() - self.margin_size[0], self.back_atlas.get_height() - self.margin_size[1], self.margin_size[0], self.margin_size[1]))

    def set_size(self, width : int, height : int):
        self.width = width
        self.height = height
        self.update_surface(self.back_atlas, self.width - self.margin_size[0] * 2, self.height - self.margin_size[1] * 2)

class Textbox (Field):
    def __init__(self, x : int, y : int, font : Font, text_color : Color = Color(255, 255, 255, 255), 
                 margin_size = (0, 0), back_atlas : Surface = None, editable = False, min_size = -1, max_size = -1, wrap = False):
        super().__init__(x, y, margin_size[0] * 2, margin_size[1] * 2, back_atlas, margin_size)
        self.editable = editable
        self.text_surfaces : List[Surface] = []
        self.font = font
        self.text_color = text_color
        self.editing = False
        self.timer = 0
        self.min_size = min_size
        self.max_size = max_size
        self.wrap = wrap
        self.set_text("")

    def collide_point(self, point : Tuple) -> bool:
        colliding_x = False
        colliding_y = False
        if point[0] > self.x and point[0] < self.x + self.surface.get_width():
            colliding_x = True
        if point[1] > self.y and point[1] < self.y + self.surface.get_height():
            colliding_y = True

        if colliding_x and colliding_y:
            self.is_colliding = True
        return colliding_x and colliding_y

    def draw_to_hud(self, dest : Surface):
        dest.blit(self.surface, (self.x, self.y))
        if self.editing:
            self.timer += 1
            if self.timer <= 60:
                last = len(self.text_surfaces) - 1
                target_x = min(self.x + self.margin_size[0] + self.text_surfaces[last].get_width() + 2, self.x + self.max_size - 4)
                draw.rect(dest, self.text_color, (target_x, self.y + self.margin_size[1] + last * self.font.get_height(), 2, self.text_surfaces[last].get_height()))
            if self.timer > 120:
                self.timer = 0

    def handle_input(self, event) -> bool:
        '''Handle per frame inputs to this textfield. Returns true if this textfield absorbed the input.'''
        if not self.editable:
            return False
        
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            if not self.editing and self.collide_point(mouse.get_pos()):
                self.editing = True
                return True
            elif self.editing and not self.collide_point(mouse.get_pos()):
                self.editing = False
                self.timer = 0
                return True
        elif not self.editing:
            return False
        
        if event.type == KEYDOWN:
            if event.key == K_BACKSPACE:
                if len(self.text) > 0:
                    self.set_text(self.text[:-1])
                    return True
            else:
                self.set_text(self.text + event.unicode)
                return True
        if event.type == KEYUP:
            return True
        return False

    def set_text(self, text : str):
        self.text = text

        if self.font == None:
            return

        #Generate the text surface
        self.text_surfaces = []
        lines = self.text.replace("\r", "\n").split("\n")
        for line in lines:
            if self.wrap:
                words = line.split()
                current_line = ""
                #Sentences
                for i in range(len(words)):
                    test_str = current_line
                    if i != 0:
                        test_str += " "
                    test_str += words[i]
                    if self.font.size(test_str)[0] >= self.max_size - self.margin_size[0] * 2:
                        self.text_surfaces.append(self.font.render(current_line, True, self.text_color))
                        current_line = words[i]
                        continue
                    if i != 0:
                        current_line += " "
                    current_line += words[i]
                self.text_surfaces.append(self.font.render(current_line, True, self.text_color))
            else:
                self.text_surfaces.append(self.font.render(line, True, self.text_color))

        if self.back_atlas == None:
            self.surface = Surface(self.max_size, self.text_surfaces[0].get_height(), SRCALPHA).convert_alpha()
            line = 0
            for text_surface in self.text_surfaces:
                self.surface.blit(text_surface, (0, line * self.font.get_height()))
            return
        
        text_height = self.font.get_height() * len(self.text_surfaces)

        #Determine the size
        target_width = 0
        if len(self.text_surfaces) == 1:
            target_width = self.text_surfaces[0].get_width()
        else:
            target_width = self.max_size
        if self.min_size > 0:
            target_width = max(self.min_size - self.margin_size[0] * 2, target_width)
        if self.max_size > 0:
            target_width = min(self.max_size - self.margin_size[0] * 2, target_width)
        self.update_surface(self.back_atlas, target_width, text_height)
        self.width, self.height = self.surface.get_width(), self.surface.get_height()

        #Blit text ontop
        for line in range(len(self.text_surfaces)):
            if line == len(self.text_surfaces) - 1:
                if self.max_size > 0 and self.text_surfaces[line].get_width() > (self.max_size - self.margin_size[0] * 2):
                    self.surface.blit(self.text_surfaces[line], (-self.margin_size[0] - self.text_surfaces[line].get_width() + self.max_size, self.margin_size[1] + line * self.font.get_height()))
                else:
                    self.surface.blit(self.text_surfaces[line], (self.margin_size[0], self.margin_size[1] + line * self.font.get_height()))
                continue
            self.surface.blit(self.text_surfaces[line], (self.margin_size[0], self.margin_size[1] + line * self.font.get_height()))

class Button (Textbox):
    def __init__(self, x : int, y : int, font : Font = None, text_color : Color = Color(255, 255, 255, 255), 
                 margin_size = (0, 0), back_atlas : Surface = None):
        super().__init__(x, y, font, text_color, margin_size, back_atlas)
        self.current_back_atlas = self.back_atlas
        self.pressed = False
        self.pressed_animation : Animation = None
        self.playing : bool = False
        self.frame : int = 0
        self.timer : float = 0.0
    
    def handle_input(self, event) -> bool:
        '''Handle per frame inputs to this button. Returns true if this button absorbed the input.'''
        
        absorb_input = False

        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            if not self.pressed and self.collide_point(mouse.get_pos()):
                self.pressed = True
                absorb_input = True
                self.frame = 0

        return absorb_input
    
    def add_animation(self, name : str, atlas_path : str, frame_width : int, frame_height : int, frame_count : int, framerate = 12.0, is_looping = True):
        self.pressed_animation = Animation.load_animation(name, atlas_path, frame_width, frame_height, frame_count, framerate, is_looping)

    def draw_to_hud(self, dest : Surface, delta : float):
        #Do animation
        if self.pressed and self.pressed_animation != None:
            self.playing = True
            self.current_back_atlas = self.pressed_animation.frames[self.frame]
            self.pressed = False
        elif self.pressed:
            self.pressed = False
        elif self.playing:
            self.timer += delta
        
        #Advance the animation frame
        if self.playing:
            if self.timer > 1/self.pressed_animation.framerate:
                self.timer = 0
                self.frame += 1
                if self.frame >= self.pressed_animation.frame_count:
                    self.frame = 0
                    self.playing = False
                    self.current_back_atlas = self.back_atlas
                else:
                    self.current_back_atlas = self.pressed_animation.frames[self.frame]

        if self.current_back_atlas != None:
            if self.font != None:
                text_surface = self.font.render(self.text, True, self.text_color)
                self.update_surface(self.current_back_atlas, *text_surface.get_size())
                self.surface.blit(text_surface, self.margin_size)
            else:
                middle_size = (self.current_back_atlas.get_width() - self.margin_size[0] * 2,
                               self.current_back_atlas.get_height() - self.margin_size[1] * 2)
                self.update_surface(self.current_back_atlas, *middle_size)

        dest.blit(self.surface, (self.x, self.y))