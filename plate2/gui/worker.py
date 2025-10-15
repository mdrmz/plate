# gui/worker.py

import time
from PySide6.QtCore import QObject, Signal, Slot
import numpy as np
import logging

# LPREngine sınıfının doğru import edildiğinden emin ol
from core_engine.lpr_engine import LPREngine


class Worker(QObject):
    """Arka planda ağır işleri (plaka tanıma) yapan işçi sınıfı."""

    # Sonuçları ve hataları ana arayüze göndermek için sinyaller
    results_ready = Signal(str, list, np.ndarray)  # camera_id, results, original_frame
    error_occurred = Signal(str, str)  # camera_id, error_message

    def __init__(self, model_path: str):
        super().__init__()
        self.lpr_engine = None
        self.model_path = model_path
        self.is_ready = False

    def setup(self):
        """Thread başlatıldıktan sonra çağrılır, motoru bu thread'de yükler."""
        try:
            logging.info(f"Worker thread'inde LPR motoru yükleniyor ({self.model_path})...")
            self.lpr_engine = LPREngine(detector_model_path=self.model_path)
            self.is_ready = True
            logging.info("LPR motoru başarıyla yüklendi.")
        except Exception as e:
            logging.error(f"Worker setup sırasında LPR motoru yüklenemedi: {e}", exc_info=True)
            self.error_occurred.emit("general", f"Motor Yüklenemedi: {e}")

    @Slot(str, np.ndarray)
    def process_frame(self, camera_id: str, frame: np.ndarray):
        """Ana arayüzden gelen kareyi işler ve sonucu sinyal olarak gönderir."""
        if not self.is_ready or self.lpr_engine is None:
            return

        try:
            t1 = time.perf_counter()
            results = self.lpr_engine.process_image(frame)
            t2 = time.perf_counter()
            if results:
                logging.info(f"[{camera_id}] Plaka bulundu: {results} ({t2 - t1:.3f} saniye)")
                # Sonuçları orijinal kare ile birlikte geri gönder
                self.results_ready.emit(camera_id, results, frame)
        except Exception as e:
            logging.error(f"[{camera_id}] process_frame sırasında hata: {e}", exc_info=True)
            self.error_occurred.emit(camera_id, f"İşlem Hatası: {e}")