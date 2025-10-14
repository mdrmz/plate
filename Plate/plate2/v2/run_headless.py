# run_headless.py

import cv2
import requests
import json
import time
import threading  # Aynı anda birden fazla kamerayı yönetmek için

# Kendi motorumuzu dahil ediyoruz
from core_engine.lpr_engine import LPREngine

# --- ⚙️ AYARLAR ⚙️ ---
# Bu bölümden sistemi kolayca yapılandırabilirsiniz.

# 1. Kamera Kaynakları
#    - Webcam için: 0, 1, 2...
#    - IP Kamera için: "rtsp://..."
CAMERA_SOURCE_GIRIS = 0  # Zorunlu giriş kamerası
CAMERA_SOURCE_CIKIS = 1  # Opsiyonel çıkış kamerası. İstemiyorsanız None yapın.

# 2. Web API Ayarları
API_URL = 'http://plate.pikselanalitik.com/api/log_event.php'

# 3. Model Yolu
YOLO_MODEL_PATH = 'C:/Users/Win11/PycharmProjects/Plate/plate2/best.pt'

# 4. Performans Ayarı
#    Motorun kaç karede bir çalışacağını belirler.
PROCESS_EVERY_N_FRAMES = 15

# -------------------------

# Programın zarif bir şekilde kapanmasını sağlamak için global bir flag
is_running = True


def send_plate_to_api(plate_text, camera_id, frame):
    """Tespit edilen yeni plakayı ve o anki GÖRÜNTÜYÜ web sunucusuna gönderir."""
    if not API_URL:
        print(f"[{camera_id.upper()}] UYARI: API_URL ayarlanmamış, veri gönderilemiyor.")
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

    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        print(f"[{camera_id.upper()}] HATA: Kamera kaynağı '{source}' açılamadı.")
        return

    print(f"[{camera_id.upper()}] Kamera '{source}' başarıyla açıldı. Akış başlıyor...")

    detected_plates = set()
    frame_counter = 0

    while is_running:
        ret, frame = cap.read()
        if not ret:
            print(f"[{camera_id.upper()}] UYARI: Kameradan görüntü alınamadı. 5 saniye sonra tekrar denenecek.")
            time.sleep(5)
            continue

        frame_counter += 1
        if frame_counter % PROCESS_EVERY_N_FRAMES == 0:
            results = lpr_engine.process_image(frame)

            for plate_text, coords in results:
                if plate_text not in detected_plates:
                    detected_plates.add(plate_text)
                    print(f"[{camera_id.upper()}] YENİ PLAKA TESPİT EDİLDİ: {plate_text}")
                    # API'ye gönderme işlemini ayrı bir thread'de yapmak,
                    # video akışının takılmasını engeller.
                    api_thread = threading.Thread(target=send_plate_to_api, args=(plate_text, camera_id, frame))
                    api_thread.start()

        # OPSİYONEL: Canlı görüntüyü bir pencerede göstermek için.
        # Eğer bir sunucuda çalıştıracaksanız bu iki satırı yorum satırı yapın (#).
        cv2.imshow(f'Kamera - {camera_id.upper()}', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            is_running = False
            break

    cap.release()
    cv2.destroyAllWindows()
    print(f"[{camera_id.upper()}] Kamera akışı sonlandırıldı.")


def main():
    global is_running

    print("Plaka Tanıma Sistemi (Headless Mod) Başlatılıyor...")
    print("Programı durdurmak için terminale Ctrl+C yapın veya görüntü penceresinde 'q' tuşuna basın.")

    try:
        lpr_engine = LPREngine(detector_model_path=YOLO_MODEL_PATH)
        print("Plaka tanıma motoru başarıyla yüklendi.")
    except Exception as e:
        print(f"KRİTİK HATA: Plaka tanıma motoru yüklenemedi: {e}")
        return

    # Her kamera için ayrı bir thread (iş parçacığı) oluştur
    threads = []

    # Giriş kamerası için thread
    giris_thread = threading.Thread(target=process_camera_stream, args=("giris", CAMERA_SOURCE_GIRIS, lpr_engine))
    threads.append(giris_thread)

    # Eğer tanımlıysa, çıkış kamerası için thread
    if CAMERA_SOURCE_CIKIS is not None:
        cikis_thread = threading.Thread(target=process_camera_stream, args=("cikis", CAMERA_SOURCE_CIKIS, lpr_engine))
        threads.append(cikis_thread)

    # Tüm thread'leri başlat
    for t in threads:
        t.start()

    try:
        # Ana thread'in, diğer thread'ler çalışırken beklemesini sağla
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        print("\nCtrl+C algılandı. Program sonlandırılıyor...")
        is_running = False
        # Thread'lerin bitmesini bekle
        for t in threads:
            t.join()

    print("Sistem başarıyla kapatıldı.")


if __name__ == "__main__":
    main()