import torch
import torch.nn as nn

volumes = []

def get_volumes():
    return volumes

def create_volume(length, width, origin, particle_size, particle_spacing):
    volumes.append(torch.zeros(width, length, 2))

    for i in range(0, len(volumes[0])):
        for j in range(0, i):
            volumes[0] = origin + [i * (particle_size + particle_spacing), j * (particle_size + particle_spacing)]