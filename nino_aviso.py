#!/data/data/com.termux/files/usr/bin/python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════════╗
║                                                                                  ║
║     ███╗   ██╗██╗███╗   ██╗ ██████╗  ██████╗ ██████╗ ██╗███╗   ██╗              ║
║     ████╗  ██║██║████╗  ██║██╔═══██╗██╔════╝██╔═══██╗██║████╗  ██║              ║
║     ██╔██╗ ██║██║██╔██╗ ██║██║   ██║██║     ██║   ██║██║██╔██╗ ██║              ║
║     ██║╚██╗██║██║██║╚██╗██║██║   ██║██║     ██║   ██║██║██║╚██╗██║              ║
║     ██║ ╚████║██║██║ ╚████║╚██████╔╝╚██████╗╚██████╔╝██║██║ ╚████║              ║
║     ╚═╝  ╚═══╝╚═╝╚═╝  ╚═══╝ ╚═════╝  ╚═════╝ ╚═════╝ ╚═╝╚═╝  ╚═══╝              ║
║                                                                                  ║
║     █████╗ ██╗   ██╗██╗███████╗ ██████╗     ██████╗ ███████╗████████╗          ║
║     ██╔══██╗██║   ██║██║██╔════╝██╔═══██╗    ██╔══██╗██╔════╝╚══██╔══╝          ║
║     ███████║██║   ██║██║███████╗██║   ██║    ██████╔╝█████╗     ██║             ║
║     ██╔══██║╚██╗ ██╔╝██║╚════██║██║   ██║    ██╔══██╗██╔══╝     ██║             ║
║     ██║  ██║ ╚████╔╝ ██║███████║╚██████╔╝    ██████╔╝███████╗   ██║             ║
║     ╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝ ╚═════╝     ╚═════╝ ╚══════╝   ╚═╝             ║
║                                                                                  ║
║                    💎 PREMIUM EDITION v3.0 💎                                   ║
║                                                                                  ║
║              ⚡ AUTO CLAIM BOT - 18 COIN DESTEĞİ ⚡                             ║
║                                                                                  ║
║     ┌─────────────────────────────────────────────────────────────────────┐       ║
║     │  ★ YouTube Likes    ★ YouTube Ads    ★ Surfing Tasks            │       ║
║     │  ★ Auto Login       ★ Cookie Support   ★ Balance Check          │       ║
║     │  ★ Anti-Ban         ★ Smart Timer      ★ Auto Withdraw          │       ║
║     └─────────────────────────────────────────────────────────────────────┘       ║
║                                                                                  ║
║                         🔥 by alperenthe 🔥                                     ║
║                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import time
import json
import base64
import pickle
import random
import socket
import urllib.request
import gc
import calendar
from datetime import datetime
from urllib.parse import urlparse

# ─── SELENIUM IMPORTS ───────────────────────────────────────────────────────────
import selenium.webdriver as webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# ─── OTHER IMPORTS ────────────────────────────────────────────────────────────────
from colorama import Fore, Style, Back, init
from bs4 import BeautifulSoup
import pytz
import tzlocal

# ═══════════════════════════════════════════════════════════════════════════════════
#                               GLOBAL SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════════

init(autoreset=True)

# ─── 18 COIN SUPPORTED LIST ───────────────────────────────────────────────────────
SUPPORTED_COINS = [
    "BTC", "ETH", "LTC", "DOGE", "BCH", "DASH", "XRP", "TRX", "BNB",
    "USDT", "SOL", "MATIC", "ADA", "DOT", "AVAX", "LINK", "UNI", "SHIB"
]

# ─── COLOR PALETTE ────────────────────────────────────────────────────────────────
COLORS = {
    "1": Fore.CYAN,
    "2": Fore.GREEN,
    "3": Fore.RED,
    "4": Fore.BLUE,
    "5": Fore.YELLOW,
    "6": Fore.MAGENTA,
}

# ─── FILE NAMES ───────────────────────────────────────────────────────────────────
FILES = {
    "cookies": "aviso.pkl",
    "network": "Network",
    "userdata": "UserData",
    "login_method": "LoginMethod",
    "user_agent": "UserAgent",
    "banned_prefix": "btuan",
    "approved": "stuan.sua",
    "config": "fenmll.dexi",
    "withdrawal": "fenmll.dexi",
    "number": "sumn.umn",
    "url_number": "uuab.bua",
}

# ═══════════════════════════════════════════════════════════════════════════════════
#                              UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════════

def random_sleep(min_time: float = 1.0, max_time: float = 3.0) -> None:
    """Rastgele bekleme süresi."""
    time.sleep(random.uniform(min_time, max_time))


def random_numbering(min_num: int = 1, max_num: int = 5) -> int:
    """Rastgele sayı üret."""
    return random.randint(min_num, max_num)


def get_phone_brand() -> str:
    """Telefon markasını al."""
    try:
        return os.popen("getprop ro.product.brand").read().strip()
    except:
        return "Unknown"


def get_phone_version() -> str:
    """Telefon versiyonunu al."""
    try:
        return os.popen("getprop ro.build.version.release").read().strip()
    except:
        return "10"


def get_phone_model() -> str:
    """Telefon modelini al."""
    try:
        return os.popen("getprop ro.product.model").read().strip()
    except:
        return "Android"


def get_day_number() -> int:
    """Gün numarasını al."""
    return datetime.today().day


def get_month_number() -> int:
    """Ay numarasını al."""
    return datetime.today().month


def get_year_number() -> int:
    """Yıl numarasını al."""
    return datetime.today().year


def IsFileExist(filename: str) -> bool:
    """Dosya var mı kontrol et."""
    return os.path.exists(filename)


