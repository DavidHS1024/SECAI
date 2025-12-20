import json
import time
import requests
from typing import List, Optional, Dict, Any, Generator
from pydantic import BaseModel, Field
from config import IA_ACTIVA, client, GOOGLE_SEARCH_KEY, GOOGLE_SEARCH_CX
from conocimiento_base import CONOCIMIENTO_BASE
from services import mock_data

# ==============================================================================
# CONFIGURACIÓN DE MODELOS
# ==============================================================================

MODELO_RAZONAMIENTO = 'gpt-5.2'
MODELO_RAPIDO = 'gpt-4o-mini' 

# ==============================================================================
# ESQUEMAS DE DATOS
# ==============================================================================

# FASE 2
class TicketSECI(BaseModel):
    titulo: str
    tipo: str
    problema: str
    solucion: str
    viabilidad: str
    esfuerzo: str
    prioridad: str
    tags: List[str]
    razonamiento: str
    fuentes_ids: List[str]

class ReporteExteriorizacion(BaseModel):
    tickets: List[TicketSECI]

# FASE 3
class Fuente(BaseModel):
    titulo: str
    url: str

class SolucionTecnica(BaseModel):
    analisis_causa_raiz: str = Field(description="Explicación técnica en Markdown. Usa viñetas y negritas.")
    solucion_detallada: str = Field(description="Pasos técnicos y código en Markdown. Usa bloques de código.")
    plan_rollback: str = Field(description="Pasos de reversión enumerados.")
    consideraciones_seguridad: str = Field(description="Lista de riesgos mitigados (OWASP).")
    fuentes_bibliograficas: List[Fuente]

class AuditoriaCalidad(BaseModel):
    estado: str = Field(description="'APROBADO' si score >= 90, sino 'OBSERVADO'")
    score: int = Field(description="Puntaje del 0 al 100.")
    analisis_seguridad: str
    analisis_eficiencia: str
    riesgos_detectados: List[str]
    recomendaciones_mejora: List[str]

# ==============================================================================
# HERRAMIENTAS DE BÚSQUEDA (GOOGLE OFFICIAL)
# ==============================================================================

def buscar_en_web(consulta: str):
    """
    Realiza una búsqueda real usando Google Custom Search API.
    """
    if not GOOGLE_SEARCH_KEY or not GOOGLE_SEARCH_CX:
        return "Búsqueda web no disponible (Faltan API Keys). Usar conocimiento interno."

    print(f"   🌐 [GOOGLE] Buscando: '{consulta}'...")
    
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_SEARCH_KEY,
        "cx": GOOGLE_SEARCH_CX,
        "q": consulta,
        "num": 4 
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            items = data.get("items", [])
            
            if not items:
                return "Google no devolvió resultados. Basar solución en conocimiento experto."
            
            resultados_texto = []
            for item in items:
                titulo = item.get('title', 'Sin título')
                link = item.get('link', '#')
                snippet = item.get('snippet', '').replace('\n', ' ')
                resultados_texto.append(f"- [{titulo}]({link}): {snippet}")
            
            return "\n".join(resultados_texto)
        else:
            return f"Error en búsqueda externa (Code {response.status_code}). Usar conocimiento interno."

    except Exception as e:
        return f"Fallo de red al buscar ({str(e)}). Usar conocimiento interno."

# ==============================================================================
# FASES DEL SISTEMA SECAI
# ==============================================================================

def analizar_exteriorizacion(comentarios_raw):
    """Fase 2: Identificación de Patrones."""
    if not comentarios_raw: return []
    if not IA_ACTIVA: return mock_data()
    
    contexto_input = "\n".join(comentarios_raw)
    prompt = f"""
    Rol: Arquitecto de Software Senior.
    Contexto Base: {CONOCIMIENTO_BASE}
    INPUT: {contexto_input}
    TAREA: Genera tickets técnicos agrupando patrones.
    REGLAS: 'fuentes_ids' exactos, 'tags' técnicos, justificación clara.
    """
    try:
        # Usamos GPT-4o para esta fase (clasificación rápida)
        completion = client.beta.chat.completions.parse(
            model='gpt-4o', 
            messages=[{"role": "user", "content": prompt}],
            response_format=ReporteExteriorizacion,
        )
        return [t.model_dump() for t in completion.choices[0].message.parsed.tickets]
    except Exception as e:
        print(f"❌ Error Fase 2: {e}")
        return []

# --- HELPERS PARA GENERACIÓN DE PROMPTS (MODO DETALLADO) ---

