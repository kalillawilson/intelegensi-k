import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Quenchsy Dashboard", layout="wide")
st.title("📊 Quenchsy Media Intelligence Dashboard")

uploaded_file = st.sidebar.file_uploader("Upload CSV File", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df['Date'] = pd.to_datetime(df['Date'])

    st.success("File berhasil dibaca!")

    # Chart 1
    st.header("1. Sentiment Breakdown")
    sent = df['Sentiment'].value_counts().reset_index()
    sent.columns = ['Sentiment', 'Count']
    fig1 = px.pie(sent, names='Sentiment', values='Count')
    st.plotly_chart(fig1, use_container_width=True)

    # Chart 2
    st.header("2. Engagement Trend Over Time")
    trend = df.groupby('Date')['Engagements'].sum().reset_index()
    fig2 = px.line(trend, x='Date', y='Engagements', markers=True)
    st.plotly_chart(fig2, use_container_width=True)

    # Chart 3
    st.header("3. Engagement by Platform")
    plat = df.groupby('Platform')['Engagements'].sum().reset_index()
    fig3 = px.bar(plat, x='Platform', y='Engagements', color='Platform', text='Engagements')
    st.plotly_chart(fig3, use_container_width=True)

    # Chart 4
    st.header("4. Media Type Mix")
    media = df['Media_Type'].value_counts().reset_index()
    media.columns = ['Media_Type', 'Count']
    fig4 = px.pie(media, names='Media_Type', values='Count')
    st.plotly_chart(fig4, use_container_width=True)

    # Chart 5
    st.header("5. Top 5 Locations by Engagement")
    loc = df.groupby('Location')['Engagements'].sum().reset_index()
    top5 = loc.sort_values(by='Engagements', ascending=False).head(5)
    fig5 = px.bar(top5, x='Location', y='Engagements', text='Engagements', color='Location')
    st.plotly_chart(fig5, use_container_width=True)
else:
    st.warning("Upload dulu file CSV kamu di sidebar yaa.")
