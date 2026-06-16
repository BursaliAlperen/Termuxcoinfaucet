import requests
from bs4 import BeautifulSoup

EMAIL = input("Email: ")
SIFRE = input("Sifre: ")

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120.0.0.0 Mobile Safari/537.36'
})

# 1. Ana sayfayı al ve CSRF token'ı bul
print("[*] Ana sayfa alınıyor...")
res = session.get('https://aviso.bz/')
soup = BeautifulSoup(res.text, 'html.parser')

csrf = soup.find('input', {'name': 'csrf_token'})
payload = {
    'login': EMAIL,
    'password': SIFRE,
    'submit': 'Enter'
}
if csrf:
    payload['csrf_token'] = csrf['value']
    print(f"[+] CSRF Token bulundu: {csrf['value'][:20]}...")

# 2. Login yap
print("[*] Login yapılıyor...")
res = session.post('https://aviso.bz/', data=payload, allow_redirects=True)

if "logout" in res.text.lower() or "balance" in res.text.lower():
    print("[+] Login başarılı!")
else:
    print("[!] Login başarısız olabilir. HTML'i kontrol et.")

# 3. Tasks-YouTube sayfasını al
print("[*] tasks-youtube sayfası alınıyor...")
res = session.get('https://aviso.bz/tasks-youtube')

# 4. HTML'i kaydet
with open('aviso_tasks.html', 'w', encoding='utf-8') as f:
    f.write(res.text)

print("[+] HTML kaydedildi: aviso_tasks.html")
print("[*] Bu dosyayı bana gönder, gerçek class isimlerini bulayım!")
