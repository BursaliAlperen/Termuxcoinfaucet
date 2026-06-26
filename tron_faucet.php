<?php
error_reporting(0);
date_default_timezone_set('Europe/Istanbul');

const siyah   = "\033[0;30m";
const kirmizi = "\033[0;31m";
const yesil   = "\033[1;32m";
const sari    = "\033[1;33m";
const mavi    = "\033[0;34m";
const cyan    = "\033[1;36m";
const beyaz   = "\033[0;37m";
const reset   = "\033[0m";

$configFile = "config.json";
$cookieJsonFile = "cookies.json";

$faucets = [
    'TRON' => 'https://tronblow.site'
];

$referansEmail = "ankaralironaldo131@gmail.com";

function clear() {
    (PHP_OS == "Linux") ? system('clear') : pclose(popen('cls', 'w'));
}

function maskeleEmail($email) {
    $parts = explode("@", $email);
    if(count($parts) == 2) {
        $name = $parts[0];
        $masked_name = substr($name, 0, 2) . str_repeat("*", max(1, strlen($name)-2));
        return $masked_name . "@" . $parts[1];
    }
    return $email;
}

function okuTimerWeb($html, $varsayilan = 62) {
    $total = 0;
    if (preg_match_all('/<div class="cd-num"[^>]*>\s*(\d+)\s*<\/div>\s*<div class="cd-lbl"[^>]*>([^<]+)<\/div>/is', $html, $matches, PREG_SET_ORDER)) {
        foreach ($matches as $match) {
            $sayi = (int)$match[1];
            $etiket = strtoupper(trim($match[2]));
            if (strpos($etiket, 'MIN') !== false) $total += $sayi * 60;
            elseif (strpos($etiket, 'SEC') !== false) $total += $sayi;
        }
        if ($total > 0) return $total + 2;
    }
    
    $odak = $html;
    if (preg_match('/<div class="alert[^>]*>(.*?)<\/div>/is', $html, $alert)) {
        $odak = strip_tags($alert[1]);
    } elseif (strlen($html) > 500) {
        return $varsayilan; 
    }
    
    if (preg_match('/(\d+)\s*(minute|min|dakika)/i', $odak, $m_min)) $total += (int)$m_min[1] * 60;
    if (preg_match('/(\d+)\s*(second|sec|saniye)/i', $odak, $m_sec)) $total += (int)$m_sec[1];
    
    return $total > 0 ? $total + 2 : $varsayilan;
}

function curlIstek($url, $method = 'GET', $data = [], $headers = [], $cookie_file = 'cookies.txt') {
    $ch = curl_init();
    $options = [
        CURLOPT_URL            => $url, CURLOPT_RETURNTRANSFER => true, CURLOPT_HEADER => false,
        CURLOPT_FOLLOWLOCATION => true, CURLOPT_SSL_VERIFYHOST => 0, CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_HTTPHEADER     => $headers, CURLOPT_CONNECTTIMEOUT => 30, CURLOPT_TIMEOUT => 30,
        CURLOPT_COOKIEFILE     => $cookie_file, CURLOPT_COOKIEJAR => $cookie_file
    ];
    if (strtoupper($method) === 'POST') {
        $options[CURLOPT_POST] = true;
        $options[CURLOPT_POSTFIELDS] = is_array($data) ? http_build_query($data) : $data;
    }
    curl_setopt_array($ch, $options);
    $response = curl_exec($ch);
    curl_close($ch);
    return $response;
}

function getHeaders($host_url) {
    $host = parse_url($host_url, PHP_URL_HOST);
    return [
        "Host: $host",
        "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Origin: $host_url",
        "Referer: $host_url/",
        "Content-Type: application/x-www-form-urlencoded"
    ];
}

function baslikCiz() {
    echo sari."╔══════════════════════════════════════════════════════╗\n";
    echo sari."║          TRON OTOMATİK FAUCET - ANINDA ÖDEME         ║\n";
    echo sari."║              Otomatik Captcha Çözümü                 ║\n";
    echo sari."║              https://tronblow.site/                  ║\n";
    echo sari."╚══════════════════════════════════════════════════════╝\n".reset;
}

