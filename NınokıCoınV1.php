<?php
error_reporting(0);
date_default_timezone_set('Europe/Istanbul');

// ANSI RENKLER
$c = [
    'reset' => "\033[0m", 'putih' => "\033[1;37m", 'merah' => "\033[1;31m",
    'hijau' => "\033[1;32m", 'kuning' => "\033[1;33m", 'biru' => "\033[1;34m",
    'cyan' => "\033[1;36m", 'abu' => "\033[0;90m"
];

$ayarDosyasi = __DIR__ . "/config.json";
$cerezDosyasi = __DIR__ . "/cookies.txt"; // [DUZELTME] Oturum kaybolmasin diye mutlak yol

// HEDEF ADRES LISTESI (NınokıCoın için tek listede)
$aktif_adresler = [
    // --- MIXTOSHI ---
    "LTC-MIX"     => "https://mixtoshi.com?r=ankaralironaldo131@gmail.com",
    "USDT-MIX"    => "https://mixtoshi.com/free-usdt?r=ankaralironaldo131@gmail.com",
    "PEPE-MIX"    => "https://mixtoshi.com/free-pepe?r=ankaralironaldo131@gmail.com",
    "SOL-MIX"     => "https://mixtoshi.com/free-sol?r=ankaralironaldo131@gmail.com",
    "DOGE-MIX"    => "https://mixtoshi.com/free-doge?r=ankaralironaldo131@gmail.com",
    "TRX-MIX"     => "https://mixtoshi.com/free-trx?r=ankaralironaldo131@gmail.com",

    // --- EX-FAUCET ---
    "LTC-EX"      => "https://ex-faucet.xyz/faucet-ltc?r=ankaralironaldo131@gmail.com",
    "USDT-EX"     => "https://ex-faucet.xyz/faucet-usdt?r=ankaralironaldo131@gmail.com",
    "PEPE-EX"     => "https://ex-faucet.xyz/faucet-pepe?r=ankaralironaldo131@gmail.com",
    "SOL-EX"      => "https://ex-faucet.xyz/faucet-sol?r=ankaralironaldo131@gmail.com",
    "DOGE-EX"     => "https://ex-faucet.xyz/faucet-doge?r=ankaralironaldo131@gmail.com",
    "TRX-EX"      => "https://ex-faucet.xyz/faucet-trx?r=ankaralironaldo131@gmail.com",

    // --- COIN VAGANZA ---
    "USDT-VGNZ"   => "https://coinvaganza.xyz?r=ankaralironaldo131@gmail.com",
    "LTC-VGNZ"    => "https://coinvaganza.xyz/claim-ltc?r=ankaralironaldo131@gmail.com",
    "DOGE-VGNZ"   => "https://coinvaganza.xyz/claim-doge?r=ankaralironaldo131@gmail.com",
    "SOL-VGNZ"    => "https://coinvaganza.xyz/claim-sol?r=ankaralironaldo131@gmail.com",
    "PEPE-VGNZ"   => "https://coinvaganza.xyz/claim-pepe?r=ankaralironaldo131@gmail.com",
    "BCH-VGNZ"    => "https://coinvaganza.xyz/claim-bch?r=ankaralironaldo131@gmail.com",
    "TRX-VGNZ"    => "https://coinvaganza.xyz/claim-trx?r=ankaralironaldo131@gmail.com",

    // --- EXCOINBIT (Hizli Akis) ---
    "TRX-EXCOIN"  => "https://excoinbit.online?r=ankaralironaldo131@gmail.com",
    "LTC-EXCOIN"  => "https://excoinbit.online/coin-ltc?r=ankaralironaldo131@gmail.com",
    "USDT-EXCOIN" => "https://excoinbit.online/coin-usdt?r=ankaralironaldo131@gmail.com",
    "SOL-EXCOIN"  => "https://excoinbit.online/coin-sol?r=ankaralironaldo131@gmail.com",
    "DOGE-EXCOIN" => "https://excoinbit.online/coin-doge?r=ankaralironaldo131@gmail.com",
    "BCH-EXCOIN"  => "https://excoinbit.online/coin-bch?r=ankaralironaldo131@gmail.com",
    "PEPE-EXCOIN" => "https://excoinbit.online/coin-pepe?r=ankaralironaldo131@gmail.com"
];

