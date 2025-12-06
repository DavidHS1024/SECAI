import json
import time
import google.generativeai as genai
from duckduckgo_search import DDGS
from config import IA_ACTIVA
from conocimiento_base import CONOCIMIENTO_BASE
from services import mock_data

# ==============================================================================
# CONFIGURACIÓN DE ARQUITECTURA HÍBRIDA
# ==============================================================================
MODELO_CEREBRO = 'models/gemini-3-pro-preview' # Razonamiento profundo (Auditoría)
MODELO_MUSCULO = 'models/gemini-2.5-flash'     # Velocidad (Investigación/Generación)

# ==============================================================================
# HERRAMIENTAS (TOOLS)
# ==============================================================================
def buscar_en_web(consulta: str):
    """Realiza una búsqueda real en internet con DuckDuckGo."""
    print(f"   🕵️‍♂️ [AGENTE] Buscando: '{consulta}'...")
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(consulta, max_results=3))
            if not results: return "Aviso: No se encontraron resultados relevantes."
            return "\n".join([f"- Título: {r['title']}\n  URL: {r['href']}\n  Resumen: {r['body']}" for r in results])
    except Exception as e:
        return f"Error en búsqueda: {str(e)}"

tools_investigacion = [buscar_en_web]

# ==============================================================================
# HELPER: ORQUESTADOR DE IA (FALLBACK)
# ==============================================================================
def llamar_ia_con_fallback(prompt, modelo_primario, tools=None, json_mode=True):
    config = {"response_mime_type": "application/json"} if (json_mode and not tools) else {}
    
    try:
        print(f"   ✨ Intentando con {modelo_primario}...")
        model = genai.GenerativeModel(modelo_primario, tools=tools, generation_config=config)
        if tools:
            chat = model.start_chat(enable_automatic_function_calling=True)
            res = chat.send_message(prompt)
        else:
            res = model.generate_content(prompt)
        return res.text
    except Exception as e:
        print(f"   ⚠️ Falló {modelo_primario} ({str(e)}). Activando Fallback...")
        try:
            model_backup = genai.GenerativeModel(MODELO_MUSCULO, tools=tools, generation_config=config)
            if tools:
                chat = model_backup.start_chat(enable_automatic_function_calling=True)
                res = chat.send_message(prompt)
            else:
                res = model_backup.generate_content(prompt)
            return res.text
        except Exception as e2:
            print(f"   ❌ Error fatal en fallback: {e2}")
            return None

def limpiar_json(texto):
    if not texto: return None
    try:
        return json.loads(texto.replace("```json", "").replace("```", "").strip())
    except: return None

# ==============================================================================
# FASES DEL AGENTE SECAI
# ==============================================================================

def analizar_exteriorizacion(comentarios):
    """Fase 2: Detección de problemas."""
    if not comentarios: return []
    if not IA_ACTIVA: return mock_data()
    
    prompt = f"""
    Rol: Arquitecto de Software Senior en Yape.
    Contexto: {CONOCIMIENTO_BASE}
    Input: {comentarios}
    Tarea: Identifica 3 problemas técnicos críticos.
    Output JSON: [{{ "titulo": "...", "tipo": "...", "problema": "...", "solucion": "Pendiente de investigación...", "viabilidad": "Alta", "esfuerzo": "Alto", "prioridad": "Alta" }}]
    """
    return limpiar_json(llamar_ia_con_fallback(prompt, MODELO_CEREBRO)) or []

def investigar_solucion_combinacion(ticket):
    """Fase 3A: Agente Investigador (ReAct)."""
    if not IA_ACTIVA: return {"solucion_detallada": "Offline", "fuentes": []}
    
    print(f"🤖 [AGENTE INVESTIGADOR] Trabajando en: {ticket['titulo']}")
    prompt = f"""
    Eres un Ingeniero Principal de Yape. Problema: {ticket['problema']} ({ticket['tipo']}).
    INSTRUCCIONES:
    1. USA 'buscar_en_web' para encontrar documentación técnica real.
    2. Redacta solución detallada en MARKDOWN.
    3. Cita fuentes.
    JSON: {{ "solucion_detallada": "Markdown...", "fuentes": [{{ "titulo": "...", "url": "..." }}] }}
    """
    return limpiar_json(llamar_ia_con_fallback(prompt, MODELO_MUSCULO, tools=tools_investigacion)) or {"solucion_detallada": "Error", "fuentes": []}

def auditar_solucion_tecnica(ticket, solucion_propuesta):
    """
    Fase 3B (NUEVO): Agente Auditor de Riesgos.
    Critica la solución propuesta basándose en la normativa y seguridad.
    """
    if not IA_ACTIVA: return {"estado": "APROBADO", "riesgos": [], "score": 100}

    print(f"🛡️ [AGENTE AUDITOR] Analizando riesgos para: {ticket['titulo']}")
    
    prompt = f"""
    Rol: Auditor de Ciberseguridad y Cumplimiento Normativo (SBS Perú) para Yape.
    
    Tus Reglas Maestras (Knowledge Base):
    {CONOCIMIENTO_BASE}
    
    Entrada a Auditar:
    - Problema: {ticket['problema']}
    - Solución Propuesta por el Ingeniero: {solucion_propuesta}
    
    Tarea:
    1. Analiza críticamente la solución. ¿Cumple con la Ley de Protección de Datos? ¿Es segura? ¿Escala bien?
    2. Identifica riesgos ocultos.
    3. Emite un veredicto.
    
    Output JSON:
    {{
        "estado": "APROBADO" | "OBSERVADO" | "RECHAZADO",
        "score": (0-100),
        "analisis_breve": "Resumen ejecutivo de 2 líneas...",
        "riesgos_detectados": ["Riesgo 1...", "Riesgo 2..."],
        "recomendaciones": ["Mejora 1...", "Mejora 2..."]
    }}
    """
    # Usamos el modelo CEREBRO (3.0) para máxima capacidad crítica
    return limpiar_json(llamar_ia_con_fallback(prompt, MODELO_CEREBRO)) or {"estado": "ERROR", "riesgos": ["Fallo en auditoría"]}

def generar_interiorizacion_hibrida(ticket, solucion_detallada):
    """Fase 4: Comunicación y Arte."""
    if not IA_ACTIVA: return {"texto_post": "Offline", "url_imagen": None}
    
    prompt = f"""
    Rol: UX Writer Yape. Problema: {ticket['problema']}. Solución: {solucion_detallada}.
    Genera JSON: {{ "texto_post": "Post...", "prompt_imagen_en": "Abstract tech art..." }}
    Nota Imagen: Estilo abstracto, sin personas, tecnológico, neón.
    """
    data = limpiar_json(llamar_ia_con_fallback(prompt, MODELO_MUSCULO))
    
    if data:
        try:
            import random
            seed = random.randint(0, 9999)
            style = ", abstract minimalist line art, glowing neon purple and cyan strokes on deep black background, technical blueprint, high quality, no faces"
            final_prompt = (data['prompt_imagen_en'] + style).replace(" ", "%20")
            data['url_imagen'] = f"https://image.pollinations.ai/prompt/{final_prompt}?width=800&height=800&nologo=true&seed={seed}"
            return data
        except: pass
    return {"texto_post": "Error contenido.", "url_imagen": None}