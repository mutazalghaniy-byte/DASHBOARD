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

# 2. FILTER SIDEBAR
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

# 4. TAB TABEL DATA
st.subheader("🔍 Pratinjau Data")
tab1, tab2 = st.tabs(["Data Bersih & Terfilter", "Data Mentah (Original)"])

with tab1:
    st.dataframe(df_filtered, use_container_width=True)
with tab2:
    st.dataframe(df_raw, use_container_width=True)

st.markdown("---")

# 5. VISUALISASI INTERAKTIF DENGAN PLOTLY
st.subheader("📊 Visualisasi Interaktif")

if total_influencers > 0:
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        country_summary = df_filtered.groupby('country').size().reset_index(name='jumlah_influencer')
        country_summary = country_summary.sort_values(by='jumlah_influencer', ascending=False).head(10)
        
        fig1 = px.bar(
            country_summary,
            y="country",
            x="jumlah_influencer",
            orientation='h',
            title="Top 10 Negara dengan Influencer Terbanyak",
            color="jumlah_influencer",
            color_continuous_scale="Blues"
        )
        fig1.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig1, use_container_width=True)

    with col_chart2:
        numeric_cols = df_filtered.select_dtypes(include=[np.number])
        corr_matrix = numeric_cols.corr()
        
        fig2 = px.imshow(
            corr_matrix,
            text_auto=".2f",
            aspect="auto",
            color_continuous_scale="Viridis",
            title="Matriks Korelasi Fitur Numerik"
        )
        st.plotly_chart(fig2, use_container_width=True)

    col_chart3, col_chart4 = st.columns(2)

    with col_chart3:
        fig3 = px.scatter(
            df_filtered,
            x="followers",
            y="avg_likes",
            size="influence_score",
            color="country",
            hover_name="channel_info" if "channel_info" in df_filtered.columns else None,
            title="Hubungan Jumlah Followers vs Rata-rata Likes",
            log_x=True,
            log_y=True
        )
        st.plotly_chart(fig3, use_container_width=True)

    with col_chart4:
        fig4 = px.histogram(
            df_filtered,
            x="60_day_eng_rate",
            nbins=20,
            title="Distribusi Engagement Rate (60 Hari)",
            color_discrete_sequence=["#00CC96"]
        )
        fig4.update_layout(xaxis_title="60 Day Engagement Rate (%)", yaxis_title="Jumlah Influencer")
        st.plotly_chart(fig4, use_container_width=True)
else:
    st.warning("⚠️ Tidak ada data yang sesuai dengan filter yang dipilih.")

st.markdown("---")

# 6. INSIGHT & REKOMENDASI
st.subheader("💡 Insight & Rekomendasi")
st.markdown("""
**3 Insight Utama:**
1. Dominasi pasar influencer teratas sebagian besar terkonsentrasi di negara-negara tertentu seperti Amerika Serikat dan beberapa negara Eropa/Amerika Latin.
2. Jumlah *followers* yang tinggi tidak selalu menjamin *engagement rate* yang lebih tinggi; influencer skala menengah sering kali memiliki keterikatan audiens (*engagement rate*) yang lebih tinggi.
3. *Influence Score* memiliki korelasi kuat dengan total interaksi (*total likes* dan *avg likes*), menjadikannya indikator efektivitas kampanye yang andal.

**Rekomendasi:**
Perusahaan atau brand disarankan untuk tidak hanya berpatokan pada total *followers* saat memilih influencer untuk kampanye pemasaran. Sebaiknya gunakan kombinasi *Influence Score* dan *Engagement Rate* 60 hari terakhir agar alokasi budget pemasaran memberikan hasil interaksi yang lebih optimal.
""")