<?php
declare(strict_types=1);

/**
 * ================================================================
 *  NINOKI ClaimCoin - Premium Musluk Botu v3.0 (Refactored)
 *  Surum: 3.0.0 | Yapi: AAA-2026 | Termux & Production Uyumlu
 * ================================================================
 */

error_reporting(E_ALL);
ini_set('display_errors', '0');
date_default_timezone_set('Asia/Jakarta');

/* ================================================================
RENK PALETI
================================================================ */
class R {
    public const S      = "\033[0m";
    public const B      = "\033[1m";
    public const D      = "\033[2m";
    public const KIR    = "\033[0;31m";
    public const YES    = "\033[0;32m";
    public const SAR    = "\033[0;33m";
    public const MAV    = "\033[0;34m";
    public const MAC    = "\033[0;35m";
    public const CAM    = "\033[0;36m";
    public const BEY    = "\033[0;37m";
    public const GRI    = "\033[0;90m";
    public const LKIR   = "\033[0;91m";
    public const LYES   = "\033[0;92m";
    public const LSAR   = "\033[0;93m";
    public const LMAV   = "\033[0;94m";
    public const LMAC   = "\033[0;95m";
    public const LCAM   = "\033[0;96m";
    public const LBEY   = "\033[0;97m";
    public const SIYAH  = "\033[0;30m"; // Fatal error düzeltmesi
    
    public const BG_KIR = "\033[41m";
    public const BG_YES = "\033[42m";
    public const BG_SAR = "\033[43m";
    public const BG_MAV = "\033[44m";
    public const BG_MAC = "\033[45m";
    public const BG_CAM = "\033[46m";
    public const BG_BEY = "\033[47m";
    public const BG_GRI = "\033[100m";
}

/* ================================================================
AAA ARAYUZ - PREMIUM CLI================================================================ */
class UI {
    private static int $w = 70;

    public static function init(): void {
        $cols = @shell_exec('tput cols 2>/dev/null');
        self::$w = (int) $cols;
        if (self::$w < 50) self::$w = 70;
    }

    public static function cls(): void {
        // system() veya popen() yerine güvenli ANSI escape kodu kullanıldı.
        echo "\033[2J\033[H"; 
    }

    private static function stripAnsi(string $text): string {
        return preg_replace('/\x1B\[[0-9;]*m/', '', $text) ?? $text;
    }

    public static function banner(): void {
        $c = R::B . R::LCAM;
        $g = R::LYES;
        $y = R::LSAR;
        $r = R::S;
        
        echo "\n";
        echo $c . "   ██████╗ ██╗███╗   ██╗ ██████╗ ██╗  ██╗██╗     " . $r . "\n";
        echo $c . "   ██╔══██╗██║████╗  ██║██╔═══██╗██║ ██╔╝██║     " . $r . "\n";
        echo $c . "   ██████╔╝██║██╔██╗ ██║██║   ██║█████╔╝ ██║     " . $r . "\n";
        echo $c . "   ██╔══██╗██║██║╚██╗██║██║   ██║██╔═██╗ ██║     " . $r . "\n";
        echo $c . "   ██║  ██║██║██║ ╚████║╚██████╔╝██║  ██╗██║     " . $r . "\n";
        echo $c . "   ╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝╚═╝     " . $r . "\n";
        echo $g . "   ═══════════════════════════════════════════════════" . $r . "\n";
        echo $y . "   NINOKI ClaimCoin - Premium Musluk Botu v3.0      " . $r . "\n";
        echo $g . "   API: bypassallshortlinks.space                   " . $r . "\n";
        echo $g . "   ═══════════════════════════════════════════════════" . $r . "\n";
    }

    public static function box(string $title, string $content, string $color = R::LCAM): void {
        $lines = explode("\n", $content);
        $max = 0;
        foreach ($lines as $line) {
            $l = strlen(self::stripAnsi($line));
            if ($l > $max) $max = $l;
        }
        
        $w = max($max + 4, strlen($title) + 4);
        if ($w > self::$w - 4) $w = self::$w - 4;
        
        echo $color . "╔" . str_repeat("═", $w) . "╗" . R::S . "\n";        echo $color . "║" . R::B . R::BEY . " " . str_pad($title, $w - 2, " ", STR_PAD_BOTH) . " " . $color . "║" . R::S . "\n";
        echo $color . "╠" . str_repeat("═", $w) . "╣" . R::S . "\n";
        
        foreach ($lines as $line) {
            $cleanLen = strlen(self::stripAnsi($line));
            $padLen = max(0, ($w - 2) - $cleanLen);
            echo $color . "║ " . R::BEY . $line . str_repeat(" ", $padLen) . $color . " ║" . R::S . "\n";
        }
        echo $color . "╚" . str_repeat("═", $w) . "╝" . R::S . "\n";
    }

