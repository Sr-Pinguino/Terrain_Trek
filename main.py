"""
This module is the main entry point of the program. Here, the modules are initialized,
the execution environment is configured, and the main program loop is started.
"""

# Import the necessary modules and libraries
from ursina import *  # Importing the Ursina library
import time  # Importing necessary for using time.time() and animating shaders
from threading import Thread  # For playing music in a separate thread
import random  # Import random

# Import the rest of the modules necessary to run the program
import program_settings
import custom_shaders
import procedural_terrain

# Dictionaries and lists with all the references used
# Earth model
earth_assets = {
    "textures": {
        "texture_low": "assets/text/earth_txt_low.png",
        "texture_mid": "assets/text/earth_txt_mid.png",
        "texture_top": "assets/text/earth_txt_top.png"
    },
    "shader": "earth_shader",
    "tree_models": {
        "low": [
            {"model": "assets/3D_models/earth_tree01_low.obj", "scale": (0.025, 0.025, 0.025), "collider": "box"},
            {"model": "assets/3D_models/earth_tree02_low.obj", "scale": (0.025, 0.025, 0.025), "collider": "box"},
        ],
        "med": [
            {"model": "assets/3D_models/earth_tree01_mid.obj", "scale": (0.025, 0.025, 0.025), "collider": "box"},
            {"model": "assets/3D_models/earth_tree02_mid.obj", "scale": (0.025, 0.025, 0.025), "collider": "box"},
        ],
        "top": [
            {"model": "assets/3D_models/earth_tree01_top.obj", "scale": (0.025, 0.025, 0.025), "collider": "box"},
            {"model": "assets/3D_models/earth_tree02_top.obj", "scale": (0.025, 0.025, 0.025), "collider": "box"},
        ]
    }
}

# Mars model
mars_assets = {
    "textures": {
        "texture_low": "assets/text/mars_txt_low.png",
        "texture_mid": "assets/text/mars_txt_mid.png",
        "texture_top": "assets/text/mars_txt_top.png"
    },
    "shader": "mars_shader",
    "tree_models": {
        "low": [
            {"model": "assets/3D_models/mars_tree01_low.obj", "scale": (0.025, 0.025, 0.025), "collider": "box"},
            {"model": "assets/3D_models/mars_tree02_low.obj", "scale": (0.025, 0.025, 0.025), "collider": "box"},
        ],
        "med": [
            {"model": "assets/3D_models/mars_tree01_mid.obj", "scale": (0.025, 0.025, 0.025), "collider": "box"},
            {"model": "assets/3D_models/mars_tree02_mid.obj", "scale": (0.025, 0.025, 0.025), "collider": "box"},
        ],
        "top": [
            {"model": "assets/3D_models/mars_tree01_top.obj", "scale": (0.025, 0.025, 0.025), "collider": "box"},
            {"model": "assets/3D_models/mars_tree02_top.obj", "scale": (0.025, 0.025, 0.025), "collider": "box"},
        ]
    }
}

# Venus model
venus_assets = {
    "textures": {
        "texture_low": "assets/text/venus_txt_low.png",
        "texture_mid": "assets/text/venus_txt_mid.png",
        "texture_top": "assets/text/venus_txt_top.png"
    },
    "shader": "venus_shader",
    "tree_models": {
        "low": [
            {"model": "assets/3D_models/venus_tree01_low.obj", "scale": (0.025, 0.025, 0.025), "collider": "box"},
            {"model": "assets/3D_models/venus_tree02_low.obj", "scale": (0.025, 0.025, 0.025), "collider": "box"},
        ],
        "med": [
            {"model": "assets/3D_models/venus_tree01_mid.obj", "scale": (0.025, 0.025, 0.025), "collider": "box"},
            {"model": "assets/3D_models/venus_tree02_mid.obj", "scale": (0.025, 0.025, 0.025), "collider": "box"},
        ],
        "top": [
            {"model": "assets/3D_models/venus_tree01_top.obj", "scale": (0.025, 0.025, 0.025), "collider": "box"},
            {"model": "assets/3D_models/venus_tree02_top.obj", "scale": (0.025, 0.025, 0.025), "collider": "box"},
        ]
    }
}

# Satellites for the sky
satellites_list = [
    "assets/3D_models/satellite_01.obj", "assets/3D_models/satellite_02.obj",
    "assets/3D_models/satellite_03.obj", "assets/3D_models/satellite_04.obj"
]

