"""Deobfuscated source recovered from sm2.py.

This file preserves the behavior of the final payload while removing the
Base32/Base64/Base58/Hex/XOR/zlib/marshal loader chain and dynamic exec layer.
"""

import json
import os
import shutil
import time
from datetime import datetime
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

import requests

RESET = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"

LOGIN_URL = "https://slotfruits.com/api/v1/users/signupFaucetPayLogin"
SPIN_URL = "https://slotfruits.com/api/v1/users/earnRoll"
ADS_URL = "https://googleads.g.doubleclick.net/mads/gma?submodel=SM-A217F&adid_p=1&format=interstitial_mb&ini_pn=com.google.android.packageinstaller&ins_pn=com.google.android.packageinstaller&omid_v=a.1.5.2-google_20241009&dv=254380203&ev=24.6.0&gl=ID&hl=in&js=afma-sdk-a-v254380999.253410000.1&kw=clothing%2Cfashion&lv=253410000&ms=CqgFmsA_ATEaQQHY5dWIJ1nnZI0TXJOCrRjxy3oie3ZsfYBDue5jJF2CTFQQuf7W9C9KnP8xbLx0FI_PC-5wIrw0itcrK2KvDP4iEt0E6Yp1pn72NO8vWhbzh19JnXz5v7gGWsohjScUvkVohNO_jbecHUPYSmq4yT-WuJZ2EFv8_r-2HeMQg4ZPiq_jwKyeOrQjsiRXsU8vcZpKSMI0Z7Pn6iha94ABhZW_FbLysDgYt2ox4f_FIffLSbr_vjYntwKQpTg44MpacMRJ2_Ch0aplBuEzXYGkOTHBpg58oZtEw_3nZ8wsO9jE5lLVvx_cmKmOEpfemdesE_wTXvV0Hv5MWrZQ2I4ulXfQrY_gKRBI5ivJJLh3XYIzgBBRhoZastP7yEVFBT7Y8iunIsK3VrABvtw9RWUDkE2lETA0ezNEzwFoAhoGTGHuS2JaZ68x68KZGPFPR1CX4CXbMf1DDtzECiUr12lOsiuPUQ2WWtrjma3PKtkBk-0B5HoTVviRRPOHqgth3x80sbtwMn4G95El7JP079-e_jUT0oa75oJQC-Ph3zmllppvqq3dJN_RCGbyELdXc042fsR1fi3Syd6w1SJROO_t2sP3o2Bdzn2_jv1aokWO8NAzbtrWUs64BUiv1-XMv3k6CReZ91Ac9T28vbfulD8b_t8WSPrIHmXCGEC4h50U74SHhRxUcOmlR7sWpB2y8WfC7NlfoGCG5r6vXzVpG1oFOvTYscbEq1GPl1SjpnwS00RVM5_wfwa6GKc53oRubkV-CBhU_KMXUN115FELhAaNab2qn8reOKeN6xdg_OkZjGgHml1GIlVQity3vBcbzP2yE898LCwcwXVc9oLcH_WHL1eb7K19Z6f5kpquk35qGtTP3xrSzDcw6t-GAxGg1lTCxlMgBA&mv=84923430.com.android.vending&lft=1&vnm=1.1.6&plbs=0&plcs=0&u_sd=1.75&request_id=1267448703&target_api=35&carrier=51011&request_agent=rn-invertase-15.8.0&seq_num=2&eid=318500618,318486317,318491267,318503826,318509511,318509849,318515546,318518927,318527162,318482080,318483611,318484497,318484801,318525018,318526145,318526848&guci=0.0.0.0.0.0.0.0&sdk_apis=7%2C8&omid_p=Google%2Fafma-sdk-a-v260480999.253410000.1&cap=m&u_w=412&u_h=828&msid=com.piratebaixe.slotMobile&an=17.android.com.spincoin.appmobile.top&u_audio=3&net=ed&u_so=p&rbv=1&loeid=44766145%2C318502926&preqs_in_session=1&preqs=1&time_in_session=70&pcc=0&sst=1766181420000&output=html&region=mobile_app&u_tz=420&client=ca-app-pub-5674874137587223&slotname=7114498212&kw_type=broad&gsb=4g&lite=0&app_wp_code=ca-app-pub-5674874137587223&app_code=5186053460&num_ads=1&vpt=8&vfmt=18&vst=0&sdkv=o.254380999.253410000.1&sdmax=0&dmax=1&sdki=3c4d&stbg=1&bisch=true&blev=0.16&canm=true&_mv=84923430.com.android.vending&heap_free=35837248&heap_max=268435456&heap_total=67108864&wv_count=0&rdps=5500&caps=inlineVideo_interactiveVideo_mraid1_mraid2_mraid3_sdkVideo_exo3_th_autoplay_mediation_scroll_av_transparentBackground_sdkAdmobApiForAds_di_aso_sfv_dinm_dim_nav_navc_dinmo_ipdof_gls_gcache_saiMacro_sai_demuxedGcache_xSeconds&is_lat=false&blob=ABPQqLFPLHz2k6c8n6CqX1sW26j7BjCjFG5-MaUl0CxgLB41Sc1B8kpJWaikL2C_Gp9pl25Xd46LPjDMkuzcNeNk1dvygLdxMwK-Y6rlwJbBvC5njmNuysN-8h288vPObPEuoucf6F2FyhorQbQv9YbRKuFGXNMnm3mLs9x1FneK3ofa6gCK_UTEhPBLeTogM4C8tHMwO2a7T816OsKSD0JYRvo61pYUj8Rx-RsJMnAhHhTzRs3ktQdg-BbwRWiEaPEswxrDeM_GpknK8GoDLzwQ_wuTxQDlAIhl0WIPz9VciYotTXJ86Pe3o5uMwqNeQhZ_qFNQWL_Rncwnb9idfxUEGM5ucxxK_zjofg8F&jsv=sdk_20190107_RC02-production-sdk_20251202_RC00"