    public static function row(string $label, string $val, string $lc = R::LCAM, string $vc = R::LYES): void {
        echo "  " . $lc . str_pad($label . ":", 22) . R::S . " " . $vc . $val . R::S . "\n";
    }

    public static function sep(string $char = "─", string $color = R::GRI): void {
        echo $color . str_repeat($char, self::$w) . R::S . "\n";
    }

    public static function spinner(int $sec, string $prefix = "[!] Bekleniyor"): void {
        $frames = ['⠋','⠙','⠹','⠸','⠼','⠴','⠦','⠧','⠇','⠏'];
        $start = time();
        $f = 0;
        while (time() - $start < $sec) {
            $rem = $sec - (time() - $start);
            $h = floor($rem / 3600);
            $m = floor(($rem % 3600) / 60);
            $s = $rem % 60;
            $t = sprintf('%02d:%02d:%02d', $h, $m, $s);
            echo R::BEY . $prefix . R::LYES . " " . $t . " " . R::LCAM . $frames[$f % 10] . R::S . "\r";
            usleep(100000);
            $f++;
        }
        echo str_repeat(" ", self::$w) . "\r";
    }

    public static function log(string $type, string $msg, string $extra = ''): void {
        $z = date("H:i:s");
        $badge = "";
        $mc = R::BEY;
        
        switch ($type) {
            case 'ok':    $badge = R::BG_YES . R::S . R::SIYAH . "  OK  " . R::S; $mc = R::LYES; break;
            case 'err':   $badge = R::BG_KIR . R::S . R::BEY . " HATA " . R::S; $mc = R::LKIR; break;
            case 'warn':  $badge = R::BG_SAR . R::S . R::SIYAH . " UYARI" . R::S; $mc = R::LSAR; break;
            case 'info':  $badge = R::BG_MAV . R::S . R::BEY . " BILGI" . R::S; $mc = R::LMAV; break;
            case 'api':   $badge = R::BG_MAC . R::S . R::BEY . " API  " . R::S; $mc = R::LMAC; break;
            case 'claim': $badge = R::BG_CAM . R::S . R::SIYAH . " TALEP" . R::S; $mc = R::LCAM; break;
            default:      $badge = R::BG_GRI . R::S . R::BEY . " KAYIT" . R::S; $mc = R::BEY; break;
        }        
        echo R::GRI . "[" . $z . "] " . R::S . $badge . " " . $mc . $msg . R::S;
        if ($extra) echo " " . R::GRI . $extra . R::S;
        echo "\n";
    }

    public static function animBanner(): void {
        $colors = [R::LKIR, R::LSAR, R::LYES, R::LCAM, R::LMAV, R::LMAC];
        for ($i = 0; $i < 6; $i++) {
            echo $colors[$i] . "   NINOKI ClaimCoin Yukleniyor" . str_repeat(".", $i + 1) . R::S . "\r";
            usleep(200000);
        }
        echo str_repeat(" ", 40) . "\r";
    }
}

/* ================================================================
YAPILANDIRMA
================================================================ */
class Config {
    private string $file;
    private array $data;

    public function __construct(string $file = 'ninoki.json') {
        $this->file = $file;
        $this->data = [];
        if (file_exists($file)) {
            $c = @file_get_contents($file);
            if ($c !== false) {
                $decoded = json_decode($c, true);
                if (is_array($decoded)) $this->data = $decoded;
            }
        }
    }

