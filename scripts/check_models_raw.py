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

print("\n--- 🔍 MODELOS DISPONIBLES PARA TU API KEY ---")
print("(Copia el nombre exacto del que quieras usar)\n")

try:
    # Listar todos los modelos
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"🔹 Nombre: {m.name}")
            print(f"   Display: {m.displayName}")
            print(f"   Límite de Tokens (Input): {m.input_token_limit}")
            print("-" * 40)

except Exception as e:
    print(f"❌ Error conectando a Google AI: {e}")

print("\n--- FIN DEL REPORTE ---")