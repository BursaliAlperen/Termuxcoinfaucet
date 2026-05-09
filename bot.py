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

# ======================= PREMIUM COLORS =======================
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

# Sadece ödüllü (rewarded) sağlayıcılar hedefleniyor
WORKING_PROVIDERS = ["monetag", "richads", "adsgram"]
REQUEST_TIMEOUT = 30 # Sunucu yüküne karşı 20'den 30'a çıkarıldı
MAX_EMPTY_REFRESHES = 3
MAX_RETRIES = 3 # 502 ve Timeout'lar için maksimum tekrar sayısı
TELEGRAM_BOT_USERNAME = os.getenv("NINOCOIN_TG_BOT", "TheOpenEarnBot")
TELEGRAM_WEBAPP_URL = os.getenv("NINOCOIN_TG_WEBAPP_URL", "https://app.theopenearn.com/")
TELEGRAM_SESSION = os.getenv("NINOCOIN_TG_SESSION", "ninocoin_telegram")
TELEGRAM_API_ID = os.getenv("NINOCOIN_API_ID", "26025122")
TELEGRAM_API_HASH = os.getenv("NINOCOIN_API_HASH", "9c832a240c0ba7cd4b01189ee35a6c59")
TELEGRAM_PHONE = os.getenv("NINOCOIN_PHONE", "+905518951725")
TELEGRAM_LOGIN_RETRY_DELAY = 5

# ======================= UI FUNCTIONS =======================
def clear():
    os.system('clear' if os.name == 'posix' else 'cls')

def center(text):
    return text.center(LINE_WIDTH)

def panel(title, lines):
    print(LINE)
    print(f"{C2}{BOLD}{center(title)}{RESET}")
    print(LINE)
    for line in lines:
        print(line)
    print(LINE)

def mask_value(value, visible_start=4, visible_end=3):
    if not value:
        return "-"
    if len(value) <= visible_start + visible_end:
        return "*" * len(value)
    return f"{value[:visible_start]}{'*' * (len(value) - visible_start - visible_end)}{value[-visible_end:]}"

def banner():
    print(LINE)
    print(f"{C2}{BOLD}")
    if LINE_WIDTH < 60:
        print(center("███╗   ██╗██╗███╗   ██╗ ██████╗"))
        print(center("████╗  ██║██║████╗  ██║██╔═══██╗"))
        print(center("██╔██╗ ██║██║██╔██╗ ██║██║   ██║"))
        print(center("██║╚██╗██║██║██║╚██╗██║██║   ██║"))
        print(center("██║ ╚████║██║██║ ╚████║╚██████╔╝"))
        print(center("╚═╝  ╚═══╝╚═╝╚═╝  ╚═══╝ ╚═════╝"))
        print(f"{WHITE}{BOLD}{center('NINOCOIN')}{RESET}")
    else:
        print("███╗   ██╗██╗███╗   ██╗ ██████╗ ██████╗ ██╗███╗   ██╗")
        print("████╗  ██║██║████╗  ██║██╔════╝██╔═══██╗██║████╗  ██║")
        print("██╔██╗ ██║██║██╔██╗ ██║██║     ██║   ██║██║██╔██╗ ██║")
        print("██║╚██╗██║██║██║╚██╗██║██║     ██║   ██║██║██║╚██╗██║")
        print("██║ ╚████║██║██║ ╚████║╚██████╗╚██████╔╝██║██║ ╚████║")
        print("╚═╝  ╚═══╝╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚═════╝ ╚═╝╚═╝  ╚═══╝")
    print(f"{RESET}")
    print(LINE)
    print(f"{C4}👑 DEV: {WHITE}@NINOCOIN {C1}┃ {C3}⚡ LOGIN: {WHITE}TELEGRAM{RESET}")
    print(LINE)

def running_timer(seconds, msg):
    while seconds > 0:
        sys.stdout.write(f"\r{C1}[{datetime.now().strftime('%H:%M:%S')}] {C5}⏳ {msg}: {C4}{seconds:02d}s{RESET} ")
        sys.stdout.flush()
        time.sleep(1)
        seconds -= 1
    sys.stdout.write("\r" + " " * LINE_WIDTH + "\r")

def normalize_auth(auth):
    auth = auth.strip()
    if not auth:
        return ""
    if auth.startswith("tma "):
        return auth
    return "tma " + auth

