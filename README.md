# 📊 PLN Meter Reading Activity Dashboard

Dashboard interaktif untuk analisis aktivitas pembacaan meter di PLN UP3 Garut.

## 📋 Fitur Utama

✅ **Distribusi Waktu Pembacaan**
- Histogram jam pembacaan per shift
- Statistik waktu kerja
- Pie chart persentase per shift

✅ **Perangkingan Petugas**
- Multi-criteria ranking (total, konsistensi, efisiensi, kecepatan)
- Customizable weights untuk setiap criteria
- Heatmap petugas × jam kerja

✅ **Analisis Detail Per Petugas**
- Pola kerja individual
- Time series pembacaan
- Trend harian

✅ **Cakupan Area Geografis**
- Scatter map koordinat pembacaan
- Coverage analysis per petugas
- Area statistics

## 🚀 Quick Start

### 1. Clone / Download Project

```bash
# Struktur folder
project/
├── dashboard.py
├── requirements.txt
├── README.md
└── modules/
    ├── __init__.py
    ├── data_loader.py
    ├── metrics.py
    └── visualizations.py
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Prepare Data

Pastikan file `kecil.xlsx` ada di folder yang sama dengan `dashboard.py`, atau update path di `data_loader.py`

```python
# Minimal struktur Excel file yang dibutuhkan:
# Columns: KD_PETUGAS, JAM_PEMBACAAN, TANGGAL_PEMBACAAN, KOORDINAT_X, KOORDINAT_Y, 
#          IDPEL, NAMA, STAND_BACA, STAN_METER, PEMKWH
```

### 4. Run Dashboard

**Locally:**
```bash
streamlit run dashboard.py
```

Dashboard akan tersedia di: `http://localhost:8501`

**On Cloud (Streamlit Cloud):**
```bash
git push ke GitHub
1. Go to https://share.streamlit.io
2. Deploy dari repo Anda
3. Update GitHub Secrets untuk data file (opsional)
```

## 📊 Cara Penggunaan

### Sidebar Filters

**Periode**
- Pilih rentang tanggal untuk filter data

**Petugas**
- Kosongkan untuk melihat semua petugas
- Atau pilih petugas spesifik

**Shift Kerja**
- Filter berdasarkan shift (Pagi, Siang, Sore, Malam)

**Konfigurasi Ranking**
- Adjust bobot untuk setiap criteria:
  - **Total Pembacaan** (default 35%)
  - **Konsistensi Waktu** (default 30%)
  - **Efisiensi Area** (default 20%)
  - **Kecepatan Pembacaan** (default 15%)
- Weights otomatis dinormalisasi

### Tabs

**1. Distribusi Waktu**
- Histogram jam pembacaan
- Breakdown per shift
- Statistik waktu detail

**2. Ranking Petugas**
- Visualisasi ranking score
- Heatmap petugas × jam
- Tabel ranking lengkap

**3. Detail Per Petugas**
- Select petugas dari dropdown
- Pola kerja individual
- Trend pembacaan harian

**4. Cakupan Area**
- Geographic scatter plot
- Area statistics per petugas

## 🔧 Technical Details

### Data Processing

#### `modules/data_loader.py`
- Load Excel file
- Clean & parse data:
  - `JAM_PEMBACAAN`: Parse berbagai format time (HH:MM, H:MM, HH:MM:SS)
  - `TANGGAL_PEMBACAAN`: Parse format DD/MM/YYYY
  - Time features: hour, minute, shift categorization
  - Geographic: fill missing koordinat dengan median
- Validate & export summary

**Supported time formats:**
```
"08:30"       → 510 minutes (08:30)
"8:30"        → 510 minutes
"08:30:45"    → 510 minutes
"00 08:30:45" → 510 minutes (DD HH:MM:SS format)
```

#### `modules/metrics.py`
Perhitungan ranking dengan 4 criteria:

1. **Total Pembacaan Score (35%)**
   - Normalized: pembacaan_petugas / total_pembacaan * 100
   - Boosted untuk relevance

2. **Konsistensi Waktu Score (30%)**
   - Coefficient of Variation: std dev / mean
   - Lower CV = higher score
   - Range: 0-100

3. **Efisiensi Area Score (20%)**
   - Geographic spread (X range × Y range)
   - Bonus untuk diversity pelanggan
   - Range: 0-100

4. **Kecepatan Pembacaan Score (15%)**
   - Average time gap antar pembacaan (per hari)
   - Optimal: 10-15 minutes
   - Range: 0-100

**Ranking Score Formula:**
```
Score = (
    0.35 × total_score +
    0.30 × consistency_score +
    0.20 × efficiency_score +
    0.15 × speed_score
)
```

