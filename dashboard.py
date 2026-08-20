import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from streamlit_folium import st_folium, folium_static
from datetime import datetime
import sys
from pathlib import Path

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.data_loader import load_and_clean_data
from modules.metrics import (
    calculate_ranking,
    calculate_time_metrics,
    calculate_activity_insight,
    get_score_explanation,
    generate_operational_recommendations
)
from modules.visualizations import (
    plot_time_distribution,
    plot_heatmap_petugas_jam,
    plot_ranking_chart,
    plot_per_petugas_detail,
    plot_area_coverage,
    build_interactive_map,
    create_top_bottom_tables
)

# PAGE CONFIG
st.set_page_config(
    page_title="Dashboard PLN Garut",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# DARK MODE STYLING
st.markdown("""
<style>
    * {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
    }

    /* Dark background */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #0F1419 !important;
        color: #E8EAED !important;
    }

    [data-testid="stSidebar"] {
        background-color: #1A1F26 !important;
        border-right: 1px solid #2D333B !important;
    }

    [data-testid="stSidebar"] * {
        color: #E8EAED !important;
    }

    /* Headers */
    h1 {
        color: #58A6FF !important;
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }

    h2 {
        color: #58A6FF !important;
        font-size: 1.5rem;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #F85149 !important;
        padding-bottom: 0.5rem;
    }

    h3 {
        color: #C9D1D9 !important;
        font-size: 1.1rem;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background-color: #161B22 !important;
        border: 1px solid #30363D !important;
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.9rem;
        color: #8B949E !important;
    }

    [data-testid="stMetricValue"] {
        font-size: 2.2rem;
        color: #58A6FF !important;
        font-weight: 700;
    }

    /* Buttons */
    .stButton > button {
        background-color: #238636 !important;
        color: white !important;
        border: 1px solid #238636 !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
    }

    .stButton > button:hover {
        background-color: #2EA043 !important;
        border-color: #2EA043 !important;
    }

    /* Data tables */
    [data-testid="stDataFrame"] {
        background-color: #0F1419 !important;
        border: 1px solid #30363D !important;
        border-radius: 8px;
    }

    /* Input fields */
    [data-baseweb="select"] > div,
    [data-baseweb="input"] > div {
        background-color: #161B22 !important;
        border-color: #30363D !important;
        color: #E8EAED !important;
    }

    /* Sliders */
    [data-baseweb="slider"] {
        color: #58A6FF !important;
    }

    /* Tabs */
    [role="tab"] {
        color: #8B949E !important;
    }

    [role="tab"][aria-selected="true"] {
        color: #58A6FF !important;
        border-bottom-color: #58A6FF !important;
    }

    /* Info and tip boxes */
    .info-box {
        background-color: #0D3A66 !important;
        border-left: 4px solid #58A6FF !important;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
        color: #E8EAED !important;
    }

    .tip-box {
        background-color: #4D3800 !important;
        border-left: 4px solid #F85149 !important;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
        color: #E8EAED !important;
    }

    /* Dividers */
    hr {
        margin: 2rem 0;
        border: 0;
        border-top: 1px solid #30363D !important;
    }

    /* Text */
    p, span, label {
        color: #E8EAED !important;
    }

    /* Caption */
    .stCaption {
        color: #8B949E !important;
    }

    /* Streamlit elements */
    .stMarkdown {
        color: #E8EAED !important;
    }

    .streamlit-expanderHeader {
        background-color: #161B22 !important;
        color: #E8EAED !important;
    }

    @media (prefers-color-scheme: light) {
        html, body, [data-testid="stAppViewContainer"] {
            background-color: #0F1419 !important;
            color: #E8EAED !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# HEADER
st.markdown("""
# Dashboard Pembacaan Meter
### PLN UP3 Garut | Analisis Aktivitas & Pola Kerja Petugas Lapangan
""")

st.markdown("""
<div class="info-box">
<b>Dashboard ini membantu Anda memahami:</b>
<br>* Jam dan waktu pembacaan meter
<br>* Performa dan produktivitas setiap petugas
<br>* Jangkauan area kerja geografis
</div>
""", unsafe_allow_html=True)

# FILE UPLOADER
st.sidebar.header("Upload Data")
uploaded_file = st.sidebar.file_uploader(
    "Pilih file Excel (.xlsx)",
    type=["xlsx"],
    help="Format: GRTREKAGT26-BACA-A_*.xlsx atau format dengan kolom: KD_PETUGAS, JAM_PEMBACAAN, TANGGAL_PEMBACAAN, KOORDINAT_X, KOORDINAT_Y, IDPEL, NAMA"
)

# LOAD DATA
@st.cache_data
def load_data(file_obj):
    return load_and_clean_data(file_obj)

if uploaded_file is not None:
    try:
        df = load_data(uploaded_file)
        data_loaded = True
        st.sidebar.success(f"File loaded: {uploaded_file.name}")
    except Exception as e:
        st.error(f"Gagal membaca file: {str(e)}")
        st.info("Pastikan format Excel sesuai: kolom harus punya KD_PETUGAS, JAM_PEMBACAAN, TANGGAL_PEMBACAAN, dst")
        data_loaded = False
else:
    st.info("Upload file Excel di sidebar kiri untuk memulai dashboard")
    data_loaded = False

if data_loaded:
    # SIDEBAR - FILTERS
    with st.sidebar:
        st.header("Filter Data")

        st.markdown("---")

        # 1. PERIODE
        st.subheader("Pilih Periode")
        min_date = df['tanggal_pembacaan'].min()
        max_date = df['tanggal_pembacaan'].max()

        date_range = st.date_input(
            "Tanggal mulai hingga akhir",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            label_visibility="collapsed"
        )

        if len(date_range) == 2:
            start_date, end_date = date_range
            df_filtered = df[(df['tanggal_pembacaan'] >= pd.Timestamp(start_date)) &
                            (df['tanggal_pembacaan'] <= pd.Timestamp(end_date))]
        else:
            df_filtered = df

        st.markdown("---")

        # 2. PETUGAS
        st.subheader("Pilih Petugas")
        all_petugas = sorted(df_filtered['kd_petugas'].unique())
        selected_petugas = st.multiselect(
            "Kosongkan untuk lihat semua petugas",
            options=all_petugas,
            default=[],
            label_visibility="collapsed"
        )

        if selected_petugas:
            df_filtered = df_filtered[df_filtered['kd_petugas'].isin(selected_petugas)]

        st.markdown("---")

        # 3. SHIFT
        st.subheader("Pilih Shift")
        shifts_available = sorted(df_filtered['shift'].unique())
        selected_shifts = st.multiselect(
            "Kosongkan untuk lihat semua shift",
            options=['Pagi (06-11)', 'Siang (11-16)', 'Sore (16-21)', 'Malam (21-06)'],
            default=list(shifts_available),
            label_visibility="collapsed"
        )

        if selected_shifts:
            df_filtered = df_filtered[df_filtered['shift'].isin(selected_shifts)]

        st.markdown("---")

        # 4. RANKING WEIGHTS
        st.subheader("Ranking Weights")
        st.caption("Adjust bobot untuk ubah ranking petugas")

        weight_total = st.slider("Total Pembacaan", 0.0, 1.0, 0.35, 0.05, label_visibility="collapsed")
        weight_consistency = st.slider("Konsistensi", 0.0, 1.0, 0.30, 0.05, label_visibility="collapsed")
        weight_efficiency = st.slider("Efisiensi", 0.0, 1.0, 0.20, 0.05, label_visibility="collapsed")
        weight_speed = st.slider("Kecepatan", 0.0, 1.0, 0.15, 0.05, label_visibility="collapsed")

        # Normalize weights
        total_weight = weight_total + weight_consistency + weight_efficiency + weight_speed
        if total_weight > 0:
            weight_total /= total_weight
            weight_consistency /= total_weight
            weight_efficiency /= total_weight
            weight_speed /= total_weight

        ranking_weights = {
            'total_pembacaan': weight_total,
            'konsistensi_waktu': weight_consistency,
            'efisiensi_area': weight_efficiency,
            'kecepatan_pembacaan': weight_speed
        }

        st.markdown("---")

        # 5. EXPORT
        st.subheader("Export")
        if st.button("Download Excel", use_container_width=True):
            output_file = '/tmp/dashboard_export.xlsx'
            with pd.ExcelWriter(output_file) as writer:
                df_filtered.to_excel(writer, sheet_name='Data', index=False)

            with open(output_file, 'rb') as f:
                st.download_button(
                    label="Download Sekarang",
                    data=f.read(),
                    file_name=f"dashboard_pln_{start_date.strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

    # MAIN CONTENT
    st.markdown("## Ringkasan Data")

    col1, col2, col3, col4, col5 = st.columns(5)

    total_pembacaan = len(df_filtered)
    jumlah_petugas = df_filtered['kd_petugas'].nunique()
    jumlah_pelanggan = df_filtered['idpel'].nunique()
    rata_per_petugas = total_pembacaan / jumlah_petugas if jumlah_petugas > 0 else 0

    kpi_activity = calculate_activity_insight(df_filtered, start_hour=6, end_hour=16)
    kpi_activity_pct = kpi_activity['pct'] if kpi_activity else 0

    with col1:
        st.metric("Total Pembacaan", f"{total_pembacaan:,}")

    with col2:
        st.metric("Jumlah Petugas", jumlah_petugas)

    with col3:
        st.metric("Jumlah Pelanggan", f"{jumlah_pelanggan:,}")

    with col4:
        st.metric("Rata-rata Pembacaan/Petugas", f"{rata_per_petugas:.0f}")

    with col5:
        st.metric("Aktivitas 06:00-16:00", f"{kpi_activity_pct:.1f}%")

    # TABS

    tab1, tab2, tab3, tab4 = st.tabs([
        "Distribusi Waktu",
        "Ranking Petugas",
        "Detail Petugas",
        "Area Geografis"
    ])

    # ====== TAB 1: DISTRIBUSI WAKTU ======
    with tab1:
        st.markdown("## Kapan Meter Dibaca?")

        st.markdown("""
        <div class="tip-box">
        <b>Apa yang dilihat di sini:</b>
        <br>* Jam berapa petugas biasanya membaca meter
        <br>* Persentase pembacaan per shift (Pagi, Siang, Sore, Malam)
        <br>* Pola kerja reguler atau tidak
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Histogram Jam Pembacaan")
            fig_time = plot_time_distribution(df_filtered)
            st.plotly_chart(fig_time, use_container_width=True)

        with col2:
            st.markdown("### Persentase per Shift")
            shift_counts = df_filtered['shift'].value_counts()
            fig_pie = go.Figure(data=[go.Pie(
                labels=shift_counts.index,
                values=shift_counts.values,
                marker=dict(colors=['#58A6FF', '#79C0FF', '#F85149', '#A371F7']),
                textposition='inside',
                textinfo='label+percent'
            )])
            fig_pie.update_layout(
                height=400,
                showlegend=False,
                paper_bgcolor='#0F1419',
                plot_bgcolor='#161B22',
                font=dict(color='#E8EAED')
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown("---")

        st.markdown("### Statistik Waktu")
        time_stats = calculate_time_metrics(df_filtered)
        st.dataframe(time_stats, use_container_width=True, hide_index=True)
        st.caption(
            "Info: Pembacaan Paling Awal/Akhir adalah jam pembacaan meter "
            "yang tercatat di sistem, bukan jam mulai/selesai kerja resmi "
            "petugas (data tidak mencatat jam clock-in/clock-out)."
        )

        # Insight aktivitas 06:00-16:00 (Pagi + Siang)
        activity_insight = calculate_activity_insight(df_filtered, start_hour=6, end_hour=16)
        if activity_insight:
            st.markdown(f"""
            <div class="info-box">
            <b>Insight:</b> {activity_insight['pct']:.1f}% aktivitas pembacaan
            ({activity_insight['count']:,} dari {activity_insight['total']:,} pembacaan)
            terjadi antara pukul {activity_insight['start_hour']:02d}:00–{activity_insight['end_hour']:02d}:00
            (shift Pagi + Siang).
            </div>
            """, unsafe_allow_html=True)

    # RANKING PETUGAS
    with tab2:
        st.markdown("## Siapa Petugas Terbaik?")

        st.markdown("""
        <div class="tip-box">
        <b>Ranking berdasarkan 4 kriteria:</b>
        <br><b>Total Pembacaan</b> - Berapa banyak meter dibaca
        <br><b>Konsistensi</b> - Seberapa teratur jam kerjanya
        <br><b>Efisiensi</b> - Seberapa luas area kerjanya
        <br><b>Kecepatan</b> - Seberapa cepat bergerak antar lokasi
        </div>
        """, unsafe_allow_html=True)

        with st.expander("Bagaimana Score 0-100 dihitung?"):
            st.markdown(get_score_explanation())

        # Calculate ranking
        ranking_df = calculate_ranking(df_filtered, ranking_weights)

        # Show weights
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total", f"{ranking_weights['total_pembacaan']:.0%}")
        with col2:
            st.metric("Konsistensi", f"{ranking_weights['konsistensi_waktu']:.0%}")
        with col3:
            st.metric("Efisiensi", f"{ranking_weights['efisiensi_area']:.0%}")
        with col4:
            st.metric("Kecepatan", f"{ranking_weights['kecepatan_pembacaan']:.0%}")

        st.markdown("---")

        # Ranking chart
        st.markdown("### Ranking Score")
        fig_rank = plot_ranking_chart(ranking_df)
        fig_rank.update_layout(
            paper_bgcolor='#0F1419',
            plot_bgcolor='#161B22',
            font=dict(color='#E8EAED'),
            title_font=dict(color='#58A6FF')
        )
        st.plotly_chart(fig_rank, use_container_width=True)

        st.markdown("---")

        # Ranking table
        st.markdown("### Tabel Lengkap")
        ranking_display = ranking_df[[
            'rank', 'kd_petugas', 'total_pembacaan',
            'total_score', 'konsistensi_score', 'efisiensi_score', 'kecepatan_score',
            'ranking_score'
        ]].copy()

        ranking_display.columns = [
            'Rank', 'Petugas', 'Total', 'Score Total', 'Score Konsistensi',
            'Score Efisiensi', 'Score Kecepatan', 'Score Akhir'
        ]

        st.dataframe(ranking_display, use_container_width=True, hide_index=True)

        st.markdown("---")

        # Top 10 & Bottom 10
        st.markdown("### Top 10 & Bottom 10 Petugas")
        top10_df, bottom10_df = create_top_bottom_tables(ranking_df, n=10)

        col_top, col_bottom = st.columns(2)
        with col_top:
            st.markdown("**Top 10**")
            st.dataframe(top10_df, use_container_width=True, hide_index=True)
        with col_bottom:
            st.markdown("**Bottom 10**")
            st.dataframe(bottom10_df, use_container_width=True, hide_index=True)

        st.markdown("---")

        # Rekomendasi operasional
        st.markdown("### Rekomendasi Operasional")
        recommendations = generate_operational_recommendations(ranking_df, df_filtered)
        if recommendations:
            rec_html = "".join([f"<li>{rec}</li>" for rec in recommendations])
            st.markdown(f"""
            <div class="info-box">
            <b>Berdasarkan hasil analisis data di atas:</b>
            <ul>{rec_html}</ul>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Belum cukup data untuk menghasilkan rekomendasi.")

        st.markdown("---")

        # Heatmap
        st.markdown("### Pola Kerja Harian (Petugas x Jam)")
        fig_heat = plot_heatmap_petugas_jam(df_filtered)
        fig_heat.update_layout(
            paper_bgcolor='#0F1419',
            plot_bgcolor='#161B22',
            font=dict(color='#E8EAED'),
            title_font=dict(color='#58A6FF')
        )
        st.plotly_chart(fig_heat, use_container_width=True)

    # DETAIL PETUGAS
    with tab3:
        st.markdown("## Detail Petugas")

        st.markdown("""
        <div class="tip-box">
        <b>Pilih satu petugas untuk melihat:</b>
        <br>* Jam dan pola kerja mereka
        <br>* Konsistensi dan trend produktivitas
        <br>* Area dan jangkauan geografis
        </div>
        """, unsafe_allow_html=True)

        selected_petugas_detail = st.selectbox(
            "Pilih Petugas",
            options=sorted(df_filtered['kd_petugas'].unique())
        )

        df_petugas = df_filtered[df_filtered['kd_petugas'] == selected_petugas_detail]

        # Metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Pembacaan", len(df_petugas))

        with col2:
            st.metric("Unique Pelanggan", df_petugas['idpel'].nunique())

        with col3:
            avg_gap = df_petugas.groupby('tanggal_pembacaan')['jam_pembacaan_menit'].diff().mean()
            st.metric("Gap Waktu Rata-rata", f"{avg_gap:.0f} min")

        with col4:
            std_dev = df_petugas.groupby('tanggal_pembacaan')['jam_pembacaan_menit'].std().mean()
            st.metric("Std Dev Jam", f"{std_dev:.0f} min")

        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Distribusi Jam Kerja")
            fig_det = plot_per_petugas_detail(df_petugas)
            fig_det.update_layout(
                paper_bgcolor='#0F1419',
                plot_bgcolor='#161B22',
                font=dict(color='#E8EAED'),
                title_font=dict(color='#58A6FF')
            )
            st.plotly_chart(fig_det, use_container_width=True)

        with col2:
            st.markdown("### Pembacaan per Hari")
            daily = df_petugas.groupby('tanggal_pembacaan').size()
            fig_daily = px.bar(x=daily.index, y=daily.values, labels={'x': 'Tanggal', 'y': 'Jumlah'})
            fig_daily.update_layout(
                height=400,
                paper_bgcolor='#0F1419',
                plot_bgcolor='#161B22',
                font=dict(color='#E8EAED'),
                title_font=dict(color='#58A6FF'),
                showlegend=False
            )
            st.plotly_chart(fig_daily, use_container_width=True)

        st.markdown("---")

        st.markdown("### Time Series Pembacaan")
        fig_ts = px.scatter(
            df_petugas.sort_values('jam_pembacaan_menit'),
            x='tanggal_pembacaan',
            y='jam_pembacaan_menit',
            color='shift',
            hover_data=['nama_pelanggan']
        )
        fig_ts.update_layout(
            height=400,
            paper_bgcolor='#0F1419',
            plot_bgcolor='#161B22',
            font=dict(color='#E8EAED'),
            title_font=dict(color='#58A6FF')
        )
        st.plotly_chart(fig_ts, use_container_width=True)

    # AREA GEOGRAFIS
    with tab4:
        st.markdown("## Jangkauan Area Kerja")

        st.markdown("""
        <div class="tip-box">
        <b>Peta Interaktif:</b>
        <br>* Marker otomatis mengelompok (cluster) saat zoom out, pecah jadi titik individual saat zoom in
        <br>* Klik marker untuk lihat detail pelanggan, petugas, dan pemakaian kWh
        <br>* Warna marker menunjukkan shift pembacaan
        <br>* Toggle layer shift, ganti basemap, fullscreen, dan alat ukur jarak tersedia di kontrol peta
        </div>
        """, unsafe_allow_html=True)

        if len(df_filtered) > 8000:
            st.caption(
                f"Data terfilter berisi {len(df_filtered):,} titik. "
                "Untuk performa, peta menampilkan sampel acak 8.000 titik "
                "(marker tetap ter-cluster). Persempit filter tanggal/petugas/shift "
                "di sidebar untuk melihat seluruh titik tanpa sampling."
            )
            map_max_points = 8000
        else:
            map_max_points = None

        try:
            folium_map = build_interactive_map(df_filtered, max_points=map_max_points)
            folium_static(folium_map, width=1100, height=600)
        except Exception as e:
            st.error(
                "Peta gagal dirender. Kemungkinan penyebab: "
                "koneksi internet ke tile map (CartoDB/OpenStreetMap) dan skrip "
                "plugin diblokir firewall/proxy jaringan."
            )
            st.exception(e)

        st.markdown("---")

        st.markdown("### Statistik Area Kerja")
        area_stats = []
        for petugas in sorted(df_filtered['kd_petugas'].unique()):
            df_p = df_filtered[df_filtered['kd_petugas'] == petugas]

            if len(df_p) > 0:
                x_min, x_max = df_p['koordinat_x'].min(), df_p['koordinat_x'].max()
                y_min, y_max = df_p['koordinat_y'].min(), df_p['koordinat_y'].max()
                area_range = ((x_max - x_min) ** 2 + (y_max - y_min) ** 2) ** 0.5

                area_stats.append({
                    'Petugas': petugas,
                    'Total Lokasi': len(df_p),
                    'X Range': f"{x_min:.2f} - {x_max:.2f}",
                    'Y Range': f"{y_min:.2f} - {y_max:.2f}",
                    'Area': f"{area_range:.4f}"
                })

        area_df = pd.DataFrame(area_stats)
        st.dataframe(area_df, use_container_width=True, hide_index=True)

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #8B949E; padding: 2rem;'>
    <p><b>Dashboard Pembacaan Meter - PLN UP3 Garut</b></p>
    <p style='font-size: 0.9rem;'>Dibuat untuk monitoring aktivitas pembacaan meter lapangan</p>
    </div>
    """, unsafe_allow_html=True)