# Sky backgrounds
sky_texture_list = [
    "assets/text/sky_00.png", "assets/text/sky_01.png",
    "assets/text/sky_02.png", "assets/text/sky_03.png", "assets/text/sky_04.png"
]

# List of different menu options
menu_list = [
    "assets/screens/menu_1.mp4", "assets/screens/menu_2.mp4",
    "assets/screens/menu_3.mp4", "assets/screens/menu_4.mp4"
]

# Called every frame and updates the value of iTime to animate the water shader effect
def update():
    water.set_shader_input("iTime", time.time() - start)  # Updates the time in the water shader to animate the waves

# Definition of the main function
def main():
    global water, start

    # Variables defining the world generation
    size = 100  # Dimension of the terrain map
    noise_scale = 10  # Frequency of the Perlin noise used to generate the height map
    fade_margin = 7  # Number of units affected to fade the edges
    water_level = 0  # Height of the water on the Y axis
    terrain_scale = 5  # Scaling of the world while keeping the number of polygons

    # Terrain elements
    tree_percent = 50  # Inverse percentage, the closer to 0 the more trees

    # Select one of the asset dictionaries randomly
    planet_assets = procedural_terrain.select_planet(earth_assets, mars_assets, venus_assets)

    # Initialization of the Ursina application
    app = Ursina()

    # Configure screen aspects such as resolution and whether it's windowed or full screen
    program_settings.screen_config()

    # Create and display the splash screen
    # The second screen starts earlier to stay in the background
    splash_screen_2 = program_settings.SplashScreen(
        texture=random.choice(menu_list), fade_duration=1, display_duration=18)

    splash_screen_1 = program_settings.SplashScreen(
        texture="assets/screens/splash_screen.png", fade_duration=1, display_duration=5)
    destroy(splash_screen_1, delay=10)  
    destroy(splash_screen_2, delay=25)  

    # Terrain generation
    # Generate the height map
    heightmap = procedural_terrain.generate_heightmap(size, noise_scale)

    # Make the edges fade to go under the water
    heightmap = procedural_terrain.apply_edge_fade(heightmap, fade_margin, water_level)

    # Generate the terrain mesh
    terrain_mesh = procedural_terrain.generate_terrain_mesh(
        size, heightmap, texture_scale=(12 * terrain_scale))

    # Create the terrain entity
    terrain = procedural_terrain.create_terrain_entity(terrain_mesh, terrain_scale)

    # Apply the shader to the terrain
    custom_shaders.apply_terrain_shader(terrain, planet_assets)

    # Water generation
    # Create the flat water entity
    water = procedural_terrain.create_water(size, water_level, terrain_scale)

    # Assign the selected planet's water shader
    if "earth_shader" == planet_assets["shader"]:
        custom_shaders.apply_water_shader_earth(water)
    elif "mars_shader" == planet_assets["shader"]:
        custom_shaders.apply_water_shader_mars(water)
    elif "venus_shader" == planet_assets["shader"]:
        custom_shaders.apply_water_shader_venus(water)

    # Start the timer, necessary to animate the shaders
    start = time.time()

    # Create a sphere that acts as an invisible wall to prevent leaving the water plane
    invisible_wall = program_settings.create_invisible_wall(size, terrain_scale, water_level)

    # Tree generation
    # Generate the noise map for 3D objects
    noise_map = procedural_terrain.generate_noise_map(size, terrain_scale)
    # Assign the selected planet's trees
    tree_models = planet_assets["tree_models"]
    # Generate trees
    placed_trees = procedural_terrain.generate_trees(
        water_level, water, terrain, noise_map, tree_percent, tree_models)

    # Add a sky entity
    # Randomly generate a sky and possibly a satellite
    sky = procedural_terrain.custom_sky(
        size, terrain_scale, water_level, satellites_list, sky_texture_list)

    # Create the first-person controller for the camera
    player_cam = program_settings.CustomFirstPersonController()
    # Select the initial position on the terrain
    player_cam.position = ((size * terrain_scale) / 2, size // 2, (size * terrain_scale) / 2)
    """
    # DEBUG Camera controller in editor mode for debugging. To use it, disable the player camera.
    debug_mode_cam = program_settings.debug_cam()
    """

    # Start playing music in a separate thread to avoid blocking execution
    music_thread = Thread(target=program_settings.play_random_music)
    music_thread.start()

    # Run the application
    app.run()

# Call the main function to start the program
if __name__ == "__main__":
    main()
