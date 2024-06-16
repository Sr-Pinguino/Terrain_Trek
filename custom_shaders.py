"""
This module manages the different Shaders needed for terrain textures.
"""

from ursina import *

# Shader to blend 3 textures based on terrain height
"""
Shader Explanation:
smoothstep: A smoothing function that takes three parameters: the two edges of the transition (edge0 and edge1) and the variable to interpolate (x). It returns a value smoothly interpolated between 0 and 1.
texture1: Texture for low heights.
texture2: Texture for mid heights.
texture3: Texture for high heights.
blend1: Interpolation between textures 1 and 2 based on height between 0 and 2 units.
blend2: Interpolation between textures 2 and 3 based on height between 2 and 4 units.
"""
def apply_terrain_shader(terrain_entity, planet_assets):
    terrain_shader = Shader(
        name='triplanar_shader', language=Shader.GLSL,
        vertex='''
        #version 140
        uniform mat4 p3d_ModelViewProjectionMatrix;
        uniform mat4 p3d_ModelMatrix;
        in vec2 p3d_MultiTexCoord0;
        in vec4 p3d_Vertex;
        in vec3 p3d_Normal;
        in vec4 p3d_Color;
        out vec3 world_normal;
        out vec3 vertex_world_position;
        out vec2 texcoord;
        out vec4 vertex_color;

        void main() {
          gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
          texcoord = p3d_MultiTexCoord0;

          world_normal = normalize(mat3(p3d_ModelMatrix) * p3d_Normal);
          vertex_world_position = (p3d_ModelMatrix * p3d_Vertex).xyz;
          vertex_color = p3d_Color;
        }
        ''',

        fragment='''
        #version 140

        uniform vec4 p3d_ColorScale;
        in vec2 texcoord;
        out vec4 fragColor;

        uniform sampler2D texture1;
        uniform sampler2D texture2;
        uniform sampler2D texture3;
        in vec3 world_normal;
        in vec3 vertex_world_position;

        uniform vec2 texture_scale;
        uniform vec2 side_texture_scale;

        in vec4 vertex_color;

        // Function to calculate smooth transitions between textures
        float smoothstep(float edge0, float edge1, float x) {
            x = clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0);
            return x * x * (3.0 - 2.0 * x);
        }

        void main() {
            // Get the vertex height in the world
            float height = vertex_world_position.y;

            // Read the textures
            vec4 color1 = texture(texture1, texcoord);
            vec4 color2 = texture(texture2, texcoord);
            vec4 color3 = texture(texture3, texcoord);

            // DEBUG Modify the transition heights
            float blend1 = smoothstep(1.0, 2.5, height);
            float blend2 = smoothstep(13.0, 18.0, height);

            // Mix the textures based on heights
            vec4 mixed_color = mix(color1, color2, blend1);
            mixed_color = mix(mixed_color, color3, blend2);

            fragColor = mixed_color * vertex_color;
        }
        ''',
        geometry='',
        default_input={
            'texture_scale': Vec2(1, 1),
            'texture1': load_texture(planet_assets["textures"]["texture_low"]),
            'texture2': load_texture(planet_assets["textures"]["texture_mid"]),
            'texture3': load_texture(planet_assets["textures"]["texture_top"]),
        }
    )

    terrain_entity.shader = terrain_shader
    terrain_entity.set_shader_input("texture1", load_texture(planet_assets["textures"]["texture_low"]))
    terrain_entity.set_shader_input("texture2", load_texture(planet_assets["textures"]["texture_mid"]))
    terrain_entity.set_shader_input("texture3", load_texture(planet_assets["textures"]["texture_top"]))

