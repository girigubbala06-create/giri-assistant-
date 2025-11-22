import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="GIRI: AI Assistant", page_icon="🤖", layout="wide")

# --- CSS STYLING ---
st.markdown("""
    <style>
    .card { background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin-bottom: 15px; border-left: 5px solid #4CAF50; }
    .card h4 { margin: 0; color: #333; }
    .card a { text-decoration: none; color: #4CAF50; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR: SETTINGS ---
with st.sidebar:
    st.header("🤖 GIRI Brain")
    
    # Check if the key is stored in Streamlit Secrets, otherwise ask for it
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
        st.success("API Key loaded securely!")
    else:
        api_key = st.text_input("Enter Gemini API Key", type="password", help="Get your free key from Google AI Studio")
        st.caption("Tip: Add this to Streamlit Secrets to avoid typing it daily.")

# --- FUNCTION: SCRAPE CERTIFICATES ---
@st.cache_data(ttl=3600)
def scrape_certificates():
    url = "https://www.real.discount/store/udemy/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    found_items = []
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        cards = soup.find_all('div', class_='col-xl-4 col-md-6')
        for card in cards[:20]: # Check top 20
            title_tag = card.find('h3')
            link_tag = card.find('a')
            if title_tag and link_tag:
                found_items.append({"title": title_tag.get_text(strip=True), "link": link_tag['href']})
    except Exception as e:
        st.error(f"Error scraping: {e}")
    return found_items

# --- MAIN APP UI ---
st.title("🤖 GIRI: The AI Assistant")

# Create two tabs: One for Certificates, One for Chatting
tab1, tab2 = st.tabs(["🎓 Free Certificates", "💬 Chat with GIRI"])

# --- TAB 1: CERTIFICATE FINDER ---
with tab1:
    st.subheader("Find 100% OFF Courses")
    search_query = st.text_input("Filter Certificates (e.g., Python, Marketing)", "")
    
    if st.button("🔄 Refresh List"):
        st.cache_data.clear()

    data = scrape_certificates()
    filtered_data = [item for item in data if search_query.lower() in item['title'].lower()]

    if filtered_data:
        for item in filtered_data:
            st.markdown(f"""
            <div class="card">
                <h4>{item['title']}</h4>
                <a href="{item['link']}" target="_blank">👉 GRAB FOR FREE</a>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No certificates found. Try a different keyword.")

# --- TAB 2: AI CHATBOT ---
with tab2:
    st.subheader("Ask GIRI Anything")
    
    if not api_key:
        st.warning("⚠️ Please enter your Google Gemini API Key in the Sidebar to start chatting.")
    else:
        # Configure the AI
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-pro")

            # Initialize Chat History
            if "messages" not in st.session_state:
                st.session_state.messages = []

            # Display Chat History
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            # User Input
            if prompt := st.chat_input("Ask about career, skills, or courses..."):
                # Display User Message
                with st.chat_message("user"):
                    st.markdown(prompt)
                st.session_state.messages.append({"role": "user", "content": prompt})

                # Generate AI Response
                with st.chat_message("assistant"):
                    with st.spinner("GIRI is thinking..."):
                        try:
                            response = model.generate_content(prompt)
                            st.markdown(response.text)
                            st.session_state.messages.append({"role": "assistant", "content": response.text})
                        except Exception as e:
                            st.error(f"An error occurred: {e}")
        except Exception as e:
            st.error(f"Invalid API Key or Connection Error: {e}")
