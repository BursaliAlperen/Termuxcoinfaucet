#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# AlperenTheCreator ✅ TAMAM

import asyncio
import os
import random
import re
import sys
import urllib.parse
from datetime import datetime

import aiohttp
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.messages import RequestWebViewRequest

API_ID = 1585960
API_HASH = "07234bf217bf52a1c29b610532af3d1f"
BOT_USERNAME = "taskcryptorewards_bot"
WEBAPP_URL = "https://appkviz.com/app"
YENI_API_KEY = "bypassallshortlink"


class C:
    G = "\033[92m"
    Y = "\033[93m"
    C = "\033[96m"
    R = "\033[91m"
    X = "\033[0m"


def clear():
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()


def _renksiz_uzunluk(text):
    return len(re.sub(r"\033\[[0-9;]*m", "", text))


def _satir(text, width):
    temiz = _renksiz_uzunluk(text)
    bosluk = max(width - temiz - 2, 0)
    return f"┃{text}{' ' * bosluk}┃"


def banner():
    clear()
    width = min(os.get_terminal_size().columns, 90)
    line = "━" * (width - 2)
    print(f"{C.G}┏{line}┓{C.X}")
    print(_satir(f"{C.Y}      ❯ AlperenTheCreator ✅ TAMAM ❮{C.X}", width))
    print(_satir("========================================", width))
    print(_satir("AlperenTheCreator ✅ TAMAM", width))
    print(_satir("========================================", width))
    print(_satir("", width))
    for row in [
        "              ███╗   ██╗██╗   ██╗██╗   ██╗██╗   ██╗██╗",
        "              ████╗  ██║██║   ██║╚██╗ ██╔╝██║   ██║██║",
        "              ██╔██╗ ██║██║   ██║ ╚████╔╝ ██║   ██║██║",
        "              ██║╚██╗██║██║   ██║  ╚██╔╝  ██║   ██║██║",
        "              ██║ ╚████║╚██████╔╝   ██║   ╚██████╔╝███████╗",
        "              ╚═╝  ╚═══╝ ╚═════╝    ╚═╝    ╚═════╝ ╚══════╝",
    ]:
        print(_satir(f"{C.C}{row}{C.X}", width))
    print(_satir(f"{C.Y}❯❯❯ WEBSİTE & TELEGRAM MINI APP OTOMATİK FARM SCRIPTİ ❮❮❮{C.X}", width))
    print(f"{C.G}┗{line}┛{C.X}")


def dashboard(balance, today_act, max_act, current_status):
    width = min(os.get_terminal_size().columns, 90)
    line = "━" * (width - 2)
    print(f"{C.G}┏{line}┓{C.X}")
    print(_satir(f"{C.Y}  GÖSTERGE PANELİ{C.X}", width))
    print(f"{C.G}┣{line}┫{C.X}")
    print(_satir(f"  Geliştirici : {C.C}AlperenTheCreator{C.X}", width))
    print(_satir(f"  Kanal       : {C.C}t.me/teamnuyul{C.X}", width))
    print(_satir(f"  Bakiye      : {C.G}{balance}{C.X}", width))
    print(_satir(f"  Aktivite    : {C.Y}{today_act}/{max_act}{C.X}", width))
    print(_satir(f"  Durum       : {current_status}", width))
    print(f"{C.G}┗{line}┛{C.X}")


def log_msg(msg, type="info"):
    now = datetime.now().strftime("%H:%M:%S")
    if type == "success":
        prefix = f"{C.G}[+]{C.X}"
    elif type == "error":
        prefix = f"{C.R}[!]{C.X}"
    else:
        prefix = f"{C.Y}[*]{C.X}"
    print(f"{C.C}[{now}]{C.X} {prefix} {msg}")