# ======================= ENGINE =======================
class OpenEarnPro:
    def __init__(self, auth):
        self.auth = normalize_auth(auth)
        self.session = requests.Session()
        self.user_id = self.extract_user_id()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Telegram-iOS/10.9.1',
            'Authorization': self.auth,
            'Content-Type': 'application/json'
        }

    def extract_user_id(self):
        try:
            user_match = re.search(r'user=([^&]+)', self.auth)
            if not user_match:
                return "7330965002"
            user_json = json.loads(urllib.parse.unquote(user_match.group(1)))
            return str(user_json.get('id', '7330965002'))
        except (json.JSONDecodeError, TypeError, ValueError):
            return "7330965002"

    def request_with_retry(self, method, url, retries=MAX_RETRIES, base_delay=2, **kwargs):
        """Dinamik backoff ile gelişmiş ağ istek yöneticisi (502 ve Timeout korumalı)"""
        for i in range(1, retries + 1):
            try:
                response = self.session.request(method, url, headers=self.headers, timeout=REQUEST_TIMEOUT, **kwargs)
                if response.status_code in [502, 503, 504]:
                    print(f"\n{C3}⚠️ Sunucu hatası ({response.status_code}). Yeniden deneniyor ({i}/{retries})...{RESET}")
                else:
                    return response
            except (requests.ConnectionError, requests.Timeout) as e:
                print(f"\n{C3}⚠️ Ağ/Zaman Aşımı. Yeniden deneniyor ({i}/{retries})...{RESET}")
            
            if i < retries:
                # Exponential backoff: 2s, 4s, 8s bekleme
                time.sleep(base_delay * (2 ** (i - 1)))
        return None

    def get_data(self, url):
        response = self.request_with_retry("GET", url)
        if response:
            if response.status_code != 200:
                print(f"{C5}⚠️ API error {response.status_code}: {url}{RESET}")
                return None
            try:
                return response.json()
            except ValueError:
                print(f"{C5}⚠️ API returned invalid JSON: {url}{RESET}")
                return None
        return None

    # --- MONETAG LOGIC ---
    def run_monetag_jacky(self):
        oaid = uuid.uuid4().hex
        manifest_url = f"https://e8ys.com/500/10719545?oaid={oaid}&tgp=ios&sdkp=1&var_3={self.user_id}&sw_version=v1.801.0"
        
        res = self.request_with_retry("GET", manifest_url)
        if not res or res.status_code != 200:
            return False
        
        try:
            data = res.json()
            ruid = data.get('ruid')
            ads = data.get('ads', [])
            if not ruid or not ads:
                return False

            imp_url = ads[0].get('impression_url')
            if imp_url:
                self.request_with_retry("GET", imp_url)

            running_timer(38, "Monetag W2E")
            resolve_res = self.request_with_retry("GET", f"https://e8ys.com/resolve?ruid={ruid}")
            
            if resolve_res and resolve_res.status_code == 200:
                complete = self.request_with_retry(
                    "POST",
                    "https://app.theopenearn.com/api/ads/complete",
                    json={"ad_type": "video", "provider": "monetag", "watched": True}
                )
                return complete is not None and complete.status_code == 200
        except ValueError:
            pass
        return False

def extract_auth_from_webview_url(webview_url):
    parsed = urllib.parse.urlparse(webview_url)
    for raw_part in (parsed.fragment, parsed.query, webview_url):
        values = urllib.parse.parse_qs(raw_part).get("tgWebAppData")
        if values:
            return urllib.parse.unquote(values[0])
        decoded_part = urllib.parse.unquote(raw_part)
        if "query_id=" in decoded_part and "hash=" in decoded_part:
            auth_data = decoded_part[decoded_part.index("query_id="):]
            for marker in ("&tgWebAppVersion=", "&tgWebAppPlatform=", "&tgWebAppThemeParams="):
                if marker in auth_data:
                    auth_data = auth_data.split(marker, 1)[0]
            return auth_data
    return ""

async def prepare_bot_for_webview(client, bot_entity):
    try:
        from telethon.tl.functions.contacts import UnblockRequest
        await client(UnblockRequest(bot_entity))
        print(f"{C4}✅ @{TELEGRAM_BOT_USERNAME} unblock kontrolü tamam.{RESET}")
    except Exception:
        pass

    try:
        await client.send_message(bot_entity, "/start")
        await asyncio.sleep(1)
    except Exception:
        pass

