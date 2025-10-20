#!/bin/bash

# Herhangi bir komutta hata olursa script'in çalışmasını anında durdurur.
# Bu, hatanın tam olarak nerede olduğunu anında görmemizi sağlar.
set -e

# --- AYARLAR ---
ENV_NAME="lpr_otonom_env"
PYTHON_VERSION="3.11"
# ---------------

echo "#####################################################################"
echo "### Piksel Analitik LPR - Tam Otonom Kurulum ve Doğrulama Scripti ###"
echo "#####################################################################"
echo

# --- ADIM 0: CONDA KURULUM KONTROLÜ ---
echo "--- ADIM 0/4: Conda Kurulumu Kontrol Ediliyor ---"
if ! command -v conda &> /dev/null; then
    echo "--> UYARI: 'conda' komutu bulunamadı. Miniconda kurulacak..."
    
    # Sistem mimarisini ve işletim sistemini algıla
    OS_TYPE=$(uname -s)
    ARCH_TYPE=$(uname -m)
    
    if [ "$OS_TYPE" == "Linux" ]; then
        if [ "$ARCH_TYPE" == "x86_64" ]; then
            MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"
        elif [ "$ARCH_TYPE" == "aarch64" ]; then # Raspberry Pi 64-bit için
            MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh"
        else
            echo "❌ HATA: Desteklenmeyen Linux mimarisi: $ARCH_TYPE"; exit 1
        fi
    elif [ "$OS_TYPE" == "Darwin" ]; then # macOS için
        if [ "$ARCH_TYPE" == "x86_64" ]; then # Intel Mac
            MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh"
        elif [ "$ARCH_TYPE" == "arm64" ]; then # Apple Silicon Mac
            MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh"
        else
            echo "❌ HATA: Desteklenmeyen macOS mimarisi: $ARCH_TYPE"; exit 1
        fi
    else
        echo "❌ HATA: Desteklenmeyen işletim sistemi: $OS_TYPE"; exit 1
    fi
    
    INSTALLER_SCRIPT="Miniconda3-latest-Installer.sh"
    echo "--> Miniconda indiriliyor: $MINICONDA_URL"
    # wget veya curl ile indir
    wget -O "$INSTALLER_SCRIPT" "$MINICONDA_URL" 2>/dev/null || curl -L -o "$INSTALLER_SCRIPT" "$MINICONDA_URL"
    
    echo "--> Miniconda kuruluyor... Lütfen bekleyin."
    # -b (batch) ile sessiz kurulum, -p ile yolu belirt
    bash "$INSTALLER_SCRIPT" -b -p "$HOME/miniconda3"
    
    # Kurulumu temizle
    rm "$INSTALLER_SCRIPT"
    
    # PATH'i bu script için geçici olarak güncelle ve gelecekteki oturumlar için conda'yı başlat
    source "$HOME/miniconda3/bin/activate"
    conda init bash
    
    echo "✅ Miniconda başarıyla kuruldu. Lütfen script bittikten sonra terminali yeniden başlatın."
else
    echo "✅ Conda zaten kurulu. Kurulum adımları devam ediyor..."
fi
echo

# --- ADIM 1: CONDA ORTAMINI OLUŞTURMA ---
echo "--- ADIM 1/4: Yeni ve Temiz Conda Ortamı Oluşturuluyor ---"
if conda info --envs | grep -q "$ENV_NAME"; then
    read -p "UYARI: '$ENV_NAME' ortamı zaten var. Silinip yeniden kurulsun mu? (e/h): " response
    if [[ "$response" =~ ^[Ee]$ ]]; then
        echo "Mevcut '$ENV_NAME' ortamı siliniyor..."
        conda deactivate || true
        conda env remove -n "$ENV_NAME" -y
        echo "Ortam başarıyla silindi."
    else
        echo "Kurulum iptal edildi."
        exit 0
    fi
fi
echo "Yeni '$ENV_NAME' ortamı Python $PYTHON_VERSION ile oluşturuluyor..."
conda create -n "$ENV_NAME" python="$PYTHON_VERSION" -y
echo "✅ ADIM 1 BAŞARIYLA TAMAMLANDI!"
echo

# --- ADIM 2: KÜTÜPHANELERİ ADIM ADIM YÜKLEME ---
echo "--- ADIM 2/4: Gerekli Kütüphaneler Tek Tek Kuruluyor ---"
eval "$(conda shell.bash hook)"
conda activate "$ENV_NAME"

# Kütüphane kurma ve test etme işlemini yapan bir fonksiyon
install_and_verify() {
    PACKAGE_NAME=$1
    INSTALL_COMMAND=$2
    VERIFY_COMMAND=$3
    echo
    echo "--> Kuruluyor: $PACKAGE_NAME..."
    # set +e ile hata durumunda script'in devam etmesini sağlıyoruz (isteğe bağlı)
    eval $INSTALL_COMMAND
    if [ $? -eq 0 ]; then
        echo "    ✅ Kurulum başarılı."
        echo "--> Doğrulanıyor: $PACKAGE_NAME..."
        if eval $VERIFY_COMMAND; then
            echo "    ✅ Doğrulama başarılı."
        else
            echo "    ❌ DOĞRULAMA HATASI: $PACKAGE_NAME kuruldu ama import edilemiyor!"
            exit 1 # Doğrulama hatası kritikse çık
        fi
    else
        echo "    ❌ KURULUM HATASI: $PACKAGE_NAME kurulamadı."
        exit 1 # Kurulum hatası kritikse çık
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
                   "pip install Pillow==9.5.0" \
                   "python -c 'from PIL import Image; print(f\"    -> Versiyon: {Image.__version__}\")'"

install_and_verify "Ultralytics (YOLO)" \
                   "pip install ultralytics" \
                   "python -c 'import ultralytics; print(\"    -> Başarıyla import edildi.\")'"

install_and_verify "EasyOCR" \
                   "pip install easyocr" \
                   "python -c 'import easyocr; print(\"    -> Başarıyla import edildi.\")'"

install_and_verify "Yardımcı Kütüphaneler" \
                   "pip install requests mysql-connector-python" \
                   "python -c 'import requests; import mysql.connector; print(\"    -> Başarıyla import edildi.\")'"

echo "✅ ADIM 2 BAŞARIYLA TAMAMLANDI!"
echo

# --- ADIM 3: NİHAİ KONTROL ---
echo "--- ADIM 3/4: Nihai Uyumluluk Kontrolü ---"
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

# --- ADIM 4: SON TALİMATLAR ---
echo "--- ADIM 4/4: Tamamlandı! ---"
echo "############################################################"
echo "### TÜM KURULUM ADIMLARI BAŞARIYLA TAMAMLANDI! ###"
echo "############################################################"
echo
echo "ÖNEMLİ: Yeni Conda kurulumunun tam olarak aktif olması için"
echo "lütfen bu terminal penceresini KAPATIP YENİDEN AÇIN."
echo
echo "Yeni terminalde uygulamayı çalıştırmak için:"
echo "1. 'conda activate $ENV_NAME' komutunu çalıştırın."
echo "2. Proje ana dizinindeyken 'python run_headless.py' komutunu çalıştırın."
echo
echo
echo "############################################################"
echo "### Piksel Analitik! ###"
echo "############################################################"
echo
