import streamlit as st
import speedtest
import plotly.graph_objects as go
import time
import pandas as pd

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

def plot_gauge(value, title, max_value=200):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title},
        gauge={
            'axis': {'range': [0, max_value]},
            'bar': {'color': "green"},
            'steps': [
                {'range': [0, max_value/2], 'color': "lightgray"},
                {'range': [max_value/2, max_value], 'color': "gray"}
            ],
            'threshold': {'line': {'color': "red", 'width': 4}, 'value': max_value*0.9}
        }
    ))
    st.plotly_chart(fig, use_container_width=True)

st.title("🚀 Internet Speed Monitor with Analog Gauges")

if st.button("Run One-Time Test"):
    result = run_speed_test()
    st.write(result)
    plot_gauge(result["Download (Mbps)"], "Download Speed (Mbps)", 200)
    plot_gauge(result["Upload (Mbps)"], "Upload Speed (Mbps)", 100)
    plot_gauge(result["Ping (ms)"], "Ping (ms)", 200)

interval = st.number_input("Set interval (seconds)", min_value=5, step=5, value=10)
if st.button("Start Interval Test"):
    stop = st.empty()
    while True:
        result = run_speed_test()
        st.write(result)
        plot_gauge(result["Download (Mbps)"], "Download Speed (Mbps)", 200)
        plot_gauge(result["Upload (Mbps)"], "Upload Speed (Mbps)", 100)
        plot_gauge(result["Ping (ms)"], "Ping (ms)", 200)
        time.sleep(interval)
        if stop.button("Stop Interval Test"):
            break

if st.session_state.log:
    df = pd.DataFrame(st.session_state.log)
    st.subheader("📊 Test Log")
    st.dataframe(df)
