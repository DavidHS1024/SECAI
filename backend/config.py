import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# --- CAMBIO A OPENAI ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

FB_PAGE_ACCESS_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN")
FB_POST_ID = os.getenv("FB_POST_ID")

# Config de página Streamlit
st.set_page_config(page_title="Yape Feedback Loop", page_icon="🟣", layout="wide")

# Inicializar Cliente OpenAI
if OPENAI_API_KEY:
    client = OpenAI(api_key=OPENAI_API_KEY)
    IA_ACTIVA = True
else:
    client = None
    IA_ACTIVA = False