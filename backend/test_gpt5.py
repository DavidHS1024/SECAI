import os
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# El modelo que queremos probar (según tu lista)
MODELO_A_PROBAR = "gpt-5.2"

print(f"🚀 Iniciando prueba de conexión con {MODELO_A_PROBAR}...")
start_time = time.time()

try:
    response = client.chat.completions.create(
        model=MODELO_A_PROBAR,
        messages=[
            {"role": "system", "content": "Eres un asistente de arquitectura de software avanzado."},
            {"role": "user", "content": "Hola. 1) Identifícate con tu nombre de modelo. 2) Explica brevemente por qué es importante la 'trazabilidad' en un sistema de feedback loop. Sé conciso."}
        ],
        temperature=0.7
    )
    
    end_time = time.time()
    duration = end_time - start_time
    
    content = response.choices[0].message.content
    tokens_in = response.usage.prompt_tokens
    tokens_out = response.usage.completion_tokens
    
    print("\n✅ ¡ÉXITO! El modelo respondió correctamente.")
    print(f"⏱️ Tiempo de respuesta: {duration:.2f} segundos")
    print(f"🔢 Tokens usados: {tokens_in} entrada / {tokens_out} salida")
    print("-" * 50)
    print(f"🤖 RESPUESTA:\n{content}")
    print("-" * 50)

except Exception as e:
    print(f"\n❌ ERROR CRÍTICO probando {MODELO_A_PROBAR}:")
    print(e)
    print("\n💡 Sugerencia: Si dice 'model not found', verifica si tu API Key tiene permisos para 'gpt-5.2' o si es un modelo en beta privada.")