def _crear_prompt_generacion(ticket, contexto_web):
    return f"""
    Actúa como Staff Software Engineer experto en Arquitectura de Alta Disponibilidad y Fintech.
    
    PROBLEMA A RESOLVER: {ticket['problema']}
    RAZONAMIENTO PREVIO: {ticket['razonamiento']}
    CONTEXTO WEB INVESTIGADO: {contexto_web}
    
    TAREA:
    Escribe un Documento de Diseño Técnico (TDD) exhaustivo y detallado para implementar esta solución en Yape.
    NO seas breve. Profundiza en cada sección.
    
    ESTRUCTURA OBLIGATORIA DEL REPORTE (Usa Markdown):
    
    1.  **Análisis de Causa Raíz (RCA) Profundo:**
        * Explica técnicamente por qué ocurre el problema actual.
        * Analiza el impacto en la base de datos y la latencia.
        * Menciona riesgos de seguridad si no se arregla.

    2.  **Solución Técnica Detallada (The "How"):**
        * **Arquitectura:** Describe los microservicios involucrados.
        * **Flujo de Datos:** Paso a paso de la petición (Request/Response).
        * **Cambios en Base de Datos:** Propón esquemas (tablas, índices) o modelos JSON.
        * **Integración:** Cómo se comunica con servicios legacy (si aplica).
        * **Código:** Incluye bloques de código (Python/Node/SQL) reales, extensos y comentados para la lógica core.

    3.  **Plan de Rollback y Contingencia:**
        * Estrategia de despliegue (Canary, Blue/Green).
        * Indicadores (KPIs) de fallo.
        * Script o pasos exactos para revertir el cambio en menos de 5 minutos.

    4.  **Consideraciones de Seguridad (OWASP & Compliance):**
        * Validación de inputs.
        * Manejo de tokens y sesiones.
        * Cumplimiento de normativa SBS (Perú).

    FUENTES:
    - Usa estrictamente los links provistos en el contexto web. Si no hay, cita documentación estándar oficial.
    """

def _crear_prompt_auditoria(ticket, solucion_obj):
    return f"""
    Actúa como Auditor CISA/CISSP Senior.
    PROBLEMA: {ticket['problema']}
    SOLUCIÓN PROPUESTA: {solucion_obj.model_dump_json()}
    
    CRITERIO (Min 90/100): 
    - Penaliza FUERTEMENTE si la solución es superficial o corta.
    - Penaliza si falta código real o pasos de rollback claros.
    
    TAREA: Evalúa críticamente y da un puntaje estricto.
    """

def _crear_prompt_refinamiento(solucion_ant, auditoria):
    return f"""
    Actúa como Tech Lead.
    SITUACIÓN: Solución rechazada (Score: {auditoria.score}).
    CRÍTICAS: {json.dumps(auditoria.riesgos_detectados)}
    
    TAREA: Reescribe la solución corrigiendo los fallos y EXPANDIENDO la explicación técnica.
    """

# --- GENERADOR MAESTRO CON STREAMING CORREGIDO (\n) ---

