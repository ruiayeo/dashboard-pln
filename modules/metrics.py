import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

def calculate_ranking(df, weights):
    """
    Calculate ranking petugas berdasarkan multiple metrics

    Parameters:
    -----------
    df : pd.DataFrame
        Dataframe dengan data pembacaan
    weights : dict
        Dictionary berisi bobot untuk setiap metric:
        - 'total_pembacaan': 0.35
        - 'konsistensi_waktu': 0.30
        - 'efisiensi_area': 0.20
        - 'kecepatan_pembacaan': 0.15

    Returns:
    --------
    pd.DataFrame
        Dataframe ranking dengan score dan rank
    """

    if len(df) == 0:
        return pd.DataFrame()

    # Initialize result
    petugas_list = sorted(df['kd_petugas'].unique())
    ranking_data = []

    for petugas in petugas_list:
        df_p = df[df['kd_petugas'] == petugas]

        # 1. Total Pembacaan Score
        total_pembacaan = len(df_p)
        total_score = (total_pembacaan / len(df)) * 100 # Normalize to 0-100
        total_score = min(total_score * 1.5, 100) # Boost untuk relevance

        # 2. Konsistensi Waktu Score
        consistency_score = _calculate_consistency_score(df_p)

        # 3. Efisiensi Area Score
        efficiency_score = _calculate_efficiency_score(df_p)

        # 4. Kecepatan Pembacaan Score
        speed_score = _calculate_speed_score(df_p)

        # Calculate weighted ranking score
        ranking_score = (
            weights['total_pembacaan'] * total_score +
            weights['konsistensi_waktu'] * consistency_score +
            weights['efisiensi_area'] * efficiency_score +
            weights['kecepatan_pembacaan'] * speed_score
        )

        ranking_data.append({
            'kd_petugas': petugas,
            'total_pembacaan': total_pembacaan,
            'total_score': round(total_score, 2),
            'konsistensi_score': round(consistency_score, 2),
            'efisiensi_score': round(efficiency_score, 2),
            'kecepatan_score': round(speed_score, 2),
            'ranking_score': round(ranking_score, 2)
        })

    # Create dataframe dan sort by ranking score descending
    ranking_df = pd.DataFrame(ranking_data)
    ranking_df = ranking_df.sort_values('ranking_score', ascending=False).reset_index(drop=True)
    ranking_df['rank'] = range(1, len(ranking_df) + 1)

    # Reorder columns
    ranking_df = ranking_df[[
        'rank', 'kd_petugas', 'total_pembacaan', 'total_score',
        'konsistensi_score', 'efisiensi_score', 'kecepatan_score', 'ranking_score'
    ]]

    return ranking_df


def _calculate_consistency_score(df_petugas):
    """
    Calculate consistency score based on working hour patterns

    Score tinggi = jam kerja konsisten (tidak terlalu beragam)
    Menggunakan coefficient of variation (std dev / mean)
    """

    if len(df_petugas) < 2:
        return 50.0

    # Get unique dates dan jam per date
    daily_hours = df_petugas.groupby('tanggal_pembacaan')['jam_pembacaan_menit'].agg([
        'min', 'max', 'mean', 'std', 'count'
    ])

    # Calculate coefficient of variation
    mean_start = daily_hours['min'].mean()
    std_start = daily_hours['min'].std()

    if mean_start > 0:
        cv = std_start / mean_start
        # Convert CV to score (inverse: low CV = high score)
        consistency = max(0, 100 - (cv * 50)) # Normalization
    else:
        consistency = 50.0

    return min(consistency, 100)


def _calculate_efficiency_score(df_petugas):
    """
    Calculate efficiency score based on geographic coverage

    Score tinggi = coverage area lebih luas / pelanggan lebih tersebar
    Menggunakan range koordinat dan concentration
    """

    if len(df_petugas) < 2:
        return 50.0

    # Calculate geographic spread
    x_range = df_petugas['koordinat_x'].max() - df_petugas['koordinat_x'].min()
    y_range = df_petugas['koordinat_y'].max() - df_petugas['koordinat_y'].min()

    # Calculate area (sqrt of product)
    area = (x_range * y_range) ** 0.5

    # Normalize to 0-100 (assuming reasonable max area)
    efficiency = min((area / 0.05) * 100, 100)

    # Bonus untuk diversity pelanggan
    unique_pelanggan = df_petugas['idpel'].nunique()
    pelanggan_bonus = (unique_pelanggan / len(df_petugas)) * 20 # Max 20 bonus points

    efficiency = min(efficiency + pelanggan_bonus, 100)

    return efficiency


