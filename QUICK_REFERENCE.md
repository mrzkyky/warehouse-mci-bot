# Quick Reference Card 📋

## Bot Commands

| Command | What it does |
|---------|--------------|
| `/start` | Show welcome & main menu |
| `/rekap` | Generate today's report |
| `/scan` | Scan SN from photo |
| `/help` | Show help message |
| `/batal` | Cancel current operation |

## Message Formats

### 🔴 Barang Keluar
```
Kebutuhan [project/tujuan]
- [nama barang] ([jumlah] [unit])
SN: [serial number]
```
**Example:**
```
Kebutuhan migrasi server unit JTB
- DCDU 12B huawei (1 unit)
SN: 21021207316TL4922814
- batterai ZTE (2 unit)
```

### 🟢 Barang Masuk
```
[sumber: sisaan/dari/terima]
- [nama barang] ([jumlah] [unit])
SN: [serial number]
```
**Example:**
```
sisaan BOQ jatibarang > rajak
- tiang 3inch 7m Biasa (25 Btg)
```

### 🔵 Stock Opname (SO)
```
SO [tanggal]

∆Data [kategori]
•[merk] [nama] [spec] ([jumlah] [unit])
```
**Example:**
```
SO 15 Maret 2026

∆Data Sfp
SFP MultiMode (MM)
•Huawei 155Mbps 15Km 1310Nm (2pcs)
•Fiberson 1G 550M 850Nm (1pcs)
```

## Supported Units

| Unit | Aliases |
|------|---------|
| pcs | buah, pcs |
| pasang | pair, pasang |
| unit | unit |
| gulung | gulung |
| btg | batang, btg |
| meter | m, meter |
| box | box |
| set | set |

## Auto-Detected Specs

Bot otomatis detect:
- **Speed**: `1G`, `10G`, `155Mbps`, `2.5G`, `25G`, `40G`, `100G`
- **Distance**: `550M`, `10Km`, `20Km`, `40Km`, `80Km`
- **Wavelength**: `850Nm`, `1310Nm`, `1550Nm`, `1270Nm`, `1330Nm`

## Auto-Detected Brands

Huawei, Cisco, ZTE, Mikrotik, TP-Link, Nokia, Alcatel-Lucent, Juniper, HP, 
Intel, Finisar, Rapid, Tarmoc, 6Com, Optone, WBS, Gcon, Nufiber, Yxfiber,
Raisecom, Ciptara, Fiberson, Gigalight, HG Genuine, Itachi, WTD, Etulink,
Mikrobits

## File Locations

| File Type | Location |
|-----------|----------|
| Database | `data/warehouse.db` |
| Reports | `reports/laporan_gudang_YYYY-MM-DD.xlsx` |
| Temp files | `temp/` (auto-cleaned) |
| Config | `.env` |

## Docker Commands

```bash
# Start
docker-compose up -d

# View logs
docker-compose logs -f bot

# Stop
docker-compose down

# Restart
docker-compose restart

# Rebuild
docker-compose up -d --build
```

## Admin Commands (CLI)

```bash
# Show stats
python admin.py stats

# List recent
python admin.py list -n 20

# Generate report
python admin.py report -d 2024-03-15 -f excel

# Export to CSV
python admin.py export -o backup.csv

# Delete transaction
python admin.py delete 123
```

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `BOT_TOKEN` | Telegram bot token | `123456:ABC-DEF...` |
| `ADMIN_IDS` | Comma-separated user IDs | `123456789,987654321` |
| `DATABASE_URL` | Database connection | `sqlite:///data/warehouse.db` |
| `TESSERACT_CMD` | OCR binary path | `/usr/bin/tesseract` |
| `COMPANY_NAME` | Company name in reports | `PT Rapid Network` |
| `REPORT_TIMEZONE` | Timezone | `Asia/Jakarta` |

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Bot tidak respon | Check token di `.env`, restart bot |
| OCR gagal | Pastikan foto jelas, terang, no blur |
| DB locked | Gunakan PostgreSQL atau restart |
| Parser salah | Gunakan format yang lebih eksplisit |
| SN tidak detect | Coba `/scan` dengan foto lebih dekat |

## Quick Test

Kirim pesan ini ke bot untuk test:
```
Kebutuhan test project
- SFP Huawei 10G 10Km (2 pcs)
SN: 21021207316TL4922814
```

Bot harus reply dengan konfirmasi detail barang.

## Support

- 🐛 Bug report: admin.py → export data
- 💡 Feature request: edit config.py
- 🆘 Emergency: `/batal` lalu ulangi

---

**Version:** 1.0  
**Updated:** March 2024  
**Maintainer:** Your IT Team