    public function load(): array {
        if (empty($this->data)) {
            UI::banner();
            UI::box("ILK KURULUM", "Lutfen asagidaki bilgileri girin.", R::LSAR);
            
            echo R::BEY . "  bypassallshortlinks API Key : " . R::LSAR;
            $api = trim(fgets(STDIN) ?: '');
            echo R::BEY . "  ClaimCoin E-Posta         : " . R::LSAR;
            $em = trim(fgets(STDIN) ?: '');
            echo R::BEY . "  ClaimCoin Sifre           : " . R::LSAR;
            $pw = trim(fgets(STDIN) ?: '');

            if (empty($api) || empty($em) || empty($pw)) {
                UI::log('err', "Tüm alanlar zorunludur!");
                exit(1);            }

            $this->data = [
                'api_key' => $api, 
                'email' => $em, 
                'pass' => $pw,
                'host' => 'https://claimcoin.in', 
                'cookie' => 'ninoki_cookies.txt', 
                'v' => '3.0'
            ];
            $this->save();
            UI::log('ok', "Ayarlar kaydedildi.");
            sleep(2);
        }
        return $this->data;
    }

    public function save(): bool {
        $json = json_encode($this->data, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
        if ($json === false) return false;
        
        $res = file_put_contents($this->file, $json);
        if ($res !== false) {
            @chmod($this->file, 0600); // Güvenlik: Sadece owner okuyabilir/yazabilir.
            return true;
        }
        return false;
    }

    public function get(string $k, $d = null) {
        return $this->data[$k] ?? $d;
    }

    public function set(string $k, $v): void {
        $this->data[$k] = $v;
        $this->save();
    }

    public function reset(): void {
        if (file_exists($this->file)) @unlink($this->file);
        $cookieFile = $this->data['cookie'] ?? 'ninoki_cookies.txt';
        if (file_exists($cookieFile)) @unlink($cookieFile);
        $this->data = [];
    }
}

/* ================================================================
HTTP ISTENCILI - GUVENLI & TERMUX UYUMLU
================================================================ */
class Http {    private string $cookie;
    private array $defHeaders;
    private int $maxRetry = 3;

    public function __construct(string $cookie) {
        $this->cookie = $cookie;
        $this->defHeaders = [
            "User-Agent: Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
            "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language: id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7"
        ];
    }

    /**
     * @return string|array
     */
    public function req(string $url, string $method = 'GET', $data = [], array $headers = [], bool $retHeader = false) {
        $attempt = 0;
        
        while ($attempt < $this->maxRetry) {
            $ch = curl_init();
            $allHeaders = array_merge($this->defHeaders, $headers);
            
            $opts = [
                CURLOPT_URL => $url,
                CURLOPT_RETURNTRANSFER => true,
                CURLOPT_HEADER => $retHeader,
                CURLOPT_FOLLOWLOCATION => true,
                CURLOPT_MAXREDIRS => 5,
                CURLOPT_SSL_VERIFYHOST => 2, // Güvenlik düzeltmesi
                CURLOPT_SSL_VERIFYPEER => true, // Güvenlik düzeltmesi
                CURLOPT_HTTPHEADER => $allHeaders,
                CURLOPT_CONNECTTIMEOUT => 15,
                CURLOPT_TIMEOUT => 45,
                CURLOPT_COOKIEFILE => $this->cookie,
                CURLOPT_COOKIEJAR => $this->cookie,
                CURLOPT_ENCODING => '', // Gzip/Deflate otomatik çözümü
            ];

            if (strtoupper($method) === 'POST') {
                $opts[CURLOPT_POST] = true;
                $opts[CURLOPT_POSTFIELDS] = is_array($data) ? http_build_query($data) : $data;
            }

            curl_setopt_array($ch, $opts);
            $resp = curl_exec($ch);
            $err = curl_error($ch);
            $code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
            $headerSize = curl_getinfo($ch, CURLINFO_HEADER_SIZE);
            curl_close($ch);
            if ($resp === false || empty($resp)) {
                $attempt++;
                UI::log('warn', "cURL/Bos Yanit", $err ?: "HTTP $code (Deneme $attempt/{$this->maxRetry})");
                sleep($attempt * 2);
                continue;
            }

            if ($code >= 500) {
                $attempt++;
                UI::log('warn', "Sunucu Hatasi", "HTTP $code (Deneme $attempt/{$this->maxRetry})");
                sleep($attempt * 2);
                continue;
            }

            if ($retHeader) {
                return [
                    'body' => substr($resp, $headerSize), 
                    'header' => substr($resp, 0, $headerSize), 
                    'code' => $code
                ];
            }
            return (string) $resp;
        }
        return $retHeader ? ['body' => '', 'header' => '', 'code' => 0] : '';
    }

