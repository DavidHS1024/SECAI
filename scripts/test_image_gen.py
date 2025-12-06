import os
import sys
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO

# --- CONFIGURACIÓN DE RUTA SEGURA ---
# Obtenemos la ruta de ESTE script y retrocedemos para buscar 'backend/.env'
script_path = Path(__file__).resolve()
project_root = script_path.parent.parent  # Subimos de 'scripts' a 'SECAI'
env_path = project_root / 'backend' / '.env'

print(f"📂 Buscando llaves en: {env_path}")

# Cargamos explícitamente desde esa ruta
load_dotenv(dotenv_path=env_path)
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ ERROR CRÍTICO: No se pudo leer GEMINI_API_KEY.")
    print("   Asegúrate de que el archivo .env existe en la carpeta 'backend'.")
    sys.exit(1)

genai.configure(api_key=api_key)

# ... (El resto de tu código sigue igual desde aquí) ...
MODELO_IMAGEN = 'models/gemini-2.0-flash-exp' # Ojo: A veces Image Gen está integrado en el modelo principal
# Intenta primero con el modelo que salió en tu lista:
# MODELO_IMAGEN = 'models/gemini-2.0-flash-exp-image-generation' 

print(f"🎨 Probando generación con: {MODELO_IMAGEN}...")

try:
    # Nota: La sintaxis para imágenes a veces cambia según la versión de la librería.
    # Esta es la estándar para modelos Imagen en Gemini.
    model = genai.GenerativeModel(MODELO_IMAGEN)
    
    prompt = "A futuristic cyberpunk city with neon lights, purple and cyan color palette, high quality, digital art"
    
    # Intentamos generar
    response = model.generate_content(prompt)
    
    # Verificar si hay partes (imágenes)
    if response.parts:
        print("✅ ¡Éxito! Imagen generada.")
        
        # Guardar la primera imagen para verla
        img_data = response.parts[0].inline_data.data
        img = Image.open(BytesIO(img_data))
        img.save("prueba_imagen_gemini.png")
        print("💾 Guardada como 'prueba_imagen_gemini.png'. ¡Revísala!")
    else:
        print("⚠️ La respuesta no contiene imágenes. Texto recibido:", response.text)

except Exception as e:
    print(f"❌ Error: {str(e)}")
    print("\n💡 NOTA: Si da error 404 o método no soportado, es posible que este modelo")
    print("requiera un método diferente (como imagen.generate_images) o no esté activo en tu región.")