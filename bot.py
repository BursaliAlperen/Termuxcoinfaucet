
import requests
import time
import os
import sys
import json
import random
import asyncio
import urllib.parse
import uuid
import re
from datetime import datetime
from telethon import TelegramClient, functions

# --- NEON COLORS ---
G = "\033[38;5;82m" ; B = "\033[38;5;27m" ; C = "\033[38;5;51m"
Y = "\033[38;5;226m" ; R = "\033[38;5;196m" ; M = "\033[38;5;201m"
W = "\033[38;5;255m" ; BOLD = "\033[1m" ; RESET = "\033[0m"

# --- CONFIG ---
API_ID = 28752231
API_HASH = 'ec1c1f2c30e2f1855c3edee7e348480b'
BOT_USER = "TheOpenEarnAppBot"
URL_WEBVIEW = "https://app.theopenearn.com/"
BASE_URL = "https://app.theopenearn.com/api"
SESSION_DIR = "sessions"

if not os.path.exists(SESSION_DIR): os.makedirs(SESSION_DIR)

# Key gate removed: the bot starts without requiring external pass links or keys.

# Global State for Dashboard
ACCOUNTS_STATUS = {}

def rgb_color(r, g, b): return f"\033[38;2;{r};{g};{b}m"

def get_rainbow_bar(percent, length=12):
    bar = ""
    filled = int(length * percent / 100)
    for i in range(length):
        r, g = int(255 * (1 - i/length)), int(255 * i/length)
        color = rgb_color(r, g, 50)
        bar += f"{color}▰" if i < filled else f"\033[38;2;60;60;60m▱"
    return bar + RESET

def get_pulse_bar(tick, length=12):
    pos = tick % length
    bar = ""
    for i in range(length):
        if i == pos: bar += f"{G}▰"
        else: bar += f"\033[38;2;60;60;60m▱"
    return bar + RESET

