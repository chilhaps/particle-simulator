import random
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
                 use_random_points = False, 
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
        self.use_random_points = use_random_points
        self.origin = origin

        self.sim_init()

    def sim_init(self):
        self.positions = torch.zeros(self.vol_width * self.vol_length, 2)
        self.velocities = torch.zeros_like(self.positions)
        self.densities = torch.zeros(self.vol_width * self.vol_length)
        self.pressure_forces = torch.zeros_like(self.positions)

        idx = 0

        if self.use_random_points:
            for i in range(0, len(self.positions)):
                self.positions[i][0] = random.randint(self.left_bound, self.right_bound)
                self.positions[i][1] = random.randint(self.bottom_bound, self.top_bound)
        else:
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

        def density_to_pressure(density):
            density_error = density - target_density
            pressure = density_error * pressure_multiplier
            return pressure
        
        def calculate_pressure_forces_beta(idx):
            for i in range(0, len(self.positions)):
                if i == idx: continue

                offset = self.positions[i] - self.positions[idx]
                distance = torch.linalg.norm(offset)

                if distance == 0:
                    offset = self.positions[random.randint(0, len(self.positions))] - self.positions[idx]
                    distance = torch.linalg.norm(offset)
                
                direction = offset / distance

                slope = smoothing_kernel_derivative(self.smoothing_radius, distance)
                density = self.densities[i]
                self.pressure_forces[i] += -density_to_pressure(density) * direction * slope * mass / density
                

        # Apply gravity
        self.velocities += down * self.grav_force * dt

        # Calculate densities
        self.densities = calculate_densities()

        # Calculate and apply pressure forces
        # for i in range(0, len(self.positions)):
        #    calculate_pressure_forces_beta(i)
        
        # pressure_acceleration = self.pressure_forces.view(2, len(self.densities)) / self.densities
        # self.velocities += pressure_acceleration.view(len(self.velocities), 2) * dt

        # Resolve collisions with bounding box
        for i in range(0, len(self.positions)):
            if self.positions[i][0] < self.left_bound:
                self.positions[i][0] = self.left_bound
                self.velocities[i][0] *= (-1 * collision_damping)

            if self.positions[i][0] > self.right_bound:
                self.positions[i][0] = self.right_bound
                self.velocities[i][0] *= (-1 * collision_damping)

            if self.positions[i][1] < self.bottom_bound:
                self.positions[i][1] = self.bottom_bound
                self.velocities[i][1] *= (-1 * collision_damping)

            if self.positions[i][1] > self.top_bound:
                self.positions[i][1] = self.top_bound
                self.velocities[i][1] *= (-1 * collision_damping)

        # Update positions
        self.positions += self.velocities

        # Could be used to track temperature of sim: print(torch.linalg.norm(self.velocities))

    def get_positions(self):
        return self.positions
    
    def get_densities(self):
        return self.densities
    
    def set_smoothing_radius(self, smoothing_radius):
        self.smoothing_radius = smoothing_radius