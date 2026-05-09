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
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

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

# RichAds öncelikli olacak şekilde
WORKING_PROVIDERS = ["richads", "monetag", "adsgram"]
REQUEST_TIMEOUT = 20
MAX_EMPTY_REFRESHES = 3

# TonexaSpinBot altyapısına göre çevresel değişkenler
TELEGRAM_BOT_USERNAME = os.getenv("TONEXA_TG_BOT", "TonexaSpinBot")
TELEGRAM_WEBAPP_URL = os.getenv("TONEXA_TG_WEBAPP_URL", "https://app.theopenearn.com/")
TELEGRAM_SESSION = os.getenv("TONEXA_TG_SESSION", "tonexa_telegram")
TELEGRAM_API_ID = os.getenv("TONEXA_API_ID", "26025122")
TELEGRAM_API_HASH = os.getenv("TONEXA_API_HASH", "9c832a240c0ba7cd4b01189ee35a6c59")
TELEGRAM_PHONE = os.getenv("TONEXA_PHONE", "+905518951725")
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
        print(center("████████╗████████╗███╗   ██╗███████╗██╗  ██╗ █████╗ "))
        print(center("╚══██╔══╝██╔═══██╗████╗  ██║██╔════╝╚██╗██╔╝██╔══██╗"))
        print(center("   ██║   ██║   ██║██╔██╗ ██║█████╗   ╚███╔╝ ███████║"))
        print(center("   ██║   ██║   ██║██║╚██╗██║██╔══╝   ██╔██╗ ██╔══██║"))
        print(center("   ██║   ╚██████╔╝██║ ╚████║███████╗██╔╝ ██╗██║  ██║"))
        print(center("   ╚═╝    ╚═════╝ ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝"))
        print(f"{WHITE}{BOLD}{center('TONEXA SPIN BOT')}{RESET}")
    else:
        print("████████╗████████╗███╗   ██╗███████╗██╗  ██╗ █████╗ ")
        print("╚══██╔══╝██╔═══██╗████╗  ██║██╔════╝╚██╗██╔╝██╔══██╗")
        print("   ██║   ██║   ██║██╔██╗ ██║█████╗   ╚███╔╝ ███████║")
        print("   ██║   ██║   ██║██║╚██╗██║██╔══╝   ██╔██╗ ██╔══██║")
        print("   ██║   ╚██████╔╝██║ ╚████║███████╗██╔╝ ██╗██║  ██║")
        print("   ╚═╝    ╚═════╝ ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝")
    print(f"{RESET}")
    print(LINE)
    print(f"{C4}👑 DEV: {WHITE}TONEXA {C1}┃ {C3}⚡ LOGIN: {WHITE}TELEGRAM{RESET}")
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
        self.session = self._create_robust_session()
        self.user_id = self.extract_user_id()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Telegram-iOS/10.9.1',
            'Authorization': self.auth,
            'Content-Type': 'application/json'
        }

    def _create_robust_session(self):
        session = requests.Session()
        retry = Retry(
            total=3,
            read=3,
            connect=3,
            backoff_factor=0.3,
            status_forcelist=(500, 502, 504)
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    def extract_user_id(self):
        try:
            user_match = re.search(r'user=([^&]+)', self.auth)
            if not user_match:
                return "7330965002"
            user_json = json.loads(urllib.parse.unquote(user_match.group(1)))
            return str(user_json.get('id', '7330965002'))
        except Exception:
            return "7330965002"

    def get_data(self, url):
        try:
            response = self.session.get(url, headers=self.headers, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as errh:
            print(f"{C5}⚠️ API HTTP Hatası: {errh}{RESET}")
            return None
        except requests.exceptions.ConnectionError:
            print(f"{C5}⚠️ Bağlantı Hatası: İnternet bağlantınızı kontrol edin.{RESET}")
            return None
        except requests.exceptions.Timeout:
            print(f"{C5}⚠️ Zaman Aşımı: Sunucu {REQUEST_TIMEOUT}s içinde yanıt vermedi.{RESET}")
            return None
        except requests.exceptions.RequestException as err:
            print(f"{C5}⚠️ Beklenmeyen Hata: {err}{RESET}")
            return None
        except ValueError:
            print(f"{C5}⚠️ API geçersiz JSON döndürdü: {url}{RESET}")
            return None

    def run_monetag_jacky(self):
        oaid = uuid.uuid4().hex
        manifest_url = f"https://e8ys.com/500/10719545?oaid={oaid}&tgp=ios&sdkp=1&var_3={self.user_id}&sw_version=v1.801.0"
        try:
            res = self.session.get(manifest_url, headers=self.headers, timeout=REQUEST_TIMEOUT)
            if res.status_code != 200:
                return False
            data = res.json()
            ruid = data.get('ruid')
            ads = data.get('ads', [])
            if not ruid or not ads:
                return False

            imp_url = ads[0].get('impression_url')
            if imp_url:
                self.session.get(imp_url, headers=self.headers, timeout=10)

            running_timer(38, "Monetag İzleniyor")
            resolve_res = self.session.get(
                f"https://e8ys.com/resolve?ruid={ruid}",
                headers=self.headers,
                timeout=REQUEST_TIMEOUT,
            )
            if resolve_res.status_code == 200:
                complete = self.session.post(
                    "https://app.theopenearn.com/api/ads/complete",
                    headers=self.headers,
                    json={"ad_type": "video", "provider": "monetag", "watched": True},
                    timeout=REQUEST_TIMEOUT,
                )
                return complete.status_code == 200
        except Exception:
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


async def prepare_bot_for_webview(client, bot_username):
    try:
        from telethon.tl.functions.contacts import UnblockRequest
        bot_entity = await client.get_input_entity(bot_username)
        await client(UnblockRequest(bot_entity))
        print(f"{C4}✅ @{bot_username} unblock kontrolü tamam.{RESET}")
    except Exception:
        pass

    try:
        bot_entity = await client.get_input_entity(bot_username)
        await client.send_message(bot_entity, "/start")
        await asyncio.sleep(1.5) 
    except Exception as e:
        print(f"{C3}⚠️ Bot başlatma denemesi başarısız oldu (Hata önemsiz olabilir): {e}{RESET}")


async def request_webview(client, bot_username, request_webview_request):
    bot_entity = await client.get_input_entity(bot_username)
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
        if "blocked" in str(exc).lower() or "inputuser" in str(exc).lower():
            print(f"{C3}⚠️ Bot engelli/bulunamadı, otomatik unblock + /start deneniyor...{RESET}")
            await prepare_bot_for_webview(client, bot_username)
            return await client(
                request_webview_request(
                    peer=bot_entity,
                    bot=bot_entity,
                    platform="ios",
                    from_bot_menu=True,
                    url=TELEGRAM_WEBAPP_URL,
                )
            )
        raise exc


async def telegram_auth_from_phone(api_id, api_hash, phone, telegram_client_cls, session_password_needed_error, request_webview_request):
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
                password = getpass.getpass(f"{C2}Telegram 2FA şifresi: {RESET}")
                await client.sign_in(password=password)
        else:
            print(f"{C4}✅ Telegram session hazır, kod gerekmedi.{RESET}")

        webview = await request_webview(client, TELEGRAM_BOT_USERNAME, request_webview_request)
        auth_data = extract_auth_from_webview_url(webview.url)
        if not auth_data:
            raise RuntimeError("Telegram WebApp auth verisi alınamadı.")
        return auth_data
    finally:
        await client.disconnect()


def get_request_webview_request():
    # Hata veren RequestAppWebViewRequest denemesini tamamen kaldırdım.
    # Sadece stabil ve bot parametresini destekleyen RequestWebViewRequest'i kullanıyoruz.
    try:
        from telethon.tl.functions.messages import RequestWebViewRequest
        return RequestWebViewRequest
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
                f"{C3}➜ Kur/Güncelle: {WHITE}python3 -m pip install -U telethon{RESET}"
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
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(
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
            print(f"\n{C5}İşlem kullanıcı tarafından iptal edildi.{RESET}")
            sys.exit(0)
        except Exception as exc:
            print(f"{C5}❌ Telegram bağlantısı başarısız: {exc}{RESET}")
            print(f"{C3}⏳ {TELEGRAM_LOGIN_RETRY_DELAY}s sonra tekrar denenecek...{RESET}")
            time.sleep(TELEGRAM_LOGIN_RETRY_DELAY)


def read_auth_input():
    panel(
        "TONEXA OTO GİRİŞ",
        [
            f"{C4}✅ Telegram API ve telefon otomatik dolduruldu.{RESET}",
            f"{C1}Telefon: {WHITE}{mask_value(TELEGRAM_PHONE)} {C1}┃ Bot: {WHITE}@{TELEGRAM_BOT_USERNAME}{RESET}"
        ],
    )
    return read_telegram_login_input()

# ======================= MAIN LOOP =======================
def main():
    clear()
    banner()
    auth_data = read_auth_input()
    bot = OpenEarnPro(auth_data)

    start_bal = 0.0
    p_index = 0
    empty_refreshes = 0

    while True:
        user = bot.get_data("https://app.theopenearn.com/api/user")
        status = bot.get_data("https://app.theopenearn.com/api/ads/daily-status")
        
        if not user or not status:
            empty_refreshes += 1
            if empty_refreshes >= MAX_EMPTY_REFRESHES:
                print(f"{C5}❌ Bağlantı/Auth çalışmadı veya süresi doldu. Yeniden giriş yapılıyor...{RESET}")
                auth_data = read_auth_input()
                bot = OpenEarnPro(auth_data)
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
        print(f"{C1}👤 User: {WHITE}{user.get('username', 'Bilinmiyor')} {C1}┃ 💰 Bal: {C4}{user.get('balance', 0)} USDT{RESET}")
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
                stat = f"{C3}[FORCE]{RESET}" if info.get('blocked') else f"{C4}[READY]{RESET}"
                active_p.append(p)
            else:
                stat = f"{WHITE}[DONE]{RESET}"

            print(f"{p.capitalize():<15} | {l:<6} | {u:<6} | {rem:<6} | {stat}")
        print(LINE)

        if not active_p:
            try:
                bot.session.post(
                    "https://app.theopenearn.com/api/wheel/spin",
                    headers=bot.headers,
                    json={"is_paid": False},
                    timeout=REQUEST_TIMEOUT,
                )
            except Exception as e:
                print(f"{C5}⚠️ Çark çevirme hatası: {e}{RESET}")
                
            final_user = bot.get_data("https://app.theopenearn.com/api/user") or user
            clear()
            banner()
            print(f"{C4}{BOLD}        🎉 TONEXA FINAL REPORT 🎉{RESET}")
            print(LINE)
            print(f"{C1}👤 USERNAME  : {WHITE}{final_user.get('username', 'Bilinmiyor')}")
            print(f"{C1}💰 FINAL BAL : {C4}{final_user.get('balance', 0)} USDT")
            print(f"{C1}📈 PROFIT    : {C4}+{round(float(final_user.get('balance', 0)) - start_bal, 5)} USDT")
            print(LINE)
            sys.exit(0)

        target = active_p[p_index % len(active_p)]
        p_index += 1

        now = datetime.now().strftime("%H:%M:%S")
        print(f"[{now}] {C1}📺 Hedefleniyor: {C3}{target.upper()}{RESET}")

        if target == "monetag":
            if bot.run_monetag_jacky():
                print(f"[{now}] {C4}✅ Monetag Başarılı!{RESET}")
            else:
                print(f"[{now}] {C5}❌ Monetag Başarısız. Geçiliyor...{RESET}")
        else:
            watch_time = 30 if target == "adsgram" else 60
            running_timer(watch_time, f"{target.upper()} İzleniyor")
            try:
                res = bot.session.post(
                    "https://app.theopenearn.com/api/ads/complete",
                    headers=bot.headers,
                    json={"ad_type": "video", "provider": target, "watched": True},
                    timeout=REQUEST_TIMEOUT,
                )
                if res.status_code == 200:
                    print(f"[{now}] {C4}✅ {target.upper()} Claim Başarılı!{RESET}")
                    if target == "adsgram":
                        running_timer(60, "Cooldown Bekleniyor")
                else:
                    print(f"[{now}] {C5}❌ {target.upper()} Blocked/Fail ({res.status_code}).{RESET}")
            except requests.exceptions.RequestException as exc:
                print(f"[{now}] {C5}❌ {target.upper()} Ağ Hatası: {exc}{RESET}")

        time.sleep(2)

if __name__ == "__main__":
    try:
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        main()
    except KeyboardInterrupt:
        print(f"\n{C5}Sistem manuel olarak kapatıldı.{RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{C5}Beklenmeyen bir fatal hata oluştu: {e}{RESET}")
        sys.exit(1)
