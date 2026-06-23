"""Readable SlotFruits faucet helper.

This file replaces the previous multi-stage obfuscated loader with the plain
Python logic it executed.  It logs in with a FaucetPay email, repeatedly claims
available spins, and sends the reward-ad callback URL with the current user id.
"""

from __future__ import annotations

import os
import shutil
import time
from datetime import datetime
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

import requests

# ANSI colors used by the terminal UI.
RESET = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"

API_BASE = "https://slotfruits.com/api/v1/users"
LOGIN_URL = f"{API_BASE}/signupFaucetPayLogin"
SPIN_URL = f"{API_BASE}/earnRoll"

DEFAULT_TIMEOUT = 30
ANDROID_USER_AGENT = "okhttp/4.12.0"

ADS_URL = (
    "https://googleads.g.doubleclick.net/mads/gma?"
    "submodel=SM-A217F&adid_p=1&format=interstitial_mb&"
    "ini_pn=com.google.android.packageinstaller&"
    "ins_pn=com.google.android.packageinstaller&"
    "omid_v=a.1.5.2-goog"
)

ADS_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Linux; Android 12; SM-A217F Build/SP1A.210812.016; wv) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 "
        "Chrome/147.0.7727.111 Mobile Safari/537.36 "
        "(Mobile; afma-sdk-a-v260480999.2534100)"
    ),
    "sec-ch-ua-platform": '"Android"',
    "sec-ch-ua": '"Android WebView";v="147", "Not.A/Brand";v="8", "Chromium";v="147"',
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


def clear() -> None:
    """Clear the terminal screen."""
    os.system("clear")


def terminal_width() -> int:
    """Return the terminal width, falling back to shutil's default."""
    return shutil.get_terminal_size().columns


def line(char: str = "═") -> str:
    """Build a full-width separator line."""
    return char * terminal_width()


def center(text: str) -> str:
    """Center text for the current terminal width."""
    return text.center(terminal_width())


def banner() -> None:
    """Render the program banner."""
    now = datetime.now()
    clear()
    print(CYAN + line("═") + RESET)
    print(CYAN + center("🚀 SLOT MOBILE SYNDICATEBOT NET 🚀") + RESET)
    print(MAGENTA + center("Created By        : Leonnnx77") + RESET)
    print(MAGENTA + center("Channel Telegram  : https://t.me/SyndicateBotNet") + RESET)
    print(MAGENTA + center(now.strftime("%Y-%m-%d %H:%M:%S")) + RESET)
    print(CYAN + line("═") + RESET)


def animate(text: str) -> None:
    """Print a short two-dot loading animation."""
    for i in range(2):
        print(f"\r{YELLOW}{text}{'.' * (i + 1)}{RESET}", end="")
        time.sleep(0.4)
    print("\r", end="")


def print_info(email: str, balance: Any, credits: Any) -> None:
    """Print current account information."""
    print(GREEN + f"Email           : {email}" + RESET)
    print(GREEN + f"Balance         : {balance}" + RESET)
    print(GREEN + f"Spin Available  : {credits}" + RESET)
    print(CYAN + line("═") + RESET)


def login(email: str) -> tuple[str, str, Any, Any]:
    """Log in with a FaucetPay email and return token, user id, balance, credits."""
    banner()
    animate("🔐 Login")

    payload = {"email": email}
    headers = {
        "User-Agent": ANDROID_USER_AGENT,
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
    }
    response = requests.post(LOGIN_URL, json=payload, headers=headers, timeout=DEFAULT_TIMEOUT)
    response.raise_for_status()
    data = response.json()

    token = data["token"]
    user = data["user"]
    return token, user["_id"], user.get("balance", 0), user.get("credits", 0)


def spin_loop(email: str, token: str, balance: Any, credits: Any) -> tuple[Any, Any]:
    """Claim spins until the API reports that no spin credits remain."""
    headers = {
        "User-Agent": ANDROID_USER_AGENT,
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip",
        "authorization": f"Bearer {token}",
    }

    while int(credits or 0) > 0:
        animate("🎰 Try To Spin")
        response = requests.get(SPIN_URL, headers=headers, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
        spin = response.json()

        total = spin.get("total", 0)
        user = spin.get("user", {})
        balance = user.get("balance", balance)
        credits = user.get("credits", credits)

        banner()
        print_info(email, balance, credits)
        print(YELLOW + f"🎁 Reward        : {total}" + RESET)
        print(CYAN + line("═") + RESET)
        time.sleep(1)

    return balance, credits


def _ad_callback_url(raw_url: str, userid: str) -> str:
    """Inject the current user id into a Google ad reward callback URL."""
    parsed = urlparse(raw_url)
    query = parse_qs(parsed.query, keep_blank_values=True)
    query["rwd_userid"] = [userid]
    return urlunparse(parsed._replace(query=urlencode(query, doseq=True)))


def ads_loop(userid: str) -> None:
    """Fetch and hit ad reward callback URLs without aborting the main loop."""
    print(CYAN + line("─") + RESET)
    print(YELLOW + "🚀 Start Ads Farming..." + RESET)

    for index in range(1, 4):
        try:
            response = requests.get(ADS_URL, headers=ADS_HEADERS, timeout=DEFAULT_TIMEOUT)
            if response.status_code != 200:
                print(RED + f"Error Ads ({response.status_code})" + RESET)
                time.sleep(3)
                continue

            data = response.json()
        except requests.RequestException as exc:
            print(RED + f"Error Ads ({exc})" + RESET)
            time.sleep(3)
            continue
        except ValueError:
            print(RED + "Error Ads (invalid JSON)" + RESET)
            time.sleep(3)
            continue

        ad_networks = data.get("ad_networks") or []
        video_urls = ad_networks[0].get("video_reward_urls", []) if ad_networks else []
        if not video_urls:
            print(RED + "Error Ads" + RESET)
            time.sleep(3)
            continue

        reward_url = _ad_callback_url(video_urls[0], userid)
        try:
            callback = requests.get(
                reward_url,
                headers={"Content-Type": "application/json"},
                timeout=DEFAULT_TIMEOUT,
            )
        except requests.RequestException as exc:
            print(RED + f"Error Ads ({exc})" + RESET)
            time.sleep(3)
            continue

        if callback.status_code == 200:
            print(GREEN + f"✔ Ads Hit {index}" + RESET)
        else:
            print(RED + "Error Ads" + RESET)
        time.sleep(3)


def main() -> None:
    """Run the login, spin, and ad-farming cycle forever."""
    email = input(" Enter Your Faucet Email => ").strip()
    token, userid, balance, credits = login(email)

    while True:
        balance, credits = spin_loop(email, token, balance, credits)
        print(GREEN + "✔ Spin Done" + RESET)
        ads_loop(userid)
        print(YELLOW + "🔄 Restarting cycle..." + RESET)


if __name__ == "__main__":
    main()
