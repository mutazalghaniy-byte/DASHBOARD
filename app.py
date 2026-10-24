# ====================================================
# DASHBOARD INFLUENCER INSTAGRAM (DATA UPDATED)
# ====================================================
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Setup tampilan visualisasi
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)

# 1. Memuat Dataset
file_path = 'top_insta_influencers_data[1].csv'
df = pd.read_csv(file_path)

# 2. Fungsi Konversi String Notasi (k, m, b, %) ke Float
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

# 3. Proses Cleaning Data
df_clean = df.copy().drop_duplicates()
df_clean['country'] = df_clean['country'].fillna('Unknown')

cols_to_convert = ['posts', 'followers', 'avg_likes', '60_day_eng_rate', 'new_post_avg_like', 'total_likes']
for col in cols_to_convert:
    df_clean[col] = df_clean[col].apply(parse_number)

df_clean['60_day_eng_rate'] = df_clean['60_day_eng_rate'].fillna(df_clean['60_day_eng_rate'].median())

# ====================================================
# 4. KEY PERFORMANCE INDICATORS (KPI)
# ====================================================
total_influencers = len(df_clean)
total_followers_sum = df_clean['followers'].sum()
avg_influence = df_clean['influence_score'].mean()
avg_engagement = df_clean['60_day_eng_rate'].mean()

print("========================================")
print("       KEY PERFORMANCE INDICATORS       ")
print("========================================")
print(f"• Total Akun Influencer Teratas : {total_influencers:,} akun")
print(f"• Total Akumulasi Followers     : {total_followers_sum:,.0f} pengikut")
print(f"• Rata-rata Skor Pengaruh       : {avg_influence:.2f} / 100")
print(f"• Rata-rata Engagement Rate     : {avg_engagement:.2f}%")
print("========================================\n")

# ====================================================
# 5. VISUALISASI DASHBOARD
# ====================================================
# Chart 1: Top 10 Negara Asal Influencer
plt.figure(figsize=(10, 5))
country_summary = df_clean.groupby('country').agg(
    jumlah_influencer=('channel_info', 'count')
).reset_index().sort_values(by='jumlah_influencer', ascending=False)

top_countries = country_summary.head(10)
sns.barplot(data=top_countries, x='jumlah_influencer', y='country', palette='Blues_r')
plt.title('Top 10 Negara dengan Influencer Terbanyak', fontsize=14, fontweight='bold')
plt.xlabel('Jumlah Influencer')
plt.ylabel('Negara')
plt.tight_layout()
plt.show()

# Chart 2: Matriks Korelasi Fitur Numerik
plt.figure(figsize=(8, 6))
numeric_df = df_clean.select_dtypes(include=[np.number])
sns.heatmap(numeric_df.corr(), annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5)
plt.title('Matriks Korelasi Antar Fitur Numerik', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.show()