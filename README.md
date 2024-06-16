# Terrain Trek v0.1 En

This project implements terrain and water simulation in a three-dimensional environment using Ursina Engine. It includes custom shaders for terrain and water visualization, simulating characteristics of planets like Earth and Mars.

## Features

- **Terrain Generation:** Utilizes a triplanar shader to blend three textures based on terrain height.
- **Water Simulation:** Includes custom shaders to simulate water in environments with distortion effects and dynamic lighting.
- **Interactivity:** Allows exploration and visualization of terrain and water in an interactive environment.

## Requirements

- Python 3.x
- Ursina Engine
- Py game

## Installation

1. Clone the repository:
    ```bash
    git clone [URL del repositorio]
    ```
2. Install dependencies:
    ```bash
    pip install ursina
    ```

## Usage

1. Run the main script:
    ```bash
    python main.py
    ```

2. The script needs to be in a folder named Terrain_Treck to run the music.

## Project Structure

├── assets/
│ ├── 3D_models/
│ │ ├── earth_trees.obj
│ │ ├── earth_trees.mtl
│ │ ├── mars_trees.obj
│ │ ├── mars_trees.mtl
│ │ ├── satellites.obj
│ │ ├── satellites.mtl
│ │ ├── venus_trees.obj
│ │ ├── venus_trees.mtl
│ ├── music/
│ │ ├── credits.txt
│ │ ├── songs.mp3
│ ├── screens/
│ │ ├── splash_screen_1.png
│ │ ├── splash_screen_2.mp4
│ ├── text/
│ │ ├── texture_low.png
│ │ ├── texture_mid.png
│ │ ├── texture_top.png
│ │ ├── sky.png
│ ├── TerrainTrek.ico
├── custom_shaders.py
├── main.py
├── procedural_terrain.py
├── program_settings.py
└── README.md




## Load Time Note

**Note:** The program may take some time to load as it converts all models into Ursina-compatible meshes at the start. We are working on optimizing this process in future updates.

## Shader Explanation

### Terrain Shader

The terrain shader uses a triplanar method to blend three textures based on terrain height. Textures are smoothly interpolated to create realistic transitions between different heights.

- **Low Texture:** Applied to low heights.
- **Mid Texture:** Applied to medium heights.
- **High Texture:** Applied to high heights.

### Water Shader

#### Earth

The water shader for Earth simulates water with a dark blue base color and dynamic light effects.

- **Base Color:** `#0033B3`
- **Main Light:** Based on dynamic noise.
- **Additional Light:** `#FFFFFF`

#### Mars

The water shader for Mars simulates water with a yellowish base color and dynamic light effects.

- **Base Color:** `#bfc974`
- **Main Light:** Based on dynamic noise.
- **Additional Light:** `#FFCC80`

#### Venus

The water shader for Venus simulates water with a reddish base color and dynamic light effects.

- **Base Color:** `#bfc974`
- **Main Light:** Based on dynamic noise.
- **Additional Light:** `#FFCC80`

## Contributions

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/new-functionality`).
3. Make changes and commit (`git commit -am 'Add new functionality'`).
4. Push changes to your repository (`git push origin feature/new-functionality`).
5. Open a Pull Request.

## License

MIT License

Copyright (c) 2024 Guillermo Gregorio

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Authors

- Guillermo Gregorio

## Acknowledgments

- Thanks to Kang for advice and debug sessions.