    public function hdr(string $type = 'def'): array {
        $base = [
            "Host: claimcoin.in",
            "User-Agent: Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
            "Accept-Language: id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7"
        ];

        if ($type === 'post') {
            return array_merge($base, [
                "Origin: https://claimcoin.in",
                "Content-Type: application/x-www-form-urlencoded",
                "Referer: https://claimcoin.in/login"
            ]);
        } 
        
        if ($type === 'ajax') {
            return array_merge($base, [
                "Origin: https://claimcoin.in",
                "Content-Type: application/x-www-form-urlencoded; charset=UTF-8",
                "X-Requested-With: XMLHttpRequest",
                "Accept: application/json, text/javascript, */*; q=0.01",
                "Referer: https://claimcoin.in/faucet"
            ]);        }

        return array_merge($base, [
            "Upgrade-Insecure-Requests: 1",
            "Referer: https://claimcoin.in/"
        ]);
    }
}

/* ================================================================
BYPASSALLSHORTLINKS API
================================================================ */
class BypassAPI {
    private string $key;
    private string $base = 'https://bypassallshortlinks.space';
    private Http $http;

    public function __construct(string $key, Http $http) {
        $this->key = $key;
        $this->http = $http;
    }

    public function balance(): array {
        $resp = $this->http->req(
            $this->base . '/api.php',
            'POST',
            json_encode(['api_key' => $this->key, 'action' => 'balance']),
            ['Content-Type: application/json']
        );
        
        $data = is_string($resp) ? json_decode($resp, true) : null;
        
        if (!empty($data['success'])) {
            return ['ok' => true, 'bal' => $data['balance'] ?? 0, 'user' => $data['user'] ?? 'bilinmiyor'];
        }
        return ['ok' => false, 'err' => $data['error'] ?? 'Bilinmeyen API hatasi'];
    }

    public function antibot(string $main, array $opts): array {
        $payload = [
            'api_key' => $this->key, 
            'action' => 'antibot',
            'main' => $main, 
            'options' => []
        ];
        
        foreach ($opts as $id => $img) {
            $payload['options'][(string)$id] = $img;
        }
                UI::log('api', "AntiBot gonderiliyor...", count($opts) . " secenek");
        $resp = $this->http->req($this->base . '/api.php', 'POST', json_encode($payload), ['Content-Type: application/json']);
        $data = is_string($resp) ? json_decode($resp, true) : null;
        
        if (!empty($data['success'])) {
            $res = $data['result'] ?? '';
            UI::log('ok', "AntiBot cozuldu", "Sira: " . $res);
            return ['ok' => true, 'order' => $res];
        }
        
        $err = $data['error'] ?? 'Bilinmeyen';
        UI::log('err', "AntiBot basarisiz", $err);
        return ['ok' => false, 'err' => $err];
    }

    public function recap(string $sitekey, string $pageurl, string $ver = 'v3', string $act = 'homepage'): array {
        $in = sprintf("%s/in.php?key=%s&method=recaptcha&sitekey=%s&pageurl=%s&action=%s&version=%s",
            $this->base, urlencode($this->key), urlencode($sitekey), urlencode($pageurl), urlencode($act), urlencode($ver));
            
        UI::log('api', "reCAPTCHA " . $ver . " gonderiliyor...", substr($sitekey, 0, 15) . "...");
        $resp = $this->http->req($in, 'GET');
        
        if (!is_string($resp) || strpos($resp, 'OK|') !== 0) {
            UI::log('err', "reCAPTCHA gonderim basarisiz", (string)$resp);
            return ['ok' => false, 'err' => (string)$resp];
        }
        
        $tid = substr($resp, 3);
        UI::log('api', "Gorev sirada", "ID: " . $tid);
        
        for ($i = 0; $i < 30; $i++) {
            UI::spinner(5, "  [API] reCAPTCHA cozuluyor");
            $res = sprintf("%s/res.php?id=%s&key=%s", $this->base, urlencode($tid), urlencode($this->key));
            $r = $this->http->req($res, 'GET');
            
            if (is_string($r) && strpos($r, 'OK|') === 0) {
                $tok = substr($r, 3);
                UI::log('ok', "reCAPTCHA cozuldu", substr($tok, 0, 20) . "...");
                return ['ok' => true, 'token' => $tok];
            }
            
            if (!is_string($r) || strpos($r, 'CAPCHA_NOT_READY') === false) {
                UI::log('err', "reCAPTCHA cozum basarisiz", (string)$r);
                return ['ok' => false, 'err' => (string)$r];
            }
        }
        return ['ok' => false, 'err' => 'Zaman asimi'];
    }
}
/* ================================================================
PARSER - GUVENLI REGEX
================================================================ */
class Parser {
    public static function csrf(string $html): string {
        if (preg_match('/name=["\']csrf_token_name["\'][^>]*value=["\']([^"\']+)["\']/s', $html, $m)) return $m[1];
        return '';
    }