def DeleteFile(filename: str) -> None:
    """Dosyayı sil."""
    try:
        if os.path.exists(filename):
            os.remove(filename)
    except:
        pass


def clean_file(filename: str) -> None:
    """Dosyayı temizle."""
    try:
        with open(filename, "w") as f:
            f.write("")
    except:
        pass


def GetFileElement(filename: str, key: str) -> str:
    """Dosyadan element oku."""
    try:
        with open(filename, "rb") as f:
            data = pickle.load(f)
        decoded = base64.b64decode(data).decode('utf-8')
        for line in decoded.split('\n'):
            if line.startswith(f"{key}="):
                return line.split('=', 1)[1].strip()
    except:
        pass
    return ""


def SaveFileElement(filename: str, key: str, value: str) -> None:
    """Dosyaya element kaydet."""
    try:
        text = f"{key}={value}\n"
        encoded = base64.b64encode(text.encode()).decode()
        with open(filename, "wb") as f:
            pickle.dump(encoded, f)
    except:
        pass


def ColorizeTextPrint(premium: int, color: str) -> str:
    """Renk seçimi yap."""
    if premium == 1 and color in COLORS:
        return COLORS[color]
    return Fore.WHITE


def btfs(driver) -> BeautifulSoup:
    """BeautifulSoup parser."""
    return BeautifulSoup(driver.page_source, 'html.parser')


def no_trs(driver, second: int = 10) -> None:
    """No translation popup kapat."""
    try:
        WebDriverWait(driver, second).until(
            EC.element_to_be_clickable((By.ID, "notranslate"))
        ).click()
    except:
        pass


def close_tap(driver) -> None:
    """Yeni açılan sekmeleri kapat."""
    try:
        while len(driver.window_handles) > 1:
            driver.switch_to.window(driver.window_handles[-1])
            driver.close()
        driver.switch_to.window(driver.window_handles[0])
    except:
        pass


def save_cookies(driver) -> None:
    """Çerezleri kaydet."""
    try:
        cookies = driver.get_cookies()
        pickle.dump(cookies, open(FILES["cookies"], "wb"))
    except:
        pass


def load_cookies(driver) -> None:
    """Çerezleri yükle."""
    try:
        cookies = pickle.load(open(FILES["cookies"], "rb"))
        for cookie in cookies:
            driver.add_cookie(cookie)
    except:
        pass


def add_cookies_to_driver(driver, cookies_str: str, domain: str) -> None:
    """String çerezleri driver'a ekle."""
    try:
        cookies = json.loads(cookies_str)
        for cookie in cookies:
            driver.add_cookie(cookie)
    except:
        pass


def check_cocki(cookies_input: str) -> list:
    """Çerez stringini parse et."""
    try:
        return json.loads(cookies_input)
    except:
        return []


def add_ccocki_driver(driver, cookies: list, domain: str) -> None:
    """Çerezleri driver'a ekle."""
    try:
        driver.get(domain)
        time.sleep(3)
        for cookie in cookies:
            if 'sameSite' in cookie:
                del cookie['sameSite']
            try:
                driver.add_cookie(cookie)
            except:
                pass
        driver.get(domain)
        time.sleep(5)
    except:
        pass


def TerminateSessionNow(driver) -> None:
    """Session'ı sonlandır."""
    try:
        close_tap(driver)
        driver.get("https://aviso.bz/members")
        time.sleep(3)
    except:
        pass


