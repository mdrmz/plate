#!/bin/bash
echo "Çıkış Kapısı LPR motoru (RTSP) başlatılıyor..."
DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
source "$DIR/lpr_pi_env/bin/activate"
python "$DIR/run_headless.py" \
    --camera "rtsp://admin:1234@192.168.1.39:554/stream1" \
    --gate "cikis"