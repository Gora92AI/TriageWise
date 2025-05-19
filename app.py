import streamlit as st
import openai

st.set_page_config(
    page_title="TriageWise: AI Triage Assistant",
    page_icon="🩺",
    layout="centered"
)

# --- Optional custom CSS ---
st.markdown("""
    <style>
        .stApp { background-color: #181e25; }
        h1, h3 { color: #1074be !important;}
        .stButton > button {
            background-color: #1074be;
            color: white;
            font-weight: bold;
            border-radius: 6px;
            padding: 0.5em 1.5em;
            margin: .5em 0;
        }
        .stAlert {
            background-color: #223a50 !important;
            border-color: #1074be !important;
            color: #dbefff !important;
        }
    </style>
    """, unsafe_allow_html=True)

# --- Centered logo ---
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.image("aigrowthlane_logo.jpg", width=180)

# --- Header & subtitle ---
st.markdown(
    "<h1 style='text-align: center; font-weight: bold;'>TriageWise</h1>",
    unsafe_allow_html=True
)
st.markdown(
    "<h3 style='text-align: center; margin-top:0;'>AI Patient Intake & Triage Assistant</h3>",
    unsafe_allow_html=True
)
st.markdown(
    "<div style='text-align:center;color:#8cbfea; font-size:18px; margin-bottom:0.7em;'>"
    "Quickly assess symptoms and get fast triage suggestions.<br>"
    "This tool does <b>not</b> replace medical advice."
    "</div>",
    unsafe_allow_html=True
)

# --- Disclaimer ---
if 'disclaimer_accepted' not in st.session_state:
    st.session_state.disclaimer_accepted = False

if not st.session_state.disclaimer_accepted:
    st.info(
        "🔖 **Disclaimer:** This app is for informational purposes only and does **not** provide medical advice. "
        "If this is a medical emergency, call your local emergency number.",
        icon="⚠️"
    )
    if st.button("Continue"):
        st.session_state.disclaimer_accepted = True
    st.stop()

# --- Intake form ---
with st.form("patient_intake"):
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("**Age**", min_value=0, max_value=120, step=1, help="Enter your age")
        gender = st.selectbox("**Gender**", ["Male", "Female", "Other"])
        severity = st.radio("**Symptom Severity**", ["Mild", "Moderate", "Severe"], horizontal=True)
    with col2:
        duration = st.text_input("**Symptom Duration**", help="e.g. '2 days', 'a week'", max_chars=40)
        conditions = st.text_area("**Existing Medical Conditions**", help="List any ongoing diagnosed conditions", height=80)
    symptoms = st.text_area("**Describe your symptoms**", help="Type e.g. fever, cough, fatigue...", height=80)

    submitted = st.form_submit_button("Get Triage Suggestion", type="primary")

# --- AI triage & summary ---
if submitted:
    if not symptoms.strip():
        st.warning("Please describe your symptoms to get a triage suggestion.")
        st.stop()

    prompt = (
        f"Patient Intake:\n"
        f"- Age: {age}\n- Gender: {gender}\n- Symptoms: {symptoms}\n"
        f"- Severity: {severity}\n- Duration: {duration}\n"
        f"- Existing Conditions: {conditions}\n\n"
        "Based on the above, respond with one of these recommendations: "
        "'Mild symptoms — Home care recommended', "
        "'Possible infection — Seek doctor in 24–48 hrs', or "
        "'Urgent — Visit ER or call provider now', "
        "plus a short, simple explanation."
    )

    with st.spinner("Analyzing your symptoms..."):
        try:
import os
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a medical triage assistant. Respond concisely."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=180
            )
            ai_output = response.choices[0].message.content.strip()

            st.success("✅ **TriageWise Suggestion:**")
            st.markdown(f"<span style='font-size:1.1em; color:#e0f8ff'>{ai_output}</span>", unsafe_allow_html=True)

            st.markdown(
                f"""
                <div style='border:1px solid #27476c; border-radius:8px; padding: 20px; margin-top:15px; background-color: #223a50; color:#e6f4ff'>
                    <b>👤 Age:</b> {age}<br>
                    <b>🚻 Gender:</b> {gender}<br>
                    <b>📝 Symptoms:</b> {symptoms}<br>
                    <b>📈 Severity:</b> {severity}<br>
                    <b>⏱️ Duration:</b> {duration}<br>
                    <b>🏥 Existing Conditions:</b> {conditions if conditions else "None"}<br>
                </div>
                """,
                unsafe_allow_html=True
            )

            summary = (
                f"TriageWise Intake Summary\n"
                f"------------------------\n"
                f"Age: {age}\n"
                f"Gender: {gender}\n"
                f"Symptoms: {symptoms}\n"
                f"Severity: {severity}\n"
                f"Duration: {duration}\n"
                f"Existing conditions: {conditions if conditions else 'None'}\n"
                f"AI Triage Suggestion: {ai_output}"
            )
            st.download_button("Download Summary", summary, file_name="triagewise_summary.txt")

        except Exception as e:
            st.error(f"😥 Something went wrong! Details: {e}")

    st.markdown("---")
    st.caption("🔒 Your information is **not stored** or shared. Powered by OpenAI GPT-4.")
    st.markdown("<center><span style='color:#7b899b;'>TriageWise &copy; 2024 | Powered by AigrowthLane</span></center>", unsafe_allow_html=True)
