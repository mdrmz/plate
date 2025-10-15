import cv2
import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.utils import to_categorical
import matplotlib.pyplot as plt

print("TensorFlow versiyonu:", tf.__version__)

# --- 1. VERİ SETİNİ YÜKLEME VE ÖN İŞLEME ---
DATA_DIR = "veri_seti/"
IMAGE_SIZE = (32, 32)
data = []
labels_text = []

if not os.path.exists(DATA_DIR) or not os.listdir(DATA_DIR):
    print(f"HATA: '{DATA_DIR}' klasörü boş veya bulunamadı!")
    print("Lütfen bir önceki adımda karakterleri bu klasöre kaydettiğinizden emin olun.")
    exit()

print("Veri seti yükleniyor...")
for folder_name in os.listdir(DATA_DIR):
    folder_path = os.path.join(DATA_DIR, folder_name)
    if not os.path.isdir(folder_path): continue

    for filename in os.listdir(folder_path):
        img_path = os.path.join(folder_path, filename)
        try:
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            img = cv2.resize(img, IMAGE_SIZE)
            data.append(img)
            labels_text.append(folder_name)
        except Exception as e:
            print(f"Hata: {img_path} - {e}")

# Veriyi ve etiketleri modelin anlayacağı formata dönüştür
data = np.array(data, dtype="float") / 255.0
data = np.expand_dims(data, axis=-1)
le = LabelEncoder()
labels = le.fit_transform(labels_text)
labels = to_categorical(labels)
(X_train, X_test, y_train, y_test) = train_test_split(data, labels, test_size=0.20, random_state=42)
print(f"Veri seti yüklendi. {len(X_train)} eğitim, {len(X_test)} test örneği bulundu.")
print(f"Toplam {len(le.classes_)} farklı karakter tespit edildi: {le.classes_}")

# --- 2. VERİ ARTIRMA (DATA AUGMENTATION) ---
aug = ImageDataGenerator(
    rotation_range=10,
    zoom_range=0.1,
    width_shift_range=0.1,
    height_shift_range=0.1,
)

# --- 3. CNN MODELİNİ OLUŞTURMA ---
num_classes = len(le.classes_)
model = Sequential([
    Conv2D(32, (3, 3), padding="same", activation="relu", input_shape=(IMAGE_SIZE[0], IMAGE_SIZE[1], 1)),
    MaxPooling2D(pool_size=(2, 2)),
    Dropout(0.25),
    Conv2D(64, (3, 3), padding="same", activation="relu"),
    MaxPooling2D(pool_size=(2, 2)),
    Dropout(0.25),
    Flatten(),
    Dense(256, activation="relu"),
    Dropout(0.5),
    Dense(num_classes, activation="softmax")
])
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
model.summary()

# --- 4. ERKEN DURDURMA (EARLY STOPPING) ---
early_stopping = EarlyStopping(monitor='val_loss', patience=5, verbose=1, restore_best_weights=True)

# --- 5. MODELİ EĞİTME ---
print("\nDayanıklı Model Eğitimi Başlatılıyor...")
history = model.fit(
    aug.flow(X_train, y_train, batch_size=32),
    validation_data=(X_test, y_test),
    epochs=150,  # Yüksek epoch sayısı, EarlyStopping en iyisini bulup durduracak
    callbacks=[early_stopping],
    verbose=1
)

# --- 6. MODELİ KAYDETME ---
print("\nEğitim Tamamlandı. En iyi model kaydediliyor...")
model.save("plaka_ocr_model_v2.h5")
np.save('etiketler_v2.npy', le.classes_)
print("Model 'plaka_ocr_model_v2.h5' ve etiketler 'etiketler_v2.npy' olarak kaydedildi.")