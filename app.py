import os
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="Dashboard Analisis Influencer Instagram",
    page_icon="📸",
    layout="wide"
)

# Judul Utama & Sumber Data
st.title("📸 Dashboard Analisis Influencer Instagram")
st.markdown("**Sumber Dataset:** `top_insta_influencers_data[1].csv` (Top Instagram Influencers)")
st.markdown(
    "Dashboard interaktif ini menyajikan KPI, visualisasi demografi negara, "
    "serta filter dinamis untuk menganalisis performa, follower, dan engagement rate influencer Instagram."
)

# 1. BACA & BERSIHKAN DATASET
file_path = 'top_insta_influencers_data[1].csv'

def parse_number(val):
    if pd.isna(val):
        return np.nan
    val = str(val).strip().lower().replace('%', '')
    if val.endswith('b'):
        return float(val[:-1]) * 1e9
    elif val.endswith('m'):
        return float(val[:-1]) * 1e6
    elif val.endswith('k'):
        return float(val[:-1]) * 1e3
    try:
        return float(val)
    except:
        return np.nan

@st.cache_data
def load_data(path):
    if os.path.exists(path):
        df = pd.read_csv(path)
    else:
        # Dummy data jika file tidak ditemukan
        data = {
            "channel_info": ["cristiano", "leomessi", "kyliejenner", "selenagomez", "therock"],
            "country": ["Spain", "Argentina", "United States", "United States", "United States"],
            "posts": ["3.3k", "1.2k", "7.1k", "1.8k", "6.2k"],
            "followers": ["475.8m", "358.7m", "365.1m", "342.1m", "334.0m"],
            "avg_likes": "2.1m",
            "60_day_eng_rate": ["1.39%", "2.15%", "1.85%", "1.20%", "0.95%"],
            "new_post_avg_like": "3.5m",
            "total_likes": "10b",
            "influence_score": [92, 90, 89, 88, 87]
        }
        df = pd.DataFrame(data)
    
    df_clean = df.copy().drop_duplicates()
    
    if 'country' in df_clean.columns:
        df_clean['country'] = df_clean['country'].fillna('Unknown')
    else:
        df_clean['country'] = 'Unknown'

    cols_to_convert = ['posts', 'followers', 'avg_likes', '60_day_eng_rate', 'new_post_avg_like', 'total_likes']
    for col in cols_to_convert:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].apply(parse_number)

    if '60_day_eng_rate' in df_clean.columns:
        df_clean['60_day_eng_rate'] = df_clean['60_day_eng_rate'].fillna(df_clean['60_day_eng_rate'].median())

    return df, df_clean

df_raw, df_clean = load_data(file_path)

# 2. FILTER SIDEBAR & TOMBOL DOWNLOAD DATA BERSIH
st.sidebar.header("🎛️ Filter Data")

daftar_negara = sorted(df_clean["country"].unique().tolist())
country_filter = st.sidebar.multiselect(
    "Pilih Negara Asal:",
    options=daftar_negara,
    default=daftar_negara
)

min_score = int(df_clean["influence_score"].min()) if "influence_score" in df_clean.columns else 0
max_score = int(df_clean["influence_score"].max()) if "influence_score" in df_clean.columns else 100

score_filter = st.sidebar.slider(
    "Rentang Influence Score:",
    min_value=min_score,
    max_value=max_score,
    value=(min_score, max_score)
)

# Terapkan Filter
df_filtered = df_clean[
    (df_clean["country"].isin(country_filter)) &
    (df_clean["influence_score"].between(score_filter[0], score_filter[1]))
]

st.sidebar.markdown("---")
st.sidebar.subheader("💾 Unduh Dataset")
csv_bersih = df_clean.to_csv(index=False).encode('utf-8')
st.sidebar.download_button(
    label="⬇️ Download Data Bersih",
    data=csv_bersih,
    file_name='dataset_influencer_bersih.csv',
    mime='text/csv'
)

