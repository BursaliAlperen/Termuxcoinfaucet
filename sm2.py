#!/usr/bin/env python3
"""NINOKI FRUIT SCRIPT

Clean and fast SlotFruits faucet helper.

Fixes the old spin counter bug by always refreshing the user profile after every
spin and by reading every known spin-count field from the API response before
printing the remaining amount.
"""

import json
import os
import shutil
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from http.client import HTTPException
from urllib.error import HTTPError, URLError
from urllib.request import Request, build_opener

SCRIPT_NAME = "NINOKI FRUIT SCRIPT"
BASE_URL = "https://slotfruits.com/api/v1/users"
LOGIN_URL = f"{BASE_URL}/signupFaucetPayLogin"
SPIN_URL = f"{BASE_URL}/earnRoll"
PROFILE_URL = f"{BASE_URL}/me"
DEFAULT_TIMEOUT = 20
REQUEST_DELAY = 0.15
IDLE_DELAY = 3.0
AD_DELAY = 0.20
AD_ROUNDS = 3

W = "\033[0m"
R = "\033[31m"
G = "\033[32m"
Y = "\033[33m"
B = "\033[34m"
M = "\033[35m"
C = "\033[36m"

COMMON_HEADERS = {
    "User-Agent": "okhttp/4.12.0",
    "Accept": "application/json",
    "Content-Type": "application/json; charset=UTF-8",
}

AD_URL = "https://googleads.g.doubleclick.net/mads/static/sdk/native/sdk-core-v40.html"


class RequestError(RuntimeError):
    pass


@dataclass
class HttpResponse:
    status_code: int
    text: str


class HttpSession:
    def __init__(self) -> None:
        self.headers: dict[str, str] = {}
        self._opener = build_opener()

    def __enter__(self) -> "HttpSession":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        return None

    def request(self, method: str, url: str, timeout: int = DEFAULT_TIMEOUT, **kwargs: Any) -> HttpResponse:
        headers = dict(self.headers)
        headers.update(kwargs.pop("headers", {}) or {})
        body = kwargs.pop("data", None)
        if "json" in kwargs:
            body = json.dumps(kwargs.pop("json")).encode("utf-8")
        if isinstance(body, str):
            body = body.encode("utf-8")
        req = Request(url, data=body, headers=headers, method=method.upper())
        try:
            with self._opener.open(req, timeout=timeout) as res:
                text = res.read().decode("utf-8", "replace")
                return HttpResponse(getattr(res, "status", 200), text)
        except HTTPError as exc:
            text = exc.read().decode("utf-8", "replace") if exc.fp else str(exc)
            raise RequestError(f"HTTP {exc.code}: {text[:200]}") from exc
        except (URLError, TimeoutError, HTTPException, OSError) as exc:
            raise RequestError(str(exc)) from exc

    def get(self, url: str, timeout: int = DEFAULT_TIMEOUT, **kwargs: Any) -> HttpResponse:
        return self.request("GET", url, timeout=timeout, **kwargs)


@dataclass
class AccountState:
    email: str
    token: str
    user_id: str
    balance: str = "0"
    credits: int = 0


def clear() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def width() -> int:
    return shutil.get_terminal_size((80, 20)).columns


def line(char: str = "=") -> str:
    return char * width()


def center(text: str) -> str:
    return text.center(width())


def banner() -> None:
    clear()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(C + line("=") + W)
    print(M + center(SCRIPT_NAME) + W)
    print(C + center("Fast & stable SlotFruits faucet runner") + W)
    print(Y + center(now) + W)
    print(C + line("=") + W)


def info(text: str, color: str = W) -> None:
    print(f"{color}{text}{W}")


def to_int(value: Any, default: int = 0) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, float)):
        return max(0, int(value))
    if isinstance(value, str):
        digits = "".join(ch for ch in value if ch.isdigit() or ch == "-")
        if digits and digits != "-":
            return max(0, int(digits))
    return default


