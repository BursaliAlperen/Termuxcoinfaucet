# Termuxcoinfaucet

Şeffaf ve düzenlenebilir bir Python/Tkinter paneli:

- 18 coin listesi içerir.
- Her coin için 2 doğrudan site linki vardır.
- Bitly/kısaltılmış link veya gizli anahtar yoktur.
- E-posta ve cüzdan alanları varsayılan olarak doldurulur.
- Arama, seçim işaretleme ve panoya kopyalama özellikleri vardır.

## Termux'a direkt (otomatik) kurulum

Aynı klasördeysen:

```bash
bash install_termux.sh
```

## Ön planda çalıştırma (klasik)

```bash
termux-x11 :1 &
export DISPLAY=:1
python bot.py
```

## Arkaplanda çalıştırma (yeni)

Kurulumdan sonra tek komut:

```bash
./manage_background.sh start
```

Durum kontrolü:

```bash
./manage_background.sh status
```

Durdurma:

```bash
./manage_background.sh stop
```

Log dosyaları:

- `logs/termux-x11.log`
- `logs/bot.log`

## Manuel çalıştırma

```bash
python bot.py
```