    public static function balance(string $html): string {
        if (preg_match('/Available Balance.*?<h2>([^<]+)<\/h2>/s', $html, $m)) return trim($m[1]);
        return '0.00';
    }

    public static function username(string $html): string {
        if (preg_match('/class=["\']user-name["\']>([^<]+)</s', $html, $m)) return trim($m[1]);
        if (preg_match('/Welcome.*?<strong>([^<]+)<\/strong>/s', $html, $m)) return trim($m[1]);
        return 'Bilinmiyor';
    }

    public static function wait(string $html): int {
        if (preg_match('/var\s+wait\s*=\s*(\d+)/', $html, $m)) return (int)$m[1];
        return 0;
    }

    public static function antibot(string $html): array {
        $main = '';
        $opts = [];
        
        if (preg_match('/Please click on the Anti-Bot links.*?src=["\']data:image\/png;base64,([^"\']+)["\']/s', $html, $m)) {
            $main = $m[1];
        }
        
        // Regex DoS (ReDoS) önlemi için optimize edilmiş yakalama
        if (preg_match_all('/rel=["\']?(\d+)["\']?[^>]*?src=["\']?data:image\/png;base64,([^"\'>\s]+)["\']?/s', $html, $m, PREG_SET_ORDER)) {
            foreach ($m as $x) {
                $opts[$x[1]] = $x[2];
            }
        }
        
        return ['main' => $main, 'opts' => $opts];
    }

    public static function success(string $html): ?string {
        if (preg_match('/Swal\.fire\(["\']Good job!["\'],\s*["\']([^"\']+)["\']/', $html, $m)) return $m[1];
        return null;
    }

    public static function error(string $html): ?string {
        if (preg_match('/alert-danger[^>]*>.*?<\/i>\s*([^<]+)/s', $html, $m)) return trim($m[1]);        return null;
    }
}

/* ================================================================
ISTATISTIKLER
================================================================ */
class Stats {
    private int $claims = 0;
    private int $fails = 0;
    private float $start;

    public function __construct() { 
        $this->start = microtime(true); 
    }

    public function claim(): void { 
        $this->claims++; 
    }

    public function fail(): void { 
        $this->fails++; 
    }

    public function report(): array {
        $elapsed = round(microtime(true) - $this->start, 2);
        $h = floor($elapsed / 3600); 
        $m = floor(($elapsed % 3600) / 60); 
        $s = $elapsed % 60;
        
        return [
            'claims' => $this->claims, 
            'fails' => $this->fails, 
            'time' => sprintf('%02d:%02d:%02d', $h, $m, $s),
            'rate' => $elapsed > 0 ? round($this->claims / ($elapsed / 3600), 2) : 0
        ];
    }

    public function show(): void {
        $r = $this->report();
        UI::box("ISTATISTIKLER", 
            "Toplam Talep: " . $r['claims'] . "\n" .
            "Toplam Hata: " . $r['fails'] . "\n" .
            "Calisma Suresi: " . $r['time'] . "\n" .
            "Talep Hizi: " . $r['rate'] . "/saat", 
            R::LMAV);
    }
}

/* ================================================================ANA BOT
================================================================ */
class Bot {
    private Config $cfg;
    private Http $http;
    private BypassAPI $api;
    private string $host;
    private Stats $stats;
    private bool $running = true;
    private array $userInfo = [];

