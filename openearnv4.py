import os
import time
import json
import uuid
import re
import urllib.parse
import random
import base64
import requests
from datetime import datetime, timezone

# Telethon Imports
try:
    from telethon.sync import TelegramClient
    from telethon import functions
except ImportError:
    print("❌ Telethon not found. Install it using: pip install telethon")
    exit()

BOT_USERNAME = 'TheOpenEarnAppBot'
ACCOUNTS_FILE = 'configopenearn.json'


def print_banner():
    # ANSI Color Codes
    c = "\033[96m"  # Cyan
    y = "\033[93m"  # Yellow
    b = "\033[1m"   # Bold
    g = "\033[92m"  # Green
    x = "\033[0m"   # Reset

    os.system('cls' if os.name == 'nt' else 'clear')

    banner = f"""
    {c}╔══════════════════════════════════════════════════════════════════╗
    ║ {y}    ██╗      ██████╗ ███╗   ██╗███████╗██╗  ██╗ {c}            ║
    ║ {y}    ██║     ██╔═══██╗████╗  ██║██╔════╝╚██╗██╔╝ {c}           ║
    ║ {y}    ██║     ██║   ██║██╔██╗ ██║█████╗   ╚███╔╝  {c}           ║
    ║ {y}    ██║     ██║   ██║██║╚██╗██║██╔══╝   ██╔██╗  {c}           ║
    ║ {y}    ███████╗╚██████╔╝██║ ╚████║███████╗██╔╝ ██╗ {c}           ║
    ║ {c}             >>> {b}LONEX V4 - AUTOMATION{c} <<<             ║
    ╠══════════════════════════════════════════════════════════════════╣
    ║ {g}  Shortlink verification tasks removed.{c}                      ║
    ╚══════════════════════════════════════════════════════════════════╝{x}
    """
    print(banner)