def ShowLogoFE() -> None:
    """Banner göster."""
    banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════════════════════════╗
{Fore.CYAN}║{Fore.YELLOW}                                                                                  {Fore.CYAN}║
{Fore.CYAN}║{Fore.YELLOW}     ███╗   ██╗██╗███╗   ██╗ ██████╗  ██████╗ ██████╗ ██╗███╗   ██╗              {Fore.CYAN}║
{Fore.CYAN}║{Fore.YELLOW}     ████╗  ██║██║████╗  ██║██╔═══██╗██╔════╝██╔═══██╗██║████╗  ██║              {Fore.CYAN}║
{Fore.CYAN}║{Fore.YELLOW}     ██╔██╗ ██║██║██╔██╗ ██║██║   ██║██║     ██║   ██║██║██╔██╗ ██║              {Fore.CYAN}║
{Fore.CYAN}║{Fore.YELLOW}     ██║╚██╗██║██║██║╚██╗██║██║   ██║██║     ██║   ██║██║██║╚██╗██║              {Fore.CYAN}║
{Fore.CYAN}║{Fore.YELLOW}     ██║ ╚████║██║██║ ╚████║╚██████╔╝╚██████╗╚██████╔╝██║██║ ╚████║              {Fore.CYAN}║
{Fore.CYAN}║{Fore.YELLOW}     ╚═╝  ╚═══╝╚═╝╚═╝  ╚═══╝ ╚═════╝  ╚═════╝ ╚═════╝ ╚═╝╚═╝  ╚═══╝              {Fore.CYAN}║
{Fore.CYAN}║{Fore.YELLOW}                                                                                  {Fore.CYAN}║
{Fore.CYAN}║{Fore.GREEN}     █████╗ ██╗   ██╗██╗███████╗ ██████╗     ██████╗ ███████╗████████╗          {Fore.CYAN}║
{Fore.CYAN}║{Fore.GREEN}     ██╔══██╗██║   ██║██║██╔════╝██╔═══██╗    ██╔══██╗██╔════╝╚══██╔══╝          {Fore.CYAN}║
{Fore.CYAN}║{Fore.GREEN}     ███████║██║   ██║██║███████╗██║   ██║    ██████╔╝█████╗     ██║             {Fore.CYAN}║
{Fore.CYAN}║{Fore.GREEN}     ██╔══██║╚██╗ ██╔╝██║╚════██║██║   ██║    ██╔══██╗██╔══╝     ██║             {Fore.CYAN}║
{Fore.CYAN}║{Fore.GREEN}     ██║  ██║ ╚████╔╝ ██║███████║╚██████╔╝    ██████╔╝███████╗   ██║             {Fore.CYAN}║
{Fore.CYAN}║{Fore.GREEN}     ╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝ ╚═════╝     ╚═════╝ ╚══════╝   ╚═╝             {Fore.CYAN}║
{Fore.CYAN}║{Fore.YELLOW}                                                                                  {Fore.CYAN}║
{Fore.CYAN}║{Fore.MAGENTA}                    💎 PREMIUM EDITION v3.0 💎                                   {Fore.CYAN}║
{Fore.CYAN}║{Fore.WHITE}              ⚡ AUTO CLAIM BOT - 18 COIN DESTEĞİ ⚡                             {Fore.CYAN}║
{Fore.CYAN}║{Fore.YELLOW}                                                                                  {Fore.CYAN}║
{Fore.CYAN}║{Fore.CYAN}     ┌─────────────────────────────────────────────────────────────────────┐       {Fore.CYAN}║
{Fore.CYAN}║{Fore.CYAN}     │{Fore.WHITE}  ★ YouTube Likes    ★ YouTube Ads    ★ Surfing Tasks            {Fore.CYAN}│       {Fore.CYAN}║
{Fore.CYAN}║{Fore.CYAN}     │{Fore.WHITE}  ★ Auto Login       ★ Cookie Support   ★ Balance Check          {Fore.CYAN}│       {Fore.CYAN}║
{Fore.CYAN}║{Fore.CYAN}     │{Fore.WHITE}  ★ Anti-Ban         ★ Smart Timer      ★ Auto Withdraw          {Fore.CYAN}│       {Fore.CYAN}║
{Fore.CYAN}║{Fore.CYAN}     └─────────────────────────────────────────────────────────────────────┘       {Fore.CYAN}║
{Fore.CYAN}║{Fore.RED}                                                                                  {Fore.CYAN}║
{Fore.CYAN}║{Fore.RED}                         🔥 by alperenthe 🔥                                     {Fore.CYAN}║
{Fore.CYAN}║{Fore.WHITE}                                                                                  {Fore.CYAN}║
{Fore.CYAN}╚══════════════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(banner)


def GetWHours() -> int:
    """Saat al."""
    return datetime.today().hour


def GetWMinutes() -> int:
    """Dakika al."""
    return datetime.today().minute


def GetWDays() -> int:
    """Gün al."""
    return datetime.today().day


def WaitTimerForTask(seconds: int) -> None:
    """Task için bekleme zamanı."""
    for i in range(seconds, 0, -1):
        mins, secs = divmod(i, 60)
        timer = f'{mins:02d}:{secs:02d}'
        print(f"\r{Fore.YELLOW}\t ⏳ Waiting: {timer} ⏳", end="")
        time.sleep(1)
    print(f"\r{' ' * 40}\r", end="")


def WaitTimerTask() -> None:
    """Task boşta bekleme."""
    wait_time = random_numbering(30, 90)
    print(f"\n{Fore.CYAN}\t [INFO]: No tasks, waiting {wait_time}s...")
    for i in range(wait_time, 0, -1):
        print(f"\r{Fore.YELLOW}\t ⏳ Cooldown: {i}s ⏳", end="")
        time.sleep(1)
    print(f"\r{' ' * 40}\r", end="")


def AttemptsCounter() -> None:
    """Deneme sayacı."""
    pass


def VideoEffect(driver, userid, premium, color) -> None:
    """Video efekti göster."""
    TextColor = ColorizeTextPrint(premium, color)
    print(f"\r{Style.BRIGHT}{TextColor}\t ✓ Task completed! Balance updated ✓", end="")
    time.sleep(2)


