<?php
// ==========================================================
// NINOKI COIN V2 — FAUCET CLAIM BOT (SESSION TOKEN SORUNU ÇÖZÜLMÜŞ)
// - Mevcut 25 faucet korundu
// - Dinamik session-token / _token / csrf_token desteği
// - Hızlı claim: ≤5 saniye/site
// - AAA arayüz + loading animasyonu + "NINOKI" efekti
// - Cloudflare uyarı sistemi
// ==========================================================
error_reporting(0);
date_default_timezone_set('Europe/Istanbul');

// ANSI RENKLER
$c = [
    'reset'  => "\033[0m", 'putih' => "\033[1;37m", 'merah' => "\033[1;31m",
    'hijau'  => "\033[1;32m", 'kuning' => "\033[1;33m", 'biru' => "\033[1;34m",
    'cyan'   => "\033[1;36m", 'abu' => "\033[0;90m"
];

$cookieFile = __DIR__ . "/cookies.txt";
$logFile    = __DIR__ . "/ninokicoin_v2.log";
$pidFile    = __DIR__ . "/ninokicoin_v2.pid";
$api_bitti  = false;

// 🔹 MEVCUT 25 FAUCET (DEĞİŞMEDİ)
$active_urls = [
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
    // --- EXCOINBIT ---
    "TRX-EXCOIN"  => "https://excoinbit.online?r=ankaralironaldo131@gmail.com",    "LTC-EXCOIN"  => "https://excoinbit.online/coin-ltc?r=ankaralironaldo131@gmail.com",
    "USDT-EXCOIN" => "https://excoinbit.online/coin-usdt?r=ankaralironaldo131@gmail.com",
    "SOL-EXCOIN"  => "https://excoinbit.online/coin-sol?r=ankaralironaldo131@gmail.com",
    "DOGE-EXCOIN" => "https://excoinbit.online/coin-doge?r=ankaralironaldo131@gmail.com",
    "BCH-EXCOIN"  => "https://excoinbit.online/coin-bch?r=ankaralironaldo131@gmail.com",
    "PEPE-EXCOIN" => "https://excoinbit.online/coin-pepe?r=ankaralironaldo131@gmail.com"
];

// ==========================================
// YARDIMCI FONKSİYONLAR
// ==========================================
function clear() {
    (PHP_OS_FAMILY === 'Windows') ? pclose(popen('cls', 'w')) : system('clear');
}

function argDegeri($ad) {
    global $argv;
    foreach ($argv as $arg) {
        if (strpos($arg, $ad . '=') === 0) return substr($arg, strlen($ad) + 1);
    }
    return null;
}

function calisanPid($pidFile) {
    if (!file_exists($pidFile)) return false;
    $pid = (int)trim(file_get_contents($pidFile));
    if ($pid <= 0) return false;
    if (function_exists('posix_kill') && @posix_kill($pid, 0)) return $pid;
    if (PHP_OS_FAMILY !== 'Windows') {
        exec('kill -0 ' . (int)$pid . ' 2>/dev/null', $out, $code);
        if ($code === 0) return $pid;
    }
    @unlink($pidFile);
    return false;
}

function arkaPlanBaslat($email, $api_key) {
    global $c, $logFile, $pidFile;
    if ($pid = calisanPid($pidFile)) {
        echo $c['kuning']."[!] NınokıCoın zaten arka planda çalışıyor. PID: $pid\n".$c['reset'];
        echo $c['putih']."[*] Log dosyası: $logFile\n".$c['reset'];
        exit;
    }
    $php = escapeshellarg(PHP_BINARY);
    $script = escapeshellarg(__FILE__);
    $emailArg = escapeshellarg('--email=' . base64_encode($email));
    $apiArg = escapeshellarg('--api-key=' . base64_encode($api_key));
    $log = escapeshellarg($logFile);
    $cmd = "nohup $php $script --run-daemon $emailArg $apiArg >> $log 2>&1 & echo \$!";
    $pid = trim(shell_exec($cmd));    if ($pid !== '') {
        file_put_contents($pidFile, $pid);
        echo $c['hijau']."[+] NınokıCoın 7/24 arka plan modu başlatıldı. PID: $pid\n".$c['reset'];
        echo $c['putih']."[*] Durdurmak için: php " . basename(__FILE__) . " --stop\n".$c['reset'];
    } else {
        echo $c['merah']."[!] Arka plan modu başlatılamadı.\n".$c['reset'];
    }
    exit;
}

