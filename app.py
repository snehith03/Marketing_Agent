import streamlit as st
import os
import time

# 1. PAGE CONFIGURATION (Must be first)
st.set_page_config(
    page_title="Nexus AI Agency",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. SECRETS SETUP
if "OPENAI_API_KEY" in st.secrets:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
else:
    st.error("⚠️ API Key missing! Add OPENAI_API_KEY to Streamlit Secrets.")
    st.stop()

# 3. CUSTOM CSS STYLING
# This injects custom HTML/CSS to make the app look "Creative"
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #262730;
        border-right: 1px solid #333;
    }
    
    /* Custom Cards */
    .css-card {
        border-radius: 15px;
        padding: 20px;
        background-color: #1E1E1E;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        margin-bottom: 20px;
        border: 1px solid #333;
    }
    
    /* Gradient Button */
    .stButton>button {
        background: linear-gradient(45deg, #FF4B4B, #FF914D);
        color: white;
        border: none;
        border-radius: 25px;
        height: 50px;
        font-weight: bold;
        font-size: 18px;
        width: 100%;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 20px rgba(255, 75, 75, 0.4);
    }
    
    /* Headers */
    h1, h2, h3 {
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
    }
    h1 {
        background: -webkit-linear-gradient(#eee, #999);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Custom Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #0E1117;
        border-radius: 4px;
        color: #fff;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FF4B4B;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# 4. IMPORT BACKEND
from backend import build_marketing_workflow

# 5. HEADER SECTION
col1, col2 = st.columns([1, 5])
with col1:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712109.png", width=80)
with col2:
    st.title("Nexus AI Agency")
    st.caption("Autonomous Multi-Agent System • Strategist → Writer → Editor Loop")

st.divider()

# 6. SIDEBAR CONTROLS
with st.sidebar:
    st.header("⚙️ Mission Control")
    st.write("Configure your campaign parameters.")
    
    with st.container():
        query = st.text_input("🎯 Core Topic", "Eco-friendly Sneakers")
        audience = st.text_input("👥 Target Audience", "Gen Z Urban Hikers")
        tone = st.select_slider("🗣️ Brand Voice", options=["Strict", "Professional", "Casual", "Edgy", "Chaos Mode"], value="Casual")
        platform_focus = st.multiselect("📱 Platform Focus", ["Twitter", "LinkedIn", "Instagram", "Email"], default=["Twitter", "LinkedIn"])
    
    st.info("💡 **Pro Tip:** Specific audiences yield better viral hooks.")

# 7. MAIN INTERFACE
if st.button("🚀 Launch Campaign Simulation"):
    
    app = build_marketing_workflow()
    
    initial_state = {
        "user_query": query,
        "target_audience": audience,
        "brand_voice": tone,
        "frequency": "Weekly",
        "date": "2025-12-20",
        "revision_count": 0
    }

    # Progressive Loading Bar
    progress_text = "Initializing Agents..."
    my_bar = st.progress(0, text=progress_text)
    
    start_time = time.time()
    
    # Run the Graph
    result = app.invoke(initial_state)
    
    # Simulate loading steps for visual effect
    for percent_complete in range(100):
        time.sleep(0.01)
        my_bar.progress(percent_complete + 1, text="Agents collaborating...")
    my_bar.empty()
    
    duration = round(time.time() - start_time, 2)
    st.success(f"✅ Campaign Generated in {duration}s")

    # --- RESULTS DASHBOARD ---
    
    # Top Row: Strategy & Score
    col_strat, col_score = st.columns([3, 2])
    
    with col_strat:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.subheader("🧠 Strategic Brief")
        with st.expander("📂 View Full Strategy Document", expanded=False):
            st.markdown(result.get("content_brief", "No brief available."))
        st.markdown('</div>', unsafe_allow_html=True)

    with col_score:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.subheader("📊 Quality Gate")
        feedback = result.get("editor_feedback", {})
        
        c1, c2 = st.columns(2)
        c1.metric("Tone Score", f"{feedback.get('tone_score', 0)}/10")
        c2.metric("Brand Score", f"{feedback.get('brand_score', 0)}/10")
        
        final_score = feedback.get('overall_score', 0)
        if final_score > 20:
            st.markdown(f"## ⭐ {final_score}/30")
        else:
            st.markdown(f"## ⚠️ {final_score}/30")
            
        st.caption(f"Verdict: **{result.get('publishing_decision', 'N/A').upper()}**")
        st.markdown('</div>', unsafe_allow_html=True)

    # Content Gallery
    st.markdown("### 📦 Generated Assets")
    content_pack = result.get("generated_content", [])
    
    if content_pack:
        # Create Custom Tabs
        tab_labels = [f"{p.platform.upper()}" for p in content_pack]
        tabs = st.tabs(tab_labels)
        
        for i, piece in enumerate(content_pack):
            with tabs[i]:
                st.markdown('<div class="css-card">', unsafe_allow_html=True)
                st.markdown(f"#### {piece.title}")
                st.caption(f"Format: {piece.format_type} | ID: {i+1}")
                st.markdown("---")
                st.code(piece.content, language="markdown")
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.error("❌ Content was rejected by the Editor Agent. Try adjusting the prompt.")

else:
    # Landing Page State (Before running)
    st.markdown("""
    <div style="text-align: center; padding: 50px;">
        <h2>Ready to disrupt the market?</h2>
        <p style="color: #888;">Configure your campaign on the left and hit Launch.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Mock Data Visuals for "Wow" factor
    c1, c2, c3 = st.columns(3)
    c1.metric("Active Agents", "3", delta="Online")
    c2.metric("Knowledge Base", "Live Web", delta="Tavily API")
    c3.metric("Model", "GPT-4o-Mini", delta="Low Latency")
