from pygame import Surface, Rect
from typing import List, Dict, Set
from vector import Vector2
from camera import Camera
import pygame, os

class Tilemap:
    TILE_BITMAPS : Dict[int, int] = {
        0x4 :  0, 0xA :  1, 0xD :  2, 0xC :  3,
        0x9 :  4, 0xE :  5, 0xF :  6, 0x7 :  7,
        0x2 :  8, 0x3 :  9, 0xB : 10, 0x5 : 11,
        0x0 : 12, 0x8 : 13, 0x6 : 14, 0x1 : 15
    }

    def load_tile_types(tile_size):
        image_files = os.listdir("Images/Tiles")
        counter = 0
        for image_file_name in image_files:
            has_collision : bool = False
            name = image_file_name.replace(".png", "")
            image_file = pygame.image.load("Images/Tiles/" + image_file_name).convert_alpha()
            if image_file.get_height() // 4 != tile_size:
                has_collision = True
            tile_type = Tilemap.Tile(image_file, name, has_collision)
            Tilemap.tile_types[counter] = tile_type
            counter += 1

    def slice_tile_texture(source : Surface):
        variations : List[Surface] = []
        tile_size = [source.width // 4, source.height // 4]
        for y in range(4):
            for x in range(4):
                variation = Surface((tile_size[0], tile_size[1]), pygame.SRCALPHA).convert_alpha()
                variation.blit(source, (0, 0), Rect(x * tile_size[0], y * tile_size[1], tile_size[0], tile_size[1])) 
                variations.append(variation)
        return variations
    
    class Chunk:
        def __init__(self, width : int, height : int, tile_width : int, tile_height : int):
            self.surface : Surface = Surface((width * tile_width, height * tile_height), pygame.SRCALPHA).convert_alpha()
            self.width = width
            self.height = height
            self.is_empty : bool = True
        
    class Tile:
        def __init__(self, source_img : Surface, name : str, has_collision : bool):
            self.variations : List[Surface] = Tilemap.slice_tile_texture(source_img)
            self.has_collision = has_collision
            self.name = name
        
        def __str__(self):
            collision_str : str = ", a floor tile."
            if self.has_collision:
                collision_str = ", a wall tile."
            return self.name + collision_str

    tile_types : Dict[int, Tile] = {}

    def __init__(self, chunk_size : int = 8, tile_size : int = 16):
        self.tiles : Dict[Vector2, int] = {}
        self.floor_chunks : Dict[Vector2,  Tilemap.Chunk] = {}
        self.wall_chunks : Dict[Vector2, Tilemap.Chunk] = {}
        self.ceiling_chunks : Dict[Vector2, Tilemap.Chunk] = {}
        self.chunk_size = chunk_size
        self.tile_size = tile_size

        if len(Tilemap.tile_types) == 0:
            Tilemap.load_tile_types(tile_size)
    
    def tile_to_world(self, tile_pos : Vector2) -> Vector2:
        '''Returns the world position of the top-left of the tile at a given tile position.'''
        return tile_pos * self.tile_size
    
    def world_to_tile(self, world_pos : Vector2) -> Vector2:
        '''Returns the tile position of the tile containing a given world position.'''
        tile_pos = Vector2(world_pos.x // self.tile_size, world_pos.y // self.tile_size)
        return tile_pos

    def get_tile(self, tile_pos : Vector2) -> int:
        '''Returns the id of the tile at a given tile position, -1 Corresponds to an empty tile.'''
        if tile_pos not in self.tiles:
            return -1
        return self.tiles[tile_pos]
    
    def get_tile_type(self, tile_pos : Vector2) -> Tile:
        '''Returns the tile data of the tile at a given tile position, returns None if no tile exists there.'''
        id:int = self.get_tile(tile_pos)
        if id == -1:
            return None
        return Tilemap.tile_types[id]

    def set_tile(self, tile_pos : Vector2, id : int):
        '''Sets the tile at the given tile position to the new tile type indicated by id, use -1 to remove tiles.'''
        #Set the tile
        self.tiles[tile_pos] = id
        tile_type = Tilemap.tile_types[id]

        chunks : Set[Vector2] = set()

        #Floor tiles (chunks are chunk_size by chunk_size tiles)
        chunks = {Vector2((tile_pos.x - 1)// self.chunk_size, tile_pos.y - 1), 
                  Vector2(tile_pos.x // self.chunk_size, tile_pos.y - 1),
                  Vector2((tile_pos.x + 1)// self.chunk_size, tile_pos.y - 1),
                  Vector2((tile_pos.x - 1)// self.chunk_size, tile_pos.y), 
                  Vector2(tile_pos.x // self.chunk_size, tile_pos.y),
                  Vector2((tile_pos.x + 1)// self.chunk_size, tile_pos.y),
                  Vector2((tile_pos.x - 1)// self.chunk_size, tile_pos.y + 1), 
                  Vector2(tile_pos.x // self.chunk_size, tile_pos.y + 1),
                  Vector2((tile_pos.x + 1)// self.chunk_size, tile_pos.y + 1)}

        #Update all adjacent chunk images the tile belongs to
        #Wall chunks
        for chunk_pos in chunks:
            if chunk_pos not in self.wall_chunks:
                if id == -1:
                    continue #We were removing a tile that was in an ungenerated chunk. No action needed.
                if chunk_pos != Vector2(tile_pos.x // self.chunk_size, tile_pos.y):
                    continue #The chunk doesn't need to be updated
                #Otherwise, generate a new chunk
                self.wall_chunks[chunk_pos] = Tilemap.Chunk(self.chunk_size, 1, self.tile_size, tile_type.variations[0].get_height())
            #Update the chunks' images
            self.update_wall_chunk(chunk_pos, self.wall_chunks[chunk_pos])

            #Check to see if the chunk still has any tiles in it, if not, remove it
            if self.wall_chunks[chunk_pos].is_empty:
                self.wall_chunks.pop(chunk_pos)

        chunks = {Vector2(tile_pos.x // self.chunk_size, tile_pos.y // self.chunk_size), 
                  Vector2((tile_pos.x - 1)// self.chunk_size, tile_pos.y // self.chunk_size),
                  Vector2(tile_pos.x // self.chunk_size, (tile_pos.y - 1) // self.chunk_size),
                  Vector2((tile_pos.x - 1)// self.chunk_size, (tile_pos.y - 1) // self.chunk_size)}

        #Floor tiles
        for chunk_pos in chunks:
            if chunk_pos not in self.floor_chunks:
                if id == -1:
                    continue #We were removing a tile that was in an ungenerated chunk. No action needed.
                #Otherwise, generate a new chunk
                self.floor_chunks[chunk_pos] = Tilemap.Chunk(self.chunk_size, self.chunk_size, self.tile_size, self.tile_size)
            #Update the chunks' images
            self.update_chunk(chunk_pos, self.floor_chunks[chunk_pos])

            #Check to see if the chunk still has any tiles in it, if not, remove it
            if self.floor_chunks[chunk_pos].is_empty:
                self.floor_chunks.pop(chunk_pos)

    def update_wall_chunk(self, chunk_pos : Vector2, chunk : Chunk):
        #Find the correct size for the chunk
        max_height = chunk.surface.get_height()
        for vert_y in range(chunk_pos.y * chunk.height, (chunk_pos.y + 1) * chunk.height):
            for vert_x in range(chunk_pos.x * chunk.width - 1, (chunk_pos.x + 1) * chunk.width + 1):
                tile_type = self.get_tile_type(Vector2(vert_x, vert_y))
                if tile_type == None:
                    continue
                height = tile_type.variations[0].get_height()
                if height > max_height:
                    max_height = height
        chunk.surface = Surface((chunk.surface.get_width(), max_height), pygame.SRCALPHA).convert_alpha()
        #chunk.surface.fill((255 * (1 - chunk_pos.y % 2), 0, 255 * (chunk_pos.y % 2), 100))

        chunk.is_empty = True
        
        for x in range(chunk.width):
            tile_type = self.get_tile(Vector2(chunk_pos.x * self.chunk_size + x, chunk_pos.y))
            if tile_type == -1 or not Tilemap.tile_types[tile_type].has_collision:
                continue
            tile_surface : Surface = Surface(Tilemap.tile_types[tile_type].variations[0].get_size(), pygame.SRCALPHA).convert_alpha()
            surf_altered = False
            #For each vertex of chunk
            for vert_y in range(2):
                for vert_x in range(2):
                    tile_bitmap : int = 0x0
                    #Build the tile image based on the neighboring tiles
                    #Topleft Tile
                    tile_pos = Vector2(chunk_pos.x * chunk.width, chunk_pos.y * chunk.height) + Vector2(vert_x + x - 1, vert_y - 1)
                    tile = self.get_tile(tile_pos)
                    if tile == tile_type:
                        tile_bitmap |= 0x1

                    #Topright Tile
                    tile_pos = Vector2(chunk_pos.x * chunk.width, chunk_pos.y * chunk.height) + Vector2(vert_x + x, vert_y - 1)
                    tile = self.get_tile(tile_pos)
                    if tile == tile_type:
                        tile_bitmap |= 0x2

                    #Bottomleft Tile
                    tile_pos = Vector2(chunk_pos.x * chunk.width, chunk_pos.y * chunk.height) + Vector2(vert_x + x - 1, vert_y)
                    tile = self.get_tile(tile_pos)
                    if tile == tile_type:
                        tile_bitmap |= 0x4
                    
                    #Bottomright Tile
                    tile_pos = Vector2(chunk_pos.x * chunk.width, chunk_pos.y * chunk.height) + Vector2(vert_x + x, vert_y)
                    tile = self.get_tile(tile_pos)
                    if tile == tile_type:
                        tile_bitmap |= 0x8

                    if tile_bitmap == 0:
                        continue
                    surf_altered = surf_altered or True
                    tile_texture = Tilemap.tile_types[tile_type].variations[Tilemap.TILE_BITMAPS[tile_bitmap]]
                    tile_surface.blit(tile_texture, ((vert_x - 0.5) * self.tile_size, (vert_y - 0.5) * self.tile_size))
            if surf_altered:
                chunk.is_empty = chunk.is_empty and False
                chunk.surface.blit(tile_surface, (x * self.tile_size, chunk.surface.get_height() - tile_texture.get_height()))

    def update_chunk(self, chunk_pos : Vector2, chunk : Chunk, is_wall = False):
        #Determine the new height of the chunk
        if is_wall:
            max_height = chunk.surface.get_height()
            for y in range(chunk_pos.y * chunk.height, (chunk_pos.y + 1) * chunk.height):
                for x in range(chunk_pos.x * chunk.width - 1, (chunk_pos.x + 1) * chunk.width + 1):
                    tile_type = self.get_tile_type(Vector2(x, y))
                    if tile_type == None:
                        continue
                    height = tile_type.variations[0].get_height()
                    if height > max_height:
                        max_height = height
            chunk.surface = Surface((chunk.surface.get_width(), max_height), pygame.SRCALPHA).convert_alpha()
            chunk.surface.fill((255 * (1 - chunk_pos.y % 2), 0, 255 * (chunk_pos.y % 2), 100))
        else:
            chunk.surface.fill((0, 0, 0, 0))
        
        chunk.is_empty = True
        for tile_type in range(len(Tilemap.tile_types)):
            if (is_wall and not Tilemap.tile_types[tile_type].has_collision or 
                not is_wall and Tilemap.tile_types[tile_type].has_collision):
                continue

            for y in range(chunk.height):
                for x in range(chunk.width):
                    tile_bitmap : int = 0x0
                    #Topleft Tile
                    tile_pos = Vector2(chunk_pos.x * chunk.width, chunk_pos.y * chunk.height) + Vector2(x, y)
                    tile = self.get_tile(tile_pos)
                    if tile == tile_type:
                        tile_bitmap |= 0x1

                    #Topright Tile
                    tile_pos = Vector2(chunk_pos.x * chunk.width, chunk_pos.y * chunk.height) + Vector2(x + 1, y)
                    tile = self.get_tile(tile_pos)
                    if tile == tile_type:
                        tile_bitmap |= 0x2

                    #Bottomleft Tile
                    tile_pos = Vector2(chunk_pos.x * chunk.width, chunk_pos.y * chunk.height) + Vector2(x, y + 1)
                    tile = self.get_tile(tile_pos)
                    if tile == tile_type:
                        tile_bitmap |= 0x4
                    
                    #Bottomright Tile
                    tile_pos = Vector2(chunk_pos.x * chunk.width, chunk_pos.y * chunk.height) + Vector2(x + 1, y + 1)
                    tile = self.get_tile(tile_pos)
                    if tile == tile_type:
                        tile_bitmap |= 0x8

                    if tile_bitmap == 0:
                        continue
                    chunk.is_empty = chunk.is_empty and False
                    tile_surface = Tilemap.tile_types[tile_type].variations[Tilemap.TILE_BITMAPS[tile_bitmap]]
                    if is_wall:
                        chunk.surface.blit(tile_surface, (x * self.tile_size, y * self.tile_size + chunk.surface.get_height() - tile_surface.get_height()))
                    else:
                        chunk.surface.blit(tile_surface, (x * self.tile_size, y * self.tile_size))

    def draw(self, camera : Camera):
        for x in range(-1, 4):
            for y in range(-1, 4):
                tile_pos = Vector2(x * self.chunk_size, y * self.chunk_size)
                chunk_pos = Vector2(x, y)
                #Draw the floors
                if chunk_pos not in self.floor_chunks:
                    continue
                position = self.tile_to_world(tile_pos + Vector2(0.5, 0.5))
                camera.add_to_unsorted(self.floor_chunks[chunk_pos].surface, position.x, position.y)

        for x in range(-1, 4):
            for y in range(-1, 4):
                tile_pos = Vector2(x * self.chunk_size, y * self.chunk_size)
                chunk_pos = Vector2(x, y)
                #Draw the walls
                for row in range(0, self.chunk_size):
                    if Vector2(chunk_pos.x, tile_pos.y + row) not in self.wall_chunks:
                        continue
                    chunk_surface = self.wall_chunks[Vector2(chunk_pos.x, tile_pos.y + row)].surface
                    draw_position = self.tile_to_world(tile_pos + Vector2(0, row))
                    draw_position.y -= (chunk_surface.get_height() - self.tile_size)
                    camera.add_to_sorted(chunk_surface, draw_position.x, draw_position.y, chunk_surface.get_height())