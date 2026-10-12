import streamlit as st

st.set_page_config(
    page_title="Customer Support AI",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="expanded"
)

with st.sidebar:
    st.title("🎧 Support AI")
    st.markdown("---")
    page = st.radio(
        "Navigate",
        options=["💬 Chat", "📊 Dashboard", "🧪 Scenario Tester", "🗂️ Data Explorer"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.caption("Customer Support Agentic AI System")

if page == "💬 Chat":
    from pages.chat import render
    render()

elif page == "📊 Dashboard":
    from pages.dashboard import render
    render()

elif page == "🧪 Scenario Tester":
    from pages.scenario_tester import render
    render()

elif page == "🗂️ Data Explorer":
    from pages.data_explorer import render
    render()