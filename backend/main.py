from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from fastapi.middleware.cors import CORSMiddleware

# Importamos la lógica existente y la función de auditoría
from services import obtener_comentarios
from ai import (
    analizar_exteriorizacion, 
    generar_interiorizacion_hibrida, 
    investigar_solucion_combinacion, 
    auditar_solucion_tecnica,
    refinar_solucion_tecnica
)

# Inicializamos la App
app = FastAPI(title="SECAI API - Yape Feedback Loop")

# Configuración de CORS (Permite conexión con React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MODELOS DE DATOS (VALIDACIÓN) ---
class ComentariosRequest(BaseModel):
    comentarios: List[str]

class TicketRequest(BaseModel):
    ticket: Dict[str, Any]
    solucion_detallada: Optional[str] = None

class RefinamientoRequest(BaseModel):
    ticket: Dict[str, Any]
    solucion_anterior: str
    reporte_auditoria: Dict[str, Any]

# --- RUTAS (ENDPOINTS) ---

@app.get("/")
def read_root():
    return {"status": "online", "message": "SECAI API Operativa"}

# 1. Socialización
@app.get("/api/socializacion")
def api_obtener_comentarios():
    print("📡 Recibiendo petición de comentarios...")
    try:
        comentarios = obtener_comentarios()
        return {
            "comentarios": comentarios,
            "cantidad": len(comentarios),
            "status": "success"
        }
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 2. Exteriorización (Análisis Inicial)
@app.post("/api/exteriorizacion")
def api_analizar_exteriorizacion(request: ComentariosRequest):
    print("⚡ Procesando insights con IA...")
    try:
        propuestas = analizar_exteriorizacion(request.comentarios)
        return propuestas
    except Exception as e:
        print(f"Error IA: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 3A. Combinación - Investigación (Agente ReAct)
@app.post("/api/investigacion")
def api_investigar_solucion(ticket: Dict[str, Any]):
    print(f"🔍 Investigando solución para: {ticket.get('titulo')}")
    try:
        resultado = investigar_solucion_combinacion(ticket)
        return resultado
    except Exception as e:
        print(f"Error Investigando: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 3B. Combinación - Auditoría (NUEVO ENDPOINT)
@app.post("/api/auditoria")
def api_auditar(req: TicketRequest):
    print(f"🛡️ Auditando solución para: {req.ticket.get('titulo')}")
    try:
        # Si no hay solución detallada (no se investigó), usamos la preliminar del ticket
        solucion_a_auditar = req.solucion_detallada or req.ticket.get('solucion')
        
        if not solucion_a_auditar:
            raise HTTPException(status_code=400, detail="No se encontró solución para auditar.")
            
        return auditar_solucion_tecnica(req.ticket, solucion_a_auditar)
    except Exception as e:
        print(f"Error Auditoría: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 4. Internalización (Generación Final)
@app.post("/api/combinacion")
def api_generar_post(req: TicketRequest):
    print("📢 Generando contenido de comunicación...")
    try:
        resultado = generar_interiorizacion_hibrida(req.ticket, req.solucion_detallada)
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/api/refinar")
def api_refinar(req: RefinamientoRequest):
    print(f"🔧 Refinando solución para: {req.ticket.get('titulo')}")
    try:
        return refinar_solucion_tecnica(req.ticket, req.solucion_anterior, req.reporte_auditoria)
    except Exception as e:
        print(f"Error Refinamiento: {e}")
        raise HTTPException(status_code=500, detail=str(e))