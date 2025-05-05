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

        self.sim_init()

    def sim_init(self):
        self.positions = torch.zeros(self.vol_width * self.vol_length, 2)
        self.velocities = torch.zeros_like(self.positions)
        self.densities = torch.zeros(self.vol_width * self.vol_length)
        self.pressure_forces = torch.zeros_like(self.positions)

        idx = 0

        for i in range(0, self.vol_length):
            for j in range(0, self.vol_width):
                pos = [self.origin[0] + i * (self.particle_size + self.particle_spacing), self.origin[1] + j * (self.particle_size + self.particle_spacing)]
                self.positions[idx][0], self.positions[idx][1] = pos[0], pos[1]
                idx += 1

    def sim_step(self, dt):
        # Initialize simulation variables
        down = torch.Tensor([0, -1])
        collision_damping = 0.75
        mass = 1
        target_density = 0.06
        pressure_multiplier = 1

        def smoothing_kernel(radius, distance):
            volume = torch.pi * (radius ** 8) / 4
            values = torch.clamp((radius ** 2 - distance ** 2), min=0)
            return (values ** 3) / volume
        
        def smoothing_kernel_derivative(radius, distance):
            f = radius ** 2 - distance ** 2
            scale = -24 / (torch.pi * radius ** 8)
            return torch.clamp((scale * distance * f ** 2), min=0)
        
        def calculate_densities():
            distances = torch.cdist(self.positions, self.positions)
            influences = torch.sum(smoothing_kernel(self.smoothing_radius, distances), 1)
            return influences * mass

        def densities_to_pressure(densities):
            density_error = densities - target_density
            pressure = density_error * pressure_multiplier
            return pressure
        
        def calculate_pressure_force():
            pass

        # Calculate change in velocity due to gravitational force
        self.velocities += down * self.grav_force * dt

        # Check for collisions with bounding box
        # TODO: Find less naive implementation
        for i in range(0, len(self.positions)):
            if not self.left_bound < self.positions[i][0] < self.right_bound:
                self.velocities[i][0] *= (-1 * collision_damping)

            if not self.bottom_bound < self.positions[i][1] < self.top_bound:
                self.velocities[i][1] *= (-1 * collision_damping)

        # Add velocity to positions
        self.positions += self.velocities

        # Calculate densities (may separate into function if needed)
        self.densities = calculate_densities()
        
        # Could be used to track temerature of sim: print(torch.linalg.norm(self.velocities))

    def get_positions(self):
        return self.positions
    
    def get_densities(self):
        return self.densities
    
    def set_smoothing_radius(self, smoothing_radius):
        self.smoothing_radius = smoothing_radius