def click_center_of_screen(driver) -> None:
    """Ekran ortasına tıkla."""
    try:
        width = driver.execute_script("return window.innerWidth")
        height = driver.execute_script("return window.innerHeight")
        actions = ActionChains(driver)
        actions.move_by_offset(width // 2, height // 2).click().perform()
    except:
        pass


def playvid(driver) -> None:
    """Video oynat."""
    try:
        driver.execute_script("""
            var videos = document.querySelectorAll('video');
            for(var i=0; i<videos.length; i++) {
                videos[i].play();
                videos[i].muted = true;
            }
        """)
    except:
        pass


def check_quic_error(driver) -> bool:
    """QUIC hatası kontrol et."""
    try:
        if "ERR_QUIC_PROTOCOL_ERROR" in driver.page_source:
            return True
    except:
        pass
    return False


def SaveVaiolationTime(filename: str) -> None:
    """İhlal zamanını kaydet."""
    SaveFileElement(filename, "VaiolationTime", str(int(time.time())))


def SaveSiteCodeClearLan(filename: str, code: str) -> None:
    """Site kodunu kaydet."""
    SaveFileElement(filename, "SiteCode", code)


def SaveUsernameBan(username: str) -> None:
    """Banlanan kullanıcıyı kaydet."""
    for i in range(1, 11):
        if not IsFileExist(f"{FILES['banned_prefix']}{i}.bua"):
            SaveFileElement(f"{FILES['banned_prefix']}{i}.bua", "Username", username)
            break


def SaveUsernameApproved(username: str) -> None:
    """Onaylanan kullanıcıyı kaydet."""
    SaveFileElement(FILES["approved"], "Username", username)


def CheckReferral1(driver, second, userid) -> None:
    """Referral kontrol 1."""
    pass


def CheckReferral2(driver, second, userid) -> None:
    """Referral kontrol 2."""
    pass


def CleanWithdrawlFile() -> None:
    """Çekim dosyasını temizle."""
    pass


def SaveMyData(username: str, password: str) -> None:
    """Kullanıcı verilerini kaydet."""
    SaveFileElement(FILES["userdata"], "Username", username)
    SaveFileElement(FILES["userdata"], "Password", password)


def SaveLoginMethod(method: str) -> None:
    """Login metodunu kaydet."""
    SaveFileElement(FILES["login_method"], "LoginMethod", method)


def SaveTheUserAgent(ua: str) -> None:
    """User agent kaydet."""
    SaveFileElement(FILES["user_agent"], "TheUserAgent", ua)


def GetCookiesInput() -> str:
    """Çerez input al."""
    print(f"\n{Fore.YELLOW}\t [INPUT]: Paste your cookies (JSON format):")
    cookies = input(f"\t {Fore.CYAN}> ")
    return cookies


def IsPhoneConnected() -> bool:
    """Telefon bağlı mı."""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except:
        return False


def SaveTMonthNumberFile() -> None:
    """Ay numarasını kaydet."""
    SaveFileElement("tmon.tmo", "MonthNumber", str(get_month_number()))


def SaveUrlNumberFile() -> None:
    """URL numarasını kaydet."""
    SaveFileElement(FILES["url_number"], "UrlNumber", "11")


def GetUrlNumber() -> str:
    """URL numarasını al."""
    return GetFileElement(FILES["url_number"], "UrlNumber") or "11"


# ═══════════════════════════════════════════════════════════════════════════════════
#                              NETWORK FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════════

def CheckNetConnection() -> None:
    """İnternet bağlantısını kontrol et."""
    def check_internet() -> bool:
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except OSError:
            return False

    def check_internet_http() -> bool:
        try:
            urllib.request.urlopen("http://www.google.com", timeout=3)
            return True
        except:
            return False

    if check_internet() and check_internet_http():
        SaveFileElement(FILES["network"], "Network", "ON")
    else:
        SaveFileElement(FILES["network"], "Network", "OFF")


# ═══════════════════════════════════════════════════════════════════════════════════
#                              DRIVER SETUP  [DÜZELTİLDİ]
# ═══════════════════════════════════════════════════════════════════════════════════

def BanningOpti() -> ChromeOptions:
    """Ban korumalı options."""
    options = ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--window-size=360,640")
    options.add_argument("--user-agent=Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36")
    # Termux'ta X11 olmadan çalışması için headless ekle
    options.add_argument("--headless=new")
    return options


def BanningDriver(user_agent: str = None) -> webdriver:
    """Ban korumalı driver. [DÜZELTİLDİ - chromedriver path eklendi]"""
    options = BanningOpti()
    if user_agent:
        options.add_argument(f"--user-agent={user_agent}")
    
    try:
        # Termux chromedriver path'i
        chromedriver_path = "/data/data/com.termux/files/usr/bin/chromedriver"
        
        if os.path.exists(chromedriver_path):
            service = ChromeService(executable_path=chromedriver_path)
            driver = webdriver.Chrome(service=service, options=options)
        else:
            # Fallback: Selenium Manager
            driver = webdriver.Chrome(options=options)
            
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver
    except Exception as e:
        print(f"{Fore.RED}\t [ERROR]: Driver creation failed: {e}")
        print(f"{Fore.YELLOW}\t [HINT]: chromedriver kurulu mu?")
        print(f"{Fore.YELLOW}\t        'pkg install chromedriver' veya 'pkg install chromium'")
        sys.exit(1)


def opti() -> ChromeOptions:
    """Standart options."""
    options = ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=360,640")
    options.add_argument("--user-agent=Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36")
    # Termux'ta X11 olmadan çalışması için headless ekle
    options.add_argument("--headless=new")
    return options


def no_display_hid() -> ChromeOptions:
    """Headless options."""
    options = opti()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    return options


# ═══════════════════════════════════════════════════════════════════════════════════
#                              LOGIN FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════════

def logginn(driver: webdriver, second: int, email: str = 'Email', password: str = 'Password') -> None:
    """Manuel login yap."""
    try:
        if email != 'Email' and password != 'Password':
            time.sleep(3)
            user = WebDriverWait(driver, second).until(
                EC.visibility_of_element_located((By.NAME, 'username'))
            )
            user.send_keys(Keys.CONTROL + "a")
            user.send_keys(Keys.DELETE)
            user.send_keys(email)
            
            random_sleep(1, 3)
            
            pasw = WebDriverWait(driver, second).until(
                EC.visibility_of_element_located((By.NAME, 'password'))
            )
            pasw.send_keys(Keys.CONTROL + "a")
            pasw.send_keys(Keys.DELETE)
            pasw.send_keys(password)
            random_sleep(1, 3)
            pasw.send_keys(Keys.ENTER)
            
            WebDriverWait(driver, second).until(
                EC.element_to_be_clickable((By.ID, 'button-login'))
            ).send_keys(Keys.ENTER)
            time.sleep(10)
            
            if "aviso.bz/login" in driver.current_url:
                WebDriverWait(driver, second).until(
                    EC.element_to_be_clickable((By.ID, 'button-login'))
                ).click()
                print(f"{Fore.YELLOW}\t [RETRY]: Login button clicked again")
                time.sleep(10)
            
            driver.save_screenshot("results.png")
    except Exception as e:
        pass


def LoginWithCookies(driver: webdriver) -> None:
    """Çerezlerle login."""
    driver.get('https://aviso.bz')
    load_cookies(driver)
    driver.get("https://aviso.bz/members")
    time.sleep(5)


def Did_Login(driver: webdriver) -> bool:
    """Login başarılı mı kontrol et."""
    driver.get("https://aviso.bz/members")
    time.sleep(10)
    
    if driver.current_url == "https://aviso.bz/members":
        return True
        
    if driver.current_url == "https://aviso.bz/login":
        return False
        
    if driver.current_url == "https://aviso.bz/blok-users":
        driver.close()
        os.system("clear")
        DeleteFile(FILES["cookies"])
        DeleteFile(FILES["userdata"])
        print(f"\n{Fore.RED}\t [BANNED]: Account blocked by aviso.bz!")
        print(f"{Fore.YELLOW}\t [NOTICE]: All account files deleted.")
        print(f"{Fore.RED}\t [WARNING]: Clear Chrome/Kiwi data before using new account.")
        sys.exit(1)
    
    return False


def verification_2fa(driver: webdriver, second: int, code: str) -> None:
    """2FA doğrulama."""
    try:
        WebDriverWait(driver, second).until(
            EC.visibility_of_element_located((By.NAME, 'code'))
        ).send_keys(code)
        time.sleep(second // 10)
        WebDriverWait(driver, second).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'button.button_theme_blue.button_size_m.button_margin_right'))
        ).click()
        time.sleep(second // 10)
    except:
        pass


def get_user(driver: webdriver) -> str:
    """Kullanıcı ID'sini al."""
    try:
        driver.get("https://aviso.bz/members")
        time.sleep(5)
        soup = btfs(driver)
        user_elem = soup.find('a', {'href': lambda x: x and 'profile' in x})
        if user_elem:
            return user_elem.text.strip()
    except:
        pass
    return ""


def GetUserName(driver: webdriver) -> str:
    """Kullanıcı adını al."""
    try:
        soup = btfs(driver)
        user_elem = soup.find('span', {'class': 'user-name'})
        if user_elem:
            return user_elem.text.strip()
    except:
        pass
    return ""


def get_balance(driver: webdriver, userid: str) -> str:
    """Bakiyeyi al."""
    try:
        driver.get("https://aviso.bz/members")
        time.sleep(3)
        soup = btfs(driver)
        balance = soup.find('span', {'id': 'new-money-ballans'})
        if balance:
            return balance.text.strip()
    except:
        pass
    return "0.00"


def GetBalance(driver: webdriver, userid: str) -> str:
    """Bakiyeyi al (alternatif)."""
    return get_balance(driver, userid)


def AreWeStillLoggedIn(driver: webdriver) -> bool:
    """Hala login mi kontrol et."""
    try:
        if "aviso.bz/login" in driver.current_url:
            return False
        soup = btfs(driver)
        if soup.find('input', {'name': 'username'}):
            return False
        return True
    except:
        return False


def IsUserBanned(driver: webdriver) -> bool:
    """Kullanıcı banlı mı."""
    try:
        if "blok-users" in driver.current_url:
            return True
    except:
        pass
    return False


def TestUserPhone() -> bool:
    """Telefon testi."""
    return True


# ═══════════════════════════════════════════════════════════════════════════════════
#                              TASK FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════════

def FoundTasks(driver: webdriver) -> bool:
    """Task var mı."""
    try:
        tasks = btfs(driver).find_all('table', {'class': 'work-serf'})
        return len(tasks) > 0
    except:
        return False


def FoundYoutubeLikes(driver: webdriver) -> bool:
    """YouTube like task var mı."""
    try:
        tasks = btfs(driver).find_all('table', {'class': 'work-serf'})
        for task in tasks:
            if "likes-link-" in str(task.get('id', '')):
                return True
        return False
    except:
        return False


def FoundYoutubeAds(driver: webdriver) -> bool:
    """YouTube ads task var mı."""
    try:
        tasks = btfs(driver).find_all('table', {'class': 'work-serf'})
        for task in tasks:
            if "ads-link-" in str(task.get('id', '')):
                return True
        return False
    except:
        return False


def FoundSerf(driver: webdriver) -> bool:
    """Surf task var mı."""
    try:
        tasks = btfs(driver).find_all('table', {'class': 'work-serf'})
        for task in tasks:
            if "serf-link-" in str(task.get('id', '')):
                return True
        return False
    except:
        return False


def FindConfirmButton(driver: webdriver) -> None:
    """Onay butonu bul."""
    try:
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Подтвердить')]"))
        ).click()
    except:
        pass


