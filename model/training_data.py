import pandas as pd
import numpy as np
import tensorflow as tf
import os
import matplotlib.pyplot as plt
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
import pickle

# Folder tempat dataset disimpan
dataset_folder = "dataset"

# Menggabungkan semua file CSV dalam folder
all_files = [os.path.join(dataset_folder, f) for f in os.listdir(dataset_folder) if f.endswith('.csv')]

# Membaca dan menggabungkan semua file menjadi satu DataFrame
dataframes = [pd.read_csv(file) for file in all_files]
data = pd.concat(dataframes, ignore_index=True)

# Pisahkan input (sensor) dan output
drop_columns = ["Waktu"]
X = data.drop(columns=drop_columns + ["Output1", "Output2"]).values
y = data[["Output1", "Output2"]].values

# Normalisasi data
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)

# Simpan scaler untuk digunakan saat prediksi
with open("scaler.pkl", "wb") as f:
    pickle.dump(scaler, f)

# Split data untuk training dan testing
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# Definisi model
model = Sequential([
    Dense(128, activation='relu', input_shape=(X_train.shape[1],)),
    Dense(64, activation='relu'),
    Dense(32, activation='relu'),
    Dense(2, activation='sigmoid')  # 2 output dengan aktivasi sigmoid
])

# Compile model
model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.0005),
              loss='binary_crossentropy',
              metrics=['mae'])

# Training model
history = model.fit(X_train, y_train, epochs=250, batch_size=32, validation_data=(X_test, y_test))

# Evaluasi model
test_loss, test_mae = model.evaluate(X_test, y_test)
print(f'Test Loss: {test_loss}, Test MAE: {test_mae}')

# Simpan model
model.save("nn_model.h5")
print("Model telah disimpan sebagai nn_model.h5")

# Plot grafik loss dan MAE
plt.figure(figsize=(12, 5))

# Plot Loss
plt.subplot(1, 2, 1)
plt.plot(history.history['loss'], label='Train Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.title('Training & Validation Loss')
plt.legend()

# Plot MAE
plt.subplot(1, 2, 2)
plt.plot(history.history['mae'], label='Train MAE')
plt.plot(history.history['val_mae'], label='Validation MAE')
plt.xlabel('Epochs')
plt.ylabel('Mean Absolute Error (MAE)')
plt.title('Training & Validation MAE')
plt.legend()

plt.tight_layout()
plt.show()
