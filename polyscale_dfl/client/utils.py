import torch

def flatten_update(update: dict):
    return torch.cat([v.flatten() for v in update.values()])

def unflatten_update(flattened, template):
    result = {}
    pointer = 0
    for k, v in template.items():
        numel = v.numel()
        result[k] = flattened[pointer:pointer+numel].reshape(v.shape)
        pointer += numel
    return result
