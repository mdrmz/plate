#!/bin/bash

# --- AYARLAR ---
# Lütfen bu bölümü kendi Raspberry Pi kurulumunuza göre DİKKATLİCE düzenleyin!

# Projenizin tam yolu
PROJECT_PATH="/home/pi/lpr_projesi/python_lpr"

# Conda ortamınızın adı
ENV_NAME="lpr_env"

# Pi'deki kullanıcı adınız (genellikle 'pi' olur)
USERNAME="pi"
# -----------------

# Script'in geri kalanı bu ayarları otomatik olarak kullanacaktır.
PYTHON_EXEC_PATH="/home/$USERNAME/anaconda3/envs/$ENV_NAME/bin/python"
SCRIPT_TO_RUN="run_headless.py"
SERVICE_NAME="lpr"
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"

echo "###################################################################"
echo "### Otomatik Başlatma ve Yeniden Başlatma Servisi Kurulumu ###"
echo "###################################################################"
echo

# Kök yetkileriyle çalıştırıldığından emin ol
if [ "$EUID" -ne 0 ]; then 
  echo "HATA: Lütfen bu script'i 'sudo' komutu ile çalıştırın: sudo ./install_scheduler.sh"
  exit 1
fi

echo "--- Adım 1/3: Otomatik Başlatma Servisi Oluşturuluyor ($SERVICE_NAME.service) ---"

# systemd servis dosyasının içeriğini oluştur
# Bu dosya, Pi açıldığında Python script'ini nasıl çalıştıracağını tanımlar
cat > ./$SERVICE_NAME.service << EOF
[Unit]
Description=Piksel Analitik Plaka Tanima Servisi
After=network-online.target # Ağ bağlantısı tamamen kurulduktan sonra başla

[Service]
Type=simple
User=$USERNAME
WorkingDirectory=$PROJECT_PATH
ExecStart=$PYTHON_EXEC_PATH $SCRIPT_TO_RUN

Restart=on-failure # Herhangi bir hata durumunda servisi yeniden başlat
RestartSec=10      # Yeniden başlatmadan önce 10 saniye bekle

[Install]
WantedBy=multi-user.target
EOF

echo "Servis dosyası geçici olarak oluşturuldu."

# Oluşturulan dosyayı systemd'nin klasörüne taşı
mv ./$SERVICE_NAME.service $SERVICE_FILE
echo "Servis dosyası '$SERVICE_FILE' adresine taşındı."

# systemd'yi yeni servis hakkında bilgilendir ve servisi "enable" yap (açılışta başlasın)
systemctl daemon-reload
systemctl enable $SERVICE_NAME.service

echo "Servis başarıyla oluşturuldu ve açılışta başlamak üzere ayarlandı."
echo

echo "--- Adım 2/3: Günlük Yeniden Başlatma Zamanlayıcısı Kuruluyor ---"
# crontab'a, mevcut görevleri silmeden, her gün saat 12:00'de reboot komutunu ekle
# Bu komut, crontab'ı okur, reboot satırının zaten olup olmadığını kontrol eder, yoksa ekler.
(crontab -l 2>/dev/null | grep -v -F "/sbin/reboot" ; echo "0 12 * * * /sbin/reboot") | crontab -

echo "Sistem her gün saat 12:00'de yeniden başlatılmak üzere ayarlandı."
echo

echo "--- Adım 3/3: Servisi Başlatma ---"
systemctl start $SERVICE_NAME.service
echo "Plaka tanıma servisi şimdi başlatıldı."
echo "Durumunu kontrol etmek için: sudo systemctl status $SERVICE_NAME"
echo

echo "############################################################"
echo "### KURULUM BAŞARIYLA TAMAMLANDI! ###"
echo "############################################################"