<?php
declare(strict_types=1);

date_default_timezone_set('Europe/Istanbul');

const APP_NAME = 'NınokıCoın V1 Faucet Bot';
const CONNECT_TIMEOUT = 5;
const REQUEST_TIMEOUT = 12;
const CAPTCHA_CONNECT_TIMEOUT = 5;
const CAPTCHA_REQUEST_TIMEOUT = 10;
const CAPTCHA_POLL_INTERVAL = 2;
const CAPTCHA_MAX_ATTEMPTS = 45;
const STEP_RETRY_LIMIT = 2;
const STEP_RETRY_DELAY_US = 250000;
const DEFAULT_LOOP_SLEEP = 60;
const MAX_RECOVERABLE_ERRORS = 5;

$debugMode = in_array('--debug', $argv, true) || getenv('NINOKI_DEBUG') === '1';
error_reporting($debugMode ? E_ALL : (E_ALL & ~E_NOTICE & ~E_WARNING & ~E_DEPRECATED));
ini_set('display_errors', $debugMode ? '1' : '0');
ini_set('log_errors', '1');

$c = [
    'reset' => "\033[0m", 'putih' => "\033[1;37m", 'merah' => "\033[1;31m",
    'hijau' => "\033[1;32m", 'kuning' => "\033[1;33m", 'biru' => "\033[1;34m",
    'cyan' => "\033[1;36m", 'abu' => "\033[0;90m"
];

$baseDir = __DIR__;
$cookieFile = $baseDir . '/cookies.txt';
$logFile = $baseDir . '/ninokicoin.log';
$pidFile = $baseDir . '/ninokicoin.pid';
$lockFile = $baseDir . '/ninokicoin.lock';
$api_bitti = false;
$shutdownRequested = false;
$lockHandle = null;
$curlPool = [];

$active_urls = [
    'LTC-MIX' => 'https://mixtoshi.com?r=ankaralironaldo131@gmail.com',
    'USDT-MIX' => 'https://mixtoshi.com/free-usdt?r=ankaralironaldo131@gmail.com',
    'PEPE-MIX' => 'https://mixtoshi.com/free-pepe?r=ankaralironaldo131@gmail.com',
    'SOL-MIX' => 'https://mixtoshi.com/free-sol?r=ankaralironaldo131@gmail.com',
    'DOGE-MIX' => 'https://mixtoshi.com/free-doge?r=ankaralironaldo131@gmail.com',
    'TRX-MIX' => 'https://mixtoshi.com/free-trx?r=ankaralironaldo131@gmail.com',
    'LTC-EX' => 'https://ex-faucet.xyz/faucet-ltc?r=ankaralironaldo131@gmail.com',
    'USDT-EX' => 'https://ex-faucet.xyz/faucet-usdt?r=ankaralironaldo131@gmail.com',
    'PEPE-EX' => 'https://ex-faucet.xyz/faucet-pepe?r=ankaralironaldo131@gmail.com',
    'SOL-EX' => 'https://ex-faucet.xyz/faucet-sol?r=ankaralironaldo131@gmail.com',
    'DOGE-EX' => 'https://ex-faucet.xyz/faucet-doge?r=ankaralironaldo131@gmail.com',
    'TRX-EX' => 'https://ex-faucet.xyz/faucet-trx?r=ankaralironaldo131@gmail.com',
    'USDT-VGNZ' => 'https://coinvaganza.xyz?r=ankaralironaldo131@gmail.com',
    'LTC-VGNZ' => 'https://coinvaganza.xyz/claim-ltc?r=ankaralironaldo131@gmail.com',
    'DOGE-VGNZ' => 'https://coinvaganza.xyz/claim-doge?r=ankaralironaldo131@gmail.com',
    'SOL-VGNZ' => 'https://coinvaganza.xyz/claim-sol?r=ankaralironaldo131@gmail.com',
    'PEPE-VGNZ' => 'https://coinvaganza.xyz/claim-pepe?r=ankaralironaldo131@gmail.com',
    'BCH-VGNZ' => 'https://coinvaganza.xyz/claim-bch?r=ankaralironaldo131@gmail.com',
    'TRX-VGNZ' => 'https://coinvaganza.xyz/claim-trx?r=ankaralironaldo131@gmail.com',
    'TRX-EXCOIN' => 'https://excoinbit.online?r=ankaralironaldo131@gmail.com',
    'LTC-EXCOIN' => 'https://excoinbit.online/coin-ltc?r=ankaralironaldo131@gmail.com',
    'USDT-EXCOIN' => 'https://excoinbit.online/coin-usdt?r=ankaralironaldo131@gmail.com',
    'SOL-EXCOIN' => 'https://excoinbit.online/coin-sol?r=ankaralironaldo131@gmail.com',
    'DOGE-EXCOIN' => 'https://excoinbit.online/coin-doge?r=ankaralironaldo131@gmail.com',
    'BCH-EXCOIN' => 'https://excoinbit.online/coin-bch?r=ankaralironaldo131@gmail.com',
    'PEPE-EXCOIN' => 'https://excoinbit.online/coin-pepe?r=ankaralironaldo131@gmail.com'
];

