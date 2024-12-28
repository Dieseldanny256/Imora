from pygame import Surface, Rect
from typing import List, Dict, Set
from vector import Vector2
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
            name = image_file_name.replace(".png", "")
            image_file = pygame.image.load("Images/Tiles/" + image_file_name).convert_alpha()
            tile_type = Tilemap.Tile(image_file, name, tile_size, 0, False)
            Tilemap.tile_types[counter] = tile_type
            counter += 1

    def slice_tile_texture(source : Surface, tile_width : int, tile_height : int):
        variations : List[Surface] = []
        tile_counts = [source.get_size()[0] // tile_width, source.get_size()[1] // tile_height]
        for y in range(tile_counts[1]):
            for x in range(tile_counts[0]):
                variation = Surface((tile_width, tile_height), pygame.SRCALPHA).convert_alpha()
                variation.blit(source, (0, 0), Rect(x * tile_width, y * tile_height, tile_width, tile_height)) 
                variations.append(variation)
        return variations
    
    class Chunk:
        def __init__(self, width : int, height : int, tile_size : int):
            self.surface : Surface = Surface((width * tile_size, height * tile_size), pygame.SRCALPHA).convert_alpha()
            self.width = width
            self.height = height
            self.is_empty : bool = True
        
    class Tile:
        def __init__(self, source_img : Surface, name : str, tile_size : int, height : int, has_collision : bool):
            self.variations : List[Surface] = Tilemap.slice_tile_texture(source_img, tile_size, tile_size + height)
            self.has_collision = has_collision
            self.name = name

    tile_types : Dict[int, Tile] = {}

    def __init__(self, chunk_size : int = 8, tile_size : int = 16):
        self.tiles : Dict[Vector2, int] = {}
        self.floor_chunks : Dict[Vector2,  Tilemap.Chunk] = {}
        self.wall_chunks : Dict[Vector2, Tilemap.Chunk] = {}
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

        #Update all adjacent chunk images the tile belongs to
        chunks : Set[Vector2] = {
            Vector2(tile_pos.x // self.chunk_size, tile_pos.y // self.chunk_size),
            Vector2((tile_pos.x - 1)// self.chunk_size, tile_pos.y // self.chunk_size),
            Vector2(tile_pos.x // self.chunk_size, (tile_pos.y - 1) // self.chunk_size),
            Vector2((tile_pos.x - 1)// self.chunk_size, (tile_pos.y - 1) // self.chunk_size)
        }
        
        for chunk_pos in chunks:
            if chunk_pos not in self.floor_chunks:
                if id == -1:
                    return #We were removing a tile that was in an ungenerated chunk. No action needed.
                #Otherwise, generate a new chunk
                self.floor_chunks[chunk_pos] = Tilemap.Chunk(self.chunk_size, self.chunk_size, self.tile_size)
            #Update the chunks' images
            self.update_chunk(chunk_pos, self.floor_chunks[chunk_pos])

            #Check to see if the chunk still has any tiles in it, if not, remove it
            if self.floor_chunks[chunk_pos].is_empty:
                self.floor_chunks.pop(chunk_pos)

    def update_chunk(self, chunk_pos : Vector2, chunk : Chunk):
        chunk.surface.fill((0, 0, 0, 0))
        chunk.is_empty = True
        for tile_type in range(len(Tilemap.tile_types)):
            for y in range(chunk.width):
                for x in range(chunk.height):
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
                    chunk.surface.blit(tile_surface, (x * self.tile_size, y * self.tile_size))

    def draw(self, dest : Surface):
        for x in range(-1, 4):
            for y in range(-1, 4):
                tile_pos = Vector2(x * self.chunk_size, y * self.chunk_size)
                chunk_pos = Vector2(x, y)
                #Draw the floors
                if chunk_pos not in self.floor_chunks:
                    continue
                dest.blit(self.floor_chunks[chunk_pos].surface, self.tile_to_world(tile_pos + Vector2(0.5, 0.5)).to_tuple())

                #TODO: Draw the walls