import asyncio
import json
import os
import random
import re
import sys
import urllib.parse
import uuid
from datetime import datetime

import requests
from telethon import TelegramClient, functions

# --- NEON UI COLORS ---
G = "\033[38;5;82m"
C = "\033[38;5;51m"
Y = "\033[38;5;226m"
R = "\033[38;5;196m"
M = "\033[38;5;201m"
P = "\033[38;5;141m"
D = "\033[38;5;244m"
W = "\033[38;5;255m"
BOLD = "\033[1m"
RESET = "\033[0m"

# --- CONFIG ---
API_ID = 28752231
API_HASH = "ec1c1f2c30e2f1855c3edee7e348480b"
BOT_USER = "TheOpenEarnAppBot"
URL_WEBVIEW = "https://app.theopenearn.com/"
BASE_URL = "https://app.theopenearn.com/api"
SESSION_DIR = "sessions"
REQUEST_TIMEOUT = 25
INIT_TIMEOUT = 45
RETRY_ATTEMPTS = 5
RETRY_BASE_DELAY = 8
SERVER_WAIT_DELAY = 180
SERVER_WAIT_CYCLES = 0  # 0 = keep retrying every SERVER_WAIT_DELAY seconds until the server recovers.
TRANSIENT_STATUS_CODES = {500, 502, 503, 504, 520, 522, 524}
UI_WIDTH = 62

os.makedirs(SESSION_DIR, exist_ok=True)

# Key gate removed: the bot starts without requiring external pass links or keys.

ACCOUNTS_STATUS = {}


def clear_screen():
    sys.stdout.write("\033[2J\033[H")


def strip_ansi(value):
    return re.sub(r"\033\[[0-9;]*m", "", value)


def fit_text(value, width):
    value = str(value)
    plain = strip_ansi(value)
    if len(plain) <= width:
        return value + " " * (width - len(plain))
    return plain[: max(0, width - 1)] + "…"


def box_line(left="╠", fill="═", right="╣"):
    return f"{C}{left}{fill * UI_WIDTH}{right}{RESET}"


def print_box_row(text="", color=W):
    print(f"{C}║{RESET}{color}{fit_text(text, UI_WIDTH)}{RESET}{C}║{RESET}")


def rgb_color(red, green, blue):
    return f"\033[38;2;{red};{green};{blue}m"


def progress_bar(percent, length=14):
    percent = max(0, min(100, int(percent or 0)))
    filled = int(length * percent / 100)
    bar = ""
    for i in range(length):
        if i < filled:
            red = int(255 * (1 - i / max(1, length)))
            green = int(255 * (i / max(1, length)))
            bar += f"{rgb_color(red, green, 90)}█"
        else:
            bar += f"{D}░"
    return f"{bar}{RESET} {Y}{percent:3}%{RESET}"


def spinner(tick):
    return ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"][tick % 10]


def short_payload(payload, limit=130):
    if isinstance(payload, dict):
        text = payload.get("message") or payload.get("error") or payload.get("raw") or str(payload)
    else:
        text = str(payload)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:limit] or "No response body"


def is_transient_status(status_code):
    return status_code in TRANSIENT_STATUS_CODES


def server_wait_exceeded(cycle):
    return SERVER_WAIT_CYCLES > 0 and cycle > SERVER_WAIT_CYCLES


def server_wait_label(cycle):
    if SERVER_WAIT_CYCLES > 0:
        return f"{cycle}/{SERVER_WAIT_CYCLES}"
    return f"{cycle}/∞"


def set_account_status(user, msg=None, percent=None, bal=None, detail=None):
    ACCOUNTS_STATUS.setdefault(
        user,
        {"msg": "Queued", "percent": 0, "bal": "0.00", "detail": "Waiting to start"},
    )
    if msg is not None:
        ACCOUNTS_STATUS[user]["msg"] = msg
    if percent is not None:
        ACCOUNTS_STATUS[user]["percent"] = percent
    if bal is not None:
        ACCOUNTS_STATUS[user]["bal"] = str(bal)
    if detail is not None:
        ACCOUNTS_STATUS[user]["detail"] = detail


