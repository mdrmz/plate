import logging
import time
from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory

class GateController:
    def __init__(self, servo_pin=18):
        self.servo = None
        # Bu açıları kendi kumanda/servo montajına göre ayarlaman gerekecek
        self.angle_release = -0.5  # Bırakma pozisyonu (-1.0 ile 1.0 arası)
        self.angle_press = 0.5   # Basma pozisyonu (-1.0 ile 1.0 arası)
        
        try:
            factory = PiGPIOFactory() # Servo titremesini önler
            self.servo = Servo(servo_pin, pin_factory=factory)
            self.servo.value = self.angle_release # Başlangıçta tuşu bırak
            logging.info(f"Servo motor GPIO {servo_pin} pininde başlatıldı.")
        except Exception as e:
            logging.error(f"HATA: Servo motor başlatılamadı. 'sudo systemctl start pigpiod' komutunu çalıştır. Hata: {e}")

    def open_gate(self):
        if not self.servo:
            logging.warning("Servo motor aktif değil, tuşa basılamıyor.")
            return
        try:
            logging.info("KAPI AÇILIYOR: Tuşa basılıyor...")
            self.servo.value = self.angle_press; time.sleep(0.5)
            self.servo.value = self.angle_release
            logging.info("Tuş bırakıldı.")
        except Exception as e:
            logging.error(f"Servo kontrolü sırasında hata: {e}")