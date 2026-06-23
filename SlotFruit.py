#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =====================================================================
#  NINOKI SLOTFRUIT – Premium Faucet Automation Engine
#  Package: com.piratebaixe.slotMobile
#  UI/UX: AAA Terminal Dashboard Edition
# =====================================================================

import json
import os
import shutil
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse
from http.client import HTTPException
from urllib.error import HTTPError, URLError
from urllib.request import Request, build_opener

# ============================================
#  PREMIUM ANSI COLOUR PALETTE (AAA STYLING)
# ============================================
RESET = '\x1b[0m'
BOLD = '\x1b[1m'
RED = '\x1b[38;5;196m'
GREEN = '\x1b[38;5;46m'
YELLOW = '\x1b[38;5;220m'
BLUE = '\x1b[38;5;33m'
MAGENTA = '\x1b[38;5;199m'
CYAN = '\x1b[38;5;45m'
GREY = '\x1b[38;5;244m'
BG_PANEL = '\x1b[48;5;234m'

# ============================================
#  GLOBAL CONFIGURATION
# ============================================
SCRIPT_NAME = "NINOKI SLOTFRUIT"
BASE_URL = "https://slotfruits.com/api/v1/users"
LOGIN_URL = f"{BASE_URL}/signupFaucetPayLogin"
SPIN_URL = f"{BASE_URL}/earnRoll"
PROFILE_URL = f"{BASE_URL}/me"

DEFAULT_TIMEOUT = 25
REQUEST_DELAY = 1.5
COOLDOWN_DELAY = 30
AD_DELAY = 0.25
AD_ROUNDS = 3
MAX_RETRIES = 3
RETRY_BACKOFF = 3.0

AD_URL = "https://googleads.g.doubleclick.net/mads/static/sdk/native/sdk-core-v40.html"

COMMON_HEADERS = {
    "User-Agent": "okhttp/4.12.0",
    "Accept": "application/json",
    "Content-Type": "application/json; charset=UTF-8",
    "Connection": "Keep-Alive",
}

class RequestError(RuntimeError):
    pass

@dataclass
class HttpResponse:
    status_code: int
    text: str
    content_type: str = ""

class HttpSession:
    def __init__(self) -> None:
        self.headers: dict[str, str] = {}
        self._opener = build_opener()

    def __enter__(self) -> "HttpSession":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        return None

    def request(self, method: str, url: str, timeout: int = DEFAULT_TIMEOUT, **kwargs: Any) -> HttpResponse:
        headers = dict(self.headers)
        headers.update(kwargs.pop("headers", {}) or {})
        body = kwargs.pop("data", None)
        
        if "json" in kwargs:
            body = json.dumps(kwargs.pop("json")).encode("utf-8")
        elif isinstance(body, str):
            body = body.encode("utf-8")
            
        req = Request(url, data=body, headers=headers, method=method.upper())
        try:
            with self._opener.open(req, timeout=timeout) as res:
                text = res.read().decode("utf-8", "replace")
                content_type = res.headers.get("Content-Type", "")
                status = getattr(res, "status", getattr(res, "code", 200))
                return HttpResponse(status, text, content_type)
        except HTTPError as exc:
            text = exc.read().decode("utf-8", "replace") if exc.fp else str(exc)
            raise RequestError(f"HTTP {exc.code}: {text[:150]}") from exc
        except (URLError, TimeoutError, HTTPException, OSError) as exc:
            raise RequestError(str(exc)) from exc

    def get(self, url: str, timeout: int = DEFAULT_TIMEOUT, **kwargs: Any) -> HttpResponse:
        return self.request("GET", url, timeout=timeout, **kwargs)

    def post(self, url: str, timeout: int = DEFAULT_TIMEOUT, **kwargs: Any) -> HttpResponse:
        return self.request("POST", url, timeout=timeout, **kwargs)

@dataclass
class AccountState:
    email: str
    token: str
    user_id: str
    balance: str = "0.00"
    credits: int = 0

def is_json_response(response: HttpResponse) -> bool:
    text = response.text.strip()
    if not text or text.startswith(("<", "<!DOCTYPE", "<html")):
        return False
    ct = response.content_type.lower()
    if "html" in ct:
        return False
    return True

def safe_json_loads(response: HttpResponse) -> dict[str, Any]:
    text = response.text.strip()
    if not text:
        raise RequestError("Sunucu bos yanit dondurdu.")
    if text.startswith(("<", "<!DOCTYPE", "<html")):
        raise RequestError("Sunucu HTML dondurdu (Cloudflare korumasi veya bakim modu).")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise RequestError(f"JSON Ayristirma Hatasi: {exc}") from exc
    return data if isinstance(data, dict) else {"data": data}