function ekraniTemizle() { (PHP_OS == "Linux") ? system('clear') : pclose(popen('cls', 'w')); }

function baslikYaz($aktifSayisi = 0, $basarili = 0, $basarisiz = 0, $toplam = 0) {
    global $c;
    echo $c['cyan']."╔════════════════════════════════════════════════════════╗\n";
    echo $c['cyan']."║ ".$c['putih']."        ✦ NINOKICOIN V1 PROFESYONEL FAUCET ✦        ".$c['cyan']."║\n";
    echo $c['cyan']."╠════════════════════════════════════════════════════════╣\n";
    echo $c['cyan']."║ ".$c['putih']."Aktif: ".$c['hijau'].str_pad((string)$aktifSayisi, 3).$c['putih']."  Basarili: ".$c['hijau'].str_pad((string)$basarili, 3).$c['putih']."  Basarisiz: ".$c['merah'].str_pad((string)$basarisiz, 3).$c['putih']."  Toplam: ".$c['kuning'].str_pad((string)$toplam, 3).$c['cyan']."║\n";
    echo $c['cyan']."╚════════════════════════════════════════════════════════╝\n".$c['reset'];
}

function yuklemeGoster($mesaj = 'NınokıCoın yukleniyor') {
    global $c;
    $logo = [
        '███╗   ██╗██╗███╗   ██╗ ██████╗ ██╗  ██╗██╗',
        '████╗  ██║██║████╗  ██║██╔═══██╗██║ ██╔╝██║',
        '██╔██╗ ██║██║██╔██╗ ██║██║   ██║█████╔╝ ██║',
        '██║╚██╗██║██║██║╚██╗██║██║   ██║██╔═██╗ ██║',
        '██║ ╚████║██║██║ ╚████║╚██████╔╝██║  ██╗██║',
        '╚═╝  ╚═══╝╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝╚═╝',
    ];
    foreach ($logo as $satir) echo $c['cyan'].$satir."\n".$c['reset'];
    for ($i = 0; $i <= 20; $i++) {
        echo $c['kuning']."\r$mesaj [".str_repeat('█', $i).str_repeat('░', 20 - $i)."] ".($i * 5)."%".$c['reset'];
        usleep(35000);
    }
    echo "\n";
}


function inputDegeriAl($html, $ad) {
    if (preg_match('/<input\b(?=[^>]*\bname=["\']'.preg_quote($ad, '/').'["\'])(?=[^>]*\bvalue=["\']([^"\']*)["\'])[^>]*>/i', $html, $m)) {
        return html_entity_decode($m[1], ENT_QUOTES);
    }
    return '';
}

function formActionBul($html, $varsayilan, $origin) {
    if (preg_match('/<form\b(?=[^>]*\bmethod=["\']?post["\']?)(?=[^>]*\baction=["\']([^"\']+)["\'])[^>]*>/i', $html, $m)) {
        $action = html_entity_decode($m[1], ENT_QUOTES);
        if (stripos($action, 'http') === 0) return $action;
        return (substr($action, 0, 1) === '/') ? $origin.$action : rtrim($varsayilan, '/').'/'.$action;
    }
    return $varsayilan;
}

function gizliAlanlariEkle($html, &$payload) {
    if (preg_match_all('/<input\b(?=[^>]*\btype=["\']?hidden["\']?)(?=[^>]*\bname=["\']([^"\']+)["\'])(?=[^>]*\bvalue=["\']([^"\']*)["\'])[^>]*>/i', $html, $gizliler, PREG_SET_ORDER)) {
        foreach ($gizliler as $gizli) {
            if ($gizli[1] !== 'captcha') $payload[$gizli[1]] = html_entity_decode($gizli[2], ENT_QUOTES);
        }
    }
}

