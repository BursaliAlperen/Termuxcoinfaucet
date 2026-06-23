#!/usr/bin/env python3
"""NINOKI FRUIT SCRIPT - SlotFruits helper for Termux."""

from __future__ import annotations

import os
import sys
import time
from datetime import datetime
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

import requests

APP_NAME = "NINOKI FRUIT SCRIPT"
BASE_URL = "https://slotfruits.com/api/v1/users"
LOGIN_URL = f"{BASE_URL}/signupFaucetPayLogin"
SPIN_URL = f"{BASE_URL}/earnRoll"
ADS_URL = "https://googleads.g.doubleclick.net/mads/gma?submodel=SM-A217F&adid_p=1&format=interstitial_mb&ini_pn=com.google.android.packageinstaller&ins_pn=com.google.android.packageinstaller&omid_v=a.1.5.2-google_20241009&dv=254380203&ev=24.6.0&gl=ID&hl=in&js=afma-sdk-a-v254380999.253410000.1&kw=clothing%2Cfashion&lv=253410000&ms=CqgFmsA_ATEaQQHY5dWIJ1nnZI0TXJOCrRjxy3oie3ZsfYBDue5jJF2CTFQQuf7W9C9KnP8xbLx0FI_PC-5wIrw0itcrK2KvDP4iEt0E6Yp1pn72NO8vWhbzh19JnXz5v7gGWsohjScUvkVohNO_jbecHUPYSmq4yT-WuJZ2EFv8_r-2H"
REQUEST_TIMEOUT = 15
SPIN_DELAY = 0.25
AD_DELAY = 0.1

W = "\033[97m"
R = "\033[91m"
G = "\033[92m"
Y = "\033[93m"
B = "\033[94m"
M = "\033[95m"
C = "\033[96m"
RESET = "\033[0m"


def clear() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def width() -> int:
    try:
        return os.get_terminal_size().columns
    except OSError:
        return 60


def line(char: str = "=") -> str:
    return char * width()


def center(text: str) -> str:
    return text.center(width())


def banner() -> None:
    clear()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{C}{line()}{RESET}")
    print(f"{M}{center(APP_NAME)}{RESET}")
    print(f"{W}{center(now)}{RESET}")
    print(f"{C}{line()}{RESET}")


def anim(text: str) -> None:
    # Keep the Termux UI responsive; older animation sleeps made the script feel slow.
    print(f"{Y}{text}{RESET}", flush=True)


def safe_json(response: requests.Response) -> dict[str, Any]:
    try:
        data = response.json()
        return data if isinstance(data, dict) else {"data": data}
    except ValueError:
        return {"raw": response.text}


def nested_get(data: dict[str, Any], *path: str) -> Any:
    cur: Any = data
    for key in path:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(key)
    return cur


def user_from_response(data: dict[str, Any]) -> dict[str, Any]:
    user = data.get("user") or nested_get(data, "data", "user") or data.get("data") or {}
    return user if isinstance(user, dict) else {}


def first_int(*values: Any, default: int = 0) -> int:
    for value in values:
        if value is None:
            continue
        try:
            return int(float(str(value).strip()))
        except (TypeError, ValueError):
            continue
    return default


def extract_spin_count(data: dict[str, Any], previous: int = 0) -> int:
    """Read the authoritative spin count from every known API field.

    The previous script could print a stale/decremented local value, so Termux
    sometimes showed fewer spins than the Android app. This function always
    prefers the freshest server-provided user counters after login/spin.
    """
    user = user_from_response(data)
    return first_int(
        data.get("credits"),
        data.get("spin"),
        data.get("spins"),
        data.get("spin_available"),
        data.get("availableSpin"),
        data.get("availableSpins"),
        nested_get(data, "data", "credits"),
        nested_get(data, "data", "spin"),
        nested_get(data, "data", "spins"),
        user.get("credits"),
        user.get("spin"),
        user.get("spins"),
        user.get("spin_available"),
        user.get("availableSpin"),
        user.get("availableSpins"),
        default=previous,
    )


