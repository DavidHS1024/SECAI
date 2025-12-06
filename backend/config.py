import os
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

FB_PAGE_ACCESS_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN")
FB_POST_ID = os.getenv("FB_POST_ID")

# Config de página Streamlit
st.set_page_config(page_title="Yape Feedback Loop", page_icon="🟣", layout="wide")

# Config de Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    IA_ACTIVA = True
else:
    IA_ACTIVA = False
