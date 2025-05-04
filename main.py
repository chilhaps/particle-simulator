# Example file showing a circle moving on screen
import pygame
import fluid_sim as fs

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

dt = 0

volume_length = 10
volume_width = 10
particle_size = 1
particle_spacing = 1
smoothing_radius = 2
gravity_force = -9.81
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

    # pygame.draw.circle(screen, "blue", circle_pos, 10)

    particles = simulation.GetPositions()

    for p in particles:
        pygame.draw.circle(screen, "blue", pygame.Vector2(p[0], p[1]), particle_size)

    densities = simulation.GetDensities()

    # print(densities)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        pass

    # flip() the display to put your work on screen
    pygame.display.flip()
    
    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    global dt 
    dt = clock.tick(60) / 1000

def fixed_update():
    simulation.SimStep(dt)

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    update()
    fixed_update()

pygame.quit()