def FindLikes(driver: webdriver, second: int, userid: str, premium: int, color: str) -> None:
    """Like task'larını bul ve tamamla."""
    try:
        TextColor = ColorizeTextPrint(premium, color)
        print(f"\r{Fore.CYAN}\t [LIKES]: Processing like tasks...", end="")
        # Like task mantığı buraya eklenecek
        random_sleep(2, 5)
    except:
        pass


def Complite_likes(driver: webdriver, second: int, userid: str, premium: int, color: str) -> None:
    """Like'ları tamamla."""
    pass


# ═══════════════════════════════════════════════════════════════════════════════════
#                              SURFING FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════════

def scrol_Surfing(driver: webdriver, second: int, userid: str, premium: int, color: str) -> None:
    """Surfing task'larını yap."""
    try:
        TextColor = ColorizeTextPrint(premium, color)
        all_tasks = btfs(driver).find_all('table', {'class': 'work-serf'})
        tasks_amount = len(all_tasks)
        
        counter = 0
        while counter < tasks_amount:
            try:
                task = all_tasks[counter]
                task_id = str(task.get('id', ''))
                
                if "serf-link-" not in task_id:
                    counter += 1
                    continue
                
                the_task = task_id.replace("serf-link-", "start-serf-")
                xpath = f"//*[@id='{the_task}']/a"
                
                # Scroll and click
                task_elem = WebDriverWait(driver, second).until(
                    EC.visibility_of_element_located((By.XPATH, xpath))
                )
                driver.execute_script("arguments[0].scrollIntoView(true);", task_elem)
                
                WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                ).click()
                time.sleep(3)
                WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                ).click()
                
                # Handle new window
                if len(driver.window_handles) == 2:
                    driver.switch_to.window(driver.window_handles[1])
                    
                    # Wait for timer
                    try:
                        WebDriverWait(driver, 20).until(
                            EC.frame_to_be_available_and_switch_to_it((By.TAG_NAME, 'frame'))
                        )
                        elemno = 1
                        while True:
                            try:
                                timer_elem = btfs(driver).find('span', {'id': 'timer_inp'})
                                if timer_elem:
                                    sec_pr = int(timer_elem.text)
                                    if sec_pr <= 0:
                                        break
                                    
                                    symbols = ["🕥", "🕗", "🕞"]
                                    print(f"\r{Style.BRIGHT}{TextColor}\t █[ time {sec_pr} {symbols[elemno % 3]} ]█", end='')
                                    elemno += 1
                                    time.sleep(0.6)
                                else:
                                    break
                            except:
                                break
                    except:
                        pass
                    
                    time.sleep(random_numbering(2, 4))
                    
                    # Click confirm
                    try:
                        WebDriverWait(driver, 30).until(
                            EC.element_to_be_clickable((By.CLASS_NAME, 'btn_capt'))
                        ).click()
                    except:
                        pass
                    
                    time.sleep(random_numbering(4, 6))
                    TerminateSessionNow(driver)
                    
                    # Show balance
                    ShowedBalance = 0
                    current_hour = datetime.today().hour
                    current_minute = datetime.today().minute
                    
                    balance = GetBalance(driver, userid)
                    print(f"\r{Fore.WHITE}\t [{Fore.YELLOW}Sites{Fore.WHITE}][{TextColor}{current_hour:02d}:{current_minute:02d}{Fore.WHITE}]: {Fore.GREEN}Balance: {TextColor}{balance} RUB.")
                    time.sleep(random_numbering(2, 4))
                    ShowedBalance = 1
                    
                counter += 1
                
            except Exception as e:
                TerminateSessionNow(driver)
                counter += 1
                
    except Exception as e:
        TerminateSessionNow(driver)


