from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

# Importamos nuestros servicios y cerebro IA
import services
import ai

app = FastAPI()

# Configuración CORS (Permitir conexión desde el Frontend React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], # Puerto por defecto de Vite
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MODELOS DE ENTRADA (Input DTOs) ---
class ReplyPayload(BaseModel):
    padre_id: str
    usuario: str
    texto: str

class ExteriorizacionPayload(BaseModel):
    comentarios: List[str]

class CombinacionPayload(BaseModel):
    ticket: Dict[str, Any]
    solucion_detallada: Any # Puede ser dict o str

class AuditoriaPayload(BaseModel):
    ticket: Dict[str, Any]
    solucion_propuesta: Any

# --- RUTAS DE LA API ---

@app.get("/")
def read_root():
    return {"status": "online", "system": "SECAI Backend (o3 Enabled)"}

# 1. SOCIALIZACIÓN
@app.get("/api/socializacion")
def get_comentarios():
    comentarios = services.obtener_comentarios()
    return {"comentarios": comentarios}

@app.post("/api/socializacion/responder")
def post_responder(payload: ReplyPayload):
    exito = services.agregar_respuesta(payload.padre_id, payload.usuario, payload.texto)
    if not exito:
        raise HTTPException(status_code=400, detail="No se pudo enviar la respuesta (Error ID o API)")
    return {"status": "ok"}

# 2. EXTERIORIZACIÓN (Análisis de Patrones)
@app.post("/api/exteriorizacion")
def post_analizar(payload: ExteriorizacionPayload):
    tickets = ai.analizar_exteriorizacion(payload.comentarios)
    return tickets

# 3. COMBINACIÓN (Investigación - AHORA CON STREAMING)
@app.post("/api/investigacion")
async def post_investigar(ticket: Dict[str, Any]):
    """
    Endpoint de Streaming.
    No devuelve un JSON estático, sino un flujo de eventos (NDJSON).
    """
    print(f"📡 Solicitud de investigación recibida para: {ticket.get('titulo', 'Ticket')}")
    
    # Generador que conecta con el yield de ai.py
    generator = ai.investigar_solucion_stream(ticket)
    
    # StreamingResponse mantiene la conexión abierta
    return StreamingResponse(generator, media_type="application/x-ndjson")

# 3B. AUDITORÍA (Manual / Legacy)
@app.post("/api/auditoria")
def post_auditar(payload: AuditoriaPayload):
    # Este endpoint se mantiene por si queremos re-auditar manualmente,
    # aunque el flujo principal ya trae la auditoría integrada.
    resultado = ai.auditar_solucion_tecnica(payload.ticket, payload.solucion_propuesta)
    return resultado

# 3C. REFINAMIENTO (Manual / Legacy)
@app.post("/api/refinar")
def post_refinar(ticket: Dict[str, Any] = Body(...), solucion_anterior: Any = Body(...), reporte_auditoria: Any = Body(...)):
    # Helper para convertir inputs si vienen anidados
    resultado = ai.refinar_solucion_tecnica(ticket, solucion_anterior, reporte_auditoria)
    return resultado

# 4. INTERNALIZACIÓN (Generación de Post)
@app.post("/api/combinacion")
def post_generar_contenido(payload: CombinacionPayload):
    resultado = ai.generar_interiorizacion_hibrida(payload.ticket, payload.solucion_detallada)
    return resultado

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)