# Water Shaders
"""
SHADER EARTH
Base Water Color: vec3(0, 0.2, 0.7)
    Hex: #0033B3
Main Light: vec3(light1) * 0.4 (dynamic, based on noise)
Additional Lights: vec3(1, 1, 1)
    Hex: #FFFFFF
"""
def apply_water_shader_earth(water):
    # Define the shader with the water effect and defined colors.
    water_shader = Shader(fragment='''
    #version 430
    vec3 permute(vec3 x) { return mod(((x*34.0)+1.0)*x, 289.0); }
    float snoise(vec2 v){
        const vec4 C = vec4(0.211324865405187, 0.366025403784439,
                -0.577350269189626, 0.024390243902439);
        vec2 i  = floor(v + dot(v, C.yy) );
        vec2 x0 = v -   i + dot(i, C.xx);
        vec2 i1;
        i1 = (x0.x > x0.y) ? vec2(1.0, 0.0) : vec2(0.0, 1.0);
        vec4 x12 = x0.xyxy + C.xxzz;
        x12.xy -= i1;
        i = mod(i, 289.0);
        vec3 p = permute( permute( i.y + vec3(0.0, i1.y, 1.0 ))
        + i.x + vec3(0.0, i1.x, 1.0 ));
        vec3 m = max(0.5 - vec3(dot(x0,x0), dot(x12.xy,x12.xy),
            dot(x12.zw,x12.zw)), 0.0);
        m = m*m ;
        m = m*m ;
        vec3 x = 2.0 * fract(p * C.www) - 1.0;
        vec3 h = abs(x) - 0.5;
        vec3 ox = floor(x + 0.5);
        vec3 a0 = x - ox;
        m *= 1.79284291400159 - 0.85373472095314 * ( a0*a0 + h*h );
        vec3 g;
        g.x  = a0.x  * x0.x  + h.x  * x0.y;
        g.yz = a0.yz * x12.xz + h.yz * x12.yw;
        return 130.0 * dot(m, g);
    }

    in vec2 uv;
    uniform sampler2D p3d_Texture0;
    uniform float iTime;
    uniform float resolution;
    uniform float distorsion;
    out vec4 fragColor;
    void main()
    {
        float offset = snoise(uv*resolution+iTime*0.2)*distorsion;
        vec4 color = texture(p3d_Texture0, uv+vec2(offset));
        float light1 = snoise(uv*resolution+iTime*0.2);
        vec3 col = mix(vec3(0,0.2,0.7),vec3(light1)*0.4,0.5);
        float light2 = snoise(uv*resolution-iTime*0.04);
        col += mix(vec3(1,1,1),vec3(light2)*0.2,0.8);
        float brightness = col.x + col.y + col.z;
        float threshold = 0.8;
        if (brightness > 2*threshold){
            col = vec3(1);
        }
        color = mix(vec4(col,1),color,0.4);
        fragColor = color;
    }''')

    water.shader = water_shader  
    water.set_shader_input("iTime", 0) 
    water.set_shader_input("resolution", 90) 
    water.set_shader_input("distorsion", 0.02) 
    return water

"""
SHADER MARS
Base Water Color: (vec3(0.75, 0.79, 0.45))
    Hex: #bfc974 
Main Light: vec3(light1) * 0.4 (dynamic, based on noise)
Additional Lights: vec3(1, 0.8, 0.5)
    Hex: #FFCC80
"""
def apply_water_shader_mars(water):
    water_shader = Shader(fragment='''
    #version 430

    vec3 permute(vec3 x) { return mod(((x*34.0)+1.0)*x, 289.0); }
    float snoise(vec2 v){
        const vec4 C = vec4(0.211324865405187, 0.366025403784439,
                -0.577350269189626, 0.024390243902439);
        vec2 i  = floor(v + dot(v, C.yy) );
        vec2 x0 = v -   i + dot(i, C.xx);
        vec2 i1;
        i1 = (x0.x > x0.y) ? vec2(1.0, 0.0) : vec2(0.0, 1.0);
        vec4 x12 = x0.xyxy + C.xxzz;
        x12.xy -= i1;
        i = mod(i, 289.0);
        vec3 p = permute( permute( i.y + vec3(0.0, i1.y, 1.0 ))
        + i.x + vec3(0.0, i1.x, 1.0 ));
        vec3 m = max(0.5 - vec3(dot(x0,x0), dot(x12.xy,x12.xy),
            dot(x12.zw,x12.zw)), 0.0);
        m = m*m ;
        m = m*m ;
        vec3 x = 2.0 * fract(p * C.www) - 1.0;
        vec3 h = abs(x) - 0.5;
        vec3 ox = floor(x + 0.5);
        vec3 a0 = x - ox;
        m *= 1.79284291400159 - 0.85373472095314 * ( a0*a0 + h*h );
        vec3 g;
        g.x  = a0.x  * x0.x  + h.x  * x0.y;
        g.yz = a0.yz * x12.xz + h.yz * x12.yw;
        return 130.0 * dot(m, g);
    }

    in vec2 uv;
    uniform sampler2D p3d_Texture0;
    uniform float iTime;
    uniform float resolution;
    uniform float distorsion;
    out vec4 fragColor;
    void main()
    {
        float offset = snoise(uv*resolution+iTime*0.2)*distorsion;
        vec4 color = texture(p3d_Texture0, uv+vec2(offset));
        float light1 = snoise(uv*resolution+iTime*0.2);
        vec3 col = mix(vec3(0.75,0.79,0.45),vec3(light1)*0.4,0.5);
        float light2 = snoise(uv*resolution-iTime*0.04);
        col += mix(vec3(1,0.8,0.5),vec3(light2)*0.2,0.8);
        float brightness = col.x + col.y + col.z;
        float threshold = 0.8;
        if (brightness > 2*threshold){
            col = vec3(1);
        }
        color = mix(vec4(col,1),color,0.4);
        fragColor = color;
    }''')

    water.shader = water_shader
    water.set_shader_input("iTime", 0) 
    water.set_shader_input("resolution", 90) 
    water.set_shader_input("distorsion", 0.02) 
    return water

