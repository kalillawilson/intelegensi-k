import streamlit as st
import pandas as pd
import plotly.express as px
from openai import OpenAI # Untuk integrasi AI
import os # Untuk mengambil API Key dari environment variable

# --- Konfigurasi Halaman Streamlit ---
st.set_page_config(layout="wide", page_title="AI-Powered Media Intelligence")

# --- Judul Dashboard ---
st.title("📊 AI-Powered Media Intelligence Dashboard")
st.markdown("Dashboard ini menyediakan insight data media dengan bantuan Kecerdasan Buatan untuk strategi konten yang lebih cerdas.")

# --- Bagian Upload File (Opsional, tapi direkomendasikan) ---
uploaded_file = st.file_uploader("Unggah file CSV Anda", type=["csv"])
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.success("✅ File berhasil diunggah dan dimuat!")
else:
    # Jika tidak ada file diunggah, coba muat data default yang sudah bersih
    try:
        # Asumsikan Anda telah mengunggah atau memiliki 'cleaned_data.csv' di sesi Colab
        df = pd.read_csv("cleaned_data.csv")
        st.info("ℹ️ Menggunakan data default (cleaned_data.csv). Unggah file Anda sendiri untuk analisis kustom.")
    except FileNotFoundError:
        st.error("🚨 Silakan unggah file CSV Anda. File 'cleaned_data.csv' tidak ditemukan. Pastikan Anda sudah menyimpannya atau mengunggah file.")
        st.stop() # Hentikan eksekusi jika tidak ada data untuk dianalisis

# --- Pra-pemrosesan Data (Ringkas, hanya untuk memastikan Streamlit memproses data yang diunggah/default) ---
# Konversi kolom 'Tanggal' ke format datetime
if 'Tanggal' in df.columns:
    df['Tanggal'] = pd.to_datetime(df['Tanggal'], errors='coerce')
    df.dropna(subset=['Tanggal'], inplace=True) # Hapus baris jika konversi tanggal gagal

# Standardisasi kolom kategorikal (huruf kapital di awal)
for col in ['Sentimen', 'Platform', 'Tipe Media', 'Lokasi']:
    if col in df.columns:
        df[col] = df[col].astype(str).str.capitalize()

# --- Konfigurasi AI (Ganti API Key Anda di sini atau gunakan Streamlit Secrets!) ---
# Untuk prototyping di Colab, Anda bisa langsung menaruhnya.
# Namun, untuk deployment di Streamlit Cloud, SANGAT disarankan menggunakan st.secrets
# atau variabel lingkungan untuk keamanan.

# Ambil API Key dari environment variable (ini lebih aman)
# Di Colab, Anda bisa mengatur environment variable sebelum menjalankan app.py
# Misalnya: os.environ['OPENROUTER_API_KEY'] = "sk-or-xxxxxxxxxxxx"
# Atau langsung masukkan stringnya seperti di bawah untuk prototyping cepat
OPENROUTER_API_KEY = "sk-or-xxxxxxxxxxxx" # <<< GANTI DENGAN API KEY OPENROUTER ANDA DI SINI!

if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "sk-or-xxxxxxxxxxxx":
    st.warning("⚠️ API Key OpenRouter belum diatur. Insight AI tidak akan berfungsi.")
    client = None # Set client ke None agar tidak ada error jika API Key tidak ada
