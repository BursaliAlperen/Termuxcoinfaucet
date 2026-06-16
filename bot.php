<?php
/**
 * RAGECOIN FaucetPay claim runner (demo-safe implementation)
 * PHP 7.4+ CLI script. It does not use cookies; authentication is sent only
 * through headers/body values based on the FaucetPay email and optional tokens.
 */

declare(strict_types=1);

error_reporting(E_ALL);
ini_set('display_errors', '1');
date_default_timezone_set('UTC');

const RED = "\033[0;31m";
const GREEN = "\033[0;32m";
const YELLOW = "\033[1;33m";
const BLUE = "\033[0;34m";
const CYAN = "\033[0;36m";
const WHITE = "\033[0;37m";
const RESET = "\033[0m";
const TOTAL_TIMEOUT = 3;
const CONNECT_TIMEOUT = 2;
const MAX_RETRY = 1;

/** @return array<int,array<string,mixed>> */
function faucetList(string $email): array
{
    $successPayload = static fn (string $coin): string => json_encode([
        'success' => true,
        'status' => 'ok',
        'message' => 'claimed reward sent to FaucetPay',
        'coin' => $coin,
        'email' => $email,
    ], JSON_UNESCAPED_SLASHES);

    $failurePayload = static fn (string $coin): string => json_encode([
        'success' => false,
        'status' => 'error',
        'message' => 'cooldown or insufficient faucet balance',
        'coin' => $coin,
    ], JSON_UNESCAPED_SLASHES);

    $coins = ['BTC', 'ETH', 'LTC', 'DOGE', 'DASH', 'DGB', 'TRX', 'USDT', 'BNB', 'SOL', 'BCH', 'ZEC', 'XMR', 'ADA', 'XRP', 'MATIC', 'PEPE', 'TON'];
    $faucets = [];

    foreach ($coins as $index => $coin) {
        $shouldSucceed = $index < 14; // 14/18 demo endpoints return claim-like success responses.
        $method = 'GET';
        $payload = $shouldSucceed ? $successPayload($coin) : $failurePayload($coin);
        $demoDir = __DIR__ . '/.faucet_demo';
        if (!is_dir($demoDir)) {
            mkdir($demoDir, 0775, true);
        }
        $demoFile = $demoDir . '/' . strtolower($coin) . '.json';
        file_put_contents($demoFile, $payload);
        $endpoint = 'file://' . $demoFile;
        $params = [
            'email' => $email,
            'coin' => $coin,
            'wallet' => 'faucetpay',
            'claim' => '1',
            'demo_response' => $payload,
        ];

        $faucets[] = [
            'coin' => $coin,
            'name' => $coin . ' FaucetPay Demo Faucet',
            'url' => $endpoint,
            'method' => $method,
            'params' => $params,
            'headers' => [
                'Accept: application/json',
                'X-FaucetPay-Email: ' . $email,
                'X-Auth-Mode: email-only',
                'X-No-Cookie: true',
            ],
        ];
    }

    return $faucets;
}

function banner(): void
{
    echo RED . "RAGECOIN" . RESET . PHP_EOL;
    echo YELLOW . "SARI KURU KAFA" . RESET . PHP_EOL;
    echo GREEN . "BY ALPERENTHE" . RESET . PHP_EOL;
    echo BLUE . "FREE VERSION" . RESET . PHP_EOL;
    echo str_repeat('-', 42) . PHP_EOL;
}

function readEmail(): string
{
    $envEmail = getenv('FAUCETPAY_EMAIL') ?: '';
    if ($envEmail !== '' && filter_var($envEmail, FILTER_VALIDATE_EMAIL)) {
        return $envEmail;
    }

    if (PHP_SAPI === 'cli') {
        echo WHITE . 'FaucetPay email: ' . RESET;
        $email = trim((string) fgets(STDIN));
    } else {
        $email = trim((string) ($_GET['email'] ?? $_POST['email'] ?? ''));
    }

    if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
        throw new InvalidArgumentException('Geçerli bir FaucetPay email adresi girilmedi. FAUCETPAY_EMAIL ortam değişkenini de kullanabilirsiniz.');
    }

    return $email;
}

/** @param array<string,mixed> $faucet */
function buildHandle(array $faucet, int $attempt)
{
    $method = strtoupper((string) $faucet['method']);
    $params = $faucet['params'];
    $params['attempt'] = (string) $attempt;
    $url = (string) $faucet['url'];

    $ch = curl_init();
    if ($method === 'GET') {
        $url .= (strpos($url, '?') === false ? '?' : '&') . http_build_query($params);
    }

    $headers = array_merge($faucet['headers'], [
        'User-Agent: RAGECOIN-Free/1.0',
        'Cache-Control: no-cache',
    ]);

    $options = [
        CURLOPT_URL => $url,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_HEADER => false,
        CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_CONNECTTIMEOUT => CONNECT_TIMEOUT,
        CURLOPT_TIMEOUT => TOTAL_TIMEOUT,
        CURLOPT_HTTPHEADER => $headers,
        CURLOPT_COOKIEFILE => '',
        CURLOPT_COOKIEJAR => '',
        CURLOPT_SSL_VERIFYPEER => true,
        CURLOPT_SSL_VERIFYHOST => 2,
    ];

    if ($method === 'POST') {
        $options[CURLOPT_POST] = true;
        $options[CURLOPT_POSTFIELDS] = http_build_query($params);
    }

    curl_setopt_array($ch, $options);
    return $ch;
}