function httpIstek($url, $method = 'GET', $data = [], $headers = [], $cookie_file = '') {
    $ch = curl_init();
    $options = [
        CURLOPT_URL => $url, CURLOPT_RETURNTRANSFER => true, CURLOPT_HEADER => true,
        CURLOPT_FOLLOWLOCATION => true, CURLOPT_SSL_VERIFYHOST => 0, CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_HTTPHEADER => $headers, CURLOPT_CONNECTTIMEOUT => 30, CURLOPT_TIMEOUT => 30,
        CURLOPT_COOKIEFILE => $cookie_file, CURLOPT_COOKIEJAR => $cookie_file
    ];
    if (strtoupper($method) === 'POST') {
        $options[CURLOPT_POST] = true;
        $options[CURLOPT_POSTFIELDS] = is_array($data) ? http_build_query($data) : $data;
    }
    curl_setopt_array($ch, $options);
    $res = curl_exec($ch);
    $err = curl_error($ch);
    $header_size = curl_getinfo($ch, CURLINFO_HEADER_SIZE);
    curl_close($ch);
    
    if ($res === false) { return ['body' => "CURL_ERROR: $err", 'headers' => '']; }
    return ['body' => substr($res, $header_size), 'headers' => substr($res, 0, $header_size)];
}

// ==========================================
// 1. AYAR BILGILERI
// ==========================================
$kayitliAyarlar = file_exists($ayarDosyasi) ? json_decode(file_get_contents($ayarDosyasi), true) : [];
ekraniTemizle();
yuklemeGoster();
baslikYaz(count($aktif_adresler));
echo $c['putih']."Her calistirmada bilgilerinizi yeniden soruyoruz. Bos birakirsaniz kayitli deger kullanilir.\n".$c['reset'];
echo $c['putih']."FaucetPay e-postasi".(empty($kayitliAyarlar['email']) ? '' : ' ['.$kayitliAyarlar['email'].']').": ".$c['reset'];
$emailGiris = trim(fgets(STDIN));
echo $c['putih']."BypassAllShortlinks API anahtari".(empty($kayitliAyarlar['api_key']) ? '' : ' [kayitli]').": ".$c['reset'];
$apiGiris = trim(fgets(STDIN));
$email = $emailGiris !== '' ? $emailGiris : ($kayitliAyarlar['email'] ?? '');
$api_key = $apiGiris !== '' ? $apiGiris : ($kayitliAyarlar['api_key'] ?? '');
if ($email === '' || $api_key === '') {
    echo $c['merah']."[!] E-posta ve API anahtari zorunludur.\n".$c['reset'];
    exit;
}
file_put_contents($ayarDosyasi, json_encode(["email" => $email, "api_key" => $api_key], JSON_PRETTY_PRINT));
echo $c['hijau']."[+] Bilgiler alindi ve ayarlar guncellendi.\n".$c['reset'];
sleep(1);

// ==========================================
// 2. HCAPTCHA COZME FONKSIYONU
// ==========================================
function hCaptchaCoz($api_key, $pageurl, $sitekey) {
    global $c;
    echo $c['kuning'] . "  [~] hCaptcha gorevi bypass API servisine gonderiliyor...\n" . $c['reset'];
    
    $safe_pageurl = urlencode($pageurl);
    $safe_sitekey = urlencode($sitekey);
    $in_url = "https://bypassallshortlinks.space/in.php?key=$api_key&method=hcaptcha&pageurl=$safe_pageurl&sitekey=$safe_sitekey";
    $api_headers = ["User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)"];
    
    $submit = httpIstek($in_url, 'GET', [], $api_headers);
    
    if (strpos($submit['body'], 'OK|') === false) {
        echo $c['merah'] . "  [!] API gonderimi basarisiz: " . $submit['body'] . "\n" . $c['reset'];
        return false;
    }
    
    $task_id = explode('|', $submit['body'])[1];
    echo $c['biru'] . "  [~] Task ID: $task_id. Sonuc bekleniyor...\n" . $c['reset'];
    
    while (true) {
        sleep(5); 
        $res_url = "https://bypassallshortlinks.space/res.php?key=$api_key&id=$task_id";
        $result = httpIstek($res_url, 'GET', [], $api_headers);
        
        if (strpos($result['body'], 'OK|') !== false) {
            echo $c['hijau'] . "  [+] hCaptcha basariyla cozuldu!\n" . $c['reset'];
            return explode('|', $result['body'])[1];
        } 
        if (strpos($result['body'], 'CAPCHA_NOT_READY') !== false || strpos($result['body'], 'ERROR_SOLVE_PENDING') !== false) {
            echo $c['kuning'] . "      [-] Durum: Beklemede (API bekleniyor)... \r" . $c['reset'];
            continue; 
        }
        if (strpos($result['body'], 'ERROR') !== false) {
            echo $c['merah'] . "\n  [!] API hatasi: " . $result['body'] . "\n" . $c['reset'];
            return false;
        }
    }
}

