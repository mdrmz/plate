# app.py
import sys
from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow

# --- AYARLAR ---
YOLO_MODEL_PATH = 'C:/Users/Win11/PycharmProjects/Plate/plate2/best.pt'

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow(model_path=YOLO_MODEL_PATH)
    window.show()
    sys.exit(app.exec())