import os
import pandas as pd
from torch.utils.data import Dataset, DataLoader
from PIL import Image
from torchvision import transforms

class HAM10000Dataset(Dataset):
    def __init__(self, csv_file, img_dir, transform=None):
        self.data = pd.read_csv(csv_file)
        self.img_dir = img_dir
        self.transform = transform

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        img_path = os.path.join(self.img_dir, self.data.iloc[idx, 0])
        image = Image.open(img_path).convert("RGB")
        label = int(self.data.iloc[idx, 1])
        if self.transform:
            image = self.transform(image)
        return image, label

def load_ham10000(csv_file, img_dir, batch_size=32):
    transform = transforms.Compose([transforms.Resize((224,224)), transforms.ToTensor()])
    dataset = HAM10000Dataset(csv_file, img_dir, transform)
    return DataLoader(dataset, batch_size=batch_size, shuffle=True)
