# core_engine/plate_detector.py

from ultralytics import YOLO

class PlateDetector:
    """
    YOLOv8 modelini kullanarak bir görüntüdeki plakaların konumunu tespit eder.
    Tek Sorumluluk: Sadece plaka tespiti yapar.
    """
    def __init__(self, model_path: str):
        """
        YOLOv8 modelini belirtilen yoldan yükler.
        :param model_path: .pt uzantılı model dosyasının yolu.
        """
        try:
            self.model = YOLO(model_path)
            print("YOLOv8 Plaka Tespit modeli başarıyla yüklendi.")
        except Exception as e:
            print(f"HATA: YOLO modeli yüklenemedi. {e}")
            raise

    def detect(self, image):
        """
        Verilen görüntü üzerinde plaka tespiti yapar.
        :param image: OpenCV formatında (numpy array) bir görüntü.
        :return: Bulunan her plakanın [x1, y1, x2, y2] formatındaki
                 koordinatlarını içeren bir liste.
        """
        # Modeli kullanarak tahmin yap
        results = self.model.predict(image, verbose=False)

        detections = []
        # Sonuçları döngüye al ve koordinatları çıkar
        for result in results:
            for box in result.boxes.xyxy:
                # Koordinatları tam sayıya çevir
                x1, y1, x2, y2 = map(int, box)
                detections.append([x1, y1, x2, y2])

        return detections