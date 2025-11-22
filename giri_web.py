import streamlit as st
import requests
from bs4 import BeautifulSoup
import time

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="GIRI: Certificate Assistant", page_icon="🤖", layout="centered")

# --- CUSTOM CSS FOR STYLING ---
st.markdown("""
    <style>
    .big-font { font-size:20px !important; font-weight: bold; }
    .card { background-color: #f9f9f9; padding: 20px; border-radius: 10px; margin-bottom: 15px; border-left: 5px solid #4CAF50; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
    .card h4 { margin: 0; color: #333; }
    .card a { text-decoration: none; color: #4CAF50; font-weight: bold; }
    .card a:hover { color: #2E7D32; }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.title("🤖 GIRI")
st.caption("Your AI Assistant for Free Certificates & Resources")

# --- SIDEBAR (CONTROLS) ---
with st.sidebar:
    st.header("⚙️ Settings")
    
    # 1. Search Logic
    search_query = st.text_input("Filter by Keyword", placeholder="e.g. Python, AI, Google")
    
    # 2. Refresh Button
    if st.button("🔄 Check for New Certificates"):
        st.session_state.needs_refresh = True

# --- SCRAPING FUNCTION ---
@st.cache_data(ttl=3600) # Cache results for 1 hour to save speed
def scrape_certificates():
    url = "https://www.real.discount/store/udemy/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    found_items = []
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        cards = soup.find_all('div', class_='col-xl-4 col-md-6')

        for card in cards[:20]: # Get top 20
            title_tag = card.find('h3')
            link_tag = card.find('a')
            
            if title_tag and link_tag:
                title = title_tag.get_text(strip=True)
                link = link_tag['href']
                img_tag = card.find('img')
                img_url = img_tag['data-src'] if img_tag and 'data-src' in img_tag.attrs else ""
                
                found_items.append({"title": title, "link": link, "img": img_url})
                
    except Exception as e:
        st.error(f"Error scraping data: {e}")
        
    return found_items

# --- MAIN DISPLAY LOGIC ---
st.subheader("🎓 Available Free Certificates")

# Load data
data = scrape_certificates()

# Filter data based on search
if search_query:
    filtered_data = [item for item in data if search_query.lower() in item['title'].lower()]
else:
    filtered_data = data

# Display Cards
if filtered_data:
    for item in filtered_data:
        st.markdown(f"""
        <div class="card">
            <h4>{item['title']}</h4>
            <p style="font-size: 14px; color: #666;">Source: Real.Discount | 100% OFF</p>
            <a href="{item['link']}" target="_blank">👉 CLAIM CERTIFICATE</a>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("No certificates found matching your keywords.")

# --- FOOTER ---
st.markdown("---")
st.markdown("*Built by GIRI • Updates Daily*")