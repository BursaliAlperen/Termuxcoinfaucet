
import requests
import time
import re
import os
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

# --- [ PRO COLORS ] ---
G, R, Y, C, W, M, B = '\033[1;32m', '\033[1;31m', '\033[1;33m', '\033[1;36m', '\033[0m', '\033[1;35m', '\033[1;34m'

CONFIG_FILE = "config.json"
SOLVER_URL = "http://157.180.15.203"
SITE_KEY = "6LfwaSgTAAAAAJJNz6oAdimVHmIe3s4fHj4D0at4"
FREE_MODE = "free"
PAID_MODE = "paid"

COINS_FREE = ["bitcoin", "ethereum", "tether", "bnb", "solana", "usdc", "ripple", "dogecoin", "tron", "toncoin", "bch", "cardano", "litecoin", "polygon", "monero", "stellar", "zcash", "dash", "digibyte", "feyorra"]
COINS_BEE = ["eth", "usdt", "bnb", "sol", "usdc", "xrp", "doge", "trx", "ton", "bch", "ada", "ltc", "matic", "xmr", "xlm", "zec", "dash", "dgb", "fey", "btcb"]
COINS_FREE_LIMITED = ["bitcoin", "tether", "dogecoin", "tron", "litecoin"]
COINS_BEE_LIMITED = ["usdt", "doge", "trx"]

def clear(): os.system('clear' if os.name == 'posix' else 'cls')

def default_headers():
    return {
        'user-agent': (
            'Mozilla/5.0 (Linux; Android 10; K) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/124.0.0.0 Mobile Safari/537.36'
        ),
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
    }

def slow_type(text, speed=0.002):
    for char in text:
        sys.stdout.write(char); sys.stdout.flush(); time.sleep(speed)
    print()

def banner(cycle=0, active_network="IDLE", email="N/A", mode=FREE_MODE):
    clear()
    line = f"{C}{'═' * 72}{W}"
    print(line)
    print(f"{G} ██████╗  ██████╗ ████████╗    ██╗      ██████╗ ███╗   ██╗███████╗██╗  ██╗{W}")
    print(f"{G} ██╔══██╗██╔═══██╗╚══██╔══╝    ██║     ██╔═══██╗████╗  ██║██╔════╝╚██╗██╔╝{W}")
    print(f"{G} ██████╔╝██║   ██║   ██║       ██║     ██║   ██║██╔██╗ ██║█████╗   ╚███╔╝ {W}")
    print(f"{G} ██╔══██╗██║   ██║   ██║       ██║     ██║   ██║██║╚██╗██║██╔══╝   ██╔██╗ {W}")
    print(f"{G} ██████╔╝╚██████╔╝   ██║       ███████╗╚██████╔╝██║ ╚████║███████╗██╔╝ ██╗{W}")
    print(f"{G} ╚═════╝  ╚═════╝    ╚═╝       ╚══════╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝{W}")
    print(line)
    print(
        f"{B}● MODE:{W} {G}{mode.upper()}{W}   "
        f"{B}● CYCLE:{W} {Y}{cycle}{W}   "
        f"{B}● NETWORK:{W} {M}{active_network}{W}"
    )
    print(
        f"{B}● USER:{W} {C}{email}{W}   "
        f"{B}● STATUS:{W} {G}ONLINE{W}   "
        f"{B}● TIME:{W} {Y}{time.strftime('%H:%M:%S')}{W}"
    )
    print(line)

def get_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            data = json.load(f)
        # Backward-compatible config migration for old/broken config files.
        if not isinstance(data, dict):
            data = {}
        if not data.get("email"):
            banner(active_network="CONFIG FIX")
            print(f"{Y}[!] Missing 'email' in config.json. Please re-enter details.{W}")
            data["email"] = input(f"{C}➤ FaucetPay Email : {W}").strip()
        if not data.get("api_key"):
            data["api_key"] = input(f"{C}➤ xEvil API Key   : {W}").strip()
        if "phpsessid" not in data:
            data["phpsessid"] = ""
        mode_input = str(data.get("mode", FREE_MODE)).strip().lower()
        data["mode"] = PAID_MODE if mode_input == PAID_MODE else FREE_MODE
        with open(CONFIG_FILE, 'w') as f:
            json.dump(data, f)
        return data

    banner(active_network="CONFIG")
    print(f"{B}[?] {W}Configuring New User Details...")
    email = input(f"{C}➤ FaucetPay Email : {W}")
    api_key = input(f"{C}➤ xEvil API Key   : {W}")
    mode_input = input(f"{C}➤ Mode (free/paid) [free]: {W}").strip().lower()
    mode = PAID_MODE if mode_input == PAID_MODE else FREE_MODE
    data = {"email": email, "api_key": api_key, "phpsessid": "", "mode": mode}
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f)
    return data

