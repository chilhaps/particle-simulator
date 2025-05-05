import random
import torch
import torch.nn as nn

class Sim:
    def __init__(self, 
                 vol_length,
                 vol_width,
                 particle_size,
                 particle_spacing,
                 grav_force,
                 top_bound,
                 bottom_bound,
                 left_bound,
                 right_bound,
                 use_random_points = False,
                 origin = [0, 0]):
        
        self.vol_length = vol_length
        self.vol_width = vol_width
        self.particle_size = particle_size
        self.particle_spacing = particle_spacing
        self.grav_force = grav_force
        self.top_bound = top_bound
        self.bottom_bound = bottom_bound
        self.left_bound = left_bound
        self.right_bound = right_bound
        self.use_random_points = use_random_points
        self.origin = origin

        self.sim_init()

    def sim_init(self):
        self.positions = torch.zeros(self.vol_width * self.vol_length, 2)
        self.velocities = torch.zeros_like(self.positions)
        self.down = torch.Tensor([0, -1])

        idx = 0

        if self.use_random_points:
            for i in range(0, len(self.positions)):
                self.positions[i][0] = random.randint(self.left_bound, self.right_bound)
                self.positions[i][1] = random.randint(self.top_bound, self.bottom_bound)
        else:
            for i in range(0, self.vol_length):
                for j in range(0, self.vol_width):
                    pos = [self.origin[0] + i * (self.particle_size + self.particle_spacing), self.origin[1] + j * (self.particle_size + self.particle_spacing)]
                    self.positions[idx][0], self.positions[idx][1] = pos[0], pos[1]
                    idx += 1

    def sim_step(self, dt):
        # Initialize simulation variables
        collision_damping = 0.75
        mass = 1

        # Apply gravity
        self.velocities += self.down * self.grav_force * dt

        # Resolve collisions
        for i in range(0, len(self.positions)):
            if self.positions[i][0] < self.left_bound:
                self.positions[i][0] = self.left_bound
                self.velocities[i][0] *= (-1 * collision_damping)

            if self.positions[i][0] > self.right_bound:
                self.positions[i][0] = self.right_bound
                self.velocities[i][0] *= (-1 * collision_damping)

            if self.positions[i][1] > self.bottom_bound:
                self.positions[i][1] = self.bottom_bound
                self.velocities[i][1] *= (-1 * collision_damping)

            if self.positions[i][1] < self.top_bound:
                self.positions[i][1] = self.top_bound
                self.velocities[i][1] *= (-1 * collision_damping)

        # Update positions
        self.positions += self.velocities

    def click_react(self, force, pos, radius, dt):
        pos = torch.Tensor(pos)

        for i in range(0, len(self.positions)):
            distance = torch.dist(self.positions[i], pos)
            direction = (self.positions[i] - pos) / torch.linalg.norm(self.positions[i] - pos)

            if distance <= radius:
                self.velocities[i] *= direction * force * dt

    def get_positions(self):
        return self.positions
    
    def set_gravity(self, gravity):
        self.grav_force = gravity