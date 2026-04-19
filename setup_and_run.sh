#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_HOME="${APP_HOME:-$HOME/termuxcoinfaucet}"

mkdir -p "$APP_HOME"

cp -f "$SOURCE_DIR"/bot.py "$APP_HOME"/
cp -f "$SOURCE_DIR"/README.md "$APP_HOME"/
cp -f "$SOURCE_DIR"/install_termux.sh "$APP_HOME"/
cp -f "$SOURCE_DIR"/manage_background.sh "$APP_HOME"/
cp -f "$SOURCE_DIR"/setup_and_run.sh "$APP_HOME"/

chmod +x "$APP_HOME"/install_termux.sh "$APP_HOME"/manage_background.sh "$APP_HOME"/setup_and_run.sh

cd "$APP_HOME"

bash install_termux.sh
bash manage_background.sh start

echo
echo "Tek klasör kurulum + arkaplan başlatma tamamlandı ✅"
echo "Klasör: $APP_HOME"
echo "Durum: bash manage_background.sh status"
