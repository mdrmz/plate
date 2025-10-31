#!/bin/bash

# Herhangi bir komutta hata olursa script'in çalışmasını anında durdurur.
set -e

# --- AYARLAR ---
ENV_NAME="lpr_pi_env"
# ---------------

echo "#####################################################################"
echo "### Piksel Analitik LPR - Raspberry Pi Nihai Kurulum Script'i     ###"
echo "#####################################################################"
echo

# --- ADIM 1: SİSTEM BAĞIMLILIKLARINI KURMA ---
echo "--- ADIM 1/4: Gerekli Sistem Kütüphaneleri Kuruluyor (Şifreniz istenebilir)... ---"
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv libopencv-dev
# PyTorch ve diğer kütüphanelerin ihtiyaç duyduğu ek paketler
sudo apt-get install -y libjpeg-dev libpng-dev libtiff-dev libopenblas-dev libatlas-base-dev gfortran
echo "✅ Sistem bağımlılıkları başarıyla kuruldu."
echo

# --- ADIM 2: PYTHON SANAL ORTAMINI OLUŞTURMA ---
echo "--- ADIM 2/4: Yeni Python Sanal Ortamı ('$ENV_NAME') Oluşturuluyor ---"
if [ -d "$ENV_NAME" ]; then
    read -p "UYARI: '$ENV_NAME' ortamı zaten var. Silinip yeniden kurulsun mu? (e/h): " response
    if [[ "$response" =~ ^[Ee]$ ]]; then
        echo "Mevcut '$ENV_NAME' ortamı siliniyor..."
        rm -rf "$ENV_NAME"
    else
        echo "Kurulum iptal edildi."; exit 0
    fi
fi
python3 -m venv "$ENV_NAME"
echo "✅ Sanal ortam başarıyla oluşturuldu."
echo

# --- ADIM 3: KÜTÜPHANELERİ PİP İLE YÜKLEME ---
echo "--- ADIM 3/4: Gerekli Python Kütüphaneleri Kuruluyor (Bu işlem ÇOK UZUN sürebilir!)... ---"
# Yeni oluşturulan sanal ortamı aktif et
source "$ENV_NAME/bin/activate"

echo "--> Adım 3.1: Pip güncelleniyor..."
pip install --upgrade pip

echo "--> Adım 3.2: PyTorch (ARM64 için) kuruluyor... LÜTFEN SABIRLI OLUN..."
# Raspberry Pi (ARM64) için en stabil PyTorch kurulum yöntemi
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
    print('\n--- KÜTÜPHANE ÖZETİ ---')
    print(f'PyTorch versiyonu: {torch.__version__}')
    print(f'Pillow versiyonu:  {Image.__version__}')
    print('-------------------------')
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