# Reverse Engineering Report for `sm2.py`

## Executive Summary

`sm2.py` is a heavily obfuscated Python loader that ultimately runs a Python 3.13 bytecode payload. The recovered payload is an automation script for `slotfruits.com` that logs in with a FaucetPay email, repeatedly calls a spin/reward endpoint while credits remain, and then triggers Google ad reward URLs after replacing their `rwd_userid` query parameter.

The deobfuscated payload is available in `sm2_deobfuscated.py`.

## Obfuscation and Encoding Layers

| Layer | Technique | Purpose | Recovery status |
|---|---|---|---|
| 1 | Base32 encoded giant bytes literal | Hides the stage-1 Python script | Fully recovered |
| 2 | Dynamic imports via string concatenation and `getattr` | Hides `base64`, `exec`, and `compile` usage | Fully recovered |
| 3 | `compile(...); exec(...)` | Executes decoded stage-1 at runtime | Removed in recovered source |
| 4 | Junk/dead functions | Adds noise (`I5pbivBrqz`, checksums, random transforms) | Identified as unused |
| 5 | XOR-obfuscated strings | Hides module/function names in stage-1 (`zlib`, `base64`, `hashlib`, `b32decode`, `decompress`) | Fully recovered |
| 6 | Chunk splitting, XOR per chunk, randomized order table | Hides a second encoded blob | Fully recovered |
| 7 | Reverse string + Base64 decode | Reassembles an intermediate Base58 string | Fully recovered |
| 8 | Base58 decode to ASCII hex | Produces a hex string | Fully recovered |
| 9 | Hex decode | Produces Base32 bytes | Fully recovered |
| 10 | Base32 decode | Produces XOR-encrypted compressed bytes | Fully recovered |
| 11 | Repeating-key XOR | Decrypts zlib-compressed marshal data; key is `[35, 203, 11, 26, 162, 162, 100, 117, 203, 183, 226, 53, 236, 34, 178, 101]` | Fully recovered |
| 12 | SHA-256 integrity check | Prevents tampering; expected digest `0a5a72021f3616f86010b92560161301f7587fa0f8577b1fcc39629ef94813d7` | Fully recovered |
| 13 | zlib decompression | Produces a marshaled Python code object | Fully recovered |
| 14 | `marshal.loads` + `exec` | Runs the final Python 3.13 bytecode payload | Removed in recovered source |

No evidence of AES, Fernet, RSA, gzip, lzma, bz2, ROT, ctypes, native embedded binaries, anti-VM, anti-debugging, anti-hooking, persistence, or filesystem-destroying behavior was found.

## Program Architecture

The recovered application is procedural and has three major runtime phases:

1. **Console UI**: clears the terminal, prints a banner, prints account status, and shows short animations.
2. **SlotFruits automation**: logs into `slotfruits.com`, retrieves token/user/balance/credits, and calls the spin endpoint until credits are exhausted.
3. **Ad reward farming**: requests a Google mobile ads endpoint, extracts JSON ad reward URLs, injects the logged-in user ID into each reward URL, and calls each URL.

## Execution Flow

1. `main()` prints the banner.
2. The user is prompted for a Faucet email.
3. An infinite `while True` loop starts.
4. `login(email)` posts the email to `https://slotfruits.com/api/v1/users/signupFaucetPayLogin`.
5. The returned token, user ID, balance, and credits are displayed.
6. `run_spin_loop(...)` repeatedly calls `https://slotfruits.com/api/v1/users/earnRoll` with a bearer token while `credits > 0`.
7. When spins finish, `run_ads_loop(user_id)` calls the Google ad endpoint and then each extracted video reward URL with `rwd_userid` set to the SlotFruits user ID.
8. The cycle restarts forever.

## Entry Point

The original final payload was top-level bytecode. In the cleaned source, that behavior is represented by `main()` and the standard `if __name__ == "__main__": main()` guard.

## Functions

| Function | Purpose | Risk |
|---|---|---|
| `clear_screen()` | Executes `clear` through `os.system` | Low; invokes a shell command |
| `terminal_width()` | Reads terminal width | Low |
| `make_line()` | Creates repeated separator line | Low |
| `center_text()` | Centers text | Low |
| `print_banner()` | Clears screen and prints branding/Telegram link | Low |
| `animate_status()` | Prints two status frames and sleeps | Low |
| `print_account_info()` | Prints email, balance, credits | Medium; exposes user email on screen/logs |
| `login()` | Sends email to SlotFruits login API and parses token/user data | Medium/high; transmits identifier and handles bearer token |
| `run_spin_loop()` | Calls authenticated SlotFruits spin endpoint until credits are zero | Medium; automated service interaction |
| `run_ads_loop()` | Calls Google ad endpoint, rewrites reward URLs, and triggers them | High; suspicious ad/reward farming behavior |
| `main()` | Orchestrates infinite login/spin/ad loop | Medium/high; endless network automation |

## Variables and Constants

Important variables include:

- `RESET`, `RED`, `GREEN`, `YELLOW`, `BLUE`, `MAGENTA`, `CYAN`: terminal ANSI color codes.
- `LOGIN_URL`: SlotFruits FaucetPay login endpoint.
- `SPIN_URL`: SlotFruits earn/spin endpoint.
- `ADS_URL`: long Google mobile ads request URL containing mobile/device/ad parameters.
- `email`: user-supplied Faucet email.
- `token`: bearer token returned by SlotFruits.
- `user_id`: SlotFruits user ID, later injected into ad reward URLs.
- `balance`: account balance returned by the API.
- `credits`: spin credits returned by the API.
- `headers`: HTTP request headers used to mimic Android/OkHttp/WebView traffic.
- `query_parameters`: parsed reward URL parameters, modified to include `rwd_userid`.

