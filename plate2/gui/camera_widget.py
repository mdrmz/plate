# gui/camera_widget.py

from PySide6.QtWidgets import (QGroupBox, QVBoxLayout, QLabel, QLineEdit,
                               QPushButton, QHBoxLayout, QListWidget)
from PySide6.QtCore import QTimer, Qt, Signal, Slot
from PySide6.QtGui import QPixmap, QImage
import cv2
import logging
import time  # GÜNCELLEME: Zaman kontrolü için time modülünü import ettik
import numpy as np
# GÜNCELLEME: Kare sayacı yerine saniye bazlı kontrol yapacağız
PROCESS_INTERVAL_SECONDS = 15


class CameraWidget(QGroupBox):
    """Tek bir kamera stream'ini yöneten arayüz bileşeni."""

    frame_to_process = Signal(str, np.ndarray)

    def __init__(self, title: str, camera_id: str):
        super().__init__(title)
        self.camera_id = camera_id

        self.cap = None
        self.timer = QTimer(self)

        # GÜNCELLEME: Kare sayacı yerine son işlem zamanını tutacağız
        self.last_process_time = 0

        self.detected_plates = set()

        # UI Elemanları
        self.video_label = QLabel("Kamera bekleniyor...")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setStyleSheet("background-color: black; color: white;")
        self.video_label.setMinimumSize(600, 400)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Webcam için '0', '1'.. veya RTSP URL girin")

        self.connect_button = QPushButton("Başlat")
        self.stop_button = QPushButton("Durdur")
        self.stop_button.setEnabled(False)

        self.results_list = QListWidget()

        # Layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.url_input)
        button_layout.addWidget(self.connect_button)
        button_layout.addWidget(self.stop_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.video_label)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(QLabel("Tespit Edilen Plakalar:"))
        main_layout.addWidget(self.results_list)

        self.setLayout(main_layout)

        # Sinyal-Slot Bağlantıları
        self.connect_button.clicked.connect(self.start_stream)
        self.stop_button.clicked.connect(self.stop_stream)
        self.timer.timeout.connect(self.update_frame)

    def start_stream(self):
        source_text = self.url_input.text()
        if not source_text: return

        try:
            source = int(source_text)
        except ValueError:
            source = source_text

        self.cap = cv2.VideoCapture(source)
        if not self.cap.isOpened():
            self.video_label.setText(f"HATA: '{source}' açılamadı!")
            logging.error(f"[{self.camera_id}] Kaynak açılamadı: {source_text}")
            self.cap = None
            return

        self.timer.start(40)  # ~25 FPS'de video akışına devam et
        self.connect_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.video_label.setText("Bağlanılıyor...")
        logging.info(f"[{self.camera_id}] Stream başlatıldı: {source_text}")

    def stop_stream(self):
        self.timer.stop()
        if self.cap:
            self.cap.release()
        self.cap = None
        self.video_label.setText(f"{self.camera_id.capitalize()} kamerası durduruldu.")
        self.connect_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        logging.info(f"[{self.camera_id}] Stream durduruldu.")

    def update_frame(self):
        if not self.cap: return
        ret, frame = self.cap.read()
        if ret:
            # --- GÜNCELLEME: Zaman bazlı kontrol ---
            # Mevcut zamanı al
            current_time = time.time()

            # Son işlemden bu yana 30 saniyeden fazla geçtiyse...
            if (current_time - self.last_process_time) > PROCESS_INTERVAL_SECONDS:
                logging.info(f"[{self.camera_id}] 30 saniye geçti, plaka taraması yapılıyor...")
                # Son işlem zamanını güncelle
                self.last_process_time = current_time
                # Ağır işlemi yapmak için kareyi Worker'a gönder
                self.frame_to_process.emit(self.camera_id, frame.copy())

            # Video akışını her zaman güncelle (kare sayacından bağımsız)
            self._display_frame(frame)
        else:
            self.stop_stream()

    @Slot(list, np.ndarray)
    def update_with_results(self, results, processed_frame):
        # Bu kısımda değişiklik yok
        frame_copy = processed_frame.copy()
        for plate_text, (x1, y1, x2, y2) in results:
            if plate_text not in self.detected_plates:
                self.detected_plates.add(plate_text)
                self.results_list.addItem(plate_text)
            cv2.rectangle(frame_copy, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame_copy, plate_text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

        self._display_frame(frame_copy)

    def _display_frame(self, frame):
        # Bu kısımda değişiklik yok
        try:
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            qt_image = QImage(rgb_image.data, w, h, ch * w, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)
            self.video_label.setPixmap(pixmap.scaled(self.video_label.size(), Qt.AspectRatioMode.KeepAspectRatio))
        except Exception as e:
            logging.error(f"Görüntü dönüştürme hatası: {e}")
            self.video_label.setText("Görüntü işlenemedi.")

    def set_default_source(self, source: str):
        # Bu kısımda değişiklik yok
        self.url_input.setText(source)