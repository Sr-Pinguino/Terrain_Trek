"""
This module contains the configuration of the graphical and visual elements of the program,
including music and other effects. It allows customization of the user experience.
"""

# Imports the necessary modules and libraries
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import pygame
import random

# HD window configuration with integer values
def screen_config():
    window.fullscreen = False
    window.size = (1920, 1080)
    window.title = "Terrain Trek v0.1"
    window.icon = "assets/TerrainTrek.ico"
    window.development_mode = False
    window.fps_counter.enabled = False
    window.exit_button.enabled = False
    window.collider_counter.enabled = False
    window.entity_counter.enabled = False
    window.cog_button.enabled = False
    window.show_cursor = False
    mouse.locked = True

# SplashScreen class to handle the welcome screen
class SplashScreen(Entity):
    def __init__(self, **kwargs):
        super().__init__(parent=camera.ui, **kwargs)
        self.splash_texture = kwargs.get("texture", None)
        self.fade_duration = kwargs.get("fade_duration", 1)
        self.display_duration = kwargs.get("display_duration", 3)
        self.create_splash()

    def create_splash(self):
        self.image = Entity(
            parent=self,
            model="quad",
            texture=self.splash_texture,
            scale=(1.778, 1),
            z=-1
        )
        self.image.fade_in(self.fade_duration)
        invoke(self.start_fade_out, delay=self.display_duration)

    def start_fade_out(self):
        self.image.fade_out(self.fade_duration)
        invoke(self.disable, delay=self.fade_duration)

# Creates a sphere slightly smaller than the water size to prevent leaving the environment
def create_invisible_wall(size, terrain_scale, water_level):
    invisible_wall = Entity(
        position=((size * terrain_scale) / 2, water_level, (size * terrain_scale) / 2),
        scale=((size * terrain_scale) * 1.45, (size * terrain_scale) * 1.45, (size * terrain_scale) * 1.45),
        model="sphere",
        collider="mesh",
        visible=False,
        double_sided=False
    )
    return invisible_wall

# Create the first-person camera by redefining the base class FirstPersonController
class CustomFirstPersonController(FirstPersonController):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Assign key events
        self.volume = 1.0
        self.is_paused = False

    def update(self):
        super().update()
        if held_keys["escape"]:
            application.quit() # Add functionality to close the program when pressing Escape

        # Volume control and pause
        if held_keys["1"]:
            self.adjust_volume(-0.1)
        if held_keys["2"]:
            self.toggle_pause()
        if held_keys["3"]:
            self.adjust_volume(0.1)

    def adjust_volume(self, amount):
        self.volume = clamp(self.volume + amount, 0, 1)
        pygame.mixer.music.set_volume(self.volume)
        print(f"Volume: {self.volume}")

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            pygame.mixer.music.pause()
        else:
            pygame.mixer.music.unpause()
        print(f"Paused: {self.is_paused}")

def debug_cam():
    EditorCamera()
    print("Editor camera mode for debug")

# Music playback
def play_random_music():
    pygame.mixer.init()
    pygame.mixer.music.set_volume(0.15)
    playlist = [
        "Terrain_Treck/assets/music/documentary-background.mp3",
        "Terrain_Treck/assets/music/folk-acoustic.mp3",
        "Terrain_Treck/assets/music/for-a-dream-lofi-vibes.mp3",
        "Terrain_Treck/assets/music/rain-outside-your-window.mp3",
        "Terrain_Treck/assets/music/video-game-liquid-drum-and-bass.mp3"
    ]
    random.shuffle(playlist)
    for track in playlist:
        pygame.mixer.music.load(track)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
