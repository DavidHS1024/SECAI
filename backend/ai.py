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
# Usamos gpt-4o para que el bucle sea rápido (10-15s) durante la demo.
MODELO_RAZONAMIENTO = 'gpt-4o' 
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
        completion = client.beta.chat.completions.parse(
            model=MODELO_RAZONAMIENTO,
            messages=[{"role": "user", "content": prompt}],
            response_format=ReporteExteriorizacion,
        )
        return [t.model_dump() for t in completion.choices[0].message.parsed.tickets]
    except Exception as e:
        print(f"❌ Error Fase 2: {e}")
        return []

# --- HELPERS PARA GENERACIÓN DE PROMPTS ---

def _crear_prompt_generacion(ticket, contexto_web):
    return f"""
    Actúa como Staff Engineer.
    PROBLEMA: {ticket['problema']}
    RAZONAMIENTO: {ticket['razonamiento']}
    CONTEXTO WEB: {contexto_web}
    
    TAREA: Diseña una solución técnica definitiva.
    REGLA DE FORMATO: 
    - Markdown limpio, listas, negritas y bloques de código.
    - NO uses encabezados gigantes (#), usa negritas para subtítulos.
    
    FUENTES BIBLIOGRÁFICAS:
    - Incluye SOLO links reales del contexto web. Si no hay, deja la lista vacía.
    """

def _crear_prompt_auditoria(ticket, solucion_obj):
    return f"""
    Actúa como Auditor CISA/CISSP.
    PROBLEMA: {ticket['problema']}
    SOLUCIÓN: {solucion_obj.model_dump_json()}
    
    CRITERIO (Min 90/100): Penaliza si es vago o inseguro.
    TAREA: Evalúa y da puntaje.
    """

def _crear_prompt_refinamiento(solucion_ant, auditoria):
    return f"""
    Actúa como Tech Lead.
    SITUACIÓN: Rechazada (Score: {auditoria.score}).
    CRÍTICAS: {json.dumps(auditoria.riesgos_detectados)}
    TAREA: Corrige la solución.
    """

# --- GENERADOR MAESTRO CON STREAMING CORREGIDO (\n) ---

def investigar_solucion_stream(ticket: Dict) -> Generator[str, None, None]:
    # IMPORTANTE: El backend debe devolver un generador SINCRONO o ASINCRONO
    # FastAPI maneja ambos, pero aquí usaremos yield estándar.
    
    if not IA_ACTIVA:
        # \n es VITAL para que el frontend detecte el fin del mensaje
        yield json.dumps({"type": "error", "message": "IA Offline"}) + "\n"
        return

    # 1. Búsqueda
    yield json.dumps({"type": "log", "emoji": "🌐", "message": "Iniciando búsqueda en Google...", "level": "info"}) + "\n"
    contexto_web = buscar_en_web(f"solucion tecnica {ticket['problema']} github stackoverflow")
    yield json.dumps({"type": "log", "emoji": "✅", "message": "Contexto web obtenido.", "level": "success"}) + "\n"

    solucion_actual = None
    ultimo_score = 0
    intentos = 0
    MAX_INTENTOS = 2 # Reducimos intentos para agilidad en demo
    SCORE_OBJETIVO = 90
    auditoria_final = None

    try:
        while intentos < MAX_INTENTOS:
            intentos += 1
            yield json.dumps({"type": "log", "emoji": "🔄", "message": f"Ciclo de Ingeniería {intentos}/{MAX_INTENTOS}...", "level": "info"}) + "\n"

            # A. GENERACIÓN / REFINAMIENTO
            if intentos == 1:
                yield json.dumps({"type": "log", "emoji": "🏗️", "message": "Diseñando arquitectura (GPT-4o)...", "level": "warning"}) + "\n"
                
                completion = client.beta.chat.completions.parse(
                    model=MODELO_RAZONAMIENTO,
                    messages=[{"role": "user", "content": _crear_prompt_generacion(ticket, contexto_web)}],
                    response_format=SolucionTecnica,
                )
                solucion_actual = completion.choices[0].message.parsed
                yield json.dumps({"type": "log", "emoji": "📝", "message": "Diseño inicial completado.", "level": "success"}) + "\n"

            else:
                yield json.dumps({"type": "log", "emoji": "🔧", "message": "Aplicando parches de seguridad...", "level": "warning"}) + "\n"
                completion = client.beta.chat.completions.parse(
                    model=MODELO_RAZONAMIENTO,
                    messages=[{"role": "user", "content": _crear_prompt_refinamiento(solucion_actual, auditoria_final)}],
                    response_format=SolucionTecnica,
                )
                solucion_actual = completion.choices[0].message.parsed

            # B. AUDITORÍA
            yield json.dumps({"type": "log", "emoji": "⚖️", "message": "Auditando calidad...", "level": "info"}) + "\n"
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
        # \n CRÍTICO AQUÍ TAMBIÉN
        yield json.dumps({"type": "result", "data": paquete}) + "\n"

    except Exception as e:
        print(f"ERROR: {e}")
        yield json.dumps({"type": "error", "message": str(e)}) + "\n"