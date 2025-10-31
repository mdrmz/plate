import cv2
import re
import easyocr
import logging

class PlateRecognizer:
    def __init__(self, gpu=False):
        try:
            # Hem Türkçe hem İngilizce karakter setini tanıması için
            self.reader = easyocr.Reader(['tr', 'en'], gpu=gpu)
            logging.info(f"EasyOCR motoru başarıyla yüklendi (GPU: {gpu}).")
        except Exception as e:
            logging.error(f"HATA: EasyOCR yüklenemedi: {e}", exc_info=True)
            raise e

    def _clean_text(self, text: str) -> str:
        if not text: return ""
        # Sadece büyük harfleri ve rakamları tut
        return re.sub(r'[^A-Z0-9]', '', text.upper())

    def recognize(self, plate_image):
        if plate_image is None or plate_image.size == 0 or self.reader is None:
            return None
        
        # EasyOCR'a en temiz haliyle, gri tonlamalı ver
        gri_plaka = cv2.cvtColor(plate_image, cv2.COLOR_BGR2GRAY)

        try:
            results = self.reader.readtext(gri_plaka, detail=0, paragraph=True)
            if not results: return None
            
            raw_plate_text = "".join(results)
            final_plate_text = self._clean_text(raw_plate_text)
            
            return final_plate_text
        except Exception as e:
            logging.error(f"EasyOCR okuma sırasında hata: {e}", exc_info=True)
            return None