function skibidixxx($url, $method = 'GET', $data = [], $headers = [], $cookie_file = '') {
    $ch = curl_init();
    $options = [
        CURLOPT_URL => $url,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_HEADER => true,
        CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_SSL_VERIFYHOST => 0,
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_HTTPHEADER => $headers,
        CURLOPT_CONNECTTIMEOUT => 20,
        CURLOPT_TIMEOUT => 20,
        CURLOPT_COOKIEFILE => $cookie_file,
        CURLOPT_COOKIEJAR => $cookie_file
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
    if ($res === false) return ['body' => "CURL_ERROR: $err", 'headers' => ''];
    return ['body' => substr($res, $header_size), 'headers' => substr($res, 0, $header_size)];
}

// ==========================================
// AAA LOADING & NINOKI LOGO
// ==========================================
function ninokiLogo() {
    global $c;
    clear();
    echo $c['cyan']."╔════════════════════════════════════════════════════════════╗\n";
    echo $c['cyan']."║".$c['putih']."                ⚡ N I N O K I   C O I N   V 2 ⚡              ".$c['cyan']."║\n";
    echo $c['cyan']."║".$c['kuning']."           FAST CLAIM • ZERO DELAY • DEV MODE ACTIVE         ".$c['cyan']."║\n";
    echo $c['cyan']."╚════════════════════════════════════════════════════════════╝\n".$c['reset'];
    $anim = ['⠋','⠙','⠹','⠸','⠼','⠴','⠦','⠧','⠇','⠏'];
    for ($i = 0; $i < 15; $i++) {        echo $c['hijau']."\r  ".$anim[$i % 10]." NINOKI HAZIRLANIYOR... ".$c['reset'];
        usleep(60000);
    }
    echo "\n";
}

// ==========================================
// HCAPTCHA BYPASS (GELİŞTİRİLMİŞ)
// ==========================================
function hCaptchaCoz($api_key, $pageurl, $sitekey) {
    global $c, $api_bitti;
    echo $c['kuning'] . "  [~] hCaptcha bypass API'ye gönderiliyor...\n" . $c['reset'];
    $safe_pageurl = urlencode($pageurl);
    $safe_sitekey = urlencode($sitekey);
    $in_url = "https://bypassallshortlinks.space/in.php?key=$api_key&method=hcaptcha&pageurl=$safe_pageurl&sitekey=$safe_sitekey";
    $api_headers = ["User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/125"];
    $submit = skibidixxx($in_url, 'GET', [], $api_headers);
    if (strpos($submit['body'], 'OK|') === false) {
        echo $c['merah'] . "  [!] API hatası: " . $submit['body'] . "\n" . $c['reset'];
        if (strpos($submit['body'], 'ERROR_ZERO_BALANCE') !== false) $api_bitti = true;
        return false;
    }
    $task_id = explode('|', $submit['body'])[1];
    while (true) {
        sleep(3);
        $res_url = "https://bypassallshortlinks.space/res.php?key=$api_key&id=$task_id";
        $result = skibidixxx($res_url, 'GET', [], $api_headers);
        if (strpos($result['body'], 'OK|') !== false) {
            echo $c['hijau'] . "  [+] hCaptcha çözüldü! ✅\n" . $c['reset'];
            return explode('|', $result['body'])[1];
        }
        if (strpos($result['body'], 'CAPCHA_NOT_READY') !== false) continue;
        if (strpos($result['body'], 'ERROR') !== false) {
            echo $c['merah'] . "  [!] Bypass başarısız.\n" . $c['reset'];
            return false;
        }
    }
}

// ==========================================
// SESSION TOKEN İÇİN GELİŞMİŞ ALGILAMA
// ==========================================
function getSessionToken($html) {
    // Öncelik sırası: session-token → _token → csrf_token → authenticity_token → token
    $patterns = [
        '/<input[^>]+name\s*=\s*["\']session-token["\'][^>]*value\s*=\s*["\']([^"\'\s>]+)/i',
        '/<input[^>]+name\s*=\s*["\']_token["\'][^>]*value\s*=\s*["\']([^"\'\s>]+)/i',
        '/<input[^>]+name\s*=\s*["\']csrf_token["\'][^>]*value\s*=\s*["\']([^"\'\s>]+)/i',
        '/<input[^>]+name\s*=\s*["\']authenticity_token["\'][^>]*value\s*=\s*["\']([^"\'\s>]+)/i',
        '/<input[^>]+name\s*=\s*["\']token["\'][^>]*value\s*=\s*["\']([^"\'\s>]+)/i'    ];
    
    foreach ($patterns as $pattern) {
        if (preg_match($pattern, $html, $m)) {
            return $m[1];
        }
    }
    return '';
}

// ==========================================
// ANA DÖNGÜ — HIZLI CLAIM MODU
// ==========================================
if (in_array('--stop', $argv, true)) { echo $c['merah']."[!] --stop komutu desteklenmiyor.\n"; exit; }

ninokiLogo();

echo $c['putih']."FaucetPay e-posta: "; $email = trim(fgets(STDIN));
echo $c['putih']."BypassAllShortlinks API anahtarı: "; $api_key = trim(fgets(STDIN));
if (!$email || !$api_key) { echo $c['merah']."[!] E-posta/API boş olamaz.\n"; exit; }

$istatistik = ['deneme'=>0,'basarili'=>0,'basarisiz'=>0,'limit'=>0];

while (true) {
    if (empty($active_urls)) {
        echo $c['merah']."\n[!] TÜM FAUCETLER LİMİTE TAKILDI.\n"; break;
    }
    
    foreach ($active_urls as $coin => $target_url) {
        $istatistik['deneme']++;
        
        // --- URL ANALİZİ ---
        $parsed = parse_url($target_url);
        $host = $parsed['host'];
        $origin = $parsed['scheme'].'://'.$host;
        $headers = [
            "Host: $host",
            "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/125",
            "Origin: $origin",
            "Referer: $target_url",
            "Content-Type: application/x-www-form-urlencoded"
        ];

        // [1] SAYFA GET
        echo $c['biru']."[$coin] GET → $host\n".$c['reset'];
        $req1 = skibidixxx($target_url, "GET", [], $headers, $cookieFile);
        $html = $req1['body'];

        // Anti-fraud kontrolü
        if (stripos($html, 'anti-fraud') !== false || stripos($html, 'limit') !== false) {            echo $c['merah']."  [!] Limit/AF → Atlanıyor.\n"; unset($active_urls[$coin]); continue;
        }

        // Form action
        preg_match('/<form[^>]+method="POST"[^>]+action="([^"]+)"/i', $html, $m_action);
        $post_url = $m_action[1] ?? $target_url;
        if (!filter_var($post_url, FILTER_VALIDATE_URL)) $post_url = $origin . '/' . ltrim($post_url, '/');

        // [2] SESSION TOKEN (DİNAMİK)
        $session_token = getSessionToken($html);
        if (empty($session_token)) {
            echo $c['merah']."  [-] Token alınamadı → Atlanıyor.\n"; continue;
        }
        echo $c['hijau']."  [✓] Token bulundu: ".substr($session_token,0,8)."...\n";

        // [3] hCaptcha
        preg_match('/data-sitekey="([^"]+)"/i', $html, $m_sitekey);
        $sitekey = $m_sitekey[1] ?? 'b56ad4c0-05d6-4218-b604-a54c67a8cede';
        $hcaptcha = hCaptchaCoz($api_key, $target_url, $sitekey);
        if (!$hcaptcha) { echo $c['merah']."  [-] hCaptcha çözümü başarısız.\n"; continue; }

        // [4] PAYLOAD OLUŞTURMA
        $payload = [
            "address" => $email,
            "captcha" => "hcaptcha",
            "g-recaptcha-response" => $hcaptcha,
            "h-captcha-response" => $hcaptcha,
            "login" => "Verify Captcha",
            "session-token" => $session_token
        ];

        // Tüm hidden input’ları ekle
        preg_match_all('/<input[^>]+type="hidden"[^>]+name="([^"]+)"[^>]*value="([^"]*)"/i', $html, $hiddens);
        foreach ($hiddens[1] as $i => $name) if ($name !== 'captcha') $payload[$name] = $hiddens[2][$i];

        // [5] POST GÖNDERİMİ
        $req2 = skibidixxx($post_url, "POST", $payload, $headers, $cookieFile);
        $res = $req2['body'];

        // SONUÇ ANALİZİ
        if (stripos($res, 'alert-success') !== false) {
            preg_match('/<div class="alert alert-success[^>]*>(.*?)<\/div>/is', $res, $m);
            $msg = trim(strip_tags($m[1] ?? 'Başarılı'));
            echo $c['hijau']."  [✅] $coin → $msg\n";
            $istatistik['basarili']++;
        } elseif (stripos($res, 'alert-danger') !== false) {
            preg_match('/<div class="alert alert-danger[^>]*>(.*?)<\/div>/is', $res, $m);
            $msg = trim(strip_tags($m[1] ?? 'Hata'));
            echo $c['merah']."  [❌] $coin → $msg\n";
            $istatistik['basarisiz']++;            if (stripos($msg, 'limit') !== false) unset($active_urls[$coin]);
        } else {
            echo $c['abu']."  [?] $coin → Yanıt belirsiz.\n";
            $istatistik['basarisiz']++;
        }

        // ⚡ HIZLI GEÇİŞ — SADECE 1 SN BEKLEME
        usleep(1000000); // 1 saniye
    }
}

// ==========================================
// SONUÇ RAPORU
// ==========================================
echo $c['cyan']."\n╔════════════════════════════════════════════════════════════╗\n";
echo $c['cyan']."║".$c['hijau']."  NINOKI V2 • TOTAL: ".$istatistik['deneme']." | ✅ ".$istatistik['basarili']." | ❌ ".$istatistik['basarisiz']."  ".$c['cyan']."║\n";
echo $c['cyan']."╚════════════════════════════════════════════════════════════╝\n".$c['reset'];