function tabloGoster($state, $alt_bilgi = "") {
    clear();
    baslikCiz();
    
    echo beyaz . "║ E-POSTA       │ WEB  │ DURUM   │ ÖDÜL       │ SÜRE   ║\n";
    echo beyaz . "╠═══════════════╪══════╪═════════╪════════════╪════════╣\n";
    
    $son_email = "";
    $basari_var = false;

    foreach ($state as $email => $webs) {
        if ($son_email !== "" && $son_email !== $email) {
            echo beyaz . "╠═══════════════╪══════╪═════════╪════════════╪════════╣\n";
        }
        $son_email = $email;
        
        $maske = maskeleEmail($email);
        if (strlen($maske) > 13) {
            $maske = substr($maske, 0, 13);
        }
        
        foreach ($webs as $web => $data) {
            $kalan = max(0, $data['timer'] - time());
            $kalan_str = $kalan > 0 ? $kalan . "sn" : "0sn";
            
            $c_email   = str_pad($maske, 13);
            $c_web     = str_pad(substr($web, 0, 4), 4);
            $c_odul    = str_pad(substr($data['reward'], 0, 10), 10);
            $c_sure    = str_pad(substr($kalan_str, 0, 6), 6);
            
            $durum_ham = $data['status'];
            if ($durum_ham === 'Başarılı!') {
                $durum_goster = yesil . "Başarılı!" . beyaz;
                $basari_var = true;
            } else {
                $durum_goster = str_pad(substr($durum_ham, 0, 7), 7);
            }
            
            $odul_goster = yesil . $c_odul . beyaz;
            $sure_goster = cyan . $c_sure . beyaz;
            
            echo beyaz . "║ " . $c_email . " │ " . $c_web . " │ " . $durum_goster . " │ " . $odul_goster . " │ " . $sure_goster . " ║\n";
        }
    }
    echo sari."╚══════════════════════════════════════════════════════╝\n".reset;
    
    if ($alt_bilgi != "") {
        if (strlen($alt_bilgi) > 52) {
            $alt_bilgi = substr($alt_bilgi, 0, 50) . "..";
        }
        echo cyan."► $alt_bilgi\n".reset;
    }

    if ($basari_var) {
        echo yesil."► Ödül başarıyla FaucetPay hesabınıza gönderildi!\n".reset;
    }
}

clear();
baslikCiz();
echo "\n";

$emails = [];
if (file_exists($configFile)) {
    $config = json_decode(file_get_contents($configFile), true);
    $emails = isset($config['emails']) ? $config['emails'] : [];
    if (empty($emails)) {
        $emails[] = $referansEmail;
        file_put_contents($configFile, json_encode(["emails" => $emails], JSON_PRETTY_PRINT));
        echo yesil . "[+] Referans e-posta kullanılıyor: " . maskeleEmail($referansEmail) . "\n";
    } else {
        echo cyan . "[i] " . count($emails) . " hesap yüklendi.\n";
    }
} else {
    echo cyan . "[+] Yapılandırma dosyası oluşturuluyor...\n";
    $emails[] = $referansEmail;
    file_put_contents($configFile, json_encode(["emails" => $emails], JSON_PRETTY_PRINT));
    echo yesil . "[+] Referans e-posta kaydedildi: " . maskeleEmail($referansEmail) . "\n";
}

sleep(1);

$state = [];
foreach ($emails as $email) {
    foreach ($faucets as $web_name => $url) {
        $state[$email][$web_name] = [
            'status' => 'Bekle',
            'reward' => '0 Sats',
            'total'  => 0,
            'timer'  => 0,
            'host'   => $url
        ];
    }
}