async def get_tg_init_data(silent=False, session_name="appkviz_session"):
    if not silent:
        banner()
        log_msg("Telegram kimlik doğrulaması başlatılıyor...")
    client = TelegramClient(session_name, API_ID, API_HASH)
    try:
        await client.connect()
    except Exception as e:
        log_msg(f"Telegram bağlantısı başarısız: {e}", "error")
        return None

    if not await client.is_user_authorized():
        log_msg("Telegram oturumu yok! Yeniden giriş gerekiyor...", "error")
        phone = input(f"{C.Y}Telefon numarası (Örnek: +905xxx): {C.X}")
        try:
            await client.send_code_request(phone)
            otp = input(f"{C.Y}OTP kodu: {C.X}")
            try:
                await client.sign_in(phone, otp)
            except SessionPasswordNeededError:
                two_fa = input(f"{C.Y}2FA şifresi (varsa): {C.X}")
                await client.sign_in(password=two_fa)
        except Exception as e:
            log_msg(f"Giriş başarısız: {e}", "error")
            await client.disconnect()
            return None
        log_msg("Giriş başarılı (oturum otomatik kaydedildi).", "success")

    try:
        webapp_result = await client(RequestWebViewRequest(
            peer=BOT_USERNAME,
            bot=BOT_USERNAME,
            platform="android",
            url=WEBAPP_URL,
        ))
        query_string = webapp_result.url.split("#tgWebAppData=", 1)[1].split("&tgWebAppVersion", 1)[0]
        init_data = urllib.parse.unquote(query_string)
        await client.disconnect()
        return init_data
    except Exception as e:
        log_msg(f"WebApp verisi alınamadı: {e}", "error")
        await client.disconnect()
        return None


class AppKvizFarmer:
    def __init__(self, init_data, session):
        self.session = session
        self.init_data = init_data
        self.base_url = "https://appkviz.com/api"
        self.headers = {
            "sec-ch-ua-platform": "Android",
            "user-agent": "Mozilla/5.0 (Linux; Android 15; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.7680.153 Mobile Safari/537.36 Telegram-Android/12.1.1",
            "accept": "*/*",
            "content-type": "application/json",
            "platform": "android",
            "origin": "https://appkviz.com",
            "x-requested-with": "org.telegram.messenger",
            "referer": "https://appkviz.com/app",
            "authorization": init_data,
        }

    def update_auth(self, new_init_data):
        self.init_data = new_init_data
        self.headers["authorization"] = new_init_data

    async def login(self):
        url = self.base_url + "/user/auth/telegram"
        async with self.session.post(url, headers=self.headers, json={"platform": "android"}) as res:
            data = await res.json(content_type=None)
            return res.status == 200 and data.get("success"), data.get("data")

    async def get_state(self):
        url = self.base_url + "/user/state"
        async with self.session.get(url, headers=self.headers) as res:
            data = await res.json(content_type=None)
            return data.get("data") if res.status == 200 and data.get("success") else None

    async def get_news(self):
        url = self.base_url + "/user/news?user_id=0&page=1&limit=50"
        async with self.session.get(url, headers=self.headers) as res:
            data = await res.json(content_type=None)
            return data.get("data") if res.status == 200 and data.get("success") else []

    async def init_task(self, news_id):
        url = self.base_url + f"/user/news/{news_id}/init"
        async with self.session.post(url, headers=self.headers, json={"newsId": news_id}) as res:
            return await res.json(content_type=None)

    async def confirm_ad(self, token):
        url = self.base_url + "/user/ad-proofs/confirm"
        payload = {"provider": YENI_API_KEY, "apiKey": YENI_API_KEY, "token": token}
        async with self.session.post(url, headers=self.headers, json=payload) as res:
            data = await res.json(content_type=None)
            return data.get("success"), data

    async def complete_task(self, news_id, token):
        url = self.base_url + f"/user/news/{news_id}/complete"
        payload = {"newsId": news_id, "token": token, "apiKey": YENI_API_KEY}
        async with self.session.post(url, headers=self.headers, json=payload) as res:
            return await res.json(content_type=None)


