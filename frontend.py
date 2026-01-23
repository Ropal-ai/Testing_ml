import time
import streamlit as st
import requests
import io
from gtts import gTTS

# --- CONFIGURATION ---
BACKEND_URL = "https://cyber-guardian-backend.onrender.com"
st.set_page_config(page_title="CyberGuardian APK Analyser", layout="wide", page_icon="🛡️")

# --- WAKE-UP CALL ---
if "backend_awake" not in st.session_state:
    # Create a placeholder to update status messages dynamically
    status_msg = st.empty()
    status_msg.info("⏳ Waking up the security engine... (Render Free Tier may take ~1-2 mins)")

    backend_up = False
    # Try for up to 90 seconds (18 attempts * 5 seconds wait)
    for i in range(18):
        try:
            # Short timeout per attempt to keep the loop moving
            response = requests.get(f"{BACKEND_URL}/", timeout=5)
            if response.status_code == 200:
                backend_up = True
                break
        except requests.exceptions.RequestException:
            # Backend is still sleeping or booting; wait and retry
            time.sleep(5)
            continue

    if backend_up:
        st.session_state["backend_awake"] = True
        status_msg.success("✅ Security Engine Ready!")
        time.sleep(1) # Let the user see the success message
        status_msg.empty() # Remove the message
    else:
        status_msg.error("⚠️ Backend is taking too long.")
        st.markdown(f"**[Click here to wake it up manually]({BACKEND_URL})**", unsafe_allow_html=True)

# --- CUSTOM STYLING ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #007bff; color: white; }
    .stAlert { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- APP HEADER ---
st.title("🛡️ CyberGuardian: APK Risk Analyser")
st.write("Helping you and your elders stay safe from malicious apps and cyber frauds.")

# --- SIDEBAR: FILE UPLOAD ---
with st.sidebar:
    st.header("Upload APK")
    uploaded_file = st.file_uploader("Choose an APK file", type=["apk"])
    st.info("The file will be scanned for dangerous permissions and analyzed by AI.")

# --- MAIN INTERFACE ---
if uploaded_file:
    # 1. SCANNING PROCESS
    with st.spinner("Analyzing APK permissions..."):
        files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
        try:
            response = requests.post(f"{BACKEND_URL}/analyze/", files=files)
            if response.status_code == 200:
                report = response.json()
            else:
                st.error("Failed to analyze the APK. Please check your backend.")
                st.stop()
        except Exception as e:
            st.error(f"Error connecting to backend: {e}")
            st.stop()

    # 2. RESULTS SECTION
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📊 Analysis Report")
        risk_score = report.get("risk_score", 0)
        
        # Risk Meter
        st.metric(label="Risk Probability", value=f"{risk_score}%")
        st.progress(risk_score / 100)
        
        if risk_score > 50:
            st.warning("⚠️ This app seems suspicious. Please read the AI explanation below.")
        else:
            st.success("✅ This app appears relatively safe.")

        # Permission List
        st.write("*Permissions Found:*")
        perms = report.get("permissions", [])
        for p in perms[:10]: # Showing top 10 for cleanliness
            st.code(p, language="text")

    with col2:
        st.subheader("🤖 AI Safety Guide (Elderly Friendly)")
        
        # LANGUAGE SELECTION
        lang_map = {
            "English": "en",
            "Hindi (हिंदी)": "hi",
            "Marathi (मराठी)": "mr",
            "Gujarati (ગુજરાતી)": "gu",
            "Tamil (தமிழ்)": "ta"
        }
        
        selected_lang = st.selectbox(
            "Select Language / भाषा चुनें:", 
            options=list(lang_map.keys())
        )
        
        # AI EXPLANATION BUTTON
        if st.button(f"Explain in {selected_lang}"):
            with st.spinner("AI is thinking..."):
                try:
                    expl_resp = requests.post(
                        f"{BACKEND_URL}/explain/",
                        json={
                            "permissions": perms,
                            "language": selected_lang
                        }
                    )
                    if expl_resp.status_code == 200:
                        explanation = expl_resp.json().get("explanation")
                        st.session_state["last_explanation"] = explanation
                        st.session_state["last_lang_code"] = lang_map[selected_lang]
                    else:
                        st.error("AI service is currently busy.")
                except:
                    st.error("Connection error with the AI module.")

        # SHOW EXPLANATION AND VOICE TOGGLE
        if "last_explanation" in st.session_state:
            st.info(st.session_state["last_explanation"])
            
            st.divider()
            st.write("🔊 *Listen to the Guide (Voice Help)*")
            st.write("Ideal for elders who prefer listening over reading.")
            
            if st.button("▶️ Play Voice Explanation"):
                with st.spinner("Converting text to speech..."):
                    try:
                        tts = gTTS(
                            text=st.session_state["last_explanation"], 
                            lang=st.session_state["last_lang_code"]
                        )
                        audio_fp = io.BytesIO()
                        tts.write_to_fp(audio_fp)
                        st.audio(audio_fp, format="audio/mp3")
                    except Exception as e:
                        st.error("Speech synthesis failed. Please try again.")

else:
    st.image("https://img.icons8.com/clouds/200/000000/shield.png")
    st.info("Please upload an APK file from the sidebar to begin the safety check.")