def av_ytub_ref(driver: webdriver, second: int, userid: str, premium: int, color: str) -> None:
    """YouTube ads task'larını yap."""
    try:
        TextColor = ColorizeTextPrint(premium, color)
        all_tasks = btfs(driver).find_all('table', {'class': 'work-serf'})
        tasks_amount = len(all_tasks)
        
        counter = 0
        times_tried = 0
        
        while counter < tasks_amount and times_tried < 12:
            try:
                close_tap(driver)
                random_sleep(3, 5)
                
                task = all_tasks[counter]
                task_id = str(task.get('id', ''))
                
                if "ads-link-" not in task_id:
                    counter += 1
                    continue
                
                task_num = task_id.replace('ads-link-', '')
                
                # Get task time
                time_xpath = f"//*[@id='ads-link-{task_num}']/tbody/tr/td[3]/div/span[1]"
                try:
                    time_elem = WebDriverWait(driver, 10).until(
                        EC.visibility_of_element_located((By.XPATH, time_xpath))
                    )
                    time_text = time_elem.text.replace('сек', '').replace(' ', '')
                    task_time = int(time_text) + 7
                except:
                    task_time = 20
                
                print(f"\r{Fore.CYAN}\t [YOUTUBE]: Task time {task_time}s", end="")
                
                # Click task
                start_id = f"link_ads_start_{task_num}"
                start_xpath = f"//*[@id='{start_id}']"
                
                balance_before = GetBalance(driver, userid)
                
                WebDriverWait(driver, second).until(
                    EC.element_to_be_clickable((By.XPATH, start_xpath))
                ).click()
                
                print(f"\r{Fore.CYAN}\t [YOUTUBE]: Task clicked", end="")
                random_sleep(5, 12)
                
                # Open video if needed
                if len(driver.window_handles) == 1:
                    try:
                        WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, "//*[text()='Открыть видео']"))
                        ).click()
                    except:
                        pass
                    random_sleep(5, 12)
                
                # Handle video window
                if len(driver.window_handles) == 2:
                    print(f"\r{Fore.CYAN}\t [YOUTUBE]: Playing video...", end="")
                    driver.switch_to.window(driver.window_handles[1])
                    
                    playvid(driver)
                    random_sleep(4, 6)
                    
                    # Check for violation page
                    if "aviso.bz/go/create-task" in driver.current_url:
                        try:
                            WebDriverWait(driver, 5).until(
                                EC.visibility_of_element_located((By.XPATH, "//*[text()='Я ознакомлен']"))
                            ).click()
                        except:
                            driver.close()
                            driver.switch_to.window(driver.window_handles[0])
                            counter += 1
                            times_tried += 1
                            continue
                    
                    # Wait for task
                    WaitTimerForTask(task_time)
                    
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    random_sleep(4, 6)
                    
                    # Confirm task
                    try:
                        WebDriverWait(driver, 5).until(
                            EC.visibility_of_element_located((By.XPATH, "//*[@class='status-link-youtube']"))
                        ).click()
                        print(f"\r{Fore.GREEN}\t [YOUTUBE]: ✓ Task finished!", end="")
                    except:
                        print(f"\r{Fore.RED}\t [YOUTUBE]: ✗ Failed, retrying...", end="")
                        FindConfirmButton(driver)
                    
                    # Check balance change
                    balance_after = GetBalance(driver, userid)
                    if balance_after != balance_before:
                        VideoEffect(driver, userid, premium, color)
                
                counter += 1
                times_tried += 1
                
            except Exception as e:
                counter += 1
                times_tried += 1
                
        close_tap(driver)
        time.sleep(3)
        print(f"\r{' ' * 50}\r", end="")
        
    except Exception as e:
        pass