class OpenEarnEngine:
    def __init__(self, query_id):
        self.query_id = query_id
        self.auth_token = f"tma {query_id}"
        self.session = requests.Session()
        self.start_balance = 0.0

        params = dict(urllib.parse.parse_qsl(query_id))

        try:
            u_raw = re.search(r'user=([^&]+)', query_id).group(1)
            u_dec = urllib.parse.unquote(u_raw)
            user_json = json.loads(u_dec)
            self.user_id = str(user_json.get('id', '7330965002'))
            raw_data = (
                f"auth_date={params.get('auth_date')}\n"
                f"query_id={params.get('query_id')}\n"
                f"user={u_dec}"
            )
            self.adsgram_data_check = base64.b64encode(raw_data.encode()).decode()
        except Exception:
            self.user_id = "7330965002"
            self.adsgram_data_check = ""

        self.headers = {
            'User-Agent': (
                'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) '
                'AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 '
                'Telegram-iOS/10.9.1'
            ),
            'Accept': 'application/json, text/plain, */*',
            'Authorization': self.auth_token,
            'Origin': 'https://app.theopenearn.com',
            'Referer': 'https://app.theopenearn.com/',
            'Content-Type': 'application/json'
        }

    def safe_req(self, method, url, **kwargs):
        while True:
            try:
                return self.session.request(method, url, timeout=15, **kwargs)
            except Exception:
                print("\r⚠️ Network Error! Retrying... ", end="", flush=True)
                time.sleep(10)

    def run_tapper(self):
        print("\n" + "👆" * 15 + " STARTING AUTO-TAP MODULE " + "👆" * 15)
        url = "https://app.theopenearn.com/api/earn"
        while True:
            res = self.safe_req("POST", url, headers=self.headers, json={"taps": 1})
            if res.status_code == 429:
                print("⚠️ Rate limit hit! Sleeping 65s to reset...")
                time.sleep(65)
                continue
            if res.status_code != 200:
                print(f"❌ Tap session interrupted (Status {res.status_code})")
                break
            data = res.json()
            if data.get('cycle_complete') or data.get('cooldown_until'):
                print("\n✅ TAP CYCLE COMPLETE!")
                break
            time.sleep(random.uniform(2.1, 3.5))

    def print_status_table(self, user, status):
        print("\n" + "=" * 65)
        bal = float(user.get('balance', 0))
        print(
            f"👤 {user.get('username')} | 💰 Bal: {bal} | "
            f"Session Profit: +{round(bal - self.start_balance, 5)}"
        )
        print("-" * 65)
        print(f"{'PROVIDER':<15} | {'LIMIT':<7} | {'USED':<7} | {'LEFT':<7} | {'STATUS'}")
        for p in ["adsgram", "monetag", "richads", "onclicka"]:
            data = status.get('providers', {}).get(p, {})
            used, limit = data.get('used', 0), data.get('limit', 0)
            rem = max(0, limit - used)
            mark = "[DONE]" if rem <= 0 else "[READY]"
            print(f"{p.capitalize():<15} | {limit:<7} | {used:<7} | {rem:<7} | {mark}")
        print("=" * 65 + "\n")

    def run_monetag(self):
        oaid = uuid.uuid4().hex
        manifest_url = (
            f"https://e8ys.com/500/10719545?oaid={oaid}&tgp=ios&sdkp=1"
            f"&var_3={self.user_id}&sw_version=v1.801.0"
        )
        res = self.safe_req("GET", manifest_url, headers=self.headers)
        if res.status_code != 200:
            return False
        data = res.json()
        ruid = data.get('ruid', None)
        ads = data.get('ads', [])
        if not ruid or not ads:
            return False
        imp_url = ads[0].get('impression_url')
        if imp_url:
            self.safe_req("GET", imp_url, headers=self.headers)
        print("[*] Watching MONETAG (38s)...")
        time.sleep(38)
        resolve_res = self.safe_req("GET", f"https://e8ys.com/resolve?ruid={ruid}", headers=self.headers)
        if resolve_res.status_code == 200:
            self.safe_req(
                "POST",
                "https://app.theopenearn.com/api/ads/complete",
                headers=self.headers,
                json={"ad_type": "video", "provider": "monetag", "watched": True},
            )
            return True
        return False

    def start_cycle(self):
        providers_to_run = ["monetag", "richads", "onclicka", "adsgram"]
        failed_providers = set()

        while True:
            u_resp = self.safe_req("GET", "https://app.theopenearn.com/api/user", headers=self.headers).json()
            s_resp = self.safe_req("GET", "https://app.theopenearn.com/api/ads/daily-status", headers=self.headers).json()
            if self.start_balance == 0.0:
                self.start_balance = float(u_resp.get('balance', 0))
            self.print_status_table(u_resp, s_resp)

            all_possible_ads_done = True
            for p in providers_to_run:
                if p in failed_providers:
                    continue
                data = s_resp['providers'].get(p, {})
                if data.get('used', 0) < data.get('limit', 0):
                    all_possible_ads_done = False
                    success = False
                    try:
                        if p == "monetag":
                            success = self.run_monetag()
                        elif p == "adsgram":
                            print("[*] Watching ADSGRAM (30s)...")
                            time.sleep(30)
                            res = self.safe_req(
                                "POST",
                                "https://app.theopenearn.com/api/ads/complete",
                                headers=self.headers,
                                json={"ad_type": "video", "provider": "adsgram", "watched": True},
                            )
                            success = (res.status_code == 200)
                            print("[*] Cooling down for 60s...")
                            time.sleep(60)
                        else:
                            wait = 120 if p in ["richads", "onclicka"] else 15
                            print(f"[*] Watching {p.upper()} ({wait}s)...")
                            time.sleep(wait)
                            res = self.safe_req(
                                "POST",
                                "https://app.theopenearn.com/api/ads/complete",
                                headers=self.headers,
                                json={"ad_type": "video", "provider": p, "watched": True},
                            )
                            success = (res.status_code == 200)

                        if success:
                            failed_providers.discard(p)
                            break
                        failed_providers.add(p)
                    except Exception:
                        failed_providers.add(p)

            rem_ads = [
                p for p in providers_to_run
                if s_resp['providers'].get(p, {}).get('used', 0) < s_resp['providers'].get(p, {}).get('limit', 0)
            ]
            if all_possible_ads_done or len(failed_providers) >= len(rem_ads):
                print("🏁 AD PHASE COMPLETE. SWITCHING TO TAPPER.")
                self.run_tapper()
                self.safe_req(
                    "POST",
                    "https://app.theopenearn.com/api/wheel/spin",
                    headers=self.headers,
                    json={"is_paid": False},
                )
                print("\n♻️ CYCLE FINISHED. RESTARTING MAIN LOOP...")
                time.sleep(10)
                return


if __name__ == "__main__":
    print_banner()

    # Check if config file exists, if not, ask the user to input data
    if not os.path.exists(ACCOUNTS_FILE):
        print("⚠️ 'configopenearn.json' not found. Let's create it.")
        phone = input("Enter phone number (include country code, e.g., +91...): ")
        api_id = input("Enter API ID: ")
        api_hash = input("Enter API Hash: ")
        accs = [{"phone": phone, "api_id": api_id, "api_hash": api_hash}]
        with open(ACCOUNTS_FILE, 'w') as f:
            json.dump(accs, f, indent=4)
        print("✅ Configuration saved to 'configopenearn.json'.")
    else:
        with open(ACCOUNTS_FILE, 'r') as f:
            accs = json.load(f)

    # Taking the first account for single account run
    acc = accs[0]

    while True:
        client = TelegramClient(
            f"session_{acc['phone'].replace('+', '')}",
            acc['api_id'],
            acc['api_hash']
        )
        try:
            client.start()
            bot = client.get_input_entity(BOT_USERNAME)
            res = client(
                functions.messages.RequestWebViewRequest(
                    peer=bot,
                    bot=bot,
                    platform='android',
                    url='https://app.theopenearn.com/'
                )
            )
            query = urllib.parse.unquote(
                res.url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0]
            )
            client.disconnect()

            engine = OpenEarnEngine(query)
            engine.start_cycle()
        except Exception as e:
            print(f"❌ Main Loop Error: {e}")
            time.sleep(60)