def _calculate_speed_score(df_petugas):
    """
    Calculate speed score based on reading intervals

    Score tinggi = pembacaan lebih cepat / gap antar pembacaan lebih kecil
    """

    if len(df_petugas) < 2:
        return 50.0

    # Calculate time gaps within same day
    daily_gaps = []

    for date in df_petugas['tanggal_pembacaan'].unique():
        df_day = df_petugas[df_petugas['tanggal_pembacaan'] == date].sort_values('jam_pembacaan_menit')

        if len(df_day) > 1:
            gaps = df_day['jam_pembacaan_menit'].diff().dropna()
            daily_gaps.extend(gaps.tolist())

    if not daily_gaps:
        return 50.0

    # Average gap (in minutes)
    avg_gap = np.mean(daily_gaps)

    # Convert to score: lower gap = higher score
    # Assuming optimal gap is around 10-15 minutes
    if avg_gap < 5:
        speed = 100 # Very fast
    elif avg_gap < 10:
        speed = 95
    elif avg_gap < 15:
        speed = 85
    elif avg_gap < 20:
        speed = 75
    elif avg_gap < 30:
        speed = 60
    else:
        speed = max(0, 100 - (avg_gap - 30) / 10)

    return min(speed, 100)


def _format_duration(total_minutes):
    """
    Format durasi dalam menit ke 'X jam Y menit'
    """
    total_minutes = int(round(total_minutes))
    hours, minutes = divmod(total_minutes, 60)
    return f"{hours} jam {minutes} menit"


def calculate_time_metrics(df):
    """
    Calculate time-based metrics.

    NOTE: df yang masuk ke fungsi ini diasumsikan sudah difilter hanya
    pembacaan aktual (lihat modules/data_loader.py langkah 10b), jadi
    'paling awal' / 'paling akhir' di sini adalah jam pembacaan meter
    sungguhan, BUKAN jam mulai/selesai kerja petugas secara resmi
    (data tidak mencatat jam clock-in/clock-out petugas).

    Returns:
    --------
    pd.DataFrame
        Overall time statistics and shift distribution.
    """

    if len(df) == 0:
        return pd.DataFrame()

    metrics = []

    # Overall statistics

    # Ambil nilai waktu dalam menit
    min_minutes = int(df['jam_pembacaan_menit'].min())
    max_minutes = int(df['jam_pembacaan_menit'].max())
    avg_minutes = round(df['jam_pembacaan_menit'].mean())

    # Konversi menit ke HH:MM
    min_hours, min_mins = divmod(min_minutes, 60)
    max_hours, max_mins = divmod(max_minutes, 60)
    avg_hours, avg_mins = divmod(avg_minutes, 60)

    # Pembacaan paling awal (BUKAN "jam mulai kerja" - data tidak
    # mencatat jam clock-in petugas, hanya jam pembacaan meter)
    metrics.append({
        'Metrik': 'Pembacaan Paling Awal',
        'Nilai': f"{min_hours:02d}:{min_mins:02d}"
    })

    # Pembacaan paling akhir
    metrics.append({
        'Metrik': 'Pembacaan Paling Akhir',
        'Nilai': f"{max_hours:02d}:{max_mins:02d}"
    })

    # Jam rata-rata
    metrics.append({
        'Metrik': 'Jam Rata-rata',
        'Nilai': f"{avg_hours:02d}:{avg_mins:02d}"
    })

    # Standar deviasi
    std_minutes = df['jam_pembacaan_menit'].std()

    metrics.append({
        'Metrik': 'Std Dev Jam Pembacaan (menit)',
        'Nilai': f"{std_minutes:.1f}"
    })

    # Rentang waktu pembacaan (ganti dari "Durasi Kerja" dalam menit
    # mentah menjadi format jam+menit yang mudah dibaca)
    duration_minutes = (
        df['jam_pembacaan_menit'].max()
        - df['jam_pembacaan_menit'].min()
    )

    metrics.append({
        'Metrik': 'Rentang Waktu Pembacaan',
        'Nilai': _format_duration(duration_minutes)
    })

    # Per shift

    shifts = [
        'Pagi (06-11)',
        'Siang (11-16)',
        'Sore (16-21)',
        'Malam (21-06)'
    ]

    for shift in shifts:

        count = len(df[df['shift'] == shift])

        pct = (
            count / len(df) * 100
            if len(df) > 0
            else 0
        )

        metrics.append({
            'Metrik': f'Pembacaan {shift}',
            'Nilai': f"{count} ({pct:.1f}%)"
        })

    return pd.DataFrame(metrics)


