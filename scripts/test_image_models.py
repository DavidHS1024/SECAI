import os
import sys
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO

# --- CONFIGURACIÓN DE RUTA ---
script_path = Path(__file__).resolve()
project_root = script_path.parent.parent
env_path = project_root / 'backend' / '.env'
load_dotenv(dotenv_path=env_path)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Los especialistas en imagen de tu lista
CANDIDATOS_IMAGEN = [
    "models/gemini-2.5-flash-image-preview",
    "models/gemini-2.5-flash-image",
    "models/gemini-3-pro-image-preview"
]

print(f"🎨 INICIANDO BÚSQUEDA DE MODELO DE IMAGEN...\n")

for modelo in CANDIDATOS_IMAGEN:
    print(f"👉 Probando: {modelo}...")
    try:
        m = genai.GenerativeModel(modelo)
        # Prompt simple
        response = m.generate_content("An apple on a table")
        
        if response.parts:
            print(f"   ✅ ¡ÉXITO! Este modelo genera imágenes.")
            # Guardamos la prueba
            img_data = response.parts[0].inline_data.data
            Image.open(BytesIO(img_data)).save(f"prueba_{modelo.replace('/','_')}.png")
            print("   💾 Imagen guardada. ¡ÚSALO!")
            break # Si uno funciona, nos detenemos
        else:
            print("   ⚠️ Respondió texto, no imagen.")
            
    except Exception as e:
        if "429" in str(e):
            print("   ❌ Cuota excedida (Bloqueado).")
        elif "404" in str(e):
            print("   👻 No encontrado / Sin acceso.")
        else:
            print(f"   ❌ Error: {str(e)[:100]}...")

print("\n--- FIN DEL DIAGNÓSTICO ---")