while (true) {
    $all_cookies = file_exists($cookieJsonFile) ? json_decode(file_get_contents($cookieJsonFile), true) : [];

    foreach ($emails as $email) {
        foreach ($faucets as $web_name => $host_url) {
            
            if (time() >= $state[$email][$web_name]['timer']) {
                $state[$email][$web_name]['status'] = 'İstek..';
                tabloGoster($state, "İşleniyor: " . maskeleEmail($email));
                
                $cookie_key = $email . "_" . $web_name;
                $temp_cookie = "cookie_temp.txt";
                if (!empty($all_cookies[$cookie_key])) {
                    file_put_contents($temp_cookie, $all_cookies[$cookie_key]);
                } else {
                    if (file_exists($temp_cookie)) unlink($temp_cookie); 
                }

                $headers = getHeaders($host_url);
                $html = curlIstek($host_url."/", "GET", [], $headers, $temp_cookie);
                
                $bekleme = okuTimerWeb($html, 0);
                
                if ($bekleme > 0) {
                    $state[$email][$web_name]['status'] = 'Bekle';
                    $state[$email][$web_name]['reward'] = '0 Sats';
                    $state[$email][$web_name]['timer'] = time() + $bekleme;
                } elseif (
                    preg_match('/name="math_q1"\s*value="([^"]+)"/i', $html, $m1) &&
                    preg_match('/name="math_q2"\s*value="([^"]+)"/i', $html, $m2) &&
                    preg_match('/name="math_op"\s*value="([^"]+)"/i', $html, $mop)
                ) {
                    $q1 = (int)$m1[1]; $q2 = (int)$m2[1]; $op = trim($mop[1]);
                    $ans = ($op == '+') ? $q1 + $q2 : (($op == '-') ? $q1 - $q2 : $q1 * $q2);
                    
                    $payload = [
                        "action" => "claim", "math_q1" => $q1, "math_q2" => $q2,
                        "math_op" => $op, "email" => $email, "math_answer" => $ans
                    ];
                    
                    $submit = curlIstek($host_url."/", "POST", $payload, $headers, $temp_cookie);
                    
                    if (preg_match('/<div class="alert alert-success[^>]*>(.*?)<\/div>/is', $submit, $msg)) {
                        $mesaj = trim(strip_tags($msg[1]));
                        
                        $kazanilan = 0;
                        if (preg_match('/(\d+)\s*satoshi?/i', $mesaj, $rew)) {
                            $kazanilan = (int)$rew[1];
                        }
                        
                        $state[$email][$web_name]['status'] = 'Başarılı!';
                        $state[$email][$web_name]['reward'] = $kazanilan . ' Sats';
                        $state[$email][$web_name]['total'] += $kazanilan;
                        $state[$email][$web_name]['timer'] = time() + okuTimerWeb($submit, 62); 
                        
                    } elseif (preg_match('/<div class="alert alert-error[^>]*>(.*?)<\/div>/is', $submit, $msg)) {
                        $mesaj = trim(strip_tags($msg[1]));
                        
                        if (stripos($mesaj, 'limit') !== false || stripos($mesaj, 'denied') !== false) {
                            $state[$email][$web_name]['status'] = 'Limit';
                            $state[$email][$web_name]['reward'] = '0 Sats';
                            $state[$email][$web_name]['timer'] = time() + 300; 
                        } else {
                            $state[$email][$web_name]['status'] = 'Hata';
                            $state[$email][$web_name]['reward'] = '0 Sats';
                            $state[$email][$web_name]['timer'] = time() + okuTimerWeb($submit, 62);
                        }
                    } else {
                        $state[$email][$web_name]['status'] = 'Hata';
                        $state[$email][$web_name]['timer'] = time() + okuTimerWeb($submit, 62);
                    }
                } else {
                    $state[$email][$web_name]['status'] = 'Bekle';
                    $state[$email][$web_name]['timer'] = time() + okuTimerWeb($html, 30);
                }
                
                if (file_exists($temp_cookie)) {
                    $all_cookies[$cookie_key] = file_get_contents($temp_cookie);
                    file_put_contents($cookieJsonFile, json_encode($all_cookies, JSON_PRETTY_PRINT));
                    unlink($temp_cookie);
                }
            }
        }
    }

    $en_kucuk = PHP_INT_MAX;
    foreach ($state as $email => $webs) {
        foreach ($webs as $web => $data) {
            if ($data['timer'] < $en_kucuk) {
                $en_kucuk = $data['timer'];
            }
        }
    }
    
    $kalan = max(0, $en_kucuk - time());
    tabloGoster($state, "Bekleme: $kalan saniye...");
    sleep(1);
}
