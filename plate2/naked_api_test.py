import requests

# URL'yi burada, hiçbir yerden almadan, doğrudan yazıyoruz.
api_url = "http://plate.pikselanalitik.com/api/log_event.php"

# Değişkenin içeriğini ve tipini kontrol edelim.
print(f"URL Değişkeni: '{api_url}'")
print(f"Değişken Tipi: {type(api_url)}")

# En basit veriyi hazırlayalım. Resim yok, sadece plaka.
# PHP script'i resim bulamayınca hata verebilir ama bu Python tarafında bir InvalidURL hatası olmamalı.
payload = {'plate': 'NAKEDTEST'}

try:
    print("\nBağlantı deneniyor...")

    # Mümkün olan en basit POST isteği.
    response = requests.post(api_url, data=payload, timeout=10)

    print("\n--- BAŞARILI ---")
    print(f"HTTP Durum Kodu: {response.status_code}")
    print(f"Sunucu Cevabı: {response.text}")

except Exception as e:
    print("\n--- HATA ---")
    print(f"Bir hata oluştu: {e}")