import os
import time
import google.generativeai as genai
from dotenv import load_dotenv
from google.api_core import exceptions

# Cargar API Key (Asegúrate de tener tu .env cerca o pega la key directo aquí solo para probar)
load_dotenv(dotenv_path="backend/.env") 
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    # Intenta buscar en la carpeta actual si no está en backend
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=api_key)

# Los modelos más interesantes de tu lista VIP
EXOTIC_MODELS = [
    "models/gemini-3-pro-preview",       # 🤯 LA JOYA (Gemini 3)
    "models/gemini-2.0-pro-exp-02-05",   # El Pro más nuevo
    "models/gemini-2.5-flash-lite",      # Versión ligera del 2.5
    "models/gemma-3-27b-it",             # Modelo abierto gigante (Gemma 3)
    "models/gemini-robotics-er-1.5-preview" # ¿Robótica? Curioso ver si responde texto
]

print("\n--- 🧪 TEST DE MODELOS EXÓTICOS SECAI ---")

for model_name in EXOTIC_MODELS:
    print(f"\n👉 Probando: {model_name}...")
    try:
        model = genai.GenerativeModel(model_name)
        start = time.time()
        
        # Prompt simple para verificar vida
        response = model.generate_content("Responde solo con la palabra: FUNCIONO")
        
        latency = time.time() - start
        print(f"   ✅ ¡VIVO! Latencia: {latency:.2f}s")
        print(f"   🗣️ Dijo: {response.text.strip()}")
        
    except exceptions.ResourceExhausted:
        print("   UwU Cuota excedida (Límite muy estricto o modelo saturado).")
    except exceptions.NotFound:
        print("   👻 Fantasma (El nombre existe pero no tienes acceso real).")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    time.sleep(1) # Respetar límites

print("\n--- FIN DEL EXPERIMENTO ---")