else:
    client = OpenAI(
        base_url = "https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )

# Fungsi untuk mendapatkan insight AI
@st.cache_data(show_spinner=False) # Cache hasil AI agar tidak memanggil API berulang kali
def get_ai_insight(data_for_ai_str, prompt_question):
    if client is None:
        return "API Key AI belum diatur, tidak dapat menghasilkan insight."
    try:
        messages = [
            {"role": "system", "content": "Anda adalah analis media cerdas dan ahli dalam memberikan 3 insight kunci, ringkas, dan relevan untuk strategi konten atau produksi media dari data yang diberikan. Fokus pada implikasi bisnis dan rekomendasi yang dapat ditindaklanjuti. Jawab dalam Bahasa Indonesia."},
            {"role": "user", "content": f"Berdasarkan data berikut:\n\n{data_for_ai_str}\n\n{prompt_question}"}
        ]
        response = client.chat.completions.create(
            model="openai/gpt-3.5-turbo", # Anda bisa coba model lain dari OpenRouter, e.g., "google/gemini-pro"
            messages=messages,
            temperature=0.7 # Kontrol kreativitas respon AI
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Gagal mendapatkan insight AI: {e}. Pastikan API Key benar dan ada koneksi internet."

# --- Tampilkan Visualisasi Data dan Insight AI ---
st.header("Visualisasi Data & Insight Otomatis 🤖")

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Distribusi Sentimen Media")
    sentiment_counts = df['Sentimen'].value_counts().reset_index()
    sentiment_counts.columns = ['Sentimen', 'Jumlah']
    fig_sentiment = px.pie(sentiment_counts,
                           names='Sentimen',
                           values='Jumlah',
                           title='Distribusi Sentimen Publik',
                           color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig_sentiment, use_container_width=True)

    st.markdown("##### Insight AI:")
    prompt_sentiment = "Berdasarkan distribusi sentimen di atas, apa 3 insight kunci tentang persepsi publik terhadap merek/kampanye ini? Kaitkan dengan implikasi untuk strategi konten atau PR."
    # Untuk AI, kirimkan data sebagai string agar AI bisa membacanya
    sentiment_data_str = sentiment_counts.to_string()
    insight_sentiment = get_ai_insight(sentiment_data_str, prompt_sentiment)
    st.write(insight_sentiment)

with col2:
    st.subheader("2. Tren Engagement Konten dari Waktu ke Waktu")
    df_daily_engagement = df.groupby(df['Tanggal'].dt.date)['Engagement'].sum().reset_index()
    df_daily_engagement.columns = ['Tanggal', 'Total Engagement']
    fig_engagement_trend = px.line(df_daily_engagement,
                                   x='Tanggal',
                                   y='Total Engagement',
                                   title='Tren Engagement Konten',
                                   markers=True)
    st.plotly_chart(fig_engagement_trend, use_container_width=True)

    st.markdown("##### Insight AI:")
    prompt_trend = "Analisis data tren engagement harian ini. Identifikasi puncak dan penurunan signifikan. Berikan 3 insight tentang performa kampanye dan apa yang mungkin menyebabkannya, serta rekomendasi untuk waktu posting di masa depan."
    engagement_data_str = df_daily_engagement.to_string()
    insight_trend = get_ai_insight(engagement_data_str, prompt_trend)
    st.write(insight_trend)

st.subheader("3. Perbandingan Engagement per Platform Media")
platform_engagement = df.groupby('Platform')['Engagement'].sum().reset_index()
fig_platform_engagement = px.bar(platform_engagement,
                                 x='Platform',
                                 y='Engagement',
                                 title='Total Engagement per Platform Media',
                                 color='Platform')
st.plotly_chart(fig_platform_engagement, use_container_width=True)

st.markdown("##### Insight AI:")
prompt_platform = "Dari perbandingan engagement antar platform, platform mana yang paling efektif dan mengapa? Berikan 3 insight untuk alokasi sumber daya konten di platform yang berbeda."
platform_data_str = platform_engagement.to_string()
insight_platform = get_ai_insight(platform_data_str, prompt_platform)
st.write(insight_platform)

col3, col4 = st.columns(2)

with col3:
    st.subheader("4. Proporsi Tipe Media")
    media_type_counts = df['Tipe Media'].value_counts().reset_index()
    media_type_counts.columns = ['Tipe Media', 'Jumlah']
    fig_media_type = px.bar(media_type_counts,
                           x='Tipe Media',
                           y='Jumlah',
                           title='Proporsi Tipe Media',
                           color='Tipe Media')
    st.plotly_chart(fig_media_type, use_container_width=True)

    st.markdown("##### Insight AI:")
    prompt_media_type = "Berdasarkan proporsi tipe media, tipe media apa yang paling dominan dan kurang? Berikan 3 insight tentang strategi produksi media yang optimal berdasarkan preferensi tipe media."
    media_type_data_str = media_type_counts.to_string()
    insight_media_type = get_ai_insight(media_type_data_str, prompt_media_type)
    st.write(insight_media_type)

with col4:
    st.subheader("5. Top 5 Lokasi Berdasarkan Engagement")
    # Pastikan Lokasi adalah string dan bukan NaN
    location_engagement = df.groupby('Lokasi')['Engagement'].sum().nlargest(5).reset_index()
    fig_location = px.bar(location_engagement,
                         x='Lokasi',
                         y='Engagement',
                         title='Top 5 Lokasi Berdasarkan Engagement',
                         color='Lokasi')
    st.plotly_chart(fig_location, use_container_width=True)

    st.markdown("##### Insight AI:")
    prompt_location = "Dari top 5 lokasi berdasarkan engagement, insight apa yang dapat Anda berikan tentang target audiens geografis? Berikan 3 insight untuk lokalisasi konten atau kampanye PR."
    location_data_str = location_engagement.to_string()
    insight_location = get_ai_insight(location_data_str, prompt_location)
    st.write(insight_location)

st.sidebar.markdown("---")
st.sidebar.markdown("### Tentang Dashboard Ini")
st.sidebar.info(
    "Dashboard ini dibangun sebagai bagian dari Mini-Capstone Project 'AI-Powered Media Insights: Elevating Content Strategy with Data'."
    "Menggabungkan visualisasi data interaktif dengan insight yang dihasilkan oleh AI untuk membantu profesional media membuat keputusan berbasis data."
)
