# run_headless.py

import cv2
import requests
import json
import time
import threading

from core_engine.lpr_engine import LPREngine

# --- ⚙️ RASPBERRY PI AYARLARI ⚙️ ---
# Bu bölümden sistemi kolayca yapılandırabilirsiniz.

# 1. Kamera Kaynakları
#    - Raspberry Pi Kamera Modülü için: 0
#    - USB Webcam için: 0, 1, 2...
#    - IP Kamera için: "rtsp://..."
CAMERA_SOURCE_GIRIS = 0  # Zorunlu giriş kamerası
CAMERA_SOURCE_CIKIS = None  # İkinci kamera yoksa veya istenmiyorsa None yapın

# 2. Web API Ayarları
API_URL = 'http://plate.pikselanalitik.com/api/log_event.php'

# 3. Model Yolu (Performans için 'nano' versiyonu şiddetle tavsiye edilir)
YOLO_MODEL_PATH = 'C:/Users/Win11/PycharmProjects/Plate/plate2/best.pt'

# 4. Performans Ayarı
#    Raspberry Pi'ın işlemcisini yormamak için bu değeri yüksek tutun.
PROCESS_EVERY_N_FRAMES = 30  # Her 30 karede bir (yaklaşık saniyede bir) işlem yap

# -------------------------

is_running = True


def send_plate_to_api(plate_text, camera_id, frame):
    """Tespit edilen plakayı ve görüntüyü web sunucusuna gönderir."""
    if not API_URL:
        print(f"[{camera_id.upper()}] UYARI: API_URL ayarlanmamış.")
        return

    print(f"[{camera_id.upper()}] API'ye gönderiliyor: {plate_text}")

    success, encoded_image = cv2.imencode('.jpg', frame)
    if not success:
        print(f"[{camera_id.upper()}] HATA: Görüntü JPEG formatına çevrilemedi.")
        return

    payload = {'plate': plate_text, 'gate': camera_id}
    files = {'image': ('capture.jpg', encoded_image.tobytes(), 'image/jpeg')}

    try:
        response = requests.post(API_URL, files=files, data=payload, timeout=10)
        response.raise_for_status()
        api_response = response.json()
        print(f"[{camera_id.upper()}] API Cevabı: {api_response.get('message', 'Mesaj yok')}")
    except requests.exceptions.RequestException as e:
        print(f"[{camera_id.upper()}] API'ye bağlanırken HATA oluştu: {e}")


def process_camera_stream(camera_id, source, lpr_engine):
    """Belirtilen kameradan görüntü akışını alan ve işleyen ana fonksiyon."""
    global is_running

    cap = cv2.VideoCapture(source, cv2.CAP_V4L2)

    # Performans için kamera çözünürlüğünü düşür
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    if not cap.isOpened():
        print(f"[{camera_id.upper()}] HATA: Kamera '{source}' açılamadı.")
        return

    print(f"[{camera_id.upper()}] Kamera '{source}' başarıyla açıldı. Akış başlıyor...")

    detected_plates = set()
    frame_counter = 0

    while is_running:
        ret, frame = cap.read()
        if not ret:
            print(f"[{camera_id.upper()}] UYARI: Kameradan görüntü alınamadı. Bekleniyor...")
            time.sleep(5)
            continue

        frame_counter += 1
        if frame_counter % PROCESS_EVERY_N_FRAMES == 0:
            results = lpr_engine.process_image(frame)

            for plate_text, coords in results:
                if plate_text not in detected_plates:
                    detected_plates.add(plate_text)
                    print(f"[{camera_id.upper()}] YENİ PLAKA: {plate_text}")
                    api_thread = threading.Thread(target=send_plate_to_api, args=(plate_text, camera_id, frame))
                    api_thread.start()

        time.sleep(0.01)  # İşlemciye nefes aldır

    cap.release()
    print(f"[{camera_id.upper()}] Kamera akışı sonlandırıldı.")


def main():
    global is_running
    print("Plaka Tanıma Sistemi (Raspberry Pi Modu) Başlatılıyor...")
    print("Durdurmak için terminale Ctrl+C yapın.")

    try:
        lpr_engine = LPREngine(detector_model_path=YOLO_MODEL_PATH)
    except Exception as e:
        print(f"KRİTİK HATA: Motor yüklenemedi: {e}")
        return

    threads = []

    giris_thread = threading.Thread(target=process_camera_stream, args=("giris", CAMERA_SOURCE_GIRIS, lpr_engine))
    threads.append(giris_thread)

    if CAMERA_SOURCE_CIKIS is not None:
        cikis_thread = threading.Thread(target=process_camera_stream, args=("cikis", CAMERA_SOURCE_CIKIS, lpr_engine))
        threads.append(cikis_thread)

    for t in threads:
        t.start()

    try:
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        print("\nCtrl+C algılandı. Sistem kapatılıyor...")
        is_running = False
        for t in threads:
            t.join()

    print("Sistem başarıyla kapatıldı.")


if __name__ == "__main__":
    main()