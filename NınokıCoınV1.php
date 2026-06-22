<?php
error_reporting(0);
date_default_timezone_set('Europe/Istanbul');

// ANSI RENKLER
$c = [
    'reset' => "\033[0m", 'putih' => "\033[1;37m", 'merah' => "\033[1;31m",
    'hijau' => "\033[1;32m", 'kuning' => "\033[1;33m", 'biru' => "\033[1;34m",
    'cyan' => "\033[1;36m", 'abu' => "\033[0;90m"
];

$cookieFile = __DIR__ . "/cookies.txt";
$logFile = __DIR__ . "/ninokicoin.log";
$pidFile = __DIR__ . "/ninokicoin.pid";

// Cookie dizini yazılabilir mi?
if (!is_writable(dirname($cookieFile))) {
    die("[!] Hata: " . dirname($cookieFile) . " dizinine yazma izni yok.\n");
}

$api_bitti = false;

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
    "TRX-EXCOIN"  => "https://excoinbit.online?r=ankaralironaldo131@gmail.com",
    "LTC-EXCOIN"  => "https://excoinbit.online/coin-ltc?r=ankaralironaldo131@gmail.com",
    "USDT-EXCOIN" => "https://excoinbit.online/coin-usdt?r=ankaralironaldo131@gmail.com",
    "SOL-EXCOIN"  => "https://excoinbit.online/coin-sol?r=ankaralironaldo131@gmail.com",    "DOGE-EXCOIN" => "https://excoinbit.online/coin-doge?r=ankaralironaldo131@gmail.com",
    "BCH-EXCOIN"  => "https://excoinbit.online/coin-bch?r=ankaralironaldo131@gmail.com",
    "PEPE-EXCOIN" => "https://excoinbit.online/coin-pepe?r=ankaralironaldo131@gmail.com"
];

function clear() {
    (PHP_OS == "Linux") ? system('clear') : pclose(popen('cls', 'w'));
}

