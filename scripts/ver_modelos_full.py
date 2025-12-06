import os
import google.generativeai as genai
from dotenv import load_dotenv

# Cargar entorno
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("❌ ERROR: No se encontró GEMINI_API_KEY en .env")
    exit()

genai.configure(api_key=API_KEY)

print("\n--- 💎 LISTA DE MODELOS DISPONIBLES (CUENTA PRO) ---")

try:
    count = 0
    # Iteramos sobre todos los modelos disponibles
    for m in genai.list_models():
        # Filtramos solo los que sirven para generar texto/chat
        if 'generateContent' in m.supported_generation_methods:
            count += 1
            print(f"📍 MODELO #{count}")
            print(f"   ID Técnico: {m.name}")
            
            # Usamos getattr para evitar el error si el campo no existe
            display = getattr(m, 'displayName', 'Sin nombre público')
            print(f"   Nombre: {display}")
            
            limit = getattr(m, 'input_token_limit', 'Desconocido')
            print(f"   Ventana de Contexto: {limit} tokens")
            print("-" * 40)

    if count == 0:
        print("⚠️ No se encontraron modelos con capacidad 'generateContent'.")

except Exception as e:
    print(f"❌ Error fatal conectando a Google AI: {e}")

print("\n--- FIN DEL REPORTE ---")