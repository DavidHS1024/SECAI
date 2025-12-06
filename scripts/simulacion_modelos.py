import os
import time
import google.generativeai as genai
from dotenv import load_dotenv
from google.api_core import exceptions

# --- CONFIGURACIÓN ---
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Colores para el reporte
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"

# Los candidatos a "Cerebro de SECAI"
CANDIDATOS = [
    "models/gemini-2.5-flash",       # El favorito (Velocidad + Potencia)
    "models/gemini-2.5-pro",         # El más potente teóricamente
    "models/gemini-2.0-flash-exp",   # El experimental rápido
    "models/gemini-1.5-pro",         # El estándar de oro actual
    "models/gemini-1.5-flash"        # La opción segura (backup)
]

# --- HERRAMIENTA DE PRUEBA ---
# Definimos una herramienta simple para ver si el modelo intenta usarla
def obtener_clima(ciudad: str):
    """Devuelve el clima simulado."""
    return f"El clima en {ciudad} es soleado."

tools_prueba = [obtener_clima]

# --- MOTOR DE SIMULACIÓN ---
def probar_modelo(model_name):
    print(f"\n{CYAN}🤖 Probando candidato: {model_name}{RESET}")
    print("-" * 40)
    
    try:
        # 1. Instanciación
        model = genai.GenerativeModel(model_name, tools=tools_prueba)
        chat = model.start_chat(enable_automatic_function_calling=True)
        
        start_time = time.time()
        
        # 2. El Reto (Prompt que OBLIGA a usar herramienta)
        # No le preguntamos "qué piensas", le pedimos un dato que NO puede saber sin la herramienta.
        response = chat.send_message("¿Cuál es el clima en Ventanilla, Perú hoy?")
        
        duration = time.time() - start_time
        
        # 3. Análisis de la Respuesta
        # Si respondió "soleado" (o similar), es que usó la herramienta internamente.
        # Si dice "no tengo acceso a información en tiempo real", falló como agente.
        
        print(f"   ⏱️ Latencia: {duration:.2f}s")
        print(f"   🗣️ Respuesta: {response.text.strip()}")
        
        # Validación
        if "soleado" in response.text.lower() or "clima" in response.text.lower():
            print(f"   🧠 Capacidad de Agente: {GREEN}CONFIRMADA (Usó la herramienta){RESET}")
            return True
        else:
            print(f"   🧠 Capacidad de Agente: {YELLOW}DUDOSA (Parece que no usó la herramienta){RESET}")
            return False

    except exceptions.ResourceExhausted:
        print(f"   ❌ Estado: {RED}CUOTA EXCEDIDA (429){RESET} - Este modelo tiene límites estrictos.")
        return False
    except exceptions.NotFound:
        print(f"   ❌ Estado: {RED}NO ENCONTRADO (404){RESET} - No tienes acceso real a este modelo.")
        return False
    except Exception as e:
        print(f"   ❌ Error inesperado: {str(e)}")
        return False

# --- EJECUCIÓN ---
print(f"\n{YELLOW}⚡ INICIANDO SIMULACIÓN DE MODELOS SECAI ⚡{RESET}")
print("Objetivo: Encontrar el modelo más capaz que soporte Function Calling sin errores.")

resultados = {}

for m in CANDIDATOS:
    exito = probar_modelo(m)
    resultados[m] = exito
    time.sleep(2) # Pausa de seguridad para no saturar la API

print(f"\n{CYAN}--- VEREDICTO FINAL ---{RESET}")
ganador = None
for modelo, funciona in resultados.items():
    icono = "✅" if funciona else "❌"
    print(f"{icono} {modelo}")
    if funciona and ganador is None:
        ganador = modelo

if ganador:
    print(f"\n🚀 El modelo recomendado para SECAI es: {GREEN}{ganador}{RESET}")
    print("Úsalo en tu archivo backend/ai.py")
else:
    print(f"\n⚠️ Ninguno pasó la prueba perfecta. Revisa los errores.")