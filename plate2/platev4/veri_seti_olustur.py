import cv2
import os
import numpy as np
import uuid  # Benzersiz dosya adı için
from core_engine.plate_detector import PlateDetector

# --- AYARLAR ---
INPUT_DIR = "plaka_resimleri"  # Okunacak plaka resimlerinin olduğu klasör
OUTPUT_DIR = "veri_seti"  # Etiketlenmiş karakterlerin kaydedileceği ana klasör
ModelPath = 'C:/Users/Win11/PycharmProjects/Plate/plate2/best.pt'

# YOLO modelini yükle
detector = PlateDetector(ModelPath)
print("YOLOv8 Plaka Tespit modeli başarıyla yüklendi.")

# Çıkış ana klasörünü oluştur
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Giriş klasöründeki tüm resimleri dolaş
for filename in os.listdir(INPUT_DIR):
    if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        continue  # Sadece resim dosyalarını işle

    img_path = os.path.join(INPUT_DIR, filename)
    print(f"\nProcessing image: {filename}")

    img = cv2.imread(img_path)
    if img is None:
        print(f"Uyarı: {filename} okunamadı.")
        continue

    img_resized = cv2.resize(img, (640, 640))
    plate_coords = detector.detect(img_resized)

    if not plate_coords:
        print("Bu resimde plaka tespit edilemedi.")
        continue

    x1, y1, x2, y2 = plate_coords[0]
    plaka_img = img_resized[y1:y2, x1:x2]
    buyuk_plaka = cv2.resize(plaka_img, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
    gri_plaka = cv2.cvtColor(buyuk_plaka, cv2.COLOR_BGR2GRAY)

    # MSER ile karakterleri bul (en stabil yöntemimiz)
    plaka_alani = gri_plaka.shape[0] * gri_plaka.shape[1]
    min_alan = int(plaka_alani * 0.005)
    max_alan = int(plaka_alani * 0.08)
    mser = cv2.MSER_create(5, min_alan, max_alan)
    yumusatilmis_plaka = cv2.GaussianBlur(gri_plaka, (5, 5), 0)
    regions, _ = mser.detectRegions(yumusatilmis_plaka)
    hulls = [cv2.convexHull(p.reshape(-1, 1, 2)) for p in regions]

    # Bulunan karakterleri konuma göre sırala
    # `boundingRect` ile her bir hull için x,y,w,h al ve x'e göre sırala
    bounding_boxes = [cv2.boundingRect(c) for c in hulls]
    hulls_and_boxes = zip(hulls, bounding_boxes)
    # Filtreleme ve sıralama
    filtered_hulls = []
    for c, bbox in hulls_and_boxes:
        x, y, w, h = bbox
        aspect_ratio = h / w if w > 0 else 0
        kon1 = h < gri_plaka.shape[0] * 0.9 and h > gri_plaka.shape[0] * 0.3
        kon2 = w < gri_plaka.shape[1] * 0.25 and w > 5
        kon3 = aspect_ratio > 1.3 and aspect_ratio < 4.0
        if kon1 and kon2 and kon3:
            filtered_hulls.append((x, c))

    filtered_hulls.sort(key=lambda x: x[0])  # x koordinatına göre sırala

    # Her bir karakteri göster ve etiketle
    for x_coord, c in filtered_hulls:
        x, y, w, h = cv2.boundingRect(c)
        kirpilmis_karakter_gri = gri_plaka[y:y + h, x:x + w].copy()

        if kirpilmis_karakter_gri.size > 0:
            # Karakteri optimize et
            _, char_binary = cv2.threshold(kirpilmis_karakter_gri, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            if np.mean(char_binary) < 128: char_binary = cv2.bitwise_not(char_binary)
            padded_char = cv2.copyMakeBorder(char_binary, 10, 10, 10, 10, cv2.BORDER_CONSTANT, value=[255])

            # Kullanıcıya karakteri göster
            cv2.imshow('Etiketlenecek Karakter (Kaydetmek icin harfe, gecmek icin Space, cikmak icin ESC bas)',
                       padded_char)
            key = cv2.waitKey(0) & 0xFF

            if key == 27:  # ESC tuşuna basılırsa
                print("Çıkış yapılıyor...")
                exit()
            elif key == 32:  # Boşluk tuşuna basılırsa
                print("Karakter atlandı.")
                continue
            elif (ord('a') <= key <= ord('z')) or (ord('0') <= key <= ord('9')):
                etiket = chr(key).upper()
                print(f"Karakter '{etiket}' olarak etiketlendi.")

                # Etiket klasörünü oluştur
                etiket_klasoru = os.path.join(OUTPUT_DIR, etiket)
                os.makedirs(etiket_klasoru, exist_ok=True)

                # Benzersiz bir isimle dosyayı kaydet
                dosya_adi = f"{etiket}_{uuid.uuid4()}.png"
                kayit_yolu = os.path.join(etiket_klasoru, dosya_adi)
                cv2.imwrite(kayit_yolu, padded_char)
            else:
                print("Geçersiz tuş. Karakter atlandı.")

cv2.destroyAllWindows()
print("\nVeri seti oluşturma tamamlandı!")