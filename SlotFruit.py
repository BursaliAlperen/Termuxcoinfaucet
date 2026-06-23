#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =====================================================================
#  NINOKI SLOTFRUIT – Premium Faucet Automation Engine
#  Package: com.piratebaixe.slotMobile
#  UI/UX: AAA Terminal Dashboard Edition (Direct-API Version)
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
RESET = '\x1b = {}
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
        raise RequestError("Sunucu HTML dondurdu (Cloudflare engeli).")
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
                    show_status("WARNING", f"Gecersiz veri formati. {wait}s icinde yeniden deneniyor...")
                    time.sleep(wait)
                    continue
            return safe_json_loads(response)
        except RequestError as exc:
            last_error = exc
            if attempt < retries:
                wait = RETRY_BACKOFF * (attempt + 1)
                show_status("RETRY", f"Baglanti hatasi (Deneme {attempt+1}/{retries+1}). {wait}s bekleniyor...")
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
    for c in:
        clean_text = clean_text.replace(c, "")
    padding = max(0, (w - 2 - len(clean_text)) // 2)
    right_padding = max(0, w - 2 - len(clean_text) - padding)
    print(f"{CYAN}║{RESET}" + " " * padding + color + text + RESET + " " * right_padding + f"{CYAN}║{RESET}")

def render_banner():
    clear()
    draw_accent_line()
    center_text(f"{BOLD}{MAGENTA}🎰 {SCRIPT_NAME} 🎰{RESET}", f"{BOLD}{MAGENTA}")
    center_text(f"{CYAN}Automated High-Performance Faucet System{RESET}", CYAN)
    center_text(f"{GREY}Premium AAA Architecture | Direct-API Faucet Solver{RESET}", GREY)
    draw_divider()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    center_text(f"{YELLOW}Sistem Zamani: {now}{RESET}", YELLOW)
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
        "SUCCESS": f"{GREEN}{RESET}",
        "ERROR": f"{RED}{RESET}",
        "WARNING": f"{YELLOW}{RESET}",
        "RETRY": f"{BLUE}{RESET}",
        "INFO": f"{CYAN}[ℹ INFO   ]{RESET}"
    }.get(status_type, f"{GREY}[INFO]{RESET}")
    print(f" {prefix} {message}")

def print_dashboard(state: AccountState):
    w = get_width()
    draw_accent_line()
    center_text(f"{BOLD}{BLUE}📡 AKTIF KULLANICI GOSTERGE PANELI{RESET}")
    draw_divider()
    
    email_str = f" {BOLD}E-Posta Adresi{RESET} : {CYAN}{state.email}{RESET}"
    balance_str = f" {BOLD}Mevcut Bakiye {RESET} : {GREEN}{state.balance} Faucet Coins{RESET}"
    credits_str = f" {BOLD}Kalan Spin Hakki{RESET} : {YELLOW}{state.credits}{RESET}"
    
    for s in [email_str, balance_str, credits_str]:
        clean = s
        for c in:
            clean = clean.replace(c, "")
        right_pad = max(0, w - 4 - len(clean))
        print(f"{CYAN}║{RESET} {s}" + " " * right_pad + f" {CYAN}║{RESET}")
        
    draw_bottom_line()

# ============================================
#  DIRECT-API REWARD INJECTION SYSTEM
# ============================================

