#!/bin/bash
set -e 
ENV_NAME="lpr_pi_env"
echo "#####################################################################"
echo "### Piksel Analitik LPR MOTORU Kurulum Script'i (Pi 5 64-bit)     ###"
echo "#####################################################################"
echo
echo "--- ADIM 1/4: Gerekli Sistem Kütüphaneleri Kuruluyor... ---"
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv libopencv-dev
sudo apt-get install -y libjpeg-dev libpng-dev libtiff-dev libopenblas-dev libatlas-base-dev gfortran
sudo apt-get install -y pigpio python3-pigpio
echo "✅ Sistem bağımlılıkları başarıyla kuruldu."
echo
echo "--- ADIM 2/4: Yeni Python Sanal Ortamı ('$ENV_NAME') Oluşturuluyor ---"
python3 -m venv "$ENV_NAME"
echo "✅ Sanal ortam başarıyla oluşturuldu."
echo
echo "--- ADIM 3/4: Python Kütüphaneleri Kuruluyor (Bu işlem UZUN sürebilir!)... ---"
source "$ENV_NAME/bin/activate"
pip install --upgrade pip
echo "--> Adım 3.1: PyTorch (ARM64 için) kuruluyor..."
pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cpu
echo "--> Adım 3.2: Diğer tüm kütüphaneler 'requirements.txt' dosyasından kuruluyor..."
pip install -r requirements.txt
echo "✅ ADIM 3 BAŞARIYLA TAMAMLANDI!"
echo
echo "--- ADIM 4/4: Kurulumun Başarısı Test Ediliyor ---"
python -c "
print('Nihai uyumluluk testi başlatılıyor...')
try:
    import torch, cv2, easyocr, ultralytics, gpiozero, mysql.connector
    from PIL import Image
    print('✅ BAŞARILI: TÜM KRİTİK KÜTÜPHANELER SORUNSUZ ÇALIŞIYOR!')
except Exception as e:
    print(f'❌ NİHAİ TEST BAŞARISIZ: Hata: {e}'); exit(1)
"
echo "✅ ADIM 4 BAŞARIYLA TAMAMLANDI!"
echo
echo "############################################################"
echo "### MOTOR KURULUMU BAŞARIYLA TAMAMLANDI! ###"
echo "############################################################"
echo "PIGPIO servisini başlatmayı unutma: sudo systemctl start pigpiod"
echo "Ve açılışta otomatik başlat: sudo systemctl enable pigpiod"
echo
echo "Kullanmak için: 'source $ENV_NAME/bin/activate' ve './start_giris.sh' veya './start_cikis.sh'"