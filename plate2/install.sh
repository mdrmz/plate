#!/bin/bash

# Hata durumunda script'in çalışmasını durdurur
set -e

# --- AYARLAR ---
ENV_NAME="lpr_env"
PYTHON_VERSION="3.11"
# ---------------

echo "############################################################"
echo "### Piksel Analitik - LPR Sistemi Kurulum Script'i ###"
echo "############################################################"
echo
echo "Bu script, '$ENV_NAME' adında yeni bir Conda ortamı oluşturacak"
echo "ve gerekli tüm Python kütüphanelerini kuracaktır."
echo

# Adım 1: Mevcut ortamı temizleme (isteğe bağlı)
if conda info --envs | grep -q "$ENV_NAME"; then
    read -p "UYARI: '$ENV_NAME' adında bir ortam zaten mevcut. Silinip yeniden kurulsun mu? (e/h): " response
    if [[ "$response" =~ ^[Ee]$ ]]; then
        echo "Mevcut '$ENV_NAME' ortamı siliniyor..."
        conda deactivate
        conda env remove -n "$ENV_NAME" -y
        echo "Ortam başarıyla silindi."
    else
        echo "Kurulum iptal edildi."
        exit 0
    fi
fi

# Adım 2: Yeni ve uyumlu Conda ortamını oluşturma
echo
echo "--- Adım 1/4: '$ENV_NAME' ortamı Python $PYTHON_VERSION ile oluşturuluyor... ---"
conda create -n "$ENV_NAME" python="$PYTHON_VERSION" -y

# Adım 3: Ortamı aktif etme ve temel kütüphaneleri kurma
# Bu bölüm, script içinde conda activate'i doğru çalıştırmak için gereklidir
eval "$(conda shell.bash hook)"
conda activate "$ENV_NAME"

echo
echo "--- Adım 2/4: Donanımla Uyumlu PyTorch Kuruluyor (cpuonly)... ---"
# Bu, "Yönerge kuraldışı" hatasını çözen en kritik adımdır
conda install pytorch torchvision torchaudio cpuonly -c pytorch -y

echo
echo "--- Adım 3/4: EasyOCR ve Diğer Gerekli Kütüphaneler Kuruluyor... ---"
# EasyOCR ve diğer ana kütüphaneleri conda-forge kanalından kuruyoruz
conda install -c conda-forge easyocr ultralytics opencv requests mysql-connector-python pyside6 pillow==9.5.0 -y

echo
echo "--- Adım 4/4: Kurulum Doğrulanıyor... ---"
python -c "
import torch
import torchvision
import easyocr
import ultralytics
import cv2
print('\n--- KÜTÜPHANE VERSİYONLARI ---')
print(f'PyTorch versiyonu: {torch.__version__}')
print(f'Torchvision versiyonu: {torchvision.__version__}')
print('EasyOCR, Ultralytics (YOLO) ve OpenCV başarıyla import edildi.')
print('-----------------------------')
"

echo
echo "############################################################"
echo "### KURULUM BAŞARIYLA TAMAMLANDI! ###"
echo "############################################################"
echo
echo "Şimdi uygulamayı çalıştırmak için aşağıdaki adımları izleyebilirsiniz:"
echo "1. Terminali kapatıp yeniden açın veya 'conda activate $ENV_NAME' komutunu çalıştırın."
echo "2. Proje ana dizinindeyken 'python run_headless.py' komutunu çalıştırın."
echo