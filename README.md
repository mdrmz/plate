# 🅿️ Piksel Analitik - Yeni Nesil Plaka Tanıma Motoru (LPR Engine)

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/YOLO-v8-blueviolet.svg)](https://ultralytics.com/)
[![OCR](https://img.shields.io/badge/OCR-EasyOCR-orange.svg)](https://github.com/JaidedAI/EasyOCR)
[![Web](https://img.shields.io/badge/Backend-PHP%208-777BB4.svg)](https://www.php.net/)
[![Database](https://img.shields.io/badge/Database-MariaDB-003545.svg)](https://mariadb.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Piksel Analitik LPR Engine**, kurumsal düzeyde ihtiyaçları karşılamak üzere tasarlanmış, uçtan uca, yapay zeka tabanlı bir plaka tanıma ve araç takip sistemidir. Gerçek zamanlı video akışlarını analiz ederek elde ettiği verileri, modern bir web paneli üzerinden anlık olarak sunar. Sistem, özellikle Raspberry Pi gibi gömülü sistemlerde 7/24 stabil çalışacak şekilde optimize edilmiştir.

---

### Proje Vizyonu
Bu proje, sadece bir plaka okuma script'i olmanın ötesinde; otopark yönetimi, güvenlikli site girişleri, lojistik takip ve akıllı şehir uygulamaları gibi senaryolarda kullanılabilecek, ölçeklenebilir ve modüler bir platformun temelini oluşturur.

![Yönetim Paneli Animasyonu](https://i.imgur.com/K7wXf9T.png)
*<p align="center">Gelişmiş Filtreleme ve Anlık Durum Tespiti Sunan Modern Yönetim Paneli</p>*

---

## 🏛️ Sistem Mimarisi

Sistem, birbirinden bağımsız ama birbiriyle mükemmel uyum içinde çalışan iki ana modülden oluşur: **Python LPR Motoru** ve **PHP Web Platformu**.

```
[IP KAMERA] --(MJPEG Stream)--> [PYTHON LPR MOTORU] --(HTTP POST)--> [PHP API] --> [MARIADB]
                                                                                           ^
                                                                                           |
                                                                                     [PHP WEB PANELİ] --(Okuma/Yazma)--> [KULLANICI]
```
Bu mimari, plaka tanıma işleminin yoğun yükünü arayüzden tamamen ayırarak maksimum performans ve stabilite sağlar.

---

## ✨ Öne Çıkan Özellikler

### 🧠 Python LPR Motoru (Beyin)
- **🚀 Son Teknoloji Plaka Tespiti:** Özel olarak eğitilmiş **YOLOv8** modeli sayesinde, zorlu açılarda ve düşük ışık koşullarında bile yüksek doğrulukla plaka tespiti yapar.
- **🎯 Yüksek Başarımlı OCR:** Geleneksel OCR motorlarının zorlandığı durumlarda dahi üstün performans gösteren, derin öğrenme tabanlı **EasyOCR** motoru ile karakterleri okur.
- **🔒 Kesintisiz Çalışma:** IP kamera bağlantısı koptuğunda veya bir hata oluştuğunda, çökmek yerine otomatik olarak **yeniden bağlanmayı deneyen** akıllı `MJPEGStreamReader` yapısına sahiptir.
- **⚡ Optimize Edilmiş Performans:** Raspberry Pi gibi kaynakları kısıtlı cihazlar için özel olarak optimize edilmiştir. "Headless" çalışma modu ve periyodik tarama özelliği ile CPU kullanımını minimumda tutar.

### 💻 PHP Web Platformu (Kontrol Merkezi)
- **🌐 Modern ve Etkileşimli Arayüz:** **Bootstrap 5** ile geliştirilmiş, her cihazda kusursuz çalışan, estetik ve kullanıcı dostu bir yönetim paneli.
- **📊 Anlık Veri Akışı ve Analiz:** Tespit edilen tüm araç hareketlerini anlık olarak listeler. **"Kayıtlı"** ve **"Yabancı"** araçları renk kodlarıyla anında ayırt eder.
- **🔍 Gelişmiş Arama ve Filtreleme:** Kayıtları; **plaka/isim**, **tarih aralığı**, **kayıt durumu** ve **işlem tipine** göre saniyeler içinde filtreleyerek aradığınız veriye anında ulaşmanızı sağlar.
- **🛠️ Tam Teşekküllü CRUD Yönetimi:** Sisteme yeni kullanıcılar ve araçlar eklemek, mevcut olanları **düzenlemek** ve silmek için eksiksiz bir arayüz sunar.
- **🔗 Akıllı Entegrasyon:** "Yabancı" olarak tespit edilen bir plakanın yanındaki tek bir butona basarak, o plakayı anında sisteme kaydetme formunu açar.
- **🗑️ Güvenli Toplu İşlemler:** Yüzlerce kaydı tek bir tıkla seçip, hem veritabanından hem de sunucudan ilgili resim dosyalarıyla birlikte **kalıcı olarak silme** imkanı.

---

## 🔧 Kurulum ve Yapılandırma

Detaylı kurulum adımları ve kodlar projenin diğer dosyalarında mevcuttur. Başlamak için `setup.sh` script'i (Linux/Pi için) veya manuel kurulum adımları izlenebilir.

### Gerekli Yapılandırmalar:
1.  **Veritabanı:** `web_panel/api/db_config.php` dosyasında veritabanı bağlantı bilgilerinizi girin.
2.  **Python Motoru:** `python_lpr/run_headless.py` dosyasının en üstündeki `AYARLAR` bölümünü kendi sisteminize göre (kamera URL'si, model yolları vb.) düzenleyin.

## ▶️ Kullanım

Sistem kurulduktan ve yapılandırıldıktan sonra, plaka tanıma motoru arka planda bir servis olarak çalıştırılır. Yönetim paneline ise herhangi bir web tarayıcıdan erişilebilir.

```bash
# Python motorunu başlatmak için (örnek):
cd /path/to/python_lpr
source lpr_env/bin/activate
python run_headless.py
```

---
*Bu proje, **Mehmet Durmaz** tarafından **Piksel Analitik** için geliştirilmiştir.*
*Akıllı Görüntü Analizi ve Karar Destek Sistemleri*
