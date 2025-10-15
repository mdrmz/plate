# core_engine/lpr_engine.py

import cv2
from .plate_detector import PlateDetector
from .plate_recognizer import PlateRecognizer # Yeni recognizer'ı import et

class LPREngine:
    def __init__(self, detector_model_path: str):
        self.detector = PlateDetector(model_path=detector_model_path)
        self.recognizer = PlateRecognizer() # Parametreler __init__ içinde

    def process_image(self, image):
        plate_coords = self.detector.detect(image)
        if not plate_coords:
            return []

        recognized_plates = []
        for coords in plate_coords:
            x1, y1, x2, y2 = coords
            h, w = image.shape[:2]
            x1, y1, x2, y2 = max(0, x1), max(0, y1), min(w, x2), min(h, y2)
            plate_image = image[y1:y2, x1:x2]

            if plate_image.size == 0: continue

            plate_text = self.recognizer.recognize(plate_image)

            if plate_text:
                recognized_plates.append((plate_text, coords))

        return recognized_plates