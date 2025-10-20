#!/bin/bash

# Herhangi bir komutta hata olursa script'in çalışmasını anında durdurur.
set -e

# --- AYARLAR ---
ENV_NAME="lpr_conda_final"
PYTHON_VERSION="3.11"
# ---------------

echo "#####################################################################"
echo "### Piksel Analitik LPR - Sadece Conda ile Kurulum Script'i ###"
echo "#####################################################################"
echo

# --- ÖN KONTROL: Conda Kurulu mu? ---
if ! command -v conda &> /dev/null
then
    echo "❌ HATA: 'conda' komutu bulunamadı. Lütfen Anaconda veya Miniconda'yı kurun."
    exit 1
fi

# --- ADIM 1: CONDA ORTAMINI OLUŞTURMA ---
echo "--- ADIM 1/3: Yeni ve Temiz Conda Ortamı Oluşturuluyor ---"
if conda info --envs | grep -q "$ENV_NAME"; then
    read -p "UYARI: '$ENV_NAME' ortamı zaten var. Silinip yeniden kurulsun mu? (e/h): " response
    if [[ "$response" =~ ^[Ee]$ ]]; then
        echo "Mevcut '$ENV_NAME' ortamı siliniyor..."
        conda deactivate || true
        conda env remove -n "$ENV_NAME" -y
    else
        echo "Kurulum iptal edildi."; exit 0
    fi
fi
echo "Yeni '$ENV_NAME' ortamı Python $PYTHON_VERSION ile oluşturuluyor..."
conda create -n "$ENV_NAME" python="$PYTHON_VERSION" -y
echo "✅ ADIM 1 BAŞARIYLA TAMAMLANDI!"
echo

# --- ADIM 2: KÜTÜPHANELERİ CONDA İLE ADIM ADIM YÜKLEME ---
echo "--- ADIM 2/3: Gerekli Kütüphaneler Conda ile Tek Tek Kuruluyor ---"
eval "$(conda shell.bash hook)"
conda activate "$ENV_NAME"

# --- Adım 2.1: PyTorch (Donanımla Uyumlu CPU Versiyonu) ---
echo
echo "--> Adım 2.1: PyTorch (Donanımla Uyumlu CPU Versiyonu) kuruluyor..."
# VERSİYON BELİRTMİYORUZ. Conda'nın kendisi, Python 3.11 ve CPU ile uyumlu en iyisini bulacak.
conda install pytorch torchvision torchaudio cpuonly -c pytorch -y
echo "--> Doğrulama: PyTorch import ediliyor..."
python -c "import torch; print(f'    -> PyTorch versiyonu: {torch.__version__}')"
echo "    ✅ PyTorch başarıyla kuruldu ve test edildi."

# --- Adım 2.2: OpenCV ---
echo
echo "--> Adım 2.2: OpenCV kuruluyor..."
conda install -c conda-forge opencv -y
echo "--> Doğrulama: OpenCV (cv2) import ediliyor..."
python -c "import cv2; print(f'    -> OpenCV versiyonu: {cv2.__version__}')"
echo "    ✅ OpenCV başarıyla kuruldu ve test edildi."

# --- Adım 2.3: Pillow (Uyumlu Versiyon) ---
echo
echo "--> Adım 2.3: Uyumlu Pillow Sürümü (9.5.0) kuruluyor..."
# Bu, 'ANTIALIAS' hatasını çözen adımdır.
conda install -c conda-forge pillow=9.5.0 -y
echo "--> Doğrulama: Pillow (PIL) import ediliyor..."
python -c "from PIL import Image; print(f'    -> Pillow versiyonu: {Image.__version__}')"
echo "    ✅ Pillow 9.5.0 başarıyla kuruldu ve test edildi."

# --- Adım 2.4: Ultralytics ve EasyOCR ---
echo
echo "--> Adım 2.4: Ultralytics (YOLO) ve EasyOCR kuruluyor..."
conda install -c conda-forge ultralytics easyocr -y
echo "--> Doğrulama: Ultralytics ve EasyOCR import ediliyor..."
python -c "import ultralytics; import easyocr; print('    -> Ultralytics ve EasyOCR başarıyla import edildi.')"
echo "    ✅ AI kütüphaneleri başarıyla kuruldu ve test edildi."

# --- Adım 2.5: Diğer Yardımcı Kütüphaneler ---
echo
echo "--> Adım 2.5: Diğer yardımcı kütüphaneler (requests, mysql-connector) kuruluyor..."
conda install -c conda-forge requests mysql-connector-python -y
echo "--> Doğrulama: Yardımcı kütüphaneler import ediliyor..."
python -c "import requests; import mysql.connector; print('    -> requests ve mysql.connector başarıyla import edildi.')"
echo "    ✅ Yardımcı kütüphaneler başarıyla kuruldu ve test edildi."
echo
echo "✅ ADIM 2 BAŞARIYLA TAMAMLANDI!"

# --- ADIM 3: NİHAİ KONTROL ---
echo
echo "--- ADIM 3/3: Tüm Kütüphanelerin Birlikte Çalıştığı Test Ediliyor ---"
python -c "
print('Nihai uyumluluk testi başlatılıyor...')
try:
    import torch, torchvision, easyocr, ultralytics, cv2, requests
    import mysql.connector
    from PIL import Image
    print('✅ BAŞARILI: TÜM KRİTİK KÜTÜPHANELER SORUNSUZ ÇALIŞIYOR!')
except Exception as e:
    print(f'❌ NİHAİ TEST BAŞARISIZ: Hata: {e}')
    exit(1)
"
echo "✅ ADIM 3 BAŞARIYLA TAMAMLANDI!"
echo

echo "############################################################"
echo "### TÜM KURULUM ADIMLARI BAŞARIYLA TAMAMLANDI! ###"
echo "############################################################"
echo
echo "Artık uygulamayı çalıştırmaya hazırsın:"
echo "1. Bu terminali kapatıp yeniden aç veya 'conda activate $ENV_NAME' komutunu çalıştır."
echo "2. Proje ana dizinindeyken 'python run_headless.py' komutunu çalıştır."
echo