async def request_webview(client, bot_entity, request_webview_request):
    try:
        return await client(
            request_webview_request(
                peer=bot_entity,
                bot=bot_entity,
                platform="ios",
                from_bot_menu=True,
                url=TELEGRAM_WEBAPP_URL,
            )
        )
    except Exception as exc:
        if "blocked this user" not in str(exc).lower():
            raise
        print(f"{C3}⚠️ Bot engelli görünüyor, otomatik unblock + /start deneniyor...{RESET}")
        await prepare_bot_for_webview(client, bot_entity)
        return await client(
            request_webview_request(
                peer=bot_entity,
                bot=bot_entity,
                platform="ios",
                from_bot_menu=True,
                url=TELEGRAM_WEBAPP_URL,
            )
        )

async def telegram_auth_from_phone(
    api_id,
    api_hash,
    phone,
    telegram_client_cls,
    session_password_needed_error,
    request_webview_request,
):
    client = telegram_client_cls(TELEGRAM_SESSION, int(api_id), api_hash)
    await client.connect()
    try:
        if not await client.is_user_authorized():
            await client.send_code_request(phone)
            code = input(f"{C2}Telegram kodunu gir: {RESET}").strip().replace(" ", "")
            try:
                await client.sign_in(phone=phone, code=code)
            except session_password_needed_error:
                print(f"{C3}🔐 Telegram 2FA algılandı.{RESET}")
                # SORUN ÇÖZÜMÜ: getpass() yerine standart input() kullanılarak şifrenin görünür olması sağlandı.
                password = input(f"{C2}Telegram 2FA şifresi (GÖRÜNÜR YAZILACAKTIR): {RESET}")
                await client.sign_in(password=password)
        else:
            print(f"{C4}✅ Telegram session hazır, kod gerekmedi.{RESET}")

        bot_entity = await client.get_entity(TELEGRAM_BOT_USERNAME)
        await prepare_bot_for_webview(client, bot_entity)
        webview = await request_webview(client, bot_entity, request_webview_request)
        auth_data = extract_auth_from_webview_url(webview.url)
        if not auth_data:
            raise RuntimeError("Telegram WebApp auth verisi alınamadı.")
        return auth_data
    finally:
        await client.disconnect()

def get_request_webview_request():
    try:
        from telethon.tl.functions.messages import RequestWebViewRequest
        return RequestWebViewRequest
    except ImportError:
        try:
            from telethon.tl.functions.messages import RequestAppWebViewRequest
            return RequestAppWebViewRequest
        except ImportError as exc:
            raise RuntimeError(
                "Telethon WebView desteği bulunamadı. "
                "Lütfen 'python3 -m pip install -U telethon' ile güncelleyin."
            ) from exc

def read_telegram_login_input():
    try:
        from telethon import TelegramClient
        from telethon.errors import SessionPasswordNeededError
        RequestWebViewRequest = get_request_webview_request()
    except (ImportError, RuntimeError) as exc:
        panel(
            "TELEGRAM MODÜLÜ HAZIR DEĞİL",
            [
                f"{C5}❌ {exc}{RESET}",
                f"{C3}➜ Kur/Güncelle: {WHITE}python3 -m pip install -U telethon{RESET}",
                f"{C5}Query/Auth fallback kapalı; Telethon düzelmeden devam edilmez.{RESET}",
            ],
        )
        sys.exit(1)

    api_id = TELEGRAM_API_ID
    api_hash = TELEGRAM_API_HASH
    phone = TELEGRAM_PHONE

    if not api_id or not api_hash or not phone:
        print(f"{C5}❌ API ID, API HASH ve telefon boş olamaz.{RESET}")
        sys.exit(1)

    while True:
        print(f"{C4}✅ Kayıtlı Telegram bilgileri kullanılıyor: {WHITE}{mask_value(phone)}{RESET}")
        print(f"{C3}⏳ Telegram bağlanıyor; kod gelirse gir, 2FA varsa otomatik algılanacak...{RESET}")
        try:
            return asyncio.run(
                telegram_auth_from_phone(
                    api_id,
                    api_hash,
                    phone,
                    TelegramClient,
                    SessionPasswordNeededError,
                    RequestWebViewRequest,
                )
            )
        except KeyboardInterrupt:
            raise
        except Exception as exc:
            print(f"{C5}❌ Telegram bağlantısı başarısız: {exc}{RESET}")
            print(f"{C3}⏳ Query/Auth'a geçilmeyecek. {TELEGRAM_LOGIN_RETRY_DELAY}s sonra tekrar denenecek...{RESET}")
            time.sleep(TELEGRAM_LOGIN_RETRY_DELAY)

