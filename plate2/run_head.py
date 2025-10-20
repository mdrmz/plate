# run_headless.py



import cv2

import time

import logging

import os

import sys



# OMP çökme hatasını ve diğer ortam sorunlarını en başta çöz

os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'



# Gerekli importları projenin kökünden yapıyoruz

from core_engine.lpr_engine import LPREngine

from core_engine.api_manager import APIManager

from core_engine.stream_reader import MJPEGStreamReader



# --- AYARLAR ---

CAMERA_SOURCE = "http://admin:123456@192.168.1.34/cgi-bin/snapshot.cgi?stream=0"

MODEL_PATH = "best.pt"

PROCESS_INTERVAL_SECONDS = 5

GATE_ID = "giriş"

API_URL = "http://plate.pikselanalitik.com/api/log_event.php"



# Konsola ve dosyaya loglama için ayarlar

logging.basicConfig(level=logging.INFO,

                    format='%(asctime)s - %(levelname)s - %(message)s',

                    handlers=[

                        logging.FileHandler("headless_app.log"),

                        logging.StreamHandler(sys.stdout)

                    ])



def main():

    logging.info("Headless Plaka Tanıma Sistemi Başlatılıyor (HTTP/MJPEG Stream)…")

    

    try:

        engine = LPREngine(detector_model_path=MODEL_PATH)

        api_manager = APIManager()

        logging.info("Gerekli motorlar başarıyla yüklendi.")

    except Exception as e:

        logging.critical(f"Motorlar yüklenirken kritik bir hata oluştu: {e}", exc_info=True)

        return



    stream_reader = MJPEGStreamReader(url=CAMERA_SOURCE)

    stream_reader.start()



    logging.info("Kamera bağlantısının kurulması için 3 saniye bekleniyor...")

    time.sleep(3)



    last_process_time = 0

    

    while True:

        try:

            ret, frame = stream_reader.read()

            

            if not ret:

                logging.warning("Stream'den kare alınamıyor, bekleniyor...")

                time.sleep(2)

                continue

            

            current_time = time.time()

            if (current_time - last_process_time) > PROCESS_INTERVAL_SECONDS:

                last_process_time = current_time

                logging.info("Tarama zamanı geldi, kare işleniyor...")

                

                results = engine.process_image(frame)

                

                if results:

                    for plate_text, _ in results:

                        logging.info(f"Plaka bulundu: {plate_text}. API'ye gönderiliyor...")

                        api_manager.send_plate_data(plate_text, GATE_ID, frame)

                else:

                    logging.info("Bu karede plaka bulunamadı.")

            

            time.sleep(0.01)



        except KeyboardInterrupt:

            logging.info("Program sonlandırılıyor..."); break

        except Exception as e:

            logging.error(f"Ana döngüde beklenmedik bir hata oluştu: {e}", exc_info=True)

            time.sleep(10)



    stream_reader.stop()

    logging.info("Sistem kapatıldı.")



# DÜZELTİLDİ: Bu satırın doğru yazılışı programın çalışmasını sağlar

if __name__ == "__main__":

    main()