def deep_get(data: Any, *keys: str) -> Any:
    stack = [data]
    seen: set[int] = set()
    while stack:
        item = stack.pop()
        if id(item) in seen:
            continue
        seen.add(id(item))
        if isinstance(item, dict):
            for key in keys:
                if key in item and item[key] not in (None, ""):
                    return item[key]
            stack.extend(item.values())
        elif isinstance(item, list):
            stack.extend(item)
    return None


def first_value(data: Any, *keys: str, default: Any = None) -> Any:
    value = deep_get(data, *keys)
    return default if value is None else value


def extract_credits(*payloads: Any, fallback: int = 0) -> int:
    credit_keys = (
        "spinAvailable",
        "spin_available",
        "spinsAvailable",
        "spins_available",
        "availableSpin",
        "available_spins",
        "spinCount",
        "spin_count",
        "credits",
        "credit",
        "freeSpin",
        "free_spins",
        "rolls",
    )
    for payload in payloads:
        value = deep_get(payload, *credit_keys)
        if value is not None:
            return to_int(value, fallback)
    return fallback


def extract_balance(*payloads: Any, fallback: str = "0") -> str:
    value = None
    for payload in payloads:
        value = deep_get(payload, "balance", "wallet", "amount", "coins", "coin")
        if value is not None:
            break
    return str(fallback if value is None else value)


def extract_user_id(*payloads: Any) -> str:
    for payload in payloads:
        value = deep_get(payload, "_id", "id", "userId", "user_id", "userid")
        if value is not None:
            return str(value)
    return ""


def extract_token(data: Any) -> str:
    token = deep_get(data, "token", "accessToken", "access_token", "jwt")
    if not token:
        raise RuntimeError("Login başarılı ama token alınamadı.")
    return str(token)


def request_json(session: HttpSession, method: str, url: str, **kwargs: Any) -> dict[str, Any]:
    response = session.request(method, url, timeout=DEFAULT_TIMEOUT, **kwargs)
    if not response.text.strip():
        return {}
    data = json.loads(response.text)
    if isinstance(data, dict):
        return data
    return {"data": data}


def auth_headers(token: str) -> dict[str, str]:
    headers = dict(COMMON_HEADERS)
    headers["Authorization"] = f"Bearer {token}"
    return headers


def login(session: HttpSession, email: str) -> AccountState:
    info("🔐 Login yapılıyor...", Y)
    payload = {"email": email}
    data = request_json(session, "POST", LOGIN_URL, json=payload, headers=COMMON_HEADERS)
    token = extract_token(data)
    user_id = extract_user_id(data)
    state = AccountState(
        email=email,
        token=token,
        user_id=user_id,
        balance=extract_balance(data),
        credits=extract_credits(data),
    )
    refresh_account(session, state)
    return state


def apply_account_payload(state: AccountState, data: dict[str, Any], *, trust_credits: bool = True) -> AccountState:
    state.user_id = state.user_id or extract_user_id(data)
    state.balance = extract_balance(data, fallback=state.balance)
    if trust_credits:
        state.credits = extract_credits(data, fallback=state.credits)
    return state


def refresh_account(session: HttpSession, state: AccountState) -> AccountState:
    # Profile endpoints can be unavailable on some SlotFruits builds.  A failed
    # refresh must never reset the terminal counter to 0, otherwise Termux shows
    # a different spin count than the app.
    urls = []
    if state.user_id:
        urls.append(f"{BASE_URL}/{state.user_id}")
    urls.append(PROFILE_URL)
    for url in urls:
        try:
            data = request_json(session, "GET", url, headers=auth_headers(state.token))
        except RequestError:
            continue
        apply_account_payload(state, data, trust_credits=True)
        return state
    return state


def print_account(state: AccountState) -> None:
    print(C + line("-") + W)
    print(f"{G}Email           : {W}{state.email}")
    print(f"{G}Balance         : {W}{state.balance}")
    print(f"{G}Spin Available  : {W}{state.credits}")
    print(C + line("-") + W)


