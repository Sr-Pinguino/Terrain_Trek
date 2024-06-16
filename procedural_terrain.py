"""
This module is responsible for the procedural generation of terrains and map elements.
It uses multiple methods to create varied and dynamic terrains that make up the game world.
"""

from ursina import *
import random
from noise import pnoise2
import numpy as np

# Selects one of the asset dictionaries randomly
def select_planet(earth_assets, mars_assets, venus_assets):
    random_planet_number = random.randint(0, 2)
    if random_planet_number == 0:
        return earth_assets
    elif random_planet_number == 1:
        return mars_assets
    elif random_planet_number == 2:
        return venus_assets

# GROUND
# Generates Perlin noise to be applied to the terrain map to create elevations and depressions
def generate_heightmap(size, noise_scale):
    base = random.randint(0, 75)
    heightmap = np.zeros((size, size))
    for x in range(size):
        for z in range(size):
            heightmap[x][z] = pnoise2(x / noise_scale, z / noise_scale, 
                                      octaves=random.randint(1, 7),
                                      repeatx=size, repeaty=size, base=base)
    return heightmap

# Applies a fade factor on the edges to make them fall below the water level
def apply_edge_fade(heightmap, fade_margin, water_level):
    size = heightmap.shape[0]
    for x in range(size):
        for z in range(size):
            distance_to_edge = min(x, z, size - x - 1, size - z - 1)
            fade_factor = min(1.0, distance_to_edge / fade_margin)
            heightmap[x][z] *= fade_factor

            if distance_to_edge < fade_margin:
                heightmap[x][z] = min(heightmap[x][z], water_level - 0.05)
    return heightmap

# Sets the normals of the 3D model to make them all face outward
def calculate_normals(vertices, triangles):
    normals = [Vec3(0, 0, 0) for _ in range(len(vertices))]
    for i in range(0, len(triangles), 3):
        v1, v2, v3 = triangles[i], triangles[i + 1], triangles[i + 2]
        normal = (vertices[v2] - vertices[v1]).cross(vertices[v3] - vertices[v1]).normalized()
        normals[v1] += normal
        normals[v2] += normal
        normals[v3] += normal
    return [n.normalized() for n in normals]

# Generates the mesh of a plane based on the points created in generate_heightmap and the normalized triangles of calculate_normals
def generate_terrain_mesh(size, heightmap, texture_scale):
    vertices = []
    triangles = []
    uvs = []
    for x in range(size):
        for z in range(size):
            y = heightmap[x][z] * 15
            vertices.append(Vec3(x, y, z))
            uvs.append((x / size * texture_scale, z / size * texture_scale))
            if x < size - 1 and z < size - 1:
                i = x * size + z
                triangles.append(i)
                triangles.append(i + 1)
                triangles.append(i + size)
                triangles.append(i + 1)
                triangles.append(i + size + 1)
                triangles.append(i + size)

    normals = calculate_normals(vertices, triangles)
    mesh = Mesh(vertices=vertices, triangles=triangles, normals=normals, uvs=uvs, mode='triangle')
    return mesh

