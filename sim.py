import random
import torch
import torchvision

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
        # Initialize simulation tensors
        self.positions = torch.zeros(self.vol_width * self.vol_length, 2)
        self.velocities = torch.zeros_like(self.positions)
        self.down = torch.Tensor([0, -1])
        self.boxes = torch.zeros(len(self.positions), 4)

        # Precompute window area
        self.env_area = torchvision.ops.box_area(torch.tensor([self.left_bound, self.top_bound, self.right_bound, self.bottom_bound]).unsqueeze(0))

        # Calculate initial particle positions
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

    def calculate_collision_mask(self):
        mask = torch.zeros_like(self.velocities)

        # Top-right boxes
        self.boxes[:, 0] = self.positions[:, 0]
        self.boxes[:, 1] = self.top_bound
        self.boxes[:, 2] = self.right_bound
        self.boxes[:, 3] = self.positions[:, 1]

        A1 = torchvision.ops.box_area(self.boxes).unsqueeze(0).transpose(0, 1)

        # Top-left boxes
        self.boxes[:, 0] = self.left_bound
        self.boxes[:, 1] = self.top_bound
        self.boxes[:, 2] = self.positions[:, 0]
        self.boxes[:, 3] = self.positions[:, 1]

        A2 = torchvision.ops.box_area(self.boxes).unsqueeze(0).transpose(0, 1)

        # Bottom-left boxes
        self.boxes[:, 0] = self.left_bound
        self.boxes[:, 1] = self.positions[:, 1]
        self.boxes[:, 2] = self.positions[:, 0]
        self.boxes[:, 3] = self.bottom_bound

        A3 = torchvision.ops.box_area(self.boxes).unsqueeze(0).transpose(0, 1)

        # Bottom-right boxes
        self.boxes[:, 0] = self.positions[:, 0]
        self.boxes[:, 1] = self.positions[:, 1]
        self.boxes[:, 2] = self.right_bound
        self.boxes[:, 3] = self.bottom_bound

        A4 = torchvision.ops.box_area(self.boxes).unsqueeze(0).transpose(0, 1)

        top_mask = torch.where((A3 + A4 - self.env_area) > 0, -1, 0).expand(self.velocities.shape).clone()
        top_mask[:, 0] = 0

        bottom_mask = torch.where((A1 + A2 - self.env_area) > 0, -1, 0).expand(self.velocities.shape).clone()
        bottom_mask[:, 0] = 0

        left_mask = torch.where((A1 + A4 - self.env_area) > 0, -1, 0).expand(self.velocities.shape).clone()
        left_mask[:, 1] = 0

        right_mask = torch.where((A2 + A3 - self.env_area) > 0, -1, 0).expand(self.velocities.shape).clone()
        right_mask[:, 1] = 0

        mask += torch.clamp(top_mask + bottom_mask + left_mask + right_mask, min=-1)

        return mask

    def gaussian(self, tensor, p, sigma = 1):
        squared_distance = torch.abs(tensor - p)**2
        return torch.exp(-squared_distance / (2 * sigma**2))

    def sim_step(self, dt):
        # Initialize simulation variables
        collision_damping = 0.75
        mass = 1

        # Apply gravity
        self.velocities += self.down * self.grav_force * dt

        # Resolve collisions
        collision_mask = self.calculate_collision_mask() * collision_damping
        collision_mask = torch.where(collision_mask == 0, 1, collision_mask)
        self.velocities *= collision_mask
        self.positions = torch.clamp(self.positions, min=torch.tensor([self.left_bound, self.top_bound]), max=torch.tensor([self.right_bound, self.bottom_bound]))
        
        # Iterative collision detection (slow!!!)
        '''
        for i in (range(0, len(self.positions))):
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
        '''

        # Update positions
        self.positions += self.velocities

    def click_react(self, force, pos, radius, dt):
        pos = torch.Tensor(pos)
        distances = torch.pairwise_distance(self.positions, pos)
        distance_scalars = self.gaussian(distances, radius / 2, radius / 2)
        directions = (self.positions - pos) / torch.linalg.norm(self.positions - pos)

        self.velocities += distance_scalars.unsqueeze(1) * directions * force * dt

        # Iterative approach (slow!!!)
        '''
        for i in range(0, len(self.positions)):
            distance = torch.dist(self.positions[i], pos)
            direction = (self.positions[i] - pos) / torch.linalg.norm(self.positions[i] - pos)

            if distance <= radius:
                self.velocities[i] += direction * force * reaction_force_scalar * dt
        '''

    def get_positions(self):
        return self.positions
    
    def get_sample_box_coords(self):
        idx = random.randint(0, len(self.boxes))
        return self.boxes[idx]
    
    def set_gravity(self, gravity):
        self.grav_force = gravity