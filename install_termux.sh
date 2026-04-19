#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

printf '\n[1/5] Paket listesi güncelleniyor...\n'
pkg update -y && pkg upgrade -y

printf '\n[2/5] Gerekli paketler kuruluyor...\n'
pkg install -y x11-repo
pkg install -y python python-tkinter git

printf '\n[3/5] Proje klasörü kontrol ediliyor...\n'
if [ ! -f "bot.py" ]; then
  echo "Hata: bot.py bu klasörde bulunamadı."
  echo "Önce projeyi klonlayın veya bot.py olan klasöre girin."
  exit 1
fi

printf '\n[4/5] Derleme kontrolü...\n'
python -m py_compile bot.py

printf '\n[5/5] Kurulum tamamlandı ✅\n'
echo "Termux-X11 ile çalıştırmak için:"
echo "  termux-x11 :1 &"
echo "  export DISPLAY=:1"
echo "  python bot.py"