"""
VENUS SHADER
Base Water Color: (vec3(0.59, 0.82, 0.39))
    Hex: #97d264 
Main Light: vec3(light1) * 0.4 (dynamic, based on noise)
Additional Lights: (vec3(0.01, 0.56, 0.65))
    Hex: #028ea5 
"""
def apply_water_shader_venus(water):
    water_shader = Shader(fragment='''
    #version 430

    vec3 permute(vec3 x) { return mod(((x*34.0)+1.0)*x, 289.0); }
    float snoise(vec2 v){
        const vec4 C = vec4(0.211324865405187, 0.366025403784439,
                -0.577350269189626, 0.024390243902439);
        vec2 i  = floor(v + dot(v, C.yy) );
        vec2 x0 = v -   i + dot(i, C.xx);
        vec2 i1;
        i1 = (x0.x > x0.y) ? vec2(1.0, 0.0) : vec2(0.0, 1.0);
        vec4 x12 = x0.xyxy + C.xxzz;
        x12.xy -= i1;
        i = mod(i, 289.0);
        vec3 p = permute( permute( i.y + vec3(0.0, i1.y, 1.0 ))
        + i.x + vec3(0.0, i1.x, 1.0 ));
        vec3 m = max(0.5 - vec3(dot(x0,x0), dot(x12.xy,x12.xy),
            dot(x12.zw,x12.zw)), 0.0);
        m = m*m ;
        m = m*m ;
        vec3 x = 2.0 * fract(p * C.www) - 1.0;
        vec3 h = abs(x) - 0.5;
        vec3 ox = floor(x + 0.5);
        vec3 a0 = x - ox;
        m *= 1.79284291400159 - 0.85373472095314 * ( a0*a0 + h*h );
        vec3 g;
        g.x  = a0.x  * x0.x  + h.x  * x0.y;
        g.yz = a0.yz * x12.xz + h.yz * x12.yw;
        return 130.0 * dot(m, g);
    }

    in vec2 uv;
    uniform sampler2D p3d_Texture0;
    uniform float iTime;
    uniform float resolution;
    uniform float distorsion;
    out vec4 fragColor;
    void main()
    {
        float offset = snoise(uv*resolution+iTime*0.2)*distorsion;
        vec4 color = texture(p3d_Texture0, uv+vec2(offset));
        float light1 = snoise(uv*resolution+iTime*0.2);
        vec3 col = mix(vec3(0.59, 0.82, 0.39), vec3(light1*0.8, light1*0.5, 0.3), 0.5);
        float light2 = snoise(uv*resolution-iTime*0.04);
        col += mix(vec3(0.01, 0.56, 0.65), vec3(light2)*0.2, 0.8);
        float brightness = col.x + col.y + col.z;
        float threshold = 0.8;
        if (brightness > 2*threshold){
            col = vec3(1);
        }
        color = mix(vec4(col,1),color,0.4);
        // Output to screen
        fragColor = color;
    }''')
    water.shader = water_shader  
    water.set_shader_input("iTime", 0) 
    water.set_shader_input("resolution", 90)
    water.set_shader_input("distorsion", 0.02) 
    return water
