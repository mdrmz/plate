# 🅿️ HEZARFEN LPR© :: Otonom Araç Tanımlama ve Stratejik Analiz Platformu

[![AI Engine](https://img.shields.io/badge/AI%20Engine-YOLO12%20%2B%20DeepOCR-9932CC?style=for-the-badge)](https://ultralytics.com/)
[![Deployment](https://img.shields.io/badge/Deployment-Edge%20Ready-blueviolet?style=for-the-badge)](https://www.nvidia.com/en-us/glossary/edge-computing/)
[![Backend](https://img.shields.io/badge/Platform-LAMP%20Stack-777BB4?style=for-the-badge)](https://www.php.net/)
[![Status](https://img.shields.io/badge/Status-Aktif%20Geli%C5%9Ftirme-green?style=for-the-badge)](https://github.com/)

**Hezarfen LPR©**, Piksel Analitik Ar-Ge departmanı tarafından geliştirilen, devrim niteliğinde bir yapay zeka vizyon platformudur. Bu sistem, standart plaka okuma yazılımlarının ötesine geçerek, kenar bilişim (edge computing) cihazları üzerinde otonom olarak çalışan, gerçek zamanlı veri toplayan ve bu veriyi stratejik içgörülere dönüştüren bir zeka motorudur.

---

## 📜 Proje Manifestosu

Gelişen dünyada veri, en değerli varlıktır. Hezarfen LPR, kritik altyapı tesisleri, akıllı şehirler, lojistik merkezleri ve yüksek güvenlikli bölgeler için "durumsal farkındalık" yaratma misyonuyla tasarlanmıştır. Amacımız sadece plakaları okumak değil, bu veriyi analiz ederek anomali tespiti, tahminsel analiz ve operasyonel verimlilik artışı sağlamaktır.

---

## 🏛️ Sistem Mimarisi

Sistem, birbirinden bağımsız ama birbiriyle mükemmel uyum içinde çalışan iki ana modülden oluşur: **Python LPR Motoru** (Kuantum Çekirdeği) ve **PHP Web Platformu** (Orion Komuta Paneli).

```
[IP KAMERA] --(MJPEG/RTSP Stream)--> [KUANTUM ÇEKİRDEĞİ (Python LPR)] --(HTTP POST)--> [ORION API (PHP)] --> [VERİTABANI (MariaDB)]
                                                                                                                         ^
                                                                                                                         |
                                                                                                             [ORION KONTROL PANELİ] --(Okuma/Yazma)--> [OPERATÖR]
```
Bu mimari, plaka tanıma işleminin yoğun yükünü arayüzden tamamen ayırarak maksimum performans ve stabilite sağlar.

---

## ✨ Öne Çıkan Özellikler

### 🧠 **Kuantum Çekirdeği: Kenar Bilişim LPR Motoru** (Python)
- **🚀 Son Teknoloji Plaka Tespiti:** Özel olarak eğitilmiş **YOLO12** modeli sayesinde, zorlu açılarda ve düşük ışık koşullarında bile yüksek doğrulukla plaka tespiti yapar.
- **🎯 Yüksek Başarımlı OCR:** Geleneksel OCR motorlarının zorlandığı durumlarda dahi üstün performans gösteren, derin öğrenme tabanlı **EasyOCR** boru hattı ile karakterleri okur.
- **🔒 Kesintisiz Çalışma:** IP kamera bağlantısı koptuğunda veya bir hata oluştuğunda, çökmek yerine otonom olarak **yeniden bağlanmayı deneyen** akıllı `MJPEGStreamReader` yapısına sahiptir.
- **⚡ Optimize Edilmiş Performans:** Raspberry Pi gibi kaynakları kısıtlı cihazlar için özel olarak optimize edilmiştir. "Headless" çalışma modu ve periyodik tarama özelliği ile CPU kullanımını minimumda tutar.
- **🛡️ Modüler Yapı:** Her bileşen (`PlateDetector`, `PlateRecognizer`, `APIManager`) kendi sınıfı içinde izole edilmiştir. Bu, gelecekte OCR motorunu veya API gönderim mantığını değiştirmeyi inanılmaz derecede kolaylaştırır.

### 💻 **Orion: Komuta ve Kontrol Paneli** (PHP)
- **🌐 Modern ve Etkileşimli Arayüz:** **Bootstrap 5** ile geliştirilmiş, her cihazda kusursuz çalışan, estetik ve kullanıcı dostu bir yönetim paneli.
- **📊 Anlık Veri Akışı ve Analiz:** Tespit edilen tüm araç hareketlerini anlık olarak listeler. **"Kayıtlı"** ve **"Yabancı"** araçları renk kodlarıyla anında ayırt eder.
- **🔍 Gelişmiş Arama ve Filtreleme:** Kayıtları; **plaka/isim**, **tarih aralığı**, **kayıt durumu** ve **işlem tipine** göre saniyeler içinde filtreleyerek aradığınız veriye anında ulaşmanızı sağlar.
- **🛠️ Tam Teşekküllü CRUD Yönetimi:** Sisteme yeni kullanıcılar ve araçlar eklemek, mevcut olanları **düzenlemek** ve silmek için eksiksiz bir arayüz sunar.
- **🔗 Akıllı Entegrasyon:** "Yabancı" olarak tespit edilen bir plakanın yanındaki tek bir butona basarak, o plakayı anında sisteme kaydetme formunu açar.
- **🗑️ Güvenli Toplu İşlemler:** Yüzlerce kaydı tek bir tıkla seçip, hem veritabanından hem de sunucudan ilgili resim dosyalarıyla birlikte **kalıcı olarak silme** imkanı.

---

## 🔧 Kurulum ve Dağıtım (Deployment)

Bu bölüm, sistemin bir Raspberry Pi 4/5 veya Debian/Ubuntu tabanlı bir sunucuya sıfırdan kurulumunu detaylandırmaktadır.

### Ön Gereksinimler
- Raspberry Pi 4 (4GB+) veya Debian/Ubuntu tabanlı bir Linux sistemi.
- İnternet bağlantısı.
- `sudo` yetkilerine sahip bir kullanıcı.

### 1. Web Sunucusu Kurulumu (LAMP Stack)
```bash
# Sistem paketlerini güncelle
sudo apt update && sudo apt upgrade -y

# Gerekli web sunucusu bileşenlerini kur
sudo apt install -y apache2 mariadb-server php libapache2-mod-php php-mysql

# Apache ve MariaDB servislerini etkinleştir ve başlat
sudo systemctl enable apache2
sudo systemctl enable mariadb
sudo systemctl start apache2
sudo systemctl start mariadb

# MariaDB için temel güvenlik ayarlarını yap
sudo mysql_secure_installation
```

### 2. Veritabanı Yapılandırması
MariaDB'ye bağlanarak gerekli veritabanını ve tabloları oluşturun.
```bash
sudo mysql -u root -p
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
  `ozel_erisim` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '0: Normal, 1: Kapıyı açma yetkisi var',
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

EXIT;
```

### 3. Web Paneli Dosyalarının Dağıtımı
Projenin `web_panel` klasöründeki dosyaları Apache'nin ana dizinine kopyalayın.
```bash
# /path/to/project/ kök dizininde olduğunuzu varsayarak:
sudo cp -R web_panel/* /var/www/html/

# `uploads` klasörüne yazma izni ver
sudo chown -R www-data:www-data /var/www/html/uploads
sudo chmod -R 775 /var/www/html/uploads
```
**`web_panel/api/db_config.php`** dosyasını kendi veritabanı bilgilerinizle güncellemeyi unutmayın.

### 4. Python Ortamı Kurulumu
Plaka tanıma uygulamasının çalışacağı izole ortamı oluşturun.
```bash
# Gerekli sistem bağımlılıklarını kur
sudo apt install -y python3-pip python3-venv libopencv-dev python3-opencv

# Projenin Python klasörüne git ve sanal ortam oluştur
cd /path/to/project/python_lpr
python3 -m venv lpr_env
source lpr_env/bin/activate

# Gerekli Python kütüphanelerini yükle (Bu adım uzun sürebilir!)
pip install --upgrade pip
pip install opencv-python ultralytics easyocr torch torchvision requests mysql-connector-python
```

---

## ⚙️ Yapılandırma

`python_lpr/run_headless.py` dosyasını açın ve en üstteki `AYARLAR` bölümünü yapılandırın:
- `CAMERA_SOURCE`: Kameranızın RTSP/HTTP URL'sini veya webcam numarasını (`0`, `1`...) girin.
- `MODEL_PATH`: `best.pt` modelinin tam yolunu girin.
- `API_URL`: Web panelinizin `log_event.php` dosyasının tam URL'sini girin (`http://localhost/api/log_event.php`).

---

## 📡 API Uç Noktası (`/api/log_event.php`)

- **Method:** `POST`
- **Content-Type:** `multipart/form-data`
- **Parametreler:**
  - `plate` (string, zorunlu): Tespit edilen plaka metni.
  - `gate` (string, zorunlu): İşlemin yapıldığı kapı ID'si ('giris', 'cikis').
  - `image` (file, zorunlu): Plakanın tespit edildiği anın JPEG formatındaki görüntüsü.
- **Başarılı Cevap (`200 OK`):**
  ```json
  {"status":"success","message":"Log başarıyla kaydedildi: Plaka=34ABC123, İşlem=giris"}
  ```
- **Hatalı Cevap (`200 OK` veya `400 Bad Request`):**
  ```json
  {"status":"error","message":"Eksik parametreler."}
  ```

---

## 🔭 Yol Haritası (Roadmap) ve Gelecek Vizyonu

Hezarfen LPR, sürekli gelişen bir platformdur. Gelecek sürümlerde planlanan modüller:

-   [ ] **Q1 2026: Isı Haritası (Heatmap) Analizi**
    -   Tespit edilen araçların yoğunluk ve bekleme sürelerini coğrafi bir harita üzerinde görselleştirerek, tesis içindeki "sıcak noktaları" belirleme.
-   [ ] **Q2 2026: Anomali Tespit Motoru**
    -   Belirli bir bölgede beklenenden uzun süre kalan, "beyaz listede" olmayan veya şüpheli hareket patternleri sergileyen araçların yapay zeka tarafından otomatik olarak işaretlenmesi.
-   [ ] **Q3 2026: Tahminsel Analiz Modülü**
    -   Tarihsel veriyi analiz ederek, gelecekteki yoğunluk anlarını ve pik saatleri **tahmin eden** bir makine öğrenmesi modeli.
-   [ ] **Q4 2026: Merkezi Filo Yönetimi**
    -   Birden fazla lokasyondaki Hezarfen LPR motorlarını tek bir merkezi `Orion` panelinden yönetme ve tüm veriyi birleşik bir "Veri Gölü" (Data Lake) üzerinde toplama.

---

*Bu teknoloji platformu, **Mehmet Durmaz**'ın liderliğinde, **Piksel Analitik**'in "Geleceği Bugünden Tasarlama" vizyonuyla geliştirilmektedir.*
*© 2025 Piksel Analitik - Stratejik Görüntü İşleme ve Yapay Zeka Çözümleri*