def extract_balance(data: dict[str, Any], previous: int = 0) -> int:
    user = user_from_response(data)
    return first_int(data.get("balance"), nested_get(data, "data", "balance"), user.get("balance"), default=previous)


def print_info(email: str, balance: int, credits: int) -> None:
    print(f"{G}Email           : {W}{email}{RESET}")
    print(f"{G}Balance         : {W}{balance}{RESET}")
    print(f"{G}Spin Available  : {W}{credits}{RESET}")
    print(f"{C}{line()}{RESET}")


def make_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({
        "User-Agent": "okhttp/4.12.0",
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
    })
    return session


def login(session: requests.Session, email: str) -> tuple[str, str, int, int]:
    banner()
    anim("Login...")
    response = session.post(LOGIN_URL, json={"email": email}, timeout=REQUEST_TIMEOUT)
    data = safe_json(response)
    if response.status_code >= 400:
        raise RuntimeError(f"Login failed ({response.status_code}): {data}")

    token = str(data.get("token") or nested_get(data, "data", "token") or "")
    user = user_from_response(data)
    userid = str(user.get("id") or user.get("_id") or data.get("userid") or data.get("userId") or "")
    balance = extract_balance(data)
    credits = extract_spin_count(data)
    if token:
        session.headers.update({"authorization": token})
    print_info(email, balance, credits)
    return token, userid, balance, credits


def spin_loop(session: requests.Session, email: str, balance: int, credits: int) -> tuple[int, int]:
    total = 0
    while credits > 0:
        anim(f"🎰 Try To Spin ({credits} left)")
        response = session.get(SPIN_URL, timeout=REQUEST_TIMEOUT)
        data = safe_json(response)
        if response.status_code >= 400:
            print(f"{R}Spin failed ({response.status_code}): {data}{RESET}")
            break

        total += 1
        balance = extract_balance(data, balance)
        # Server is authoritative. Fallback to one local decrement only if the
        # API omits all known spin fields.
        server_credits = extract_spin_count(data, previous=-1)
        credits = server_credits if server_credits >= 0 else max(credits - 1, 0)
        banner()
        print_info(email, balance, credits)
        print(f"{G}✔ Spin Done     : {W}{total}{RESET}")
        time.sleep(SPIN_DELAY)
    return balance, credits


def ads_loop(session: requests.Session, userid: str, rounds: int = 3) -> None:
    if not userid:
        return
    print(f"{C}{line()}{RESET}")
    for _ in range(rounds):
        try:
            response = session.get(ADS_URL, timeout=REQUEST_TIMEOUT)
            data = safe_json(response)
            vid_url = data.get("video_url") or data.get("url")
            if not vid_url:
                continue
            parsed = urlparse(str(vid_url))
            qs = parse_qs(parsed.query)
            qs["rwd_userid"] = [userid]
            new_url = urlunparse(parsed._replace(query=urlencode(qs, doseq=True)))
            r = session.get(new_url, timeout=REQUEST_TIMEOUT)
            print(f"{G}Ad request: {r.status_code}{RESET}")
            time.sleep(AD_DELAY)
        except requests.RequestException as exc:
            print(f"{R}Ad skipped: {exc}{RESET}")
            break


def main() -> int:
    try:
        banner()
        email = input(f"{Y}FaucetPay Email: {W}").strip()
        if not email:
            print(f"{R}Email required.{RESET}")
            return 1
        session = make_session()
        token, userid, balance, credits = login(session, email)
        if not token:
            print(f"{Y}Warning: token missing; continuing with session cookies only.{RESET}")
        balance, credits = spin_loop(session, email, balance, credits)
        ads_loop(session, userid)
        print(f"{G}{APP_NAME} finished. Balance={balance}, Spins={credits}{RESET}")
        return 0
    except KeyboardInterrupt:
        print(f"\n{Y}Stopped by user.{RESET}")
        return 130
    except Exception as exc:  # noqa: BLE001 - show clear Termux error.
        print(f"{R}Error: {exc}{RESET}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