function writeLog(string $message, string $level = 'INFO'): void
{
    global $logFile;
    file_put_contents($logFile, '[' . date('Y-m-d H:i:s') . "] [$level] $message\n", FILE_APPEND | LOCK_EX);
}

function out(string $message, string $color = 'reset', bool $newline = true): void
{
    global $c, $daemonMode;
    $plain = preg_replace('/\033\[[0-9;]*m/', '', $message);
    writeLog($plain);
    if (!$daemonMode) {
        echo ($c[$color] ?? '') . $message . ($c['reset'] ?? '') . ($newline ? "\n" : '');
    }
}

function argDegeri(string $ad): ?string
{
    global $argv;
    foreach ($argv as $arg) {
        if (strpos($arg, $ad . '=') === 0) return substr($arg, strlen($ad) + 1);
    }
    return null;
}

function clearScreen(): void
{
    global $daemonMode;
    if (!$daemonMode && PHP_SAPI === 'cli') echo "\033[2J\033[H";
}

function acquireLock(string $lockFile): bool
{
    global $lockHandle;
    $lockHandle = fopen($lockFile, 'c+');
    if (!$lockHandle || !flock($lockHandle, LOCK_EX | LOCK_NB)) return false;
    ftruncate($lockHandle, 0);
    fwrite($lockHandle, (string)getmypid());
    fflush($lockHandle);
    return true;
}

function calisanPid(string $pidFile): int|false
{
    if (!is_file($pidFile)) return false;
    $pid = (int)trim((string)file_get_contents($pidFile));
    if ($pid <= 0) return false;
    if (function_exists('posix_kill') && @posix_kill($pid, 0)) return $pid;
    @unlink($pidFile);
    return false;
}

function arkaPlanBaslat(string $email, string $api_key): void
{
    global $logFile, $pidFile;
    if ($pid = calisanPid($pidFile)) { out("[!] Zaten çalışıyor. PID: $pid", 'kuning'); exit; }
    $cmd = sprintf('nohup %s %s --run-daemon --email=%s --api-key=%s >> %s 2>&1 & echo $!', escapeshellarg(PHP_BINARY), escapeshellarg(__FILE__), escapeshellarg(base64_encode($email)), escapeshellarg(base64_encode($api_key)), escapeshellarg($logFile));
    $pid = trim((string)shell_exec($cmd));
    if ($pid !== '') { file_put_contents($pidFile, $pid); out("[+] Arka plan modu başlatıldı. PID: $pid", 'hijau'); out("[*] Log: $logFile", 'putih'); }
    else out('[!] Arka plan modu başlatılamadı.', 'merah');
    exit;
}

function arkaPlanDurdur(): void
{
    global $pidFile;
    $pid = calisanPid($pidFile);
    if (!$pid) { out('[!] Çalışan süreç bulunamadı.', 'kuning'); exit; }
    if (function_exists('posix_kill')) @posix_kill($pid, SIGTERM); else exec('kill ' . (int)$pid . ' 2>/dev/null');
    @unlink($pidFile);
    out("[+] Süreç durduruldu. PID: $pid", 'hijau');
    exit;
}