def request_json(session: HttpSession, method: str, url: str, **kwargs: Any) -> dict[str, Any]:
    retries = kwargs.pop("retries", MAX_RETRIES)
    last_error = None
    for attempt in range(retries + 1):
        try:
            response = session.request(method, url, timeout=DEFAULT_TIMEOUT, **kwargs)
            if not is_json_response(response):
                if attempt < retries:
                    wait = RETRY_BACKOFF * (attempt + 1)
                    show_status("WARNING", f"Geçersiz veri formatı. {wait}s içinde yeniden deneniyor...")
                    time.sleep(wait)
                    continue
            return safe_json_loads(response)
        except RequestError as exc:
            last_error = exc
            if attempt < retries:
                wait = RETRY_BACKOFF * (attempt + 1)
                show_status("RETRY", f"Bağlantı hatası (Deneme {attempt+1}/{retries+1}). {wait}s bekleniyor...")
                time.sleep(wait)
            else:
                raise last_error
    raise last_error or RequestError("Bilinmeyen kritik hata.")

def auth_headers(token: str) -> dict[str, str]:
    headers = dict(COMMON_HEADERS)
    headers["Authorization"] = f"Bearer {token}"
    return headers

# ============================================
#  AAA TERMINAL GRAPHICS ENGINE
# ============================================

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def get_width():
    return min(shutil.get_terminal_size((80, 20)).columns, 90)

def draw_accent_line():
    w = get_width()
    print(f"{CYAN}╔" + "═" * (w - 2) + "╗" + f"{RESET}")

def draw_bottom_line():
    w = get_width()
    print(f"{CYAN}╚" + "═" * (w - 2) + "╝" + f"{RESET}")

def draw_divider():
    w = get_width()
    print(f"{GREY}╟" + "─" * (w - 2) + "╢" + f"{RESET}")