def banner():
    print(box_line("╔", "═", "╗"))
    print_box_row("", M)
    print_box_row(f"{BOLD}        ███╗   ██╗██╗███╗   ██╗ ██████╗", M)
    print_box_row("        ████╗  ██║██║████╗  ██║██╔═══██╗", P)
    print_box_row("        ██╔██╗ ██║██║██╔██╗ ██║██║   ██║", M)
    print_box_row("        ██║╚██╗██║██║██║╚██╗██║██║   ██║", P)
    print_box_row("        ██║ ╚████║██║██║ ╚████║╚██████╔╝", M)
    print_box_row("        ╚═╝  ╚═══╝╚═╝╚═╝  ╚═══╝ ╚═════╝", P)
    print_box_row(f"{BOLD}                 C O I N  •  NİNOCOIN", C)
    print_box_row("", M)
    print(box_line())
    print_box_row("APP: NİNOCOIN • SOURCE: TheOpenEarn • KEY: OFF • VER: 1.1.3", G)
    print(box_line("╚", "═", "╝"))


def dashboard(tick=0, footer="Running"):
    clear_screen()
    banner()
    print(f"{C}╔{'═' * UI_WIDTH}╗{RESET}")
    print_box_row(f"{spinner(tick)} LIVE ACCOUNT CENTER  •  {datetime.now().strftime('%H:%M:%S')}  •  {footer}", Y)
    print(f"{C}╠{'═' * UI_WIDTH}╣{RESET}")
    header = f"{'ACCOUNT':<14} {'STATE':<12} {'PROGRESS':<21} {'BAL':>9}"
    print_box_row(header, W)
    print(f"{C}╟{'─' * UI_WIDTH}╢{RESET}")

    if not ACCOUNTS_STATUS:
        print_box_row("No session loaded yet. Add an account or place .session files in sessions/.", D)
    else:
        for user, data in ACCOUNTS_STATUS.items():
            progress = progress_bar(data.get("percent", 0))
            row = (
                f"{str(user)[:14]:<14} "
                f"{str(data.get('msg', ''))[:12]:<12} "
                f"{strip_ansi(progress):<21} "
                f"{str(data.get('bal', '0.00'))[:9]:>9}"
            )
            color = G
            if any(word in data.get("msg", "") for word in ["Fail", "Error", "Timeout", "Net", "Down"]):
                color = R
            elif data.get("msg") in ["Done", "Completed", "No Ads", "Tap Done", "Ads Done"]:
                color = C
            print_box_row(row, color)
            detail = data.get("detail")
            if detail:
                print_box_row(f"  └─ {detail}", D)

    print(f"{C}╚{'═' * UI_WIDTH}╝{RESET}")
    sys.stdout.flush()


async def dashboard_refresher(stop_event):
    tick = 0
    while not stop_event.is_set():
        dashboard(tick)
        tick += 1
        await asyncio.sleep(0.75)
    dashboard(tick, footer="Finished")


async def create_session():
    phone = input(f"{G}[?] Phone (+...): {W}").strip()
    sess_name = phone.replace("+", "")
    client = TelegramClient(os.path.join(SESSION_DIR, sess_name), API_ID, API_HASH)
    await client.start(phone=lambda: phone)
    print(f"{G}[✓] Account Linked Successfully!{RESET}")
    await client.disconnect()


async def get_init_data(session_path):
    client = TelegramClient(session_path, API_ID, API_HASH)
    await client.connect()
    try:
        bot = await client.get_input_entity(BOT_USER)
        webview = await client(
            functions.messages.RequestWebViewRequest(
                peer=bot,
                bot=bot,
                platform="android",
                from_bot_menu=False,
                url=URL_WEBVIEW,
            )
        )
        if "tgWebAppData=" not in webview.url:
            raise ValueError("WebView data not found")
        raw_data = webview.url.split("tgWebAppData=")[1].split("&tgWebAppVersion")[0]
        return urllib.parse.unquote(raw_data)
    finally:
        await client.disconnect()


