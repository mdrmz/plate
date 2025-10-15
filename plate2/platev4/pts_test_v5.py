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

# --- 3. EN STABİL YÖNTEM: adaptiveThreshold ile Karakter Adaylarını Bulma ---
th_img = cv2.adaptiveThreshold(gri_plaka, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 13, 2)
# --- İNCE AYAR 1: Agresif gürültü temizleme (morphologyEx) kaldırıldı ---
# Bu satır, ince karakterlerin kaybolmasına neden olabildiği için devredışı bırakıldı.
# kernel = np.ones((3, 3), np.uint8)
# th_img = cv2.morphologyEx(th_img, cv2.MORPH_OPEN, kernel, iterations=1)

cnt = cv2.findContours(th_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnt = cnt[0]

# --- 4. KARAKTER FİLTRELEME, OPTİMİZASYON VE OKUMA ---
H, W = buyuk_plaka.shape[:2]
cizim_plaka = buyuk_plaka.copy()
bulunan_karakterler_ve_konumlari = []

print("\nKarakterler Tesseract için optimize ediliyor ve okunuyor...")
for c in cnt:
    rect = cv2.minAreaRect(c)
    (x_center, y_center), (w, h), angle = rect

    # --- İNCE AYAR 2: Filtreler tüm karakterleri yakalamak için daha esnek hale getirildi ---
    aspect_ratio = max(w, h) / min(w, h) if min(w, h) > 0 else 0
    kon1 = h > H * 0.35 and h < H * 0.9  # Minimum yükseklik şartı biraz gevşetildi
    kon2 = w > 5  # Minimum genişlik basitçe 5 pikselden büyük olsun
    kon3 = aspect_ratio > 1.2 and aspect_ratio < 5.0  # En-boy oranı aralığı genişletildi

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
            # UZMAN DOKUNUŞU: Karakteri Tesseract için Mükemmelleştirme
            _, char_binary = cv2.threshold(kirpilmis_karakter_gri, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            if np.mean(char_binary) > 128:
                char_binary = cv2.bitwise_not(char_binary)
            padded_char = cv2.copyMakeBorder(char_binary, 10, 10, 10, 10, cv2.BORDER_CONSTANT, value=[0])

            config = "--psm 10 -c tessedit_char_whitelist=0123456789ABCDEFGHKLMNPRSTUVZ"
            okunan_karakter = pytesseract.image_to_string(padded_char, config=config).strip()

            if len(okunan_karakter) == 1:
                bulunan_karakterler_ve_konumlari.append((minx, okunan_karakter))

# --- 5. SONUÇLARI GÖSTERME ---
# (Bu bölümde değişiklik yok)
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