import torch
import torch.nn as nn

class FluidSim:
    def __init__(self, 
                 vol_length, 
                 vol_width, 
                 particle_size, 
                 particle_spacing, 
                 smoothing_radius, 
                 grav_force, top_bound, 
                 bottom_bound, 
                 left_bound, 
                 right_bound, 
                 origin = [0, 0]):
        
        self.vol_length = vol_length
        self.vol_width = vol_width
        self.particle_size = particle_size
        self.particle_spacing = particle_spacing
        self.smoothing_radius = smoothing_radius
        self.grav_force = grav_force
        self.top_bound = top_bound
        self.bottom_bound = bottom_bound
        self.left_bound = left_bound
        self.right_bound = right_bound
        self.origin = origin

        self.SimInit()

    def SimInit(self):
        self.positions = torch.zeros(self.vol_width * self.vol_length, 2)
        self.velocity = torch.zeros_like(self.positions)
        self.densities = torch.zeros_like(self.positions)

        idx = 0

        for i in range(0, self.vol_length):
            for j in range(0, self.vol_width):
                pos = [self.origin[0] + i * (self.particle_size + self.particle_spacing), self.origin[1] + j * (self.particle_size + self.particle_spacing)]
                self.positions[idx][0], self.positions[idx][1] = pos[0], pos[1]
                idx += 1

    def SimStep(self, dt):
        def SmoothingKernel(radius, distance):
            value = max(0, radius * radius - distance * distance)
            return value ** 3

        def CalculateDensity(sample_point):
            density = 0
            mass = 1
            
            for position in self.positions:
                distance = torch.linalg.norm(position - sample_point).item()
                #print(distance)
                influence = SmoothingKernel(self.smoothing_radius, distance)
                #print(influence)
                density += mass * influence
            
            return density

        # Initialize constants
        down = torch.Tensor([0, -1])
        collision_damping = 0.75

        # Calculate change in velocity due to gravitational force
        self.velocity += down * self.grav_force * dt

        # Check for collisions with bounding box
        # TODO: Find less naive implementation
        for i in range(0, len(self.positions)):
            if not self.left_bound < self.positions[i][0] < self.right_bound:
                self.velocity[i][0] *= (-1 * collision_damping)

            if not self.bottom_bound < self.positions[i][1] < self.top_bound:
                self.velocity[i][1] *= (-1 * collision_damping)

        # Add velocity to positions
        self.positions += self.velocity

        self.densities = CalculateDensity(self.positions[0])
        
        # Could be used to track temerature of sim: print(torch.linalg.norm(self.velocity))

    def GetPositions(self):
        return self.positions
    
    def GetDensities(self):
        return self.densities