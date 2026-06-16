from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import os
import sys
import requests
import re

# ================= CONFIGURATION =================
BRAND_NAME = "QONTEX AVISO.BZ"
VERSION = "v3.0.0 REAL"
CLEAR_EVERY = 10
# =================================================

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    clear_screen()
    banner = f"""
{Colors.OKCYAN}{Colors.BOLD}
   ██████╗ ██████╗  ██████╗ ███╗   ██╗████████╗███████╗
  ██╔════╝██╔═══██╗██╔════╝ ████╗  ██║╚══██╔══╝██╔════╝
  ██║     ██║   ██║██║  ███╗██╔██╗ ██║   ██║   ███████╗
  ██║     ██║   ██║██║   ██║██║╚██╗██║   ██║   ╚════██║
  ╚██████╗╚██████╔╝╚██████╔╝██║ ╚████║   ██║   ███████║
   ╚═════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚══════╝
{Colors.OKGREEN}       [ {BRAND_NAME} REAL SYSTEM ]
{Colors.OKBLUE}       [ Selenium + Real Browser | {VERSION} ]
{Colors.WARNING}       [ Termux Optimized | 0 Errors ]
{Colors.ENDC}
"""
    print(banner)

class WaryonoCaptcha:
    """Waryono.my.id API Entegrasyonu"""    
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://waryono.my.id"

    def solve_hcaptcha(self, site_key, page_url):
        print(f"{Colors.WARNING}[*] hCaptcha Waryono API'ye gönderiliyor...{Colors.ENDC}")
        try:
            params = {
                'key': self.api_key,
                'method': 'hcaptcha',
                'sitekey': site_key,
                'pageurl': page_url
            }
            res = requests.post(f"{self.base_url}/in.php", data=params)
            if "OK" not in res.text:
                raise Exception(f"API Hatası: {res.text}")
            
            task_id = res.text.split('|')[1]
            print(f"{Colors.OKBLUE}[*] Task ID: {task_id}. Çözüm bekleniyor...{Colors.ENDC}")
            
            for _ in range(30): 
                time.sleep(5)
                res = requests.get(f"{self.base_url}/res.php", params={
                    'key': self.api_key,
                    'action': 'get',
                    'id': task_id
                })
                if "OK" in res.text:
                    token = res.text.split('|')[1]
                    print(f"{Colors.OKGREEN}[+] hCaptcha başarıyla çözüldü!{Colors.ENDC}")
                    return token
                elif "CAPCHA_NOT_READY" in res.text:
                    continue
                else:
                    raise Exception(f"API Hatası: {res.text}")
            raise Exception("Zaman aşımı: Captcha çözülemedi.")
        except Exception as e:
            print(f"{Colors.FAIL}[!] Captcha Hatası: {e}{Colors.ENDC}")
            return None

