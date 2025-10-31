import cv2
import logging
import mysql.connector
from .plate_detector import PlateDetector
from .plate_recognizer import PlateRecognizer
from .gate_controller import GateController

class LPREngine:
    def __init__(self, detector_model_path: str, db_config: dict, servo_pin: int):
        self.detector = PlateDetector(model_path=detector_model_path)
        self.recognizer = PlateRecognizer(gpu=False) # Pi'de her zaman CPU
        self.gate_controller = GateController(servo_pin=servo_pin)
        self.db_config = db_config

    def _check_whitelist(self, plate: str) -> bool:
        conn = None; cursor = None
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            query = "SELECT ozel_erisim FROM araclar WHERE plaka = %s"
            cursor.execute(query, (plate,))
            result = cursor.fetchone()
            if result and result[0] == 1:
                logging.info(f"Yetki Kontrol: Plaka ({plate}) ÖZEL ERİŞİME SAHİP.")
                return True
        except mysql.connector.Error as err:
            logging.error(f"Veritabanı whitelist kontrol hatası: {err}")
        finally:
            if cursor: cursor.close()
            if conn and conn.is_connected(): conn.close()
        
        logging.info(f"Yetki Kontrol: Plaka ({plate}) özel erişime sahip DEĞİL.")
        return False

    def process_image(self, image):
        yolo_input = cv2.resize(image, (320, 320))
        plate_coords_yolo = self.detector.detect(yolo_input)
        if not plate_coords_yolo: return []

        h_orig, w_orig = image.shape[:2]
        recognized_plates = []

        for (x1_y, y1_y, x2_y, y2_y) in plate_coords_yolo:
            x1 = int(x1_y * w_orig / 320); y1 = int(y1_y * h_orig / 320)
            x2 = int(x2_y * w_orig / 320); y2 = int(y2_y * h_orig / 320)
            plate_image = image[y1:y2, x1:x2]
            if plate_image.size == 0: continue
            
            plate_text = self.recognizer.recognize(plate_image)
            
            if plate_text:
                recognized_plates.append((plate_text, (x1, y1, x2, y2)))
                if self._check_whitelist(plate_text):
                    self.gate_controller.open_gate()

        return recognized_plates