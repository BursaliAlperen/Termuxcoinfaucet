"""NINOKI SlotCoin - readable SlotFruits/FaucetPay helper.

This is a single-file, unobfuscated reconstruction with optional support for up
to five FaucetPay email accounts. Pick an account by typing 1, 2, 3, 4, or 5;
empty slots can be filled from the same menu.
"""

import json
import os
import shutil
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

import requests

APP_NAME = "NINOKI SlotCoın"
CREATOR_TG = "AlperenTHE"
ACCOUNTS_FILE = Path(__file__).with_name("SlotCoin_accounts.json")
MAX_ACCOUNTS = 5

W = "\033[0m"
R = "\033[31m"
G = "\033[32m"
Y = "\033[33m"
B = "\033[34m"
M = "\033[35m"
C = "\033[36m"


def clear():
    os.system("clear" if os.name != "nt" else "cls")


def width():
    return shutil.get_terminal_size(fallback=(70, 20)).columns


def line(char="═"):
    return char * width()


def center(text):
    return text.center(width())


def banner():
    clear()
    print(C + line("═") + W)
    print(center(f"🚀 {APP_NAME} 🚀"))
    print(C + line("═") + W)
    print("Creator TG       : " + M + CREATOR_TG + W)
    print("Saat             : " + Y + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + W)
    print(C + line("═") + W)


def anim(text):
    for i in range(2):
        print(Y + text + "." * i + W, end="\r")
        time.sleep(0.4)
    print(" " * width(), end="\r")


def safe_json(response):
    try:
        return response.json()
    except Exception:
        return {}


