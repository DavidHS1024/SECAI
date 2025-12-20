from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

import services
import ai

app = FastAPI()

# --- CONFIGURACIÓN CORS (MODO PERMISIVO) ---
# Permitimos "*" para evitar problemas entre localhost y 127.0.0.1
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MODELOS DE ENTRADA (DTOs) ---
class ReplyPayload(BaseModel):
    padre_id: str
    usuario: str
    texto: str

class ExteriorizacionPayload(BaseModel):
    comentarios: List[str]

class CombinacionPayload(BaseModel):
    ticket: Dict[str, Any]
    solucion_detallada: Any 

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
    print("📡 GET /api/socializacion solicitado")
    comentarios = services.obtener_comentarios()
    return {"comentarios": comentarios}

@app.post("/api/socializacion/responder")
def post_responder(payload: ReplyPayload):
    exito = services.agregar_respuesta(payload.padre_id, payload.usuario, payload.texto)
    if not exito:
        raise HTTPException(status_code=400, detail="Error enviando respuesta")
    return {"status": "ok"}

# 2. EXTERIORIZACIÓN (El punto donde tenías el error)
@app.post("/api/exteriorizacion")
def post_analizar(payload: ExteriorizacionPayload):
    print(f"📥 [BACKEND] Recibida solicitud de Análisis con {len(payload.comentarios)} comentarios.")
    
    # Llamamos a la lógica que YA PROBASTE que funciona
    try:
        tickets = ai.analizar_exteriorizacion(payload.comentarios)
        print(f"📤 [BACKEND] Análisis completado. Retornando {len(tickets)} tickets.")
        return tickets
    except Exception as e:
        print(f"❌ [BACKEND] Error interno en IA: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# 3. COMBINACIÓN (Investigación + Streaming)
@app.post("/api/investigacion")
async def post_investigar(ticket: Dict[str, Any]):
    print(f"📡 [STREAM] Iniciando investigación para: {ticket.get('titulo', 'Ticket')}")
    generator = ai.investigar_solucion_stream(ticket)
    return StreamingResponse(generator, media_type="application/x-ndjson")

# 3B. AUDITORÍA (Legacy)
@app.post("/api/auditoria")
def post_auditar(payload: AuditoriaPayload):
    return ai.auditar_solucion_tecnica(payload.ticket, payload.solucion_propuesta)

# 3C. REFINAMIENTO (Legacy)
@app.post("/api/refinar")
def post_refinar(ticket: Dict[str, Any] = Body(...), solucion_anterior: Any = Body(...), reporte_auditoria: Any = Body(...)):
    return ai.refinar_solucion_tecnica(ticket, solucion_anterior, reporte_auditoria)

# 4. INTERNALIZACIÓN
@app.post("/api/combinacion")
def post_generar_contenido(payload: CombinacionPayload):
    return ai.generar_interiorizacion_hibrida(payload.ticket, payload.solucion_detallada)

if __name__ == "__main__":
    import uvicorn
    # Importante: host="0.0.0.0" ayuda a evitar problemas de binding local
    uvicorn.run(app, host="0.0.0.0", port=8000)