def spin_once(session: HttpSession, state: AccountState) -> dict[str, Any]:
    # The original script used the earnRoll endpoint directly.  Some server
    # versions accept GET, some accept POST with userId, so try both without
    # dropping the loop on the first method mismatch.
    headers = auth_headers(state.token)
    errors: list[str] = []
    if state.user_id:
        try:
            return request_json(session, "POST", SPIN_URL, json={"userId": state.user_id}, headers=headers)
        except RequestError as exc:
            errors.append(str(exc))
    try:
        return request_json(session, "GET", SPIN_URL, headers=headers)
    except RequestError as exc:
        errors.append(str(exc))
        raise RequestError(" | ".join(errors)) from exc


def should_stop_from_response(data: dict[str, Any]) -> bool:
    status = str(first_value(data, "status", "message", "error", default="")).lower()
    stop_words = ("no spin", "no spins", "not enough", "limit", "finished", "unavailable", "0 spin")
    return any(word in status for word in stop_words)


def spin_loop(session: HttpSession, state: AccountState) -> None:
    total = 0
    while True:
        refresh_account(session, state)
        if state.credits <= 0:
            print_account(state)
            info("⏳ Spin yok; çıkmıyorum, reklam/yenileme döngüsü devam ediyor...", Y)
            ads_loop(session, state.user_id)
            refresh_account(session, state)
            time.sleep(IDLE_DELAY)
            continue

        before = state.credits
        info(f"🎰 Spin deneniyor... Kalan: {before}", Y)
        try:
            data = spin_once(session, state)
        except RequestError as exc:
            info(f"❌ Spin isteği başarısız: {exc}", R)
            time.sleep(1)
            refresh_account(session, state)
            continue

        apply_account_payload(state, data, trust_credits=True)
        refresh_account(session, state)
        response_credits = extract_credits(data, fallback=state.credits)
        if response_credits != state.credits:
            state.credits = min(response_credits, state.credits) if response_credits < before else response_credits
        if state.credits >= before:
            # If the API response omits the updated counter, keep terminal output
            # aligned with the app by consuming exactly one visible spin locally.
            state.credits = max(0, before - 1)

        total += 1
        print_account(state)
        info(f"✔ Spin Done | Bu oturumdaki spin: {total}", G)

        if should_stop_from_response(data):
            state.credits = 0
            continue
        time.sleep(REQUEST_DELAY)


def ads_loop(session: HttpSession, user_id: str) -> None:
    print(C + line("-") + W)
    info("📺 Hızlı reklam ping döngüsü başlıyor...", Y)
    for index in range(1, AD_ROUNDS + 1):
        try:
            parsed = urlparse(AD_URL)
            qs = parse_qs(parsed.query)
            qs["seq_num"] = [str(index)]
            new_url = urlunparse(parsed._replace(query=urlencode(qs, doseq=True)))
            response = session.get(new_url, timeout=DEFAULT_TIMEOUT)
            if response.status_code < 400:
                info(f"✔ Ads ping {index}/{AD_ROUNDS}", G)
            else:
                info(f"⚠ Ads ping {index}/{AD_ROUNDS}: HTTP {response.status_code}", Y)
        except RequestError as exc:
            info(f"⚠ Ads ping {index}/{AD_ROUNDS}: {exc}", Y)
        time.sleep(AD_DELAY)


def main() -> int:
    banner()
    email = input(f"{C}FaucetPay email: {W}").strip()
    if not email or "@" not in email:
        info("❌ Geçerli bir email gir.", R)
        return 1

    with HttpSession() as session:
        session.headers.update(COMMON_HEADERS)
        try:
            state = login(session, email)
        except (RequestError, RuntimeError, ValueError) as exc:
            info(f"❌ Login başarısız: {exc}", R)
            return 1

        print_account(state)
        ads_loop(session, state.user_id)
        spin_loop(session, state)

    return 0


if __name__ == "__main__":
    sys.exit(main())
