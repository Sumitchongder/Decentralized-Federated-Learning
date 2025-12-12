import torch

def fed_avg(updates: list):
    """
    Federated averaging of client weight updates
    updates: list of state_dict dictionaries from clients
    """
    avg_update = {}
    for k in updates[0].keys():
        avg_update[k] = sum([u[k] for u in updates]) / len(updates)
    return avg_update
