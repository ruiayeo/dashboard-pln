import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import folium
from folium.plugins import MarkerCluster, Fullscreen, MiniMap, MeasureControl

# Dark Mode Colors - GitHub Dark Inspired
COLORS_DARK = ['#58A6FF', '#79C0FF', '#79C0FF', '#A371F7', '#D2A8FF']
SHIFT_COLORS_DARK = {
    'Pagi (06-11)': '#58A6FF', # Blue
    'Siang (11-16)': '#79C0FF', # Light Blue
    'Sore (16-21)': '#F85149', # Red/Orange
    'Malam (21-06)': '#A371F7' # Purple
}

# Dark Mode Layout Config
DARK_LAYOUT = dict(
    template='plotly_dark',
    paper_bgcolor='#0F1419',
    plot_bgcolor='#161B22',
    font=dict(family='Arial, sans-serif', color='#E8EAED', size=12),
    title_font=dict(color='#58A6FF', size=14),
    margin=dict(l=50, r=30, t=50, b=50),
    hovermode='closest'
)


def plot_time_distribution(df):
    """
    Histogram distribusi jam pembacaan - Dark Mode
    Menampilkan garis vertikal jam rata-rata pembacaan.
    """

    if len(df) == 0:
        return go.Figure().add_annotation(text="Tidak ada data")

    fig = go.Figure()

    for shift in ['Pagi (06-11)', 'Siang (11-16)', 'Sore (16-21)', 'Malam (21-06)']:
        df_shift = df[df['shift'] == shift]
        if len(df_shift) > 0:
            fig.add_trace(go.Histogram(
                x=df_shift['jam_pembacaan_menit'],
                name=shift,
                marker_color=SHIFT_COLORS_DARK.get(shift, '#58A6FF'),
                nbinsx=20,
                opacity=0.8,
                hovertemplate='<b>%{fullData.name}</b><br>Jam: %{x}<br>Jumlah: %{y}<extra></extra>'
            ))

    fig.update_layout(
        title="Distribusi Pembacaan Meter per Jam",
        xaxis_title="Jam (menit dari pukul 00:00)",
        yaxis_title="Jumlah Pembacaan",
        barmode='overlay',
        height=400,
        **DARK_LAYOUT
    )

    fig.update_xaxes(
        tickformat='d',
        ticktext=[f"{h:02d}:00" for h in range(0, 24, 2)],
        tickvals=list(range(0, 24*60, 2*60))
    )

    # Garis rata-rata jam pembacaan
    avg_minutes = df['jam_pembacaan_menit'].mean()
    avg_hour, avg_min = divmod(int(round(avg_minutes)), 60)

    fig.add_vline(
        x=avg_minutes,
        line_width=2,
        line_dash='dash',
        line_color='#FFD33D',
        annotation_text=f"Rata-rata {avg_hour:02d}:{avg_min:02d}",
        annotation_position="top",
        annotation_font=dict(color='#FFD33D', size=12)
    )

    return fig


def plot_heatmap_petugas_jam(df):
    """
    Heatmap petugas × jam - Dark Mode
    """

    if len(df) == 0:
        return go.Figure().add_annotation(text="Tidak ada data")

    df_copy = df.copy()
    df_copy['hour'] = df_copy['jam_pembacaan_menit'] // 60

    pivot = pd.crosstab(df_copy['kd_petugas'], df_copy['hour'])
    pivot = pivot.reindex(columns=range(24), fill_value=0)

    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=[f"{h:02d}:00" for h in range(24)],
        y=pivot.index,
        colorscale=[
            [0, '#161B22'],
            [0.3, '#0D3A66'],
            [0.7, '#58A6FF'],
            [1, '#79C0FF']
        ],
        colorbar=dict(title="Jumlah<br>Pembacaan", thickness=20, len=0.7),
        hovertemplate='<b>Petugas: %{y}</b><br>Jam: %{x}<br>Total: %{z}<extra></extra>'
    ))

    fig.update_layout(
        title="Pola Kerja Petugas (Siapa Bekerja Jam Berapa)",
        xaxis_title="Jam Kerja",
        yaxis_title="Kode Petugas",
        height=max(350, len(pivot) * 18),
        **DARK_LAYOUT
    )

    return fig