def load_accounts():
    if not ACCOUNTS_FILE.exists():
        return [""] * MAX_ACCOUNTS
    try:
        data = json.loads(ACCOUNTS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return [""] * MAX_ACCOUNTS
    accounts = data.get("accounts", []) if isinstance(data, dict) else []
    accounts = [str(email).strip() for email in accounts[:MAX_ACCOUNTS]]
    return accounts + ([""] * (MAX_ACCOUNTS - len(accounts)))


def save_accounts(accounts):
    ACCOUNTS_FILE.write_text(
        json.dumps({"accounts": accounts[:MAX_ACCOUNTS]}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def choose_account():
    accounts = load_accounts()
    while True:
        banner()
        print(G + "FaucetPay hesapları" + W)
        for index, email in enumerate(accounts, start=1):
            label = email if email else "[boş - eklemek için seç]"
            print(f"{Y}{index}{W}) {label}")
        print(f"{Y}A{W}) Hesap ekle/güncelle")
        print(f"{Y}Q{W}) Çıkış")
        choice = input("Seçim (1-5/A/Q): ").strip().lower()

        if choice == "q":
            raise SystemExit

        if choice == "a":
            slot = input("Güncellenecek slot (1-5): ").strip()
            if not slot.isdigit() or not 1 <= int(slot) <= MAX_ACCOUNTS:
                input(R + "Geçersiz slot. Devam için Enter..." + W)
                continue
            email = input("FaucetPay email: ").strip()
            if not email:
                input(R + "Email boş olamaz. Devam için Enter..." + W)
                continue
            accounts[int(slot) - 1] = email
            save_accounts(accounts)
            continue

        if choice.isdigit() and 1 <= int(choice) <= MAX_ACCOUNTS:
            slot_index = int(choice) - 1
            if not accounts[slot_index]:
                email = input(f"Slot {choice} için FaucetPay email gir: ").strip()
                if not email:
                    input(R + "Email boş olamaz. Devam için Enter..." + W)
                    continue
                accounts[slot_index] = email
                save_accounts(accounts)
            return accounts[slot_index]

        input(R + "Geçersiz seçim. Devam için Enter..." + W)


def print_info(email, balance, credits):
    print(G + "Email           : " + W + str(email))
    print(G + "Balance         : " + W + str(balance))
    print(G + "Spin Available  : " + W + str(credits))
    print(C + line("═") + W)


def login(email):
    banner()
    anim("🔐 Login")
    url = "https://slotfruits.com/api/v1/users/signupFaucetPayLogin"
    payload = {"email": email}
    headers = {
        "User-Agent": "okhttp/4.12.0",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
    }
    data = safe_json(requests.post(url, data=json.dumps(payload), headers=headers, timeout=30))
    token = data.get("token")
    user = data.get("user", {}) or {}
    return token, user.get("_id"), user.get("balance", 0), user.get("credits", 0)


def spin_loop(email, token, balance=0, credits=0):
    if not token:
        print(R + "Token alınamadı; spin atlanıyor." + W)
        return balance, credits

    url_spin = "https://slotfruits.com/api/v1/users/earnRoll"
    headers_spin = {
        "User-Agent": "okhttp/4.12.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip",
        "authorization": "Bearer " + token,
    }
    while int(credits or 0) > 0:
        anim("🎰 Try To Spin")
        spin = safe_json(requests.get(url_spin, headers=headers_spin, timeout=30))
        total = spin.get("total", 0)
        user = spin.get("user", {}) or {}
        balance = user.get("balance", balance)
        credits = user.get("credits", int(credits or 1) - 1)
        banner()
        print_info(email, balance, credits)
        print(Y + "🎁 Reward        : " + W + str(total))
        print(C + line("═") + W)
        time.sleep(1)
    return balance, credits


def ads_loop(userid):
    if not userid:
        print(R + "User ID alınamadı; ads farming atlanıyor." + W)
        return

    url = "https://googleads.g.doubleclick.net/mads/gma?submodel=SM-A217F&adid_p=1&format=interstitial_mb&ini_pn=com.google.android.packageinstaller&ins_pn=com.google.android.packageinstaller&omid_v=a.1.5.2-google_20241009&dv=254380203&ev=24.6.0&gl=ID&hl=in&js=afma-sdk-a-v254380999.253410000.1&kw=clothing%2Cfashion&lv=253410000&ms=CqgFmsA_ATEaQQHY5dWIJ1nnZI0TXJOCrRjxy3oie3ZsfYBDue5jJF2CTFQQuf7W9C9KnP8xbLx0FI_PC-5wIrw0itcrK2KvDP4iEt0E6Yp1pn72NO8vWhbzh19JnXz5v7gGWsohjScUvkVohNO_jbecHUPYSmq4yT-WuJZ2EFv8_r-2HxOMJ5IgLNs"
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 12; SM-A217F Build/SP1A.210812.016; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/147.0.7727.111 Mobile Safari/537.36 (Mobile; afma-sdk-a-v260480999.253410000.1)",
        "sec-ch-ua-platform": "\"Android\"",
        "sec-ch-ua": "\"Android WebView\";v=\"147\", \"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"147\"",
        "sec-ch-ua-mobile": "?1",
        "x-requested-with": "com.piratebaixe.slotMobile",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://googleads.g.doubleclick.net/mads/static/sdk/native/sdk-core-v40.html",
        "accept-language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
        "if-none-match": "13022804227014334371",
        "priority": "u=1, i",
        "Cookie": "IDE=AHWqTUmPTIJAy-Z7wZUR-Si3c3uYRcuBwUfjmr_ffdlWQMrcruxMTVUyL8XPtA-y_Dk",
    }
    print(C + line("─") + W)
    print(Y + "🚀 Start Ads Farming..." + W)
    response = requests.get(url, headers=headers, timeout=30)
    data = safe_json(response)
    ad_network = (data.get("ad_networks") or [{}])[0]
    video_urls = ad_network.get("video_reward_urls") or [url]
    vid_url = video_urls[0]
    parsed = urlparse(vid_url)
    qs = parse_qs(parsed.query, keep_blank_values=True)
    qs["rwd_userid"] = userid
    new_url = urlunparse(parsed._replace(query=urlencode(qs, doseq=True)))
    result = requests.get(new_url, headers=headers, timeout=30)
    if result.status_code == 200:
        print(G + "✔ Ads Hit " + W + new_url)
    else:
        print(R + "Error Ads" + W)
    time.sleep(3)


def run_account(email):
    token, userid, balance, credits = login(email)
    banner()
    print_info(email, balance, credits)
    balance, credits = spin_loop(email, token, balance, credits)
    ads_loop(userid)


def main():
    while True:
        email = choose_account()
        run_account(email)
        again = input("Başka hesaba geçmek için Enter, çıkmak için Q: ").strip().lower()
        if again == "q":
            break


if __name__ == "__main__":
    main()
