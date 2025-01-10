import time, sys
import pygame
from tilemap import Tilemap
from vector import Vector2
from camera import Camera
from typing import List
from ui import Textbox, Button

pygame.init()

class Editor:
    """The entry point of the program"""
    def __init__(self):
        self.screen = pygame.display.set_mode((640, 360))
        pygame.display.set_caption("Imora Editor")
        self.clock = pygame.time.Clock()
        self.delta = 0
        self.mouse_down = False
        self.right_mouse_down = False
        self.movement : Vector2 = Vector2(0, 0)
        self.previous_time : float = time.time()
        self.delta : float
        self.has_saved = True

        self.box_font : pygame.Font = pygame.font.Font("Fonts/box.ttf", 20)
        self.tilemap : Tilemap = Tilemap()
        textbox_back = pygame.image.load("Images/UI/TextboxBack.png")
        self.textbox = Textbox(100, 100, self.box_font, back_atlas=textbox_back, margin_size=(8,8))
        self.textfield = Textbox(100, self.screen.get_height()/2, self.box_font, back_atlas=textbox_back, margin_size=(8,8), editable=True, min_size=420, max_size=420)
        self.save_button = Button(self.screen.get_width() - 32, 0, back_atlas=pygame.image.load("Images/UI/SaveButton.png"), margin_size=(8,8))
        self.save_button.add_animation("SavePress", "Images/UI/SaveButtonPress.png", 32, 32, 5, 12, False)
        self.load_button = Button(self.screen.get_width() - 64, 0, back_atlas=pygame.image.load("Images/UI/LoadButton.png"), margin_size=(8,8))
        self.load_button.add_animation("LoadPress", "Images/UI/LoadButtonPress.png", 32, 32, 5, 12, False)
        self.new_button = Button(self.screen.get_width() - 96, 0, back_atlas=pygame.image.load("Images/UI/NewButton.png"), margin_size=(8,8))
        self.new_button.add_animation("NewPress", "Images/UI/NewButtonPress.png", 32, 32, 5, 12, False)

        self.exit_prompt = Textbox(self.screen.get_width()/2 - 150, 100, self.box_font, back_atlas=textbox_back, margin_size=(8,8), max_size=300, wrap=True)
        self.exit_prompt.set_text("You have unsaved changes!\n\nAre you sure you want to do this without saving?")
        self.exit_prompt.y = self.screen.get_height()/2 - self.exit_prompt.height - 10

        self.yes_button = Button(0, 0, self.box_font, margin_size=(8, 8), back_atlas=textbox_back)
        self.yes_button.set_text("Yes")
        self.yes_button.x = self.screen.get_width()/2 - self.yes_button.surface.get_width() - 10
        self.yes_button.y = self.screen.get_height()/2

        self.no_button = Button(0, 0, self.box_font, margin_size=(8, 8), back_atlas=textbox_back)
        self.no_button.set_text("No")
        self.no_button.x = self.screen.get_width()/2 + 10
        self.no_button.y = self.screen.get_height()/2
        
        self.camera : Camera = Camera(0, 0)
        self.position : Vector2 = Vector2(0, 0)
        self.tile_type : int = 0
        
        self.current_file : str = ""

        self.textbox.set_text(Tilemap.tile_types[self.tile_type].name)
        self.textfield.set_text(self.current_file)

        self.icons : List[pygame.Surface] = []

    def quit(self):
        if not self.has_saved:
            if not self.save_warning():
                return
        pygame.quit()
        sys.exit()
        
    def save_warning(self) -> bool:
        while(True):
            self.delta = time.time() - self.previous_time
            self.previous_time = time.time()

            for event in pygame.event.get():
                if self.yes_button.handle_input(event):
                    return True
                if self.no_button.handle_input(event):
                    return False
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            self.exit_prompt.draw_to_hud(self.screen)
            self.yes_button.draw_to_hud(self.screen, self.delta)
            self.no_button.draw_to_hud(self.screen, self.delta)
            self.save_button.draw_to_hud(self.screen, self.delta)
            self.load_button.draw_to_hud(self.screen, self.delta)
            self.new_button.draw_to_hud(self.screen, self.delta)

            # flip() the display to put your work on screen
            pygame.display.flip()

            self.clock.tick(60)  # limits FPS to 60

    def save_menu(self) -> bool:
        self.delta = time.time() - self.previous_time
        self.previous_time = time.time()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.current_file = self.textfield.text
                    return False
            if self.textfield.handle_input(event):
                pass
        
        self.textfield.draw_to_hud(self.screen)
        self.save_button.draw_to_hud(self.screen, self.delta)

        # flip() the display to put your work on screen
        pygame.display.flip()

        self.clock.tick(60)  # limits FPS to 60
        return True

    def load_menu(self) -> bool:
        self.delta = time.time() - self.previous_time
        self.previous_time = time.time()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.current_file = self.textfield.text
                    return False
            if self.textfield.handle_input(event):
                pass
        
        self.textfield.draw_to_hud(self.screen)
        self.load_button.draw_to_hud(self.screen, self.delta)

        # flip() the display to put your work on screen
        pygame.display.flip()

        self.clock.tick(60)  # limits FPS to 60
        return True

    def update(self) -> bool:
        """Runs once every frame and returns False when it should exit the program"""
        self.delta = time.time() - self.previous_time
        self.previous_time = time.time()

        for event in pygame.event.get():
            if self.textbox.handle_input(event):
                continue
            if self.new_button.handle_input(event):
                if not self.has_saved:
                    if not self.save_warning():
                        continue
                self.current_file = ""
                self.has_saved = True
                self.tilemap.clear()
                continue
            if self.load_button.handle_input(event):
                if not self.has_saved:
                    if not self.save_warning():
                        continue
                self.textfield.set_text("")
                self.textfield.editing = True
                while (self.load_menu()):
                    pass
                if self.tilemap.load("Levels/" + self.current_file + ".json"):
                    self.has_saved = True
                self.camera.set_position(Vector2(0, 0))
                continue
            if self.save_button.handle_input(event):
                if self.current_file == "":
                    self.textfield.set_text("")
                    self.textfield.editing = True
                    while (self.save_menu()):
                        pass
                if self.current_file == "":
                    continue
                self.tilemap.save("Levels/" + self.current_file + ".json")
                self.has_saved = True
                continue
            if event.type == pygame.QUIT:
                self.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.mouse_down = True
                if event.button == 3:
                    self.right_mouse_down = True
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.mouse_down = False
                if event.button == 3:
                    self.right_mouse_down = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    self.movement.y -= 1
                if event.key == pygame.K_a:
                    self.movement.x -= 1
                if event.key == pygame.K_s:
                    self.movement.y += 1
                if event.key == pygame.K_d:
                    self.movement.x += 1
                if event.key == pygame.K_LEFT:
                    self.tile_type = (self.tile_type - 1) % len(Tilemap.tile_types)
                    self.textbox.set_text(Tilemap.tile_types[self.tile_type].name)
                if event.key == pygame.K_RIGHT:
                    self.tile_type = (self.tile_type + 1) % len(Tilemap.tile_types)
                    self.textbox.set_text(Tilemap.tile_types[self.tile_type].name)
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    self.movement.y += 1
                if event.key == pygame.K_a:
                    self.movement.x += 1
                if event.key == pygame.K_s:
                    self.movement.y -= 1
                if event.key == pygame.K_d:
                    self.movement.x -= 1
        
        self.position += self.movement * 10 * 16 * self.delta
        self.camera.set_position(self.position)
        
        world_pos = self.camera.screen_to_world(Vector2.from_tuple(pygame.mouse.get_pos()))
        tile_pos = self.tilemap.world_to_tile(world_pos)

        if (self.right_mouse_down):
            self.tilemap.set_tile(tile_pos, -1)
            self.has_saved = False
        elif (self.mouse_down):
            self.tilemap.set_tile(tile_pos, self.tile_type)
            self.has_saved = False

        # Draw graphics
        self.screen.fill((0, 0, 0))
        self.tilemap.draw(self.camera)
        self.camera.draw(self.screen)

        tile_pos_text = self.box_font.render(str(tile_pos), True, (255, 255, 255))
        tile_icon : pygame.Surface = Tilemap.get_tile_icon(self.tile_type)
        lower_opacity_icon = tile_icon.copy()
        lower_opacity_icon.set_alpha(150)
        snapped_world_pos = self.camera.world_to_screen(self.tilemap.tile_to_world(tile_pos))
        self.screen.blit(lower_opacity_icon, (snapped_world_pos.x, snapped_world_pos.y - tile_icon.get_height() + tile_icon.get_width()))

        #Hud Elements
        self.screen.blit(tile_icon, (10, 10))
        self.textbox.x = 20 + tile_icon.get_width()
        self.textbox.y = 10
        self.screen.blit(tile_pos_text, (20 + tile_icon.get_width(), 20 + self.textbox.surface.get_height()))
        self.textbox.draw_to_hud(self.screen)
        self.save_button.draw_to_hud(self.screen, self.delta)
        self.load_button.draw_to_hud(self.screen, self.delta)
        self.new_button.draw_to_hud(self.screen, self.delta)

        # flip() the display to put your work on screen
        pygame.display.flip()

        self.clock.tick(60)  # limits FPS to 60
        return True

editor = Editor()

while editor.update():
    pass