    public function __construct() {
        UI::init();
        $this->cfg = new Config();
        $a = $this->cfg->load();
        $this->host = $a['host'] ?? 'https://claimcoin.in';
        $this->http = new Http($a['cookie'] ?? 'ninoki_cookies.txt');
        $this->api = new BypassAPI($a['api_key'], $this->http);
        $this->stats = new Stats();
    }

    public function run(): void {
        UI::cls();
        UI::animBanner();
        UI::banner();
        
        UI::log('info', "API baglantisi kontrol ediliyor...");
        $bal = $this->api->balance();
        
        if (!$bal['ok']) {
            UI::log('err', "API baglantisi basarisiz", $bal['err']);
            UI::box("HATA", "bypassallshortlinks.space API'sine baglanilamiyor.\nLutfen API anahtarinizi kontrol edin.", R::LKIR);
            exit(1);
        }
        
        UI::box("API BAGLANDI", "Kullanici: " . $bal['user'] . "\nBakiye: " . $bal['bal'] . " token", R::LYES);
        UI::sep();
        
        while ($this->running) {
            try { 
                $this->cycle(); 
            } catch (Throwable $e) {
                UI::log('err', "Dongu hatasi: " . get_class($e), $e->getMessage());
                $this->stats->fail();
                sleep(15);
            }
        }
    }

    private function cycle(): void {        UI::log('info', "Oturum kontrol ediliyor...");
        $dash = $this->http->req($this->host . '/dashboard', 'GET', [], $this->http->hdr('def'));
        
        if (empty($dash) || (strpos($dash, 'Dashboard | ClaimCoin') === false && strpos($dash, 'Login') !== false)) {
            UI::log('warn', "Oturum gecersiz, giris yapiliyor...");
            if (!$this->login()) {
                UI::log('err', "Giris basarisiz, 30sn bekleniyor...");
                $this->stats->fail();
                sleep(30);
                return;
            }
            $dash = $this->http->req($this->host . '/dashboard', 'GET', [], $this->http->hdr('def'));
        }

        if (empty($dash)) {
            UI::log('err', "Dashboard verisi alinamadi.");
            $this->stats->fail();
            sleep(10);
            return;
        }

        $this->userInfo = [
            'username' => Parser::username($dash),
            'balance' => Parser::balance($dash)
        ];

        UI::box("HESAP BILGILERI", 
            "Kullanici: " . $this->userInfo['username'] . "\n" .
            "Mevcut Bakiye: " . $this->userInfo['balance'], 
            R::LCAM);
            
        $this->faucet();
    }

    private function login(): bool {
        UI::log('info', "Giris sayfasi aliniyor...");
        $page = $this->http->req($this->host . '/login', 'GET', [], $this->http->hdr('def'));
        
        if (empty($page)) {
            UI::log('err', "Giris sayfasi bos dondu");
            return false;
        }
        
        $csrf = Parser::csrf($page);
        if (empty($csrf)) {
            UI::log('err', "CSRF bulunamadi");
            return false;
        }
        
        UI::log('api', "Giris deneniyor...", $this->cfg->get('email'));        $data = [
            'csrf_token_name' => $csrf, 
            'email' => $this->cfg->get('email'), 
            'password' => $this->cfg->get('pass')
        ];
        
        $resp = $this->http->req($this->host . '/auth/login', 'POST', $data, $this->http->hdr('post'));
        
        if (is_string($resp) && strpos($resp, 'Dashboard | ClaimCoin') !== false) {
            UI::log('ok', "Giris basarili!");
            return true;
        }
        
        $err = is_string($resp) ? Parser::error($resp) : null;
        if ($err) {
            UI::log('err', "Giris basarisiz", $err);
            if (stripos($err, 'Invalid') !== false || stripos($err, 'Wrong') !== false) {
                UI::log('warn', "Hatali bilgi, ayarlar sifirlaniyor...");
                $this->cfg->reset();
                UI::box("YENIDEN BASLAT", "Ayarlar temizlendi. Yeniden baslatin.", R::LSAR);
                exit(0);
            }
        } else { 
            UI::log('err', "Bilinmeyen giris yaniti"); 
        }
        return false;
    }

