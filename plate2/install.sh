#!/bin/bash
set -e # Hata olursa dur

# --- AYARLAR ---
ENV_NAME="lpr_pi_final_env"
# ---------------

echo "#####################################################################"
echo "### Piksel Analitik LPR - Raspberry Pi 5 (64-bit) Kurulum Scripti ###"
echo "#####################################################################"
echo

# --- ADIM 1: SİSTEM BAĞIMLILIKLARI ---
echo "--- ADIM 1/4: Gerekli Sistem Kütüphaneleri Kuruluyor (Şifre istenebilir)... ---"
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv libopencv-dev
sudo apt-get install -y libjpeg-dev libpng-dev libtiff-dev libopenblas-dev libatlas-base-dev gfortran
echo "✅ Sistem bağımlılıkları başarıyla kuruldu."
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
# Raspberry Pi 5 (ARM64) için en stabil PyTorch kurulum yöntemi (CPU versiyonu)
pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cpu

echo "--> Adım 3.3: Diğer tüm kütüphaneler kuruluyor..."
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