def banner():
    print(f"{C}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
    print(f"{M}{BOLD}  ███╗   ██╗██╗███╗   ██╗ ██████╗  ██████╗ ██████╗ ██╗███╗   ██╗")
    print(f" ████╗  ██║██║████╗  ██║██╔═══██╗██╔════╝██╔═══██╗██║████╗  ██║")
    print(f" ██╔██╗ ██║██║██╔██╗ ██║██║   ██║██║     ██║   ██║██║██╔██╗ ██║")
    print(f" ██║╚██╗██║██║██║╚██╗██║██║   ██║██║     ██║   ██║██║██║╚██╗██║")
    print(f" ██║ ╚████║██║██║ ╚████║╚██████╔╝╚██████╗╚██████╔╝██║██║ ╚████║")
    print(f" ╚═╝  ╚═══╝╚═╝╚═╝  ╚═══╝ ╚═════╝  ╚═════╝ ╚═════╝ ╚═╝╚═╝  ╚═══╝")
    print(f"{C}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
    print(f"{G}{BOLD}    APP  :- {W}NİNOCOIN       {C}| {G}SC :- {W}TheOpenEarn")
    print(f"{G}{BOLD}    KEY  :- {W}Disabled       {C}| {G}VER:- {W}1.1.0 ")
    print(f"{C}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")

async def dashboard_refresher():
    while True:
        sys.stdout.write("\033[H") # Move cursor to top
        banner()
        print(f"{Y}[ LIVE MULTI-ACCOUNT MONITOR ]{RESET}")
        print(f"{M}─────────────────────────────────────────────────────────────{RESET}")
        print(f"{'USERNAME':<15} | {'STATUS':<12} | {'PROGRESS':<15} | {'BAL'}")
        print(f"{M}─────────────────────────────────────────────────────────────{RESET}")
        
        for user, data in ACCOUNTS_STATUS.items():
            if "Tap" in data['msg']:
                bar = get_pulse_bar(int(time.time()*3))
                prog_str = "TAPPING"
            else:
                bar = get_rainbow_bar(data['percent'])
                prog_str = f"{data['percent']:3}%"

            print(f"{G}{user[:15]:<15} {RESET}| {C}{data['msg'][:12]:<12} {RESET}| {bar} {Y}{prog_str} {RESET}| {G}{data['bal']}")
        
        print(f"{M}─────────────────────────────────────────────────────────────{RESET}")
        print(f"{W} Time: {datetime.now().strftime('%H:%M:%S')} | Total Sessions: {len(ACCOUNTS_STATUS)}")
        sys.stdout.flush()
        await asyncio.sleep(0.5)

async def create_session():
    phone = input(f"{G}[?] Phone (+...): {W}").strip()
    sess_name = phone.replace('+', '')
    client = TelegramClient(os.path.join(SESSION_DIR, sess_name), API_ID, API_HASH)
    await client.start(phone=lambda: phone)
    print(f"{G}[✓] Account Linked Successfully!{RESET}")
    await client.disconnect()

async def get_init_data(session_path):
    client = TelegramClient(session_path, API_ID, API_HASH)
    await client.connect()
    try:
        bot = await client.get_input_entity(BOT_USER)
        wv = await client(functions.messages.RequestWebViewRequest(
            peer=bot, bot=bot, platform='android', from_bot_menu=False, url=URL_WEBVIEW
        ))
        raw_data = wv.url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0]
        return urllib.parse.unquote(raw_data)
    except Exception:
        return None
    finally:
        await client.disconnect()

class OpenEarnEngine:
    def __init__(self, query_id, sess_name):
        self.session = requests.Session()
        self.headers = {'Authorization': f"tma {query_id}", 'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
        try:
            u_raw = re.search(r'user=([^&]+)', query_id).group(1)
            self.user_info = json.loads(urllib.parse.unquote(u_raw))
            self.username = self.user_info.get('username', sess_name)
            self.user_id = str(self.user_info.get('id'))
        except Exception:
            self.username = sess_name
            self.user_id = "0"
        
        ACCOUNTS_STATUS[self.username] = {'msg': 'Starting...', 'percent': 0, 'bal': '0.00'}

    def update_status(self, msg=None, percent=None, bal=None):
        if msg: ACCOUNTS_STATUS[self.username]['msg'] = msg
        if percent is not None: ACCOUNTS_STATUS[self.username]['percent'] = percent
        if bal is not None: ACCOUNTS_STATUS[self.username]['bal'] = str(bal)

    async def wait_linear(self, duration, msg):
        self.update_status(msg=msg)
        for i in range(1, 101):
            self.update_status(percent=i)
            await asyncio.sleep(duration / 100)

    async def run_ads(self):
        while True:
            try:
                # Refresh Balance
                u_res = self.session.get(f"{BASE_URL}/user", headers=self.headers).json()
                self.update_status(bal=u_res.get('balance', '0'))

                status = self.session.get(f"{BASE_URL}/ads/daily-status", headers=self.headers).json()
                if status.get('remaining', 0) == 0:
                    self.update_status(msg="Ads Done", percent=100); break
                
                providers = status.get('providers', {})
                active = next(
                    (
                        (k, v)
                        for k, v in providers.items()
                        if v.get('remaining', 0) > 0 and not v.get('blocked', False)
                    ),
                    None,
                )
                if not active: break
                
                name, info = active
                wait = 15
                if name == "adsgram": wait = 30
                elif name == "monetag": wait = 38
                elif name in ["richads", "onclicka"]: wait = 120
                
                await self.wait_linear(wait, f"Ad: {name[:7]}")
                
                if name == "monetag":
                    oaid = uuid.uuid4().hex
                    m_url = f"https://e8ys.com/500/10719545?oaid={oaid}&tgp=ios&sdkp=1&var_3={self.user_id}&sw_version=v1.801.0"
                    m_res = self.session.get(m_url, headers=self.headers).json()
                    if m_res.get('ruid'): self.session.get(f"https://e8ys.com/resolve?ruid={m_res['ruid']}", headers=self.headers)

                res = self.session.post(f"{BASE_URL}/ads/complete", json={"ad_type": "video", "provider": name, "watched": True}, headers=self.headers).json()
                if res.get('success'):
                    self.update_status(msg="Success!", bal=res['new_balance'])
                    if name == "adsgram": await self.wait_linear(60, "Adsgram CD")
            except Exception:
                break

    async def run_tapper(self):
        self.update_status(msg="Tapping...")
        while True:
            try:
                res = self.session.post(f"{BASE_URL}/earn", headers=self.headers, json={"taps": 1})
                if res.status_code == 429:
                    self.update_status(msg="Rate Limit")
                    await asyncio.sleep(65); continue
                
                data = res.json()
                if data.get('balance'): self.update_status(bal=data['balance'])
                if data.get('cycle_complete') or data.get('cooldown_until'):
                    self.update_status(msg="Tap Done", percent=100); break
                
                await asyncio.sleep(random.uniform(2.1, 3.5))
            except Exception:
                break

    async def run_spin(self):
        self.update_status(msg="Spinning...")
        try:
            res = self.session.post(f"{BASE_URL}/wheel/spin", headers=self.headers, json={"is_paid": False}).json()
            if res.get('success'):
                u_res = self.session.get(f"{BASE_URL}/user", headers=self.headers).json()
                self.update_status(bal=u_res.get('balance'))
        except Exception:
            pass

async def start_account(sess_path, sess_name, mode):
    init_data = await get_init_data(sess_path)
    if init_data:
        bot = OpenEarnEngine(init_data, sess_name)
        if mode in ['1', '2']: await bot.run_ads()
        if mode in ['1', '3']: 
            await bot.run_spin()
            await bot.run_tapper()

async def main():
    os.system('clear' if os.name == 'posix' else 'cls')
    banner()
    print(f"{G}[✓] NİNOCOIN key kontrolü devre dışı. Bot doğrudan başlatılıyor.{RESET}")

    while True:
        if input(f"{G}[?] Add more Telegram accounts? (y/n): {W}").lower() == 'y':
            await create_session()
        else: break

    print(f"\n{Y}[1] Full Mode | [2] Ads Only | [3] Tap Only")
    mode = input(f"{G}[?] Choice: {W}").strip()
    if mode not in {'1', '2', '3'}:
        print(f"{R}[!] Invalid choice. Full Mode selected by default.{RESET}")
        mode = '1'

    sessions = [f for f in os.listdir(SESSION_DIR) if f.endswith('.session')]
    if not sessions: return

    # Dashboard display clear
    os.system('clear' if os.name == 'posix' else 'cls')
    asyncio.create_task(dashboard_refresher())

    tasks = []
    for sess_file in sessions:
        path = os.path.join(SESSION_DIR, sess_file.replace('.session', ''))
        tasks.append(start_account(path, sess_file.replace('.session', ''), mode))

    await asyncio.gather(*tasks)
    print(f"\n{G}[★] ALL PROCESSES FINISHED SUCCESSFULLY!{RESET}")
    while True: await asyncio.sleep(10)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit()
