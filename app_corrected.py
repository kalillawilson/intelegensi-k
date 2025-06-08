
import streamlit as st
import pandas as pd
import plotly.express as px
import openai
import os

# Setup page
st.set_page_config(page_title="AI-Assisted Media Analysis", layout="wide")
st.title("📊 Media Analysis Dashboard with AI Insight")
st.markdown("Unggah file CSV hasil crawling untuk melihat insight media dan sentimen.")

# Set OpenRouter API
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
openai.api_key = OPENROUTER_API_KEY
openai.base_url = "https://openrouter.ai/api/v1"

@st.cache_data(show_spinner=False)
def get_ai_insight(data_for_ai_str, prompt_question):
    if not openai.api_key:
        return "API Key belum diatur, insight AI tidak bisa diproses."
    try:
        messages = [
            {"role": "system", "content": "Anda adalah analis media profesional."},
            {"role": "user", "content": f"Berdasarkan data berikut:

{data_for_ai_str}

{prompt_question}"}
        ]
        response = openai.ChatCompletion.create(
            model="openai/gpt-3.5-turbo",
            messages=messages,
            temperature=0.7
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"❌ Gagal mendapatkan insight AI: {e}"

uploaded_file = st.file_uploader("Unggah file CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
else:
    try:
        df = pd.read_csv("cleaned_data.csv")
    except:
        st.warning("Tidak ada data yang tersedia.")
        st.stop()

# Pastikan kolom yang dibutuhkan ada
required_columns = ['Tanggal', 'Sentimen', 'Engagement', 'Platform', 'Tipe Media', 'Lokasi']
if not all(col in df.columns for col in required_columns):
    st.error("🚫 Data tidak lengkap. Pastikan CSV mengandung kolom: " + ", ".join(required_columns))
    st.stop()

df['Tanggal'] = pd.to_datetime(df['Tanggal'])

# Visualisasi sentimen
fig_sentimen = px.histogram(df, x='Sentimen', title='Distribusi Sentimen', color='Sentimen')
st.plotly_chart(fig_sentimen, use_container_width=True)

# Tren waktu
df_daily = df.groupby(df['Tanggal'].dt.date).size().reset_index(name='Jumlah')
fig_trend = px.line(df_daily, x='Tanggal', y='Jumlah', title='Jumlah Berita per Hari')
st.plotly_chart(fig_trend, use_container_width=True)

# Platform distribusi
fig_platform = px.histogram(df, x='Platform', title='Distribusi Platform', color='Platform')
st.plotly_chart(fig_platform, use_container_width=True)

# Jenis media
fig_media = px.histogram(df, x='Tipe Media', title='Jenis Media', color='Tipe Media')
st.plotly_chart(fig_media, use_container_width=True)

# Lokasi
fig_lokasi = px.histogram(df, x='Lokasi', title='Sebaran Lokasi', color='Lokasi')
st.plotly_chart(fig_lokasi, use_container_width=True)

# Ringkasan data
with st.expander("📄 Ringkasan Data"):
    st.dataframe(df.head(50))

# AI Insight
st.subheader("🧠 AI Insight Berdasarkan Data")
data_for_ai = df[['Tanggal', 'Sentimen', 'Engagement', 'Platform', 'Tipe Media', 'Lokasi']].head(50).to_string(index=False)
prompt = "Apa insight yang bisa diambil dari data media ini, dan strategi komunikasi seperti apa yang disarankan?"

if st.button("🔍 Dapatkan Insight AI"):
    with st.spinner("Meminta insight dari AI..."):
        result = get_ai_insight(data_for_ai, prompt)
        st.success("Insight berhasil diambil!")
        st.markdown(result)
