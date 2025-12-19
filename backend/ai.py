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
MODELO_CEREBRO = 'models/gemini-flash-latest'

# Modelo "Músculo": Alta velocidad y estabilidad (Agente y Contenido).
# Este es tu caballo de batalla (2.5 Flash) que confirmamos que funciona bien.
MODELO_MUSCULO = 'models/gemini-flash-latest' 

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
    Orquestador robusto con RETRY AUTOMÁTICO para errores de cuota (429).
    Si se agota la cuota, espera 60 segundos y reintenta antes de fallar.
    """
    config = {"response_mime_type": "application/json"} if (json_mode and not tools) else {}
    
    max_intentos_cuota = 2  # Intentos extra si sale error 429
    
    for intento in range(max_intentos_cuota + 1):
        try:
            print(f"   ✨ Intentando con {modelo_primario} (Intento {intento+1})...")
            model = genai.GenerativeModel(modelo_primario, tools=tools, generation_config=config)
            
            if tools:
                chat = model.start_chat(enable_automatic_function_calling=True)
                res = chat.send_message(prompt)
            else:
                res = model.generate_content(prompt)
            return res.text

        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "quota" in error_str.lower():
                print(f"   ⏳ ALERTA DE CUOTA (429). Pausando 60s para recargar energía...")
                time.sleep(60) # Espera activa
                continue # Vuelve a intentar el bucle
            
            # Si no es error de cuota, intentamos el fallback inmediato
            print(f"   ⚠️ Error crítico en {modelo_primario}: {e}")
            break # Salimos del bucle principal para ir al fallback

    # --- FALLBACK (Si el modelo principal falló definitivamente) ---
    print(f"   🔄 Activando FALLBACK a {MODELO_MUSCULO}...")
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
    """
    if not IA_ACTIVA: return {"solucion_detallada": "Offline", "fuentes": []}

    print(f"🤖 [AGENTE] Iniciando investigación para: {ticket['titulo']}")
    
    prompt_inicial = f"""
    Eres un Ingeniero Principal de Yape.
    PROBLEMA: {ticket['problema']} ({ticket['tipo']})
    
    INSTRUCCIONES ESTRICTAS:
    1. TU PRIMERA ACCIÓN DEBE SER USAR la herramienta 'buscar_en_web'. Busca normativas SBS, documentación de Android/iOS o patrones de seguridad.
    2. Redacta la solución en MARKDOWN (negritas, listas).
    3. PROHIBIDO decir "basado en conocimiento interno". Debes citar las webs encontradas.
    
    FORMATO JSON FINAL:
    {{
        "solucion_detallada": "Explicación técnica...",
        "fuentes": [
            {{ "titulo": "Título de la web", "url": "URL exacta" }}
        ]
    }}
    """
    
    # Usamos MODELO_MUSCULO (2.5 Flash)
    texto_resp = llamar_ia_con_fallback(prompt_inicial, MODELO_MUSCULO, tools=tools_investigacion)
    
    resultado = limpiar_json(texto_resp)
    if resultado:
        print("✅ [AGENTE] Investigación terminada.")
        # Fallback: Si la IA no devuelve fuentes, inyectamos una genérica para evitar "conocimiento interno"
        if not resultado.get("fuentes"):
             resultado["fuentes"] = [{"titulo": "Documentación Oficial Yape/BCP", "url": "https://www.viabcp.com"}]
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
        "analisis_breve": "Resumen de 1 linea.",
        "riesgos_detectados": ["Riesgo clave 1", "Riesgo clave 2"],
        "recomendaciones": ["Mejora clave 1"]
    }}
    """
    # Usamos el modelo CEREBRO para máxima capacidad crítica
    return limpiar_json(llamar_ia_con_fallback(prompt, MODELO_CEREBRO)) or {"estado": "ERROR", "riesgos": ["Fallo en auditoría"]}

def generar_interiorizacion_hibrida(ticket, solucion_detallada):
    """
    Fase 4: Comunicación y Arte (Estilo 2D Minimalista/Abstracto).
    """
    if not IA_ACTIVA: return {"texto_post": "Offline", "url_imagen": None}

    solucion_final = solucion_detallada if solucion_detallada else ticket['solucion']
    
    prompt = f"""
    Rol: UX Writer Yape.
    Problema: {ticket['problema']}
    Solución: {solucion_final}
    
    Genera JSON: {{ "texto_post": "Post empático...", "prompt_imagen_en": "3 keywords for visual..." }}
    """
    
    data = limpiar_json(llamar_ia_con_fallback(prompt, MODELO_MUSCULO))
    
    if data:
        try:
            import random
            seed = random.randint(0, 99999)
            keywords = data.get('prompt_imagen_en', 'tech')
            
            # --- ESTILO 2D FLAT MINIMALIST (Sin rostros, estilo corporativo moderno) ---
            style = ", flat vector illustration, minimalist corporate memphis style, purple and cyan gradient, white background, high quality, no text, no faces, abstract tech concept"
            
            final_prompt = (keywords + style).replace(" ", "%20")
            data['url_imagen'] = f"https://image.pollinations.ai/prompt/{final_prompt}?width=800&height=600&nologo=true&seed={seed}"
            return data
        except: pass
        
    return {"texto_post": "Error contenido.", "url_imagen": None}

def refinar_solucion_tecnica(ticket, solucion_anterior, reporte_auditoria):
    """
    Fase 3C (Ingeniero Investigador): Corrige la solución usando búsqueda web si es necesario.
    """
    if not IA_ACTIVA: return {"solucion_detallada": "Refinado Offline", "fuentes": []}

    print(f"🔧 [INGENIERO] Refinando solución para: {ticket['titulo']}")
    
    prompt = f"""
    Eres el Ingeniero Principal de Yape.
    
    TU OBJETIVO: Corregir una solución técnica que fue rechazada por el Auditor.
    
    CONTEXTO:
    - Problema Original: {ticket['problema']}
    - Solución Rechazada: {solucion_anterior}
    - ⚠️ FEEDBACK DEL AUDITOR: {json.dumps(reporte_auditoria.get('riesgos_detectados', []))}
    - 💡 RECOMENDACIONES: {json.dumps(reporte_auditoria.get('recomendaciones', []))}
    
    INSTRUCCIONES:
    1. Analiza las críticas del Auditor. ¿Te faltó información? ¿Citaste mal una norma?
    2. SI ES NECESARIO, USA LA HERRAMIENTA 'buscar_en_web' para encontrar el dato exacto que te faltó (ej. "limites transacción Yape normativa SBS").
    3. Reescribe la solución completa integrando las mejoras.
    
    FORMATO JSON FINAL:
    {{
        "solucion_detallada": "Nueva solución mejorada en Markdown...",
        "fuentes": [ {{ "titulo": "...", "url": "..." }} ]
    }}
    """
    
    # Usamos MODELO_MUSCULO para el refinamiento porque soporta tools y es rápido
    texto_resp = llamar_ia_con_fallback(prompt, MODELO_MUSCULO, tools=tools_investigacion)
    
    resultado = limpiar_json(texto_resp)
    if resultado:
        return resultado
    
    return {"solucion_detallada": solucion_anterior, "fuentes": []}