def calculate_activity_insight(df, start_hour=6, end_hour=16):
    """
    Hitung persentase aktivitas pembacaan yang terjadi dalam rentang jam
    tertentu (default 06:00-16:00, yaitu gabungan shift Pagi + Siang).

    Returns:
    --------
    dict dengan keys: 'pct', 'count', 'total', 'start_hour', 'end_hour'
    atau None kalau df kosong.
    """

    if len(df) == 0:
        return None

    start_minutes = start_hour * 60
    end_minutes = end_hour * 60

    in_range = df[
        (df['jam_pembacaan_menit'] >= start_minutes) &
        (df['jam_pembacaan_menit'] < end_minutes)
    ]

    pct = len(in_range) / len(df) * 100

    return {
        'pct': pct,
        'count': len(in_range),
        'total': len(df),
        'start_hour': start_hour,
        'end_hour': end_hour
    }


def get_score_explanation():
    """
    Penjelasan naratif bagaimana Ranking Score (0-100) dihitung,
    untuk ditampilkan di dashboard (mis. dalam expander).
    """

    return """
**Ranking Score** adalah rata-rata tertimbang (weighted average) dari 4 komponen, masing-masing sudah dinormalisasi ke skala 0–100. Bobot tiap komponen bisa diubah di sidebar (**Ranking Weights**).

| Komponen | Yang diukur | Cara hitung (ringkas) |
|---|---|---|
| **Total Score** | Seberapa banyak meter dibaca petugas ini dibanding total semua petugas | `(pembacaan petugas ÷ total pembacaan) × 100 × 1.5`, dibatasi maksimum 100 |
| **Konsistensi Score** | Seberapa teratur jam pembacaan pertama petugas dari hari ke hari | `100 − (std jam pertama ÷ rata-rata jam pertama) × 50`. Makin kecil variasinya, makin tinggi skornya |
| **Efisiensi Score** | Seberapa luas area geografis yang dijangkau + keragaman pelanggan yang dilayani | Luas area (dari rentang koordinat) dinormalisasi ke 0–100, ditambah bonus keragaman pelanggan (maksimum +20) |
| **Kecepatan Score** | Rata-rata jeda waktu antar pembacaan dalam hari yang sama | Jeda ≤5 menit 100, jeda 30+ menit skornya menurun bertahap |

**Formula akhir:**

`Ranking Score = (bobot Total × Total Score) + (bobot Konsistensi × Konsistensi Score) + (bobot Efisiensi × Efisiensi Score) + (bobot Kecepatan × Kecepatan Score)`

Skor ini murni berdasarkan pola data pembacaan (kuantitas, keteraturan, cakupan area, kecepatan) — bukan penilaian kualitas kerja petugas secara langsung, karena tidak semua faktor lapangan (medan sulit, gangguan pelanggan, dll) tercatat dalam data.
"""


