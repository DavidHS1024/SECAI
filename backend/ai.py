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
# Modelo "Cerebro": Alta capacidad (Análisis inicial). Si falla, hace fallback.
# Usamos el 3.0 Pro como ideal, pero sabemos que puede fallar por cuota.
MODELO_CEREBRO = 'models/gemini-3-pro-preview'

# Modelo "Músculo": Alta velocidad y estabilidad (Agente y Contenido).
# Este es tu caballo de batalla (2.5 Flash) que confirmamos que funciona bien.
MODELO_MUSCULO = 'models/gemini-2.5-flash' 

# ==============================================================================
# HERRAMIENTAS (TOOLS)
# ==============================================================================

def buscar_en_web(consulta: str):
    """
    Realiza una búsqueda real en internet con DuckDuckGo.
    Args:
        consulta: Término de búsqueda optimizado por la IA.
    Returns:
        Texto formateado con los resultados más relevantes.
    """
    print(f"   🕵️‍♂️ [AGENTE] Buscando: '{consulta}'...")
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(consulta, max_results=3))
            if not results:
                return "Aviso: No se encontraron resultados relevantes."
            
            # Formato optimizado para que la IA lo digiera fácilmente
            return "\n".join([f"- Título: {r['title']}\n  URL: {r['href']}\n  Resumen: {r['body']}" for r in results])
    except Exception as e:
        return f"Error en búsqueda: {str(e)}"

# Registro de herramientas disponibles para el Agente
tools_investigacion = [buscar_en_web]

# ==============================================================================
# HELPER: ORQUESTADOR DE IA (FALLBACK)
# ==============================================================================

def llamar_ia_con_fallback(prompt, modelo_primario, tools=None, json_mode=True):
    """
    Intenta usar el modelo potente. Si falla (429/Error), 
    automáticamente salta al modelo rápido (Músculo).
    
    Maneja inteligentemente el conflicto de 'JSON Mode' vs 'Tools':
    - Si hay tools, DESACTIVA json_mode forzado para evitar error 400.
    """
    # Si usamos tools, desactivamos json_mode nativo porque la API no soporta ambos a la vez
    config = {"response_mime_type": "application/json"} if (json_mode and not tools) else {}
    
    # INTENTO 1: Modelo Principal
    try:
        print(f"   ✨ Intentando con {modelo_primario}...")
        model = genai.GenerativeModel(modelo_primario, tools=tools, generation_config=config)
        
        if tools:
            # Modo Chat automático para uso de herramientas
            chat = model.start_chat(enable_automatic_function_calling=True)
            res = chat.send_message(prompt)
        else:
            # Modo generación simple
            res = model.generate_content(prompt)
        return res.text
        
    except Exception as e:
        print(f"   ⚠️ Falló {modelo_primario} ({str(e)}).")
        print(f"   🔄 Activando FALLBACK a {MODELO_MUSCULO}...")
        
        # INTENTO 2: Modelo de Respaldo (El confiable 2.5 Flash)
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
    """Limpia bloques de código markdown si la IA los genera en modo texto."""
    if not texto: return None
    try:
        # Quitamos ```json al inicio y ``` al final si existen
        return json.loads(texto.replace("```json", "").replace("```", "").strip())
    except:
        print(f"   ❌ Error parseando JSON: {texto[:50]}...")
        return None

# ==============================================================================
# FASES DEL AGENTE SECAI (LÓGICA DE NEGOCIO)
# ==============================================================================

def analizar_exteriorizacion(comentarios):
    """
    Fase 2: Análisis y detección de problemas.
    Usa el modelo 'Cerebro' para clasificar feedback.
    """
    if not comentarios: return []
    if not IA_ACTIVA: return mock_data()
    
    prompt = f"""
    Rol: Arquitecto de Software Senior en Yape.
    Contexto: {CONOCIMIENTO_BASE}
    Input: {comentarios}
    
    Tarea: Identifica 3 problemas técnicos críticos basados en los comentarios.
    IMPORTANTE: En 'solucion', escribe EXACTAMENTE: "Pendiente de investigación por Agente IA".
    
    Output JSON Array: [{{ "titulo": "...", "tipo": "...", "problema": "...", "solucion": "Pendiente de investigación por Agente IA", "viabilidad": "Alta", "esfuerzo": "Alto", "prioridad": "Alta" }}]
    """
    
    return limpiar_json(llamar_ia_con_fallback(prompt, MODELO_CEREBRO)) or []

def investigar_solucion_combinacion(ticket):
    """
    Fase 3: Agente Investigador (ReAct) con acceso a Web.
    Este es el núcleo del agente: Busca -> Razona -> Responde.
    """
    if not IA_ACTIVA: return {"solucion_detallada": "Offline", "fuentes": []}

    print(f"🤖 [AGENTE] Iniciando investigación para: {ticket['titulo']}")
    
    prompt_inicial = f"""
    Eres un Ingeniero Principal de Yape.
    PROBLEMA: {ticket['problema']} ({ticket['tipo']})
    
    INSTRUCCIONES ESTRICTAS PARA EL AGENTE:
    1. DEBES USAR la herramienta 'buscar_en_web' para encontrar documentación técnica real (ej. normativa SBS, docs de Android/AWS, patrones de seguridad).
    2. Redacta una Solución Técnica detallada usando FORMATO MARKDOWN (usa **negritas**, - listas, ### subtítulos) para que sea legible.
    3. Si la búsqueda devuelve URLs, ES OBLIGATORIO incluirlas en el campo 'fuentes'. No inventes links.
    
    FORMATO JSON FINAL (Sin markdown extra):
    {{
        "solucion_detallada": "Explicación técnica con formato Markdown...",
        "fuentes": [
            {{ "titulo": "Título de la web encontrada", "url": "URL exacta" }}
        ]
    }}
    """
    
    # Usamos MODELO_MUSCULO (2.5 Flash) que es rápido para tools y soporta bien el bucle
    texto_resp = llamar_ia_con_fallback(prompt_inicial, MODELO_MUSCULO, tools=tools_investigacion)
    
    resultado = limpiar_json(texto_resp)
    if resultado:
        print("✅ [AGENTE] Investigación terminada.")
        return resultado
    
    return {"solucion_detallada": "Error en investigación.", "fuentes": []}

