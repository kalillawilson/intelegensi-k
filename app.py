import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Quenchsy Dashboard", layout="wide")
st.title("📊 Quenchsy Media Intelligence Dashboard")

# Load data langsung dari file CSV (tidak perlu upload)
df = pd.read_csv("cleaned_data.csv")
df['Date'] = pd.to_datetime(df['Date'])

st.success("📁 Data berhasil dimuat!")

# 1. Sentiment Breakdown
st.header("1. Sentiment Breakdown")
sent = df['Sentiment'].value_counts().reset_index()
sent.columns = ['Sentiment', 'Count']
fig1 = px.pie(sent, names='Sentiment', values='Count')
st.plotly_chart(fig1, use_container_width=True)

st.markdown("💡 *Insight:* Sentimen positif mendominasi, menunjukkan brand Quenchsy diterima dengan baik. Namun, ada sentimen negatif yang muncul di Instagram dan perlu dievaluasi.")

# 2. Engagement Trend
st.header("2. Engagement Trend Over Time")
trend = df.groupby('Date')['Engagements'].sum().reset_index()
fig2 = px.line(trend, x='Date', y='Engagements', markers=True)
st.plotly_chart(fig2, use_container_width=True)

st.markdown("💡 *Insight:* Terdapat lonjakan engagement pada pertengahan Februari, kemungkinan karena kolaborasi dengan influencer besar.")

# 3. Platform Comparison
st.header("3. Engagement by Platform")
plat = df.groupby('Platform')['Engagements'].sum().reset_index()
fig3 = px.bar(plat, x='Platform', y='Engagements', color='Platform', text='Engagements')
st.plotly_chart(fig3, use_container_width=True)

st.markdown("💡 *Insight:* TikTok adalah platform dengan engagement tertinggi. Twitter memiliki engagement terendah, meskipun sentimennya positif.")

# 4. Media Type Mix
st.header("4. Media Type Mix")
media = df['Media_Type'].value_counts().reset_index()
media.columns = ['Media_Type', 'Count']
fig4 = px.pie(media, names='Media_Type', values='Count')
st.plotly_chart(fig4, use_container_width=True)

st.markdown("💡 *Insight:* Konten berbentuk video adalah yang paling dominan, dan ini selaras dengan karakter Gen Z yang visual-first.")

# 5. Top 5 Locations
st.header("5. Top 5 Locations by Engagement")
loc = df.groupby('Location')['Engagements'].sum().reset_index()
top5 = loc.sort_values(by='Engagements', ascending=False).head(5)
fig5 = px.bar(top5, x='Location', y='Engagements', text='Engagements', color='Location')
st.plotly_chart(fig5, use_container_width=True)

st.markdown("💡 *Insight:* Makassar dan Jakarta menjadi dua kota dengan engagement tertinggi, menandakan potensi aktivasi lokal di wilayah tersebut.")
