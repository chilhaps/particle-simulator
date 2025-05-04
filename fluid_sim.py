import torch
import torch.nn as nn

class FluidSim:
    def __init__(self, vol_length, vol_width, particle_size, particle_spacing, grav_force, top_bound, bottom_bound, left_bound, right_bound, origin = [0, 0]):
        self.vol_length = vol_length
        self.vol_width = vol_width
        self.particle_size = particle_size
        self.particle_spacing = particle_spacing
        self.grav_force = grav_force
        self.top_bound = top_bound
        self.bottom_bound = bottom_bound
        self.left_bound = left_bound
        self.right_bound = right_bound
        self.origin = origin

        self.SimInit()

    def SimInit(self):
        self.positions = torch.zeros(self.vol_width, self.vol_length, 2)
        self.velocity = torch.zeros_like(self.positions)

        for i in range(0, len(self.positions)):
            for j in range(0, len(self.positions[i])):
                pos = [self.origin[0] + i * (self.particle_size + self.particle_spacing), self.origin[1] + j * (self.particle_size + self.particle_spacing)]
                self.positions[i][j][0], self.positions[i][j][1] = pos[0], pos[1]

    def SimStep(self, dt):
        # Initialize constants
        down = torch.Tensor([0, -1])
        collision_damping = 0.75

        # Calculate change in velocity due to gravitational force
        self.velocity += down * self.grav_force * dt

        # Check for collisions with bounding box
        for i in range(0, len(self.positions)):
            for j in range(0, len(self.positions[i])):
                if not self.left_bound < self.positions[i][j][0] < self.right_bound:
                    self.velocity[i][j][0] *= (-1 * collision_damping)

                if not self.bottom_bound < self.positions[i][j][1] < self.top_bound:
                    self.velocity[i][j][1] *= (-1 * collision_damping)

        # Apply velocity to positions
        self.positions += self.velocity
        # print(torch.linalg.norm(self.velocity))

    def GetPositions(self):
        return self.positions