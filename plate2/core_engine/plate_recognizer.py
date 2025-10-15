"""# core_engine/new_plate_recognizer.py

import cv2
import numpy as np
import re
from tensorflow.keras.models import load_model


class PlateRecognizer:
    def __init__(self, ocr_model_path='C:/Users/Win11/PycharmProjects/Plate/plate2/platev4/plaka_ocr_model_v2.h5', labels_path='C:/Users/Win11/PycharmProjects/Plate/plate2/platev4/etiketler_v2.npy '):
        # DEĞİŞTİ: Tesseract yerine kendi modelimizi ve etiketlerimizi yüklüyoruz
        try:
            self.model = load_model(ocr_model_path)
            self.labels = np.load(labels_path, allow_pickle=True)
            self.image_size = self.model.input_shape[1:3]  # Modelin giriş boyutunu (örn: 32,32) otomatik al
            print(f"'{ocr_model_path}' modeli ve etiketleri başarıyla yüklendi.")
        except Exception as e:
            print(f"HATA: OCR modeli veya etiket dosyası yüklenemedi: {e}")
            self.model = None
            self.labels = None

    def _post_process_text(self, text: str) -> str:
        # Bu fonksiyon, ham OCR sonucunu plaka formatına göre düzeltmek için
        # hala çok faydalı olabilir. Şimdilik basit tutuyoruz.
        if not text: return ""
        # Sadece izin verilen karakterleri tut (modelin etiketlerine göre)
        allowed_chars = "".join(self.labels)
        s = re.sub(f'[^{allowed_chars}]', '', text.upper())
        return s

    def recognize(self, plate_image):
        if plate_image is None or plate_image.size == 0 or self.model is None:
            return None

        # 1. BÜYÜTME VE SEGMENTASYON İÇİN ÖN İŞLEME
        buyuk_plaka = cv2.resize(plate_image, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
        gri_plaka = cv2.cvtColor(buyuk_plaka, cv2.COLOR_BGR2GRAY)
        th_img = cv2.adaptiveThreshold(gri_plaka, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 25, 2)

        # 2. KARAKTER ADAYLARINI BULMA
        cnt = cv2.findContours(th_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]

        H, W = buyuk_plaka.shape[:2]
        bulunan_karakterler_ve_konumlari = []

        # 3. FİLTRELEME VE TEK TEK OKUMA
        for c in cnt:
            rect = cv2.minAreaRect(c)
            (x_center, y_center), (w, h), angle = rect

            aspect_ratio = max(w, h) / min(w, h) if min(w, h) > 0 else 0
            if not (h > H * 0.35 and h < H * 0.9 and w > 5 and aspect_ratio > 1.2 and aspect_ratio < 5.0):
                continue

            box = np.int64(cv2.boxPoints(rect))
            minx, miny = np.min(box[:, 0]), np.min(box[:, 1])
            maxx, maxy = np.max(box[:, 0]), np.max(box[:, 1])

            kirpilmis_karakter_gri = gri_plaka[miny:maxy, minx:maxx].copy()

            if kirpilmis_karakter_gri.size > 0:
                # DEĞİŞTİ: Tesseract optimizasyonu yerine kendi modelimiz için ön işleme yapıyoruz

                # 1. Modeli eğitirken kullandığımız boyuta getir
                karakter_resmi = cv2.resize(kirpilmis_karakter_gri, self.image_size)

                # 2. Normalizasyon ve boyutlandırma
                karakter_resmi = karakter_resmi.astype("float") / 255.0
                karakter_resmi = np.expand_dims(karakter_resmi, axis=-1)
                karakter_resmi = np.expand_dims(karakter_resmi, axis=0)

                # 3. KENDİ MODELİMİZLE TAHMİN
                tahmin = self.model.predict(karakter_resmi, verbose=0)
                tahmin_indeksi = np.argmax(tahmin)
                okunan_karakter = self.labels[tahmin_indeksi]

                if okunan_karakter:
                    bulunan_karakterler_ve_konumlari.append((minx, okunan_karakter))

        if not bulunan_karakterler_ve_konumlari:
            return None

        # 4. SON ADIM: BİRLEŞTİRME
        bulunan_karakterler_ve_konumlari.sort(key=lambda x: x[0])
        raw_plate_text = "".join([karakter for kon, karakter in bulunan_karakterler_ve_konumlari])

        final_plate_text = self._post_process_text(raw_plate_text)

        return final_plate_text"""

# core_engine/new_plate_recognizer.py

import cv2
import numpy as np
import re
import easyocr


class PlateRecognizer:
    def __init__(self, gpu=True):
        """
        EasyOCR Reader'ı başlatır.
        :param gpu: GPU desteği kullanılacaksa True, sadece CPU ise False.
        """
        try:
            # EasyOCR'ı İngilizce karakter seti ile başlatıyoruz.
            # Plakalardaki harf ve rakamlar için genellikle yeterlidir.
            self.reader = easyocr.Reader(['en'], gpu=gpu)
            print("EasyOCR motoru başarıyla yüklendi.")
        except Exception as e:
            print(f"HATA: EasyOCR yüklenemedi: {e}")
            self.reader = None

    def _post_process_text(self, text: str) -> str:
        """
        EasyOCR'dan gelen metni temizler.
        """
        if not text: return ""
        # İzin verilmeyen tüm karakterleri temizle ve büyük harfe çevir
        s = re.sub(r'[^A-Z0-9]', '', text.upper())
        return s

    def recognize(self, plate_image):
        """
        Verilen plaka görüntüsündeki metni EasyOCR ile okur.
        """
        if plate_image is None or plate_image.size == 0 or self.reader is None:
            return None

        # 1. GÖRÜNTÜYÜ HAZIRLAMA
        # EasyOCR'ın daha iyi çalışması için plakayı büyütmek faydalıdır.
        buyuk_plaka = cv2.resize(plate_image, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
        # EasyOCR renkli veya gri tonlamalı görüntü alabilir, gri genellikle daha stabildir.
        gri_plaka = cv2.cvtColor(buyuk_plaka, cv2.COLOR_BGR2GRAY)

        # 2. EASYOCR İLE OKUMA
        # readtext fonksiyonu hem metni bulur hem de okur.
        # detail=0 sadece metinleri döndürür, detail=1 ise koordinat ve güven skoru da verir.
        try:
            results = self.reader.readtext(gri_plaka, detail=1, paragraph=False)
        except Exception as e:
            print(f"EasyOCR okuma sırasında hata: {e}")
            return None

        if not results:
            return None

        # 3. SONUÇLARI BİRLEŞTİRME
        # EasyOCR sonuçları her zaman soldan sağa sıralı olmayabilir, bu yüzden x-koordinatına göre sıralayalım.
        # Bounding box'ın sol üst köşesinin x değerine göre sırala: result[0][0][0]
        results.sort(key=lambda x: x[0][0][0])

        # Okunan tüm metin parçalarını birleştir
        raw_plate_text = "".join([res[1] for res in results])

        # Son temizliği yap
        final_plate_text = self._post_process_text(raw_plate_text)

        return final_plate_text