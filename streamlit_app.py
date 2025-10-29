import streamlit as st
import requests
import datetime

# from exception.exceptions import TradingBotException
import sys

BASE_URL = "https://ai-travel-planner-1-ld5p.onrender.com"  # Backend endpoint

st.set_page_config(
    page_title="🌍 Travel Planner Agentic Application",
    page_icon="🌍",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .hero {
        padding: 20px 0 10px 0;
        text-align: left;
    }
    .hero h1 { font-size:48px; margin:0; }
    .hero p { font-size:18px; color:#AAB0B6; margin-top:6px }
    .card {
        background-color: #0f1720;
        padding: 18px;
        border-radius: 8px;
        box-shadow: 0 4px 20px rgba(2,6,23,0.6);
        color: #e6eef8;
    }
    .center { display:flex; justify-content:center }
    </style>
    <div class="hero">
      <h1>🌍 Travel Planner Agentic Application</h1>
      <p>Tell me where you want to go and I'll generate a full travel plan (itinerary, places, costs, and tips).</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# We remove the initial quick-search button and keep a single polished form below.
# The main interactive input is a centered form that submits to the backend.

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
st.header("How can I help you in planning a trip? Let me know where do you want to visit.")

# Chat input box at bottom
with st.form(key="query_form", clear_on_submit=True):
    user_input = st.text_input("User Input", placeholder="e.g. Plan a trip to Goa for 5 days")
    submit_button = st.form_submit_button("Send")

if submit_button and user_input.strip():
    try:
        # # Show user message
        # Show thinking spinner while backend processes
        with st.spinner("Bot is thinking..."):
            payload = {"question": user_input}
            response = requests.post(f"{BASE_URL}/query", json=payload)

        if response.status_code == 200:
            answer = response.json().get("answer", "No answer returned.")
            
            # Display the AI response in a clean format
            st.markdown(answer)
            
            # Add a download button for the travel plan
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M')
            download_filename = f"travel_plan_{timestamp}.md"
            st.download_button(
                label="📥 Download Travel Plan",
                data=answer,
                file_name=download_filename,
                mime="text/markdown"
            )
        else:
            st.error(" Bot failed to respond: " + response.text)

    except Exception as e:
        raise Exception(f"The response failed due to {e}")