def generate_operational_recommendations(ranking_df, df):
    """
    Menghasilkan rekomendasi operasional berdasarkan hasil analisis data
    (bukan teks template statis - semua angka dihitung langsung dari
    ranking_df dan df yang diberikan).

    Returns:
    --------
    list of str
    """

    if len(ranking_df) == 0 or len(df) == 0:
        return []

    recommendations = []

    # 1. Petugas dengan ranking score terendah
    n_bottom = min(5, len(ranking_df))
    bottom_score = ranking_df.nsmallest(n_bottom, 'ranking_score')['kd_petugas'].tolist()
    recommendations.append(
        f"Petugas dengan ranking score terendah ({', '.join(bottom_score)}) "
        "disarankan mendapat pendampingan atau evaluasi lanjutan untuk "
        "memahami penyebab rendahnya skor, baik dari sisi konsistensi jadwal, "
        "cakupan area, maupun kecepatan pembacaan."
    )

    # 2. Konsistensi jadwal rendah
    n_consistency = min(5, len(ranking_df))
    low_consistency = ranking_df.nsmallest(n_consistency, 'konsistensi_score')['kd_petugas'].tolist()
    recommendations.append(
        f"Petugas dengan konsistensi jadwal terendah ({', '.join(low_consistency)}) "
        "menunjukkan variasi jam pembacaan yang cukup tinggi dari hari ke hari. "
        "Supervisi jadwal kerja dapat membantu menstabilkan pola kerja mereka."
    )

    # 3. Konsentrasi aktivitas pada jam tertentu
    activity = calculate_activity_insight(df, start_hour=6, end_hour=16)
    if activity and activity['pct'] > 90:
        recommendations.append(
            f"Sebanyak {activity['pct']:.1f}% pembacaan terkonsentrasi pada pukul "
            f"{activity['start_hour']:02d}:00-{activity['end_hour']:02d}:00. "
            "Penjadwalan sumber daya (jumlah petugas aktif, jam operasional "
            "layanan pendukung) sebaiknya disesuaikan dengan pola beban kerja ini."
        )

    # 4. Efisiensi area rendah
    n_efficiency = min(5, len(ranking_df))
    low_efficiency = ranking_df.nsmallest(n_efficiency, 'efisiensi_score')['kd_petugas'].tolist()
    recommendations.append(
        f"Petugas dengan skor efisiensi area terendah ({', '.join(low_efficiency)}) "
        "memiliki cakupan area geografis yang relatif sempit. Perlu dicek apakah "
        "ini disebabkan oleh area kerja yang memang padat (urban) atau ada potensi "
        "rute yang bisa dioptimalkan."
    )

    return recommendations


def calculate_efficiency_metrics(df):
    """
    Calculate efficiency metrics untuk setiap petugas.

    Returns:
    --------
    pd.DataFrame
        Detailed efficiency metrics.
    """

    if len(df) == 0:
        return pd.DataFrame()

    petugas_metrics = []

    # Per petugas
    for petugas in sorted(df['kd_petugas'].dropna().unique()):

        df_p = df[df['kd_petugas'] == petugas]

        # Basic metrics
        total = len(df_p)

        unique_customers = df_p['idpel'].nunique()

        unique_days = df_p['tanggal_pembacaan'].nunique()

        # Average reading per day
        per_day = (
            total / unique_days
            if unique_days > 0
            else 0
        )

        # Time range
        min_minutes = int(
            df_p['jam_pembacaan_menit'].min()
        )

        max_minutes = int(
            df_p['jam_pembacaan_menit'].max()
        )

        min_hour = min_minutes // 60
        max_hour = max_minutes // 60

        # Geographic range

        x_range = (
            df_p['koordinat_x'].max()
            - df_p['koordinat_x'].min()
        )

        y_range = (
            df_p['koordinat_y'].max()
            - df_p['koordinat_y'].min()
        )

        # Store metrics

        petugas_metrics.append({
            'Petugas': petugas,

            'Total Pembacaan': total,

            'Unique Pelanggan': unique_customers,

            'Hari Kerja': unique_days,

            'Per Hari': f"{per_day:.1f}",

            'Jam Awal': f"{min_hour:02d}:00",

            'Jam Akhir': f"{max_hour:02d}:00",

            'X Range': f"{x_range:.4f}",

            'Y Range': f"{y_range:.4f}"
        })

    return pd.DataFrame(petugas_metrics)