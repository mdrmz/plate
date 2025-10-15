import cv2
import os
import matplotlib.pyplot as plt
import numpy as np
import pytesseract
from core_engine.plate_detector import PlateDetector
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

# --- Tesseract Kurulum Ayarları ---
try:
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    print("Tesseract yolu başarıyla tanımlandı.")
except Exception as e:
    print(f"HATA: Tesseract yolu bulunamadı! Lütfen yolu kontrol edin. Hata: {e}")
    exit()

# --- Görüntü ve Model Yolları ---
ModelPath = 'C:/Users/Win11/PycharmProjects/Plate/plate2/best.pt'
img_path = 'C:/Users/Win11/PycharmProjects/Plate/plate2/data/10.jpg'  # Test etmek istediğin resmin yolu

# --- 1. PLAKA TESPİTİ VE ÖN İŞLEME ---
img = cv2.imread(img_path)
if img is None:
    print(f"HATA: Resim yüklenemedi. Lütfen şu yolu kontrol edin: {img_path}")
    exit()

img_resized = cv2.resize(img, (640, 640))

detector = PlateDetector(ModelPath)
plate_coords = detector.detect(img_resized)

if not plate_coords:
    print("HATA: Resimde plaka tespit edilemedi.")
    exit()

x1, y1, x2, y2 = plate_coords[0]

plaka_img = img_resized[y1:y2, x1:x2]
buyuk_plaka = cv2.resize(plaka_img, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
gri_plaka = cv2.cvtColor(buyuk_plaka, cv2.COLOR_BGR2GRAY)
th_img = cv2.adaptiveThreshold(gri_plaka, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 11, 2)
kernel = np.ones((5, 5), np.uint8)
th_img = cv2.morphologyEx(th_img, cv2.MORPH_OPEN, kernel, iterations=1)
cnt = cv2.findContours(th_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnt = cnt[0]
cnt = sorted(cnt, key=cv2.contourArea, reverse=True)[:15]

# --- 2. GELİŞTİRİLMİŞ KARAKTER AYRIŞTIRMA VE OKUMA ---

H, W = buyuk_plaka.shape[:2]
cizim_plaka = buyuk_plaka.copy()
bulunan_karakterler_ve_konumlari = []

print("\nKarakterler Tesseract için optimize ediliyor ve okunuyor...")
for i, c in enumerate(cnt):
    rect = cv2.minAreaRect(c)
    (x_center, y_center), (w, h), angle = rect

    aspect_ratio = max(w, h) / min(w, h) if min(w, h) > 0 else 0
    kon1 = max([w, h]) < W / 4
    kon2 = w * h > 300
    kon3 = aspect_ratio > 1.3 and aspect_ratio < 4.0

    if kon1 and kon2 and kon3:
        box = cv2.boxPoints(rect)
        box = np.int64(box)
        cv2.drawContours(cizim_plaka, [box], 0, (0, 255, 0), 2)

        minx = np.min(box[:, 0])
        miny = np.min(box[:, 1])
        maxx = np.max(box[:, 0])
        maxy = np.max(box[:, 1])

        kirpilmis_karakter_gri = gri_plaka[miny:maxy, minx:maxx].copy()

        if kirpilmis_karakter_gri.size > 0:
            # --- UZMAN DOKUNUŞU: Karakteri Tesseract için Mükemmelleştirme ---

            # 1. Otsu metodu ile karaktere özel en iyi threshold değerini bul
            _, char_binary = cv2.threshold(kirpilmis_karakter_gri, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            # 2. Tesseract'in sevdiği formata (siyah yazı, beyaz arka plan) getir.
            #    Eğer resmin ortalaması 128'den büyükse (çoğunlukla beyazsa), format doğrudur. Değilse, renkleri ters çevir.
            if np.mean(char_binary) < 128:
                char_binary = cv2.bitwise_not(char_binary)

            # 3. Kenar boşluğu (padding) ekle
            padded_char = cv2.copyMakeBorder(char_binary, 10, 10, 10, 10, cv2.BORDER_CONSTANT, value=[255])
            # ------------------------------------------------------------------

            config = "--psm 10 -c tessedit_char_whitelist=0123456789ABCDEFGHKLMNPRSTUVZ"
            okunan_karakter = pytesseract.image_to_string(padded_char, config=config).strip()
            print(f"Kontur #{i + 1} için Tesseract sonucu: '{okunan_karakter}'")

            if len(okunan_karakter) == 1:
                bulunan_karakterler_ve_konumlari.append((minx, okunan_karakter))

# --- 3. SONUÇLARI GÖSTERME ---
bulunan_karakterler_ve_konumlari.sort(key=lambda x: x[0])
plaka_metni = "".join([karakter for kon, karakter in bulunan_karakterler_ve_konumlari])

print("-" * 30)
print(f"✅ Tespit Edilen Nihai Plaka Metni: {plaka_metni}")
print("-" * 30)

sonuc_resmi = cizim_plaka.copy()
cv2.putText(sonuc_resmi, plaka_metni, (20, H - 20), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)

plt.figure(figsize=(12, 6))
plt.title(f"Okunan Plaka: {plaka_metni}")
plt.imshow(cv2.cvtColor(sonuc_resmi, cv2.COLOR_BGR2RGB))
plt.axis('off')
plt.show()