## Imported Modules

- `json`: serializes login request body.
- `os`: runs `clear` via `os.system`.
- `shutil`: reads terminal dimensions.
- `time`: sleeps between actions.
- `datetime.datetime`: called in the banner routine, but the value is unused.
- `urllib.parse`: parses and rewrites ad reward URLs.
- `requests`: performs all HTTP requests.

## Network Requests

| Method | URL/domain | Description |
|---|---|---|
| `POST` | `https://slotfruits.com/api/v1/users/signupFaucetPayLogin` | Sends `{"email": email}` and receives token/user state |
| `GET` | `https://slotfruits.com/api/v1/users/earnRoll` | Authenticated with `authorization: Bearer <token>`; consumes spin credits and receives rewards |
| `GET` | `https://googleads.g.doubleclick.net/mads/gma?...` | Fetches ad metadata/reward URLs while spoofing Android WebView/mobile app headers |
| `GET` | dynamic `video_reward_urls` | Hits each reward URL after setting `rwd_userid=<SlotFruits user_id>` |

## Filesystem Operations

No file reads/writes/deletes were recovered in the final payload. The only OS operation is `os.system("clear")`, which launches the terminal clear command.

## Subprocesses

- `os.system("clear")` invokes a shell command to clear the terminal.

## Persistence Mechanisms

No persistence mechanisms were found. There are no crontab edits, startup file edits, service installs, registry changes, shell profile changes, or scheduled tasks.

## Security Mechanisms in the Loader

- SHA-256 verification of the decompressed marshal bytes prevents simple payload tampering.
- Runtime `exec`, `compile`, and `marshal.loads` prevent static inspection by casual readers.
- Several unused junk functions and randomized-looking identifiers frustrate manual analysis.

## Hidden Payloads and Embedded Artifacts

- Hidden payload: Python 3.13 marshaled bytecode for the SlotFruits/ad automation script.
- Embedded ad artifact: a very long Google ads URL and static Android WebView headers/cookie.
- Embedded token/cookie-like value: Google `IDE=...` cookie in ad request headers.
- No native binaries were recovered.

## Suspicious Behavior

- Heavy obfuscation for an otherwise simple automation script.
- Dynamic bytecode execution via `marshal.loads` and `exec`.
- Infinite automation loop against a rewards/faucet service.
- Ad reward URL manipulation by replacing `rwd_userid`.
- Mobile app/device header spoofing.
- Embedded Google advertising cookie and app/ad publisher identifiers.

## IOCs

### Domains

- `slotfruits.com`
- `googleads.g.doubleclick.net`
- `t.me`

### URLs

- `https://slotfruits.com/api/v1/users/signupFaucetPayLogin`
- `https://slotfruits.com/api/v1/users/earnRoll`
- `https://googleads.g.doubleclick.net/mads/gma?...`
- `https://googleads.g.doubleclick.net/mads/static/sdk/native/sdk-core-v40.html`
- `https://t.me/SyndicateBotNet`

### Hashes

- Final marshal bytes SHA-256: `0a5a72021f3616f86010b92560161301f7587fa0f8577b1fcc39629ef94813d7`

### Tokens / Cookies / Identifiers

- Google ad cookie: `IDE=AHWqTUmPTIJAy-Z7wZUR-Si3c3uYRcuBwUfjmr_ffdlWQMrcruxMTVUyL8XPtA-y_Dk`
- Package/app IDs: `com.piratebaixe.slotMobile`, `17.android.com.spincoin.appmobile.top`
- Google ad client/app code values: `ca-app-pub-5674874137587223`, `5186053460`, slot `7114498212`

### IP Addresses

No IP addresses were embedded. The string `0.0.0.0.0.0.0.0` appears as a `guci` query value, not as a usable IP IOC.

## MITRE ATT&CK Mapping

| Technique | Applicability | Evidence |
|---|---|---|
| T1027 - Obfuscated Files or Information | Strong | Multiple encoding/compression/encryption layers and marshal bytecode |
| T1140 - Deobfuscate/Decode Files or Information | Strong | Runtime Base32/Base64/Base58/Hex/XOR/zlib/marshal decoding |
| T1059.006 - Command and Scripting Interpreter: Python | Strong | Python script executes payload dynamically |
| T1059 - Command and Scripting Interpreter | Limited | `os.system("clear")` invokes shell for terminal clearing |
| T1105 - Ingress Tool Transfer / network communication | Weak/partial | Network communication exists, but no file transfer was recovered |
| T1071.001 - Web Protocols | Moderate | HTTP(S) API/ad traffic via `requests` |

## Risk Assessment

Overall risk: **Medium to High**.

The recovered code is not a traditional credential stealer or destructive malware based on the recovered payload, but it is intentionally concealed, dynamically executes bytecode, handles user identifiers and bearer tokens, and performs suspicious ad/reward automation. Running it may violate third-party service terms, expose user account details, and trigger automated network abuse indicators.

## Optimization and Hardening Suggestions

If this were legitimate automation, it should be rewritten to:

- Remove all obfuscation and dynamic execution.
- Add explicit error handling for HTTP failures and malformed JSON.
- Add request timeouts.
- Avoid infinite loops without user confirmation.
- Avoid embedding cookies, ad identifiers, or static device spoofing headers.
- Avoid printing personal email/account details unless explicitly requested.
- Replace `os.system("clear")` with a safer terminal-control abstraction or make it optional.

## Confidence

| Component | Confidence |
|---|---:|
| Loader decoding chain | High |
| Final payload source reconstruction | High |
| Network endpoint identification | High |
| No persistence found | High |
| No embedded native binaries found | High |
| Absence of anti-VM/anti-debugging beyond obfuscation | Medium-high |
| MITRE mapping | Medium |
