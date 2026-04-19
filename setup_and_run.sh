#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

bash install_termux.sh
bash manage_background.sh start

echo
echo "Tek komut kurulum + arkaplan başlatma tamamlandı ✅"
echo "Durum: bash manage_background.sh status"
