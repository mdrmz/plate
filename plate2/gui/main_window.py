# gui/main_window.py

import sys
import logging
import os
from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QApplication
from PySide6.QtCore import QThread, Slot
import numpy as np

# Gerekli importlar
from .camera_widget import CameraWidget
from .worker import Worker
from .api_manager import APIManager

# OMP Hatası için en üste ekliyoruz
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'


class MainWindow(QMainWindow):
    def __init__(self, model_path: str):
        super().__init__()
        self.setWindowTitle("Plaka Tanıma Sistemi v2.2 (Final)")
        self.setGeometry(100, 100, 1280, 720)

        self.api_manager = APIManager()
        self.thread = QThread()
        self.worker = Worker(model_path=model_path)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.setup)
        self.thread.start()

        self.cam_giris = CameraWidget(title="Giriş Kamerası", camera_id="giris")
        self.cam_cikis = CameraWidget(title="Çıkış Kamerası", camera_id="cikis")

        self.cam_giris.set_default_source("0")
        self.cam_cikis.set_default_source("1")

        # --- Sinyal-Slot Bağlantıları ---
        self.cam_giris.frame_to_process.connect(self.worker.process_frame)
        self.cam_cikis.frame_to_process.connect(self.worker.process_frame)
        self.worker.results_ready.connect(self.handle_results)
        self.worker.error_occurred.connect(self.handle_worker_error)

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.cam_giris)
        main_layout.addWidget(self.cam_cikis)
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    @Slot(str, list, np.ndarray)
    def handle_results(self, camera_id, results, frame):
        target_widget = self.cam_giris if camera_id == "giris" else self.cam_cikis
        target_widget.update_with_results(results, frame)

        for plate_text, _ in results:
            self.api_manager.send_plate_data(plate_text, camera_id, frame)

    @Slot(str, str)
    def handle_worker_error(self, camera_id, error_message):
        logging.error(f"Worker Hatası ({camera_id}): {error_message}")

    def closeEvent(self, event):
        logging.info("Uygulama kapatılıyor...")
        self.cam_giris.stop_stream()
        self.cam_cikis.stop_stream()
        self.thread.quit()
        self.thread.wait()
        event.accept()