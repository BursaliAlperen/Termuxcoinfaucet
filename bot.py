import asyncio
import getpass
import json
import os
import shutil
import re
import sys
import time
import uuid
import urllib.parse
from datetime import datetime

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ======================= PREMIUM UI & COLORS =======================
C1 = "\033[38;5;51m"    # cyan neon
C2 = "\033[38;5;199m"   # pink neon
C3 = "\033[38;5;226m"   # yellow neon
C4 = "\033[38;5;46m"    # green neon
C5 = "\033[38;5;196m"   # red neon
WHITE = "\033[97m"
BOLD = "\033[1m"
RESET = "\033[0m"
TERM_WIDTH = shutil.get_terminal_size((60, 20)).columns
LINE_WIDTH = max(46, min(60, TERM_WIDTH))
LINE = f"{C1}{'━' * LINE_WIDTH}{RESET}"

# Öncelikli sağlayıcılar
WORKING_PROVIDERS = ["richads", "monetag", "adsgram"]
REQUEST_TIMEOUT = 25
MAX_EMPTY_REFRESHES = 3

# Yapılandırma
TELEGRAM_BOT_USERNAME = "TonexaSpinBot"
TELEGRAM_WEBAPP_URL = "https://app.theopenearn.com/"
TELEGRAM_SESSION = "tonexa_session"
TELEGRAM_API_ID = "26025122"
TELEGRAM_API_HASH = "9c832a240c0ba7cd4b01189ee35a6c59"
TELEGRAM_PHONE = "+905518951725"

# ======================= UI FUNCTIONS =======================
def clear():
    os.system('clear' if os.name == 'posix' else 'cls')

def center(text):
    return text.center(LINE_WIDTH)

def banner():
    print(LINE)
    print(f"{C2}{BOLD}")
    if LINE_WIDTH < 60:
        print(center("████████╗ ██████╗ ███╗   ██╗███████╗██╗  ██╗ █████╗ "))
        print(center("╚══██╔══╝██╔═══██╗████╗  ██║██╔════╝╚██╗██╔╝██╔══██╗"))
        print(center("   ██║   ██║   ██║██╔██╗ ██║█████╗   ╚███╔╝ ███████║"))
        print(center("   ██║   ██║   ██║██║╚██╗██║██╔══╝   ██╔██╗ ██╔══██║"))
        print(center("   ██║   ╚██████╔╝██║ ╚████║███████╗██╔╝ ██╗██║  ██║"))
    else:
        print(center("████████╗ ██████╗ ███╗   ██╗███████╗██╗  ██╗ █████╗ "))
        print(center("╚══██╔══╝██╔═══██╗████╗  ██║██╔════╝╚██╗██╔╝██╔══██╗"))
        print(center("   ██║   ██║   ██║██╔██╗ ██║█████╗   ╚███╔╝ ███████║"))
        print(center("   ██║   ██║   ██║██║╚██╗██║██╔══╝   ██╔██╗ ██╔══██║"))
        print(center("   ██║   ╚██████╔╝██║ ╚████║███████╗██╔╝ ██╗██║  ██║"))
    print(f"{RESET}")
    print(LINE)
    print(f"{C4}👑 DEV: {WHITE}TONEXA {C1}┃ {C3}⚡ SYSTEM: {WHITE}2.5D AAA ENGINE{RESET}")
    print(LINE)

def running_timer(seconds, msg):
    while seconds > 0:
        sys.stdout.write(f"\r{C1}[{datetime.now().strftime('%H:%M:%S')}] {C5}⏳ {msg}: {C4}{seconds:02d}s{RESET} ")
        sys.stdout.flush()
        time.sleep(1)
        seconds -= 1
    sys.stdout.write("\r" + " " * LINE_WIDTH + "\r")

# ======================= CORE ENGINE =======================
class TonexaEngine:
    def __init__(self, auth):
        self.auth = "tma " + auth.replace("tma ", "")
        self.session = self._setup_session()
        self.user_id = self._extract_id()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Telegram-iOS/10.12.1',
            'Authorization': self.auth,
            'Content-Type': 'application/json',
            'Origin': 'https://app.theopenearn.com',
            'Referer': 'https://app.theopenearn.com/'
        }

    def _setup_session(self):
        s = requests.Session()
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))
        return s

    def _extract_id(self):
        try:
            match = re.search(r'user=([^&]+)', self.auth)
            if match:
                user_data = json.loads(urllib.parse.unquote(match.group(1)))
                return str(user_data.get('id', '7330965002'))
        except: pass
        return "7330965002"

    def get_api(self, endpoint):
        try:
            res = self.session.get(f"https://app.theopenearn.com/api/{endpoint}", headers=self.headers, timeout=REQUEST_TIMEOUT)
            return res.json() if res.status_code == 200 else None
        except: return None

    def post_api(self, endpoint, data):
        try:
            res = self.session.post(f"https://app.theopenearn.com/api/{endpoint}", headers=self.headers, json=data, timeout=REQUEST_TIMEOUT)
            return res.status_code == 200
        except: return False

    def run_monetag(self):
        oaid = uuid.uuid4().hex
        url = f"https://e8ys.com/500/10719545?oaid={oaid}&tgp=ios&sdkp=1&var_3={self.user_id}&sw_version=v1.801.0"
        try:
            res = self.session.get(url, headers=self.headers, timeout=10).json()
            ruid = res.get('ruid')
            if ruid:
                running_timer(38, "RichAds/Monetag Stream")
                resolve = self.session.get(f"https://e8ys.com/resolve?ruid={ruid}", timeout=10)
                if resolve.status_code == 200:
                    return self.post_api("ads/complete", {"ad_type": "video", "provider": "monetag", "watched": True})
        except: pass
        return False