def plot_ranking_chart(ranking_df):
    """
    Bar chart ranking petugas - Dark Mode
    Diperbaiki supaya tetap terbaca dengan jumlah petugas besar (mis. 61):
    - Tinggi chart menyesuaikan jumlah petugas (lebih longgar per baris)
    - Label skor ditaruh di luar bar (textposition='outside') supaya tidak
      tertimpa/tenggelam di dalam bar yang pendek
    - Margin kiri diperbesar supaya kode petugas tidak terpotong
    - Font label disesuaikan (lebih kecil) supaya tidak saling tumpuk
    - Legend warna threshold ditambahkan sebagai anotasi
    """

    if len(ranking_df) == 0:
        return go.Figure().add_annotation(text="Tidak ada data")

    ranking_sorted = ranking_df.sort_values('ranking_score', ascending=True)
    n = len(ranking_sorted)

    fig = go.Figure()

    # Color berdasarkan score
    colors = []
    for score in ranking_sorted['ranking_score']:
        if score >= 80:
            colors.append('#58A6FF') # Top - Light Blue
        elif score >= 60:
            colors.append('#79C0FF') # Good - Lighter Blue
        elif score >= 40:
            colors.append('#F85149') # Average - Red
        else:
            colors.append('#DA3633') # Needs - Dark Red

    fig.add_trace(go.Bar(
        y=ranking_sorted['kd_petugas'],
        x=ranking_sorted['ranking_score'],
        orientation='h',
        marker_color=colors,
        text=ranking_sorted['ranking_score'].round(1),
        textposition='outside',
        textfont=dict(size=10, color='#E8EAED'),
        hovertemplate='<b>%{y}</b><br>Score: %{x:.1f}<extra></extra>'
    ))

    # Tinggi menyesuaikan jumlah petugas, dengan jarak antar baris cukup
    # supaya label kode petugas (sumbu Y) tetap terbaca untuk n besar
    chart_height = max(450, n * 26)

    fig.update_layout(
        title=f"Ranking {n} Petugas (Score 0-100)",
        xaxis_title="Score",
        yaxis_title="",
        height=chart_height,
        **DARK_LAYOUT
    )
    fig.update_layout(margin=dict(l=150, r=90, t=70, b=50))

    fig.update_xaxes(range=[0, 112])
    fig.update_yaxes(tickfont=dict(size=10))

    # Legend manual untuk threshold warna (di pojok kanan atas area plot)
    legend_items = [
        ("≥ 80 Top", '#58A6FF'),
        ("60–79 Good", '#79C0FF'),
        ("40–59 Average", '#F85149'),
        ("< 40 Perlu Perhatian", '#DA3633'),
    ]
    for i, (label, color) in enumerate(legend_items):
        fig.add_annotation(
            x=1.0, y=1.0 - (i * 0.035),
            xref='paper', yref='paper',
            xanchor='left', yanchor='top',
            showarrow=False,
            text=f"<span style='color:{color}'>■</span> {label}",
            font=dict(size=10, color='#E8EAED'),
            align='left'
        )

    return fig


def create_top_bottom_tables(ranking_df, n=10):
    """
    Ambil Top-N dan Bottom-N petugas berdasarkan ranking_score.

    Returns:
    --------
    (top_df, bottom_df) : tuple of pd.DataFrame
    """

    if len(ranking_df) == 0:
        return pd.DataFrame(), pd.DataFrame()

    cols = [
        'rank', 'kd_petugas', 'total_pembacaan',
        'total_score', 'konsistensi_score', 'efisiensi_score',
        'kecepatan_score', 'ranking_score'
    ]
    col_labels = [
        'Rank', 'Petugas', 'Total Meter',
        'Score Total', 'Score Konsistensi', 'Score Efisiensi',
        'Score Kecepatan', 'Score Akhir'
    ]

    sorted_df = ranking_df.sort_values('ranking_score', ascending=False).reset_index(drop=True)

    top_df = sorted_df.head(n)[cols].copy()
    top_df.columns = col_labels

    bottom_df = sorted_df.tail(n).sort_values('ranking_score', ascending=True)[cols].copy()
    bottom_df.columns = col_labels

    return top_df, bottom_df


