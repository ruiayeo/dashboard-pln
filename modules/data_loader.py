import pandas as pd
import numpy as np
from pathlib import Path
import re

def load_and_clean_data(file_obj=None):
    """
    Load dan clean data dari Excel file

    Parameters:
    -----------
    file_obj : file-like object or None
        File object dari st.file_uploader, atau None untuk fallback ke file lokal

    Returns:
    --------
    pd.DataFrame
        Cleaned dataframe dengan columns yang sudah diproses
    """

    df = None
    
    # Jika ada file upload dari Streamlit
    if file_obj is not None:
        try:
            print(f"Loading data dari uploaded file: {file_obj.name}")
            df = pd.read_excel(file_obj, sheet_name=0)
        except Exception as e:
            raise ValueError(f"Gagal membaca file uploaded: {str(e)}")
    else:
        # Fallback ke file lokal (untuk testing/development)
        possible_paths = [
            '9.GRTREKAGT26-BACA-A_11-08-2026.xlsx',
            'kecil.xlsx',
            Path('.') / '9.GRTREKAGT26-BACA-A_11-08-2026.xlsx',
            Path('.') / 'kecil.xlsx',
        ]

        for path in possible_paths:
            if Path(path).exists():
                print(f"Loading data dari file lokal: {path}")
                df = pd.read_excel(path, sheet_name=0) 
                break

        if df is None:
            raise FileNotFoundError(
                f"Tidak ada file Excel ditemukan. "
                f"Pilih file via upload Streamlit atau letakkan file di folder project."
            )

    # CLEANING & FEATURE ENGINEERING
    # Drop kolom yang tidak perlu
    cols_to_drop = ['Column1', 'UP3', 'ULP', 'TARIF', 'BLTH', 'DAYA', 'KD_PETUGAS', 'KODE_PESAN', 'DLPD']
    df = df.drop(columns=[col for col in cols_to_drop if col in df.columns], errors='ignore')

    # Rename columns ke lowercase dengan underscore
    df.columns = df.columns.str.lower().str.replace(' ', '_')

    # Parse tanggal pembacaan
    df['tanggal_pembacaan'] = pd.to_datetime(df['tanggal_pembacaan'], format='%d/%m/%Y', errors='coerce')

    # Parse jam pembacaan - handle berbagai format
    df['jam_pembacaan'] = df['jam_pembacaan'].astype(str).str.strip()
    df['jam_pembacaan_menit'] = df['jam_pembacaan'].apply(_parse_time_to_minutes)

    # Extract jam dan menit sebagai separate columns
    df['jam'] = df['jam_pembacaan_menit'] // 60
    df['menit'] = df['jam_pembacaan_menit'] % 60

    # Categorize shift
    df['shift'] = df['jam_pembacaan_menit'].apply(_assign_shift)

    # Kode petugas diambil dari KODE_RBM (atau KD_PETUGAS)
    if 'kode_rbm' in df.columns:
        df['kd_petugas'] = df['kode_rbm'].astype(str).str.strip().str.upper()
    elif 'kd_petugas' in df.columns:
        df['kd_petugas'] = df['kd_petugas'].astype(str).str.strip().str.upper()
    else:
        print("Warning: kd_petugas dan kode_rbm tidak ditemukan")
        df['kd_petugas'] = 'UNKNOWN'

    # Clean customer ID dan nama
    if 'idpel' in df.columns:
        df['idpel'] = df['idpel'].astype(str).str.strip()
    else:
        print("Warning: idpel kolom tidak ditemukan")
        df['idpel'] = 'UNKNOWN'

    # Nama pelanggan - try berbagai nama kolom
    if 'nama_pelanggan' in df.columns:
        df['nama_pelanggan'] = df['nama_pelanggan'].astype(str).str.strip()
    elif 'nama' in df.columns:
        df['nama_pelanggan'] = df['nama'].astype(str).str.strip()
    else:
        df['nama_pelanggan'] = 'N/A'

    # Handle koordinat - AUTO-DETECT nama kolom 
    lat_names = ['koordinat_y', 'lat', 'latitude', 'lintang', 'lintang_gps', 'y', 'LATITUDE', 'Latitude']
    lon_names = ['koordinat_x', 'lon', 'long', 'longitude', 'bujur', 'bujur_gps', 'x', 'LONGITUDE', 'Longitude']
    
    lat_col = None
    lon_col = None
    
    # Cari kolom lintang (Y)
    for name in lat_names:
        if name in df.columns:
            lat_col = name
            break
    
    # Cari kolom bujur (X)
    for name in lon_names:
        if name in df.columns:
            lon_col = name
            break
    
    # Jika ditemukan, rename ke standard name dan convert to numeric
    if lat_col and lon_col:
        df.rename(columns={lat_col: 'koordinat_y', lon_col: 'koordinat_x'}, inplace=True)
        print(f"Auto-detected GPS columns: {lat_col} (Y), {lon_col} (X)")
    elif lat_col and not lon_col:
        df.rename(columns={lat_col: 'koordinat_y'}, inplace=True)
        print(f"Found lintang column {lat_col}, but bujur column not found")
        df['koordinat_x'] = 0
    elif lon_col and not lat_col:
        df.rename(columns={lon_col: 'koordinat_x'}, inplace=True)
        print(f"Found bujur column {lon_col}, but lintang column not found")
        df['koordinat_y'] = 0
    else:
        print(f"GPS columns not found. Peta tidak akan muncul di dashboard.")
        print(f"Available columns: {list(df.columns)}")
        df['koordinat_x'] = 0
        df['koordinat_y'] = 0
    
    # Convert to numeric dan fill missing values dengan 0
    if 'koordinat_x' in df.columns:
        df['koordinat_x'] = pd.to_numeric(df['koordinat_x'], errors='coerce').fillna(0)
    else:
        df['koordinat_x'] = 0
    
    if 'koordinat_y' in df.columns:
        df['koordinat_y'] = pd.to_numeric(df['koordinat_y'], errors='coerce').fillna(0)
    else:
        df['koordinat_y'] = 0

    # Handle meter reading values
    df['ada_pembacaan_aktual'] = pd.to_numeric(df['stand_baca'] if 'stand_baca' in df.columns else 0, errors='coerce').notna()

    if 'stand_baca' in df.columns:
        df['stand_baca'] = pd.to_numeric(df['stand_baca'], errors='coerce').fillna(0).astype(int)
    else:
        df['stand_baca'] = 0

    if 'stan_meter' in df.columns:
        df['stan_meter'] = pd.to_numeric(df['stan_meter'], errors='coerce').fillna(0).astype(int)
    else:
        df['stan_meter'] = 0

    if 'pemkwh' in df.columns:
        df['pemkwh'] = pd.to_numeric(df['pemkwh'], errors='coerce').fillna(0).astype(float)
    else:
        df['pemkwh'] = 0.0

    # Buang baris tanpa pembacaan aktual
    n_before = len(df)
    df = df[df['ada_pembacaan_aktual']].drop(columns=['ada_pembacaan_aktual']).reset_index(drop=True)
    n_dropped = n_before - len(df)
    if n_dropped > 0:
        print(f"Rows without active reading removed: {n_dropped}")

    # Sort by time
    df = df.sort_values(['tanggal_pembacaan', 'jam_pembacaan_menit']).reset_index(drop=True)

    # Select final columns
    final_columns = [
        'tanggal_pembacaan', 'jam_pembacaan', 'jam_pembacaan_menit', 'jam', 'menit', 'shift',
        'kd_petugas', 'nama_pelanggan', 'idpel',
        'koordinat_x', 'koordinat_y',
        'stand_baca', 'stan_meter', 'pemkwh'
    ]

    df = df[[col for col in final_columns if col in df.columns]]

    # Validate
    print(f"\nData loaded: {len(df)} rows x {len(df.columns)} columns")
    print(f"Unique petugas: {df['kd_petugas'].nunique()}")
    print(f"Unique pelanggan: {df['idpel'].nunique()}")
    print(f"Date range: {df['tanggal_pembacaan'].min()} to {df['tanggal_pembacaan'].max()}")
    
    # Cek GPS data
    valid_gps = len(df[(df['koordinat_x'] != 0) & (df['koordinat_y'] != 0)])
    if valid_gps > 0:
        print(f"Valid GPS points: {valid_gps}")
    else:
        print(f"Valid GPS points: 0")

    return df


