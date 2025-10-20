#!/bin/bash

# Herhangi bir komutta hata olursa script'in çalışmasını anında durdurur.
set -e

# --- AYARLAR ---
ENV_NAME="lpr_nihai_env"
PYTHON_VERSION="3.11"
# ---------------

echo "#####################################################################"
echo "### Piksel Analitik LPR - Nihai Kurulum ve Doğrulama Script'i     ###"
echo "#####################################################################"
echo

# --- ADIM 0: SİSTEM ANALİZİ VE CONDA KONTROLÜ ---
echo "--- ADIM 0/4: Sistem Analiz Ediliyor ve Conda Kontrol Ediliyor ---"
OS_TYPE=$(uname -s)
ARCH_TYPE=$(uname -m)

echo "-> İşletim Sistemi: $OS_TYPE"
echo "-> Mimari: $ARCH_TYPE"

# DESTEKLENMEYEN 32-BIT KONTROLÜ
if [ "$ARCH_TYPE" == "armv7l" ]; then
    echo; echo "❌ HATA: Desteklenmeyen 32-bit (armv7l) mimari tespit edildi."
    echo "Bu proje 64-bit bir işletim sistemi gerektirir."; exit 1
fi
echo "✅ Sistem mimarisi destekleniyor."

if ! command -v conda &> /dev/null; then
    echo "❌ HATA: 'conda' komutu bulunamadı. Lütfen önce Anaconda veya Miniconda kurun."
    exit 1
fi
echo "✅ Conda kurulu."
echo

# --- ADIM 1: CONDA ORTAMINI OLUŞTURMA ---
echo "--- ADIM 1/4: Yeni ve Temiz Conda Ortamı Oluşturuluyor ---"
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
conda create -n "$ENV_NAME" python="$PYTHON_VERSION" -y
echo "✅ ADIM 1 BAŞARIYLA TAMAMLANDI!"
echo

# --- ADIM 2: KÜTÜPHANELERİ CONDA İLE ADIM ADIM YÜKLEME ---
echo "--- ADIM 2/4: Gerekli Kütüphaneler Conda ile Adım Adım Kuruluyor ---"
eval "$(conda shell.bash hook)"
conda activate "$ENV_NAME"

# Kütüphane kurma ve test etme fonksiyonu
install_and_verify() {
    PACKAGE_NAME=$1; INSTALL_COMMAND=$2; VERIFY_COMMAND=$3
    echo; echo "--> Kuruluyor: $PACKAGE_NAME...";
    if eval $INSTALL_COMMAND; then
        echo "    ✅ Kurulum başarılı."; echo "--> Doğrulanıyor: $PACKAGE_NAME...";
        if eval $VERIFY_COMMAND; then echo "    ✅ Doğrulama başarılı."; else echo "    ❌ DOĞRULAMA HATASI!"; exit 1; fi
    else echo "    ❌ KURULUM HATASI!"; exit 1; fi
}

# --- Adım 2.1: PyTorch (Donanımla Uyumlu CPU Versiyonu) ---
install_and_verify "PyTorch (CPU Uyumlu)" \
                   "conda install pytorch torchvision torchaudio cpuonly -c pytorch -y" \
                   "python -c 'import torch; print(f\"    -> Versiyon: {torch.__version__}\")'"

# --- Adım 2.2: Kalan Tüm Kütüphaneler (Tek Seferde) ---
# Conda'nın en iyi uyumluluğu bulabilmesi için kalanları tek bir komutta kurmak en sağlıklısıdır.
# Ama her birini ayrı ayrı test edeceğiz.
install_and_verify "Ana Kütüphaneler (OpenCV, Pillow, Ultralytics, EasyOCR)" \
                   "conda install -c conda-forge opencv ultralytics easyocr pillow=9.5.0 -y" \
                   "python -c 'import cv2; import ultralytics; import easyocr; from PIL import Image; print(\"    -> Başarıyla import edildi.\")'"

# --- Adım 2.3: PySide6 (GUI Kütüphanesi) ---
install_and_verify "PySide6 (GUI Kütüphanesi)" \
                   "conda install -c conda-forge pyside6 -y" \
                   "python -c 'from PySide6.QtWidgets import QApplication; print(\"    -> Başarıyla import edildi.\")'"

# --- Adım 2.4: Diğer Yardımcı Kütüphaneler ---
install_and_verify "Yardımcı Kütüphaneler (requests, mysql-connector)" \
                   "conda install -c conda-forge requests mysql-connector-python -y" \
                   "python -c 'import requests; import mysql.connector; print(\"    -> Başarıyla import edildi.\")'"

echo "✅ ADIM 2 BAŞARIYLA TAMAMLANDI!"
echo

# --- ADIM 3: NİHAİ KONTROL ---
echo "--- ADIM 3/4: Nihai Uyumluluk Kontrolü ---"
python -c "
print('Nihai uyumluluk testi başlatılıyor...')
try:
    import torch, torchvision, easyocr, ultralytics, cv2, requests
    import mysql.connector
    from PIL import Image
    from PySide6.QtCore import QObject
    print('✅ BAŞARILI: TÜM KÜTÜPHANELER SORUNSUZ ÇALIŞIYOR!')
except Exception as e:
    print(f'❌ NİHAİ TEST BAŞARISIZ: Hata: {e}')
    exit(1)
"
echo "✅ ADIM 3 BAŞARIYLA TAMAMLANDI!"
echo

# --- ADIM 4: SON TALİMATLAR ---
echo "--- ADIM 4/4: Tamamlandı! ---"
echo "############################################################"
echo "### TÜM KURULUM ADIMLARI BAŞARIYLA TAMAMLANDI! ###"
echo "############################################################"
echo
echo "ÖNEMLİ: Kurulumun tam aktif olması için bu terminali"
echo "lütfen KAPATIP YENİDEN AÇIN."
echo
echo "Yeni terminalde uygulamayı çalıştırmak için:"
echo "1. 'conda activate $ENV_NAME' komutunu çalıştırın."
echo "2. Proje ana dizinindeyken 'python run_headless.py' komutunu çalıştırın."
echo
echo "#############################################################"
echo "# Script, Piksel Analitik adına Mehmet Durmaz Tarafından          #"
echo "# özel olarak hazırlanmıştır. İyi günlerde kullanın!          #"
echo "# Piksel Analitik#"
echo "#https://pikselanalitik.com #"
echo "#############################################################"