def get_mode_coin_sets(mode):
    if mode == PAID_MODE:
        return COINS_FREE, COINS_BEE, True
    return COINS_FREE_LIMITED, COINS_BEE_LIMITED, False

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
    session.headers.update(default_headers())
    url = f"https://claimfreecoins.io/{coin}-faucet/?r=arasarathinam3@gmail.com" if site_type == "free" else f"https://beefaucet.org/{coin}-faucet/?r=anilodhi2019@gmail.com"
    if site_type == "bee": session.cookies.update({'PHPSESSID': sess_id})

    try:
        res = session.get(url, timeout=10)
        if "cloudflare" in res.text.lower():
            return f"{R}CLOUDFLARE BLOCK{W}"
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
    config = get_config()
    mode = config.get("mode", FREE_MODE).lower()
    if mode not in (FREE_MODE, PAID_MODE):
        mode = FREE_MODE
    free_coins, bee_coins, enable_bee = get_mode_coin_sets(mode)
    cycle = 1
    while True:
        banner(cycle=cycle, active_network="BATCH START", email=config['email'], mode=mode)
        print(f"{M}🌀 BATCH: #{cycle} STARTING...{W}\n")

        # --- SOURCE 1 ---
        token1 = get_captcha_token(config['api_key'], "https://claimfreecoins.io/tether-faucet/?r=arasarathinam3@gmail.com")
        if token1:
            print(f"\n{C}🌐 NETWORK: {Y}ClaimFreeCoins.io ({mode.upper()}){W}")
            with ThreadPoolExecutor(max_workers=5) as ex:
                futures = {ex.submit(claim_process, c, config['email'], token1, "free"): c for c in free_coins}
                for f in as_completed(futures):
                    coin = futures[f]
                    result = f.result()
                    icon = f"{G}💸{W}" if "CLAIM SUCCESSFUL" in result else f"{Y}⚠️{W}"
                    slow_type(f"  {W}➤ {coin.upper():<11} : {result} {icon}")

        # Security Check
        print(f"\n{B}[🛡️] Firewall Scan: {W}Bypassing...", end="")
        s = requests.Session()
        s.headers.update(default_headers())
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
        if enable_bee:
            token2 = get_captcha_token(config['api_key'], "https://beefaucet.org/usdt-faucet/?r=anilodhi2019@gmail.com")
            if token2 and config['phpsessid']:
                print(f"\n{C}🐝 NETWORK: {Y}BeeFaucet.org ({mode.upper()}){W}")
                with ThreadPoolExecutor(max_workers=5) as ex:
                    futures = {ex.submit(claim_process, c, config['email'], token2, "bee", config['phpsessid']): c for c in bee_coins}
                    for f in as_completed(futures):
                        coin = futures[f]
                        result = f.result()
                        icon = f"{G}💰{W}" if "CLAIM SUCCESSFUL" in result else f"{Y}⚠️{W}"
                        slow_type(f"  {W}➤ {coin.upper():<11} : {result} {icon}")
            else:
                print(f"{Y}[!] BeeFaucet skipped: token/session missing.{W}")
        else:
            print(f"{Y}[!] FREE mode: BeeFaucet disabled, limited faucet set active.{W}")

        print(f"\n{G}✅ BATCH {cycle} PRINTING COMPLETED!{W}")
        for i in range(30, 0, -1):
            sys.stdout.write(f"\r{B}⏳ System Re-Energizing: {R}{i}s {W}until next print...")
            sys.stdout.flush(); time.sleep(1)
        cycle += 1

if __name__ == "__main__":
    try: start_bot()
    except KeyboardInterrupt: print(f"\n\n{R}🚨 SYSTEM STOPPED BY ADMIN.{W}"); sys.exit()