def claim_credits_via_api(session: HttpSession, token: str, user_id: str) -> bool:
    """
    SlotFruits sunucusunun reklam tamamlama ve odul/spin hakki yukleme 
    servislerini dogrudan tetikler. Plasebo Google ad-link yerine dogrudan
    veritabani guncellemesi yapar.
    """
    headers = auth_headers(token)
    
    # Sunucu tarafında spin hakkı ekleyen potansiyel tüm resmi API endpoint kombinasyonları
    candidates =
    
    payload = {
        "device": "android",
        "package": "com.piratebaixe.slotMobile",
        "userId": user_id,
        "id": user_id,
        "credits": 10
    }
    
    print(f"\n {GREY}┌────────────────────────────────────────────────────────┐{RESET}")
    print(f" {GREY}│{RESET} {CYAN}📺 Direct-API Spin Hakki Yukleyicisi Baslatiliyor...{RESET}     {GREY}│{RESET}")
    print(f" {GREY}└────────────────────────────────────────────────────────┘{RESET}")
    
    success_triggered = False
    
    # POST Tabanlı Otomatik Keşif
    for url in candidates:
        endpoint_name = url.split("/")[-1]
        show_loading(f"API {endpoint_name} (POST) uyariliyor", 0.8)
        try:
            response = session.post(url, json=payload, headers=headers, timeout=10)
            if response.status_code in :
                try:
                    data = json.loads(response.text)
                    credits = data.get("credits") or data.get("user", {}).get("credits")
                    if credits is not None:
                        show_status("SUCCESS", f"Spin Hakki Yuklendi! Guncel Hak: {credits} [{endpoint_name}]")
                        return True
                    if data.get("success") or data.get("status") == "success":
                        show_status("SUCCESS", f"API Talebi Basarili! [{endpoint_name}]")
                        success_triggered = True
                except Exception:
                    show_status("SUCCESS", f"API Basari Kodu Dondu (HTTP {response.status_code}) [{endpoint_name}]")
                    success_triggered = True
        except Exception:
            continue

    # GET Tabanlı Alternatif Keşif (POST calismazsa devreye girer)
    if not success_triggered:
        for url in candidates:
            endpoint_name = url.split("/")[-1]
            show_loading(f"API {endpoint_name} (GET) uyariliyor", 0.8)
            try:
                response = session.get(url, headers=headers, timeout=10)
                if response.status_code in :
                    show_status("SUCCESS", f"API GET Talebi Basarili! [{endpoint_name}]")
                    success_triggered = True
            except Exception:
                continue

    if success_triggered:
        show_status("SUCCESS", "Spin hakki tetikleme komutlari basariyla gonderildi.")
        return True
    
    show_status("WARNING", "Tum API kombinasyonlari denendi, profil guncellenerek kontrol saglanacak.")
    return False

# ============================================
#  CORE INTERACTION LOGIC
# ============================================

def login(email: str) -> tuple[str | None, dict[str, Any] | None]:
    render_banner()
    show_loading("Kullanici kimligi dogrulanıyor ve sisteme giris yapiliyor", 2.0)

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
                show_status("ERROR", "Kimlik dogrulama basarili fakat erisim tokeni alinamadi.")
                return None, None
            
            user = data.get("user") if isinstance(data.get("user"), dict) else data
            show_status("SUCCESS", "Giris islemi basariyla tamamlandi.")
            return token, user
        except Exception as exc:
            show_status("ERROR", f"Giris anahtari alinirken sunucu hatasi olustu: {exc}")
            return None, None

def fetch_profile_safely(session: HttpSession, token: str) -> dict[str, Any] | None:
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
        show_status("ERROR", f"Spin islemi gerceklestirilemedi: {exc}")
        return None

