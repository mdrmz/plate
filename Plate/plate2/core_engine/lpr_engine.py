# core_engine/lpr_engine.py

import cv2
from .plate_detector import PlateDetector
from .plate_recognizer import PlateRecognizer


class LPREngine:
    """
    Plaka tanıma sürecini yöneten ana motor sınıfı.
    Detector ve Recognizer sınıflarını orkestra şefi gibi yönetir.
    """

    def __init__(self, detector_model_path: str):
        """
        Gerekli olan detector ve recognizer nesnelerini başlatır.
        :param detector_model_path: YOLO modelinin dosya yolu.
        """
        self.detector = PlateDetector(model_path=detector_model_path)
        self.recognizer = PlateRecognizer()

    def process_image(self, image):
        """
        Bir görüntü üzerinde tam plaka tanıma sürecini çalıştırır.
        1. Plakaları tespit et.
        2. Her plakayı kırp.
        3. Kırpılan plakadaki metni oku.
        :param image: İşlenecek olan tam görüntü.
        :return: [(plaka_metni, koordinatlar), ...] formatında bir sonuç listesi.
        """
        # 1. Görüntüdeki tüm plaka konumlarını bul
        plate_coords = self.detector.detect(image)

        if not plate_coords:
            return []

        recognized_plates = []
        for coords in plate_coords:
            x1, y1, x2, y2 = coords

            # 2. Plakayı görüntüden kırp
            # Koordinatların görüntü sınırları içinde olduğundan emin ol
            h, w = image.shape[:2]
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)

            plate_image = image[y1:y2, x1:x2]

            # Eğer kırpılan görüntü çok küçükse veya boşsa atla
            if plate_image.size == 0:
                continue

            # 3. Kırpılan plaka üzerindeki metni oku
            plate_text = self.recognizer.recognize(plate_image)

            if plate_text:
                recognized_plates.append((plate_text, coords))

        return recognized_plates