def _parse_time_to_minutes(time_str):
    """
    Parse berbagai format waktu ke dalam menit

    Format yang bisa dihandle:
    - "08:30" -> 510
    - "8:30" -> 510
    - "08:30:45" -> 510
    - "HH:MM:SS" format
    - "H:MM:SS" format
    """

    try:
        if pd.isna(time_str):
            return np.nan

        time_str = str(time_str).strip()

        # Handle format "DD HH:MM:SS"
        if ' ' in time_str:
            time_str = time_str.split(' ', 1)[1]

        # Split by colon
        parts = time_str.split(':')

        if len(parts) >= 2:
            hour = int(parts[0])
            minute = int(parts[1])
            return hour * 60 + minute
        else:
            return np.nan

    except Exception as e:
        return np.nan


def _assign_shift(minutes):
    """
    Assign shift berdasarkan jam dalam menit

    Shift:
    - Pagi: 06:00 - 11:00 (360 - 660)
    - Siang: 11:00 - 16:00 (660 - 960)
    - Sore: 16:00 - 21:00 (960 - 1260)
    - Malam: 21:00 - 06:00 (1260 - 360 next day)
    """

    if pd.isna(minutes):
        return 'Unknown'

    minutes = int(minutes)

    if 360 <= minutes < 660:
        return 'Pagi (06-11)'
    elif 660 <= minutes < 960:
        return 'Siang (11-16)'
    elif 960 <= minutes < 1260:
        return 'Sore (16-21)'
    else:
        return 'Malam (21-06)'


def get_data_summary(df):
    """
    Get summary statistics dari dataframe
    """
    summary = {
        'total_rows': len(df),
        'unique_petugas': df['kd_petugas'].nunique(),
        'unique_pelanggan': df['idpel'].nunique(),
        'date_start': df['tanggal_pembacaan'].min(),
        'date_end': df['tanggal_pembacaan'].max(),
        'total_days': (df['tanggal_pembacaan'].max() - df['tanggal_pembacaan'].min()).days + 1
    }

    return summary