# 3. INDIKATOR KINERJA UTAMA (KPI)
st.subheader("📈 Key Performance Indicators (KPI)")
total_influencers = len(df_filtered)
total_followers_sum = df_filtered["followers"].sum() if total_influencers > 0 else 0
avg_influence = df_filtered["influence_score"].mean() if total_influencers > 0 else 0
avg_engagement = df_filtered["60_day_eng_rate"].mean() if total_influencers > 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Influencer (Terfilter)", f"{total_influencers:,} Akun")
col2.metric("Total Akumulasi Followers", f"{total_followers_sum/1e6:,.1f} Juta" if total_followers_sum >= 1e6 else f"{total_followers_sum:,.0f}")
col3.metric("Rata-rata Influence Score", f"{avg_influence:.2f} / 100")
col4.metric("Rata-rata Engagement Rate", f"{avg_engagement:.2f}%")

st.markdown("---")

# 4. MEMBUAT PILIHAN TAB UNTUK MENU UTAMA
tab_data, tab_visual, tab_insight = st.tabs([
    "🔍 Pratinjau Data", 
    "📊 Visualisasi Interaktif", 
    "💡 Insight & Rekomendasi"
])

# ================= TAB 1: PRATINJAU DATA =================
with tab_data:
    st.markdown("### 📋 Data Bersih & Terfilter")
    st.markdown("Menampilkan data yang telah dibersihkan dari duplikat dan sudah diterapkan filter dari sidebar.")
    st.dataframe(df_filtered, use_container_width=True)
    
    st.markdown("---")
    
    st.markdown("### 🗄️ Data Mentah (Original)")
    cek_masalah = st.checkbox("⚠️ Tampilkan hanya data yang Kosong (Null) atau Duplikat (Clon)")
    
    if cek_masalah:
        # Mencari baris yang mengandung NaN atau Duplikat
        df_bermasalah = df_raw[df_raw.isna().any(axis=1) | df_raw.duplicated(keep=False)]
        if df_bermasalah.empty:
            st.success("Bagus! Tidak ditemukan data kosong atau kloningan.")
        else:
            st.warning(f"Ditemukan {len(df_bermasalah)} baris data yang kosong atau duplikat.")
            st.dataframe(df_bermasalah, use_container_width=True)
    else:
        st.dataframe(df_raw, use_container_width=True)

