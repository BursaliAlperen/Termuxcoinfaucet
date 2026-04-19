"""Termux Coin Faucet dashboard.

This file replaces the previous encrypted loader with a transparent,
editable Tkinter application.
"""

from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass
from datetime import datetime
from tkinter import ttk


@dataclass(frozen=True)
class FaucetSite:
    name: str
    url: str


@dataclass(frozen=True)
class Coin:
    symbol: str
    network: str
    sites: tuple[FaucetSite, FaucetSite]


DEFAULT_EMAIL = "ankaralironaldo131@gmail.com"
DEFAULT_WALLET = "74CAMdGaWgAnhNdR9biSkxRYK6BCY86K"


COINS: list[Coin] = [
    Coin("BTC", "Bitcoin", (FaucetSite("Site A", "https://freebitco.in"), FaucetSite("Site B", "https://faucetcrypto.com"))),
    Coin("ETH", "Ethereum", (FaucetSite("Site A", "https://faucetscrypto.com"), FaucetSite("Site B", "https://faucetpay.io"))),
    Coin("LTC", "Litecoin", (FaucetSite("Site A", "https://litecoinfaucet.org"), FaucetSite("Site B", "https://allcoins.pw"))),
    Coin("DOGE", "Dogecoin", (FaucetSite("Site A", "https://dogefaucet.com"), FaucetSite("Site B", "https://faucet.ooo"))),
    Coin("TRX", "Tron", (FaucetSite("Site A", "https://tronfaucet.xyz"), FaucetSite("Site B", "https://earnbitmoon.club"))),
    Coin("BNB", "BNB Smart Chain", (FaucetSite("Site A", "https://freebnb.co.in"), FaucetSite("Site B", "https://pipeflare.io"))),
    Coin("SOL", "Solana", (FaucetSite("Site A", "https://solfaucet.togatech.org"), FaucetSite("Site B", "https://stakely.io/en/faucet/solana-sol"))),
    Coin("ADA", "Cardano", (FaucetSite("Site A", "https://cardanofaucet.net"), FaucetSite("Site B", "https://allfaucet.xyz"))),
    Coin("XRP", "Ripple", (FaucetSite("Site A", "https://xrpfaucet.info"), FaucetSite("Site B", "https://faucetspeedbtc.com"))),
    Coin("BCH", "Bitcoin Cash", (FaucetSite("Site A", "https://bchfaucet.com"), FaucetSite("Site B", "https://firefaucet.win"))),
    Coin("DASH", "Dash", (FaucetSite("Site A", "https://dashfaucet.org"), FaucetSite("Site B", "https://coinfaucet.eu"))),
    Coin("ZEC", "Zcash", (FaucetSite("Site A", "https://zecfaucet.org"), FaucetSite("Site B", "https://freeltc.online"))),
    Coin("XLM", "Stellar", (FaucetSite("Site A", "https://stellarfaucet.com"), FaucetSite("Site B", "https://faucetworld.in"))),
    Coin("MATIC", "Polygon", (FaucetSite("Site A", "https://faucet.polygon.technology"), FaucetSite("Site B", "https://stakely.io/en/faucet/polygon-matic"))),
    Coin("AVAX", "Avalanche", (FaucetSite("Site A", "https://core.app/tools/testnet-faucet"), FaucetSite("Site B", "https://faucets.chain.link/fuji"))),
    Coin("TON", "TON", (FaucetSite("Site A", "https://faucet.tonxapi.com"), FaucetSite("Site B", "https://testgiver.ton.org"))),
    Coin("ATOM", "Cosmos", (FaucetSite("Site A", "https://stakely.io/en/faucet/cosmos-atom"), FaucetSite("Site B", "https://faucet.quicknode.com/cosmos"))),
    Coin("DOT", "Polkadot", (FaucetSite("Site A", "https://paritytech.github.io/polkadot-testnet-faucet"), FaucetSite("Site B", "https://faucet.polkadot.io"))),
]


class FaucetApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Termux Coin Faucet Panel")
        self.geometry("1080x700")
        self.configure(bg="#0f172a")

        self.search_var = tk.StringVar()
        self.email_var = tk.StringVar(value=DEFAULT_EMAIL)
        self.wallet_var = tk.StringVar(value=DEFAULT_WALLET)
        self.status_var = tk.StringVar(value="Hazır")
        self.rows: list[tuple[Coin, tk.BooleanVar, tk.BooleanVar, tk.StringVar]] = []

        self._build_layout()

    def _build_layout(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Treeview", rowheight=28)

        header = tk.Label(
            self,
            text="18 Coin • 2 Site / Coin • Bitly ve Key Yok",
            bg="#0f172a",
            fg="#e2e8f0",
            font=("Segoe UI", 16, "bold"),
            pady=12,
        )
        header.pack(fill="x")

        top = tk.Frame(self, bg="#0f172a")
        top.pack(fill="x", padx=16, pady=(0, 8))

        tk.Label(top, text="E-posta", bg="#0f172a", fg="#cbd5e1").grid(row=0, column=0, sticky="w")
        tk.Entry(top, textvariable=self.email_var, width=35).grid(row=1, column=0, padx=(0, 8), sticky="ew")
        tk.Label(top, text="Cüzdan", bg="#0f172a", fg="#cbd5e1").grid(row=0, column=1, sticky="w")
        tk.Entry(top, textvariable=self.wallet_var, width=45).grid(row=1, column=1, padx=(0, 8), sticky="ew")
        tk.Label(top, text="Ara (coin/network)", bg="#0f172a", fg="#cbd5e1").grid(row=0, column=2, sticky="w")
        search_entry = tk.Entry(top, textvariable=self.search_var, width=25)
        search_entry.grid(row=1, column=2, sticky="ew")
        search_entry.bind("<KeyRelease>", lambda _e: self.refresh_rows())

        top.columnconfigure(1, weight=1)
        top.columnconfigure(2, weight=1)

        table = ttk.Treeview(
            self,
            columns=("coin", "network", "site_a", "site_b", "checked"),
            show="headings",
            height=16,
        )
        self.table = table
        table.heading("coin", text="Coin")
        table.heading("network", text="Network")
        table.heading("site_a", text="Site A (Direkt)")
        table.heading("site_b", text="Site B (Direkt)")
        table.heading("checked", text="Son İşaret")
        table.column("coin", width=80)
        table.column("network", width=140)
        table.column("site_a", width=320)
        table.column("site_b", width=320)
        table.column("checked", width=160)
        table.pack(fill="both", expand=True, padx=16)

        controls = tk.Frame(self, bg="#0f172a")
        controls.pack(fill="x", padx=16, pady=10)

        tk.Button(controls, text="Seçili Coin'i İşaretle", command=self.mark_selected, bg="#22c55e", fg="#0b1220").pack(side="left")
        tk.Button(controls, text="Kopyala: Hesap Bilgisi", command=self.copy_identity, bg="#38bdf8", fg="#0b1220").pack(side="left", padx=8)
        tk.Label(controls, textvariable=self.status_var, bg="#0f172a", fg="#e2e8f0").pack(side="right")

        self.refresh_rows()

    def refresh_rows(self) -> None:
        for item in self.table.get_children():
            self.table.delete(item)

        query = self.search_var.get().strip().lower()
        for coin in COINS:
            haystack = f"{coin.symbol} {coin.network}".lower()
            if query and query not in haystack:
                continue

            self.table.insert(
                "",
                "end",
                values=(
                    coin.symbol,
                    coin.network,
                    coin.sites[0].url,
                    coin.sites[1].url,
                    "-",
                ),
            )

        self.status_var.set(f"Gösterilen coin: {len(self.table.get_children())}/{len(COINS)}")

    def mark_selected(self) -> None:
        selected = self.table.selection()
        if not selected:
            self.status_var.set("Önce bir coin seç.")
            return

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for row_id in selected:
            current = list(self.table.item(row_id, "values"))
            current[-1] = now
            self.table.item(row_id, values=current)
        self.status_var.set(f"{len(selected)} coin işaretlendi.")

    def copy_identity(self) -> None:
        payload = f"email={self.email_var.get()}\nwallet={self.wallet_var.get()}"
        self.clipboard_clear()
        self.clipboard_append(payload)
        self.status_var.set("Hesap bilgisi panoya kopyalandı.")


if __name__ == "__main__":
    app = FaucetApp()
    app.mainloop()
