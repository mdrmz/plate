import cv2
import os
import matplotlib.pyplot as plt
import numpy as np
import pytesseract
from core_engine.plate_detector import PlateDetector

os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

# --- Tesseract Kurulum Ayarları ---
# Lütfen Tesseract'ı kurduğun yolu kendi bilgisayarına göre güncelle!
try:
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    print("Tesseract yolu başarıyla tanımlandı.")
except Exception as e:
    print(f"HATA: Tesseract yolu bulunamadı! Lütfen yolu kontrol edin. Hata: {e}")
    exit()

# --- Görüntü ve Model Yolları ---
ModelPath = 'C:/Users/Win11/PycharmProjects/Plate/plate2/best.pt'
img_path = 'C:/Users/Win11/PycharmProjects/Plate/plate2/data/4.jpg'  # Test etmek istediğin resmin yolu

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

# --- 2. KARAKTER AYRIŞTIRMA VE TESSERACT İLE OKUMA ---

H, W = buyuk_plaka.shape[:2]
cizim_plaka = buyuk_plaka.copy()
bulunan_karakterler_ve_konumlari = []

print("\nKarakterler Tesseract ile okunuyor...")
for i, c in enumerate(cnt):
    rect = cv2.minAreaRect(c)
    (x_center, y_center), (w, h), angle = rect

    # Karakter olabilecek konturları filtrele
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

        # Tesseract ile karakteri oku
        if kirpilmis_karakter.size > 0:
            config = "--psm 10 -c tessedit_char_whitelist=0123456789ABCDEFGHKLMNPRSTUVZ"
            okunan_karakter = pytesseract.image_to_string(kirpilmis_karakter, config=config).strip()
            print(f"Kontur #{i + 1} için Tesseract sonucu: '{okunan_karakter}'")

            if len(okunan_karakter) == 1:
                bulunan_karakterler_ve_konumlari.append((minx, okunan_karakter))

# --- 3. SONUÇLARI GÖSTERME ---

# Karakterleri soldan sağa doğru sırala ve plaka metnini oluştur
bulunan_karakterler_ve_konumlari.sort(key=lambda x: x[0])
plaka_metni = "".join([karakter for kon, karakter in bulunan_karakterler_ve_konumlari])

print("-" * 30)
print(f"✅ Tespit Edilen Nihai Plaka Metni: {plaka_metni}")
print("-" * 30)

# Okunan metni resmin üzerine yaz
sonuc_resmi = cizim_plaka.copy()
cv2.putText(sonuc_resmi, plaka_metni, (20, H - 20), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)

# Sonucu ekranda göster
plt.figure(figsize=(12, 6))
plt.title(f"Okunan Plaka: {plaka_metni}")
plt.imshow(cv2.cvtColor(sonuc_resmi, cv2.COLOR_BGR2RGB))
plt.axis('off')
plt.show()