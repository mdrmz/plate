import cv2
import os
import matplotlib.pyplot as plt
import numpy as np
import pytesseract
from core_engine.plate_detector import PlateDetector
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

# --- 1. AYARLAR ---
try:
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    print("Tesseract yolu başarıyla tanımlandı.")
except Exception as e:
    print(f"HATA: Tesseract yolu bulunamadı! Lütfen yolu kontrol edin. Hata: {e}")
    exit()

ModelPath = 'C:/Users/Win11/PycharmProjects/Plate/plate2/best.pt'
img_path = 'C:/Users/Win11/PycharmProjects/Plate/plate2/data/10.jpg'

# --- 2. PLAKA TESPİTİ ---
img = cv2.imread(img_path)
if img is None:
    print(f"HATA: Resim yüklenemedi. Lütfen şu yolu kontrol edin: {img_path}")
    exit()

img_resized = cv2.resize(img, (640, 640))
detector = PlateDetector(ModelPath)
plate_coords = detector.detect(img_resized)
if not plate_coords:
    print("HATA: Bu resimde plaka tespit edilemedi.")
    exit()

x1, y1, x2, y2 = plate_coords[0]
plaka_img = img_resized[y1:y2, x1:x2]
buyuk_plaka = cv2.resize(plaka_img, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
gri_plaka = cv2.cvtColor(buyuk_plaka, cv2.COLOR_BGR2GRAY)
plaka_alani = gri_plaka.shape[0] * gri_plaka.shape[1]

# --- 3. GÜNCELLENMİŞ YÖNTEM: MSER İLE KARAKTER ADAYLARINI BULMA ---

# YENİ ADIM: MSER'den önce gürültüyü azaltmak için Gaussian Blur uygula
yumusatilmis_plaka = cv2.GaussianBlur(gri_plaka, (5, 5), 0)

# MSER'i akıllı parametrelerle oluştur
min_alan = int(plaka_alani * 0.005)
max_alan = int(plaka_alani * 0.08)
mser = cv2.MSER_create(5, min_alan, max_alan)

# MSER'i artık yumuşatılmış resim üzerinde çalıştır
regions, _ = mser.detectRegions(yumusatilmis_plaka)

# Tespit edilen bölgeleri işlenebilir konturlara dönüştür
hulls = [cv2.convexHull(p.reshape(-1, 1, 2)) for p in regions]

# --- 4. KARAKTER FİLTRELEME, OPTİMİZASYON VE OKUMA ---
H, W = buyuk_plaka.shape[:2]
cizim_plaka = buyuk_plaka.copy()
bulunan_karakterler_ve_konumlari = []

print("\nKarakterler Tesseract için optimize ediliyor ve okunuyor...")
for i, c in enumerate(hulls):
    x, y, w, h = cv2.boundingRect(c)

    aspect_ratio = h / w if w > 0 else 0
    kon1 = h < H * 0.9 and h > H * 0.3
    kon2 = w < W * 0.25 and w > 5
    kon3 = aspect_ratio > 1.3 and aspect_ratio < 4.0

    if kon1 and kon2 and kon3:
        cv2.rectangle(cizim_plaka, (x, y), (x + w, y + h), (0, 255, 0), 2)

        kirpilmis_karakter_gri = gri_plaka[y:y + h, x:x + w].copy()

        if kirpilmis_karakter_gri.size > 0:
            _, char_binary = cv2.threshold(kirpilmis_karakter_gri, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            if np.mean(char_binary) < 128:
                char_binary = cv2.bitwise_not(char_binary)
            padded_char = cv2.copyMakeBorder(char_binary, 10, 10, 10, 10, cv2.BORDER_CONSTANT, value=[255])

            config = "--psm 10 -c tessedit_char_whitelist=0123456789ABCDEFGHKLMNPRSTUVZ"
            okunan_karakter = pytesseract.image_to_string(padded_char, config=config).strip()

            if len(okunan_karakter) == 1:
                bulunan_karakterler_ve_konumlari.append((x, okunan_karakter))

# --- 5. SONUÇLARI GÖSTERME ---
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