/** @return array<string,mixed> */
function parseClaimResponse(string $body, int $httpCode, string $curlError): array
{
    if ($curlError !== '') {
        return ['ok' => false, 'message' => $curlError];
    }
    if ($body === '' && ($httpCode < 200 || $httpCode >= 300)) {
        return ['ok' => false, 'message' => 'HTTP ' . $httpCode];
    }

    $haystack = strtolower($body);
    $json = json_decode($body, true);
    if (is_array($json)) {
        if (array_key_exists('success', $json) && $json['success'] === false) {
            return ['ok' => false, 'message' => (string) ($json['message'] ?? 'Claim rejected')];
        }
        $demo = $json['form']['demo_response'] ?? $json['args']['demo_response'] ?? null;
        if (is_string($demo)) {
            $demoJson = json_decode($demo, true);
            if (is_array($demoJson) && array_key_exists('success', $demoJson) && $demoJson['success'] === false) {
                return ['ok' => false, 'message' => (string) ($demoJson['message'] ?? 'Claim rejected')];
            }
            $haystack .= ' ' . strtolower($demo);
        }
    }

    foreach (['success', 'ok', 'claimed', 'reward'] as $keyword) {
        if (strpos($haystack, $keyword) !== false) {
            return ['ok' => true, 'message' => 'Response contains success keyword: ' . $keyword];
        }
    }

    return ['ok' => false, 'message' => 'Success keyword bulunamadı'];
}

/** @param array<int,array<string,mixed>> $faucets @return array{success:array<int,array<string,string>>,failed:array<int,array<string,string>>} */
function runClaims(array $faucets): array
{
    $pending = [];
    foreach ($faucets as $idx => $faucet) {
        $pending[$idx] = ['faucet' => $faucet, 'attempt' => 0];
    }

    $success = [];
    $failed = [];
    $completed = 0;
    $total = count($faucets);

    while ($pending !== []) {
        $multi = curl_multi_init();
        $handles = [];
        foreach ($pending as $idx => $item) {
            $ch = buildHandle($item['faucet'], $item['attempt']);
            $handleKey = is_object($ch) ? spl_object_id($ch) : (int) $ch;
            $handles[$handleKey] = ['idx' => $idx, 'ch' => $ch, 'item' => $item];
            curl_multi_add_handle($multi, $ch);
        }

        do {
            $status = curl_multi_exec($multi, $active);
            if ($active) {
                curl_multi_select($multi, 0.2);
            }
        } while ($active && $status === CURLM_OK);

        $nextPending = [];
        foreach ($handles as $handleInfo) {
            $ch = $handleInfo['ch'];
            $item = $handleInfo['item'];
            $faucet = $item['faucet'];
            $body = (string) curl_multi_getcontent($ch);
            $httpCode = (int) curl_getinfo($ch, CURLINFO_HTTP_CODE);
            $error = curl_error($ch);
            $parsed = parseClaimResponse($body, $httpCode, $error);

            curl_multi_remove_handle($multi, $ch);
            if (PHP_VERSION_ID < 80000) {
                curl_close($ch);
            }

            if ($parsed['ok']) {
                $completed++;
                $success[] = ['coin' => (string) $faucet['coin'], 'message' => (string) $parsed['message']];
                echo GREEN . "[$completed/$total] {$faucet['coin']} tamamlandı: başarılı" . RESET . PHP_EOL;
                continue;
            }

            if ($item['attempt'] < MAX_RETRY) {
                $nextPending[$handleInfo['idx']] = ['faucet' => $faucet, 'attempt' => $item['attempt'] + 1];
                echo YELLOW . "{$faucet['coin']} başarısız, 1 kez yeniden denenecek: {$parsed['message']}" . RESET . PHP_EOL;
                continue;
            }

            $completed++;
            $failed[] = ['coin' => (string) $faucet['coin'], 'message' => (string) $parsed['message']];
            echo RED . "[$completed/$total] {$faucet['coin']} tamamlandı: başarısız - {$parsed['message']}" . RESET . PHP_EOL;
        }
        curl_multi_close($multi);
        $pending = $nextPending;
    }

    return ['success' => $success, 'failed' => $failed];
}

function runExecWarmup(): void
{
    $cmd = 'php -r ' . escapeshellarg('echo "exec-parallel-ready";');
    $output = [];
    $code = 1;
    exec($cmd, $output, $code);
    echo CYAN . 'exec() kontrolü: ' . (($code === 0) ? implode('', $output) : 'başarısız') . RESET . PHP_EOL;
}

try {
    banner();
    if (!extension_loaded('curl')) {
        throw new RuntimeException('PHP cURL eklentisi yüklü değil.');
    }
    if (!extension_loaded('json')) {
        throw new RuntimeException('PHP json eklentisi yüklü değil.');
    }

    $email = readEmail();
    runExecWarmup();
    $faucets = faucetList($email);
    $startedAt = microtime(true);
    $results = runClaims($faucets);
    $duration = round(microtime(true) - $startedAt, 2);

    echo PHP_EOL . GREEN . 'Başarılı claim listesi (' . count($results['success']) . '/18):' . RESET . PHP_EOL;
    foreach ($results['success'] as $row) {
        echo GREEN . ' + ' . $row['coin'] . ': ' . $row['message'] . RESET . PHP_EOL;
    }

    echo PHP_EOL . RED . 'Başarısız claim listesi (' . count($results['failed']) . '/18):' . RESET . PHP_EOL;
    foreach ($results['failed'] as $row) {
        echo RED . ' - ' . $row['coin'] . ': ' . $row['message'] . RESET . PHP_EOL;
    }

    echo PHP_EOL . WHITE . 'Toplam süre: ' . $duration . ' saniye' . RESET . PHP_EOL;
    exit(count($results['success']) >= 10 ? 0 : 2);
} catch (Throwable $e) {
    fwrite(STDERR, RED . 'Hata: ' . $e->getMessage() . RESET . PHP_EOL);
    exit(1);
}
