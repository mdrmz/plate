# run_headless.py
import cv2
import time
import logging
import os
import sys
import argparse

os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

from core_engine.lpr_engine import LPREngine
from core_engine.api_manager import APIManager
# RTSP için MJPEGStreamReader'a ihtiyacımız yok

# --- AYARLAR ---
MODEL_PATH = "best.pt"
PROCESS_INTERVAL_SECONDS = 5

# DEĞİŞTİ: Veritabanı ve API Ayarları (Senin PHP koduna göre güncellendi)
# Raspberry Pi'nin sunucudaki veritabanına bağlanması için gereken bilgiler.
DB_CONFIG = {
    'host': 'plate.pikselanalitik.com', # Sunucunun alan adı veya IP adresi
    'user': 'pikselan_plate',          # Senin PHP kodundaki $username
    'password': 'KWw7m#]mid4O@Gt-',      # Senin PHP kodundaki $password
    'database': 'pikselan_plate'       # Senin PHP kodundaki $dbname
}
API_URL = "http://plate.pikselanalitik.com/api/log_event.php"

# DONANIM AYARLARI (Servo Pinleri)
# İki kapı da AYNI servoyu (GPIO 18) tetikleyecek
GATE_SERVO_PINS = { 'giris': 18, 'cikis': 18 }
# -----------------

parser = argparse.ArgumentParser(description="Headless Plaka Tanıma Motoru")
parser.add_argument("--camera", required=True, help="Kameranın tam RTSP URL'si")
parser.add_argument("--gate", required=True, choices=['giris', 'cikis'], help="Kapı ID'si ('giris' veya 'cikis')")
args = parser.parse_args()

log_file_name = f"headless_{args.gate}.log"
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - [%(name)s] - %(message)s',
                    handlers=[logging.FileHandler(log_file_name), logging.StreamHandler(sys.stdout)])
logger = logging.getLogger(args.gate.upper())

def main():
    logger.info(f"Sistem Başlatılıyor - Kapı: {args.gate}, Kaynak: {args.camera}")
    
    try:
        servo_pin = GATE_SERVO_PINS.get(args.gate)
        if servo_pin is None:
            logger.error(f"'{args.gate}' için servo pini tanımlanmamış. Kapı açma çalışmayacak.")
        
        # LPREngine'i güncellenmiş DB_CONFIG ile başlat
        engine = LPREngine(detector_model_path=MODEL_PATH, 
                           db_config=DB_CONFIG, 
                           servo_pin=servo_pin)
                           
        api_manager = APIManager(api_url=API_URL)
        logger.info("Motorlar başarıyla yüklendi.")
    except Exception as e:
        logger.critical(f"Motorlar yüklenirken kritik hata: {e}", exc_info=True); return

    cap = None
    last_process_time = 0
    
    while True:
        try:
            if cap is None or not cap.isOpened():
                logger.info(f"RTSP kaynağına bağlanılıyor: {args.camera}...")
                os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"
                cap = cv2.VideoCapture(args.camera, cv2.CAP_FFMPEG)
                
                if not cap.isOpened():
                    logger.error("Kameraya bağlanılamadı. 10 saniye sonra tekrar denenecek...")
                    time.sleep(10)
                    continue
                logger.info("Kamera bağlantısı başarılı.")

            ret, frame = cap.read()
            if not ret:
                logger.warning("Kameradan kare okunamadı. Yeniden bağlanılıyor..."); cap.release(); cap = None; time.sleep(5)
                continue
            
            current_time = time.time()
            if (current_time - last_process_time) > PROCESS_INTERVAL_SECONDS:
                last_process_time = current_time
                logger.info("Tarama zamanı geldi, kare işleniyor...")
                results = engine.process_image(frame)
                if results:
                    for plate_text, _ in results:
                        logger.info(f"Plaka bulundu: {plate_text}. API'ye gönderiliyor...")
                        api_manager.send_plate_data(plate_text, args.gate, frame)
                else:
                    logger.info("Bu karede plaka bulunamadı.")
            time.sleep(0.01)

        except KeyboardInterrupt:
            logger.info("Program sonlandırılıyor..."); break
        except Exception as e:
            logger.error(f"Ana döngüde hata: {e}", exc_info=True); time.sleep(10)

    if cap: cap.release()
    logger.info("Sistem kapatıldı.")

if __name__ == "__main__":
    main()