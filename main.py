import streamlit as st
import speedtest
import plotly.graph_objects as go
import pandas as pd
import time

if "log" not in st.session_state:
    st.session_state.log = []

def run_speed_test():
    st_test = speedtest.Speedtest()
    st_test.get_best_server()
    download = st_test.download() / 1_000_000
    upload = st_test.upload() / 1_000_000
    ping = st_test.results.ping
    server = st_test.get_best_server()
    location = f"{server['name']}, {server['country']}"

    result = {
        "Ping (ms)": round(ping, 2),
        "Download (Mbps)": round(download, 2),
        "Upload (Mbps)": round(upload, 2),
        "Server": location,
        "Timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    if download > 50 and upload > 20 and ping < 50:
        result["Status"] = "Good"
    else:
        result["Status"] = "Bad"

    st.session_state.log.append(result)
    return result

def compact_gauge(value, title, max_value=200, color="green"):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title, 'font': {'size': 14}},
        gauge={
            'axis': {'range': [0, max_value], 'tickwidth': 1, 'tickcolor': "black"},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 1,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, max_value/2], 'color': "lightgray"},
                {'range': [max_value/2, max_value], 'color': "darkgray"}
            ],
            'threshold': {'line': {'color': "red", 'width': 3}, 'value': max_value*0.9}
        }
    ))
    fig.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
    return fig

st.set_page_config(page_title="Speed Monitor", layout="wide")
st.title("⚡ Compact Internet Speed Dashboard")

col1, col2, col3 = st.columns(3)

if st.button("Run One-Time Test"):
    result = run_speed_test()
    with col1:
        st.plotly_chart(compact_gauge(result["Download (Mbps)"], "Download", 200, "blue"), use_container_width=True)
    with col2:
        st.plotly_chart(compact_gauge(result["Upload (Mbps)"], "Upload", 100, "orange"), use_container_width=True)
    with col3:
        st.plotly_chart(compact_gauge(result["Ping (ms)"], "Ping", 200, "green"), use_container_width=True)
    st.success(f"Server: {result['Server']} | Status: {result['Status']}")

interval = st.number_input("Set interval (seconds)", min_value=5, step=5, value=10)
if st.button("Start Interval Test"):
    stop = st.empty()
    while True:
        result = run_speed_test()
        with col1:
            st.plotly_chart(compact_gauge(result["Download (Mbps)"], "Download", 200, "blue"), use_container_width=True)
        with col2:
            st.plotly_chart(compact_gauge(result["Upload (Mbps)"], "Upload", 100, "orange"), use_container_width=True)
        with col3:
            st.plotly_chart(compact_gauge(result["Ping (ms)"], "Ping", 200, "green"), use_container_width=True)
        st.info(f"Last Test: {result['Timestamp']} | Status: {result['Status']}")
        time.sleep(interval)
        if stop.button("Stop Interval Test"):
            break

if st.session_state.log:
    df = pd.DataFrame(st.session_state.log)
    st.subheader("📊 Test Log")
    st.dataframe(df)