class OpenEarnEngine:
    def __init__(self, query_id, sess_name):
        self.session = requests.Session()
        self.headers = {
            "Authorization": f"tma {query_id}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0",
        }
        self.username = sess_name
        self.user_id = "0"
        self.failed = False
        try:
            user_match = re.search(r"user=([^&]+)", query_id)
            if user_match:
                self.user_info = json.loads(urllib.parse.unquote(user_match.group(1)))
                self.username = self.user_info.get("username") or sess_name
                self.user_id = str(self.user_info.get("id") or "0")
        except Exception:
            pass

        set_account_status(self.username, "Starting", 8, "0.00", "Session connected")

    def update_status(self, msg=None, percent=None, bal=None, detail=None):
        if msg and any(word in msg for word in ["Error", "Fail", "Timeout", "Net", "Down"]):
            self.failed = True
        set_account_status(self.username, msg, percent, bal, detail)

    def _request_json_sync(self, method, url, **kwargs):
        kwargs.setdefault("timeout", REQUEST_TIMEOUT)
        response = self.session.request(method, url, **kwargs)
        try:
            payload = response.json()
        except ValueError:
            payload = {"raw": response.text[:300]}
        return response.status_code, payload

    async def request_json(self, method, url, label="API", retry=True, **kwargs):
        attempts = RETRY_ATTEMPTS if retry else 1
        last_status = None
        last_payload = {}
        for attempt in range(1, attempts + 1):
            try:
                status_code, payload = await asyncio.to_thread(self._request_json_sync, method, url, **kwargs)
            except requests.RequestException as exc:
                last_status = 0
                last_payload = {"error": str(exc)}
                if attempt >= attempts:
                    raise
                delay = RETRY_BASE_DELAY * attempt
                self.update_status(
                    "Retrying",
                    min(95, 15 + attempt * 12),
                    detail=f"{label}: network issue, retry {attempt}/{attempts} in {delay}s",
                )
                await asyncio.sleep(delay)
                continue

            last_status, last_payload = status_code, payload
            if not retry or not is_transient_status(status_code) or attempt >= attempts:
                return status_code, payload

            delay = RETRY_BASE_DELAY * attempt
            self.update_status(
                "Server Busy",
                min(95, 15 + attempt * 12),
                detail=f"{label}: server {status_code}, retry {attempt}/{attempts} in {delay}s",
            )
            await asyncio.sleep(delay)

        return last_status, last_payload

    async def wait_for_server(self, label, status_code, payload, cycle):
        self.update_status(
            "Server Wait",
            95,
            detail=f"{label}: server {status_code}. 5/5 done; retrying in {SERVER_WAIT_DELAY // 60} min ({server_wait_label(cycle)})",
        )
        await asyncio.sleep(SERVER_WAIT_DELAY)

    async def wait_linear(self, duration, msg, detail=None):
        self.update_status(msg=msg, detail=detail)
        for percent in range(1, 101):
            self.update_status(percent=percent)
            await asyncio.sleep(duration / 100)

    async def run_ads(self):
        self.update_status("Ads Check", 10, detail="Daily ad status is being checked")
        server_cycles = 0
        while True:
            try:
                status_code, user_data = await self.request_json("GET", f"{BASE_URL}/user", label="Balance", headers=self.headers)
                if is_transient_status(status_code):
                    server_cycles += 1
                    if server_wait_exceeded(server_cycles):
                        self.update_status("Server Down", 100, detail=f"Balance still returns {status_code}: {short_payload(user_data)}")
                        break
                    await self.wait_for_server("Balance", status_code, user_data, server_cycles)
                    continue
                if status_code >= 400:
                    self.update_status("HTTP Error", 100, detail=f"/user returned {status_code}: {short_payload(user_data)}")
                    break
                self.update_status(bal=user_data.get("balance", "0"))

                status_code, status = await self.request_json("GET", f"{BASE_URL}/ads/daily-status", label="Ads status", headers=self.headers)
                if is_transient_status(status_code):
                    server_cycles += 1
                    if server_wait_exceeded(server_cycles):
                        self.update_status("Server Down", 100, detail=f"Ads status still returns {status_code}: {short_payload(status)}")
                        break
                    await self.wait_for_server("Ads status", status_code, status, server_cycles)
                    continue
                if status_code >= 400:
                    self.update_status("Ads Error", 100, detail=f"daily-status returned {status_code}: {short_payload(status)}")
                    break

                server_cycles = 0
                if status.get("remaining", 0) == 0:
                    self.update_status("Ads Done", 100, detail="No remaining ads for today")
                    break

                providers = status.get("providers") or {}
                active = next(
                    (
                        (name, info)
                        for name, info in providers.items()
                        if info.get("remaining", 0) > 0 and not info.get("blocked", False)
                    ),
                    None,
                )
                if not active:
                    self.update_status("No Ads", 100, detail="No active ad provider is available")
                    break

                name, _info = active
                wait = 15
                if name == "adsgram":
                    wait = 30
                elif name == "monetag":
                    wait = 38
                elif name in ["richads", "onclicka"]:
                    wait = 120

                await self.wait_linear(wait, f"Ad: {name[:8]}", f"Watching {name} for {wait} seconds")

                if name == "monetag":
                    oaid = uuid.uuid4().hex
                    monetag_url = (
                        f"https://e8ys.com/500/10719545?oaid={oaid}"
                        f"&tgp=ios&sdkp=1&var_3={self.user_id}&sw_version=v1.801.0"
                    )
                    status_code, monetag = await self.request_json("GET", monetag_url, label="Monetag", headers=self.headers)
                    if status_code < 400 and monetag.get("ruid"):
                        await self.request_json("GET", f"https://e8ys.com/resolve?ruid={monetag['ruid']}", headers=self.headers)

                status_code, result = await self.request_json(
                    "POST",
                    f"{BASE_URL}/ads/complete",
                    label="Ad complete",
                    json={"ad_type": "video", "provider": name, "watched": True},
                    headers=self.headers,
                )
                if is_transient_status(status_code):
                    server_cycles += 1
                    if server_wait_exceeded(server_cycles):
                        self.update_status("Server Down", 100, detail=f"Ad complete still returns {status_code}: {short_payload(result)}")
                        break
                    await self.wait_for_server("Ad complete", status_code, result, server_cycles)
                    continue
                if status_code >= 400:
                    self.update_status("Ad Error", 100, detail=f"complete returned {status_code}: {short_payload(result)}")
                    break
                if result.get("success"):
                    self.update_status("Ad Success", 100, result.get("new_balance"), f"{name} completed")
                    if name == "adsgram":
                        await self.wait_linear(60, "Cooldown", "Adsgram cooldown")
                else:
                    self.update_status("Ad Failed", 100, detail=str(result)[:160])
                    break
            except requests.RequestException as exc:
                self.update_status("Net Error", 100, detail=str(exc)[:160])
                break
            except Exception as exc:
                self.update_status("Ads Error", 100, detail=str(exc)[:160])
                break

    async def run_tapper(self):
        self.update_status("Tapping", 0, detail="Tap cycle started")
        server_cycles = 0
        while True:
            try:
                status_code, data = await self.request_json(
                    "POST",
                    f"{BASE_URL}/earn",
                    label="Tap",
                    headers=self.headers,
                    json={"taps": 1},
                )
                if status_code == 429:
                    self.update_status("Rate Limit", 25, detail="Waiting 65 seconds")
                    await asyncio.sleep(65)
                    continue
                if is_transient_status(status_code):
                    server_cycles += 1
                    if server_wait_exceeded(server_cycles):
                        self.update_status("Server Down", 100, detail=f"Tap still returns {status_code}: {short_payload(data)}")
                        break
                    await self.wait_for_server("Tap", status_code, data, server_cycles)
                    continue
                if status_code >= 400:
                    self.update_status("Tap Error", 100, detail=f"earn returned {status_code}: {short_payload(data)}")
                    break

                server_cycles = 0
                if data.get("balance"):
                    self.update_status(bal=data["balance"])
                if data.get("cycle_complete") or data.get("cooldown_until"):
                    self.update_status("Tap Done", 100, detail="Tap cycle completed or cooldown started")
                    break

                self.update_status("Tapping", random.randint(20, 85), detail="Sending safe tap interval")
                await asyncio.sleep(random.uniform(2.1, 3.5))
            except requests.RequestException as exc:
                self.update_status("Net Error", 100, detail=str(exc)[:160])
                break
            except Exception as exc:
                self.update_status("Tap Error", 100, detail=str(exc)[:160])
                break

    async def run_spin(self):
        self.update_status("Spinning", 10, detail="Trying daily wheel spin")
        server_cycles = 0
        while True:
            try:
                status_code, result = await self.request_json(
                    "POST",
                    f"{BASE_URL}/wheel/spin",
                    label="Wheel",
                    headers=self.headers,
                    json={"is_paid": False},
                )
                if is_transient_status(status_code):
                    server_cycles += 1
                    if server_wait_exceeded(server_cycles):
                        self.update_status("Server Down", 100, detail=f"Wheel still returns {status_code}: {short_payload(result)}")
                        return
                    await self.wait_for_server("Wheel", status_code, result, server_cycles)
                    continue
                if status_code >= 400:
                    self.update_status("Spin Error", 100, detail=f"wheel returned {status_code}: {short_payload(result)}")
                    return
                if result.get("success"):
                    _status_code, user_data = await self.request_json("GET", f"{BASE_URL}/user", label="Balance", headers=self.headers)
                    self.update_status("Spin Done", 100, user_data.get("balance"), "Wheel spin completed")
                else:
                    self.update_status("Spin Skip", 100, detail=str(result)[:160])
                return
            except requests.RequestException as exc:
                self.update_status("Net Error", 100, detail=str(exc)[:160])
                return
            except Exception as exc:
                self.update_status("Spin Error", 100, detail=str(exc)[:160])
                return


