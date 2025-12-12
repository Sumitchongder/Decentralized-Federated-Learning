from torchvision import datasets, transforms
from torch.utils.data import DataLoader, random_split

def load_cifar(num_clients=2, batch_size=32):
    transform = transforms.Compose([transforms.ToTensor()])
    dataset = datasets.CIFAR10(root="./data", train=True, download=True, transform=transform)
    length = len(dataset) // num_clients
    clients_data = random_split(dataset, [length]*num_clients)
    loaders = [DataLoader(d, batch_size=batch_size, shuffle=True) for d in clients_data]
    test_loader = DataLoader(datasets.CIFAR10(root="./data", train=False, download=True, transform=transform), batch_size=batch_size)
    return loaders, test_loader