# ======================= TELEGRAM AUTH =======================
async def get_tg_auth():
    from telethon import TelegramClient
    from telethon.errors import SessionPasswordNeededError
    from telethon.tl.functions.messages import RequestWebViewRequest

    client = TelegramClient(TELEGRAM_SESSION, int(TELEGRAM_API_ID), TELEGRAM_API_HASH)
    await client.connect()

    if not await client.is_user_authorized():
        await client.send_code_request(TELEGRAM_PHONE)
        code = input(f"{C2}Kod: {RESET}")
        try:
            await client.sign_in(TELEGRAM_PHONE, code)
        except SessionPasswordNeededError:
            pw = getpass.getpass(f"{C2}2FA Şifresi: {RESET}")
            await client.sign_in(password=pw)
    
    print(f"{C4}✅ Oturum Açıldı, WebApp Verisi Alınıyor...{RESET}")
    
    bot_entity = await client.get_input_entity(TELEGRAM_BOT_USERNAME)
    
    # Hatalı parametreleri temizlenmiş RequestWebViewRequest kullanımı
    result = await client(RequestWebViewRequest(
        peer=bot_entity,
        bot=bot_entity,
        url=TELEGRAM_WEBAPP_URL,
        platform="ios",
        from_bot_menu=True
    ))
    
    await client.disconnect()
    
    # Auth verisini URL'den ayıkla
    query = urllib.parse.unquote(result.url.split('tgWebAppData=')[1].split('&')[0])
    return query

# ======================= MAIN PROCESS =======================
def main():
    clear()
    banner()
    
    try:
        loop = asyncio.get_event_loop()
        auth_data = loop.run_until_complete(get_tg_auth())
    except Exception as e:
        print(f"{C5}❌ Giriş Hatası: {e}{RESET}")
        return

    engine = TonexaEngine(auth_data)
    start_bal = 0.0

    while True:
        user = engine.get_api("user")
        status = engine.get_api("ads/daily-status")

        if not user or not status:
            print(f"{C5}⚠️ Veri Alınamadı, 10sn Bekleniyor...{RESET}")
            time.sleep(10)
            continue

        if start_bal == 0.0: start_bal = float(user['balance'])

        clear()
        banner()
        print(f"{C1}👤 {WHITE}{user['username']} {C1}┃ 💰 {C4}{user['balance']} USDT {C1}┃ 📈 {C3}+{round(float(user['balance'])-start_bal, 4)}{RESET}")
        print(LINE)

        providers = status.get('providers', {})
        active_list = []

        for p in WORKING_PROVIDERS:
            info = providers.get(p, {})
            rem = info.get('limit', 0) - info.get('used', 0)
            if rem > 0:
                print(f"{C1}📺 {p.upper():<10} ┃ Kalan: {C4}{rem:<2} {C1}┃ Durum: {C4}HAZIR{RESET}")
                active_list.append(p)
            else:
                print(f"{WHITE}📺 {p.upper():<10} ┃ Kalan: 0  ┃ Durum: TAMAM{RESET}")

        if not active_list:
            print(LINE)
            print(f"{C3}🎉 Günlük tüm reklamlar izlendi! Çark çevriliyor...{RESET}")
            engine.post_api("wheel/spin", {"is_paid": False})
            print(f"{C4}✅ İşlem Tamamlandı. Kapatılıyor.{RESET}")
            break

        target = active_list[0]
        print(LINE)
        print(f"{C1}▶️ İşleniyor: {C2}{target.upper()}{RESET}")

        success = False
        if target == "monetag" or target == "richads":
            success = engine.run_monetag()
        else:
            running_timer(32, f"{target.upper()} İzleniyor")
            success = engine.post_api("ads/complete", {"ad_type": "video", "provider": target, "watched": True})

        if success:
            print(f"{C4}✅ Başarılı! Bakiyen güncellendi.{RESET}")
            if target == "adsgram": running_timer(60, "Sınır Beklemesi")
        else:
            print(f"{C5}❌ Hata oluştu, sonraki sağlayıcıya geçiliyor.{RESET}")
        
        time.sleep(3)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{C5}Durduruldu.{RESET}")
