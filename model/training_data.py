import pandas as pd
import numpy as np
import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
import pickle
import matplotlib.pyplot as plt

# Folder tempat dataset disimpan
dataset_folder = "dataset"

# Menggabungkan semua file CSV dalam folder
all_files = []
file_name = []

for f in os.listdir(dataset_folder):
    if f.endswith('.csv'):
        filename = os.path.splitext(f)[0]
        file_path = os.path.join(dataset_folder, f)
        file_name.append(filename)

        # Baca file CSV
        df = pd.read_csv(file_path)

        # Tambah kolom dengan nama file, tanpa kasih nama kolom eksplisit
        filename_column = np.full((df.shape[0], 1), filename)  # bikin kolom isian nama file
        df_values_with_filename = np.hstack((df.values, filename_column.reshape(-1, 1)))

        # Buat DataFrame baru dari hasil gabungan
        df_combined = pd.DataFrame(df_values_with_filename)

        all_files.append(df_combined)

# Membaca dan menggabungkan semua file menjadi satu DataFrame
dataframes = [pd.read_csv(file) for file in all_files]
data = pd.concat(dataframes, ignore_index=True)

# Dapatkan class_names otomatis dari file_name (hanya nama unik)
class_names = list(set(file_name))

# Fungsi untuk one-hot encoding
def one_hot_encode(file_name, class_names):
    one_hot_labels = []
    for name in file_name:
        one_hot = [1 if name == class_name else 0 for class_name in class_names]
        one_hot_labels.append(one_hot)
    return np.array(one_hot_labels)

# Pisahkan input (sensor) dan output
X = data.drop(data.columns[0], axis=1).values
y = one_hot_encode(file_name, class_names)

# Normalisasi data
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)

# Simpan scaler untuk digunakan saat prediksi
with open("scaler.pkl", "wb") as f:
    pickle.dump(scaler, f)

# Split data untuk training dan testing
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# Konversi data ke format tensor PyTorch
X_train_tensor = torch.tensor(X_train, dtype=torch.float32)
y_train_tensor = torch.tensor(y_train, dtype=torch.float32)

X_test_tensor = torch.tensor(X_test, dtype=torch.float32)
y_test_tensor = torch.tensor(y_test, dtype=torch.float32)

# Buat DataLoader untuk batch training
train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)

test_dataset = TensorDataset(X_test_tensor, y_test_tensor)
test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)

# Definisikan model menggunakan PyTorch
class NeuralNetwork(nn.Module):
    def __init__(self, input_size, output_size):
        super(NeuralNetwork, self).__init__()
        self.layer1 = nn.Linear(input_size, 128)
        self.layer2 = nn.Linear(128, 64)
        self.layer3 = nn.Linear(64, 32)
        self.output_layer = nn.Linear(32, output_size)
    
    def forward(self, x):
        x = torch.relu(self.layer1(x))
        x = torch.relu(self.layer2(x))
        x = torch.relu(self.layer3(x))
        x = torch.softmax(self.output_layer(x), dim=1)
        return x

# Inisialisasi model
model = NeuralNetwork(X_train.shape[1], len(class_names))

# Loss function dan optimizer
criterion = nn.BCELoss()  # Binary Cross Entropy loss untuk multi-output classification
optimizer = optim.Adam(model.parameters(), lr=0.0005)

# Training loop
num_epochs = 250
train_losses = []
test_losses = []

for epoch in range(num_epochs):
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0
    
    for inputs, labels in train_loader:
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        running_loss += loss.item()

        # Menghitung akurasi
        _, predicted = torch.max(outputs.data, 1)
        _, actual = torch.max(labels.data, 1)
        correct += (predicted == actual).sum().item()
        total += labels.size(0)
    
    # Simpan loss dan akurasi per epoch
    train_losses.append(running_loss / len(train_loader))
    
    # Evaluasi pada data testing
    model.eval()
    test_loss = 0.0
    with torch.no_grad():
        for inputs, labels in test_loader:
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            test_loss += loss.item()

    test_losses.append(test_loss / len(test_loader))

    # Print loss dan akurasi per epoch
    if (epoch+1) % 50 == 0:
        print(f"Epoch [{epoch+1}/{num_epochs}], Loss: {running_loss / len(train_loader):.4f}, Test Loss: {test_loss / len(test_loader):.4f}")

# Evaluasi model
model.eval()
with torch.no_grad():
    y_pred = model(X_test_tensor)
    _, predicted = torch.max(y_pred.data, 1)
    _, actual = torch.max(y_test_tensor.data, 1)
    correct = (predicted == actual).sum().item()
    accuracy = correct / len(y_test_tensor) * 100

print(f"Test Accuracy: {accuracy:.2f}%")

# Simpan model
torch.save(model.state_dict(), "nn_model.pth")
print("Model telah disimpan sebagai nn_model.pth")

# Plot grafik loss
plt.figure(figsize=(12, 5))

# Plot Training Loss
plt.subplot(1, 2, 1)
plt.plot(train_losses, label='Train Loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.title('Training Loss')
plt.legend()

# Plot Test Loss
plt.subplot(1, 2, 2)
plt.plot(test_losses, label='Test Loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.title('Test Loss')
plt.legend()

plt.tight_layout()
plt.show()