def clear_screen() -> None:
    os.system("clear")


def terminal_width() -> int:
    return shutil.get_terminal_size().columns


def make_line(char: str = "═") -> str:
    return char * terminal_width()


def center_text(text: str) -> str:
    return text.center(terminal_width())


def print_banner() -> None:
    _now = datetime.now()
    clear_screen()
    print(CYAN + make_line("═"))
    print(center_text("🚀 SLOT MOBILE SYNDICATEBOT NET 🚀"))
    print(CYAN + make_line("═"))
    print(f"{MAGENTA}Created By        : {RESET}Leonnnx77")
    print(f"{MAGENTA}Channel Telegram  : {RESET}https://t.me/SyndicateBotNet")
    print(CYAN + make_line("═"))


def animate_status(text: str) -> None:
    for i in range(2):
        print(f"{YELLOW}{text}{'.' * (i + 1)}{RESET}", end="\r")
        time.sleep(0.4)


def print_account_info(email: str, balance, credits) -> None:
    print()
    print(f"{GREEN}Email           : {RESET}{email}")
    print(f"{GREEN}Balance         : {RESET}{balance}")
    print(f"{GREEN}Spin Available  : {RESET}{credits}")
    print(CYAN + make_line("═"))


def login(email: str):
    print_banner()
    animate_status("🔐 Login")
    payload = {"email": email}
    headers = {
        "User-Agent": "okhttp/4.12.0",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
    }
    response_json = requests.post(LOGIN_URL, data=json.dumps(payload), headers=headers).json()
    token = response_json.get("token")
    user = response_json.get("user", {})
    return token, user.get("_id"), user.get("balance", 0), user.get("credits", 0)


def normalize_credit_count(value) -> int:
    """Best-effort conversion of API credit values to an integer count."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def run_spin_loop(email: str, token: str, balance, credits):
    credits = normalize_credit_count(credits)
    repeated_credit_count = 0

    while credits > 0:
        animate_status("🎰 Try To Spin")
        headers = {
            "User-Agent": "okhttp/4.12.0",
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip",
            "authorization": f"Bearer {token}",
        }
        spin_response = requests.get(SPIN_URL, headers=headers).json()
        total_reward = spin_response.get("total", 0)
        user = spin_response.get("user", {})
        balance = user.get("balance", balance)
        new_credits = normalize_credit_count(user.get("credits", credits))
        if new_credits == credits:
            repeated_credit_count += 1
        else:
            repeated_credit_count = 0
        credits = new_credits
        print_banner()
        print_account_info(email, balance, credits)
        print(f"{YELLOW}🎁 Reward        : {RESET}{total_reward}")
        print(CYAN + make_line("═"))
        if spin_response.get("message"):
            print(f"{YELLOW}API Message      : {RESET}{spin_response.get('message')}")
        if spin_response.get("success") is False or repeated_credit_count >= 2:
            print(f"{YELLOW}Spin stopped because the API no longer decreased credits.{RESET}")
            break
        time.sleep(1)
    return balance, credits


def run_ads_loop(user_id: str) -> None:
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 12; SM-A217F Build/SP1A.210812.016; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/147.0.7727.111 Mobile Safari/537.36 (Mobile; afma-sdk-a-v260480999.253410000.1)",
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
    print(CYAN + make_line("─"))
    print(f"{YELLOW}🚀 Start Ads Farming...{RESET}")

    for _ in range(1):
        try:
            response = requests.get(ADS_URL, headers=headers)
            if "application/json" in response.headers.get("Content-Type", ""):
                data = response.json()
                for video_reward_url in data.get("ad_networks", [])[0].get("video_reward_urls", []):
                    parsed_url = urlparse(video_reward_url)
                    query_parameters = parse_qs(parsed_url.query, keep_blank_values=True)
                    query_parameters["rwd_userid"] = [user_id]
                    updated_url = urlunparse(
                        parsed_url._replace(query=urlencode(query_parameters, doseq=True))
                    )
                    reward_response = requests.get(updated_url, headers=headers)
                    print(f"{GREEN}✔ Ads Hit {reward_response.status_code}{RESET}")
        except Exception:
            print(f"{RED}Error Ads{RESET}")
        time.sleep(3)


def main() -> None:
    print_banner()
    email = input(f"{YELLOW} Enter Your Faucet Email => {RESET}")
    while True:
        token, user_id, balance, credits = login(email)
        print_banner()
        print_account_info(email, balance, credits)
        balance, credits = run_spin_loop(email, token, balance, credits)
        print(f"{GREEN}✔ Spin Done{RESET}")
        run_ads_loop(user_id)
        print(f"{CYAN}🔄 Restarting cycle...{RESET}")


if __name__ == "__main__":
    main()
