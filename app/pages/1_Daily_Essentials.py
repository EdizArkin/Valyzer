import streamlit as st

st.title("🛍️ Daily Essentials Price Recommendation")

product_name = st.text_input("Enter a product name (e.g., 'milk', 't-shirt')")

if st.button("Predict Price"):
    # Placeholder for prediction logic
    st.success(f"Predicted optimal price for '{product_name}': ₺42.90")
    st.line_chart([38.0, 40.5, 42.0, 42.9])