def plot_per_petugas_detail(df_petugas):
    """
    Histogram detail per petugas - Dark Mode
    """

    if len(df_petugas) == 0:
        return go.Figure().add_annotation(text="Tidak ada data")

    fig = go.Figure()

    for shift in ['Pagi (06-11)', 'Siang (11-16)', 'Sore (16-21)', 'Malam (21-06)']:
        df_shift = df_petugas[df_petugas['shift'] == shift]
        if len(df_shift) > 0:
            fig.add_trace(go.Histogram(
                x=df_shift['jam_pembacaan_menit'],
                name=shift,
                marker_color=SHIFT_COLORS_DARK.get(shift, '#58A6FF'),
                nbinsx=15,
                opacity=0.8,
                hovertemplate='<b>%{fullData.name}</b><br>Jumlah: %{y}<extra></extra>'
            ))

    fig.update_layout(
        title="Pola Jam Kerja Petugas",
        xaxis_title="Jam",
        yaxis_title="Jumlah",
        barmode='overlay',
        height=350,
        **DARK_LAYOUT
    )

    return fig


def plot_area_coverage(df):
    """
    Peta geografis area kerja petugas menggunakan tile OpenStreetMap
    (via Plotly scatter_mapbox, tidak perlu API key/token).

    CATATAN KOORDINAT: berdasarkan pengecekan data, kolom 'koordinat_x'
    sebenarnya berisi LATITUDE (lintang, rentang -7.1 s/d -7.4 untuk
    area Garut) dan 'koordinat_y' berisi LONGITUDE (bujur, rentang
    107.5 s/d 108.0). Ini kebalik dari penamaan kolomnya, jadi
    di-mapping eksplisit di sini: lat=koordinat_x, lon=koordinat_y.
    """

    if len(df) == 0 or 'koordinat_x' not in df.columns:
        return go.Figure().add_annotation(text="Tidak ada data geografis")

    df_map = df.copy()
    df_map['lat'] = df_map['koordinat_x']
    df_map['lon'] = df_map['koordinat_y']

    center_lat = df_map['lat'].mean()
    center_lon = df_map['lon'].mean()

    n_petugas = df_map['kd_petugas'].nunique()

    # Palet warna diperluas supaya cukup untuk banyak petugas (bisa
    # sampai puluhan) tanpa warna berulang terlalu cepat
    color_palette = (
        px.colors.qualitative.Alphabet
        + px.colors.qualitative.Light24
        + px.colors.qualitative.Dark24
    )

    fig = px.scatter_mapbox(
        df_map,
        lat='lat',
        lon='lon',
        color='kd_petugas',
        size='pemkwh',
        size_max=16,
        hover_name='nama_pelanggan',
        hover_data={
            'kd_petugas': True,
            'pemkwh': ':.0f',
            'lat': ':.5f',
            'lon': ':.5f'
        },
        zoom=11,
        center={'lat': center_lat, 'lon': center_lon},
        title=f"Peta Area Kerja {n_petugas} Petugas",
        labels={
            'lat': 'Lintang',
            'lon': 'Bujur',
            'kd_petugas': 'Petugas',
            'pemkwh': 'kWh'
        },
        color_discrete_sequence=color_palette
    )

    fig.update_layout(
        mapbox_style='open-street-map',
        height=600,
        margin=dict(l=0, r=0, t=50, b=0),
        paper_bgcolor='#0F1419',
        font=dict(family='Arial, sans-serif', color='#E8EAED', size=12),
        title_font=dict(color='#58A6FF', size=14),
        legend=dict(
            bgcolor='rgba(15,20,25,0.85)',
            bordercolor='#30363D',
            borderwidth=1,
            font=dict(size=9),
            itemsizing='constant'
        )
    )

    fig.update_traces(
        hovertemplate='<b>%{hovertext}</b><br>Petugas: %{customdata[0]}<br>Koordinat: (%{customdata[2]}, %{customdata[3]})<br>kWh: %{customdata[1]}<extra></extra>'
    )

    return fig


