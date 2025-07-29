import pygame
import pygame.locals
import pygame_widgets
import sim as sm

from pygame_widgets.slider import Slider
from pygame_widgets.textbox import TextBox

# Environment variables
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

# Pygame variables
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
running = True
dt = 0

# Input variables
click_radius = 5
clicking = False
mouse_coords = ([0, 0])

# Simulation init values
volume_length = 100
volume_width = 100
particle_size = 1
particle_spacing = 2
gravity_force = -9.81
top_bound = 0
bottom_bound = SCREEN_HEIGHT
left_bound = 0
right_bound = SCREEN_WIDTH
use_random_points = True
origin = [SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2]

# Simulation variables
reaction_force = 200000

# Initialize sim object
simulation = sm.Sim(volume_length, 
                         volume_width, 
                         particle_size, 
                         particle_spacing,
                         gravity_force, 
                         top_bound, 
                         bottom_bound, 
                         left_bound, 
                         right_bound,
                         use_random_points,
                         origin)

# Initialize widget objects
slider = Slider(screen, 80, 80, 360, 40, min=-20, max=20, step=0.1, handleColour=(255,255,255))
output = TextBox(screen, 80, 160, 200, 25, fontSize=12)

def draw_box(box_coords):
    left = min(box_coords[0], box_coords[2]).item()
    top = min(box_coords[1], box_coords[3]).item()
    width = abs(box_coords[0] - box_coords[2]).item()
    height = abs(box_coords[1] - box_coords[3]).item()

    sample_box = pygame.Rect(left, top, width, height)
    pygame.draw.rect(screen, 'red', sample_box, width=1)

def update():
    global dt
    global mouse_coords
    global clicking

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("black")

    particles = simulation.get_positions()

    for p in particles:
        pygame.draw.circle(screen, "blue", pygame.Vector2(p[0], p[1]), particle_size)

    mouse_coords = pygame.mouse.get_pos()
    pygame.draw.circle(screen, "white", pygame.Vector2(mouse_coords), click_radius, width=1)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_r]:
        coords = simulation.get_sample_box_coords()
        draw_box(coords)
    
    output.setText('Gravity: {}'.format(str(slider.getValue())[:4]))
    simulation.set_gravity(slider.getValue())
    pygame_widgets.update(events)

    # flip() the display to put your work on screen
    pygame.display.flip()
    
    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

    if pygame.mouse.get_pressed()[0]:
        clicking = True
    else:
        clicking = False

def fixed_update():
    simulation.sim_step(dt)
    if clicking:
        simulation.click_react(reaction_force, mouse_coords, click_radius, dt)

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.locals.MOUSEWHEEL:
            click_radius += event.y
            if click_radius < 0: click_radius = 0

    update()
    fixed_update()

pygame.quit()
