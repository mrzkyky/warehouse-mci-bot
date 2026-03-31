# User Workflow Guide

## Daily Workflow untuk Staff Gudang

### 1. Mulai Hari

Buka Telegram, cari bot, kirim `/start`

### 2. Catat Barang Keluar

**Cara 1: Chat Natural**
```
Kebutuhan migrasi server unit JTB
- DCDU 12B huawei (1 unit)
SN: 21021207316TL4922814
- batterai ZTE ZXDC48 FB100B3 (1 unit)
SN: 219502212702
```

**Cara 2: Foto + OCR (untuk SN)**
1. Kirim foto label barang
2. Bot scan otomatis
3. Tambahkan detail lainnya

### 3. Catat Barang Masuk

```
sisaan BOQ jatibarang > rajak
- tiang 3inch 7m Biasa (25 Btg)
- SFP Huawei 10G 10km (5 pcs)
SN: 21021207316TL4922814, 21021207316TL4922815
```

### 4. Stock Opname

```
SO 15 Maret 2026

∆Data Sfp
SFP MultiMode (MM)
•Huawei 155Mbps 15Km 1310 Nm (2pcs)
•Fiberson 1G 550M 850Nm (1pcs)
•Cisco 1G 550M 850Nm (7pcs)
```

### 5. Rekap Hari Ini

Ketik `/rekap` atau "rekap"

Bot akan kirim:
- 📄 Text report (bisa copy-paste ke WhatsApp grup)
- 📊 Excel file (untuk arsip)

## Format yang Didukung

### Unit/Jumlah
- `pcs` / `buah`
- `pasang` / `pair`
- `unit`
- `gulung`
- `btg` / `batang`
- `meter` / `m`
- `box`
- `set`

### Spesifikasi Otomatis
Bot bisa deteksi:
- **Speed**: `1G`, `10G`, `155Mbps`, dll
- **Distance**: `10Km`, `550M`, dll  
- **Wavelength**: `1310Nm`, `850Nm`, dll

### Brands Auto-Detect
Huawei, Cisco, ZTE, Mikrotik, Nokia, Juniper, HP, Intel, Finisar, dll.

## Tips

### 1. Kirim Multi Item Sekaligus
```
Kebutuhan project X
- Item A (2 pcs)
- Item B (1 unit)
SN: XXX
- Item C (5 pasang)
```

### 2. Simpan Draft
Kalo belum yakin, jangan konfirmasi dulu. Edit dulu baru kirim ulang.

### 3. Foto yang Bagus
- Adequate lighting
- Fokus pada label
- Avoid glare/reflection
- SN harus terbaca jelas

### 4. Backup Data
Excel report otomatis tersimpan, download dari chat untuk backup.

## Common Scenarios

### Scenario: Install di Branch
```
Branch Brebes mas udin
- batterai PJUTS (2 unit)
- ONT Huawei (1 unit)
SN: 4857544312345678
```

### Scenario: Sisaan BOQ
```
sisaan BOQ jatibarang > rajak
- tiang 3inch 7m Biasa (25 Btg)
- kabel dropcore 1core (3 gulung)
```

### Scenario: Stock Opname SFP
```
SO 20 Maret 2026

∆Data Sfp
SFP Single Mode
•Cisco 1G 10Km (3pcs)
•Huawei 10G 10Km (2pcs)
[1270/1330Nm]
```

## Commands

| Command | Fungsi |
|---------|--------|
| `/start` | Menu utama |
| `/rekap` | Laporan hari ini |
| `/scan` | Scan SN dari foto |
| `/help` | Bantuan |
| `/batal` | Batal input |

## FAQ

**Q: Bot tidak mengerti pesan saya?**
A: Pastikan ada keyword: "keluar", "masuk", "sisaan", "kebutuhan", atau "SO"

**Q: SN tidak terdeteksi?**
A: Coba gunakan `/scan` dan kirim foto label

**Q: Bisa edit data?**
A: Untuk sekarang hapus dan input ulang. Kontak admin untuk edit.

**Q: Report kemarin?**
A: Admin bisa generate dengan command `admin.py report -d 2024-03-15`

**Q: Multi user?**
A: Ya, semua orang bisa pakai bot yang sama. Data tersimpan per user.

## Emergency Contacts

Jika ada masalah:
1. Coba `/batal` lalu ulangi
2. Restart bot (admin)
3. Hubungi IT support
