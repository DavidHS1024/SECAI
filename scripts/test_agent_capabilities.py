import os
import google.generativeai as genai
from dotenv import load_dotenv
from google.ai.generativelanguage_v1beta.types import content

# Cargar entorno
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

# Colores para la consola
GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
RESET = "\033[0m"

def print_status(test_name, success, message=""):
    status = f"{GREEN}✅ PASÓ{RESET}" if success else f"{RED}❌ FALLÓ{RESET}"
    print(f"[{test_name}]: {status} {message}")

if not API_KEY:
    print(f"{RED}ERROR: No se encontró GEMINI_API_KEY en .env{RESET}")
    exit()

genai.configure(api_key=API_KEY)

print(f"\n{CYAN}--- INICIANDO DIAGNÓSTICO DE AGENTE SECAI ---{RESET}\n")

# ---------------------------------------------------------
# TEST 1: LISTAR MODELOS DISPONIBLES
# ---------------------------------------------------------
print(f"{CYAN}1. Verificando modelos disponibles...{RESET}")
try:
    models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    
    # Buscamos los modelos clave
    has_1_5 = any('gemini-1.5-flash' in m for m in models)
    has_2_0 = any('gemini-2.0-flash' in m for m in models)
    
    print_status("Acceso a Gemini 1.5 Flash", has_1_5)
    print_status("Acceso a Gemini 2.0 Flash (Exp)", has_2_0)
    
    if has_2_0:
        MODEL_TO_USE = 'gemini-2.0-flash-exp'
    elif has_1_5:
        MODEL_TO_USE = 'gemini-1.5-flash'
    else:
        MODEL_TO_USE = models[0] # Fallback
        
    print(f"   -> Modelo seleccionado para pruebas: {CYAN}{MODEL_TO_USE}{RESET}")

except Exception as e:
    print_status("Listar Modelos", False, str(e))
    exit()

# ---------------------------------------------------------
# TEST 2: GENERACIÓN BÁSICA
# ---------------------------------------------------------
print(f"\n{CYAN}2. Probando latencia y respuesta simple...{RESET}")
try:
    model = genai.GenerativeModel(MODEL_TO_USE)
    response = model.generate_content("Di 'Sistemas SECAI en línea' si me escuchas.")
    
    if "SECAI" in response.text:
        print_status("Respuesta Básica", True, f"Latency ok. Resp: {response.text.strip()}")
    else:
        print_status("Respuesta Básica", False, f"Respuesta inesperada: {response.text}")
except Exception as e:
    print_status("Respuesta Básica", False, str(e))

# ---------------------------------------------------------
# TEST 3: FUNCTION CALLING (El Cerebro del Agente)
# ---------------------------------------------------------
print(f"\n{CYAN}3. Probando CAPACIDAD DE AGENTE (Function Calling)...{RESET}")
# Definimos una herramienta falsa para ver si la IA intenta usarla
tools_schema = {
    "function_declarations": [
        {
            "name": "buscar_en_sbs",
            "description": "Busca normativas en la Superintendencia de Banca y Seguros.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "El tema a buscar, ej: 'biometría'"
                    }
                },
                "required": ["query"]
            }
        }
    ]
}

try:
    model_agent = genai.GenerativeModel(MODEL_TO_USE, tools=[tools_schema])
    chat = model_agent.start_chat()
    
    # Le pedimos algo que REQUIERA la herramienta
    response = chat.send_message("Necesito saber qué dice la SBS sobre la autenticación biométrica para apps móviles.")
    
    # Verificamos si la IA decidió llamar a la función
    if response.candidates[0].content.parts[0].function_call:
        fc = response.candidates[0].content.parts[0].function_call
        print_status("Detección de Intención", True)
        print(f"   -> La IA decidió ejecutar: {CYAN}{fc.name}('{fc.args['query']}'){RESET}")
        print(f"   -> {GREEN}¡CONCLUSIÓN: Tu API soporta Agentes ReAct!{RESET}")
    else:
        print_status("Detección de Intención", False, "La IA respondió con texto en lugar de usar la herramienta.")
        print(f"   -> Respuesta: {response.text}")

except Exception as e:
    print_status("Test de Agente", False, str(e))

print(f"\n{CYAN}--- FIN DEL DIAGNÓSTICO ---{RESET}")