function arkaPlanDurumu(): void
{
    global $pidFile, $logFile;
    $pid = calisanPid($pidFile);
    out($pid ? "[+] Arka planda çalışıyor. PID: $pid" : '[!] Arka planda çalışmıyor.', $pid ? 'hijau' : 'kuning');
    out("[*] Log: $logFile", 'putih');
    exit;
}

function shutdownNow(): void { global $shutdownRequested; $shutdownRequested = true; writeLog('Durdurma sinyali alındı.'); }
function safeSleep(int $seconds): void { global $shutdownRequested; for ($i = 0; $i < $seconds && !$shutdownRequested; $i++) sleep(1); }

function curlRequest(string $url, string $method = 'GET', array|string $data = [], array $headers = [], string $cookie_file = '', int $connectTimeout = CONNECT_TIMEOUT, int $timeout = REQUEST_TIMEOUT, int $retries = STEP_RETRY_LIMIT): array
{
    global $curlPool;
    $host = parse_url($url, PHP_URL_HOST) ?: 'default';
    $key = $host . '|' . $cookie_file;
    $ch = $curlPool[$key] ?? curl_init();
    $curlPool[$key] = $ch;
    $baseHeaders = array_merge(['Connection: keep-alive', 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Encoding: gzip, deflate'], $headers);
    $postFields = is_array($data) ? http_build_query($data) : $data;

    for ($attempt = 0; $attempt <= $retries; $attempt++) {
        curl_setopt_array($ch, [
            CURLOPT_URL => $url, CURLOPT_RETURNTRANSFER => true, CURLOPT_HEADER => true,
            CURLOPT_FOLLOWLOCATION => true, CURLOPT_MAXREDIRS => 3, CURLOPT_SSL_VERIFYHOST => 0,
            CURLOPT_SSL_VERIFYPEER => false, CURLOPT_HTTPHEADER => $baseHeaders,
            CURLOPT_CONNECTTIMEOUT => $connectTimeout, CURLOPT_TIMEOUT => $timeout,
            CURLOPT_ENCODING => '', CURLOPT_TCP_KEEPALIVE => 1, CURLOPT_FORBID_REUSE => false,
            CURLOPT_FRESH_CONNECT => false, CURLOPT_COOKIEFILE => $cookie_file, CURLOPT_COOKIEJAR => $cookie_file,
            CURLOPT_POST => strtoupper($method) === 'POST', CURLOPT_POSTFIELDS => strtoupper($method) === 'POST' ? $postFields : null,
        ]);
        $raw = curl_exec($ch);
        $errno = curl_errno($ch);
        $err = curl_error($ch);
        $info = curl_getinfo($ch);
        if ($raw !== false && $errno === 0 && (int)($info['http_code'] ?? 0) < 500) {
            $headerSize = (int)($info['header_size'] ?? 0);
            return ['ok' => true, 'body' => substr($raw, $headerSize), 'headers' => substr($raw, 0, $headerSize), 'http_code' => (int)$info['http_code'], 'error' => null];
        }
        writeLog("HTTP hata/yeniden deneme ($attempt): $url code=" . ($info['http_code'] ?? 0) . " errno=$errno err=$err", 'WARN');
        if ($attempt < $retries) usleep(STEP_RETRY_DELAY_US * ($attempt + 1));
    }
    return ['ok' => false, 'body' => '', 'headers' => '', 'http_code' => (int)($info['http_code'] ?? 0), 'error' => $err ?: 'HTTP error'];
}

function resolveUrl(string $base, string $origin, string $action): string
{
    if ($action === '' || str_starts_with($action, '#')) return $base;
    if (preg_match('~^https?://~i', $action)) return $action;
    return str_starts_with($action, '/') ? $origin . $action : rtrim(dirname($base), '/') . '/' . $action;
}

function parseForm(string $html, string $target_url, string $origin): array
{
    preg_match('/<form[^>]+method=["\']?POST["\']?[^>]*action=["\']([^"\']+)["\']/i', $html, $mAction);
    preg_match('/<input[^>]+type=["\']?text["\']?[^>]+name=["\']([^"\']+)["\']/i', $html, $mEmail);
    preg_match('/name=["\']session-token["\']\s*value=["\']([^"\']+)["\']/i', $html, $mToken);
    preg_match('/data-sitekey=["\']([^"\']+)["\']/i', $html, $mSitekey);
    preg_match_all('/<input[^>]+type=["\']?hidden["\']?[^>]+name=["\']([^"\']+)["\'][^>]*value=["\']([^"\']*)["\']/i', $html, $hidden);
    $hiddenFields = [];
    foreach (($hidden[1] ?? []) as $i => $name) if ($name !== 'captcha') $hiddenFields[$name] = $hidden[2][$i] ?? '';
    return [
        'post_url' => resolveUrl($target_url, $origin, $mAction[1] ?? ''),
        'email_name' => $mEmail[1] ?? '',
        'session_token' => $mToken[1] ?? '',
        'sitekey' => $mSitekey[1] ?? 'b56ad4c0-05d6-4218-b604-a54c67a8cede',
        'hidden' => $hiddenFields,
    ];
}

function extractAlert(string $html, string $type = 'success'): ?string
{
    if (!preg_match('/<div class="alert alert-' . preg_quote($type, '/') . '[^>]*>(.*?)<\/div>/is', $html, $m)) return null;
    return trim(preg_replace('/\s+/', ' ', strip_tags(str_replace('&times;', '', $m[1]))));
}

function hCaptchaCoz(string $api_key, string $pageurl, string $sitekey): string|false
{
    global $api_bitti;
    out('  [~] hCaptcha görevi API\'ye gönderiliyor...', 'kuning');
    $headers = ['User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)'];
    $inUrl = 'https://bypassallshortlinks.space/in.php?key=' . urlencode($api_key) . '&method=hcaptcha&pageurl=' . urlencode($pageurl) . '&sitekey=' . urlencode($sitekey);
    $submit = curlRequest($inUrl, 'GET', [], $headers, '', CAPTCHA_CONNECT_TIMEOUT, CAPTCHA_REQUEST_TIMEOUT, 1);
    if (!$submit['ok'] || !str_starts_with(trim($submit['body']), 'OK|')) {
        out('  [!] API gönderimi başarısız: ' . ($submit['body'] ?: $submit['error']), 'merah');
        if (str_contains($submit['body'], 'ERROR_ZERO_BALANCE') || str_contains($submit['body'], 'ERROR_KEY_DOES_NOT_EXIST') || str_contains($submit['body'], 'ERROR_WRONG_USER_KEY')) $api_bitti = true;
        return false;
    }
    $taskId = explode('|', trim($submit['body']), 2)[1] ?? '';
    for ($attempt = 1; $attempt <= CAPTCHA_MAX_ATTEMPTS; $attempt++) {
        safeSleep(CAPTCHA_POLL_INTERVAL);
        $resUrl = 'https://bypassallshortlinks.space/res.php?key=' . urlencode($api_key) . '&id=' . urlencode($taskId);
        $result = curlRequest($resUrl, 'GET', [], $headers, '', CAPTCHA_CONNECT_TIMEOUT, CAPTCHA_REQUEST_TIMEOUT, 1);
        $body = trim($result['body']);
        if (str_starts_with($body, 'OK|')) { out('  [+] hCaptcha çözüldü.', 'hijau'); return explode('|', $body, 2)[1] ?? false; }
        if (str_contains($body, 'CAPCHA_NOT_READY') || str_contains($body, 'ERROR_SOLVE_PENDING') || !$result['ok']) continue;
        if (str_contains($body, 'ERROR')) {
            out("  [!] API hatası: $body", 'merah');
            if (str_contains($body, 'ERROR_ZERO_BALANCE') || str_contains($body, 'ERROR_KEY_DOES_NOT_EXIST') || str_contains($body, 'ERROR_WRONG_USER_KEY')) $api_bitti = true;
            return false;
        }
    }
    out('  [!] hCaptcha zaman aşımı: maksimum deneme sayısına ulaşıldı.', 'merah');
    return false;
}

function hasLimitSignal(string $html): bool
{
    $s = strtolower($html);
    return str_contains($s, 'anti fraud') || str_contains($s, 'antifraud') || str_contains($s, 'anti-fraud') || str_contains($s, 'daily claim limit') || str_contains($s, 'sufficient funds');
}

function claimOne(string $coin, string $target_url, string $email, string $api_key, string $cookieFile): string
{
    global $api_bitti;
    $parsed = parse_url($target_url);
    $host = $parsed['host'] ?? '';
    $origin = ($parsed['scheme'] ?? 'https') . '://' . $host;
    $headers = ["Host: $host", 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36', "Origin: $origin", "Referer: $target_url", 'Content-Type: application/x-www-form-urlencoded'];

    out("[1] Sayfa açılıyor: $coin", 'biru');
    $req = curlRequest($target_url, 'GET', [], $headers, $cookieFile);
    if (!$req['ok'] || $req['body'] === '') { out('  [-] Sayfa alınamadı: ' . ($req['error'] ?? 'boş yanıt'), 'merah'); return 'retry'; }
    $html = $req['body'];
    if (hasLimitSignal($html)) { out("  [!] Limit/anti-fraud algılandı: $coin", 'merah'); return 'limit'; }

    $form = parseForm($html, $target_url, $origin);
    $isExcoin = str_contains($host, 'excoinbit.online');
    if ($isExcoin && $form['email_name'] === '') { out('  [-] E-posta alanı bulunamadı.', 'merah'); return 'retry'; }
    if (!$isExcoin && $form['session_token'] === '') {
        $alert = extractAlert($html, 'danger');
        out('  [-] Session Token alınamadı.' . ($alert ? " Web bilgisi: $alert" : ''), 'merah');
        return $alert && hasLimitSignal($alert) ? 'limit' : 'retry';
    }

    $captcha = hCaptchaCoz($api_key, $target_url, $form['sitekey']);
    if (!$captcha) return $api_bitti ? 'api_stop' : 'retry';

    $payload = $isExcoin
        ? [$form['email_name'] => $email, 'g-recaptcha-response' => $captcha, 'h-captcha-response' => $captcha]
        : ['address' => $email, 'captcha' => 'hcaptcha', 'g-recaptcha-response' => $captcha, 'h-captcha-response' => $captcha, 'login' => 'Verify Captcha'];
    $payload = array_merge($payload, $form['hidden']);

    out('[3] Ödül formu gönderiliyor...', 'biru');
    $post = curlRequest($form['post_url'], 'POST', $payload, $headers, $cookieFile);
    if (!$post['ok']) return 'retry';
    $body = $post['body'];
    if (hasLimitSignal($body)) { out("  [!] Limit/bakiye/anti-fraud algılandı: $coin", 'merah'); return 'limit'; }
    if ($msg = extractAlert($body, 'success')) { out("  [+] BAŞARILI ($coin): $msg", 'hijau'); return 'success'; }
    if ($msg = extractAlert($body, 'danger')) { out("  [-] BAŞARISIZ ($coin): $msg", 'merah'); return hasLimitSignal($msg) ? 'limit' : 'failed'; }
    out('  [-] Claim durumu bilinmiyor.', 'merah');
    return 'failed';
}

if (in_array('--stop', $argv, true)) arkaPlanDurdur();
if (in_array('--status', $argv, true)) arkaPlanDurumu();

$daemonMode = in_array('--run-daemon', $argv, true);
$backgroundMode = in_array('--background', $argv, true) || in_array('--arka-plan', $argv, true);

if (PHP_SAPI === 'cli' && function_exists('pcntl_signal')) {
    pcntl_async_signals(true);
    pcntl_signal(SIGTERM, 'shutdownNow');
    pcntl_signal(SIGINT, 'shutdownNow');
}

if ($daemonMode) {
    $email = base64_decode(argDegeri('--email') ?? '', true) ?: '';
    $api_key = base64_decode(argDegeri('--api-key') ?? '', true) ?: '';
    if ($email === '' || $api_key === '') exit(1);
    if (!acquireLock($lockFile)) { writeLog('Başka bir kopya çalışıyor, çıkılıyor.', 'WARN'); exit(0); }
    file_put_contents($pidFile, (string)getmypid());
} else {
    clearScreen();
    out(APP_NAME . ' hazırlanıyor', 'cyan');
    echo $c['putih'] . 'FaucetPay e-posta adresinizi girin: ' . $c['reset'];
    $email = trim((string)fgets(STDIN));
    echo $c['putih'] . 'BypassAllShortlinks API anahtarınızı girin: ' . $c['reset'];
    $api_key = trim((string)fgets(STDIN));
    if ($email === '' || $api_key === '') { out('[!] E-posta ve API anahtarı boş bırakılamaz.', 'merah'); exit(1); }
    if ($backgroundMode) arkaPlanBaslat($email, $api_key);
    if (!acquireLock($lockFile)) { out('[!] Başka bir kopya zaten çalışıyor.', 'kuning'); exit(0); }
    file_put_contents($pidFile, (string)getmypid());
}

register_shutdown_function(function () use ($pidFile, &$curlPool): void {
    foreach ($curlPool as $ch) if (is_resource($ch) || $ch instanceof CurlHandle) curl_close($ch);
    if (is_file($pidFile) && trim((string)file_get_contents($pidFile)) === (string)getmypid()) @unlink($pidFile);
    writeLog('Süreç kapandı.');
});

$istatistik = ['deneme' => 0, 'basarili' => 0, 'basarisiz' => 0, 'limit' => 0];
$recoverableErrors = 0;

while (!$shutdownRequested) {
    if ($api_bitti) { out('[!] API bittiği için betik durduruldu.', 'merah'); break; }
    if (empty($active_urls)) { out('[!] Tüm faucetler limite takıldı veya bakiye bitti.', 'merah'); break; }

    foreach (array_keys($active_urls) as $coin) {
        if ($shutdownRequested || $api_bitti || !isset($active_urls[$coin])) break;
        $istatistik['deneme']++;
        clearScreen();
        out("Hedef: $coin | Aktif: " . count($active_urls) . " | Deneme: {$istatistik['deneme']} | Başarılı: {$istatistik['basarili']} | Başarısız: {$istatistik['basarisiz']} | Limit: {$istatistik['limit']}", 'cyan');

        $status = claimOne($coin, $active_urls[$coin], $email, $api_key, $cookieFile);
        if ($status === 'success') { $istatistik['basarili']++; $recoverableErrors = 0; }
        elseif ($status === 'limit') { $istatistik['limit']++; unset($active_urls[$coin]); $recoverableErrors = 0; }
        elseif ($status === 'api_stop') { $api_bitti = true; break; }
        else { $istatistik['basarisiz']++; $recoverableErrors++; }

        unset($status);
        if ($recoverableErrors >= MAX_RECOVERABLE_ERRORS) {
            out('[!] Ardışık hata sınırı aşıldı; kısa toparlanma beklemesi uygulanıyor.', 'kuning');
            safeSleep(10);
            $recoverableErrors = 0;
        } else {
            usleep(200000);
        }
    }

    if (!$shutdownRequested && !$api_bitti && !empty($active_urls)) {
        $sleep = DEFAULT_LOOP_SLEEP;
        foreach (array_keys($active_urls) as $name) {
            if (str_contains($name, 'PEPE-EXCOIN')) $sleep = max($sleep, 180);
            elseif (str_contains($name, 'EXCOIN')) $sleep = max($sleep, 120);
        }
        out("[5] Döngü bitti. Dinamik bekleme: $sleep sn", 'kuning');
        safeSleep($sleep);
    }
}