function argDegeri($ad) {
    global $argv;
    foreach ($argv as $arg) {
        if (strpos($arg, $ad . '=') === 0) {
            return substr($arg, strlen($ad) + 1);
        }
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
    $cmd = "nohup $php $script --run-daemon $emailArg $apiArg >> $log 2>&1 & echo $!";
    $pid = trim(shell_exec($cmd));
    if ($pid !== '') {
        file_put_contents($pidFile, $pid);
        echo $c['hijau']."[+] NınokıCoın 7/24 arka plan modu başlatıldı. PID: $pid\n".$c['reset'];
        echo $c['putih']."[*] BypassAllShortlinks bakiyesi/API erişimi bitene kadar çalışır.\n".$c['reset'];        echo $c['putih']."[*] Log dosyası: $logFile\n".$c['reset'];
        echo $c['putih']."[*] Durdurmak için: php " . basename(__FILE__) . " --stop\n".$c['reset'];
    } else {
        echo $c['merah']."[!] Arka plan modu başlatılamadı.\n".$c['reset'];
    }
    exit;
}

function arkaPlanDurdur() {
    global $c, $pidFile;
    $pid = calisanPid($pidFile);
    if (!$pid) {
        echo $c['kuning']."[!] Çalışan arka plan süreci bulunamadı.\n".$c['reset'];
        exit;
    }
    if (function_exists('posix_kill')) @posix_kill($pid, SIGTERM);
    else exec('kill ' . (int)$pid . ' 2>/dev/null');
    @unlink($pidFile);
    echo $c['hijau']."[+] Arka plan süreci durduruldu. PID: $pid\n".$c['reset'];
    exit;
}

function arkaPlanDurumu() {
    global $c, $pidFile, $logFile;
    $pid = calisanPid($pidFile);
    if ($pid) {
        echo $c['hijau']."[+] NınokıCoın arka planda çalışıyor. PID: $pid\n".$c['reset'];
        echo $c['putih']."[*] Log dosyası: $logFile\n".$c['reset'];
    } else {
        echo $c['kuning']."[!] NınokıCoın arka planda çalışmıyor.\n".$c['reset'];
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
        CURLOPT_CONNECTTIMEOUT => 15,
        CURLOPT_TIMEOUT => 15,
        CURLOPT_COOKIEFILE => $cookie_file,
        CURLOPT_COOKIEJAR => $cookie_file
    ];
    if (strtoupper($method) === 'POST') {        $options[CURLOPT_POST] = true;
        $options[CURLOPT_POSTFIELDS] = is_array($data) ? http_build_query($data) : $data;
    }
    curl_setopt_array($ch, $options);
    $res = curl_exec($ch);
    $err = curl_error($ch);
    $header_size = curl_getinfo($ch, CURLINFO_HEADER_SIZE);
    curl_close($ch);
    if ($res === false) {
        return ['body' => "CURL_ERROR: $err", 'headers' => ''];
    }
    return ['body' => substr($res, $header_size), 'headers' => substr($res, 0, $header_size)];
}

function yukleniyor($mesaj = "NınokıCoın hazırlanıyor") {
    global $c;
    clear();
    echo $c['cyan']."╔════════════════════════════════════════════════════════════╗\n";
    echo $c['cyan']."║".$c['putih']."                 NINOKICOIN V1 FAUCET BOT                 ".$c['cyan']."║\n";
    echo $c['cyan']."║".$c['kuning']."              Güvenli başlangıç ve kontrol modu            ".$c['cyan']."║\n";
    echo $c['cyan']."╚════════════════════════════════════════════════════════════╝\n".$c['reset'];
    $animasyon = ['⠋','⠙','⠹','⠸','⠼','⠴','⠦','⠧','⠇','⠏'];
    for ($i = 0; $i < 20; $i++) {
        echo $c['hijau']."\r  ".$animasyon[$i % count($animasyon)]." $mesaj... ".$c['reset'];
        usleep(80000);
    }
    echo "\n";
}

if (in_array('--stop', $argv, true)) arkaPlanDurdur();
if (in_array('--status', $argv, true)) arkaPlanDurumu();

$daemonMode = in_array('--run-daemon', $argv, true);
$backgroundMode = in_array('--background', $argv, true) || in_array('--arka-plan', $argv, true);

if ($daemonMode) {
    $email = base64_decode(argDegeri('--email') ?? '', true) ?: '';
    $api_key = base64_decode(argDegeri('--api-key') ?? '', true) ?: '';
    if ($email === '' || $api_key === '') exit;
    file_put_contents($pidFile, getmypid());
    register_shutdown_function(function() use ($pidFile) {
        if (file_exists($pidFile) && trim(file_get_contents($pidFile)) == getmypid()) @unlink($pidFile);
    });
} else {
    yukleniyor();
    echo $c['putih']."FaucetPay e-posta adresinizi girin: ".$c['reset'];
    $email = trim(fgets(STDIN));
    echo $c['putih']."BypassAllShortlinks API anahtarınızı girin: ".$c['reset'];
    $api_key = trim(fgets(STDIN));
    if ($email === '' || $api_key === '') {        echo $c['merah']."[!] E-posta ve API anahtarı boş bırakılamaz.\n".$c['reset'];
        exit;
    }
    if ($backgroundMode) arkaPlanBaslat($email, $api_key);
}

$istatistik = ['deneme' => 0, 'basarili' => 0, 'basarisiz' => 0, 'limit' => 0];

function hCaptchaCoz($api_key, $pageurl, $sitekey) {
    global $c, $api_bitti;
    echo $c['kuning'] . "  [~] hCaptcha görevi bypass API'sine gönderiliyor...\n" . $c['reset'];
    $safe_pageurl = urlencode($pageurl);
    $safe_sitekey = urlencode($sitekey);
    $in_url = "https://bypassallshortlinks.space/in.php?key=$api_key&method=hcaptcha&pageurl=$safe_pageurl&sitekey=$safe_sitekey";
    $api_headers = ["User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)"];
    $submit = skibidixxx($in_url, 'GET', [], $api_headers);
    if (strpos($submit['body'], 'OK|') === false) {
        echo $c['merah'] . "  [!] API gönderimi başarısız: " . $submit['body'] . "\n" . $c['reset'];
        if (strpos($submit['body'], 'ERROR_ZERO_BALANCE') !== false ||
            strpos($submit['body'], 'ERROR_KEY_DOES_NOT_EXIST') !== false ||
            strpos($submit['body'], 'ERROR_WRONG_USER_KEY') !== false) {
            $api_bitti = true;
            echo $c['merah'] . "  [!] BypassAllShortlinks API bakiyesi/erişimi bitti. 7/24 çalışma durduruluyor.\n" . $c['reset'];
        }
        return false;
    }
    $task_id = explode('|', $submit['body'])[1];
    echo $c['biru'] . "  [~] Task ID: $task_id. Sonuç bekleniyor...\n" . $c['reset'];

    $start_time = time();
    $max_wait = 40; // maksimum 40 saniye

    while (true) {
        if (time() - $start_time > $max_wait) {
            echo $c['merah'] . "\n[!] hCaptcha çözümü zaman aşımına uğradı.\n" . $c['reset'];
            return false;
        }
        sleep(5);
        $res_url = "https://bypassallshortlinks.space/res.php?key=$api_key&id=$task_id";
        $result = skibidixxx($res_url, 'GET', [], $api_headers);
        if (strpos($result['body'], 'OK|') !== false) {
            echo $c['hijau'] . "  [+] hCaptcha başarıyla çözüldü!\n" . $c['reset'];
            return explode('|', $result['body'])[1];
        }
        if (strpos($result['body'], 'CAPCHA_NOT_READY') !== false || strpos($result['body'], 'ERROR_SOLVE_PENDING') !== false) {
            echo $c['kuning'] . "      [-] Durum: Beklemede (API yanıtı bekleniyor)... \r" . $c['reset'];
            continue;
        }
        if (strpos($result['body'], 'ERROR') !== false) {
            echo $c['merah'] . "\n[!] API hatası: " . $result['body'] . "\n" . $c['reset'];            if (strpos($result['body'], 'ERROR_ZERO_BALANCE') !== false ||
                strpos($result['body'], 'ERROR_KEY_DOES_NOT_EXIST') !== false ||
                strpos($result['body'], 'ERROR_WRONG_USER_KEY') !== false ||
                strpos($result['body'], 'ERROR_ZERO_CAPTCHA_FILESIZE') !== false) {
                $api_bitti = true;
                echo $c['merah'] . "  [!] BypassAllShortlinks API bakiyesi/erişimi bitti. 7/24 çalışma durduruluyor.\n" . $c['reset'];
            }
            return false;
        }
    }
}

function getToken($html) {
    $patterns = ['session-token', '_token', 'csrf_token', 'token', 'csrf'];
    foreach ($patterns as $p) {
        if (preg_match('/name="' . preg_quote($p, '/') . '"\s*value="([^"]+)"/i', $html, $m)) {
            return $m[1];
        }
    }
    return '';
}

while (true) {
    if ($api_bitti) {
        echo $c['merah']."[!] API bittiği için betik durduruldu.\n".$c['reset'];
        exit;
    }
    if (empty($active_urls)) {
        clear();
        echo $c['merah']."[!] TÜM FAUCETLER LİMİTE TAKILDI VEYA BAKİYE BİTTİ!\n[!] BETİK OTOMATİK OLARAK DURDURULDU.\n".$c['reset'];
        exit;
    }

    foreach ($active_urls as $coin => $target_url) {
        $istatistik['deneme']++;
        clear();
        echo $c['cyan']."╔════════════════════════════════════════════════════════════╗\n";
        echo $c['cyan']."║".$c['putih']."              🚀 NINOKICOIN V1 ÇOKLU FAUCET 🚀             ".$c['cyan']."║\n";
        echo $c['cyan']."╠════════════════════════════════════════════════════════════╣\n";
        echo $c['putih']."  Hedef koin        : ".$c['hijau'].$coin.$c['reset']."\n";
        echo $c['putih']."  Aktif faucet      : ".$c['hijau'].count($active_urls).$c['reset']."\n";
        echo $c['putih']."  Toplam deneme     : ".$c['kuning'].$istatistik['deneme'].$c['reset']."\n";
        echo $c['putih']."  Başarılı claim    : ".$c['hijau'].$istatistik['basarili'].$c['reset']."\n";
        echo $c['putih']."  Başarısız claim   : ".$c['merah'].$istatistik['basarisiz'].$c['reset']."\n";
        echo $c['putih']."  Limit/çıkarılan   : ".$c['kuning'].$istatistik['limit'].$c['reset']."\n";
        echo $c['cyan']."╚════════════════════════════════════════════════════════════╝\n".$c['reset'];

        $parsed_url = parse_url($target_url);
        $dynamic_host = $parsed_url['host'];
        $dynamic_origin = $parsed_url['scheme'] . '://' . $dynamic_host;        $headers = [
            "Host: $dynamic_host",
            "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Origin: $dynamic_origin",
            "Referer: $target_url",
            "Content-Type: application/x-www-form-urlencoded"
        ];

        echo $c['biru']."[1] Sayfa açılıyor: $coin...\n".$c['reset'];
        $req1 = skibidixxx($target_url, "GET", [], $headers, $cookieFile);
        $html = $req1['body'];

        // Cloudflare kontrolü
        if (strpos($html, 'Just a moment') !== false || strpos($html, 'cf-browser-verification') !== false) {
            echo $c['merah']."  [!] Cloudflare JS Challenge algılandı. Bu site botla geçilemez.\n".$c['reset'];
            unset($active_urls[$coin]);
            $istatistik['limit']++;
            sleep(1);
            continue;
        }

        // EXCOINBIT özel işlem
        if (strpos($dynamic_host, 'excoinbit.online') !== false) {
            preg_match('/<input[^>]+type="text"[^>]+name="([^"]+)"/i', $html, $m_email_name);
            $email_input_name = $m_email_name[1] ?? 'address';
            preg_match('/data-sitekey="([^"]+)"/i', $html, $m_sitekey);
            $sitekey = $m_sitekey[1] ?? 'b56ad4c0-05d6-4218-b604-a54c67a8cede';

            if (empty($m_email_name[1])) {
                echo $c['merah']."  [-] E-posta alanı bulunamadı. Atlanıyor...\n".$c['reset'];
                sleep(1); continue;
            }

            echo $c['hijau']."  [+] Dinamik e-posta alanı: $email_input_name\n".$c['reset'];
            echo $c['biru']."\n[2] hCaptcha bypass başlatılıyor...\n".$c['reset'];
            $hcaptcha_token = hCaptchaCoz($api_key, $target_url, $sitekey);
            if (!$hcaptcha_token) {
                if ($api_bitti) exit;
                sleep(1); continue;
            }

            echo $c['biru']."\n[3] Ödül formu gönderiliyor...\n".$c['reset'];
            $payload = [
                $email_input_name => $email,
                "g-recaptcha-response" => $hcaptcha_token,
                "h-captcha-response" => $hcaptcha_token
            ];
            preg_match_all('/<input[^>]+type="hidden"[^>]+name="([^"]+)"[^>]*value="([^"]*)"/i', $html, $hiddens);
            if (!empty($hiddens[1])) {
                for ($i = 0; $i < count($hiddens[1]); $i++) {                    if ($hiddens[1][$i] != 'captcha') $payload[$hiddens[1][$i]] = $hiddens[2][$i];
                }
            }

            $post_url = !empty($m_action[1]) ? ($m_action[1][0] === '/' ? $dynamic_origin . $m_action[1] : rtrim($target_url, '/') . '/' . $m_action[1]) : $target_url;
            $req2 = skibidixxx($post_url, "POST", $payload, $headers, $cookieFile);
            $responHTML = $req2['body'];

            $res_lower = strtolower(strip_tags($responHTML));
            $success_keywords = ['congratulations', 'successfully', 'claimed', 'reward', 'success', 'thank you'];
            $fail_keywords = ['limit', 'sufficient funds', 'anti-fraud', 'antifraud', 'wait', 'cooldown'];

            $is_success = false;
            foreach ($success_keywords as $kw) {
                if (strpos($res_lower, $kw) !== false) { $is_success = true; break; }
            }

            $is_limit = false;
            foreach ($fail_keywords as $kw) {
                if (strpos($res_lower, $kw) !== false) { $is_limit = true; break; }
            }

            if ($is_success) {
                echo $c['hijau']."  [+] BAŞARILI ($coin): Genel başarı mesajı algılandı.\n".$c['reset'];
                $istatistik['basarili']++;
            } elseif ($is_limit) {
                echo $c['merah']."  [!] LIMIT/BAKİYE ($coin): Algılandı, listeden çıkarılıyor.\n".$c['reset'];
                unset($active_urls[$coin]);
                $istatistik['limit']++;
            } else {
                echo $c['merah']."  [-] BAŞARISIZ veya bilinmeyen yanıt.\n".$c['reset'];
                $istatistik['basarisiz']++;
            }
            sleep(1);
            continue;
        }

        // Diğer siteler
        preg_match('/<form[^>]+method="POST"[^>]+action="([^"]+)"/i', $html, $m_action);
        $post_url = $target_url;
        if (!empty($m_action[1])) {
            $action_path = $m_action[1];
            if (strpos($action_path, 'http') === false) {
                $post_url = (substr($action_path, 0, 1) === '/') ? $dynamic_origin . $action_path : rtrim($target_url, '/') . '/' . $action_path;
            } else {
                $post_url = $action_path;
            }
        }

        $session_token = getToken($html);        preg_match('/data-sitekey="([^"]+)"/i', $html, $m_sitekey);
        $sitekey = $m_sitekey[1] ?? 'b56ad4c0-05d6-4218-b604-a54c67a8cede';

        if (empty($session_token)) {
            echo $c['merah']."  [-] Session token alınamadı.\n".$c['reset'];
            sleep(1); continue;
        }

        echo $c['hijau']."  [+] Token alındı!\n".$c['reset'];
        echo $c['biru']."\n[2] hCaptcha bypass başlatılıyor...\n".$c['reset'];
        $hcaptcha_token = hCaptchaCoz($api_key, $target_url, $sitekey);
        if (!$hcaptcha_token) {
            if ($api_bitti) exit;
            sleep(1); continue;
        }

        echo $c['biru']."\n[3] Ödül formu gönderiliyor...\n".$c['reset'];
        $payload = [
            "address" => $email,
            "captcha" => "hcaptcha",
            "g-recaptcha-response" => $hcaptcha_token,
            "h-captcha-response" => $hcaptcha_token,
            "login" => "Verify Captcha"
        ];
        preg_match_all('/<input[^>]+type="hidden"[^>]+name="([^"]+)"[^>]*value="([^"]*)"/i', $html, $hiddens);
        if (!empty($hiddens[1])) {
            for ($i = 0; $i < count($hiddens[1]); $i++) {
                if ($hiddens[1][$i] != 'captcha') $payload[$hiddens[1][$i]] = $hiddens[2][$i];
            }
        }

        $req2 = skibidixxx($post_url, "POST", $payload, $headers, $cookieFile);
        $responHTML = $req2['body'];

        $res_lower = strtolower(strip_tags($responHTML));
        $success_keywords = ['congratulations', 'successfully', 'claimed', 'reward', 'success', 'thank you'];
        $fail_keywords = ['limit', 'sufficient funds', 'anti-fraud', 'antifraud', 'wait', 'cooldown'];

        $is_success = false;
        foreach ($success_keywords as $kw) {
            if (strpos($res_lower, $kw) !== false) { $is_success = true; break; }
        }

        $is_limit = false;
        foreach ($fail_keywords as $kw) {
            if (strpos($res_lower, $kw) !== false) { $is_limit = true; break; }
        }

        if ($is_success) {
            echo $c['hijau']."  [+] BAŞARILI ($coin): Genel başarı mesajı algılandı.\n".$c['reset'];            $istatistik['basarili']++;
        } elseif ($is_limit) {
            echo $c['merah']."  [!] LIMIT/BAKİYE ($coin): Algılandı, listeden çıkarılıyor.\n".$c['reset'];
            unset($active_urls[$coin]);
            $istatistik['limit']++;
        } else {
            echo $c['merah']."  [-] BAŞARISIZ veya bilinmeyen yanıt.\n".$c['reset'];
            $istatistik['basarisiz']++;
        }
        sleep(1);
    }

    // Akıllı cooldown
    if (!empty($active_urls)) {
        $cooldown_time = 60;
        foreach ($active_urls as $c_name => $c_url) {
            if (strpos($c_name, 'PEPE-EXCOIN') !== false) $cooldown_time = max($cooldown_time, 180);
            elseif (strpos($c_name, 'EXCOIN') !== false) $cooldown_time = max($cooldown_time, 120);
        }
        echo $c['kuning']."\n[5] Döngü bitti. Cooldown: $cooldown_time sn...\n".$c['reset'];
        for ($i = $cooldown_time; $i > 0; $i--) {
            echo $c['abu']."  [-] Cooldown: $i saniye...\r".$c['reset'];
            sleep(1);
        }
    }
}
