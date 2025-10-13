import cv2

# --- AYARLAR ---
# Test etmek istediğiniz kamera kaynağını buraya yazın:
# - Normal bir USB webcam için: 0 (genellikle)
# - DroidCam genellikle ikinci kamera olarak görünür: 1 veya 2'yi deneyin
# - Bir IP kamera için: "rtsp://kullanici:sifre@192.168.1.X:554/stream1"
# - Bir video dosyası için: "test_videos/video.mp4"

CAMERA_SOURCE = 1  # <--- DEĞİŞTİRİLECEK YER BURASI

# ----------------

print(f"Kamera kaynağı deneniyor: {CAMERA_SOURCE}")

# Video yakalama nesnesini oluştur
cap = cv2.VideoCapture(CAMERA_SOURCE)

# Kameranın başarıyla açılıp açılmadığını kontrol et
if not cap.isOpened():
    print("--- HATA ---")
    print(f"Kamera kaynağı '{CAMERA_SOURCE}' AÇILAMADI.")
    print("\nLütfen şunları kontrol edin:")
    print("1. Webcam'iniz başka bir uygulama (Zoom, Skype vb.) tarafından kullanılmıyor mu?")
    print("2. DroidCam kullanıyorsanız, telefon ve bilgisayardaki uygulamanın çalıştığından emin misiniz?")
    print("3. DroidCam için 0 yerine 1 veya 2'yi denediniz mi?")
    print("4. IP kamera URL'si veya dosya yolu doğru yazılmış mı?")
    exit()

print("--- BAŞARILI ---")
print("Kamera başarıyla açıldı. Görüntü akışı başlatılıyor...")
print("Görüntü penceresini kapatmak için 'q' tuşuna basın.")

# Görüntüyü kare kare okumak için döngü
while True:
    # Bir kare oku
    ret, frame = cap.read()

    # Kare doğru okunamadıysa (bağlantı koptuysa vb.), döngüden çık
    if not ret:
        print("Kameradan görüntü alınamadı. Akış sonlandırıldı.")
        break

    # Okunan kareyi ekranda göster
    cv2.imshow("Kamera Testi (Kapatmak icin 'q' tusuna basin)", frame)

    # 'q' tuşuna basılırsa döngüden çık
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Her şey bittiğinde, yakalamayı serbest bırak ve pencereleri kapat
print("Program sonlandırılıyor...")
cap.release()
cv2.destroyAllWindows()