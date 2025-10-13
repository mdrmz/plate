import requests
import cv2

# --- 🎯🎯🎯 AYARLAR 🎯🎯🎯 ---
# Lütfen bu satıra, web sunucunuzdaki log_event.php dosyasının
# TAM VE DOĞRU web adresini yazın.
API_URL = 'http://plate.pikselanalitik.com/api/log_event.php'

# Test için göndereceğimiz sahte plaka
TEST_PLATE = "34TEST123"

# Test için göndereceğimiz sahte resim dosyası
# Projenizin ana klasöründe 'test_image.jpg' adında herhangi bir resim dosyası olduğundan emin olun.
TEST_IMAGE_PATH = 'C:/Users/Win11/PycharmProjects/Plate/plate2/data/1.jpg'


# -----------------------------

def run_api_test():
    print("--- API Bağlantı Testi Başlatıldı ---")

    # 1. Test resmini oku
    try:
        frame = cv2.imread(TEST_IMAGE_PATH)
        if frame is None:
            print(f"HATA: '{TEST_IMAGE_PATH}' adında bir resim dosyası bulunamadı!")
            return
        success, encoded_image = cv2.imencode('.jpg', frame)
        if not success:
            print("HATA: Test resmi .jpg formatına çevrilemedi.")
            return
    except Exception as e:
        print(f"Resim okunurken hata oluştu: {e}")
        return

    # 2. Gönderilecek verileri hazırla
    payload = {'plate': TEST_PLATE, 'gate': 'test'}
    files = {'image': ('capture.jpg', encoded_image.tobytes(), 'image/jpeg')}

    # 3. Bağlantıyı denemeden önce URL'nin ne olduğunu ekrana yazdır
    print(f"\n[DEBUG] Bağlanılacak URL: '{API_URL}'")

    # 4. API'ye bağlanmayı dene
    try:
        print("API'ye istek gönderiliyor...")
        response = requests.post(API_URL, files=files, data=payload, timeout=10)
        response.raise_for_status()  # HTTP hatalarını yakala

        api_response = response.json()
        print("\n--- BAŞARILI ---")
        print(f"API Cevabı: {api_response.get('message', 'Mesaj yok')}")

    except requests.exceptions.RequestException as e:
        print("\n--- HATA ---")
        print(f"API'ye bağlanırken bir sorun oluştu: {e}")


if __name__ == "__main__":
    run_api_test()