# -*- coding: utf-8 -*-
"""Ninoki BeeFaucet auto-claim bot.

This file is the fully decrypted and cleaned version of the original bot.
It keeps the faucet automation flow, removes the shortlink key gate, and uses
English-only status messages.
"""

import json
import os
import re
import sys
import time
from typing import Optional

import requests
from bs4 import BeautifulSoup

# --- Console colors ---
GREEN = "\033[38;5;46m"
RED = "\033[38;5;196m"
YELLOW = "\033[38;5;226m"
BLUE = "\033[38;5;51m"
PINK = "\033[38;5;201m"
WHITE = "\033[0m"

CONFIG_FILE = "config.json"
CAPTCHA_SOLVER_URL = "http://waryono.my.id"
SITE_KEY = "6LfwaSgTAAAAAJJNz6oAdimVHmIe3s4fHj4D0at4"
REFERRAL_EMAIL = "anilodhi2019@gmail.com"

COINS = [
    "eth", "usdt", "bnb", "sol", "usdc", "xrp", "doge", "trx", "ton",
    "bch", "ada", "ltc", "matic", "xmr", "xlm", "zec", "dash", "dgb", "fey",
]

session = requests.Session()
session.headers.update({
    "user-agent": (
        "Mozilla/5.0 (Linux; Android 12; K) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
    )
})


def clear() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def type_text(text: str, delay: float = 0.003) -> None:
    for char in text:
        print(char, end="", flush=True)
        time.sleep(delay)
    print()


def loading(text: str = "Loading", steps: int = 3, delay: float = 0.15) -> None:
    for index in range(steps):
        print(f"{YELLOW}{text}{'.' * (index + 1)}{WHITE}   ", end="\r", flush=True)
        time.sleep(delay)
    print(" " * (len(text) + steps + 5), end="\r", flush=True)


def banner() -> None:
    clear()
    print(f"{GREEN} ███╗   ██╗██╗███╗   ██╗ ██████╗ ██╗  ██╗██╗{WHITE}")
    print(f"{GREEN} ████╗  ██║██║████╗  ██║██╔═══██╗██║ ██╔╝██║{WHITE}")
    print(f"{GREEN} ██╔██╗ ██║██║██╔██╗ ██║██║   ██║█████╔╝ ██║{WHITE}")
    print(f"{GREEN} ██║╚██╗██║██║██║╚██╗██║██║   ██║██╔═██╗ ██║{WHITE}")
    print(f"{GREEN} ██║ ╚████║██║██║ ╚████║╚██████╔╝██║  ██╗██║{WHITE}")
    print(f"{GREEN} ╚═╝  ╚═══╝╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝╚═╝{WHITE}")
    print(f"{YELLOW}                 ⚡ Ninoki fast claim ⚡{WHITE}")
    print(GREEN + "=" * 55 + WHITE)


def save_config(config: dict) -> None:
    with open(CONFIG_FILE, "w", encoding="utf-8") as file:
        json.dump(config, file, indent=2)


def first_value(config: dict, keys: tuple[str, ...]) -> str:
    for key in keys:
        value = config.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def normalize_config(config: dict) -> dict:
    """Support older config.json files and prevent missing-key crashes."""
    normalized = {
        "email": first_value(config, ("email", "mail", "faucetpay", "faucetpay_email", "address", "wallet")),
        "api_key": first_value(config, ("api_key", "apikey", "api", "captcha_key", "captcha_api_key", "key")),
    }

    changed = normalized["email"] != config.get("email") or normalized["api_key"] != config.get("api_key")

    if not normalized["email"]:
        normalized["email"] = input(f"{GREEN}[+] FaucetPay email: {WHITE}").strip()
        changed = True

    if not normalized["api_key"]:
        normalized["api_key"] = input(f"{GREEN}[+] Waryono captcha API key: {WHITE}").strip()
        changed = True

    if changed:
        save_config(normalized)

    return normalized


def load_config() -> dict:
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as file:
            return normalize_config(json.load(file))

    banner()
    type_text(f"{YELLOW}[!] First-time setup required{WHITE}")
    data = normalize_config({})
    save_config(data)
    return data


