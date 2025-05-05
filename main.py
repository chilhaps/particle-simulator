# Example file showing a circle moving on screen
import pygame
import pygame_widgets
import fluid_sim as fs

from pygame_widgets.slider import Slider
from pygame_widgets.textbox import TextBox

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

slider = Slider(screen, 100, 100, 800, 40, min=0, max=20, step=0.1)
slider_val = TextBox(screen, 80, 200, 200, 50, fontSize=12)
slider_val.disable()

density_output = TextBox(screen, 80, 249, 200, 50, fontSize=12)
density_output.disable()

dt = 0

volume_length = 50
volume_width = 50
particle_size = 1
particle_spacing = 3
smoothing_radius = 10
gravity_force = 0
top_bound = 720
bottom_bound = -720
left_bound = 0
right_bound = 720
origin = [screen.get_width() / 2, screen.get_height() / 2]

simulation = fs.FluidSim(volume_length, 
                         volume_width, 
                         particle_size, 
                         particle_spacing,
                         smoothing_radius,
                         gravity_force, 
                         top_bound, 
                         bottom_bound, 
                         left_bound, 
                         right_bound, 
                         origin)

def update():
    # fill the screen with a color to wipe away anything from last frame
    screen.fill("black")

    particles = simulation.get_positions()

    for p in particles:
        pygame.draw.circle(screen, "blue", pygame.Vector2(p[0], p[1]), particle_size)

    densities = simulation.get_densities()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        pass
    
    density_output.setText(str(densities.tolist()[1275]))
    slider_val.setText(str(slider.getValue()))
    
    simulation.set_smoothing_radius(slider.getValue())
    pygame.draw.circle(screen, "white", particles.tolist()[1275], slider.getValue(), 1)

    pygame_widgets.update(events)

    # flip() the display to put your work on screen
    pygame.display.flip()
    
    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    global dt 
    dt = clock.tick(60) / 1000

def fixed_update():
    simulation.sim_step(dt)

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False

    update()
    fixed_update()

pygame.quit()