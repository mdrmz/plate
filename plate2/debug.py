import cv2
import os
import logging
import sys
import time

os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

from core_engine.lpr_engine import LPREngine
from core_engine.stream_reader import MJPEGStreamReader

# --- AYARLAR ---
CAMERA_SOURCE = "http://admin:123456@192.168.1.34/cgi-bin/snapshot.cgi?stream=0"
MODEL_PATH = "best.pt"
DEBUG_OUTPUT_DIR = "debug_output" # Çıktı resimlerinin kaydedileceği klasör

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', stream=sys.stdout)

def main():
    logging.info("Görsel Hata Ayıklama Modu Başlatılıyor...")
    
    # Çıktı klasörünü oluştur
    os.makedirs(DEBUG_OUTPUT_DIR, exist_ok=True)
    
    try:
        engine = LPREngine(detector_model_path=MODEL_PATH)
        logging.info("Gerekli motorlar başarıyla yüklendi.")
    except Exception as e:
        logging.critical(f"Motorlar yüklenirken hata: {e}", exc_info=True)
        return

    stream_reader = MJPEGStreamReader(url=CAMERA_SOURCE)
    stream_reader.start()
    logging.info("Kamera bağlantısı kuruluyor, ilk karenin alınması bekleniyor...")
    time.sleep(5) # Bağlantı ve ilk kare için bolca zaman ver

    ret, frame = stream_reader.read()
    stream_reader.stop() # Sadece tek bir kare alacağımız için stream'i durdur

    if not ret or frame is None:
        logging.error("Kameradan kare alınamadı. Lütfen bağlantıyı ve URL'yi kontrol edin.")
        return

    # --- HATA AYIKLAMA ADIMLARI ---

    # 1. Orijinal kareyi kaydet
    cv2.imwrite(os.path.join(DEBUG_OUTPUT_DIR, "01_original_frame.jpg"), frame)
    logging.info("1. Orijinal kare 'debug_output/01_original_frame.jpg' olarak kaydedildi.")

    # 2. YOLO'nun gördüğü kareyi kaydet
    yolo_input = cv2.resize(frame, (320, 320))
    cv2.imwrite(os.path.join(DEBUG_OUTPUT_DIR, "02_yolo_input.jpg"), yolo_input)
    logging.info("2. YOLO'ya gönderilen 320x320 kare kaydedildi.")

    # 3. Plaka tespiti yap ve sonuçları çiz
    plate_coords_yolo = engine.detector.detect(yolo_input)
    
    frame_with_detections = frame.copy()
    if plate_coords_yolo:
        logging.info(f"3. YOLO {len(plate_coords_yolo)} adet potansiyel plaka buldu.")
        h_orig, w_orig = frame.shape[:2]
        
        for i, (x1_y, y1_y, x2_y, y2_y) in enumerate(plate_coords_yolo):
            # Koordinatları orijinal resim boyutuna ölçekle
            x1 = int(x1_y * w_orig / 320)
            y1 = int(y1_y * h_orig / 320)
            x2 = int(x2_y * w_orig / 320)
            y2 = int(y2_y * h_orig / 320)
            
            # Bulunan kutuyu orijinal resme çiz
            cv2.rectangle(frame_with_detections, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # 4. Kırpılan plakayı kaydet
            plate_image = frame[y1:y2, x1:x2]
            if plate_image.size > 0:
                plate_filename = f"04_cropped_plate_{i}.jpg"
                cv2.imwrite(os.path.join(DEBUG_OUTPUT_DIR, plate_filename), plate_image)
                logging.info(f"4. Kırpılan plaka '{plate_filename}' olarak kaydedildi.")

                # 5. Kırpılan plakayı okumayı dene
                plate_text = engine.recognizer.recognize(plate_image)
                logging.info(f"5. OCR Sonucu: '{plate_text}'")
                
    else:
        logging.warning("3. YOLO bu karede HİÇBİR plaka tespit edemedi.")

    cv2.imwrite(os.path.join(DEBUG_OUTPUT_DIR, "03_yolo_detections.jpg"), frame_with_detections)
    logging.info("YOLO tespitlerinin çizildiği kare '03_yolo_detections.jpg' olarak kaydedildi.")
    logging.info("Hata ayıklama tamamlandı. Lütfen 'debug_output' klasörünü kontrol edin.")

if __name__ == "__main__":
    main()
