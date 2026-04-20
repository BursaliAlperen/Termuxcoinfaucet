
import requests
import time
import re
import os
import json
import sys
import random
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

# --- [ PRO COLORS ] ---
G, R, Y, C, W, M, B = '\033[1;32m', '\033[1;31m', '\033[1;33m', '\033[1;36m', '\033[0m', '\033[1;35m', '\033[1;34m'

CONFIG_FILE = "config.json"
SOLVER_URL = "http://157.180.15.203"
SITE_KEY = "6LfwaSgTAAAAAJJNz6oAdimVHmIe3s4fHj4D0at4"

# --- 🔑 KEY SYSTEM DATABASE ---
KEY_SYSTEM = [
    {"link": "https://bit.ly/4rVKoyd", "key": "C4COIN-CHANNEL-BRO"},
    {"link": "https://bit.ly/4s6DMxk", "key": "C4COIN1"},
    {"link": "https://bit.ly/3NhNJZk", "key": "C4COIN-SMART"},
    {"link": "https://bit.ly/4rXKiWO", "key": "C4COIN-CRAZY"},
    {"link": "https://bit.ly/47AE0nU", "key": "C4coin-Earn"},
    {"link": "https://bit.ly/4bw1qNI", "key": "C4COIN-C4COIN"},
    {"link": "https://bit.ly/4lfWlMF", "key": "C4COIN-RUSH"},
    {"link": "https://bit.ly/4lrbOtC", "key": "SMART-C4COIN"}
]

COINS_FREE = ["bitcoin", "ethereum", "tether", "bnb", "solana", "usdc", "ripple", "dogecoin", "tron", "toncoin", "bch", "cardano", "litecoin", "polygon", "monero", "stellar", "zcash", "dash", "digibyte", "feyorra"]
COINS_BEE = ["eth", "usdt", "bnb", "sol", "usdc", "xrp", "doge", "trx", "ton", "bch", "ada", "ltc", "matic", "xmr", "xlm", "zec", "dash", "dgb", "fey", "btcb"]

def clear(): os.system('clear' if os.name == 'posix' else 'cls')

def slow_type(text, speed=0.002):
    for char in text:
        sys.stdout.write(char); sys.stdout.flush(); time.sleep(speed)
    print()

def banner():
    clear()
    print(f"{C}────────────────────────────────────────────────────────{W}")
    print(f"{G}   _____  _  _    _____  ____  _____  _   _ ")
    print(f"  / ____|| || |  / ____|/ __ \|_   _|| \ | |")
    print(f" | |     | || |_| |    | |  | | | |  |  \| |")
    print(f" | |____ |__   _| |____| |__| |_| |_ | |\  |")
    print(f"  \_____|   |_|  \_____|\____/|_____||_| \_|")
    print(f"                                           ")
    print(f"{M}             X   V E N U J A N             ")
    print(f"{C}────────────────────────────────────────────────────────{W}")
    print(f"{G}      🚀  ULTIMATE CRYPTO PRINTING ENGINE v7.0  🚀      {W}")
    print(f"{C}────────────────────────────────────────────────────────{W}")
    print(f" {B}● ADMIN: {G}VENUJAN {B}● STATUS: {G}ONLINE {B}● TIME: {Y}{time.strftime('%H:%M:%S')}{W}")
    print(f"{C}────────────────────────────────────────────────────────{W}")

def verify_key():
    banner()
    # Randomly select a key from the database
    selected = random.choice(KEY_SYSTEM)
    print(f"{B}[!] {Y}VISIT THE LINK BELOW TO GET THE ACCESS KEY:")
    print(f"{C}➤ LINK: {G}{selected['link']}{W}\n")
    
    user_key = input(f"{B}[?] {W}ENTER ACCESS KEY: {W}").strip()
    
    if user_key == selected['key']:
        print(f"\n{G}✅ ACCESS GRANTED! INITIALIZING...{W}")
        time.sleep(2)
    else:
        print(f"\n{R}❌ INVALID KEY! TERMINATING SESSION...{W}")
        sys.exit()

def get_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f: return json.load(f)
    else:
        banner()
        print(f"{B}[?] {W}Configuring New User Details...")
        email = input(f"{C}➤ FaucetPay Email : {W}")
        api_key = input(f"{C}➤ xEvil API Key   : {W}")
        data = {"email": email, "api_key": api_key, "phpsessid": ""}
        with open(CONFIG_FILE, 'w') as f: json.dump(data, f)
        return data