async def start_account(sess_path, sess_name, mode):
    set_account_status(sess_name, "Telegram", 3, "0.00", "Opening Telegram webview")
    try:
        init_data = await asyncio.wait_for(get_init_data(sess_path), timeout=INIT_TIMEOUT)
    except asyncio.TimeoutError:
        set_account_status(sess_name, "Timeout", 100, detail=f"Telegram init exceeded {INIT_TIMEOUT} seconds")
        return
    except Exception as exc:
        set_account_status(sess_name, "Login Fail", 100, detail=str(exc)[:160])
        return

    if not init_data:
        set_account_status(sess_name, "Login Fail", 100, detail="Empty Telegram init data")
        return

    bot = OpenEarnEngine(init_data, sess_name)
    if bot.username != sess_name:
        ACCOUNTS_STATUS.pop(sess_name, None)
    if mode in ["1", "2"]:
        await bot.run_ads()
    if mode in ["1", "3"]:
        await bot.run_spin()
        await bot.run_tapper()
    if not bot.failed:
        bot.update_status("Completed", 100, detail="Selected tasks finished")


async def main():
    clear_screen()
    banner()
    print(f"{G}[✓] NİNOCOIN key kontrolü kaldırıldı. Bot doğrudan başlıyor.{RESET}")

    while True:
        answer = input(f"{G}[?] Add more Telegram accounts? (y/n): {W}").strip().lower()
        if answer == "y":
            await create_session()
        else:
            break

    print(f"\n{Y}[1] Full Mode  |  [2] Ads Only  |  [3] Tap Only{RESET}")
    mode = input(f"{G}[?] Choice: {W}").strip()
    if mode not in {"1", "2", "3"}:
        print(f"{R}[!] Invalid choice. Full Mode selected by default.{RESET}")
        mode = "1"

    sessions = [file for file in os.listdir(SESSION_DIR) if file.endswith(".session")]
    if not sessions:
        print(f"{R}[!] No .session files found in {SESSION_DIR}.{RESET}")
        return

    for sess_file in sessions:
        set_account_status(sess_file.replace(".session", ""), "Queued", 0, "0.00", "Waiting in task queue")

    stop_event = asyncio.Event()
    dashboard_task = asyncio.create_task(dashboard_refresher(stop_event))
    tasks = []
    for sess_file in sessions:
        session_name = sess_file.replace(".session", "")
        session_path = os.path.join(SESSION_DIR, session_name)
        tasks.append(start_account(session_path, session_name, mode))

    await asyncio.gather(*tasks)
    stop_event.set()
    await dashboard_task
    print(f"\n{G}[★] ALL PROCESSES FINISHED. Check the status table above for account results.{RESET}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit()
