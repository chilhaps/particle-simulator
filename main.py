# Example file showing a circle moving on screen
import pygame
import pygame.locals
import pygame_widgets
import sim as sm

from pygame_widgets.slider import Slider
from pygame_widgets.textbox import TextBox

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

dt = 0
click_radius = 5

volume_length = 25
volume_width = 25
particle_size = 1
particle_spacing = 2
gravity_force = -9.81
top_bound = 0
bottom_bound = 720
left_bound = 0
right_bound = 1280
use_random_points = True
origin = [screen.get_width() / 2, screen.get_height() / 2]

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

slider = Slider(screen, 80, 80, 360, 40, min=-20, max=20, step=0.1, handleColour=(255,255,255))
output = TextBox(screen, 80, 160, 200, 25, fontSize=12)

def update():
    # fill the screen with a color to wipe away anything from last frame
    screen.fill("black")

    particles = simulation.get_positions()

    for p in particles:
        pygame.draw.circle(screen, "blue", pygame.Vector2(p[0], p[1]), particle_size)

    mouse_coords = pygame.mouse.get_pos()
    pygame.draw.circle(screen, "white", pygame.Vector2(mouse_coords), click_radius, width=1)


    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        pass
    
    output.setText('Gravity: {}'.format(str(slider.getValue())[:4]))
    simulation.set_gravity(slider.getValue())
    pygame_widgets.update(events)

    # flip() the display to put your work on screen
    pygame.display.flip()
    
    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    global dt 
    dt = clock.tick(60) / 1000

    if pygame.mouse.get_pressed()[0]:
        simulation.click_react(20, mouse_coords, click_radius, dt)

def fixed_update():
    simulation.sim_step(dt)

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.locals.MOUSEWHEEL:
            click_radius += event.y
    
    

    update()
    fixed_update()

pygame.quit()