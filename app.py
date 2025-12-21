import streamlit as st
import os

# 1. PAGE CONFIG
st.set_page_config(page_title="AI Marketing Agency", layout="wide")

# 2. SECRETS MANAGEMENT (CRITICAL STEP)
# We set the environment variable *before* importing backend
if "OPENAI_API_KEY" in st.secrets:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
else:
    st.error("⚠️ OpenAI API Key missing! Add it to Streamlit Secrets.")
    st.stop()

# 3. IMPORT LOGIC
from backend import build_marketing_workflow

st.title("🚀 Autonomous AI Marketing Agency")
st.markdown("Multi-Agent System: **Strategist** ➔ **Writer** ➔ **Editor** (with Feedback Loops)")

# 4. SIDEBAR
with st.sidebar:
    st.header("Campaign Inputs")
    query = st.text_input("Product/Topic", "AI-powered Coffee Maker")
    audience = st.text_input("Target Audience", "Busy Tech Professionals")
    tone = st.selectbox("Brand Tone", ["Witty", "Professional", "Urgent", "Luxury"])

# 5. RUN BUTTON
if st.button("▶️ Start Campaign"):
    
    app = build_marketing_workflow()
    
    # Initial State
    initial_state = {
        "user_query": query,
        "target_audience": audience,
        "brand_voice": tone,
        "frequency": "Weekly",
        "date": "2025-12-20",
        "revision_count": 0
    }

    with st.status("🤖 Agency is working...", expanded=True) as status:
        st.write("🔍 Strategist is researching trends...")
        result = app.invoke(initial_state)
        status.update(label="✅ Campaign Finished", state="complete", expanded=False)

    # 6. RESULTS DISPLAY
    
    # Tab 1: Strategy
    st.divider()
    st.subheader("1. 🧠 Strategy Brief")
    with st.expander("Read Full Brief", expanded=False):
        st.markdown(result.get("content_brief", "No brief generated."))

    # Tab 2: Content
    st.subheader("2. 📦 Generated Content")
    content_pack = result.get("generated_content", [])
    
    if content_pack:
        tabs = st.tabs([f"Piece {i+1}" for i in range(len(content_pack))])
        for i, piece in enumerate(content_pack):
            with tabs[i]:
                st.caption(f"Platform: {piece.platform.upper()} | Type: {piece.format_type}")
                st.markdown(f"### {piece.title}")
                st.info(piece.content)
    else:
        st.error("No content was published (rejected by Editor).")

    # Tab 3: Editor Stats
    st.subheader("3. 📊 Quality Report")
    feedback = result.get("editor_feedback", {})
    cols = st.columns(4)
    cols[0].metric("Tone Score", feedback.get("tone_score", 0))
    cols[1].metric("Fact Score", feedback.get("fact_score", 0))
    cols[2].metric("Brand Score", feedback.get("brand_score", 0))
    cols[3].metric("Total", f"{feedback.get('overall_score', 0)}/30")
    
    if "rationale" in feedback:
        st.warning(f"Editor's Final Note: {feedback['rationale']}")