# Generates the 3D model entity that creates the terrain
def create_terrain_entity(mesh, terrain_scale):
    terrain_entity = Entity(model=mesh, collider='mesh', double_sided=True)
    terrain_entity.scale = (terrain_scale, terrain_scale, terrain_scale)
    terrain_entity.position = (0, ((terrain_scale / 2) // 2), 0)
    return terrain_entity

# WATER
# Creates the flat circular shape to create the water layer
def create_circular_water_mesh(radius, resolution):
    vertices = []
    triangles = []
    for i in range(resolution):
        angle = 2 * np.pi * i / resolution
        x = np.cos(angle) * radius
        z = np.sin(angle) * radius
        vertices.append(Vec3(x, 0, z))
    vertices.append(Vec3(0, 0, 0))
    for i in range(resolution):
        triangles.append(resolution)
        triangles.append(i)
        triangles.append((i + 1) % resolution)
    normals = [Vec3(0, 1, 0) for _ in range(len(vertices))]
    uvs = [(v.x / radius / 2 + 0.5, v.z / radius / 2 + 0.5) for v in vertices]
    mesh = Mesh(vertices=vertices, triangles=triangles, normals=normals, uvs=uvs, mode='triangle')
    return mesh

# Creates the 3D model entity that creates the water
def create_water(size, water_level, terrain_scale):
    radius = size / 2
    resolution = size
    water_mesh = create_circular_water_mesh(radius, resolution)
    water_entity = Entity(model=water_mesh, position=((size * terrain_scale) / 2, water_level, (size * terrain_scale) / 2),
                          scale=(terrain_scale * 1.5, 1, terrain_scale * 1.5), collider='box')
    return water_entity

# TREES AND OBJECTS
# Generates a noise map that is converted to numeric values based on grayscale
def generate_noise_map(size, terrain_scale):
    size_map = size * terrain_scale
    base = random.randint(0, 75)
    noise_map = np.zeros((size_map, size_map))

    for y in range(size_map):
        for x in range(size_map):
            noise_value = pnoise2(x / terrain_scale, y / terrain_scale, base=base)
            noise_map[x][y] = (noise_value + 0.5) / 1.5

    return noise_map

# Places trees on the terrain based on their height
# The maximum is 0.75 out of 1 to leave 25% of the map without objects
def generate_trees(water_level, water_entity, terrain_entity, objects_map, tree_percent, tree_models):
    lower_tree_limit = 0.375
    upper_tree_limit = 0.75
    size = len(objects_map)

    adjust_lower_tree_limit = lower_tree_limit + ((upper_tree_limit - lower_tree_limit) * tree_percent) / 100.0

    placed_positions = set()

    # Checks at the opacity points above the indicated level if the terrain is above water_level
    # If so, places the tree at the height established by the raycast
    for y in range(size):
        for x in range(size):
            if adjust_lower_tree_limit <= objects_map[x][y] <= upper_tree_limit:
                world_position = Vec3(x, 0, y) + terrain_entity.position
                hit_info = raycast(world_position + Vec3(0, 50, 0), Vec3(0, -1, 0), ignore=[water_entity])

                if hit_info.hit and hit_info.world_point.y > water_level:
                    tree_type = None
                    if water_level < hit_info.world_point.y <= 2:
                        tree_type = random.choice(tree_models['low'])
                    elif 2 < hit_info.world_point.y <= 15:
                        tree_type = random.choice(tree_models['med'])
                    elif hit_info.world_point.y > 15:
                        tree_type = random.choice(tree_models['top'])

                    if tree_type and (x, y) not in placed_positions:
                        tree = Entity(
                            model=tree_type['model'],
                            scale=tree_type['scale'],
                            position=hit_info.world_point,
                            collider=tree_type['collider'],
                            rotation=(0, random.randint(0, 360), 0)
                        )
                        placed_positions.add((x, y))
                        mark_surroundings(objects_map, x, y, size)

    return objects_map

# Marks the space where an object has been placed and all its adjacent spaces as 1 to prevent overlapping
def mark_surroundings(objects_map, x, y, size):
    offsets = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    for dx, dy in offsets:
        nx, ny = x + dx, y + dy
        if 0 <= nx < size and 0 <= ny < size:
            objects_map[nx][ny] = 1.0

# Creates a sky by applying a texture to the inside of a sphere and can also generate some satellites
def custom_sky(size, terrain_scale, water_level, satellites_list, sky_texture_list):
    dome_sky = Entity(
        parent=scene,
        model='sphere',
        texture=random.choice(sky_texture_list),
        position=((size * terrain_scale) / 2, water_level, (size * terrain_scale) / 2),
        scale=((size * terrain_scale) * 1.75, (size * terrain_scale) * 1.75, (size * terrain_scale) * 1.75),
        double_sided=True
    )

    # Places a random number of satellites in the sky
    satellites_number = random.randint(0, 2)
    for i in range(satellites_number):
        satellite = Entity(
            model= random.choice(satellites_list),  # The model and texture are selected from the sky_texture list
            scale= random.uniform(0.001, 0.05), 
            position=(random.randint(50, 400), random.randint(150, 200), random.randint(50, 400)),  # Random position of the satellites in X, Y, Z
             double_sided=True
        ) 