def get_captcha_token(api_key, page_url):
    sys.stdout.write(f"\r{Y}[⚡] Captcha Engine {W}➤ {C}PENETRATING...   ")
    sys.stdout.flush()
    try:
        res = requests.get(f"{SOLVER_URL}/in.php?key={api_key}&method=userrecaptcha&pageurl={page_url}&sitekey={SITE_KEY}", timeout=15).text
        if "OK|" in res:
            cid = res.split('|')[1]
            while True:
                time.sleep(2)
                status = requests.get(f"{SOLVER_URL}/res.php?key={api_key}&action=get&id={cid}", timeout=15).text
                if "OK|" in status:
                    print(f"{G}[BYPASS SUCCESS]{W}"); return status.split('|')[1]
                if "ERROR" in status: return None
        return None
    except: return None

def claim_process(coin, email, token, site_type, sess_id=""):
    session = requests.Session()
    session.headers.update({'user-agent': 'Mozilla/5.0 (Linux; Android 10)'})
    url = f"https://claimfreecoins.io/{coin}-faucet/?r=arasarathinam3@gmail.com" if site_type == "free" else f"https://beefaucet.org/{coin}-faucet/?r=anilodhi2019@gmail.com"
    if site_type == "bee": session.cookies.update({'PHPSESSID': sess_id})

    try:
        res = session.get(url, timeout=10)
        s_token = re.search(r'name="session-token" value="(.*?)"', res.text)
        if s_token:
            payload = {'session-token': s_token.group(1), 'address': email, 'captcha': 'recaptcha', 'g-recaptcha-response': token, 'login': 'Verify Captcha'}
            post_res = session.post(url, data=payload, timeout=15)
            body = post_res.text.lower()
            if "satoshi was sent" in body:
                amt = re.search(r'(\d+) satoshi', body)
                val = amt.group(1) if amt else "?"
                return f"{G}CLAIM SUCCESSFUL {W}⚡ {Y}{val} Sat{W}"
            if "invalid captcha" in body: return f"{R}INVALID CAPTCHA{W}"
            if "cloudflare" in body: return f"{R}CLOUDFLARE BLOCK{W}"
        return f"{R}SYSTEM REJECTED{W}"
    except: return f"{R}ERROR{W}"

def start_bot():
    verify_key() # Verify Key System first
    config = get_config()
    cycle = 1
    while True:
        banner()
        print(f"{M}🌀 BATCH: #{cycle} STARTING...{W}\n")

        # --- SOURCE 1 ---
        token1 = get_captcha_token(config['api_key'], "https://claimfreecoins.io/tether-faucet/?r=arasarathinam3@gmail.com")
        if token1:
            print(f"\n{C}🌐 NETWORK: {Y}ClaimFreeCoins.io{W}")
            with ThreadPoolExecutor(max_workers=5) as ex:
                futures = {ex.submit(claim_process, c, config['email'], token1, "free"): c for c in COINS_FREE}
                for f in as_completed(futures):
                    coin = futures[f]
                    slow_type(f"  {W}➤ {coin.upper():<11} : {f.result()} {G}💸{W}")

        # Security Check
        print(f"\n{B}[🛡️] Firewall Scan: {W}Bypassing...", end="")
        s = requests.Session()
        try:
            r = s.get("https://beefaucet.org/usdt-faucet/?r=anilodhi2019@gmail.com", timeout=10)
            if "Cloudflare" in r.text:
                print(f"{R} [BLOCKED]{W}")
                if not config.get('phpsessid'): manual_id = input(f"{C}➤ Enter PHPSESSID: {W}"); config['phpsessid'] = manual_id
            else:
                print(f"{G} [CLEAR]{W}")
                aid = s.cookies.get_dict().get('PHPSESSID')
                if aid: config['phpsessid'] = aid
        except: pass

        # --- SOURCE 2 ---
        token2 = get_captcha_token(config['api_key'], "https://beefaucet.org/usdt-faucet/?r=anilodhi2019@gmail.com")
        if token2 and config['phpsessid']:
            print(f"\n{C}🐝 NETWORK: {Y}BeeFaucet.org{W}")
            with ThreadPoolExecutor(max_workers=5) as ex:
                futures = {ex.submit(claim_process, c, config['email'], token2, "bee", config['phpsessid']): c for c in COINS_BEE}
                for f in as_completed(futures):
                    coin = futures[f]
                    slow_type(f"  {W}➤ {coin.upper():<11} : {f.result()} {G}💰{W}")

        print(f"\n{G}✅ BATCH {cycle} PRINTING COMPLETED!{W}")
        for i in range(30, 0, -1):
            sys.stdout.write(f"\r{B}⏳ System Re-Energizing: {R}{i}s {W}until next print...")
            sys.stdout.flush(); time.sleep(1)
        cycle += 1

if __name__ == "__main__":
    try: start_bot()
    except KeyboardInterrupt: print(f"\n\n{R}🚨 SYSTEM STOPPED BY ADMIN.{W}"); sys.exit()
