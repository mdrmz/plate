# gui/api_manager.py

import threading
import requests
import cv2
import urllib.parse
import logging
import os
from PySide6.QtCore import QObject, Slot
import numpy as np

# Varsayılan API_URL
API_URL = os.environ.get("API_URL", "http://plate.pikselanalitik.com/api/log_event.php")


class APIManager(QObject):
    """API iletişimini yöneten sınıf."""

    def __init__(self):
        super().__init__()

    def is_valid_url(self, url: str) -> bool:
        try:
            parts = urllib.parse.urlparse(url)
            return parts.scheme in ("http", "https") and bool(parts.netloc)
        except Exception:
            return False

    def sanitize_url(self, url: str) -> str:
        if not url: return url
        url = url.strip().replace("\n", "").replace("\r", "").replace("\t", "")
        return "".join(ch for ch in url if ord(ch) >= 32)

    @Slot(str, str, np.ndarray)
    def send_plate_data(self, plate_text: str, camera_id: str, frame: np.ndarray):
        """
        Veriyi API'ye göndermek için bir arka plan thread'i başlatır.
        Bu slot ana arayüz thread'inde çalışır ama asıl işi başka bir thread'e verir.
        """
        try:
            # Senin yazdığın _send fonksiyonunu bir thread içinde çalıştırmak için
            # onu bu metoda dahil ettim ve logging kullandım.
            thread = threading.Thread(target=self._send_request,
                                      args=(plate_text, camera_id, frame),
                                      daemon=True)
            thread.start()
        except Exception as e:
            logging.error(f"API gönderme thread'i başlatılırken hata: {e}", exc_info=True)

    def _send_request(self, plate_text: str, camera_id: str, frame: np.ndarray):
        """
        Bu fonksiyon arka planda çalışır ve API'ye POST isteği atar.
        (Senin yazdığın orijinal fonksiyondur, print'ler logging ile değiştirildi)
        """
        global API_URL
        if not API_URL:
            logging.warning("API_URL ayarlanmamış, veri gönderilemiyor.")
            return

        url = self.sanitize_url(API_URL)
        if not self.is_valid_url(url):
            logging.error(f"API_URL geçersiz görünüyor: '{url}'. Gönderim iptal edildi.")
            return

        if not plate_text or str(plate_text).strip() == "":
            logging.error("Gönderilecek plaka değeri boş. Gönderim iptal edildi.")
            return

        success, encoded_image = cv2.imencode('.jpg', frame)
        if not success:
            logging.error("Görüntü JPEG'e çevrilemedi. Gönderim iptal edildi.")
            return
        img_bytes = encoded_image.tobytes()

        payload = {'plate': plate_text, 'gate': camera_id}
        files = {'image': ('capture.jpg', img_bytes, 'image/jpeg')}

        logging.info(f"API isteği hazırlanıyor: URL='{url}', Payload={payload}")

        try:
            session = requests.Session()
            session.trust_env = False  # Proxy ayarlarını yoksay

            resp = session.post(url, files=files, data=payload, timeout=15)

            logging.info(f"API Cevabı: Durum Kodu={resp.status_code}")
            logging.debug(f"API Raw Cevabı (ilk 500 karakter): {resp.text[:500]}")

            try:
                data = resp.json()
                logging.debug(f"API JSON Cevabı: {data}")
            except ValueError:
                logging.debug("API cevabı JSON formatında değil.")

        except requests.exceptions.RequestException as e:
            logging.error(f"API'ye bağlanırken hata oluştu: {e}", exc_info=True)
        except Exception as ex:
            logging.error(f"API gönderimi sırasında beklenmeyen hata: {ex}", exc_info=True)