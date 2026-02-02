# Sistem Analisis Gadai

Sistem terintegrasi untuk analisis data gadai dengan struktur modular dan mudah dibaca.

## 📁 Struktur Project

```
gadai_bigdata/
├── config.py                    # Konfigurasi global
├── main.py                      # Entry point utama
├── README.md                    # Dokumentasi
├── requirements.txt             # Dependencies
│
├── data/                        # Folder data input
│   └── gadai_raw.xlsx
│
├── output/                      # Folder hasil analisis
│   ├── gadai_processed.csv
│   ├── outlet_summary.csv
│   └── summary.txt
│
└── src/                         # Source code modules
    ├── loader.py               # Load & normalisasi data
    ├── processor.py            # Processing & feature engineering
    ├── analyzer.py             # Analisis & agregasi
    ├── reporter.py             # Generate laporan
    ├── utils.py                # Utility functions
    │
    └── (scripts lama - opsional)
        ├── dedupe_gadai.py
        ├── feature_risk_gadai.py
        ├── normalize_gadai.py
        ├── validate_gadai.py
        └── visualize_outlet_risk.py
```

## 🚀 Cara Pakai

### 1. Install Dependencies
```bash
pip install pandas openpyxl matplotlib seaborn numpy
```

### 2. Jalankan Sistem
```bash
python main.py
```

### 3. Lihat Hasil
Output akan tersimpan di folder `output/`:
- `gadai_processed.csv` - Data lengkap hasil processing
- `outlet_summary.csv` - Summary per outlet
- `summary.txt` - Ringkasan analisis

## 📊 Fitur Sistem

### 1. **Loader Module** (`src/loader.py`)
- Load data dari Excel
- Normalisasi nama kolom otomatis

### 2. **Processor Module** (`src/processor.py`)
- Auto-detect kolom penting
- Type casting (datetime, numeric)
- Feature engineering:
  - Lama gadai (hari)
  - Outstanding pokok
  - Rasio pinjaman
  - Status transaksi (aktif/lunas/lewat_jt)
  - Flag high risk

### 3. **Analyzer Module** (`src/analyzer.py`)
- Analisis status transaksi
- Agregasi per outlet
- Identifikasi outlet berisiko

### 4. **Reporter Module** (`src/reporter.py`)
- Generate CSV reports
- Generate summary text
- Top 10 outlet rankings

## ⚙️ Konfigurasi

Edit `config.py` untuk mengubah:
- Path file input/output
- Threshold risiko
- Prioritas status
- Mapping kolom

```python
# Contoh: Ubah threshold risiko
RISK_THRESHOLD = {
    "rasio_pinjaman": 0.9,   # 90%
    "late_ratio": 0.3,        # 30%
    "auction_ratio": 0.2      # 20%
}
```

## 📝 Output Example

```
============================================================
  SISTEM ANALISIS GADAI
  2026-02-02 10:30:45
============================================================

============================================================
  STEP 1: LOADING DATA
============================================================
✓ Data loaded dari: gadai_raw.xlsx

Data Awal
  Baris: 26,908
  Kolom: 23

✓ Kolom berhasil dinormalisasi
  Jumlah kolom: 23

============================================================
  STEP 2: PROCESSING DATA
============================================================

✓ Kolom terdeteksi:
  ✓ pinjaman        -> pokok pinjaman
  ✓ jaminan         -> pokok pinjaman
  ✓ terbayar        -> pokok terbayar
  ✓ tanggal         -> tanggal
  ✓ tanggal_jt      -> tanggal jt
  ✓ outlet          -> outlet

✓ Type casting...
✓ Feature engineering...
  - Lama gadai (hari)
  - Outstanding pokok
  - Rasio pinjaman
  - Status transaksi
  - Flag high risk

============================================================
  STEP 3: ANALYZING DATA
============================================================

✓ Status Transaksi:
  - aktif       : 15,234 ( 56.6%)
  - lunas       :  8,901 ( 33.1%)
  - lewat_jt    :  2,773 ( 10.3%)

✓ Analisis 45 outlet selesai

Top 5 Outlet (berdasarkan total pinjaman):
  Outlet Jakarta Pusat           - Rp 5,234,567,890 (2156 transaksi)
  Outlet Bandung                 - Rp 3,456,789,012 (1823 transaksi)
  ...

============================================================
  STEP 4: SAVING REPORTS
============================================================
✓ Data processed    : gadai_processed.csv
✓ Outlet summary    : outlet_summary.csv
✓ Summary text      : summary.txt

✓ Semua laporan tersimpan di folder: output/

============================================================
  ✓ PROSES SELESAI
============================================================

Total data diproses  : 26,908 transaksi
Total outlet         : 45 outlet
Transaksi berisiko   : 3,456 (12.8%)
```

## 🔧 Maintenance

### Tambah Fitur Baru
1. Buat module baru di `src/`
2. Import di `main.py`
3. Panggil di function `main()`

### Update Threshold
Edit nilai di `config.py`:
```python
RISK_THRESHOLD = {
    "rasio_pinjaman": 0.85,  # Ubah dari 0.9 ke 0.85
}
```

## 📞 Support

Untuk pertanyaan atau issue, hubungi Big Data Team.

---
**Version:** 1.0.0  
**Last Updated:** February 2026
