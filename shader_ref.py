import pygame
import moderngl
from pygame_render import RenderEngine

# Initialize pygame
pygame.init()

# Initialize render engine
engine = RenderEngine(900, 600)

# Load sprite
sprite = engine.load_texture('resources/sprite.png')

# Create layer and define filter (best practice for pixel art)
layer = engine.make_layer(size=(320, 180))
layer.texture.filter = (moderngl.NEAREST, moderngl.NEAREST)

# Calculate scaling value for layer
scale = engine.screen.size[0] // layer.size[0]

# Initialize shader
shader = engine.load_shader_from_path('shaders/vertex.glsl', 'shaders/fragment.glsl')

# Initialize game loop values
clock = pygame.time.Clock()
total_time = 0
running = True

while running:
    # Tick the clock at 60 frames per second
    clock.tick(60)

    # Game logic here!
    total_time += clock.get_time()
    shader['time'] = total_time

    # Clear screen
    engine.clear(0, 0, 0)

    # Render sprite to layer, then layer to screen
    engine.render(sprite, layer, position=(10, 10))
    engine.render(layer.texture, engine.screen, scale=scale, shader=shader)

    # Flip display
    pygame.display.flip()

    # Process events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