class AvisoRealBot:
    def __init__(self, email, password, captcha_api_key):
        self.email = email
        self.password = password
        self.captcha_solver = WaryonoCaptcha(captcha_api_key)
        self.claim_count = 0
        self.total_earned = 0.0
        self.task_log = []
        self.driver = None        
    def setup_driver(self):
        """Termux için Chromium driver ayarları"""
        print(f"{Colors.OKBLUE}[*] Chromium başlatılıyor...{Colors.ENDC}")
        
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Linux; Android 14; SM-A155F) AppleWebKit/537.36 Chrome/120.0.0.0 Mobile Safari/537.36')
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_page_load_timeout(30)
            print(f"{Colors.OKGREEN}[+] Chromium başarıyla başlatıldı!{Colors.ENDC}")
            return True
        except Exception as e:
            print(f"{Colors.FAIL}[!] Chromium başlatılamadı: {e}{Colors.ENDC}")
            return False

    def login(self):
        """Aviso.bz'ye gerçek tarayıcı ile giriş"""
        print(f"{Colors.OKBLUE}[*] Aviso.bz'ye giriş yapılıyor...{Colors.ENDC}")
        try:
            self.driver.get('https://aviso.bz/')
            time.sleep(3)
            
            email_field = self.driver.find_element(By.NAME, 'login') or self.driver.find_element(By.CSS_SELECTOR, 'input[type="email"]')
            password_field = self.driver.find_element(By.NAME, 'password') or self.driver.find_element(By.CSS_SELECTOR, 'input[type="password"]')
            
            email_field.send_keys(self.email)
            password_field.send_keys(self.password)
            
            submit_btn = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"], input[type="submit"], .btn-login')
            submit_btn.click()
            
            time.sleep(5)
            
            if "logout" in self.driver.page_source.lower() or "balance" in self.driver.page_source.lower() or "Баланс" in self.driver.page_source:
                print(f"{Colors.OKGREEN}[+] Giriş başarılı!{Colors.ENDC}")
                return True
            else:
                print(f"{Colors.FAIL}[!] Giriş başarısız.{Colors.ENDC}")
                return False
                
        except Exception as e:
            print(f"{Colors.FAIL}[!] Giriş Hatası: {e}{Colors.ENDC}")            return False

    def get_youtube_tasks(self):
        """YouTube görevlerini bul"""
        try:
            print(f"{Colors.OKCYAN}[*] YouTube görevleri sayfasına gidiliyor...{Colors.ENDC}")
            self.driver.get('https://aviso.bz/tasks-youtube')
            time.sleep(5)
            
            tasks = []
            
            task_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Просмотр видеоролика')]")
            
            for element in task_elements:
                try:
                    parent = element.find_element(By.XPATH, "./ancestor::tr | ./ancestor::div[contains(@class, 'task')]")
                    execute_btn = parent.find_element(By.XPATH, ".//a[contains(@href, 'execute') or contains(@href, 'tasks-youtube')] | .//button[contains(@class, 'btn')]")
                    
                    if execute_btn:
                        tasks.append({
                            'element': execute_btn,
                            'title': "YouTube Video Task"
                        })
                except:
                    continue
            
            if not tasks:
                execute_buttons = self.driver.find_elements(By.XPATH, "//a[contains(text(), 'Выполнить')] | //button[contains(text(), 'Выполнить')]")
                for btn in execute_buttons:
                    tasks.append({
                        'element': btn,
                        'title': "YouTube Task"
                    })
            
            print(f"{Colors.OKGREEN}[+] {len(tasks)} YouTube görevi bulundu!{Colors.ENDC}")
            return tasks
            
        except Exception as e:
            print(f"{Colors.FAIL}[!] Görevleri çekerken hata: {e}{Colors.ENDC}")
            return []

    def execute_task(self, task):
        """Tek bir görevi çalıştır"""
        try:
            print(f"{Colors.OKCYAN}[*] Görev Çalıştırılıyor: {task.get('title')}{Colors.ENDC}")
            
            task['element'].click()
            time.sleep(5)
            
            try:                hcaptcha_div = self.driver.find_element(By.CSS_SELECTOR, '.h-captcha, div[data-sitekey]')
                site_key = hcaptcha_div.get_attribute('data-sitekey')
                
                if site_key:
                    print(f"{Colors.WARNING}[*] hCaptcha tespit edildi!{Colors.ENDC}")
                    token = self.captcha_solver.solve_hcaptcha(site_key, self.driver.current_url)
                    
                    if token:
                        self.driver.execute_script(f"""
                            document.querySelector('[name="h-captcha-response"]').value = '{token}';
                            document.querySelector('[name="h-captcha-response"]').dispatchEvent(new Event('change'));
                        """)
                        time.sleep(2)
                        
                        self.driver.execute_script("document.querySelector('form').submit();")
                        time.sleep(5)
            except NoSuchElementException:
                pass
            
            try:
                iframe = self.driver.find_element(By.TAG_NAME, 'iframe')
                yt_url = iframe.get_attribute('src')
                
                if yt_url and 'youtube' in yt_url:
                    print(f"{Colors.OKBLUE}[*] YouTube video izleniyor (15 saniye)...{Colors.ENDC}")
                    self.driver.execute_script(f"window.open('{yt_url}', '_blank');")
                    self.driver.switch_to.window(self.driver.window_handles[-1])
                    time.sleep(15)
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])
            except:
                pass
            
            try:
                confirm_btn = self.driver.find_element(By.XPATH, "//a[contains(text(), 'Подтвердить просмотр')] | //button[contains(text(), 'Подтвердить просмотр')]")
                confirm_btn.click()
                time.sleep(3)
                
                if "Вы успешно выполнили задание!" in self.driver.page_source or "успешно" in self.driver.page_source.lower():
                    reward_match = re.search(r'\+([\d\.]+)', self.driver.page_source)
                    reward = float(reward_match.group(1)) if reward_match else 0.02
                    
                    self.total_earned += reward
                    self.claim_count += 1
                    
                    status = "Tıklandı, Ödül Alındı"
                    self.task_log.append(f"[Task {self.claim_count}] | {status} | +{reward} RUB")
                    print(f"{Colors.OKGREEN}[+] {status} +{reward} RUB{Colors.ENDC}")
                    return True
                else:                    print(f"{Colors.WARNING}[!] Onaylama başarısız.{Colors.ENDC}")
                    return False
                    
            except NoSuchElementException:
                print(f"{Colors.FAIL}[!] Onay butonu bulunamadı.{Colors.ENDC}")
                return False
                
        except Exception as e:
            print(f"{Colors.FAIL}[!] Görev hatası: {e}{Colors.ENDC}")
            return False

    def run(self):
        """Ana döngü"""
        if not self.setup_driver():
            return
            
        if not self.login():
            self.driver.quit()
            return
            
        try:
            while True:
                print_banner()
                print(f"{Colors.OKGREEN}[*] Toplam Claim: {self.claim_count} | Toplam Kazanç: {self.total_earned:.2f} RUB{Colors.ENDC}\n")
                
                print(f"{Colors.OKCYAN}--- Anlık Claimler ---{Colors.ENDC}")
                for log in self.task_log[-5:]:
                    print(f"{Colors.OKBLUE}{log}{Colors.ENDC}")
                print(f"{Colors.OKCYAN}---------------------{Colors.ENDC}\n")
                
                tasks = self.get_youtube_tasks()
                if not tasks:
                    print(f"{Colors.WARNING}[*] Uygun görev yok. 60 saniye bekleniyor...{Colors.ENDC}")
                    time.sleep(60)
                    continue
                    
                for task in tasks:
                    success = self.execute_task(task)
                    if success and self.claim_count % CLEAR_EVERY == 0:
                        print(f"\n{Colors.WARNING}[*] {CLEAR_EVERY} Claim'e ulaşıldı! Ekran temizleniyor...{Colors.ENDC}")
                        time.sleep(2)
                        self.task_log = []
                        break 
                    
                    time.sleep(5)
                    
        except KeyboardInterrupt:
            print(f"\n{Colors.WARNING}[*] Kullanıcı tarafından durduruldu.{Colors.ENDC}")
        finally:
            if self.driver:                self.driver.quit()
                print(f"{Colors.OKBLUE}[*] Tarayıcı kapatıldı.{Colors.ENDC}")

def main():
    print_banner()
    print(f"{Colors.OKCYAN}{Colors.BOLD}QONTEX AVISO.BZ Gerçek Sistem Otomasyon Aracına Hoşgeldin!{Colors.ENDC}")
    email = input(f"{Colors.OKBLUE}[*] Aviso Email: {Colors.ENDC}")
    password = input(f"{Colors.OKBLUE}[*] Aviso Şifre: {Colors.ENDC}")
    captcha_api = input(f"{Colors.OKBLUE}[*] Waryono API Key: {Colors.ENDC}")
    
    bot = AvisoRealBot(email, password, captcha_api)
    bot.run()

if __name__ == "__main__":
    main()
