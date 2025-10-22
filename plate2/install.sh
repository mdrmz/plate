#!/bin/bash

# Herhangi bir komutta hata olursa script'in çalışmasını anında durdurur.
set -e

# --- AYARLAR ---
ENV_NAME="lpr_pi_minimal_env"
# ---------------

echo "#####################################################################"
echo "### Piksel Analitik LPR - RPi5 Minimal Kurulum Script'i           ###"
echo "#####################################################################"
echo

# --- ADIM 1: SİSTEM KONTROLÜ VE TEMEL PAKETLER ---
echo "--- ADIM 1/4: Sistem Kontrolü ve Temel Kurulum (Şifre istenebilir)... ---"

# 64-bit kontrolü
ARCH_TYPE=$(uname -m)
if [ "$ARCH_TYPE" != "aarch64" ]; then
    echo "❌ HATA: Bu script sadece 64-bit (aarch64) Raspberry Pi OS içindir."
    echo "Mevcut mimari: $ARCH_TYPE"
    exit 1
fi
echo "✅ 64-bit sistem doğrulandı."

# Sadece pip ve venv kurulu mu diye bak, yoksa kur. Diğer dev paketlerini kurmuyoruz.
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv
echo "✅ Temel Python araçları (pip, venv) kontrol edildi/kuruldu."
echo

# --- ADIM 2: PYTHON SANAL ORTAMINI OLUŞTURMA ---
echo "--- ADIM 2/4: Yeni Python Sanal Ortamı ('$ENV_NAME') Oluşturuluyor ---"
if [ -d "$ENV_NAME" ]; then
    read -p "UYARI: '$ENV_NAME' ortamı zaten var. Silinip yeniden kurulsun mu? (e/h): " response
    if [[ "$response" =~ ^[Ee]$ ]]; then rm -rf "$ENV_NAME"; else echo "İptal edildi."; exit 0; fi
fi
python3 -m venv "$ENV_NAME"
echo "✅ Sanal ortam başarıyla oluşturuldu."
echo

# --- ADIM 3: KÜTÜPHANELERİ PİP İLE YÜKLEME ---
echo "--- ADIM 3/4: Python Kütüphaneleri Kuruluyor (Bu işlem UZUN sürebilir!)... ---"
source "$ENV_NAME/bin/activate"

echo "--> Adım 3.1: Pip güncelleniyor..."
pip install --upgrade pip

echo "--> Adım 3.2: PyTorch (ARM64 için) kuruluyor... LÜTFEN SABIRLI OLUN..."
# Raspberry Pi (ARM64) için en stabil PyTorch kurulum yöntemi (CPU versiyonu)
pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cpu

echo "--> Adım 3.3: Diğer tüm kütüphaneler kuruluyor..."
# OpenCV'yi de pip ile kurmayı deniyoruz. Çoğu zaman çalışır.
pip install opencv-python ultralytics easyocr Pillow==9.5.0 requests mysql-connector-python

echo "✅ ADIM 3 BAŞARIYLA TAMAMLANDI!"
echo

# --- ADIM 4: NİHAİ KONTROL ---
echo "--- ADIM 4/4: Kurulumun Başarısı Test Ediliyor ---"
python -c "
print('Nihai uyumluluk testi başlatılıyor...')
try:
    import torch, cv2, easyocr, ultralytics
    from PIL import Image
    import requests, mysql.connector
    print('✅ BAŞARILI: TÜM KRİTİK KÜTÜPHANELER SORUNSUZ ÇALIŞIYOR!')
except Exception as e:
    print(f'❌ NİHAİ TEST BAŞARISIZ: Hata: {e}'); exit(1)
"
echo "✅ ADIM 4 BAŞARIYLA TAMAMLANDI!"
echo

echo "############################################################"
echo "### TÜM KURULUM ADIMLARI BAŞARIYLA TAMAMLANDI! ###"
echo "############################################################"
echo
echo "Artık uygulamayı çalıştırmaya hazırsın:"
echo "1. 'source $ENV_NAME/bin/activate' komutu ile sanal ortamı aktif et."
echo "2. 'python run_headless.py' komutunu çalıştır."
echo