async def main():
    init_data = await get_tg_init_data()
    if not init_data:
        log_msg("Kimlik doğrulama başarısız. Program durduruldu.", "error")
        sys.exit(1)

    async with aiohttp.ClientSession() as session:
        farmer = AppKvizFarmer(init_data, session)
        ok, auth_data = await farmer.login()
        if not ok:
            log_msg("API giriş durumu: başarısız > Script durduruldu.", "error")
            return

        while True:
            state = await farmer.get_state()
            if not state:
                log_msg("Güncel durum alınamadı. Token süresi dolmuş veya ağ kesilmiş olabilir.", "error")
                log_msg("Otomatik yeniden bağlantı başlatılıyor...")
                new_init_data = await get_tg_init_data(silent=True)
                if new_init_data:
                    farmer.update_auth(new_init_data)
                    await farmer.login()
                    log_msg("Otomatik yeniden bağlantı ve giriş başarılı!", "success")
                    continue
                log_msg("Yeniden bağlantı başarısız. 10 saniye sonra tekrar denenecek...", "error")
                await asyncio.sleep(10)
                continue

            user = state.get("user", {})
            settings = state.get("settings", {})
            balance = user.get("balance", 0)
            today_act = user.get("todayActivities", 0)
            max_act = settings.get("daily_limit_views", 0)
            cooldown = int(settings.get("news_task_cooldown_seconds", 30))
            banner()
            dashboard(balance, today_act, max_act, f"{C.G}Çalışıyor{C.X}")
            log_msg("Haber görevleri kontrol ediliyor...")

            if max_act and today_act >= max_act:
                log_msg("Günlük limit doldu! Otomatik durduruldu.", "success")
                return

            news_list = await farmer.get_news()
            tasks_processed = 0
            for news in news_list or []:
                if news.get("completed"):
                    continue
                news_id = news.get("id")
                title = (news.get("title") or "")[:60]
                if len(news.get("title") or "") > 60:
                    title += "..."
                log_msg(f"Görev ID {news_id} işleniyor. Hedef: {title}")
                init_res = await farmer.init_task(news_id)
                if init_res.get("needsCaptcha") or not init_res.get("adSessionToken"):
                    log_msg("Görev captcha istiyor veya başlatılamadı. Atlanıyor!", "error")
                    continue
                token = init_res.get("adSessionToken")
                log_msg("Reklam kanıtı onayı gönderiliyor...")
                confirmed, _ = await farmer.confirm_ad(token)
                if not confirmed:
                    log_msg("Reklam onayı başarısız. Atlanıyor!", "error")
                    continue
                comp_res = await farmer.complete_task(news_id, token)
                if comp_res.get("success"):
                    log_msg(f"Görev ID {news_id} ödülü başarıyla alındı!", "success")
                    tasks_processed += 1
                    for remaining in range(cooldown, 0, -1):
                        sys.stdout.write(f"\r{C.Y}[*]{C.X} Bekleme aktif: {remaining} saniye kaldı...   ")
                        sys.stdout.flush()
                        await asyncio.sleep(1)
                    print(f"\r{C.G}[+]{C.X} Bekleme bitti! Yeni veriler yükleniyor...          ")
                    break
                log_msg("Görev tamamlanamadı. Atlanıyor!", "error")

            if tasks_processed == 0:
                loop_time = random.randint(15, 30)
                log_msg("Şu anda yeni görev yok.")
                for remaining in range(loop_time, 0, -1):
                    sys.stdout.write(f"\r{C.Y}[*]{C.X} Dinlenme: {remaining} saniye sonra tekrar kontrol...   ")
                    sys.stdout.flush()
                    await asyncio.sleep(1)
                print("\r" + " " * 70 + "\r", end="")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{C.R}[!] Program kullanıcı tarafından zorla durduruldu.{C.X}")
        sys.exit(0)
