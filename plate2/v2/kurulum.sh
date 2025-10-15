#!/bin/bash

# Herhangi bir komut hata verirse script'i durdur
set -e
echo "--- Piksel Analitik ---"
echo "--- Plaka Tanıma Sistemi Kurulum Script'i Başlatıldı ---"

# 1. Adım: Sistem paketlerini güncelle
echo -e "\n[ADIM 1/5] Sistem güncelleniyor..."
sudo apt update
sudo apt upgrade -y

# 2. Adım: Gerekli sistem bağımlılıklarını kur
echo -e "\n[ADIM 2/5] Gerekli sistem bağımlılıkları kuruluyor..."
sudo apt install -y python3-venv python3-pip tesseract-ocr tesseract-ocr-tur \
    libopenjp2-7 libatlas-base-dev libopenblas-dev libavformat-dev \
    libswscale-dev libgtk-3-dev ffmpeg wget

# 3. Adım: Python sanal ortamını oluştur
echo -e "\n[ADIM 3/5] Python sanal ortamı 'lpr_pi_env' oluşturuluyor..."
python3 -m venv lpr_pi_env

# 4. Adım: Gerekli Python kütüphanelerini kur
echo -e "\n[ADIM 4/5] Gerekli Python kütüphaneleri kuruluyor..."
# Sanal ortamın pip'ini kullanarak kurulum yap
lpr_pi_env/bin/pip install --upgrade pip
lpr_pi_env/bin/pip install pytesseract requests opencv-python-headless ultralytics

# PyTorch ve Torchvision'ı manuel olarak kur (Raspberry Pi için özel)
# Python sürümünü ve mimariyi kontrol et
PY_VERSION=$(python3 --version | cut -d ' ' -f 2 | cut -d '.' -f 1,2 | sed 's/\.//')
ARCH=$(uname -m)

if [ "$ARCH" != "aarch64" ]; then
    echo "HATA: Bu script sadece 64-bit Raspberry Pi OS (aarch64) için tasarlanmıştır."
    exit 1
fi

echo "Python sürümü: 3.${PY_VERSION:1}, Mimari: $ARCH"
echo "PyTorch ve Torchvision indiriliyor... Bu işlem biraz uzun sürebilir."

# PyTorch v2.2.0 (Python 3.11 için) - Gerekirse bu linkleri kendi Python sürümünüze göre güncelleyin
# Linkler: https://github.com/Qengineering/PyTorch-Raspberry-Pi_64-bit/releases
TORCH_URL="https://github.com/Qengineering/PyTorch-Raspberry-Pi_64-bit/releases/download/v2.2.0/torch-2.2.0-cp311-cp311-linux_aarch64.whl"
TORCHVISION_URL="https://github.com/Qengineering/PyTorch-Raspberry-Pi_64-bit/releases/download/v2.2.0/torchvision-0.17.0-cp311-cp311-linux_aarch64.whl"

wget -q $TORCH_URL -O torch.whl
wget -q $TORCHVISION_URL -O torchvision.whl

lpr_pi_env/bin/pip install torch.whl
lpr_pi_env/bin/pip install torchvision.whl

# İndirilen .whl dosyalarını temizle
rm torch.whl torchvision.whl

echo "Python kütüphaneleri başarıyla kuruldu."

# 5. Adım: Gerekli klasörleri oluştur
echo -e "\n[ADIM 5/5] Gerekli klasörler (models) oluşturuluyor..."
mkdir -p models


echo -e "\n--- Kurulum Tamamlandı! ---"
echo "--- Piksel Analitik ---"
echo "Lütfen 'yolov8n.pt' model dosyasını 'models' klasörüne indirin."
echo "Ardından sistemi çalıştırmak için aşağıdaki komutları kullanın:"
echo "1. source lpr_pi_env/bin/activate"
echo "2. python3 run_headless.py"
echo "--- Piksel Analitik ---"