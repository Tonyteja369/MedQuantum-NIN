import streamlit as st
import requests
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import io

# Setup Streamlit page configuration
st.set_page_config(page_title="MedQuantum-NIN | ECG Dashboard", page_icon="🫀", layout="wide")

st.title("🫀 MedQuantum-NIN: Clinical ECG Analysis Dashboard")
st.markdown("---")

# Setup backend API url
API_URL = "http://127.0.0.1:8000/analyze"

# Helper function to get available samples
@st.cache_data
def get_sample_files():
    data_dir = "data"
    if os.path.exists(data_dir):
        files = [f for f in os.listdir(data_dir) if f.endswith('.csv') or f.endswith('.npy')]
        return files
    return []

# Sidebar for inputs
st.sidebar.header("📥 Input Source")
input_method = st.sidebar.radio("Select input method:", ("Upload File", "Select Sample Dataset"))

uploaded_file = None
selected_sample = None

if input_method == "Upload File":
    uploaded_file = st.sidebar.file_uploader("Upload an ECG File (.csv or .npy)", type=["csv", "npy"])
else:
    samples = get_sample_files()
    if samples:
        selected_sample = st.sidebar.selectbox("Choose a sample file:", samples)
    else:
        st.sidebar.warning("No sample files found in /data/ directory.")

run_btn = st.sidebar.button("🚀 Run Analysis", use_container_width=True)

if run_btn:
    file_to_send = None
    file_name = ""
    
    if input_method == "Upload File" and uploaded_file is not None:
        file_to_send = uploaded_file.getvalue()
        file_name = uploaded_file.name
    elif input_method == "Select Sample Dataset" and selected_sample is not None:
        file_path = os.path.join("data", selected_sample)
        with open(file_path, "rb") as f:
            file_to_send = f.read()
        file_name = selected_sample

    if file_to_send is None:
        st.error("Please provide a valid ECG file.")
    else:
        with st.spinner("⏳ Analyzing ECG and computing probabilistic quantum mappings..."):
            try:
                response = requests.post(
                    API_URL,
                    files={"file": (file_name, file_to_send)}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    st.success("✅ Analysis Complete")
                    
                    # Layout organization
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.subheader("📈 Annotated ECG Signal")
                        signal = np.array(result.get("signal", []))
                        time = np.array(result.get("time", []))
                        r_peaks = result.get("r_peaks", [])
                        p_peaks = result.get("p_peaks", [])
                        q_peaks = result.get("q_peaks", [])
                        s_peaks = result.get("s_peaks", [])
                        t_peaks = result.get("t_peaks", [])
                        
                        if len(signal) > 0 and len(time) > 0:
                            fig, ax = plt.subplots(figsize=(12, 5))
                            
                            # Plot Main Signal
                            ax.plot(time, signal, color='black', linewidth=1, label="ECG Signal")
                            
                            # Overlay Peaks
                            if r_peaks: ax.scatter(time[r_peaks], signal[r_peaks], color='red', marker='x', s=100, label='R-Peak', zorder=5)
                            if p_peaks: ax.scatter(time[p_peaks], signal[p_peaks], color='blue', marker='o', s=50, label='P-Peak', zorder=5)
                            if q_peaks: ax.scatter(time[q_peaks], signal[q_peaks], color='orange', marker='v', s=50, label='Q-Peak', zorder=5)
                            if s_peaks: ax.scatter(time[s_peaks], signal[s_peaks], color='purple', marker='^', s=50, label='S-Peak', zorder=5)
                            if t_peaks: ax.scatter(time[t_peaks], signal[t_peaks], color='green', marker='s', s=50, label='T-Peak', zorder=5)
                            
                            ax.set_xlabel("Time (Seconds)")
                            ax.set_ylabel("Amplitude")
                            ax.set_title("PQRST Waveform Analysis")
                            ax.grid(True, linestyle='--', alpha=0.6)
                            ax.legend(loc="upper right", ncol=6)
                            
                            st.pyplot(fig)
                        else:
                            st.warning("No signal data returned from backend.")
                            
                        # Feature display
                        st.subheader("⏱️ Clinical Features Extracted")
                        f_cols = st.columns(5)
                        f_cols[0].metric("Heart Rate", f"{result.get('heart_rate', 0)} BPM")
                        f_cols[1].metric("RR Interval", f"{result['features'].get('rr_interval', 0)} s")
                        f_cols[2].metric("PR Interval", f"{result['features'].get('pr_interval', 0)} s")
                        f_cols[3].metric("QRS Duration", f"{result['features'].get('qrs_duration', 0)} s")
                        f_cols[4].metric("QT Interval", f"{result['features'].get('qt_interval', 0)} s")
                        
                    with col2:
                        st.subheader("🩺 Final Diagnosis")
                        diag = result.get("diagnosis", "Unknown")
                        if diag == "Normal":
                            st.markdown(f"<h2 style='color: #28a745; text-align: center;'>{diag}</h2>", unsafe_allow_html=True)
                        elif diag == "Bradycardia":
                            st.markdown(f"<h2 style='color: #ffc107; text-align: center;'>{diag}</h2>", unsafe_allow_html=True)
                        elif diag == "Tachycardia":
                            st.markdown(f"<h2 style='color: #dc3545; text-align: center;'>{diag}</h2>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<h2 style='text-align: center;'>{diag}</h2>", unsafe_allow_html=True)
                        
                        st.subheader("📊 Probabilities")
                        probs = result.get("probabilities", {})
                        if probs:
                            df_probs = pd.DataFrame({
                                "Condition": list(probs.keys()),
                                "Probability": list(probs.values())
                            })
                            # Find highest prob to highlight
                            max_idx = df_probs["Probability"].idxmax()
                            colors = ['#007bff' if i != max_idx else '#ff4b4b' for i in range(len(df_probs))]
                            
                            fig2, ax2 = plt.subplots(figsize=(5, 4))
                            ax2.bar(df_probs["Condition"].str.capitalize(), df_probs["Probability"], color=colors)
                            ax2.set_ylabel("Confidence")
                            ax2.set_ylim(0, 1.0)
                            ax2.grid(axis='y', linestyle='--', alpha=0.7)
                            st.pyplot(fig2)
                            
                        st.subheader("🧠 Explainability")
                        st.info(result.get("explanation", "No explanation available."))
                        
                        st.subheader("💬 Patient Note")
                        st.success(result.get("patient_message", ""))
                        
                    st.markdown("---")
                    st.subheader("📝 Medical SOAP Report")
                    soap_text = result.get("soap_note", "No SOAP note generated.")
                    st.text_area("Generated Report", soap_text, height=250)
                    
                    st.download_button(
                        label="⬇️ Download SOAP Note",
                        data=soap_text,
                        file_name="SOAP_Report.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
            
            except requests.exceptions.ConnectionError:
                st.error("🚨 Backend Server Not Reachable! Make sure FastAPI is running on http://127.0.0.1:8000")
            except Exception as e:
                st.error(f"🚨 An error occurred: {str(e)}")
