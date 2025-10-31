# core_engine/stream_reader.py

import cv2
import requests
import numpy as np
import threading
import time
import logging


class MJPEGStreamReader:
    """
    Bir MJPEG stream'ini (örn: snapshot.cgi) `requests` ile okuyan ve
    cv2.VideoCapture gibi davranan bir sınıf.
    Bağlantı kopsa bile arka planda yeniden bağlanmayı dener.
    """

    def __init__(self, url):
        self.url = url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.latest_frame = None
        self.is_running = False
        self.lock = threading.Lock()  # Thread güvenliği için
        self.thread = None

    def start(self):
        """Arka planda video okuma thread'ini başlatır."""
        if self.is_running:
            logging.warning("Stream reader zaten çalışıyor.")
            return

        self.is_running = True
        self.thread = threading.Thread(target=self._read_loop, daemon=True)
        self.thread.start()
        logging.info("MJPEG Stream Reader başlatıldı.")

    def _read_loop(self):
        """
        Bu fonksiyon arka planda sürekli çalışır, stream'e bağlanır,
        JPEG karelerini ayrıştırır ve `self.latest_frame`'i günceller.
        """
        while self.is_running:
            try:
                logging.info(f"Kameraya bağlanılıyor: {self.url}")
                stream = requests.get(self.url, headers=self.headers, stream=True, timeout=10)

                if stream.status_code == 200:
                    logging.info("BAŞARILI! Görüntü akışı başladı.")
                    bytes_buffer = bytes()

                    for chunk in stream.iter_content(chunk_size=4096):
                        if not self.is_running: break  # Durdurma komutu geldiyse çık

                        bytes_buffer += chunk
                        a = bytes_buffer.find(b'\xff\xd8')  # JPEG başlangıcı
                        b = bytes_buffer.find(b'\xff\xd9')  # JPEG bitişi

                        if a != -1 and b != -1:
                            jpg_data = bytes_buffer[a:b + 2]
                            bytes_buffer = bytes_buffer[b + 2:]

                            frame = cv2.imdecode(np.frombuffer(jpg_data, dtype=np.uint8), cv2.IMREAD_COLOR)

                            # Thread güvenli bir şekilde en son kareyi güncelle
                            with self.lock:
                                self.latest_frame = frame
                else:
                    logging.warning(f"Sunucudan hatalı yanıt: {stream.status_code}. 5 sn sonra tekrar denenecek...")
                    time.sleep(5)

            except requests.exceptions.RequestException as e:
                logging.error(f"Bağlantı hatası: {e}. 5 sn sonra tekrar denenecek...")
                time.sleep(5)
            except Exception as e:
                logging.error(f"Stream okuma döngüsünde beklenmedik hata: {e}", exc_info=True)
                time.sleep(5)

    def read(self):
        """
        En son yakalanan kareyi döndürür. cv2.VideoCapture.read() gibi davranır.
        :return: (ret, frame) -> (bool, np.ndarray)
        """
        with self.lock:
            if self.latest_frame is None:
                return False, None
            # Dışarıya çerçevenin bir kopyasını vererek thread güvenliğini artır
            frame_copy = self.latest_frame.copy()

        return True, frame_copy

    def stop(self):
        """Arka plan thread'ini güvenli bir şekilde durdurur."""
        logging.info("MJPEG Stream Reader durduruluyor...")
        self.is_running = False
        if self.thread:
            self.thread.join()  # Thread'in bitmesini bekle