// ==========================================
// 3. ANA CALISMA DONGUSU
// ==========================================
$basariliKlaim = 0;
$basarisizKlaim = 0;
$toplamDeneme = 0;

while (true) {
    if (empty($aktif_adresler)) {
        ekraniTemizle();
        echo $c['merah']."[!] TUM FAUCETLER LIMITTE VEYA BAKIYESI BITMIS!\n[!] BETIK OTOMATIK OLARAK DURDU.\n".$c['reset'];
        exit;
    }

    foreach ($aktif_adresler as $coin => $target_url) {
        ekraniTemizle();
        baslikYaz(count($aktif_adresler), $basariliKlaim, $basarisizKlaim, $toplamDeneme);
        echo $c['putih']." Hedef  : ".$c['hijau'].$coin.$c['reset']."\n";
        echo $c['putih']." Referans: ".$c['cyan']."ankaralironaldo131@gmail.com".$c['reset']."\n";
        echo $c['cyan']."────────────────────────────────────────────────────────\n".$c['reset'];
        $toplamDeneme++;

        $parsed_url = parse_url($target_url);
        $dynamic_host = $parsed_url['host'];
        $dynamic_origin = $parsed_url['scheme'] . '://' . $dynamic_host;

        $headers = [
            "Host: $dynamic_host",
            "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Origin: $dynamic_origin",
            "Referer: $target_url",
            "Content-Type: application/x-www-form-urlencoded"
        ];

        // 1. ANA SAYFAYI AC 
        echo $c['biru']."[1] Sayfa aciliyor: $coin...\n".$c['reset'];
        $req1 = httpIstek($target_url, "GET", [], $headers, $cerezDosyasi);
        $html = $req1['body'];

        // --- ERKEN KONTROL (ANTI-FRAUD & GENEL LIMIT) ---
        $html_lower = strtolower($html);
        if (strpos($html_lower, "anti fraud") !== false || 
            strpos($html_lower, "antifraud") !== false || 
            strpos($html_lower, "anti-fraud") !== false || 
            strpos($html_lower, "daily claim limit") !== false || 
            strpos($html_lower, "sufficient funds") !== false) {
            
            echo $c['merah']."\n  [!] DUR: Ilk sayfada Anti-Fraud/Limit uyarisi algilandi: $coin!\n".$c['reset'];
            echo $c['kuning']."  [*] Listeden cikariliyor: $coin listeden...\n".$c['reset'];
            unset($aktif_adresler[$coin]); 
            sleep(1); 
            continue;
        }
        // ----------------------------------------------------------

        // [DUZELTME] POST verisi redirectte kaybolmasin diye form action adresini yakala
        $post_url = formActionBul($html, $target_url, $dynamic_origin);

        // ==========================================================
        // MANTIK KOLU: EXCOINBIT (HIZLI AKIS)
        // ==========================================================
        if (strpos($dynamic_host, 'excoinbit.online') !== false) {
            
            preg_match('/<input[^>]+type="text"[^>]+name="([^"]+)"/i', $html, $m_email_name);
            $email_input_name = $m_email_name[1] ?? 'address'; 

            preg_match('/data-sitekey="([^"]+)"/i', $html, $m_sitekey);
            $sitekey = $m_sitekey[1] ?? 'b56ad4c0-05d6-4218-b604-a54c67a8cede';

            if (empty($m_email_name[1])) {
                echo $c['merah']."  [-] E-posta formu bulunamadi. Geciliyor... (Cooldown/Limit olabilir)\n".$c['reset'];
                sleep(1); continue;
            }

            echo $c['hijau']."  [+] Dinamik e-posta alani bulundu: $email_input_name\n".$c['reset'];
            echo $c['biru']."\n[2] hCaptcha bypass baslatiliyor...\n".$c['reset'];
            
            $hcaptcha_token = hCaptchaCoz($api_key, $target_url, $sitekey);

            if ($hcaptcha_token) {
                echo $c['biru']."\n[3] Odul formu gonderiliyor...\n".$c['reset'];
                
                $payload = [
                    $email_input_name => $email, 
                    "g-recaptcha-response" => $hcaptcha_token,
                    "h-captcha-response" => $hcaptcha_token
                ];
                // [DUZELTME] Tum gizli inputlari otomatik al
                gizliAlanlariEkle($html, $payload);

                $req2 = httpIstek($post_url, "POST", $payload, $headers, $cerezDosyasi);
                $responHTML = $req2['body'];

                if (preg_match('/<div class="alert alert-success[^>]*>(.*?)<\/div>/is', $responHTML, $msg)) {
                    $pesan = trim(preg_replace('/\s+/', ' ', strip_tags(str_replace('&times;', '', $msg[1]))));
                    echo $c['hijau']."  [+] BASARILI ($coin): $pesan\n".$c['reset'];
                    $basariliKlaim++;
                } elseif (preg_match('/<div class="alert alert-danger[^>]*>(.*?)<\/div>/is', $responHTML, $msg)) {
                    $pesan = trim(preg_replace('/\s+/', ' ', strip_tags(str_replace('&times;', '', $msg[1]))));
                    echo $c['merah']."  [-] BASARISIZ ($coin): $pesan\n".$c['reset'];
                    $basarisizKlaim++;

                    // BURADA EK ANTI-FRAUD KONTROLU
                    $pesan_lower = strtolower($pesan);
                    if (strpos($pesan_lower, 'limit') !== false ||
                        strpos($pesan_lower, 'sufficient') !== false ||
                        strpos($pesan_lower, 'anti-fraud') !== false ||
                        strpos($pesan_lower, 'antifraud') !== false) {

                        echo $c['kuning']."  [!] Listeden cikariliyor: $coin calisma listesinden...\n".$c['reset'];
                        unset($aktif_adresler[$coin]);
                    }
                } else {
                    echo $c['merah']."  [-] Klaim durumu bilinmiyor / yukleme basarisiz.\n".$c['reset'];
                }
            } else {
                echo $c['merah']."[-] Bypass basarisiz, bu koin geciliyor...\n".$c['reset'];
                $basarisizKlaim++;
            }
        } 
        
        // ==========================================================
        // MANTIK KOLU: MIXTOSHI, EX-FAUCET VE COINVAGANZA
        // ==========================================================
        else {
            preg_match('/data-sitekey=["\']([^"\']+)["\']/i', $html, $m_sitekey);
            
            $session_token = inputDegeriAl($html, 'session-token');
            $sitekey = $m_sitekey[1] ?? 'b56ad4c0-05d6-4218-b604-a54c67a8cede';

            // [DUZELTME] Token neden yok, bunu aciklayan hata tarayicisi
            if (empty($session_token)) {
                echo $c['merah']."  [-] Oturum tokeni alinamadi.\n".$c['reset'];
                if (preg_match('/<div class="alert alert-danger[^>]*>(.*?)<\/div>/is', $html, $m_alert)) {
                    $pesan = trim(preg_replace('/\s+/', ' ', strip_tags(str_replace('&times;', '', $m_alert[1]))));
                    echo $c['kuning']."  [*] Web bilgisi: $pesan\n".$c['reset'];
                    if (strpos(strtolower($pesan), 'wait') !== false) echo $c['kuning']."  [*] Bu faucet cooldown durumunda, simdilik geciliyor...\n".$c['reset'];
                } elseif (strpos($html, 'Just a moment') !== false || strpos($html, 'cf-browser-verification') !== false) {
                    echo $c['merah']."  [!] Cloudflare engeli! Gecerli cookies/clearance gerekli.\n".$c['reset'];
                }
                sleep(1); continue;
            }

            echo $c['hijau']."  [+] Oturum tokeni alindi!\n".$c['reset'];
            echo $c['biru']."\n[2] hCaptcha bypass baslatiliyor...\n".$c['reset'];
            
            $hcaptcha_token = hCaptchaCoz($api_key, $target_url, $sitekey);

            if ($hcaptcha_token) {
                echo $c['biru']."\n[3] Odul formu gonderiliyor...\n".$c['reset'];
                
                $payload = [
                    "address" => $email,
                    "captcha" => "hcaptcha",
                    "g-recaptcha-response" => $hcaptcha_token, 
                    "h-captcha-response" => $hcaptcha_token,
                    "login" => "Verify Captcha"
                ];
                // [DUZELTME] Antibotlinks ve CSRF icin tum gizli formlari al
                gizliAlanlariEkle($html, $payload);

                $req2 = httpIstek($post_url, "POST", $payload, $headers, $cerezDosyasi);
                $responHTML = $req2['body'];

                // BURADA EK ANTI-FRAUD KONTROLU
                $respon_lower = strtolower($responHTML);
                if (strpos($respon_lower, "daily claim limit") !== false ||
                    strpos($respon_lower, "sufficient funds") !== false ||
                    strpos($respon_lower, "anti-fraud") !== false ||
                    strpos($respon_lower, "antifraud") !== false) {

                    echo $c['merah']."\n  [!] STOP: Limit/Bakiye/Anti-Fraud algilandi: $coin!\n".$c['reset'];
                    unset($aktif_adresler[$coin]); 
                    sleep(1); continue;
                }

                if (preg_match('/<div class="alert alert-success[^>]*>(.*?)<\/div>/is', $responHTML, $msg)) {
                    $pesan = trim(preg_replace('/\s+/', ' ', strip_tags(str_replace('&times;', '', $msg[1]))));
                    echo $c['hijau']."  [+] BASARILI ($coin): $pesan\n".$c['reset'];
                    $basariliKlaim++;
                } elseif (preg_match('/<div class="alert alert-danger[^>]*>(.*?)<\/div>/is', $responHTML, $msg)) {
                    $pesan = trim(preg_replace('/\s+/', ' ', strip_tags(str_replace('&times;', '', $msg[1]))));
                    echo $c['merah']."  [-] BASARISIZ ($coin): $pesan\n".$c['reset'];
                    $basarisizKlaim++;
                } else {
                    echo $c['merah']."  [-] Klaim durumu bilinmiyor.\n".$c['reset'];
                }
            } else {
                echo $c['merah']."[-] Bypass basarisiz, bu koin geciliyor...\n".$c['reset'];
                $basarisizKlaim++;
            }
        }

        echo $c['kuning']."\n  [*] Sonraki koinden once 1 saniye kisa mola...\n".$c['reset'];
        sleep(1);
    }

    // ==========================================
    // 5. AKILLI BEKLEME (kalan koinlere gore dinamik)
    // ==========================================
    if (!empty($aktif_adresler)) {
        $cooldown_time = 60; // Varsayilan 1 dakika
        foreach ($aktif_adresler as $c_name => $c_url) {
            if (strpos($c_name, 'PEPE-EXCOIN') !== false) { $cooldown_time = max($cooldown_time, 180); } 
            elseif (strpos($c_name, 'EXCOIN') !== false) { $cooldown_time = max($cooldown_time, 120); } 
        }

        echo $c['kuning']."\n[5] Dongu tamamlandi. Akilli bekleme moduna geciliyor ($cooldown_time sn)...\n".$c['reset'];
        for ($i = $cooldown_time; $i > 0; $i--) {
            echo $c['abu']."  [-] Cooldown bekleniyor: $i saniye...\r".$c['reset'];
            sleep(1);
        }
    }
}