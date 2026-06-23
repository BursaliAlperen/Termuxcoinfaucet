#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════╗
║                    🎰  S L O T  F R U I T  🎰                    ║
║                         NINOKI EDITION                          ║
║              Deobfuscated & Enhanced Version                   ║
╚══════════════════════════════════════════════════════════════════╝

Original: sm2.py (SYNDICATEBOT NET ENCRYPTION LEVEL 3)
Decryption Layers:
  Layer 1: Base32 outer encoding
  Layer 2: XOR stream cipher (16-byte key)
  Layer 3: Base32 chunk decode
  Layer 4: XOR stream cipher (same key)
  Layer 5: Base64 decode
  Layer 6: Hex decode
  Layer 7: Base32 decode
  Layer 8: XOR stream cipher
  Layer 9: Zlib decompress
  Layer 10: SHA256 hash verification
  Layer 11: Marshal.loads -> Python bytecode
  Layer 12: exec() execution

Fixed Issues:
  ✓ Spin infinite loop bug (is_spinning flag never cleared)
  ✓ Thread safety (added threading.Lock)
  ✓ Proper exception handling (try/finally)
  ✓ Clean exit handling
"""

import os
import sys
import time
import random
import threading
from datetime import datetime

# ═════════════════════════════════════════════════════════════════
# KONFIGURASYON
# ═════════════════════════════════════════════════════════════════
CONFIG = {
    "ADS_HIT_TARGET": 200,
    "SPIN_COST": 1,
    "STARTING_SPINS": 10,
    "REEL_SYMBOLS": ["🍒", "🍋", "🍊", "🍇", "🍉", "💎", "7️⃣", "🎰"],
    "PAYOUT_TABLE": {
        "🍒🍒🍒": 5,
        "🍋🍋🍋": 10,
        "🍊🍊🍊": 15,
        "🍇🍇🍇": 20,
        "🍉🍉🍉": 25,
        "💎💎💎": 50,
        "7️⃣7️⃣7️⃣": 100
    },
    "JACKPOT_MULTIPLIER": 10,
    "ANIMATION_FRAMES": 8,
    "ANIMATION_DELAY": 0.08
}

# ═════════════════════════════════════════════════════════════════
# ASCII BANNER - NINOKI
# ═════════════════════════════════════════════════════════════════
def print_banner():
    os.system('clear' if os.name != 'nt' else 'cls')
    banner = r"""
    ████████████████████████████████████████████████████████████████
    ██                                                            ██
    ██     ███████╗██╗      ██████╗ ████████╗███████╗██████╗      ██
    ██     ██╔════╝██║     ██╔═══██╗╚══██╔══╝██╔════╝██╔══██╗     ██
    ██     ███████╗██║     ██║   ██║   ██║   █████╗  ██████╔╝     ██
    ██     ╚════██║██║     ██║   ██║   ██║   ██╔══╝  ██╔══██╗     ██
    ██     ███████║███████╗╚██████╔╝   ██║   ███████╗██║  ██║     ██
    ██     ╚══════╝╚══════╝ ╚═════╝    ╚═╝   ╚══════╝╚═╝  ╚═╝     ██
    ██                                                            ██
    ██              🍒 🍋 🍊 🍇 🍉 💎 7️⃣ 🎰                    ██
    ██                     N I N O K I                            ██
    ██                                                            ██
    ████████████████████████████████████████████████████████████████
    """
    print("\033[1;33m" + banner + "\033[0m")
    print("\033[1;32m" + "  💰 KAZANÇ: Her 200 Reklam = 50 Bedava Spin! 💰".center(66) + "\033[0m")
    print("\033[1;36m" + "  🔓 Deobfuscated from sm2.py | Thread-Safe | No Infinite Loops".center(66) + "\033[0m")
    print("\n")

# ═════════════════════════════════════════════════════════════════
# LOADING EKRANI
# ═════════════════════════════════════════════════════════════════
def loading_screen(text="Yükleniyor", duration=2.0):
    chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    end_time = time.time() + duration
    i = 0
    while time.time() < end_time:
        print(f"\r\033[1;36m[{chars[i % len(chars)]}] {text}...\033[0m", end="", flush=True)
        time.sleep(0.1)
        i += 1
    print("\r" + " " * 50 + "\r", end="")

# ═════════════════════════════════════════════════════════════════
# SLOT MAKINESI SINIFI (THREAD-SAFE)
# ═════════════════════════════════════════════════════════════════
class SlotFruit:
    """
    Thread-safe slot machine implementation.
    
    FIXED BUG: Original sm2.py had infinite loop issue where
    is_spinning flag was set to True but never cleared if spin
    animation completed or exception occurred.
    
    SOLUTION: Added try/finally block to ALWAYS clear is_spinning.
    """
    
    def __init__(self):
        self.spins = CONFIG["STARTING_SPINS"]
        self.ads_watched = 0
        self.total_earned = 0
        self.lock = threading.Lock()
        self.is_spinning = False
        self.reel = CONFIG["REEL_SYMBOLS"]
        self.spin_history = []
        
    def get_status(self):
        """Thread-safe status reading."""
        with self.lock:
            return {
                "spins": self.spins,
                "ads": self.ads_watched,
                "earned": self.total_earned,
                "next_reward": CONFIG["ADS_HIT_TARGET"] - (self.ads_watched % CONFIG["ADS_HIT_TARGET"]),
                "is_spinning": self.is_spinning,
                "history_count": len(self.spin_history)
            }
    
    def watch_ad(self):
        """
        Ads Hit 200 Logic:
        Every 200 ads watched = 50 bonus spins reward.
        This is the core monetization loop from original sm2.py.
        """
        with self.lock:
            self.ads_watched += 1
            remaining = self.ads_watched % CONFIG["ADS_HIT_TARGET"]
            
            if remaining == 0:
                bonus = 50
                self.spins += bonus
                return {
                    "hit": True,
                    "bonus": bonus,
                    "total_ads": self.ads_watched,
                    "message": f"🎉 TEBRIKLER! {CONFIG['ADS_HIT_TARGET']}. reklam! +{bonus} SPIN!"
                }
            return {
                "hit": False,
                "progress": remaining,
                "target": CONFIG["ADS_HIT_TARGET"],
                "total_ads": self.ads_watched,
                "message": f"📺 Reklam izlendi! ({remaining}/{CONFIG['ADS_HIT_TARGET']})"
            }
    
    def spin(self):
        """
        SAFE SPIN MECHANISM
        
        Original sm2.py bug: spin would finish but is_spinning remained True,
        causing "10 spins remaining" display in Termux while being stuck.
        
        Fix: try/finally guarantees is_spinning is ALWAYS cleared.
        """
        with self.lock:
            if self.is_spinning:
                return {"error": "⏳ Zaten dönüyor! Lütfen bekleyin..."}
            if self.spins <= 0:
                return {"error": "❌ Spin hakkı kalmadı! Reklam izleyin."}
            
            self.is_spinning = True
            self.spins -= 1
        
        try:
            result = self._animate_spin()
            self.spin_history.append(result)
            return result
        finally:
            with self.lock:
                self.is_spinning = False
    
    def _animate_spin(self):
        """Spin animation and result calculation."""
        columns = [
            [random.choice(self.reel) for _ in range(3)],
            [random.choice(self.reel) for _ in range(3)],
            [random.choice(self.reel) for _ in range(3)]
        ]
        
        for frame in range(CONFIG["ANIMATION_FRAMES"]):
            temp = [random.choice(self.reel) for _ in range(3)]
            print(f"\r\033[1;35m[ {' | '.join(temp)} ]\033[0m", end="", flush=True)
            time.sleep(CONFIG["ANIMATION_DELAY"])
        
        final = [col[1] for col in columns]
        print(f"\r\033[1;32m[ {' | '.join(final)} ]\033[0m\n")
        
        combo = "".join(final)
        payout = CONFIG["PAYOUT_TABLE"].get(combo, 0)
        
        is_jackpot = final[0] == final[1] == final[2] and payout > 0
        
        if is_jackpot:
            payout *= CONFIG["JACKPOT_MULTIPLIER"]
            message = f"🎰 JACKPOT! {combo} = +{payout} SPIN!"
        elif payout > 0:
            message = f"✅ Kazanç! {combo} = +{payout} SPIN!"
        else:
            message = f"❌ Kaybettin... {combo}"
        
        with self.lock:
            self.spins += payout
            self.total_earned += payout
        
        return {
            "result": final,
            "combo": combo,
            "payout": payout,
            "is_jackpot": is_jackpot,
            "spins_left": self.get_status()["spins"],
            "message": message
        }
    
    def get_history(self, limit=10):
        """Get recent spin history."""
        with self.lock:
            return self.spin_history[-limit:]

# ═════════════════════════════════════════════════════════════════
# ANA OYUN DONGUSU
# ═════════════════════════════════════════════════════════════════
def main():
    print_banner()
    loading_screen("Sistem başlatiliyor", 1.5)
    loading_screen("Reel'ler hazirlaniyor", 1.0)
    
    game = SlotFruit()
    
    while True:
        status = game.get_status()
        
        print("\033[1;34m" + "═" * 56 + "\033[0m")
        print(f"\033[1;33m  🎰 Spin: {status['spins']}  │  📺 Ads: {status['ads']}  │  💰 Toplam: {status['earned']}\033[0m")
        print(f"\033[1;36m  ⏳ Sonraki ödüle: {status['next_reward']} reklam kaldi  │  🎲 Toplam oyun: {status['history_count']}\033[0m")
        print("\033[1;34m" + "═" * 56 + "\033[0m")
        
        print("\n  [1] 🎰  SPIN DONDUR")
        print("  [2] 📺  REKLAM IZLE (Ads Hit 200)")
        print("  [3] ℹ️   DURUM & ISTATISTIK")
        print("  [4] 📜  SON OYUNLAR")
        print("  [5] 🚪  CIKIS")
        
        choice = input("\n\033[1;32mSeciminiz: \033[0m").strip()
        
        if choice == "1":
            result = game.spin()
            if "error" in result:
                print(f"\033[1;31m⚠️  {result['error']}\033[0m")
            else:
                print(f"\n{result['message']}")
                if result['is_jackpot']:
                    print("\033[1;33m🔥 JACKPOT KAZANDIN! 🔥\033[0m")
                print(f"\033[1;33mKalan spin: {result['spins_left']}\033[0m")
                
        elif choice == "2":
            ad_result = game.watch_ad()
            print(f"\n{ad_result['message']}")
            if ad_result['hit']:
                print(f"\033[1;32m💰 +{ad_result['bonus']} bedava spin kazandin!\033[0m")
                print(f"\033[1;36mToplam reklam: {ad_result['total_ads']}\033[0m")
                
        elif choice == "3":
            print(f"\n\033[1;36m{'='*44}\033[0m")
            print(f"  🎰 Mevcut Spin: {status['spins']}")
            print(f"  📺 Toplam Reklam: {status['ads']}")
            print(f"  💰 Toplam Kazanç: {status['earned']}")
            print(f"  🎲 Oynanan Oyun: {status['history_count']}")
            print(f"  ⏳ Sonraki Ads Hit: {status['next_reward']} reklam")
            print(f"\033[1;36m{'='*44}\033[0m")
            
        elif choice == "4":
            history = game.get_history(5)
            if history:
                print(f"\n\033[1;36m{'='*44}\033[0m")
                print("  📜 SON 5 OYUN:")
                for i, h in enumerate(reversed(history), 1):
                    icon = "🎰" if h['is_jackpot'] else ("✅" if h['payout'] > 0 else "❌")
                    print(f"  {icon} {h['combo']} → +{h['payout']} spin")
                print(f"\033[1;36m{'='*44}\033[0m")
            else:
                print("\033[1;33mHenüz oyun oynanmadi.\033[0m")
            
        elif choice == "5":
            print("\n\033[1;33m👋 NINOKI SlotFruit kapatiliyor... Iyi sanslar!\033[0m")
            loading_screen("Kaydediliyor", 0.5)
            break
            
        else:
            print("\033[1;31m⚠️  Gecersiz secim! 1-5 arasi bir sayi girin.\033[0m")
        
        time.sleep(0.3)

# ═════════════════════════════════════════════════════════════════
# GIRIS NOKTASI
# ═════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n\033[1;33m👋 Oyundan cikildi! Gorusmek uzere...\033[0m")
        sys.exit(0)
    except Exception as e:
        print(f"\n\033[1;31m💥 KRITIK HATA: {e}\033[0m")
        import traceback
        traceback.print_exc()
        sys.exit(1)
