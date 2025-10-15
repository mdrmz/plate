# app.py

import os
import sys

# OMP çökme hatasını önlemek için BU İKİ SATIRI EN BAŞA EKLEYİN
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

import logging
from PySide6.QtWidgets import QApplication

# Gerekli importları projenin kökünden, paket yapısını kullanarak yapıyoruz
from gui.main_window import MainWindow

# Konsola ve dosyaya loglama için ayarlar
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("app.log"),
                        logging.StreamHandler()
                    ])

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Model yolunu burada merkezi olarak yönet
    model_file = "C:/Users/Win11/PycharmProjects/Plate/plate2/best.pt"

    # Ana pencereyi oluştur ve göster
    logging.info("Uygulama başlatılıyor...")
    win = MainWindow(model_path=model_file)
    win.show()

    sys.exit(app.exec())