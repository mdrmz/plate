#!/bin/bash
# 'set -e' komutunu KULLANMIYORUZ. Bu sayede bir komut hata verse bile script devam eder.

# --- AYARLAR ---
ENV_NAME="lpr_dayanikli_env"
PYTHON_VERSION="3.11"
# ---------------

echo "#####################################################################"
echo "### Piksel Analitik LPR - Dayanıklı Kurulum ve Doğrulama Script'i ###"
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
# Bu adım kritik olduğu için burada hata olursa çıkıyoruz.
set -e 
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
# Kritik adım bitti, hata durumunda devam etme moduna geri dönüyoruz.
set +e

# --- ADIM 2: KÜTÜPHANELERİ ADIM ADIM YÜKLEME VE TEST ETME ---
echo "--- ADIM 2/3: Gerekli Kütüphaneler Tek Tek Kuruluyor ve Test Ediliyor ---"
eval "$(conda shell.bash hook)"
conda activate "$ENV_NAME"

# Kütüphane kurma ve test etme işlemini yapan bir fonksiyon
install_and_verify() {
    PACKAGE_NAME=$1
    INSTALL_COMMAND=$2
    VERIFY_COMMAND=$3

    echo
    echo "--> Kuruluyor: $PACKAGE_NAME..."
    
    # Kurulum komutunu çalıştır
    eval $INSTALL_COMMAND
    
    # Son komutun durumunu kontrol et (0 = başarılı, diğerleri = hatalı)
    if [ $? -eq 0 ]; then
        echo "    ✅ Kurulum başarılı."
        echo "--> Doğrulanıyor: $PACKAGE_NAME..."
        
        # Doğrulama komutunu çalıştır
        eval $VERIFY_COMMAND
        if [ $? -eq 0 ]; then
            echo "    ✅ Doğrulama başarılı."
        else
            echo "    ❌ DOĞRULAMA HATASI: $PACKAGE_NAME kuruldu ama import edilemiyor!"
        fi
    else
        echo "    ❌ KURULUM HATASI: $PACKAGE_NAME kurulamadı. Diğer kütüphanelere devam ediliyor..."
    fi
}

# Şimdi fonksiyonu her bir kütüphane için ayrı ayrı çağırıyoruz
install_and_verify "PyTorch (CPU Uyumlu)" \
                   "conda install pytorch torchvision torchaudio cpuonly -c pytorch -y" \
                   "python -c 'import torch; print(f\"    -> Versiyon: {torch.__version__}\")'"

install_and_verify "OpenCV" \
                   "conda install -c conda-forge opencv -y" \
                   "python -c 'import cv2; print(f\"    -> Versiyon: {cv2.__version__}\")'"

install_and_verify "Pillow (Uyumlu Sürüm)" \
                   "conda install -c conda-forge pillow=9.5.0 -y" \
                   "python -c 'from PIL import Image; print(f\"    -> Versiyon: {Image.__version__}\")'"

install_and_verify "Ultralytics (YOLO)" \
                   "conda install -c conda-forge ultralytics -y" \
                   "python -c 'import ultralytics; print(\"    -> Başarıyla import edildi.\")'"

install_and_verify "EasyOCR" \
                   "conda install -c conda-forge easyocr -y" \
                   "python -c 'import easyocr; print(\"    -> Başarıyla import edildi.\")'"

install_and_verify "Yardımcı Kütüphaneler" \
                   "conda install -c conda-forge requests mysql-connector-python -y" \
                   "python -c 'import requests; import mysql.connector; print(\"    -> Başarıyla import edildi.\")'"

echo
echo "✅ ADIM 2 TAMAMLANDI! (Tüm kütüphaneler denenmiştir.)"

# --- ADIM 3: NİHAİ KONTROL ---
echo
echo "--- ADIM 3/3: Nihai Uyumluluk Kontrolü ---"
echo "Tüm kütüphanelerin birlikte çalışıp çalışmadığı test ediliyor..."

python -c "
import sys
installed_ok = True
print('\n--- NİHAİ KONTROL RAPORU ---')
try:
    import torch; print('✅ PyTorch')
except Exception as e:
    print(f'❌ PyTorch - HATA: {e}'); installed_ok = False
try:
    import cv2; print('✅ OpenCV')
except Exception as e:
    print(f'❌ OpenCV - HATA: {e}'); installed_ok = False
try:
    import ultralytics; print('✅ Ultralytics')
except Exception as e:
    print(f'❌ Ultralytics - HATA: {e}'); installed_ok = False
try:
    import easyocr; print('✅ EasyOCR')
except Exception as e:
    print(f'❌ EasyOCR - HATA: {e}'); installed_ok = False
print('--------------------------')
if not installed_ok:
    print('Bazı kütüphaneler kurulamadı veya çalışmıyor. Lütfen yukarıdaki hataları kontrol edin.')
    sys.exit(1)
"
echo "✅ ADIM 3 BAŞARIYLA TAMAMLANDI!"
echo

echo "############################################################"
echo "### KURULUM TAMAMLANDI! ###"
echo "############################################################"
echo
echo "Lütfen yukarıdaki raporu kontrol edin. Eğer ❌ işareti varsa,"
echo "o kütüphanenin kurulumunda bir sorun yaşanmış demektir."
echo
echo "Her şey yolundaysa, uygulamayı çalıştırmaya hazırsın:"
echo "1. Terminali kapatıp yeniden aç veya 'conda activate $ENV_NAME' komutunu çalıştır."
echo "2. Proje ana dizinindeyken 'python run_headless.py' komutunu çalıştır."
echo
