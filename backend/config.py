import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# --- API KEYS ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Facebook Graph API
FB_PAGE_ACCESS_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN")
FB_POST_ID = os.getenv("FB_POST_ID")

# Google Programmable Search (Nuevo)
GOOGLE_SEARCH_KEY = os.getenv("GOOGLE_SEARCH_KEY")
GOOGLE_SEARCH_CX = os.getenv("GOOGLE_SEARCH_CX")

# Config de página Streamlit (Legacy)
st.set_page_config(page_title="SECAI", page_icon="🟣", layout="wide")

# Inicializar Cliente OpenAI
if OPENAI_API_KEY:
    client = OpenAI(api_key=OPENAI_API_KEY)
    IA_ACTIVA = True
else:
    client = None
    IA_ACTIVA = False