def center_text(text, color=RESET):
    w = get_width()
    clean_text = text
    # Remove ANSI code lengths for proper centering computation
    for c in [RESET, BOLD, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, GREY]:
        clean_text = clean_text.replace(c, "")
    padding = max(0, (w - 2 - len(clean_text)) // 2)
    right_padding = max(0, w - 2 - len(clean_text) - padding)
    print(f"{CYAN}║{RESET}" + " " * padding + color + text + RESET + " " * right_padding + f"{CYAN}║{RESET}")

def render_banner():
    clear()
    draw_accent_line()
    center_text(f"{BOLD}{MAGENTA}║ 🎰 {SCRIPT_NAME} 🎰 ║{RESET}", f"{BOLD}{MAGENTA}")
    center_text(f"{CYAN}Automated High-Performance Faucet System{RESET}", CYAN)
    center_text(f"{GREY}Premium AAA Architecture | Secure Execution Flow{RESET}", GREY)
    draw_divider()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    center_text(f"{YELLOW}Sistem Zamanı: {now}{RESET}", YELLOW)
    draw_bottom_line()

def show_loading(text, duration=1.5):
    w = get_width()
    spinners = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    end_time = time.time() + duration
    i = 0
    while time.time() < end_time:
        sys.stdout.write(f"\r {CYAN}║{RESET} {YELLOW}{spinners[i % len(spinners)]}{RESET} {text}...")
        sys.stdout.flush()
        time.sleep(0.1)
        i += 1
    sys.stdout.write("\r" + " " * (w-1) + "\r")

def show_status(status_type, message):
    prefix = {
        "SUCCESS": f"{GREEN}[✔ SUCCESS]{RESET}",
        "ERROR": f"{RED}[✘ ERROR  ]{RESET}",
        "WARNING": f"{YELLOW}[⚠ WARNING]{RESET}",
        "RETRY": f"{BLUE}[🔄 RETRY  ]{RESET}",
        "INFO": f"{CYAN}[ℹ INFO   ]{RESET}"
    }.get(status_type, f"{GREY}[INFO]{RESET}")
    
    print(f" {prefix} {message}")

def print_dashboard(state: AccountState):
    w = get_width()
    draw_accent_line()
    center_text(f"{BOLD}{BLUE}📡 AKTİF KULLANICI GÖSTERGE PANELİ{RESET}")
    draw_divider()
    
    email_str = f" {BOLD}E-Posta Adresi{RESET} : {CYAN}{state.email}{RESET}"
    balance_str = f" {BOLD}Mevcut Bakiye {RESET} : {GREEN}{state.balance} Faucet Coins{RESET}"
    credits_str = f" {BOLD}Kalan Spin Hakı{RESET} : {YELLOW}{state.credits}{RESET}"
    
    # Render fields neatly
    for s in [email_str, balance_str, credits_str]:
        clean = s
        for c in [RESET, BOLD, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, GREY]:
            clean = clean.replace(c, "")
        right_pad = max(0, w - 4 - len(clean))
        print(f"{CYAN}║{RESET} {s}" + " " * right_pad + f" {CYAN}║{RESET}")
        
    draw_bottom_line()

# ============================================
#  CORE CORE INTERACTION LOGIC
# ============================================

def login(email: str) -> tuple[str | None, dict[str, Any] | None]:
    render_banner()
    show_loading("Kullanıcı kimliği doğrulanıyor ve sisteme giriş yapılıyor", 2.0)

    with HttpSession() as session:
        session.headers.update(COMMON_HEADERS)
        payload = {
            "email": email,
            "device": "android",
            "package": "com.piratebaixe.slotMobile"
        }
        try:
            data = request_json(session, "POST", LOGIN_URL, json=payload, headers=COMMON_HEADERS)
            token = data.get("token") or data.get("accessToken") or data.get("access_token") or data.get("jwt")
            if not token:
                show_status("ERROR", "Kimlik doğrulama başarılı fakat erişim tokeni alınamadı.")
                return None, None
            
            user = data.get("user") if isinstance(data.get("user"), dict) else data
            show_status("SUCCESS", "Giriş işlemi başarıyla tamamlandı.")
            return token, user
        except Exception as exc:
            show_status("ERROR", f"Giriş anahtarı alınırken sunucu hatası oluştu: {exc}")
            return None, None

def fetch_profile_safely(session: HttpSession, token: str) -> dict[str, Any] | None:
    """Sunucudan en güncel kullanıcı verilerini (bakiye ve spin hakkı) çeker."""
    headers = auth_headers(token)
    try:
        data = request_json(session, "GET", PROFILE_URL, headers=headers, retries=1)
        return data.get("user") if isinstance(data.get("user"), dict) else data
    except Exception:
        return None

def spin_once(session: HttpSession, token: str) -> dict[str, Any] | None:
    headers = auth_headers(token)
    try:
        return request_json(session, "GET", SPIN_URL, headers=headers, retries=1)
    except RequestError as exc:
        show_status("ERROR", f"Spin işlemi gerçekleştirilemedi: {exc}")
        return None

def ads_loop(userid: str):
    """Google AdMob / DoubleClick reklam izleme simülasyonu tetikleyicisi"""
    try:
        print(f"\n {GREY}┌────────────────────────────────────────────────────────┐{RESET}")
        print(f" {GREY}│{RESET} {CYAN}📺 Premium Reklam Döngüsü Başlatılıyor...{RESET}               {GREY}│{RESET}")
        print(f" {GREY}└────────────────────────────────────────────────────────┘{RESET}")

        with HttpSession() as session:
            for index in range(1, AD_ROUNDS + 1):
                try:
                    parsed = urlparse(AD_URL)
                    qs = parse_qs(parsed.query)
                    qs["seq_num"] = [str(index)]
                    qs["rwd_userid"] = [str(userid)]
                    new_url = urlunparse(parsed._replace(query=urlencode(qs, doseq=True)))

                    response = session.get(new_url, timeout=DEFAULT_TIMEOUT)
                    if response.status_code < 400:
                        show_status("SUCCESS", f"Reklam Paketi Tetiklendi [{index}/{AD_ROUNDS}]")
                    else:
                        show_status("WARNING", f"Reklam Paketi Uyarı Kod Aldı [{index}/{AD_ROUNDS}]: HTTP {response.status_code}")
                except RequestError as exc:
                    show_status("WARNING", f"Reklam Hatası [{index}/{AD_ROUNDS}]: {exc}")
                time.sleep(AD_DELAY)

        show_status("SUCCESS", "Reklam döngüsü kararlılıkla tamamlandı.")
    except Exception as e:
        show_status("ERROR", f"Reklam havuzu genel hatası: {e}")
        time.sleep(2)

def spin_loop(email: str, token: str, balance: str, credits: int, userid: str):
    """Ana otomasyon döngüsü."""
    state = AccountState(email=email, token=token, user_id=userid, balance=str(balance), credits=credits)
    total_spins_in_session = 0

    with HttpSession() as session:
        session.headers.update(COMMON_HEADERS)

        while True:
            try:
                render_banner()
                print_dashboard(state)

                # Haklar bittiyse otomatik olarak reklam izle ve profili sunucudan kontrol et
                if state.credits <= 0:
                    show_status("WARNING", "Kullanılabilir Spin hakkı kalmadı. Reklam döngüsü çalıştırılıyor...")
                    ads_loop(state.user_id)
                    
                    show_loading("Yeni spin hakları için profil güncelleniyor", 4.0)
                    profile_data = fetch_profile_safely(session, token)
                    if profile_data:
                        new_credits = profile_data.get("credits", 0)
                        state.balance = str(profile_data.get("balance", state.balance))
                        if isinstance(new_credits, str):
                            new_credits = int(''.join(ch for ch in new_credits if ch.isdigit()) or 0)
                        state.credits = int(new_credits)
                        
                        if state.credits > 0:
                            show_status("SUCCESS", f"Harika! Sunucudan {state.credits} yeni spin hakkı alındı.")
                            time.sleep(2)
                            continue
                    
                    show_status("INFO", f"Henüz yeni hak tanımlanmadı. {COOLDOWN_DELAY} saniye sonra tekrar kontrol edilecek...")
                    time.sleep(COOLDOWN_DELAY)
                    continue

                show_loading("Slot makinesi döndürülüyor (Earn Roll)", REQUEST_DELAY)
                data = spin_once(session, token)
                
                if data is None:
                    show_status("RETRY", "Hata oluştu, döngü yeniden başlatılıyor...")
                    time.sleep(3)
                    continue

                success = data.get("success", False) or (data.get("status") == "success")
                
                # Yeni bakiye ve kredi verilerini güvenli bir şekilde işle
                new_balance = data.get("balance") or data.get("user", {}).get("balance")
                if new_balance is not None:
                    state.balance = str(new_balance)
                    
                raw_credits = data.get("credits") or data.get("user", {}).get("credits")
                if raw_credits is not None:
                    if isinstance(raw_credits, str):
                        raw_credits = int(''.join(ch for ch in raw_credits if ch.isdigit()) or 0)
                    state.credits = int(raw_credits)
                else:
                    # Fallback if endpoint doesn't return updated credits explicitly
                    state.credits = max(0, state.credits - 1)

                total_spins_in_session += 1
                
                if success:
                    reward = data.get("reward") or data.get("win") or "Ödül Alındı"
                    show_status("SUCCESS", f"Başarılı Spin! Kazanılan Ödül: {GREEN}{reward}{RESET}")
                else:
                    message = data.get("message", "Sunucu spini onaylamadı veya pas geçti.")
                    show_status("WARNING", f"Spin Es Geçildi: {message}")

                show_status("INFO", f"Oturumdaki Toplam Spin: {total_spins_in_session}")
                time.sleep(1.0)

            except KeyboardInterrupt:
                print("\n")
                show_status("ERROR", "Kullanıcı tarafından durduruldu. Çıkış yapılıyor...")
                break
            except Exception as e:
                show_status("ERROR", f"Döngü içerisinde çalışma zamanı hatası: {e}")
                time.sleep(5)

# ============================================
#  MAIN ENTRY POINT
# ============================================

def main():
    clear()
    render_banner()

    print(f"\n {BOLD}{CYAN}🔑 KULLANICI GİRİŞ PANELİ{RESET}")
    print(f" {GREY}────────────────────────────────────────────────────────{RESET}")
    email = input(f" {BOLD}{YELLOW}▶ FaucetPay E-Posta Adresinizi Girin:{RESET} ").strip()

    if not email or "@" not in email:
        print("")
        show_status("ERROR", "Geçersiz e-posta formatı girdiniz. Program sonlandırılıyor.")
        sys.exit(1)

    token, user = login(email)

    if not token or not user:
        print("")
        show_status("ERROR", "Kimlik doğrulama başarısız. Bilgilerinizi kontrol edin.")
        sys.exit(1)

    balance = str(user.get('balance', '0.00'))
    credits = user.get('credits', 0)
    if isinstance(credits, str):
        credits = int(''.join(ch for ch in credits if ch.isdigit()) or 0)
        
    userid = str(user.get('id') or user.get('_id') or email)

    # Otomasyon döngüsünü başlat
    spin_loop(email, token, balance, credits, userid)

if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as critical_error:
        print(f"\n\x1b[31m[KRİTİK SİSTEM HATASI]: {critical_error}\x1b[0m")
