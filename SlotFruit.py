#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import json
import random
import requests
import shutil
from datetime import datetime

# ANSI Color Codes
H0 = "\033[0m"
H1 = "\033[31m"
H2 = "\033[32m"
H3 = "\033[33m"
H4 = "\033[34m"
H5 = "\033[35m"
H6 = "\033[36m"
H7 = "\033[1;97m"
H8 = "\033[1;32m"
H9 = "\033[1;31m"

# Global stats
SESSION_STATS = {
    "spins": 0,
    "wins": 0,
    "total_reward": 0,
    "ads_hits": 0
}

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def get_terminal_width():
    try:
        return shutil.get_terminal_size().columns
    except Exception:
        return 80

def center(text):
    return text.center(get_terminal_width())

def line(char="═"):
    return char * get_terminal_width()

def banner():
    clear()
    print(f"{H4}{line('═')}{H0}")
    print(center(f"{H7}╔══════════════════════════════════════╗{H0}"))
    print(center(f"{H7}║{H2}  🎰  𝐒𝐋𝐎𝐓𝐅𝐑𝐔𝐈𝐓  𝐅𝐀𝐑𝐌𝐄𝐑  🎰  {H7}║{H0}"))
    print(center(f"{H7}╠══════════════════════════════════════╣{H0}"))
    print(center(f"{H7}║{H6}        𝐀  𝐏𝐋𝐔𝐒  𝐄𝐃𝐈𝐓𝐈𝐎𝐍        {H7}║{H0}"))
    print(center(f"{H7}╠══════════════════════════════════════╣{H0}"))
    print(center(f"{H7}║{H3}  Created By : {H5}🇦🇱𝐀𝐥𝐩𝐞𝐫𝐞𝐧𝐓𝐇𝐄{H3}          {H7}║{H0}"))
    print(center(f"{H7}║{H3}  Version    : {H5}2.1.0 (Debug)             {H7}║{H0}"))
    print(center(f"{H7}╚══════════════════════════════════════╝{H0}"))
    print(f"{H4}{line('═')}{H0}")
    print()

def print_status(msg, status="info"):
    now = datetime.now().strftime("%H:%M:%S")
    if status == "success":
        print(f"{H2}[{now}] ✔ {msg}{H0}")
    elif status == "error":
        print(f"{H1}[{now}] ✖ {msg}{H0}")
    elif status == "warning":
        print(f"{H3}[{now}] ⚠ {msg}{H0}")
    elif status == "info":
        print(f"{H6}[{now}] ℹ {msg}{H0}")
    elif status == "spin":
        print(f"{H5}[{now}] 🎰 {msg}{H0}")
    elif status == "ads":
        print(f"{H3}[{now}] 💰 {msg}{H0}")
    elif status == "win":
        print(f"{H8}[{now}] 🎉 {msg}{H0}")
    elif status == "debug":
        print(f"{H3}[{now}] 🐞 {msg}{H0}")

def print_info(email, balance, credits):
    print(f"{H4}{line('─')}{H0}")
    print(f"{H6}  👤 Email          : {H7}{email}{H0}")
    print(f"{H6}  💵 Balance        : {H2}${balance:.2f}{H0}")
    print(f"{H6}  🎲 Spins Left     : {H3}{credits}{H0}")
    print(f"{H6}  📊 Session Stats  : {H5}{SESSION_STATS['spins']} spins, {SESSION_STATS['wins']} wins, ${SESSION_STATS['total_reward']:.4f} total{H0}")
    print(f"{H4}{line('─')}{H0}")
    print()

def login(email):
    url = "https://slotfruits.com/api/v1/users/signupFaucetPayLogin"
    headers = {
        "User-Agent": "okhttp/4.12.0",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json"
    }
    data = {"email": email}

    try:
        print_status("Logging in...", "info")
        res = requests.post(url, json=data, headers=headers, timeout=15)
        res.raise_for_status()
        res_json = res.json()
    except Exception as e:
        print_status(f"Login failed: {e}", "error")
        return None, None, {}

    token = res_json.get("token")
    user = res_json.get("user", {}) or {}
    user_id = user.get("_id") if user else None

    if not token or not user_id:
        print_status("Invalid credentials or API error!", "error")
        print_status(f"Response: {res_json}", "warning")
        return None, None, {}

    print_status("Login successful! ✅", "success")
    return token, user_id, res_json

