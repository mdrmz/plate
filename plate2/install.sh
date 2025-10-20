#!/bin/bash

# Herhangi bir komutta hata olursa script'in çalışmasını anında durdurur.
set -e

# --- AYARLAR ---
# Kurulacak Conda ortamının adı ve Python versiyonu
ENV_NAME="lpr_os_uyumlu_env"
PYTHON_VERSION="3.11"
# ---------------

echo "#####################################################################"
echo "### Piksel Analitik LPR - Tam Otomatik Kurulum ve Doğrulama Scripti ###"
echo "#####################################################################"
echo

# --- ÖN KONTROL: Conda Kurulu mu? ---
if ! command -v conda &> /dev/null
then
    echo "❌ HATA: 'conda' komutu bulunamadı."
    echo "Lütfen devam etmeden önce Anaconda veya Miniconda'yı kurduğunuzdan emin olun."
    echo "İndirme adresi: https://www.anaconda.com/download"
    exit 1
fi

# --- ADIM 1: CONDA ORTAMINI OLUŞTURMA ---
echo "--- ADIM 1/3: Yeni ve Temiz Conda Ortamı Oluşturuluyor ---"
if conda info --envs | grep -q "$ENV_NAME"; then
    read -p "UYARI: '$ENV_NAME' ortamı zaten var. Silinip yeniden kurulsun mu? (e/h): " response
    if [[ "$response" =~ ^[Ee]$ ]]; then
        echo "Mevcut '$ENV_NAME' ortamı siliniyor..."
        conda deactivate || true # Hata verirse bile devam et
        conda env remove -n "$ENV_NAME" -y
        echo "Ortam başarıyla silindi."
    else
        echo "İşlem iptal edildi."
        exit 0
    fi
fi
echo "Yeni '$ENV_NAME' ortamı Python $PYTHON_VERSION ile oluşturuluyor..."
conda create -n "$ENV_NAME" python="$PYTHON_VERSION" -y
echo "✅ ADIM 1 BAŞARIYLA TAMAMLANDI!"
echo

# --- ADIM 2: KÜTÜPHANELERİ ADIM ADIM YÜKLEME VE TEST ETME ---
echo "--- ADIM 2/3: Gerekli Kütüphaneler Tek Tek Kuruluyor ve Test Ediliyor ---"
# Conda'yı script içinde aktif hale getirmek için
eval "$(conda shell.bash hook)"
conda activate "$ENV_NAME"

# --- Adım 2.1: PyTorch (CPU Versiyonu) ---
echo
echo "--> Adım 2.1: PyTorch (Donanımla Uyumlu CPU Versiyonu) kuruluyor..."
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

# --- Adım 2.3: Ultralytics (YOLO) ---
echo
echo "--> Adım 2.3: Ultralytics (YOLOv8) kuruluyor..."
pip install ultralytics
echo "--> Doğrulama: Ultralytics import ediliyor..."
python -c "import ultralytics; print(f'    -> Ultralytics versiyonu: {ultralytics.__version__}')"
echo "    ✅ Ultralytics başarıyla kuruldu ve test edildi."

# --- Adım 2.4: Pillow (Uyumlu Versiyon) ---
echo
echo "--> Adım 2.4: Uyumlu Pillow Sürümü (9.5.0) kuruluyor..."
pip install Pillow==9.5.0
echo "--> Doğrulama: Pillow (PIL) import ediliyor..."
python -c "from PIL import Image; print(f'    -> Pillow versiyonu: {Image.__version__}')"
echo "    ✅ Pillow 9.5.0 başarıyla kuruldu ve test edildi. ('ANTIALIAS' hatası çözüldü)"

# --- Adım 2.5: EasyOCR ---
echo
echo "--> Adım 2.5: EasyOCR kuruluyor..."
pip install easyocr
echo "--> Doğrulama: EasyOCR import ediliyor..."
python -c "import easyocr; print('    -> EasyOCR başarıyla import edildi.')"
echo "    ✅ EasyOCR başarıyla kuruldu ve test edildi."

# --- Adım 2.6: Diğer Yardımcı Kütüphaneler ---
echo
echo "--> Adım 2.6: Diğer yardımcı kütüphaneler (requests, mysql-connector) kuruluyor..."
pip install requests 
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
    import torch
    import torchvision
    import easyocr
    import ultralytics
    import cv2
    import requests
    import mysql.connector
    from PIL import Image

    print('\n--- KÜTÜPHANE ÖZETİ ---')
    print(f'PyTorch:     {torch.__version__}')
    print(f'Torchvision: {torchvision.__version__}')
    print(f'Pillow:      {Image.__version__}')
    print('-------------------------')
    print('✅ BAŞARILI: TÜM KRİTİK KÜTÜPHANELER BİRLİKTE UYUM İÇİNDE ÇALIŞIYOR!')

except ImportError as e:
    print(f'❌ NİHAİ TEST BAŞARISIZ: Bir kütüphane import edilemedi: {e}')
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