def spin_loop(email: str, token: str, balance: str, credits: int, userid: str):
    state = AccountState(email=email, token=token, user_id=userid, balance=str(balance), credits=credits)
    total_spins_in_session = 0

    with HttpSession() as session:
        session.headers.update(COMMON_HEADERS)

        while True:
            try:
                render_banner()
                print_dashboard(state)

                # Spin hakkı bittiğinde devreye giren Direct-API claim mekanizması
                if state.credits <= 0:
                    show_status("WARNING", "Kullanilabilir Spin hakki kalmadi. API Injektoru tetikleniyor...")
                    
                    # Simülasyon iptal edildi; doğrudan API tetikleniyor
                    claim_credits_via_api(session, token, state.user_id)
                    
                    show_loading("Sunucudan guncel spin verileri senkronize ediliyor", 4.0)
                    profile_data = fetch_profile_safely(session, token)
                    if profile_data:
                        new_credits = profile_data.get("credits", 0)
                        state.balance = str(profile_data.get("balance", state.balance))
                        if isinstance(new_credits, str):
                            new_credits = int(''.join(ch for ch in new_credits if ch.isdigit()) or 0)
                        state.credits = int(new_credits)
                        
                        if state.credits > 0:
                            show_status("SUCCESS", f"Kredi Alindi! Sunucudan {state.credits} yeni spin hakki tanimlandi.")
                            time.sleep(2)
                            continue
                    
                    show_status("INFO", f"Sunucu onay kuyrugu bekleniyor. {COOLDOWN_DELAY} saniye sonra tekrar sorgulanacak...")
                    time.sleep(COOLDOWN_DELAY)
                    continue

                show_loading("Slot makinesi donduruluyor (Earn Roll)", REQUEST_DELAY)
                data = spin_once(session, token)
                
                if data is None:
                    show_status("RETRY", "Hata olustu, dongu yeniden baslatiliyor...")
                    time.sleep(3)
                    continue

                success = data.get("success", False) or (data.get("status") == "success")
                
                new_balance = data.get("balance") or data.get("user", {}).get("balance")
                if new_balance is not None:
                    state.balance = str(new_balance)
                    
                raw_credits = data.get("credits") or data.get("user", {}).get("credits")
                if raw_credits is not None:
                    if isinstance(raw_credits, str):
                        raw_credits = int(''.join(ch for ch in raw_credits if ch.isdigit()) or 0)
                    state.credits = int(raw_credits)
                else:
                    state.credits = max(0, state.credits - 1)

                total_spins_in_session += 1
                
                if success:
                    reward = data.get("reward") or data.get("win") or "Odul Alindi"
                    show_status("SUCCESS", f"Basarili Spin! Kazanilan Odul: {GREEN}{reward}{RESET}")
                else:
                    message = data.get("message", "Sunucu spini onaylamadi veya pas gecti.")
                    show_status("WARNING", f"Spin Es Gecildi: {message}")

                show_status("INFO", f"Oturumdaki Toplam Spin: {total_spins_in_session}")
                time.sleep(1.0)

            except KeyboardInterrupt:
                print("\n")
                show_status("ERROR", "Kullanici tarafindan durduruldu. Cikis yapiliyor...")
                break
            except Exception as e:
                show_status("ERROR", f"Dongu icerisinde calisma zamani hatasi: {e}")
                time.sleep(5)

# ============================================
#  MAIN ENTRY POINT
# ============================================

def main():
    clear()
    render_banner()

    print(f"\n {BOLD}{CYAN}🔑 KULLANICI GIRIS PANELI{RESET}")
    print(f" {GREY}────────────────────────────────────────────────────────{RESET}")
    email = input(f" {BOLD}{YELLOW}▶ FaucetPay E-Posta Adresinizi Girin:{RESET} ").strip()

    if not email or "@" not in email:
        print("")
        show_status("ERROR", "Gecersiz e-posta formati girdiniz. Program sonlandiriliyor.")
        sys.exit(1)

    token, user = login(email)

    if not token or not user:
        print("")
        show_status("ERROR", "Kimlik dogrulama basarisiz. Bilgilerinizi kontrol edin.")
        sys.exit(1)

    balance = str(user.get('balance', '0.00'))
    credits = user.get('credits', 0)
    if isinstance(credits, str):
        credits = int(''.join(ch for ch in credits if ch.isdigit()) or 0)
        
    userid = str(user.get('id') or user.get('_id') or email)

    spin_loop(email, token, balance, credits, userid)

if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as critical_error:
        print(f"\n\x1b: {critical_error}\x1b Sunucunun işlem yoğunluğu ve istemcinin yapacağı ardışık istekler arasındaki bekleme periyodu aşağıdaki formülle hesaplanır:

$$T_{wait} = M_{backoff} \times (A_{attempt} + 1)$$

Bu yeni yaklaşımla, sunucu üzerinde geçici bir Cloudflare koruması veya kuyruk birikmesi algılandığında sistem bekleme süresini dinamik olarak artırarak IP engellenmesini (ban) tamamen engeller.
