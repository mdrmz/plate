import cv2
import os
import matplotlib.pyplot as plt
from core_engine.plate_detector import PlateDetector
os.environ['KMP_DUPLICATE_LIB_OK']='TRUE'
# Model ve resim yollarını tanımla
ModelPath = 'C:/Users/Win11/PycharmProjects/Plate/plate2/best.pt'
img_path = 'C:/Users/Win11/PycharmProjects/Plate/plate2/data/10.jpg'

# Plaka tespit nesnesini oluştur
detector = PlateDetector(ModelPath)
plate_coords=detector.detect(img_path)
image = cv2.imread(img_path)
original_image = image.copy()
if plate_coords:
        # Birden fazla plaka bulunma ihtimaline karşı döngü kullanmak en iyisidir
        for box in plate_coords:
                # Koordinatları tam sayıya çevir
                x1, y1, x2, y2 = int(box[0]), int(box[1]), int(box[2]), int(box[3])
                kirpilan_plaka = original_image[y1:y2, x1:x2]
                # Resmin üzerine dikdörtgeni çiz
                # cv2.rectangle(resim, başlangıç_noktası, bitiş_noktası, renk, kalınlık)
                cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 3)
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
plt.figure(figsize=(10, 8)) # Gösterilecek pencerenin boyutunu ayarlar
plt.imshow(kirpilan_plaka)
plt.title('Tespit Edilen Plaka')
plt.axis('off') # Eksenleri gizle
plt.show()