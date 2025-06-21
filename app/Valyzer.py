import streamlit as st

st.set_page_config(
    page_title="Valyzer",
    page_icon="💡", #designed icon future
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("💡 Valyzer")
st.subheader("Smarter Prices, Sharper Insights")

st.markdown(
    """
    **Valyzer** is an AI-powered dynamic pricing and demand forecasting tool.  
    Choose a page from the sidebar to begin analyzing **daily consumer goods** or **travel pricing**.
    """
)

st.image("images/Valyzer_Logo1.3.png", width=5000)