def spin(token, user_id):
    """Gerçek spin işlemi - debug ile response'u gösterir"""
    global SESSION_STATS
    
    url_spin = "https://slotfruits.com/api/v1/users/earnRoll"
    headers_spin = {
        "User-Agent": "okhttp/4.12.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip",
        "authorization": f"Bearer {token}"
    }

    try:
        res = requests.get(url_spin, headers=headers_spin, timeout=15)
        res.raise_for_status()
        res_json = res.json()
    except Exception as e:
        print_status(f"Spin error: {e}", "error")
        return 0

    # DEBUG: Response'u göster
    print_status(f"Spin Response: {json.dumps(res_json, indent=2)}", "debug")

    # Reward'ı çıkarmak için tüm olasılıkları dene
    reward = 0
    if isinstance(res_json, dict):
        # Doğrudan anahtarlar
        for key in ["total", "reward", "amount", "win", "prize", "value", "credits", "points"]:
            if key in res_json:
                try:
                    reward = float(res_json[key])
                    break
                except:
                    pass
        # Eğer bulamazsak nested kontrol
        if reward == 0:
            for nested in ["data", "result", "response", "user"]:
                if nested in res_json and isinstance(res_json[nested], dict):
                    for key in ["total", "reward", "amount", "win", "prize", "value", "credits", "points"]:
                        if key in res_json[nested]:
                            try:
                                reward = float(res_json[nested][key])
                                break
                            except:
                                pass
                    if reward > 0:
                        break

    SESSION_STATS["spins"] += 1
    if reward > 0:
        SESSION_STATS["wins"] += 1
        SESSION_STATS["total_reward"] += reward

    return reward

def ads_loop(rwd_userid, doses):
    global SESSION_STATS
    
    print_status("Starting Ads Farming... 💰", "ads")
    base_url = "https://googleads.g.doubleclick.net/mads/gma"

    params = {
        "submodel": "SM-A217F",
        "adid_p": "1",
        "format": "interstitial_mb",
        "ini_p": "com.google.android.packageinstaller",
        "ins_p": "com.google.android.packageinstaller",
        "omid_v": "a.1.5.2-google_20241009",
        "dv": "254380203",
        "ev": "24.6.0",
        "gl": "ID",
        "hl": "in",
        "js": "afma-sdk-a-v254380999.253410000.1",
        "kw": "clothing,fashion",
        "lv": "253410000",
        "mv": "84923430.com.android.vending",
        "lft": "1",
        "vnm": "1.1.6",
        "plbs": "0",
        "plcs": "0",
        "u_sd": "1.75",
        "request_id": str(random.randint(1000000000, 9999999999)),
        "target_api": "35",
        "carrier": "51011",
        "request_agent": "rn-invertase-15.8.0",
        "seq_num": str(random.randint(1, 10)),
        "eids": "318500618,318486317,318491267,318503826,318509511,318509849,318515546,318518927,318527162,318482080,318483611,318484497,318484801,318525018,318526145,318526848",
        "guci": "0.0.0.0.0.0.0.0",
        "sdk_apis": "7,8",
        "omid_p": "Google/afma-sdk-a-v260480999.253410000.1",
        "cap": "m",
        "u_w": "412",
        "u_h": "828",
        "msid": "com.piratebaixe.slotMobile",
        "an": "17.android.com.spincoin.appmobile.top",
        "u_audio": "3",
        "net": "ed",
        "u_so": "p",
        "rbv": "1",
        "loeid": "44766145,318502926",
        "preqs_in_session": "1",
        "preqs": "1",
        "time_in_session": "70",
        "pcc": "0",
        "sst": str(int(time.time() * 1000)),
        "output": "htlm",
        "region": "mobile_app",
        "u_tz": "420",
        "client": "ca-app-pub-5674874137587223",
        "slotname": "7114498212",
        "kw_type": "broad",
        "gsb": "4g",
        "lite": "0",
        "app_wp_code": "ca-app-pub-5674874137587223",
        "app_code": "5186053460",
        "num_ads": "1",
        "vpt": "8",
        "vfmdt": "18",
        "vst": "0",
        "sdkv": "o.254380999.253410000.1",
        "sdkmax": "0",
        "dmax": "1",
        "sdki": "3c4d",
        "stbg": "1",
        "bisch": "true",
        "blev": "0.16",
        "canm": "true",
        "_mv": "84923430.com.android.vending",
        "heap_free": str(random.randint(30000000, 40000000)),
        "heap_max": "268435456",
        "heap_total": "67108864",
        "wv_count": "0",
        "rdps": "5500",
        "caps": "inlineVideo_interactiveVideo_mraid1_mraid2_mraid3_sdkVideo_exo3_th_autoplay_mediation_scroll_av_transparentBackground_sdkAdmobApiForAds_di_aso_sfv_dim_dim_nav_navc_dinmo_ipof_gls_gcach_e_saiMacro_sai_demuxedGcache_xSeconds",
        "is_lat": "false",
        "jsv": "sdk_20190107_RC02-production-sdk_20251202_RC00"
    }

    params['rwd_userid'] = str(rwd_userid)
    params['doses'] = str(doses)

    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 12; SM-A217F Build/SP1A.210812.016; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/147.0.7727.111 Mobile Safari/537.36 (Mobile; afma-sdk-a-v260480999.253410000.1)",
        "Sec-CH-UA": '"Android WebView";v="147", "Not.A/Brand";v="8", "Chromium";v="147"',
        "Sec-CH-UA-Platform": '"Android"',
        "Sec-CH-UA-Mobile": "?1",
        "X-Requested-With": "com.piratebaixe.slotMobile",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://googleads.g.doubleclick.net/mads/static/sdk/native/sdk-core-v40.html",
        "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
        "Priority": "u=1, i"
    }

    hit_count = 0
    for i in range(doses):
        try:
            params['request_id'] = str(random.randint(1000000000, 9999999999))
            params['seq_num'] = str(random.randint(1, 10))
            res = requests.get(base_url, params=params, headers=headers, timeout=10)
            if res.status_code in [200, 304]:
                hit_count += 1
                SESSION_STATS["ads_hits"] += 1
                print_status(f"Ads Hit {hit_count}/{doses} ✅", "ads")
            else:
                print_status(f"Ads Miss {i+1}/{doses} (HTTP {res.status_code})", "warning")
        except Exception as e:
            print_status(f"Ads Error {i+1}: {e}", "error")
        time.sleep(random.uniform(0.5, 2.0))

    print_status(f"Ads farming complete! {hit_count}/{doses} hits ✅", "success")
    return hit_count