def investigar_solucion_stream(ticket: Dict) -> Generator[str, None, None]:
    if not IA_ACTIVA:
        yield json.dumps({"type": "error", "message": "IA Offline"}) + "\n"
        return

    # 1. Búsqueda
    yield json.dumps({"type": "log", "emoji": "🌐", "message": "Iniciando búsqueda profunda en Google...", "level": "info"}) + "\n"
    contexto_web = buscar_en_web(f"solucion tecnica {ticket['problema']} github stackoverflow documentation")
    yield json.dumps({"type": "log", "emoji": "✅", "message": "Contexto web obtenido.", "level": "success"}) + "\n"

    solucion_actual = None
    ultimo_score = 0
    intentos = 0
    MAX_INTENTOS = 2 
    SCORE_OBJETIVO = 90
    auditoria_final = None

    try:
        while intentos < MAX_INTENTOS:
            intentos += 1
            yield json.dumps({"type": "log", "emoji": "🔄", "message": f"Ciclo de Ingeniería {intentos}/{MAX_INTENTOS} (GPT-5.2)...", "level": "info"}) + "\n"

            # A. GENERACIÓN / REFINAMIENTO
            if intentos == 1:
                yield json.dumps({"type": "log", "emoji": "🏗️", "message": "Arquitecto Senior diseñando solución detallada...", "level": "warning"}) + "\n"
                
                completion = client.beta.chat.completions.parse(
                    model=MODELO_RAZONAMIENTO,
                    messages=[{"role": "user", "content": _crear_prompt_generacion(ticket, contexto_web)}],
                    response_format=SolucionTecnica,
                )
                solucion_actual = completion.choices[0].message.parsed
                yield json.dumps({"type": "log", "emoji": "📝", "message": "Diseño técnico completado.", "level": "success"}) + "\n"

            else:
                yield json.dumps({"type": "log", "emoji": "🔧", "message": "Aplicando parches y expandiendo documentación...", "level": "warning"}) + "\n"
                completion = client.beta.chat.completions.parse(
                    model=MODELO_RAZONAMIENTO,
                    messages=[{"role": "user", "content": _crear_prompt_refinamiento(solucion_actual, auditoria_final)}],
                    response_format=SolucionTecnica,
                )
                solucion_actual = completion.choices[0].message.parsed

            # B. AUDITORÍA
            yield json.dumps({"type": "log", "emoji": "⚖️", "message": "Auditando calidad y seguridad...", "level": "info"}) + "\n"
            completion = client.beta.chat.completions.parse(
                model=MODELO_RAZONAMIENTO,
                messages=[{"role": "user", "content": _crear_prompt_auditoria(ticket, solucion_actual)}],
                response_format=AuditoriaCalidad,
            )
            auditoria_final = completion.choices[0].message.parsed
            ultimo_score = auditoria_final.score
            
            color = "success" if ultimo_score >= 90 else "warning"
            yield json.dumps({"type": "log", "emoji": "📊", "message": f"Score Auditoría: {ultimo_score}/100", "level": color}) + "\n"

            if ultimo_score >= SCORE_OBJETIVO:
                yield json.dumps({"type": "log", "emoji": "🏆", "message": "Calidad Objetivo Alcanzada.", "level": "success"}) + "\n"
                break

        # RETORNO FINAL
        paquete = {
            "investigacion": solucion_actual.model_dump(),
            "auditoria": auditoria_final.model_dump()
        }
        yield json.dumps({"type": "result", "data": paquete}) + "\n"

    except Exception as e:
        print(f"ERROR: {e}")
        yield json.dumps({"type": "error", "message": str(e)}) + "\n"

# Helpers
def limpiar_json(texto):
    try: return json.loads(texto.replace("```json", "").replace("```", "").strip())
    except: return None
    
def generar_interiorizacion_hibrida(ticket, solucion_detallada):
    print(f"🎨 [DALL-E] Iniciando generación de contenido para: {ticket['titulo']}")
    
    # 1. Redactor UX (Estilo Yape - Prompt Afinado)
    prompt_redaccion = f"""
    Rol: UX Writer experto en banca móvil (estilo Yape).
    Tarea: Redactar un post de Facebook empático y técnico informando la solución de este problema: {ticket['titulo']}.
    
    Salida JSON esperada:
    {{
        "texto_post": "El contenido del post (con emojis, tono cercano pero profesional, invitando al feedback)...",
        "prompt_imagen_en": "Un prompt detallado en INGLÉS para DALL-E 3. Estilo: Ilustración animada 2D de alta calidad (tipo caricatura moderna, flat design pulido), vibrante, amigable, con líneas limpias. Paleta de colores dominante morado y cian intenso (branding Yape). Debe parecer una gráfica oficial de redes sociales de una startup fintech."
    }}
    """
    
    try:
        # Generación de Texto
        completion = client.chat.completions.create(
            model=MODELO_RAPIDO, 
            messages=[{"role":"user","content":prompt_redaccion}], 
            response_format={"type":"json_object"}
        )
        data = json.loads(completion.choices[0].message.content)
        
        url_imagen = None
        
        # 2. Generación de Imagen (DALL-E 3)
        if IA_ACTIVA:
            try:
                print(f"   🖌️ Generando imagen con prompt: {data['prompt_imagen_en'][:50]}...")
                response = client.images.generate(
                    model="dall-e-3",
                    prompt=data['prompt_imagen_en'],
                    size="1024x1024",
                    quality="standard",
                    n=1,
                )
                url_imagen = response.data[0].url
                print("   ✅ Imagen generada exitosamente.")
            except Exception as e_img:
                print(f"   ⚠️ Error generando imagen: {e_img}")
                url_imagen = "https://placehold.co/600x400?text=Error+Generando+Imagen"

        return {
            "texto_post": data.get("texto_post"), 
            "url_imagen": url_imagen
        }

    except Exception as e:
        print(f"❌ Error CRÍTICO en Generación de Contenido: {e}")
        return {"texto_post": f"Error generando contenido: {str(e)}", "url_imagen": None}