def read_auth_input():
    panel(
        "NINOCOIN OTO GİRİŞ",
        [
            f"{C4}✅ Telegram API ve telefon otomatik dolduruldu.{RESET}",
            f"{C1}Telefon: {WHITE}{mask_value(TELEGRAM_PHONE)} {C1}┃ Bot: {WHITE}@{TELEGRAM_BOT_USERNAME}{RESET}",
            f"{C3}Query/Auth fallback kapalı; bot sadece Telegram ile giriş yapacak.{RESET}",
        ],
    )
    return read_telegram_login_input()

# ======================= MAIN LOOP =======================
def main():
    clear()
    banner()
    bot = OpenEarnPro(read_auth_input())

    start_bal = 0.0
    p_index = 0
    empty_refreshes = 0

    while True:
        user = bot.get_data("https://app.theopenearn.com/api/user")
        status = bot.get_data("https://app.theopenearn.com/api/ads/daily-status")
        if not user or not status:
            empty_refreshes += 1
            if empty_refreshes >= MAX_EMPTY_REFRESHES:
                print(f"{C5}❌ Bağlantı/Auth çalışmadı veya süresi doldu. Yeniden giriş yapın.{RESET}")
                bot = OpenEarnPro(read_auth_input())
                empty_refreshes = 0
            else:
                print(f"{C3}⏳ Veri alınamadı, tekrar deneniyor ({empty_refreshes}/{MAX_EMPTY_REFRESHES})...{RESET}")
                time.sleep(5)
            continue
        empty_refreshes = 0

        if start_bal == 0.0:
            start_bal = float(user['balance'])

        clear()
        banner()
        print(f"{C1}👤 User: {WHITE}{user['username']} {C1}┃ 💰 Bal: {C4}{user['balance']} USDT{RESET}")
        print(LINE)

        print(f"{C3}{BOLD}{'PROVIDER':<15} | {'LIMIT':<6} | {'USED':<6} | {'LEFT':<6} | {'STATUS'}{RESET}")
        providers = status.get('providers', {})
        active_p = []

        for p in WORKING_PROVIDERS:
            info = providers.get(p)
            if not info:
                continue
            u, l = info.get('used', 0), info.get('limit', 0)
            rem = max(0, l - u)

            if rem > 0:
                if info.get('blocked'):
                    stat = f"{C3}[FORCE]{RESET}"
                else:
                    stat = f"{C4}[READY]{RESET}"
                active_p.append(p)
            else:
                stat = f"{WHITE}[DONE]{RESET}"

            print(f"{p.capitalize():<15} | {l:<6} | {u:<6} | {rem:<6} | {stat}")
        print(LINE)

        if not active_p:
            bot.request_with_retry("POST", "https://app.theopenearn.com/api/wheel/spin", json={"is_paid": False})
            final_user = bot.get_data("https://app.theopenearn.com/api/user") or user
            clear()
            banner()
            print(f"{C4}{BOLD}        🎉 NINOCOIN FINAL REPORT 🎉{RESET}")
            print(LINE)
            print(f"{C1}👤 USERNAME  : {WHITE}{final_user['username']}")
            print(f"{C1}💰 FINAL BAL : {C4}{final_user['balance']} USDT")
            print(f"{C1}📈 PROFIT    : {C4}+{round(float(final_user['balance']) - start_bal, 5)} USDT")
            print(LINE)
            sys.exit()

        target = active_p[p_index % len(active_p)]
        p_index += 1

        now = datetime.now().strftime("%H:%M:%S")
        print(f"[{now}] {C1}📺 Targeting: {C3}{target.upper()}{RESET}")

        if target == "monetag":
            if bot.run_monetag_jacky():
                print(f"[{now}] {C4}✅ Monetag Success!{RESET}")
            else:
                print(f"[{now}] {C5}❌ Monetag Failed. Moving...{RESET}")
        else:
            watch_time = 30 if target == "adsgram" else 60
            running_timer(watch_time, f"Watching {target.upper()}")
            
            res = bot.request_with_retry(
                "POST",
                "https://app.theopenearn.com/api/ads/complete",
                json={"ad_type": "video", "provider": target, "watched": True}
            )
            
            if res and res.status_code == 200:
                print(f"[{now}] {C4}✅ {target.upper()} Claim Success!{RESET}")
                if target == "adsgram":
                    running_timer(60, "Cooldown")
            else:
                code = res.status_code if res else "Zaman Aşımı"
                print(f"[{now}] {C5}❌ {target.upper()} Blocked/Fail ({code}).{RESET}")

        time.sleep(2)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit()