def get_captcha_token(api_key: str, coin: str) -> Optional[str]:
    page_url = f"https://beefaucet.org/{coin}-faucet/"

    try:
        loading(f"Submitting captcha for {coin.upper()}")
        response = requests.get(
            f"{CAPTCHA_SOLVER_URL}/in.php",
            params={
                "key": api_key,
                "method": "userrecaptcha",
                "pageurl": page_url,
                "sitekey": SITE_KEY,
            },
            timeout=15,
        ).text

        if "OK|" not in response:
            return None

        captcha_id = response.split("|", 1)[1]
        for _ in range(20):
            loading(f"Solving {coin.upper()}")
            time.sleep(5)
            status = requests.get(
                f"{CAPTCHA_SOLVER_URL}/res.php",
                params={"key": api_key, "action": "get", "id": captcha_id},
                timeout=15,
            ).text

            if "OK|" in status:
                return status.split("|", 1)[1]
            if status.startswith("ERROR"):
                return None

    except requests.RequestException as exc:
        print(f"{RED}[!] Captcha request failed: {exc}{WHITE}")

    return None


def claim_coin(config: dict, coin: str, captcha_token: str) -> None:
    sys.stdout.write(f"\r\033[K{PINK}⚡ Claiming → {coin.upper():<6}{WHITE}")
    sys.stdout.flush()

    try:
        url = f"https://beefaucet.org/{coin}-faucet/?r={REFERRAL_EMAIL}"
        response = session.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        session_token = soup.find("input", {"name": "session-token"})
        if not session_token or not session_token.get("value"):
            print(f"\r{RED}[X] {coin.upper():<7}: Session token not found{WHITE}")
            return

        claim_response = session.post(
            url,
            data={
                "session-token": session_token["value"],
                "address": config["email"],
                "captcha": "recaptcha",
                "g-recaptcha-response": captcha_token,
                "login": "Verify",
            },
            timeout=10,
        )
        claim_response.raise_for_status()

        if "satoshi was sent" in claim_response.text:
            match = re.search(r"([0-9.]+) satoshi was sent", claim_response.text)
            amount = match.group(1) if match else "OK"
            print(f"\r{GREEN}[✓] {coin.upper():<7}: Success (+{amount}){WHITE}")
        else:
            print(f"\r{YELLOW}[!] {coin.upper():<7}: Cooldown or skipped{WHITE}")

    except requests.RequestException as exc:
        print(f"\r{RED}[!] {coin.upper():<7}: Connection error ({exc}){WHITE}")


def start_bot() -> None:
    config = load_config()
    start_time = time.time()
    cycle = 1

    while True:
        banner()
        uptime = time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time))
        print(f"{BLUE}╔════════════════ STATUS ══════════════╗{WHITE}")
        print(f"{GREEN}   Cycle   : {cycle}")
        print(f"   Uptime  : {uptime}")
        print(f"   Target  : {config['email']}{WHITE}")
        print(f"{BLUE}╚══════════════════════════════════════╝{WHITE}\n")
        loading("Starting fast claim batch")

        for index in range(0, len(COINS), 4):
            chunk = COINS[index:index + 4]
            captcha_token = None

            while captcha_token is None:
                captcha_token = get_captcha_token(config["api_key"], chunk[0])
                if not captcha_token:
                    print(f"\r{RED}[!] Captcha failed. Retrying for {chunk[0].upper()}...{WHITE}   ")
                    time.sleep(5)

            print(f"\r{GREEN}[✓] Captcha received for batch{WHITE}                           ")

            for coin in chunk:
                claim_coin(config, coin, captcha_token)
                time.sleep(0.5)

            print(f"\n{YELLOW}[~] Batch completed. Loading the next batch...{WHITE}")
            loading("Loading")
            time.sleep(1)

        print(f"\n{GREEN}[#] Cycle {cycle} completed{WHITE}")
        time.sleep(10)
        cycle += 1


if __name__ == "__main__":
    try:
        start_bot()
    except KeyboardInterrupt:
        print(f"\n{RED}[!] Stopped by user.{WHITE}")