    private function faucet(): void {
        $maxRetries = 5;
        $retryCount = 0;

        while ($retryCount < $maxRetries) {
            UI::log('info', "Musluk sayfasina gidiliyor...");
            $page = $this->http->req($this->host . '/faucet', 'GET', [], $this->http->hdr('def'));
            
            if (empty($page)) {
                UI::log('err', "Musluk sayfasi bos, tekrar deneniyor...");
                $retryCount++;
                sleep(5);
                continue;
            }

            $wait = Parser::wait($page);
            if ($wait > 0) {
                UI::log('warn', "Bekleme suresi", $wait . "sn");
                UI::spinner($wait, "  [BEKLEME] Musluk hazirlaniyor");
                $retryCount++;
                continue;
            }
            $csrf = Parser::csrf($page);
            if (empty($csrf)) { 
                UI::log('err', "CSRF eksik"); 
                $retryCount++;
                sleep(10); 
                continue; 
            }

            $ab = Parser::antibot($page);
            if (empty($ab['main']) || count($ab['opts']) < 3) {
                UI::log('err', "AntiBot gorselleri bulunamadi, tekrar...");
                $retryCount++;
                sleep(5); 
                continue;
            }

            UI::log('info', "AntiBot algilandi", count($ab['opts']) . " secenek");
            $res = $this->api->antibot($ab['main'], $ab['opts']);
            
            if (!$res['ok']) {
                UI::log('err', "AntiBot cozulemedi, atlaniyor...");
                $this->stats->fail();
                sleep(30); 
                return;
            }

            $order = str_replace(',', ' ', $res['order']);
            UI::log('ok', "AntiBot siralama", $order);

            $recap = $this->api->recap('6LdnVw4qAAAAAFPMxvegAK9JcBflI-0tb8YKMxZU', $this->host . '/faucet', 'v3', 'homepage');
            if (!$recap['ok']) {
                UI::log('err', "reCAPTCHA basarisiz, atlaniyor...");
                $this->stats->fail();
                sleep(30); 
                return;
            }

            UI::log('claim', "Talep gonderiliyor...");
            $data = [
                'captcha' => 'recaptchav3', 
                'recaptchav3' => $recap['token'],
                'antibotlinks' => $order, 
                'csrf_token_name' => $csrf
            ];
            
            $resp = $this->http->req($this->host . '/faucet/verify', 'POST', $data, $this->http->hdr('post'));
            
            if (!is_string($resp)) {
                UI::log('err', "Sunucudan geçersiz yanıt alındı.");                $retryCount++;
                sleep(10);
                continue;
            }

            $succ = Parser::success($resp);
            $err = Parser::error($resp);
            
            if ($succ) {
                $this->stats->claim();
                UI::log('ok', "TALEP BASARILI!", $succ);
                $r = $this->stats->report();
                UI::row("Toplam Talep", (string)$r['claims']);
                UI::row("Calisma Suresi", $r['time']);
                UI::row("Talep Hizi", $r['rate'] . "/saat");
                
                $nw = Parser::wait($resp);
                if ($nw > 0) {
                    UI::log('info', "Sonraki talep bekleme sonrasi");
                    UI::spinner($nw, "  [BEKLEME] Sonraki talep");
                }
                
                UI::sep();
                $this->stats->show();
                UI::sep();
                return; // Başarılı, döngüden çık.
            } 
            
            if ($err) {
                UI::log('err', "Talep basarisiz", $err);
                $this->stats->fail();
            } else {
                UI::log('warn', "Belirsiz yanit, tekrar...");
            }
            
            $retryCount++;
            sleep(10);
        }
        
        UI::log('err', "Maksimum deneme sayısına ulaşıldı. Döngü sonlandırılıyor.");
        $this->stats->fail();
    }
}

/* ================================================================
GIRIS
================================================================ */
if (php_sapi_name() !== 'cli') {
    die("Bu script sadece CLI (Terminal) ortaminda calistirilmalidir.\n");
}
if (function_exists('pcntl_signal')) {
    pcntl_signal(SIGINT, function() { 
        UI::log('warn', "\nKapatiliyor..."); 
        exit(0); 
    });
}

try {
    $bot = new Bot();
    $bot->run();
} catch (Throwable $e) {
    UI::log('err', "Kritik hata: " . get_class($e), $e->getMessage());
    UI::box("COKME RAPORU", $e->getMessage() . "\nSatir: " . $e->getLine() . "\nDosya: " . $e->getFile(), R::LKIR);
    exit(1);
}