#### `modules/visualizations.py`
- Plotly charts (interactive)
- PLN color palette (`#003366`, `#FF6600`, etc)
- Responsive design

### Architecture

```
User Input (Sidebar)
        ↓
Data Filtering (Pandas)
        ↓
Metrics Calculation
        ↓
Visualization (Plotly)
        ↓
Display (Streamlit)
```

## 📈 Performance Tips

**Untuk 14,000 data points:**
- Load time: ~2-3 detik (first load dengan cache)
- Filter update: ~1 detik
- Max memory: ~200MB

**Optimization:**
- `@st.cache_data` untuk data loading
- Vectorized pandas operations
- Efficient plotly rendering

## 🔐 Deployment

### Option 1: Streamlit Cloud (Free)

```bash
# Setup
1. Push ke GitHub (public repo)
2. Go to https://share.streamlit.io
3. Deploy dengan GitHub auth

# Setup data file (2 cara):
A. Commit kecil.xlsx ke repo
B. Upload via Streamlit secrets:
   - Dashboard settings → Secrets
   - Upload file dalam session
```

### Option 2: Self-Hosted (PLN Server)

```bash
# Server requirements
- Python 3.8+
- 2GB RAM minimum
- Port 8501 (Streamlit default)

# Setup
git clone <repo>
cd dashboard
pip install -r requirements.txt
streamlit run dashboard.py --server.port 80

# Background process
nohup streamlit run dashboard.py > dashboard.log 2>&1 &
```

### Option 3: Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "dashboard.py", "--server.port", "8501"]
```

```bash
docker build -t pln-dashboard .
docker run -p 8501:8501 pln-dashboard
```

## 📝 Configuration

### Ranking Weights

Edit di sidebar atau hardcode di `dashboard.py`:

```python
ranking_weights = {
    'total_pembacaan': 0.35,      # Total pembacaan
    'konsistensi_waktu': 0.30,    # Konsistensi jam kerja
    'efisiensi_area': 0.20,       # Coverage geografis
    'kecepatan_pembacaan': 0.15   # Kecepatan gap antar pembacaan
}
```

### Color Palette

Update di `modules/visualizations.py`:

```python
PLN_COLORS = ['#003366', '#FF6600', '#FFD700', '#FF6347', '#4B0082']

SHIFT_COLORS = {
    'Pagi (06-11)': '#FFD700',
    'Siang (11-16)': '#FFA500',
    'Sore (16-21)': '#FF6347',
    'Malam (21-06)': '#4B0082'
}
```

## 🐛 Troubleshooting

**Error: File tidak ditemukan**
```
Solusi: Update path di modules/data_loader.py:
    possible_paths = [file_path, '/path/to/kecil.xlsx', ...]
```

**Error: Column tidak ditemukan**
```
Solusi: Update nama kolom di data_loader.py sesuai Excel Anda
    df.columns untuk check existing columns
```

**Performa lambat**
```
Solusi:
- Reduce data volume (filter by date range)
- Use st.cache_data decorator
- Lower resolution untuk scatter plots
```

**Heatmap tidak muncul**
```
Solusi: 
- Pastikan ada minimal 5+ petugas berbeda
- Check koordinat tidak kosong
```

## 📊 Expected Output

### KPI Cards
```
Total Pembacaan: 14,000
Jumlah Petugas: 50
Jumlah Pelanggan: 8,000
Rata-rata per Petugas: 280
Pembacaan/Pelanggan: 1.75
```

### Ranking Top 3
```
Rank 1: [PETUGAS_001] - Score 89.5
  Total: 400 meter
  Consistency: 92
  Efficiency: 85
  Speed: 88

Rank 2: [PETUGAS_002] - Score 87.3
  ...
```

## 🔄 Update Data

**Untuk update dengan data terbaru:**

```python
# Option 1: Replace Excel file
# Delete kecil.xlsx, upload file baru

# Option 2: Modify data_loader.py
def load_data():
    # Fetch dari database / API
    # Atau read dari multiple Excel files
    pass

# Option 3: Streamlit file uploader
uploaded_file = st.file_uploader("Upload Excel", type='xlsx')
if uploaded_file:
    df = pd.read_excel(uploaded_file)
```

## 📖 References

- [Streamlit Docs](https://docs.streamlit.io)
- [Plotly Docs](https://plotly.com/python/)
- [Pandas Docs](https://pandas.pydata.org/docs/)

## 👨‍💼 Support

- **Questions**: Tanya Mei atau supervisor PLN
- **Bugs**: Report dengan screenshot + error message
- **Feature Request**: List di GitHub issues

## 📄 License

Internal use for PLN UP3 Garut only.

---

**Last Updated**: 2024  
**Version**: 1.0  
**Status**: ✅ Production Ready