def get_user_info(token):
    url = "https://slotfruits.com/api/v1/users/me"
    headers = {
        "User-Agent": "okhttp/4.12.0",
        "Accept": "application/json, text/plain, */*",
        "authorization": f"Bearer {token}"
    }
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        return res.json()
    except:
        return {}

def spin_loop(email):
    token, user_id, res_json = login(email)

    if not token or not user_id:
        print_status("Cannot proceed without valid login!", "error")
        retry = input(f"{H3}Retry? (y/n): {H0}").strip().lower()
        if retry == 'y':
            spin_loop(email)
        return

    # Extract balance & credits
    balance = 0
    credits = 0
    if "balance" in res_json:
        balance = float(res_json["balance"])
    elif "user" in res_json and res_json["user"]:
        balance = float(res_json["user"].get("balance", 0))
    
    if "credits" in res_json:
        credits = int(res_json["credits"])
    elif "user" in res_json and res_json["user"]:
        credits = int(res_json["user"].get("credits", 0))
    elif "spins" in res_json:
        credits = int(res_json["spins"])
    elif "rolls" in res_json:
        credits = int(res_json["rolls"])

    # Güncel bilgileri al
    user_info = get_user_info(token)
    if user_info:
        balance = float(user_info.get("balance", balance))
        credits = int(user_info.get("credits", credits))

    print_info(email, balance, credits)

    if credits <= 0:
        print_status("No spins left! Switching to ads... ⚠️", "warning")
        ads_loop(user_id, 10)
        print_status("Restarting cycle in 3 seconds...", "info")
        time.sleep(3)
        spin_loop(email)
        return

    spin_count = 0
    while credits > 0:
        spin_count += 1
        remaining = credits - 1
        print_status(f"Spin {spin_count} / Remaining: {remaining}", "spin")

        reward = spin(token, user_id)

        if reward > 0:
            print_status(f"🎉 WIN! +${reward:.4f}", "win")
        else:
            print_status(f"💨 No reward this time", "warning")

        credits -= 1
        if spin_count % 5 == 0:
            user_info = get_user_info(token)
            if user_info:
                balance = float(user_info.get("balance", balance))
                credits = int(user_info.get("credits", credits))
                print_info(email, balance, credits)

        time.sleep(random.uniform(0.8, 1.5))

    print_status("🎰 All spins used! 🎰", "success")
    print_status(f"📊 Session Stats: {SESSION_STATS['spins']} spins, {SESSION_STATS['wins']} wins, ${SESSION_STATS['total_reward']:.4f} total", "info")
    
    ads_loop(user_id, 15)
    print_status("Restarting cycle in 5 seconds...", "info")
    time.sleep(5)
    spin_loop(email)

def main():
    banner()
    print(f"{H6}  🎰 SlotFruit Auto Farmer v2.1 (Debug){H0}")
    print(f"{H6}  📧 Enter your FaucetPay email to start{H0}")
    print(f"{H6}  ⌨️  Press Ctrl+C to stop anytime{H0}")
    print()

    try:
        email = input(f"{H5}  📧 Email => {H0}").strip()
    except KeyboardInterrupt:
        print()
        print_status("Exiting... 👋", "info")
        sys.exit(0)

    if not email or "@" not in email:
        print_status("Invalid email format!", "error")
        sys.exit(1)

    print()
    print_status("Starting farming session... 🚀", "info")
    try:
        spin_loop(email)
    except KeyboardInterrupt:
        print()
        print()
        print_status("📊 Final Stats:", "info")
        print_status(f"Total Spins: {SESSION_STATS['spins']}", "info")
        print_status(f"Total Wins: {SESSION_STATS['wins']}", "info")
        print_status(f"Total Reward: ${SESSION_STATS['total_reward']:.4f}", "success")
        print_status(f"Ads Hits: {SESSION_STATS['ads_hits']}", "info")
        print()
        print_status("Stopped by user. Goodbye! 👋", "info")
        sys.exit(0)

if __name__ == "__main__":
    main()
