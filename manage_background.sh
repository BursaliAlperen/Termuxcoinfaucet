#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNTIME_DIR="$APP_DIR/.runtime"
LOG_DIR="$APP_DIR/logs"
X11_PID_FILE="$RUNTIME_DIR/termux-x11.pid"
BOT_PID_FILE="$RUNTIME_DIR/bot.pid"

mkdir -p "$RUNTIME_DIR" "$LOG_DIR"

is_running() {
  local pid_file="$1"
  if [ ! -f "$pid_file" ]; then
    return 1
  fi

  local pid
  pid="$(cat "$pid_file")"
  if [ -z "$pid" ] || ! kill -0 "$pid" 2>/dev/null; then
    rm -f "$pid_file"
    return 1
  fi

  return 0
}

start_services() {
  if is_running "$BOT_PID_FILE"; then
    echo "Bot zaten arkaplanda çalışıyor (PID: $(cat "$BOT_PID_FILE"))."
    return 0
  fi

  export DISPLAY=:1

  if ! is_running "$X11_PID_FILE"; then
    nohup termux-x11 :1 >"$LOG_DIR/termux-x11.log" 2>&1 &
    echo $! >"$X11_PID_FILE"
    sleep 1
  fi

  cd "$APP_DIR"
  nohup python bot.py >"$LOG_DIR/bot.log" 2>&1 &
  echo $! >"$BOT_PID_FILE"

  echo "Başlatıldı."
  echo "- termux-x11 PID: $(cat "$X11_PID_FILE")"
  echo "- bot.py PID: $(cat "$BOT_PID_FILE")"
  echo "Loglar: $LOG_DIR"
}

stop_services() {
  if is_running "$BOT_PID_FILE"; then
    kill "$(cat "$BOT_PID_FILE")"
    rm -f "$BOT_PID_FILE"
    echo "bot.py durduruldu."
  else
    echo "bot.py zaten kapalı."
  fi

  if is_running "$X11_PID_FILE"; then
    kill "$(cat "$X11_PID_FILE")"
    rm -f "$X11_PID_FILE"
    echo "termux-x11 durduruldu."
  else
    echo "termux-x11 zaten kapalı."
  fi
}

status_services() {
  if is_running "$BOT_PID_FILE"; then
    echo "bot.py çalışıyor (PID: $(cat "$BOT_PID_FILE"))."
  else
    echo "bot.py çalışmıyor."
  fi

  if is_running "$X11_PID_FILE"; then
    echo "termux-x11 çalışıyor (PID: $(cat "$X11_PID_FILE"))."
  else
    echo "termux-x11 çalışmıyor."
  fi
}

case "${1:-start}" in
start)
  start_services
  ;;
stop)
  stop_services
  ;;
restart)
  stop_services
  start_services
  ;;
status)
  status_services
  ;;
*)
  echo "Kullanım: $0 {start|stop|restart|status}"
  exit 1
  ;;
esac
