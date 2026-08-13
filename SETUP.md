# 🚀 Quick Setup Guide

Setup dashboard dalam 5 menit!

## ✅ Prerequisites

- Python 3.8+ (download dari https://python.org)
- pip (included dengan Python)
- Excel file `kecil.xlsx`

## 📦 Step 1: Install Dependencies

Open terminal/command prompt, go to project folder:

```bash
# Windows
python -m pip install -r requirements.txt

# Mac/Linux
pip install -r requirements.txt
```

**Expected output:**
```
Successfully installed streamlit plotly pandas numpy openpyxl scikit-learn...
```

Jika ada error, coba:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 🧪 Step 2: Test Data

Validate data sebelum jalankan dashboard:

```bash
python test_data.py
```

**Expected output:**
```
✅ Data loaded successfully!
✅ Ranking calculated for 50 petugas
✅ ALL TESTS PASSED!
✅ Data ready to use in dashboard
```

Jika ada error, check:
1. File `kecil.xlsx` ada di folder yang sama dengan script
2. Format Excel sesuai (check README.md → Data Format)
3. Python version: `python --version` (should be 3.8+)

## 🎯 Step 3: Run Dashboard

```bash
streamlit run dashboard.py
```

**Expected output:**
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

Otomatis akan open di browser. Jika tidak, buka manual:
- http://localhost:8501

## 🎮 Step 4: Explore Dashboard

### Sidebar Filters
1. **Periode**: Select tanggal range
2. **Petugas**: Filter petugas tertentu (atau kosongkan untuk all)
3. **Shift**: Select shift kerja
4. **Ranking Weights**: Adjust bobot untuk setiap criteria

### Main Tabs

**📊 Distribusi Waktu**
- Lihat histogram jam pembacaan
- Breakdown per shift
- Statistik waktu

**🏆 Ranking Petugas**
- Lihat ranking top petugas
- Heatmap petugas × jam
- Adjust weights untuk berbagai scenario

**👤 Detail Per Petugas**
- Select petugas dari dropdown
- Lihat pola kerja individual
- Time series trend

**🗺️ Cakupan Area**
- Visualisasi geographic coverage
- Area statistics per petugas

## 📤 Export Data

Click **📊 Export ke Excel** di sidebar untuk download data yang sudah di-filter

## 🌐 Deploy ke Cloud

### Option A: Streamlit Cloud (Recommended - Free)

1. **Prepare Git repository:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/dashboard-pln
   git push -u origin main
   ```

2. **Deploy:**
   - Go to https://share.streamlit.io
   - Login dengan GitHub account
   - Click "New app"
   - Select: 
     - Repository: `YOUR_USERNAME/dashboard-pln`
     - Branch: `main`
     - Main file path: `dashboard.py`
   - Click "Deploy"

3. **Share URL:** `https://your-app-name-YOUR_USERNAME.streamlit.app`

### Option B: Self-Hosted (Heroku/AWS)

```bash
# Create Procfile
echo "web: streamlit run dashboard.py --server.port=$PORT --server.headless=true" > Procfile

# Deploy ke Heroku
heroku login
heroku create your-app-name
git push heroku main

# Open app
heroku open
```

## 🔧 Troubleshooting

### Error: "ModuleNotFoundError: No module named 'streamlit'"

```bash
# Solution:
pip install streamlit
# or
pip install -r requirements.txt
```

### Error: "File kecil.xlsx not found"

```bash
# Check file exists:
dir  # Windows
ls   # Mac/Linux

# If not there, copy to project folder or update path in data_loader.py
```

### Dashboard loads slowly

```python
# Option 1: Filter data by date range di sidebar
# Option 2: Reduce data size
# Option 3: Increase Streamlit cache
```

### Columns error saat load

1. Open `kecil.xlsx` dengan Excel
2. Check column names match ini:
   - KD_PETUGAS
   - JAM_PEMBACAAN
   - TANGGAL_PEMBACAAN
   - KOORDINAT_X, KOORDINAT_Y
   - IDPEL, NAMA
   - STAND_BACA, STAN_METER, PEMKWH

3. Update `data_loader.py` jika nama berbeda:
   ```python
   # Line: df = df.drop(columns=[...])
   # Tambahkan nama kolom actual Anda
   ```

## 📊 Data Format

**Minimal required columns:**

| Column | Type | Example | Format |
|--------|------|---------|--------|
| KD_PETUGAS | String | P001 | Unique petugas ID |
| TANGGAL_PEMBACAAN | Date | 01/12/2024 | DD/MM/YYYY |
| JAM_PEMBACAAN | Time | 08:30 | HH:MM atau H:MM |
| KOORDINAT_X | Float | -7.2156 | Longitude |
| KOORDINAT_Y | Float | 107.6891 | Latitude |
| IDPEL | String/Int | 123456 | Customer ID |
| NAMA | String | AHMAD | Customer name |
| STAND_BACA | Int | 1234 | Meter reading |
| STAN_METER | Int | 1234 | Meter value |
| PEMKWH | Float | 50.5 | kWh |

**Optional columns:**
- TARIF, BLTH, DAYA, KODE_RBM, etc (akan di-drop otomatis)

## 🎓 Customization

### Change Ranking Weights

Edit di sidebar (recommended) atau di `dashboard.py`:

```python
ranking_weights = {
    'total_pembacaan': 0.40,      # ← adjust here
    'konsistensi_waktu': 0.30,
    'efisiensi_area': 0.20,
    'kecepatan_pembacaan': 0.10
}
```

### Change Colors

Edit di `modules/visualizations.py`:

```python
PLN_COLORS = ['#003366', '#FF6600', ...]  # PLN branding colors

SHIFT_COLORS = {
    'Pagi (06-11)': '#FFD700',
    'Siang (11-16)': '#FFA500',
    ...
}
```

### Add Custom Analysis

1. Edit `modules/metrics.py` → add new metric function
2. Edit `modules/visualizations.py` → add new chart function
3. Edit `dashboard.py` → add new tab dan integrate

Example:
```python
# 1. Add metric function in metrics.py
def calculate_custom_metric(df):
    return result

# 2. Add chart in visualizations.py
def plot_custom_chart(df):
    return fig

# 3. Use in dashboard.py
custom_result = calculate_custom_metric(df_filtered)
fig = plot_custom_chart(df_filtered)
st.plotly_chart(fig)
```

## 📞 Support

- **Setup issues**: Check error message di terminal
- **Data issues**: Run `python test_data.py` untuk diagnose
- **Features**: Edit code atau ask supervisor
- **Performance**: Filter data atau optimize queries

## 🎉 Done!

Dashboard sudah ready untuk presentation ke PLN supervisor.

**Next steps:**
1. Prepare presentation talking points
2. Test dengan supervisor
3. Adjust ranking weights sesuai feedback
4. Deploy ke production

Good luck! 🚀
