# updated gui/main_window.py
# Düzeltilmiş ve hata ayıklama + URL sanitize eklenmiş versiyon
# NOT: LPREngine sınıfınızın process_image(frame) -> List[ (plate_text, (x1,y1,x2,y2)) ] döndüğünü varsayıyorum.

from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel,
                               QLineEdit, QHBoxLayout, QGroupBox, QListWidget)
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QPixmap, QImage
import cv2
import requests
import json
import urllib.parse
import os
import sys

from core_engine.lpr_engine import LPREngine

PROCESS_EVERY_N_FRAMES = 10
# Varsayılan API_URL; isterseniz ortam değişkeni ile geçersiz kılınabilir:
API_URL = os.environ.get("API_URL", "http://plate.pikselanalitik.com/api/log_event.php")


class MainWindow(QMainWindow):
    def __init__(self, model_path: str):
        super().__init__()
        self.setWindowTitle("Plaka Tanıma Sistemi (Hata Ayıklama Modu)")
        self.setGeometry(100, 100, 1280, 720)

        # --- MOTOR YÜKLEME KONTROLÜ ---
        print("1. Plaka tanıma motoru yükleniyor...")
        try:
            self.lpr_engine = LPREngine(detector_model_path=model_path)
            print("   ✅ Plaka tanıma motoru BAŞARIYLA yüklendi.")
        except Exception as e:
            print(f"   ❌ HATA: Plaka tanıma motoru YÜKLENEMEDİ: {e}")
            self.lpr_engine = None
        # -----------------------------

        self.cap_giris, self.timer_giris, self.giris_frame_counter = None, None, 0
        self.cap_cikis, self.timer_cikis, self.cikis_frame_counter = None, None, 0

        self._create_ui()

        self.giris_widgets["connect_button"].clicked.connect(lambda: self.start_stream("giris"))
        self.giris_widgets["stop_button"].clicked.connect(lambda: self.stop_stream("giris"))

        self.cikis_widgets["connect_button"].clicked.connect(lambda: self.start_stream("cikis"))
        self.cikis_widgets["stop_button"].clicked.connect(lambda: self.stop_stream("cikis"))

        # Otomatik başlat (isteğe bağlı)
        try:
            self.start_stream("giris")
        except Exception as e:
            print("Otomatik giriş başlatılırken hata:", e)

    def _create_ui(self):
        self.group_giris, self.giris_widgets = self._create_camera_group("Giriş Kamerası")
        self.group_cikis, self.cikis_widgets = self._create_camera_group("Çıkış Kamerası")
        # Varsayılan olarak webcam index 0
        self.giris_widgets["url_input"].setText("0")
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.group_giris)
        main_layout.addWidget(self.group_cikis)
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def _create_camera_group(self, title):
        group_box = QGroupBox(title)
        layout = QVBoxLayout()
        video_label = QLabel("Kamera bekleniyor...")
        video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        video_label.setStyleSheet("background-color: black; color: white;")
        video_label.setMinimumSize(600, 400)
        url_input = QLineEdit()
        url_input.setPlaceholderText("Webcam için '0', '1'.. veya RTSP URL girin")
        connect_button = QPushButton("Başlat")
        stop_button = QPushButton("Durdur")
        stop_button.setEnabled(False)
        button_layout = QHBoxLayout()
        button_layout.addWidget(url_input)
        button_layout.addWidget(connect_button)
        button_layout.addWidget(stop_button)
        results_list = QListWidget()
        detected_plates = set()
        layout.addWidget(video_label)
        layout.addLayout(button_layout)
        layout.addWidget(QLabel("Tespit Edilen Plakalar:"))
        layout.addWidget(results_list)
        group_box.setLayout(layout)
        widgets = {"video_label": video_label, "url_input": url_input,
                   "connect_button": connect_button, "stop_button": stop_button,
                   "results_list": results_list, "detected_plates": detected_plates}
        return group_box, widgets

    def start_stream(self, camera_id):
        widgets = self.giris_widgets if camera_id == "giris" else self.cikis_widgets
        source_text = widgets["url_input"].text()
        if not source_text:
            return
        try:
            source = int(source_text)
        except ValueError:
            source = source_text
        cap = cv2.VideoCapture(source)
        # Küçük bekleme: bazı RTSP/HTTP streamler açılırken süre isteyebilir
        if not cap.isOpened():
            widgets["video_label"].setText(f"HATA: '{source}' açılamadı!")
            print(f"start_stream: Kaynak açılamadı -> {repr(source_text)}")
            return
        timer = QTimer(self)
        if camera_id == "giris":
            self.cap_giris, self.timer_giris = cap, timer
            self.timer_giris.timeout.connect(self.update_frame_giris)
            self.timer_giris.start(40)
        else:
            self.cap_cikis, self.timer_cikis = cap, timer
            self.timer_cikis.timeout.connect(self.update_frame_cikis)
            self.timer_cikis.start(40)
        widgets["connect_button"].setEnabled(False)
        widgets["stop_button"].setEnabled(True)

    def update_frame_giris(self):
        """Giriş kamerasından kare okur, işler ve ekranda günceller."""
        if not self.cap_giris:
            return
        ret, frame = self.cap_giris.read()
        if ret:
            self.giris_frame_counter += 1
            # --- HATA AYIKLAMA KONTROLÜ ---
            if self.lpr_engine and self.giris_frame_counter % PROCESS_EVERY_N_FRAMES == 0:
                print(f"[{self.giris_frame_counter}] >>> Plaka tanıma motoru ÇALIŞTIRILIYOR...")
                try:
                    results = self.lpr_engine.process_image(frame)
                    print(f"    <<< Motor sonucu: {results}")
                    self._process_results(results, frame, "giris")
                except Exception as e:
                    print(f"    ❌ HATA: Motor çalışırken bir sorun oluştu: {e}")
            # -------------------------------
            self._display_frame(frame, self.giris_widgets["video_label"])
        else:
            self.stop_stream("giris")

    def update_frame_cikis(self):
        if not self.cap_cikis:
            return
        ret, frame = self.cap_cikis.read()
        if ret:
            self._display_frame(frame, self.cikis_widgets["video_label"])
        else:
            self.stop_stream("cikis")

    def _process_results(self, results, frame, camera_id):
        # results: [(plate_text, (x1,y1,x2,y2)), ...]
        widgets = self.giris_widgets if camera_id == "giris" else self.cikis_widgets
        for item in results:
            try:
                plate_text, coords = item
            except Exception:
                # Eğer motor farklı format döndürürse hata ayıkla
                print("Beklenmeyen motor sonucu formatı:", item)
                continue
            if not plate_text:
                continue
            if plate_text not in widgets["detected_plates"]:
                widgets["detected_plates"].add(plate_text)
                widgets["results_list"].addItem(plate_text)
                # API'ye gönderme (asenkron hale getirilebilir)
                self.send_plate_to_api(plate_text, camera_id, frame)
            # Görselleştirme
            try:
                x1, y1, x2, y2 = coords
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, plate_text, (x1, max(y1 - 10, 0)), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            except Exception:
                # eğer coords beklenenden farklıysa atla
                pass

    # -------------------------
    # URL sanitize / validation
    # -------------------------
    def is_valid_url(self, url: str) -> bool:
        try:
            parts = urllib.parse.urlparse(url)
            return parts.scheme in ("http", "https") and bool(parts.netloc)
        except Exception:
            return False

    def sanitize_url(self, url: str) -> str:
        if not url:
            return url
        url = url.strip()
        # kontrol karakterlerini temizle
        url = url.replace("\n", "").replace("\r", "").replace("\t", "")
        # zero-width veya diğer kontrol karakterlerini kaldır
        url = "".join(ch for ch in url if ord(ch) >= 32)
        return url

    def send_plate_to_api(self, plate_text, camera_id, frame):
        """
        Background thread ile API'ye POST atar. Geniş debug çıktılarını konsola yazdırır:
        - kullanılacak URL
        - sanitize edilmiş URL
        - plate_text'in içeriği (repr)
        - gönderilen dosya anahtarları / boyutu
        - request method ve sunucudan dönen raw cevap
        """
        import threading
        def _send():
            global API_URL
            if not API_URL:
                print("UYARI: API_URL ayarlanmamış, veri gönderilemiyor.")
                return

            # sanitize and validate URL
            url_raw = API_URL
            print("DEBUG: Raw API_URL repr:", repr(url_raw))
            url = self.sanitize_url(url_raw)
            print("DEBUG: Sanitized API_URL repr:", repr(url))
            if not self.is_valid_url(url):
                print("HATA: API_URL geçersiz görünüyor. Gönderim iptal edildi.")
                return

            # plate kontrolü
            print("DEBUG: plate_text repr:", repr(plate_text))
            if not plate_text or str(plate_text).strip() == "":
                print("HATA: Gönderilecek plaka değeri boş. Gönderim iptal edildi.")
                return

            # encode frame to jpg
            success, encoded_image = cv2.imencode('.jpg', frame)
            if not success:
                print("HATA: Görüntü JPEG'e çevrilemedi. Gönderim iptal edildi.")
                return
            img_bytes = encoded_image.tobytes()

            payload = {'plate': plate_text, 'gate': camera_id}
            files = {'image': ('capture.jpg', img_bytes, 'image/jpeg')}

            # Show what we will send (lengths, keys)
            print("DEBUG: payload repr:", repr(payload))
            print("DEBUG: files keys:", list(files.keys()), "image size:", len(img_bytes))

            try:
                # Session that ignores environment (proxy vars) to avoid broken proxy envs
                session = requests.Session()
                session.trust_env = False

                # Prepare request for inspection (optional)
                prep = requests.Request('POST', url, files=files, data=payload).prepare()
                print("DEBUG: Prepared request method:", prep.method)
                print("DEBUG: Prepared request url:", prep.url)
                # prep.body may be bytes (multipart); show length only to avoid huge output
                body_len = len(prep.body) if prep.body is not None else 0
                print("DEBUG: Prepared request body length:", body_len)
                # show headers that will be sent
                print("DEBUG: Prepared headers (partial):")
                for k in ('Content-Type', 'User-Agent'):
                    if k in prep.headers:
                        print(f"  {k}: {prep.headers[k]}")

                # Send the request
                resp = session.send(prep, timeout=15)
                print("DEBUG: HTTP status code:", resp.status_code)
                # Show raw response text (truncated)
                text = resp.text or ""
                print("DEBUG: Raw response (first 1000 chars):", text[:1000])

                # Try to parse JSON
                try:
                    data = resp.json()
                    print("DEBUG: JSON response:", data)
                except ValueError:
                    print("DEBUG: Response is not JSON.")

            except requests.exceptions.RequestException as e:
                print("API'ye bağlanırken RequestException oluştu:", repr(e))
                # show traceback for deeper debugging
                import traceback
                traceback.print_exc()
            except Exception as ex:
                print("Beklenmeyen hata:", repr(ex))
                import traceback
                traceback.print_exc()

        # run in background thread
        try:
            t = threading.Thread(target=_send, daemon=True)
            t.start()
        except Exception as e:
            print("Thread başlatılırken hata:", e)

    def _display_frame(self, frame, label):
        try:
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)
            label.setPixmap(pixmap.scaled(label.size(), Qt.AspectRatioMode.KeepAspectRatio))
        except Exception as e:
            # Görüntü dönüştürme sırasında hata gelirse text göster
            label.setText("Görüntü işlenemedi: " + str(e))

    def stop_stream(self, camera_id):
        if camera_id == "giris" and self.timer_giris:
            try:
                self.timer_giris.stop()
            except Exception:
                pass
            try:
                self.cap_giris.release()
            except Exception:
                pass
            self.cap_giris, self.timer_giris = None, None
            self.giris_widgets["video_label"].setText("Giriş kamerası durduruldu.")
            self.giris_widgets["connect_button"].setEnabled(True)
            self.giris_widgets["stop_button"].setEnabled(False)
        elif camera_id == "cikis" and self.timer_cikis:
            try:
                self.timer_cikis.stop()
            except Exception:
                pass
            try:
                self.cap_cikis.release()
            except Exception:
                pass
            self.cap_cikis, self.timer_cikis = None, None
            self.cikis_widgets["video_label"].setText("Çıkış kamerası durduruldu.")
            self.cikis_widgets["connect_button"].setEnabled(True)
            self.cikis_widgets["stop_button"].setEnabled(False)

    def closeEvent(self, event):
        self.stop_stream("giris")
        self.stop_stream("cikis")
        event.accept()


# Eğer modül doğrudan çalıştırılırsa basit bir test başlat (opsiyonel)
if __name__ == "__main__":
    # model path argümanı verin veya default bir path kullanın
    model = sys.argv[1] if len(sys.argv) > 1 else "model.pt"
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    win = MainWindow(model)
    win.show()
    sys.exit(app.exec())