def build_interactive_map(df, max_points=None):
    """
    Peta interaktif berbasis Folium/Leaflet - jauh lebih kaya fitur
    dibanding scatter mapbox biasa:

    - Marker DI-CLUSTER otomatis (MarkerCluster) sehingga tetap ringan
      walau ribuan titik, dan cluster pecah jadi marker individual saat
      di-zoom in
    - Klik marker untuk lihat popup detail (IDPEL, nama, petugas, jam
      pembacaan, shift, kWh)
    - Warna marker per SHIFT (mudah dibedakan visual), kode petugas
      tetap muncul di popup
    - Toggle layer per shift (bisa sembunyikan/tampilkan shift tertentu
      lewat kontrol layer di kanan atas)
    - Bisa ganti basemap: OpenStreetMap / CartoDB Dark / CartoDB Light
    - Tombol Fullscreen
    - MiniMap kecil di pojok untuk konteks lokasi saat zoom in jauh
    - Alat ukur jarak (MeasureControl)
    - Legend warna shift

    CATATAN KOORDINAT: 'koordinat_x' = latitude, 'koordinat_y' = longitude
    (lihat catatan di plot_area_coverage).

    Parameters:
    -----------
    df : pd.DataFrame
    max_points : int, optional
        Batasi jumlah titik yang dirender (sampling acak) untuk menjaga
        performa browser kalau data sangat besar. None = tampilkan semua.

    Returns:
    --------
    folium.Map
    """

    if len(df) == 0 or 'koordinat_x' not in df.columns:
        # Peta kosong dengan pesan
        m = folium.Map(location=[-7.22, 107.90], zoom_start=10, tiles='OpenStreetMap')
        folium.Marker(
            [-7.22, 107.90],
            popup="Tidak ada data geografis untuk filter saat ini"
        ).add_to(m)
        return m

    df_map = df.copy()
    df_map['lat'] = df_map['koordinat_x']
    df_map['lon'] = df_map['koordinat_y']

    if max_points is not None and len(df_map) > max_points:
        df_map = df_map.sample(max_points, random_state=42)

    center_lat = df_map['lat'].mean()
    center_lon = df_map['lon'].mean()

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=12,
        tiles='OpenStreetMap',
        control_scale=True
    )

    # Basemap alternatif (bisa ditukar via layer control kanan atas).
    # OpenStreetMap dipakai sebagai basemap default/awal (bukan CartoDB)
    # karena tile OSM paling jarang diblokir firewall/proxy jaringan kantor.
    folium.TileLayer(
        'CartoDB dark_matter',
        name='Dark Mode',
        control=True
    ).add_to(m)
    folium.TileLayer(
        'CartoDB positron',
        name='Terang (Light)',
        control=True
    ).add_to(m)

    shift_colors = {
        'Pagi (06-11)': '#58A6FF',
        'Siang (11-16)': '#F0C040',
        'Sore (16-21)': '#F85149',
        'Malam (21-06)': '#A371F7'
    }

    # Satu FeatureGroup + MarkerCluster per shift supaya bisa
    # ditoggle nyala/mati sendiri-sendiri dari layer control
    for shift_name, color in shift_colors.items():
        df_shift = df_map[df_map['shift'] == shift_name]
        if len(df_shift) == 0:
            continue

        fg = folium.FeatureGroup(name=f"{shift_name} ({len(df_shift)})", show=True)
        cluster = MarkerCluster(
            options={'maxClusterRadius': 45},
            disableClusteringAtZoom=17
        )

        for _, row in df_shift.iterrows():
            popup_html = f"""
            <div style="font-family: Arial; font-size: 12px; min-width: 200px;">
                <b>{row.get('nama_pelanggan', '-')}</b><br>
                IDPEL: {row.get('idpel', '-')}<br>
                Petugas (KODE_RBM): <b>{row.get('kd_petugas', '-')}</b><br>
                Jam Pembacaan: {row.get('jam_pembacaan', '-')}<br>
                Shift: {shift_name}<br>
                Pemakaian: {row.get('pemkwh', 0):.0f} kWh
            </div>
            """
            folium.CircleMarker(
                location=[row['lat'], row['lon']],
                radius=6,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.85,
                weight=1,
                popup=folium.Popup(popup_html, max_width=280),
                tooltip=f"{row.get('kd_petugas', '-')} - {row.get('nama_pelanggan', '-')}"
            ).add_to(cluster)

        cluster.add_to(fg)
        fg.add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)
    Fullscreen(position='topleft').add_to(m)
    MiniMap(toggle_display=True, position='bottomleft').add_to(m)
    MeasureControl(position='bottomright', primary_length_unit='meters').add_to(m)

    # Legend manual (folium tidak punya legend bawaan)
    legend_items_html = "".join([
        f'<div style="margin-bottom:4px;">'
        f'<span style="display:inline-block;width:12px;height:12px;'
        f'background:{color};border-radius:50%;margin-right:6px;"></span>'
        f'{shift_name}</div>'
        for shift_name, color in shift_colors.items()
    ])
    legend_html = f"""
    <div style="
        position: fixed;
        bottom: 30px; left: 60px; z-index: 9999;
        background: rgba(15,20,25,0.9);
        color: #E8EAED;
        padding: 10px 14px;
        border-radius: 8px;
        border: 1px solid #30363D;
        font-family: Arial; font-size: 12px;
    ">
        <b>Shift Pembacaan</b><br><br>
        {legend_items_html}
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    return m


def plot_efficiency_comparison(ranking_df):
    """
    Radar chart - Dark Mode
    """

    if len(ranking_df) < 2:
        return go.Figure().add_annotation(text="Perlu minimal 2 petugas")

    top_5 = ranking_df.head(5)

    fig = go.Figure()

    categories = ['Total', 'Konsistensi', 'Efisiensi', 'Kecepatan', 'Ranking Score']

    for idx, row in top_5.iterrows():
        fig.add_trace(go.Scatterpolar(
            r=[
                row['total_score'],
                row['konsistensi_score'],
                row['efisiensi_score'],
                row['kecepatan_score'],
                row['ranking_score']
            ],
            theta=categories,
            fill='toself',
            name=f"#{row['rank']} {row['kd_petugas']}",
            opacity=0.7
        ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        title="Perbandingan Top 5 Petugas",
        height=500,
        **DARK_LAYOUT
    )

    return fig


def plot_daily_trend(df):
    """
    Line chart trend - Dark Mode
    """

    if len(df) == 0:
        return go.Figure().add_annotation(text="Tidak ada data")

    daily_count = df.groupby('tanggal_pembacaan').size()

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=daily_count.index,
        y=daily_count.values,
        mode='lines+markers',
        name='Pembacaan',
        line=dict(color='#58A6FF', width=2),
        marker=dict(size=6),
        hovertemplate='<b>%{x|%d %B %Y}</b><br>Total: %{y}<extra></extra>'
    ))

    if len(daily_count) > 2:
        z = np.polyfit(range(len(daily_count)), daily_count.values, 1)
        p = np.poly1d(z)

        fig.add_trace(go.Scatter(
            x=daily_count.index,
            y=p(range(len(daily_count))),
            mode='lines',
            name='Trend',
            line=dict(color='#F85149', width=2, dash='dash')
        ))

    fig.update_layout(
        title="Trend Pembacaan Harian",
        xaxis_title="Tanggal",
        yaxis_title="Jumlah Pembacaan",
        height=350,
        **DARK_LAYOUT
    )

    return fig


def plot_shift_distribution(df):
    """
    Pie chart distribusi shift - Dark Mode
    """

    if len(df) == 0:
        return go.Figure().add_annotation(text="Tidak ada data")

    shift_counts = df['shift'].value_counts()

    fig = go.Figure(data=[go.Pie(
        labels=shift_counts.index,
        values=shift_counts.values,
        marker=dict(
            colors=[SHIFT_COLORS_DARK.get(s, '#58A6FF') for s in shift_counts.index],
            line=dict(color='#0F1419', width=2)
        ),
        textposition='inside',
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>Pembacaan: %{value}<br>Persen: %{percent}<extra></extra>'
    )])

    fig.update_layout(
        title="Distribusi Pembacaan per Shift",
        height=350,
        **DARK_LAYOUT
    )

    return fig


def create_summary_table(ranking_df):
    """
    Summary table untuk export
    """

    if len(ranking_df) == 0:
        return pd.DataFrame()

    summary = ranking_df[[
        'rank', 'kd_petugas', 'total_pembacaan',
        'total_score', 'konsistensi_score', 'efisiensi_score',
        'kecepatan_score', 'ranking_score'
    ]].copy()

    summary.columns = [
        'Rank', 'Petugas', 'Total Meter',
        'Score Total', 'Score Konsistensi', 'Score Efisiensi',
        'Score Kecepatan', 'Score Akhir'
    ]

    return summary