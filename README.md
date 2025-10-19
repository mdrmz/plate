# Piksel Analitik - Akıllı Plaka Tanıma Sistemi

Bu proje, gerçek zamanlı video akışlarından (IP Kamera, Webcam) plaka tespiti ve okuması yapan, sonuçları bir web API'sine gönderen ve modern bir yönetim paneli üzerinden sunan uçtan uca bir sistemdir. Sistem, özellikle Raspberry Pi gibi gömülü sistemler üzerinde "headless" (arayüzsüz) çalışacak şekilde optimize edilmiştir.

![Yönetim Paneli Ekran Görüntüsü](https://i.imgur.com/K7wXf9T.png)

## 核心 özellikler

### Plaka Tanıma Uygulaması (Python)
- **Gerçek Zamanlı Plaka Tespiti:** Yüksek doğruluklu, özel eğitilmiş **YOLOv8** modeli ile video akışlarındaki plakaları anlık olarak tespit eder.
- **Güçlü Karakter Okuma (OCR):** Karakterleri okumak için **EasyOCR** motorunu kullanır. Bu, farklı ışık koşulları ve plaka tiplerine karşı yüksek dayanıklılık sağlar.
- **"Headless" Çalışma Modu:** Raspberry Pi gibi cihazlarda kaynakları verimli kullanmak için herhangi bir grafik arayüz olmadan, arka planda bir servis olarak çalışır.
- **Stabil Video Akışı:** Standart `cv2.VideoCapture`'ın kararsız olabildiği IP kameralar için, `requests` tabanlı **MJPEG stream reader** ile donma yapmayan ve bağlantı koptuğunda otomatik yeniden bağlanan bir yapıya sahiptir.
- **API Entegrasyonu:** Tespit edilen her plakayı, anlık kamera görüntüsüyle birlikte belirtilen bir web API'sine güvenli bir şekilde gönderir.

### Yönetim Paneli (PHP & MariaDB)
- **Modern ve Duyarlı Arayüz:** **Bootstrap 5** ile tasarlanmış, mobil cihazlarda ve masaüstünde harika görünen estetik bir arayüz.
- **Canlı Log Takibi:** Sistemin tespit ettiği tüm giriş/çıkış olaylarını anlık olarak listeler.
- **Akıllı Durum Tespiti:** Tespit edilen plakaların sistemde **"Kayıtlı"** mı yoksa **"Yabancı"** mı olduğunu otomatik olarak belirler ve etiketler.
- **Gelişmiş Filtreleme:** Kayıtları; plaka/isim, tarih aralığı, kayıt durumu ve işlem tipine göre detaylı bir şekilde filtreleme imkanı.
- **Toplu İşlemler:** Listelenen kayıtlardan birden fazlasını seçerek tek seferde silme özelliği.
- **Kullanıcı ve Araç Yönetimi (CRUD):** Sisteme yeni araç sahipleri ve araçları ekleme, mevcut olanları düzenleme ve silme için tam teşekküllü bir yönetim arayüzü.

## 🚀 Kullanılan Teknolojiler

- **Python Uygulaması:**
  - Python 3.9+
  - OpenCV
  - Ultralytics (YOLOv8)
  - EasyOCR & PyTorch
  - Requests
  - NumPy
- **Web Paneli:**
  - PHP 8+
  - MariaDB (veya MySQL)
  - Apache2
  - Bootstrap 5

## 🔧 Kurulum

Sistemi Raspberry Pi veya Debian/Ubuntu tabanlı bir sunucuya kurmak için aşağıdaki adımları izleyin.

### 1. Web Sunucusu (LAMP Stack) Kurulumu
Öncelikle PHP panelinin çalışacağı ortamı hazırlayın.
```bash
# Sistem paketlerini güncelle
sudo apt update && sudo apt upgrade -y

# Gerekli web sunucusu bileşenlerini kur
sudo apt install -y apache2 mariadb-server php libapache2-mod-php php-mysql
```
Kurulumdan sonra `sudo mysql_secure_installation` komutu ile veritabanı güvenliğini yapılandırın.

### 2. Veritabanı Kurulumu
MariaDB/MySQL'e bağlanarak gerekli veritabanını ve tabloları oluşturun.
```bash
sudo mysql
```
Açılan komut satırına aşağıdaki SQL kodlarını yapıştırın:
```sql
CREATE DATABASE plaka_sistemi CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE plaka_sistemi;

CREATE TABLE `kullanicilar` (
  `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `ad` VARCHAR(100) NOT NULL,
  `soyad` VARCHAR(100) NOT NULL,
  `telefon` VARCHAR(20) DEFAULT NULL,
  `kayit_tarihi` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE `araclar` (
  `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `plaka` VARCHAR(20) NOT NULL UNIQUE,
  `kullanici_id` INT NOT NULL,
  `ozel_erisim` TINYINT(1) NOT NULL DEFAULT 0,
  FOREIGN KEY (`kullanici_id`) REFERENCES `kullanicilar` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE `giris_cikis_loglari` (
  `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `plaka` VARCHAR(20) NOT NULL,
  `arac_id` INT DEFAULT NULL,
  `islem_tipi` ENUM('giris', 'cikis') NOT NULL,
  `islem_zamani` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `resim_yolu` VARCHAR(255) DEFAULT NULL,
  FOREIGN KEY (`arac_id`) REFERENCES `araclar` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB;
```

### 3. Python Ortamı ve Kütüphaneleri Kurulumu
Plaka tanıma uygulamasının çalışacağı izole ortamı oluşturun.
```bash
# Gerekli sistem bağımlılıklarını kur
sudo apt install -y python3-pip python3-venv libopencv-dev python3-opencv

# Proje klasörüne git ve sanal ortam oluştur
cd /path/to/your/python_lpr
python3 -m venv lpr_env
source lpr_env/bin/activate

# Gerekli Python kütüphanelerini yükle
pip install --upgrade pip
pip install opencv-python ultralytics easyocr torch torchvision requests mysql-connector-python
```

## ⚙️ Yapılandırma

Çalıştırmadan önce aşağıdaki dosyaları kendi sisteminize göre yapılandırmanız gerekmektedir.

1.  **Web Paneli Veritabanı Bağlantısı:**
    - `web_panel/api/db_config.php` dosyasını açın.
    - `$username`, `$password`, `$dbname` değişkenlerini kendi MariaDB kurulumunuza göre güncelleyin.

2.  **Python Uygulaması Ayarları:**
    - `python_lpr/run_headless.py` dosyasını açın.
    - En üstteki `AYARLAR` bölümünü yapılandırın:
        - `CAMERA_SOURCE`: Kameranızın RTSP/HTTP URL'sini veya webcam numarasını (`0`, `1`...) girin.
        - `MODEL_PATH`: `best.pt` modelinin tam yolunu girin.
        - `API_URL`: Web panelinizin `log_event.php` dosyasının tam URL'sini girin (Eğer aynı cihazda çalışıyorsa `http://localhost/api/log_event.php` yeterlidir).

## ▶️ Nasıl Çalıştırılır?

1.  **Web Panelini Aktif Et:** `web_panel/` klasörünün içindeki `api`, `admin`, ve `uploads` klasörlerini web sunucunuzun ana dizinine (`/var/www/html/`) kopyalayın. `uploads` klasörüne yazma izni verin (`sudo chown -R www-data:www-data /var/www/html/uploads`).

2.  **Python Uygulamasını Başlat:**
    ```bash
    # Projenin Python klasörüne gidin
    cd /path/to/your/python_lpr

    # Sanal ortamı aktif edin
    source lpr_env/bin/activate

    # Uygulamayı başlatın
    python run_headless.py
    ```
    Uygulama arka planda çalışmaya başlayacak, tespit ettiği plakaları API'ye gönderecek ve tüm işlemleri `headless_app.log` dosyasına kaydedecektir.

3.  **Yönetim Panelini Görüntüle:**
    - Tarayıcınızı açın ve `http://<RASPBERRY_PI_IP_ADRESI>/admin/` adresine gidin.

---
**Piksel Analitik** adına Mehmet Durmaz tarafından geliştirilmiştir.
