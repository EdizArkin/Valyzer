import streamlit as st

# Set Streamlit page configuration
st.set_page_config(
    page_title="Valyzer",
    page_icon="images/Valyzer_Icon1.0.png", #designed icon future
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


st.image("images/Valyzer_Logo1.3.png", width=600)