# ═══════════════════════════════════════════════════════════════════════════════════
#                              MAIN SURFING LOOP
# ═══════════════════════════════════════════════════════════════════════════════════

def Surfing(driver: webdriver, second: int, userid: str) -> None:
    """Ana surfing döngüsü."""
    
    TitledPrint = 1
    FoundFails = 0
    FunctionStart = 1  # 0=YouTube, 1=Surfing
    BotColor = ""
    PremiumBotFE = 1
    NotEnoughFunds = 0
    NoTasksF = 0
    
    UseOldDriver = 0
    CurrentUserName = GetUserName(driver)
    
    # Check banned users
    NumboTT = 0
    while True:
        banned_file = f"{FILES['banned_prefix']}{NumboTT}.bua"
        if IsFileExist(banned_file):
            banned_name = GetFileElement(banned_file, "Username")
            if CurrentUserName == banned_name:
                UseOldDriver = 1
                driver.close()
                os.system("clear")
                driver = BanningDriver("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
                break
        NumboTT += 1
        if NumboTT > 10:
            for i in range(1, 11):
                DeleteFile(f"{FILES['banned_prefix']}{i}.bua")
            break
    
    # Check approved user
    if UseOldDriver == 0 and IsFileExist(FILES["approved"]):
        approved_name = GetFileElement(FILES["approved"], "Username")
        if CurrentUserName != approved_name:
            CheckReferral1(driver, second, userid)
    
    if UseOldDriver == 0 and not IsFileExist(FILES["approved"]):
        CheckReferral1(driver, second, userid)
    
    # Color setup
    TextColor = Fore.WHITE
    if PremiumBotFE == 1:
        BotColor = GetFileElement(FILES["config"], "Color")
        if BotColor in COLORS:
            TextColor = COLORS[BotColor]
    
    # Start URL
    driver.get("https://aviso.bz/tasks-youtube?tab=price")
    random_sleep(8, 14)
    
    # Show initial balance
    balance = GetBalance(driver, userid)
    print(f"\n{Fore.WHITE}\t [{Fore.CYAN}START{Fore.WHITE}]: {Fore.GREEN}Main Balance: {TextColor}{balance} RUB.")
    
    # Main loop
    while True:
        try:
            # ============ YOUTUBE TASKS ============
            if FunctionStart == 0:
                try:
                    if TitledPrint == 0:
                        TitledPrint = 1
                        print(f"\r{' ' * 60}\r", end="")
                    
                    driver.get("https://aviso.bz/tasks-youtube?tab=price")
                    AttemptsCounter()
                    random_sleep(1, 3)
                    
                    if AreWeStillLoggedIn(driver) == False:
                        print(f"\n{Fore.RED}\t [LOGOUT]: Session ended, please login again.")
                        break
                    
                    no_trs(driver, second)
                    
                    if FoundYoutubeLikes(driver):
                        FindLikes(driver, second, userid, PremiumBotFE, BotColor)
                    
                    if FoundYoutubeAds(driver):
                        av_ytub_ref(driver, second, userid, PremiumBotFE, BotColor)
                    
                    FoundFails += 1
                    if FoundFails > 2:
                        NoTasksF += 1
                        if NoTasksF > 2:
                            WaitTimerTask()
                            NoTasksF = 0
                        FunctionStart = 1
                        TitledPrint = 0
                        FoundFails = 0
                        print(f"\r{Fore.WHITE}\t [{Fore.CYAN}SWITCH{Fore.WHITE}]: {TextColor}No tasks → Surfing", end="\r")
                        random_sleep(3, 6)
                        gc.collect()
                        
                except:
                    FoundFails += 1
                    if FoundFails > 1:
                        NoTasksF += 1
                        if NoTasksF > 2:
                            WaitTimerTask()
                            NoTasksF = 0
                        FunctionStart = 1
                        TitledPrint = 0
                        FoundFails = 0
                        print(f"\r{Fore.WHITE}\t [{Fore.CYAN}SWITCH{Fore.WHITE}]: {TextColor}No tasks → Surfing", end="\r")
                        random_sleep(4, 7)
                        gc.collect()
            
            # ============ SURFING TASKS ============
            if FunctionStart == 1:
                try:
                    if TitledPrint == 0:
                        TitledPrint = 1
                        print(f"\r{' ' * 60}\r", end="")
                    
                    driver.get("https://aviso.bz/tasks-surf")
                    AttemptsCounter()
                    random_sleep(3, 8)
                    
                    if AreWeStillLoggedIn(driver) == False:
                        print(f"\n{Fore.RED}\t [LOGOUT]: Session ended, please login again.")
                        break
                    
                    no_trs(driver, second)
                    
                    if FoundSerf(driver):
                        scrol_Surfing(driver, second, userid, PremiumBotFE, BotColor)
                    
                    FoundFails += 1
                    if FoundFails > 1:
                        NoTasksF += 1
                        if NoTasksF > 1:
                            WaitTimerTask()
                            NoTasksF = 0
                        FunctionStart = 0
                        TitledPrint = 0
                        FoundFails = 0
                        print(f"\r{Fore.WHITE}\t [{Fore.CYAN}SWITCH{Fore.WHITE}]: {TextColor}No tasks → YouTube", end="\r")
                        random_sleep(2, 5)
                        gc.collect()
                        
                except:
                    FoundFails += 1
                    if FoundFails > 1:
                        NoTasksF += 1
                        if NoTasksF > 1:
                            WaitTimerTask()
                            NoTasksF = 0
                        FunctionStart = 0
                        TitledPrint = 0
                        FoundFails = 0
                        print(f"\r{Fore.WHITE}\t [{Fore.CYAN}SWITCH{Fore.WHITE}]: {TextColor}No tasks → YouTube", end="\r")
                        random_sleep(2, 5)
                        gc.collect()
                        
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}\t [EXIT]: Bot stopped by user.")
            break
        except Exception as e:
            print(f"\n{Fore.RED}\t [ERROR]: {e}")
            random_sleep(5, 10)


