from torch.utils.data import DataLoader, Dataset

class ClientDatasetWrapper:
    """
    Wrap a PyTorch Dataset to optionally sample subsets for client training.
    """
    def __init__(self, dataset: Dataset, batch_size=32, shuffle=True, sample_size=None):
        if sample_size:
            self.dataset = torch.utils.data.Subset(dataset, range(sample_size))
        else:
            self.dataset = dataset
        self.loader = DataLoader(self.dataset, batch_size=batch_size, shuffle=shuffle)

    def get_loader(self):
        return self.loader
