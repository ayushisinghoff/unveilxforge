import os
import torch
import torch.nn as nn

from torch.utils.data import DataLoader, random_split, ConcatDataset
from torchvision import datasets, transforms, models


DATASET_PATH = "dataset"
BATCH_SIZE = 16
EPOCHS = 10
LEARNING_RATE = 0.0001


DOCUMENT_TYPES = [
    "passport",
    "visa",
    "national_id",
    "driving_license"
]


# Image preprocessing + augmentation
train_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomRotation(3),
    transforms.RandomHorizontalFlip(),
    transforms.ColorJitter(
        brightness=0.2,
        contrast=0.2
    ),
    transforms.ToTensor(),
    transforms.Normalize(
        [0.485, 0.456, 0.406],
        [0.229, 0.224, 0.225]
    )
])


# Load all document types
datasets_list = []

for doc_type in DOCUMENT_TYPES:

    path = os.path.join(
        DATASET_PATH,
        doc_type
    )

    data = datasets.ImageFolder(
        path,
        transform=train_transform
    )

    print(
        doc_type,
        "->",
        data.classes,
        "->",
        len(data),
        "images"
    )

    datasets_list.append(data)


# Combine datasets
full_dataset = ConcatDataset(datasets_list)

print()
print("Total images:", len(full_dataset))


# Split dataset
train_size = int(0.8 * len(full_dataset))
validation_size = len(full_dataset) - train_size

train_data, validation_data = random_split(
    full_dataset,
    [train_size, validation_size]
)


train_loader = DataLoader(
    train_data,
    batch_size=BATCH_SIZE,
    shuffle=True
)

validation_loader = DataLoader(
    validation_data,
    batch_size=BATCH_SIZE,
    shuffle=False
)


# Load ResNet18
model = models.resnet18(
    weights=models.ResNet18_Weights.DEFAULT
)


# Freeze earlier layers
for parameter in model.parameters():
    parameter.requires_grad = False


# Allow final ResNet block to learn
for parameter in model.layer4.parameters():
    parameter.requires_grad = True


# Replace classifier
model.fc = nn.Linear(
    model.fc.in_features,
    2
)


# Device
device = torch.device(
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)

print()
print("Using device:", device)

model = model.to(device)


# Loss + optimizer
criterion = nn.CrossEntropyLoss()

optimizer = torch.optim.Adam(
    filter(
        lambda p: p.requires_grad,
        model.parameters()
    ),
    lr=LEARNING_RATE
)


# Training
print()
print("Starting training...")
print()


for epoch in range(EPOCHS):

    model.train()

    correct = 0
    total = 0
    loss_total = 0

    for images, labels in train_loader:

        images = images.to(device)
        labels = labels.to(device)

        optimizer.zero_grad()

        outputs = model(images)

        loss = criterion(
            outputs,
            labels
        )

        loss.backward()

        optimizer.step()

        loss_total += loss.item()

        predictions = outputs.argmax(
            dim=1
        )

        total += labels.size(0)

        correct += (
            predictions == labels
        ).sum().item()


    train_accuracy = (
        correct / total * 100
    )


    # Validation
    model.eval()

    correct = 0
    total = 0

    with torch.no_grad():

        for images, labels in validation_loader:

            images = images.to(device)
            labels = labels.to(device)

            outputs = model(images)

            predictions = outputs.argmax(
                dim=1
            )

            total += labels.size(0)

            correct += (
                predictions == labels
            ).sum().item()


    validation_accuracy = (
        correct / total * 100
    )


    print(
        f"Epoch {epoch + 1}/{EPOCHS} | "
        f"Loss: {loss_total:.3f} | "
        f"Train: {train_accuracy:.2f}% | "
        f"Validation: {validation_accuracy:.2f}%"
    )


# Save model
os.makedirs(
    "model",
    exist_ok=True
)

torch.save(
    model.state_dict(),
    "model/tampering_model.pth"
)

print()
print("==============================")
print("Training complete!")
print("Model saved successfully.")
print("==============================")