import os
import requests
from dotenv import load_dotenv

# Cargar variables de entorno (Asegúrate de agregarlas a tu .env antes)
load_dotenv()

# Si no las has puesto en el .env, puedes pegarlas temporalmente aquí para probar
API_KEY = os.getenv("GOOGLE_SEARCH_KEY") # Tu AIzaSyD...
CX_ID = os.getenv("GOOGLE_SEARCH_CX")    # Tu 017c...

def test_google_search():
    if not API_KEY or not CX_ID:
        print("❌ Error: Faltan las credenciales GOOGLE_SEARCH_KEY o GOOGLE_SEARCH_CX.")
        return

    print(f"🔑 Probando credenciales...")
    print(f"   - Key: {API_KEY[:5]}...{API_KEY[-4:]}")
    print(f"   - CX:  {CX_ID[:5]}...{CX_ID[-3:]}")

    query = "solucion error crash android camera samsung a52 github"
    url = "https://www.googleapis.com/customsearch/v1"
    
    params = {
        "key": API_KEY,
        "cx": CX_ID,
        "q": query,
        "num": 3 # Pedimos solo 3 resultados
    }

    try:
        print("\n🌐 Enviando petición a Google...")
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ ¡ÉXITO! Conexión establecida.\n")
            
            items = data.get("items", [])
            if not items:
                print("⚠️ La búsqueda no devolvió resultados (pero la API funciona).")
            
            for item in items:
                print(f"🔹 Título: {item.get('title')}")
                print(f"   Link:   {item.get('link')}")
                print(f"   Snippet: {item.get('snippet')[:100]}...\n")
                
        else:
            print(f"❌ Error HTTP {response.status_code}:")
            print(response.text)

    except Exception as e:
        print(f"❌ Error de conexión: {str(e)}")

if __name__ == "__main__":
    test_google_search()