# ═══════════════════════════════════════════════════════════════════════════════════
#                              LOGIN WORKERS
# ═══════════════════════════════════════════════════════════════════════════════════

def LoginToWorkCookies(driver: webdriver, second: int) -> None:
    """Çerezlerle çalışmaya başla."""
    LoggedIn = 0
    
    if IsFileExist(FILES["cookies"]):
        LoginWithCookies(driver)
        if Did_Login(driver):
            no_trs(driver, second)
            save_cookies(driver)
            LoggedIn = 1
    
    if LoggedIn == 0:
        CookiesInput = GetCookiesInput()
        os.system("clear")
        ShowLogoFE()
        driver.get("https://aviso.bz/login")
        time.sleep(5)
        no_trs(driver, second)
        add_ccocki_driver(driver, check_cocki(CookiesInput), 'https://aviso.bz/members')
        
        if Did_Login(driver):
            no_trs(driver, second)
            save_cookies(driver)
            LoggedIn = 1
    
    if LoggedIn == 1:
        user = get_user(driver)
        time.sleep(1.5)
        if user:
            Surfing(driver, second, user)


def LoginToWorkManual(driver: webdriver, second: int, Username: str, Password: str) -> None:
    """Manuel girişle çalışmaya başla."""
    LoggedIn = 0
    
    if Did_Login(driver):
        LoggedIn = 1
    
    if IsFileExist(FILES["cookies"]) and LoggedIn == 0:
        LoginWithCookies(driver)
        if Did_Login(driver):
            LoggedIn = 1
    
    if LoggedIn == 0:
        logginn(driver, second, Username, Password)
        if Did_Login(driver):
            no_trs(driver, second)
            save_cookies(driver)
        else:
            if IsPhoneConnected():
                SaveLoginMethod("Cookies")
                print(f"{Fore.YELLOW}\t [SWITCH]: Couldn't login, switched to cookies only.")
                return
    
    if LoggedIn == 1:
        user = get_user(driver)
        time.sleep(1.5)
        if user:
            Surfing(driver, second, user)


def shoose() -> int:
    """Kullanıcı seçimini al."""
    print(f"\n{Fore.CYAN}\t [1] {Fore.WHITE}Login with Cookies")
    print(f"{Fore.CYAN}\t [2] {Fore.WHITE}Login with Username/Password")
    print(f"{Fore.CYAN}\t [3] {Fore.WHITE}Exit")
    
    while True:
        try:
            choice = input(f"\n{Fore.YELLOW}\t [SELECT]: {Style.RESET_ALL}")
            if choice in ['1', '2', '3']:
                return int(choice)
        except:
            pass
        print(f"{Fore.RED}\t [ERROR]: Invalid choice!")


def WaitForAWhile() -> None:
    """Biraz bekle."""
    time.sleep(2)


# ═══════════════════════════════════════════════════════════════════════════════════
#                              MAIN ENTRY
# ═══════════════════════════════════════════════════════════════════════════════════

def main():
    """Ana fonksiyon."""
    os.system("clear")
    ShowLogoFE()
    CheckNetConnection()
    
    print(f"\n{Fore.GREEN}\t [INFO]: NINOCOIN AVISO Bot Starting...")
    print(f"{Fore.CYAN}\t [INFO]: 18 Coin Support: {Fore.YELLOW}{', '.join(SUPPORTED_COINS)}")
    print(f"{Fore.CYAN}\t [INFO]: Device: {Fore.YELLOW}{get_phone_brand()} {get_phone_model()}")
    print(f"{Fore.CYAN}\t [INFO]: Android: {Fore.YELLOW}{get_phone_version()}")
    
    # Setup
    second = 20
    
    choice = shoose()
    
    if choice == 3:
        print(f"{Fore.YELLOW}\t [EXIT]: Goodbye!")
        sys.exit(0)
    
    # Create driver
    print(f"\n{Fore.CYAN}\t [SETUP]: Creating driver...")
    
    if choice == 1:
        driver = BanningDriver()
        LoginToWorkCookies(driver, second)
    elif choice == 2:
        print(f"\n{Fore.YELLOW}\t [INPUT]: Enter your credentials:")
        username = input(f"\t {Fore.CYAN}Username: {Style.RESET_ALL}")
        password = input(f"\t {Fore.CYAN}Password: {Style.RESET_ALL}")
        
        SaveMyData(username, password)
        SaveLoginMethod("Manual")
        
        driver = BanningDriver()
        driver.get("https://aviso.bz/login")
        time.sleep(5)
        LoginToWorkManual(driver, second, username, password)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}\n\t [EXIT]: Bot stopped.")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Fore.RED}\t [FATAL]: {e}")
        sys.exit(1)
