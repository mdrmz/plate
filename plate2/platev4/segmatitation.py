import cv2
import os
import matplotlib.pyplot as plt
import numpy as np
from core_engine.plate_detector import PlateDetector

os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

ModelPath = 'C:/Users/Win11/PycharmProjects/Plate/plate2/best.pt'
img_path = 'C:/Users/Win11/PycharmProjects/Plate/plate2/data/4.jpg'


output_dir = "kaydedilen_karakterler"
os.makedirs(output_dir, exist_ok=True)  # Klasör zaten varsa hata vermez



img = cv2.imread(img_path)
img = cv2.resize(img, (640, 640))

detector = PlateDetector(ModelPath)
plate_coords = detector.detect(img)
x1, y1, x2, y2 = plate_coords[0]


plaka_img = img[y1:y2, x1:x2]
buyuk_plaka = cv2.resize(plaka_img, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)


gri_plaka = cv2.cvtColor(buyuk_plaka, cv2.COLOR_BGR2GRAY)


th_img = cv2.adaptiveThreshold(gri_plaka, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 11, 2)


kernel = np.ones((5, 5), np.uint8)
th_img = cv2.morphologyEx(th_img, cv2.MORPH_OPEN, kernel, iterations=1)


cnt = cv2.findContours(th_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnt = cnt[0]
cnt = sorted(cnt, key=cv2.contourArea, reverse=True)[:12]



H, W = buyuk_plaka.shape[:2]
cizim_plaka = buyuk_plaka.copy()
bulunan_karakterler = []


base_filename = os.path.splitext(os.path.basename(img_path))[0]
karakter_sayaci = 0

for c in cnt:
    rect = cv2.minAreaRect(c)
    (x_center, y_center), (w, h), angle = rect

    kon1 = max([w, h]) < W / 4
    kon2 = w * h > 300

    if kon1 and kon2:
        box = cv2.boxPoints(rect)
        box = np.int64(box)
        cv2.drawContours(cizim_plaka, [box], 0, (0, 255, 0), 2)

        minx = np.min(box[:, 0])
        miny = np.min(box[:, 1])
        maxx = np.max(box[:, 0])
        maxy = np.max(box[:, 1])

        kirpilmis_karakter = th_img[miny:maxy, minx:maxx].copy()
        bulunan_karakterler.append((minx, kirpilmis_karakter))


        if kirpilmis_karakter.size > 0:

            dosya_adi = f"{base_filename}_char_{karakter_sayaci}.png"
            kayit_yolu = os.path.join(output_dir, dosya_adi)

            # Resmi kaydet
            cv2.imwrite(kayit_yolu, kirpilmis_karakter)
            karakter_sayaci += 1



plt.figure(figsize=(10, 5))
plt.title("Tespit Edilen Karakterler")
plt.imshow(cv2.cvtColor(cizim_plaka, cv2.COLOR_BGR2RGB))
plt.axis('off')
plt.show()

bulunan_karakterler.sort(key=lambda x: x[0])

plt.figure(figsize=(15, 5))
plt.suptitle("Soldan Sağa Sıralanmış Karakterler")
for i, (x_coord, karakter) in enumerate(bulunan_karakterler):
    if karakter.size > 0:
        plt.subplot(1, len(bulunan_karakterler), i + 1)
        plt.imshow(karakter, cmap='gray')
        plt.axis('off')
plt.show()