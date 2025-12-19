import json
import time
from typing import List, Optional, Dict, Any, Generator
from pydantic import BaseModel, Field
from openai import OpenAI
from duckduckgo_search import DDGS
from config import IA_ACTIVA, client
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
# HERRAMIENTAS BLINDADAS
# ==============================================================================

def buscar_en_web(consulta: str):
    """
    Versión a prueba de fallos. Si DDGS falla, devuelve un contexto simulado
    para no romper el bucle de calidad.
    """
    print(f"   🌐 [SISTEMA] Intentando buscar en web: '{consulta}'...")
    try:
        # Intentamos la búsqueda real con timeout implícito
        with DDGS() as ddgs:
            # max_results bajo para velocidad
            results = list(ddgs.text(consulta, max_results=3))
            
            if not results:
                return "No se encontraron resultados externos. Basar solución en conocimiento interno y estándares OWASP."
            
            return "\n".join([f"- {r['title']}: {r['body']} ({r['href']})" for r in results])
            
    except Exception as e:
        print(f"   ⚠️ [ADVERTENCIA] Falló DuckDuckGo ({str(e)}). Usando conocimiento base.")
        # Fallback para que el agente no se detenga
        return f"Error de conexión a búsqueda externa. Asumir contexto estándar de Android/iOS y Seguridad Bancaria para: {consulta}"

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

# --- FUNCIONES INTERNAS ---

def _generar_solucion_inicial(ticket, contexto_web):
    prompt = f"""
    Actúa como Staff Engineer.
    PROBLEMA: {ticket['problema']}
    RAZONAMIENTO: {ticket['razonamiento']}
    CONTEXTO WEB: {contexto_web}
    
    TAREA: Diseña una solución técnica definitiva.
    
    REGLA DE FORMATO VISUAL:
    - Usa Listas (-) para enumerar.
    - Usa **Negritas** para conceptos clave.
    - Usa Bloques de código (```) obligatorios.
    
    REQUISITOS:
    1. Causa Raíz: Profundidad técnica.
    2. Rollback: Pasos exactos.
    3. Seguridad: Mitigación explícita.
    4. Fuentes: Usa el contexto web provisto.
    """
    completion = client.beta.chat.completions.parse(
        model=MODELO_RAZONAMIENTO,
        messages=[{"role": "user", "content": prompt}],
        response_format=SolucionTecnica,
    )
    return completion.choices[0].message.parsed

def _auditar_internamente(ticket, solucion_obj):
    prompt = f"""
    Actúa como Auditor CISA/CISSP.
    PROBLEMA: {ticket['problema']}
    SOLUCIÓN: {solucion_obj.model_dump_json()}
    
    CRITERIO (Min 90/100):
    - Penaliza (-20) si es puro texto sin código.
    - Penaliza (-20) si falta rollback.
    
    TAREA: Evalúa seguridad y completitud.
    """
    completion = client.beta.chat.completions.parse(
        model=MODELO_RAZONAMIENTO,
        messages=[{"role": "user", "content": prompt}],
        response_format=AuditoriaCalidad,
    )
    return completion.choices[0].message.parsed

def _refinar_solucion(ticket, solucion_anterior_obj, auditoria_obj, contexto_web):
    prompt = f"""
    Actúa como Tech Lead.
    SITUACIÓN: Rechazada (Score: {auditoria_obj.score}).
    CRÍTICAS: {json.dumps(auditoria_obj.riesgos_detectados)}
    
    TAREA: Reescribe la solución corrigiendo fallos.
    MEJORA EL FORMATO: Usa Markdown limpio, listas y código.
    """
    completion = client.beta.chat.completions.parse(
        model=MODELO_RAZONAMIENTO,
        messages=[{"role": "user", "content": prompt}],
        response_format=SolucionTecnica,
    )
    return completion.choices[0].message.parsed

# --- GENERADOR DE STREAMING ---

def investigar_solucion_stream(ticket: Dict) -> Generator[str, None, None]:
    """Generador robusto con manejo de errores en cada paso."""
    if not IA_ACTIVA:
        yield json.dumps({"type": "error", "message": "IA Offline"})
        return

    # 1. Búsqueda de Contexto (Blindada)
    yield json.dumps({"type": "log", "emoji": "🌐", "message": "Analizando contexto técnico...", "level": "info"})
    
    # Pequeña pausa para asegurar que el frontend reciba el primer mensaje antes de bloquearse buscando
    time.sleep(0.1) 
    
    contexto_web = buscar_en_web(f"solucion tecnica {ticket['problema']} github issues")
    
    solucion_actual = None
    ultimo_score = 0
    intentos = 0
    MAX_INTENTOS = 3
    SCORE_OBJETIVO = 90
    auditoria_final = None

    try:
        while intentos < MAX_INTENTOS:
            intentos += 1
            yield json.dumps({"type": "log", "emoji": "🔄", "message": f"Ejecutando Ciclo de Ingeniería {intentos}/{MAX_INTENTOS}...", "level": "info"})

            # A. GENERACIÓN
            if intentos == 1:
                yield json.dumps({"type": "log", "emoji": "🏗️", "message": "Ingeniero: Diseñando arquitectura...", "level": "info"})
                solucion_actual = _generar_solucion_inicial(ticket, contexto_web)
            else:
                yield json.dumps({"type": "log", "emoji": "🔧", "message": "Tech Lead: Refinando solución...", "level": "warning"})
                solucion_actual = _refinar_solucion(ticket, solucion_actual, auditoria_final, contexto_web)

            # B. AUDITORÍA
            yield json.dumps({"type": "log", "emoji": "⚖️", "message": "Auditor: Verificando seguridad...", "level": "info"})
            auditoria_final = _auditar_internamente(ticket, solucion_actual)
            ultimo_score = auditoria_final.score
            
            color = "success" if ultimo_score >= 90 else "warning"
            yield json.dumps({"type": "log", "emoji": "📊", "message": f"Auditoría: {auditoria_final.estado} ({ultimo_score} pts)", "level": color})

            # C. SALIDA
            if ultimo_score >= SCORE_OBJETIVO:
                yield json.dumps({"type": "log", "emoji": "✅", "message": "Estándar de calidad alcanzado.", "level": "success"})
                break
            
            if intentos == MAX_INTENTOS:
                yield json.dumps({"type": "log", "emoji": "⚠️", "message": "Entregando mejor versión disponible.", "level": "warning"})

        # RETORNO FINAL
        if solucion_actual and auditoria_final:
            paquete_final = {
                "investigacion": solucion_actual.model_dump(),
                "auditoria": auditoria_final.model_dump()
            }
            yield json.dumps({"type": "result", "data": paquete_final})
        else:
             yield json.dumps({"type": "error", "message": "No se generó solución válida."})

    except Exception as e:
        print(f"❌ Error CRÍTICO en stream: {e}")
        yield json.dumps({"type": "error", "message": f"Error interno: {str(e)}"})

# Helpers
def limpiar_json(texto):
    try: return json.loads(texto.replace("```json", "").replace("```", "").strip())
    except: return None
    
def generar_interiorizacion_hibrida(ticket, solucion_detallada):
    prompt = f"Rol: UX Writer. Post FB sobre: {ticket['titulo']}. JSON: {{'texto_post': '...', 'prompt_imagen_en': '...'}}"
    try:
        res = client.chat.completions.create(model=MODELO_RAPIDO, messages=[{"role":"user","content":prompt}], response_format={"type":"json_object"}).choices[0].message.content
        return limpiar_json(res)
    except: return {"texto_post": "Error", "url_imagen": None}