# ================= TAB 2: VISUALISASI INTERAKTIF =================
with tab_visual:
    if total_influencers > 0:
        st.info("💡 *Tips: Kamu bisa mengunduh gambar diagram dengan mengarahkan kursor ke diagram lalu klik ikon kamera (Download plot as a png) di pojok kanan atas.*")
        
        # DIAGRAM 1: Bar Chart Negara
        st.markdown("### 1. Top 10 Negara dengan Influencer Terbanyak")
        country_summary = df_filtered.groupby('country').size().reset_index(name='jumlah_influencer')
        country_summary = country_summary.sort_values(by='jumlah_influencer', ascending=False).head(10)
        
        fig1 = px.bar(
            country_summary,
            y="country", x="jumlah_influencer",
            orientation='h', color="jumlah_influencer", color_continuous_scale="Blues"
        )
        fig1.update_layout(yaxis={'categoryorder': 'total ascending'}, height=500)
        st.plotly_chart(fig1, use_container_width=True)
        st.markdown("**Penjelasan:** Diagram ini menunjukkan persebaran dominasi asal negara para influencer. Berguna untuk melihat target audiens geografis terbesar.")
        st.download_button("⬇️ Download Data Top Negara (CSV)", data=country_summary.to_csv(index=False).encode('utf-8'), file_name="top_10_negara.csv", mime="text/csv", key="dl_1")
        
        st.markdown("---")
        
        # DIAGRAM 2: Matriks Korelasi
        st.markdown("### 2. Matriks Korelasi Fitur Numerik")
        numeric_cols = df_filtered.select_dtypes(include=[np.number])
        corr_matrix = numeric_cols.corr()
        
        fig2 = px.imshow(
            corr_matrix,
            text_auto=".2f", aspect="auto", color_continuous_scale="Viridis"
        )
        fig2.update_layout(height=600)
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown("**Penjelasan:** Matriks ini mengukur hubungan antar metrik. Nilai yang mendekati 1 menunjukkan hubungan sebab-akibat yang sangat kuat (misalnya Followers vs Total Likes).")
        st.download_button("⬇️ Download Data Korelasi (CSV)", data=corr_matrix.to_csv().encode('utf-8'), file_name="korelasi_matriks.csv", mime="text/csv", key="dl_2")
        
        st.markdown("---")
        
        # DIAGRAM 3: Scatter Plot Followers vs Likes
        st.markdown("### 3. Hubungan Jumlah Followers vs Rata-rata Likes")
        fig3 = px.scatter(
            df_filtered,
            x="followers", y="avg_likes", size="influence_score", color="country",
            hover_name="channel_info" if "channel_info" in df_filtered.columns else None,
            log_x=True, log_y=True
        )
        fig3.update_layout(height=550)
        st.plotly_chart(fig3, use_container_width=True)
        st.markdown("**Penjelasan:** Menunjukkan pola apakah *followers* tinggi selalu menjamin interaksi (likes) yang tinggi. Ukuran gelembung menunjukkan besarnya skor pengaruh.")
        df_scatter = df_filtered[['channel_info', 'country', 'followers', 'avg_likes', 'influence_score']] if 'channel_info' in df_filtered.columns else df_filtered[['country', 'followers', 'avg_likes', 'influence_score']]
        st.download_button("⬇️ Download Data Scatter Plot (CSV)", data=df_scatter.to_csv(index=False).encode('utf-8'), file_name="scatter_followers_likes.csv", mime="text/csv", key="dl_3")
        
        st.markdown("---")
        
        # DIAGRAM 4: Histogram Engagement Rate
        st.markdown("### 4. Distribusi Engagement Rate (60 Hari)")
        fig4 = px.histogram(
            df_filtered,
            x="60_day_eng_rate", nbins=20, color_discrete_sequence=["#00CC96"]
        )
        fig4.update_layout(xaxis_title="60 Day Engagement Rate (%)", yaxis_title="Jumlah Influencer", height=500)
        st.plotly_chart(fig4, use_container_width=True)
        st.markdown("**Penjelasan:** Menunjukkan sebaran rasio interaksi (engagement). Ini membantu kita mengetahui standar engagement rata-rata di industri, apakah cenderung tinggi atau rendah.")
        df_hist = df_filtered[['channel_info', '60_day_eng_rate']] if 'channel_info' in df_filtered.columns else df_filtered[['60_day_eng_rate']]
        st.download_button("⬇️ Download Data Engagement (CSV)", data=df_hist.to_csv(index=False).encode('utf-8'), file_name="distribusi_engagement.csv", mime="text/csv", key="dl_4")

    else:
        st.warning("⚠️ Tidak ada data yang sesuai dengan filter yang dipilih.")

# ================= TAB 3: INSIGHT & REKOMENDASI =================
with tab_insight:
    st.markdown("""
    ### 💡 3 Insight Utama
    1. Sebagian besar influencer top global secara demografis terkonsentrasi kuat di wilayah Amerika Serikat.
    2. Tingginya angka *followers* terbukti tidak selalu menjamin besarnya persentase *engagement rate* dari audiens.
    3. Metrik *Influence Score* memiliki korelasi positif yang sangat kuat terhadap rata-rata jumlah *likes*.

    ### 🎯 Rekomendasi
    Pilih influencer berdasarkan kombinasi *Influence Score* dan *Engagement Rate* alih-alih hanya berfokus pada jumlah *followers* untuk memastikan efektivitas interaksi audiens.
    """)