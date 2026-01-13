import sys
import os
# Add project root to sys.path (Valyzer folder)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from src.config.config import IMG_PATH

# Set Streamlit page configuration
st.set_page_config(
    page_title="Valyzer",
    page_icon=f"{IMG_PATH}Valyzer_Icon1.0.png", #designed icon future
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


st.image(f"{IMG_PATH}Valyzer_Logo1.3.png", width=600)
