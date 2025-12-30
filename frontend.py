import streamlit as st
import requests
from gtts import gTTS
import io

# --- CONFIGURATION ---
BACKEND_URL = "http://127.0.0.1:8000"  # Ensure this matches your FastAPI address  https://cyber-guardian-backend.onrender.com

st.set_page_config(
    page_title="CyberGuardian APK Scanner",
    page_icon="🛡️",
    layout="wide"
)

# --- HEADER ---
st.title("🛡️ CyberGuardian APK Analyzer")
st.markdown("""
    **Upload an Android APK file** to scan it for malware using our 
    Hybrid AI & Static Analysis engine.
""")
st.divider()

# --- SIDEBAR (History or Info) ---
with st.sidebar:
    st.header("ℹ️ How it works")
    st.markdown("""
    1. **Upload APK**: The file is securely stored temporarily.
    2. **Extraction**: Permissions and manifest data are extracted.
    3. **AI Analysis**: Our ML model predicts malicious behavior.
    4. **Report**: You get a detailed risk score and verdict.
    """)
    st.info("Backend Status: Checking...")
    try:
        requests.get(f"{BACKEND_URL}/")
        st.success("Online ✅")
    except:
        st.error("Offline ❌ (Start FastAPI first!)")

# --- MAIN APP LOGIC ---

# 1. FILE UPLOAD SECTION
uploaded_file = st.file_uploader("Choose an APK file...", type="apk")

if uploaded_file is not None:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.info(f"📄 File: {uploaded_file.name}")
        st.caption(f"Size: {uploaded_file.size / (1024*1024):.2f} MB")
        
        # Upload Button
        if st.button("🚀 Upload & Scan", type="primary"):
            with st.spinner("Uploading and Analyzing..."):
                try:
                    # A. UPLOAD FILE
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/vnd.android.package-archive")}
                    upload_resp = requests.post(f"{BACKEND_URL}/upload/", files=files)
                    
                    if upload_resp.status_code == 200:
                        file_data = upload_resp.json()
                        file_path = file_data["file_path"]
                        
                        # B. ANALYZE FILE
                        analyze_resp = requests.post(f"{BACKEND_URL}/analyze/", json={"file_path": file_path})
                        
                        if analyze_resp.status_code == 200:
                            report = analyze_resp.json()
                            st.session_state["report"] = report  # Save to state
                        else:
                            st.error(f"Analysis failed: {analyze_resp.text}")
                    else:
                        st.error(f"Upload failed: {upload_resp.text}")
                        
                except Exception as e:
                    st.error(f"Connection Error: {e}")

    # 2. RESULTS SECTION
    if "report" in st.session_state:
        report = st.session_state["report"]
        
        st.divider()
        st.subheader("📊 Analysis Results")
        
        # Top Metrics
        m1, m2, m3 = st.columns(3)
        
        # Verdict Color Logic
        verdict = report.get("verdict", "UNKNOWN")
        risk_score = report.get("risk_score", 0)
        color = "green" if risk_score < 40 else ("orange" if risk_score < 70 else "red")
        
        m1.metric(label="Verdict", value=verdict, delta_color="inverse")
        m2.metric(label="Risk Score", value=f"{risk_score}/100")
        m3.metric(label="ML Confidence", value=f"{report.get('ml_result', {}).get('confidence', 0)*100:.1f}%")

        # Visual Risk Bar
        st.progress(min(risk_score, 100))

        # Two Column Layout for Details
        row1_1, row1_2 = st.columns(2)
        
        with row1_1:
            st.write("### 🚨 Dangerous Permissions")
            dang_perms = report.get("dangerous_permissions", [])
            if dang_perms:
                for item in dang_perms:
                    st.warning(f"**{item['permission']}**: {item['description']}")
            else:
                st.success("No dangerous permissions detected!")

        with row1_2:
            st.write("### 🤖 AI Explanation")

            lang_map = {
                "English": "en",
                "Hindi (हिंदी)": "hi",
                "Marathi (मराठी)": "mr",
                "Gujarati (ગુજરાતી)": "gu",
                "Tamil (தமிழ்)": "ta"
            }
            selected_lang = st.selectbox("Select Language", options=list(lang_map.keys()))
            # Ask backend to explain specific permissions
            all_perms = report.get("permissions", [])
            if st.button("Explain Risks (AI)"):
                with st.spinner(f"Generating explanation in {selected_lang}..."):
                    try:
                        expl_resp = requests.post(
                            f"{BACKEND_URL}/explain/",
                            json={
                                "permissions": [d['permission'] for d in dang_perms] if dang_perms else all_perms[:5],
                                "language": selected_lang
                            }
                        )
                        if expl_resp.status_code == 200:
                            explanation = expl_resp.json().get("explanation", "No info.")
                            st.session_state["last_explanation"] = explanation
                            st.session_state["last_lang_code"] = lang_map[selected_lang]
                            st.info(explanation)
                        else:
                            st.error("Failed to fetch explanation.")
                    except:
                        st.warning("Could not fetch explanation.")

            if "last_explanation" in st.session_state:
              st.divider()
              st.write("🔊 **Listen to Explanation**")
              if st.button("Generate Audio"):
                  try:
                      with st.spinner("Converting text to speech..."):
                         tts = gTTS(text=st.session_state["last_explanation"], lang=st.session_state  ["last_lang_code"])
                         audio_fp = io.BytesIO()
                         tts.write_to_fp(audio_fp)
                         st.audio(audio_fp, format="audio/mp3")
                  except Exception as e:
                      st.error(f"Audio Error: {e}")

        # Raw Data Expander
        with st.expander("📂 View Full JSON Report"):
            st.json(report)