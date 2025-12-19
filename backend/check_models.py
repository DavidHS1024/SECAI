import os
from openai import OpenAI
from dotenv import load_dotenv

# Cargar variables de entorno (.env)
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("❌ Error: No se encontró OPENAI_API_KEY en el archivo .env")
    exit()

print(f"🔑 Usando API Key: {api_key[:5]}...{api_key[-4:]}")
client = OpenAI(api_key=api_key)

print("\n📡 Consultando modelos disponibles en tu cuenta de OpenAI...\n")

try:
    # Obtener lista de modelos
    models_response = client.models.list()
    all_models = [m.id for m in models_response.data]
    
    # Ordenar alfabéticamente
    all_models.sort()

    # Filtramos los modelos de interés (Ignoramos dall-e, tts, whisper para este check)
    interesantes = [m for m in all_models if "gpt" in m or "o1" in m]
    
    print(f"✅ Se encontraron {len(all_models)} modelos en total.")
    print("--------------------------------------------------")
    print("🧠 MODELOS DE TEXTO/RAZONAMIENTO DISPONIBLES:")
    print("--------------------------------------------------")
    
    for model in interesantes:
        # Destacar los modelos clave
        if model in ["gpt-4o", "gpt-4o-mini", "o1-preview", "o1-mini"]:
            print(f"🌟 {model}  <-- RECOMENDADO / NUEVO")
        else:
            print(f"   {model}")

    print("\n--------------------------------------------------")
    
    # Verificación específica de lo que buscas
    busqueda = ["gpt-5", "gpt-5.2", "o1-preview", "o1-mini"]
    print("🔎 Verificación de modelos avanzados:")
    for b in busqueda:
        found = any(b in m for m in all_models)
        estado = "DISPONIBLE ✅" if found else "NO DISPONIBLE ❌"
        print(f"   - {b}: {estado}")

except Exception as e:
    print(f"❌ Error al conectar con OpenAI: {e}")