def auditar_solucion_tecnica(ticket, solucion_propuesta):
    """
    Fase 3B (Auditoría): Analiza riesgos usando el conocimiento base.
    """
    if not IA_ACTIVA: return {"estado": "APROBADO", "riesgos": [], "score": 100}

    print(f"🛡️ [AUDITOR] Analizando riesgos para: {ticket['titulo']}")
    
    prompt = f"""
    Rol: Auditor de Ciberseguridad y Cumplimiento Normativo (SBS Perú) para Yape.
    Base de Conocimiento: {CONOCIMIENTO_BASE}
    
    Entrada:
    - Problema: {ticket['problema']}
    - Solución Propuesta: {solucion_propuesta}
    
    Tarea:
    1. Analiza críticamente la solución contra las normas de seguridad y privacidad.
    2. Identifica riesgos ocultos.
    3. Emite un veredicto y puntaje de seguridad.
    
    Output JSON:
    {{
        "estado": "APROBADO" | "OBSERVADO" | "RECHAZADO",
        "score": (0-100),
        "analisis_breve": "Resumen ejecutivo...",
        "riesgos_detectados": ["Riesgo 1...", "Riesgo 2..."],
        "recomendaciones": ["Mejora 1...", "Mejora 2..."]
    }}
    """
    # Usamos el modelo CEREBRO para máxima capacidad crítica
    return limpiar_json(llamar_ia_con_fallback(prompt, MODELO_CEREBRO)) or {"estado": "ERROR", "riesgos": ["Fallo en auditoría"]}

def generar_interiorizacion_hibrida(ticket, solucion_detallada):
    """
    Fase 4: Comunicación y Arte (Estilo Minimalista/Neon).
    """
    if not IA_ACTIVA: return {"texto_post": "Offline", "url_imagen": None}

    # Usamos la solución detallada si existe
    solucion_final = solucion_detallada if solucion_detallada else ticket['solucion']
    
    prompt = f"""
    Rol: UX Writer Yape.
    Problema: {ticket['problema']}
    Solución: {solucion_final}
    
    Genera JSON: {{ "texto_post": "Post empático...", "prompt_imagen_en": "Abstract tech concept..." }}
    
    NOTA PARA PROMPT IMAGEN: Describe conceptos abstractos (velocidad, seguridad, conexión) sin mencionar personas.
    """
    
    data = limpiar_json(llamar_ia_con_fallback(prompt, MODELO_MUSCULO))
    
    if data:
        try:
            import random
            seed = random.randint(0, 9999)
            
            # --- NUEVO ESTILO MINIMALISTA / NEON / SIN ROSTROS ---
            style = ", abstract minimalist line art, glowing neon purple and cyan strokes on deep black background, technical blueprint aesthetic, vector graphics, high quality, no faces, no text"
            
            final_prompt = (data['prompt_imagen_en'] + style).replace(" ", "%20")
            data['url_imagen'] = f"https://image.pollinations.ai/prompt/{final_prompt}?width=800&height=800&nologo=true&seed={seed}"
            return data
        except: pass
        
    return {"texto_post": "Error generando contenido.", "url_imagen": None}

def refinar_solucion_tecnica(ticket, solucion_anterior, reporte_auditoria):
    """
    Fase 3C (Refinamiento): El Ingeniero corrige la solución basándose en el feedback del Auditor.
    """
    if not IA_ACTIVA: return {"solucion_detallada": "Refinado Offline", "fuentes": []}

    print(f"🔧 [AGENTE INGENIERO] Refinando solución para: {ticket['titulo']}")
    
    prompt = f"""
    Rol: Ingeniero Principal de Yape.
    Tarea: CORREGIR y MEJORAR una solución técnica rechazada o observada por el Auditor.
    
    Contexto:
    - Problema Original: {ticket['problema']}
    - Solución Previa (Deficiente): {solucion_anterior}
    - Feedback del Auditor (CRÍTICO): {json.dumps(reporte_auditoria.get('riesgos_detectados', []))}
    - Recomendaciones: {json.dumps(reporte_auditoria.get('recomendaciones', []))}
    
    Instrucciones:
    1. Reescribe la solución técnica integrando TODAS las recomendaciones del auditor.
    2. Mantén las fuentes originales si son válidas, o busca nuevas si es necesario (simulado aquí).
    3. Asegura que cumple con la normativa SBS mencionada en los riesgos.
    
    Salida JSON:
    {{
        "solucion_detallada": "Nueva versión mejorada en Markdown...",
        "fuentes": [ ... (mismas o nuevas) ... ]
    }}
    """
    
    # Usamos el modelo CEREBRO (3.0) para asegurar que la corrección sea de alta calidad
    return limpiar_json(llamar_ia_con_fallback(prompt, MODELO_CEREBRO)) or {"solucion_detallada": solucion_anterior, "fuentes": []}