import cv2
import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.preprocessing.image import ImageDataGenerator  # Veri artırma için
from tensorflow.keras.callbacks import EarlyStopping  # Erken durdurma için
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.utils import to_categorical

# 1. VERİ SETİNİ YÜKLEME (Bu kısım aynı)
DATA_DIR = 'karakterseti/'
IMAGE_SIZE = (32, 32)
data = []
labels_text = []

for folder_name in os.listdir(DATA_DIR):
    # ... (Birkaç adım önceki veri yükleme kodunun aynısı) ...
    # ... Bu kısmı önceki eğitim kodundan kopyalayabilirsin ...
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

data = np.array(data, dtype="float") / 255.0
data = np.expand_dims(data, axis=-1)
le = LabelEncoder()
labels = le.fit_transform(labels_text)
labels = to_categorical(labels)
(X_train, X_test, y_train, y_test) = train_test_split(data, labels, test_size=0.20, random_state=42)

# 2. VERİ ARTIRMA (DATA AUGMENTATION) TANIMLAMA
# Eğitim verileri üzerinde rastgele küçük oynamalar yapacak jeneratörü oluştur
aug = ImageDataGenerator(
    rotation_range=10,  # 10 dereceye kadar rastgele döndür
    zoom_range=0.1,  # %10'a kadar rastgele yakınlaştır
    width_shift_range=0.1,  # Genişliğin %10'u kadar rastgele kaydır
    height_shift_range=0.1,  # Yüksekliğin %10'u kadar rastgele kaydır
)

# 3. CNN MODELİNİ OLUŞTURMA (Daha basit ve Dropout'lu bir model)
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

# 4. ERKEN DURDURMA (EARLY STOPPING) TANIMLAMA
# Test (validation) kaybı 5 epoch boyunca iyileşmezse eğitimi durdur ve en iyi ağırlıkları geri yükle
early_stopping = EarlyStopping(monitor='val_loss', patience=5, verbose=1, restore_best_weights=True)

# 5. MODELİ EĞİTME (Veri artırma ve erken durdurma ile)
print("\nGelişmiş Model Eğitimi Başlatılıyor...")
history = model.fit(
    aug.flow(X_train, y_train, batch_size=32),  # Eğitim için 'aug.flow' kullanılıyor
    validation_data=(X_test, y_test),
    epochs=50,  # Yüksek epoch sayısı, EarlyStopping en iyisini bulup durduracak
    callbacks=[early_stopping],  # Callback'i ekle
    verbose=1
)

# 6. MODELİ KAYDETME
print("\nEğitim Tamamlandı. En iyi model kaydediliyor...")
model.save("plaka_ocr_model_v2.h5")
np.save('etiketler_v2.npy', le.classes_)
print("Model 'plaka_ocr_model_v2.h5' olarak kaydedildi.")