#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

printf '\n[1/6] Paket listesi güncelleniyor...\n'
pkg update -y && pkg upgrade -y

printf '\n[2/6] Gerekli paketler kuruluyor...\n'
pkg install -y x11-repo
pkg install -y python python-tkinter git

printf '\n[3/6] Proje klasörü kontrol ediliyor...\n'
if [ ! -f "bot.py" ]; then
  echo "Hata: bot.py bu klasörde bulunamadı."
  echo "Önce projeyi klonlayın veya bot.py olan klasöre girin."
  exit 1
fi

printf '\n[4/6] Derleme kontrolü...\n'
python -m py_compile bot.py

printf '\n[5/6] Script izinleri ayarlanıyor...\n'
chmod +x manage_background.sh

printf '\n[6/6] Kurulum tamamlandı ✅\n'
echo "Ön plan çalıştırma:"
echo "  termux-x11 :1 &"
echo "  export DISPLAY=:1"
echo "  python bot.py"
echo
echo "Arkaplan (otomatik) çalıştırma:"
echo "  ./manage_background.sh start"
echo "  ./manage_background.sh status"
echo "  ./manage_background.sh stop"
