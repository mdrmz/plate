# 🅿️ HEZARFEN LPR© :: Endüstriyel Otonom Geçiş Kontrol Platformu
## (v2.0 - Tam Otonom "Çift Motorlu" Kenar Cihazı)

[![AI Engine](https://img.shields.io/badge/AI%20Engine-YOLOv8%20(Dual%20Motor)-9932CC?style=for-the-badge)](https://ultralytics.com/)
[![Deployment](https://img.shields.io/badge/Deployment-100%25%20Offline%20Edge-blueviolet?style=for-the-badge)](https://www.raspberrypi.com/products/raspberry-pi-5/)
[![Hardware](https://img.shields.io/badge/Hardware-Raspberry%20Pi%205%20(64--bit)-orange?style=for-the-badge)](https://www.raspberrypi.com/products/raspberry-pi-5/)
[![Status](https://img.shields.io/badge/Status-G%C3%B6rev%20Kritik%20(7/24)-green?style=for-the-badge)](https://github.com/)

Bu, bir plaka tanıma script'i değildir. Bu, **Piksel Analitik Ar-Ge** departmanının sahadaki en zorlu koşullara (ışık, gölge, açı, donanım uyumsuzlukları) karşı verdiği mücadelenin ve mühendislik zaferinin bir özetidir.

Bu platform, internete **ihtiyaç duymayan**, tüm kararları milisaniyeler içinde **Raspberry Pi 5** üzerinde otonom olarak alan ve `findContours` gibi ilkel yöntemlerin cehenneminden bizi kurtaran, çift yapay zeka motorlu bir "Edge AI" zeka platformudur.

---

## ⚔️ Savaş Alanı: Çılgınlığın Üstesinden Gelmek

Bu projeye giden yol, başarısızlıklarla ve "çöp" sonuçlarla doluydu. Sahadaki her LPR sisteminin kabusu olan problemleri tek tek tespit ettik ve yendik:

1.  **DÜŞMAN 1: Klasik OpenCV (`findContours`)**
    * **Problem:** Işığa, gölgeye ve vida deliklerine karşı aşırı kırılgandı.
    * **Felaket Sonuç:** `34JILIDIE301` gibi "karakter çorbası" sonuçlar üretiyordu.
    * **Durum:** **YENİLDİ.**

2.  **DÜŞMAN 2: Jenerik OCR Motorları (`EasyOCR` / `Tesseract`)**
    * **Problem:** Plaka fontlarını tanımak için değil, genel dokümanları okumak için eğitilmişlerdi. `TR` logosu ve vida delikleri kafalarını karıştırıyordu.
    * **Felaket Sonuç:** `34LD6301`'i `04IO6Z04` veya `34ID6J01` olarak yanlış okuyordu.
    * **Durum:** **YENİLDİ.**

3.  **DÜŞMAN 3: Ezberci Modeller (İlk Keras Denemesi)**
    * **Problem:** Kendi eğittiğimiz ilk sınıflandırma modeli o kadar "overfit" olmuştu ki, harfleri değil, harflerin arkasındaki **arka planı** ezberlemişti.
    * **Felaket Sonuç:** O efsanevi `arkaplan40YH0A6404` hatası.
    * **Durum:** **YENİLDİ.**

---

## 🏆 Nihai Çözüm: "İki Aşamalı Çift Motorlu" YOLO Mimarisi

Tüm bu düşmanları yenmek için, sıfırdan, devrim niteliğinde bir mimari tasarladık. Artık "karakter ayırma" (segmentasyon) işini, `findContours` gibi ilkel yöntemlere değil, doğrudan ikinci bir yapay zeka motoruna bıraktık.

* **MOTOR 1 (Plaka-YOLO - `best.pt`):**
    * **Görevi:** Tam kamera görüntüsünü alır ve sahnedeki **plakanın yerini** %99 doğrulukla bulur, kırpar.

* **MOTOR 2 (Karakter-YOLO - `char2.pt`):**
    * **Görevi:** Motor 1'in kırptığı o küçük plaka resmini alır. `findContours`'un aksine, ışık veya gölgeden etkilenmez. Sadece plaka fontlarını tanımak için eğitilmiş bu canavar, plakanın içindeki **her bir karakteri** tek tek bulur ve **ne olduğunu** söyler (`3`, `4`, `L`, `D`...).

Bu mimari, `TensorFlow`, `Keras`, `EasyOCR`, `Tesseract` gibi onlarca ağır ve problemli kütüphaneyi çöpe atmamızı sağladı. Sistem artık **sadece `ultralytics` (YOLO) ve `opencv`** ile "mis gibi" çalışıyor.

---

## 🤖 Saha Testi: Raspberry Pi 5'in Çelik İradesi (Kurulum & Stabilite)

Bu zekayı sahaya kurmak, kod yazmaktan daha zordu. Pi 5'i, 7/24 çalışacak otonom bir "görev kritik" cihaza dönüştürdük:

1.  **Otonom Başlangıç & Kendi Kendini İyileştirme (`systemd`):**
    * Sistem için özel bir `lpr-motor.service` yazdık. Raspberry Pi'nin fişi çekilip takılsa bile, sistem **otomatik olarak başlar**.
    * `Restart=on-failure` parametresi sayesinde, RTSP akışı kopsa veya Python script'i beklenmedik bir hata ile **çökse bile**, `systemd` 15 saniye içinde servisi **otomatik olarak yeniden başlatır**. Sistem kendi kendini iyileştirir.

2.  **Önleyici Bakım & Isı Yönetimi (`cronjob`):**
    * Yapay zeka motorlarının uzun süreli çalışması RAM'i doldurabilir ve bu da Pi'nin ısınmasına neden olabilir.
    * Bunu engellemek için, bir `cronjob` (zamanlanmış görev) kurduk. Sistem, her gece 00:00'da (veya saatte bir) kendini **planlı olarak yeniden başlatır**. Bu, bellek (RAM) sızıntılarını temizler ve Pi'nin her zaman taze ve serin kalmasını sağlar.

3.  **Temiz Kurulum (64-bit Gücü):**
    * Tüm `armv7l` (32-bit) hatalarını geride bıraktık. Pi 5'e **64-bit** işletim sistemi kurduk ve `install_pi_final.sh` ile sadece ve sadece ihtiyacımız olan (PyTorch, Ultralytics, OpenCV) kütüphaneleri kuran temiz bir sanal ortam (`lpr_yolo_env`) oluşturduk.

---

## 🔩 Donanım Mükemmelliği: Titremeyen Servo (`gate_controller`)

Projenin en inatçı sorunlarından biri de servo motoruydu. Zayıf sinyaller nedeniyle "titreme" (`jitter`) yapıyor veya tuşa tam basmıyordu. Bunu da aştık:

1.  **Güçlü Sinyal (`PiGPIOFactory`):** Standart `gpiozero` kütüphanesi yerine, donanımsal PWM (darbe) üreten `PiGPIOFactory` kütüphanesini kullandık. Bu, Pi'den servoya giden sinyali **kaya gibi stabil** hale getirdi ve titremeyi %100 yok etti.
2.  **Yeterli Güç (Harici Amper):** Servonun, Pi'nin 5V pininden değil, **harici bir 5V güç kaynağından** (yeterli Amper sağlayan) beslenmesini sağladık.

**Sonuç:** Servo motor artık her seferinde kusursuz, kararlı ve güçlü bir şekilde kapı kumandasının tuşuna basıyor.

---

## ✨ Nihai Platform Özellikleri (v2.0 - Otonom)

* **%100 Offline:** İnternet olmadan, `allowed_plates.txt` dosyasından plaka okuyor.
* **Otonom Kayıt:** Tüm giriş/çıkışları `gate_log.csv` dosyasına otomatik kaydediyor.
* **Çift Kamera Desteği:** İki kamerayı (Giriş/Çıkış) aynı anda, takılmadan işliyor.
* **Akıllı Tanıma:** Plakaları 1 harf hatayla (Levenshtein) tanıyıp gürültüyü (modelin bulduğu `license plates` yazısını) filtreliyor.
* **Tam Otomatik:** RPi açıldığında `systemd` ile kendi kendine başlıyor, çökerse yeniden başlıyor.
* **Stabil Bakım:** `cronjob` ile periyodik RAM temizliği (restart) yapıyor.
* **Güçlü Donanım:** `PiGPIOFactory` ve Harici Güç sayesinde servo motor artık kusursuz çalışıyor.

---

*Bu teknoloji platformu, **Mehmet Durmaz**'ın liderliğinde, aylarca süren Ar-Ge, deneme-yanılma ve sayısız "çökme"nin ardından, **Piksel Analitik**'in "Geleceği Bugünden Tasarlama" vizyonuyla geliştirilmiştir.*
*© 2025 Piksel Analitik - Otonom Kenar Bilişim Çözümleri*
