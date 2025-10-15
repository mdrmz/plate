# main.py (Ana Çalıştırma Dosyası)

import cv2
from core_engine.lpr_engine import LPREngine
import matplotlib.pyplot as plt
import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE' # BU SATIRI EKLEYİN

# Model ve resim yolunu belirt
ModelPath = 'C:/Users/Win11/PycharmProjects/Plate/plate2/best.pt'
img_path = 'C:/Users/Win11/PycharmProjects/Plate/plate2/data/10.jpg'

# Motoru başlat
engine = LPREngine(detector_model_path=ModelPath)

# Resmi işle
image = cv2.imread(img_path)
results = engine.process_image(image)

print("Tespit Edilen Plakalar:")
# Sonuçları çizdir
for plate_text, (x1, y1, x2, y2) in results:
    print(f"- {plate_text}")
    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
    cv2.putText(image, plate_text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

# Sonucu göster
plt.figure(figsize=(15, 10))
plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
plt.title("Plaka Okuma Sonucu")
plt.axis('off')
plt.show()