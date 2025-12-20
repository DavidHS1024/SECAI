import logging
from fastapi import FastAPI, HTTPException, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any

import services
import ai

# --- CONFIGURACIÓN DE LOGS ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uvicorn")

app = FastAPI()

# --- MIDDLEWARE DE LOGGING (EL CHIVATO) ---
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"👉 INGRESO: {request.method} {request.url}")
    try:
        response = await call_next(request)
        logger.info(f"👈 SALIDA: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"❌ ERROR EN REQUEST: {e}")
        raise e

# --- CORS (PERMISIVO TOTAL) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Acepta todo (localhost, 127.0.0.1, IP local)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MODELOS ---
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

# --- RUTAS ---

@app.get("/")
def read_root():
    return {"status": "online", "system": "SECAI Backend (o3 Enabled)"}

@app.get("/api/socializacion")
def get_comentarios():
    print("📡 GET /api/socializacion")
    return {"comentarios": services.obtener_comentarios()}

@app.post("/api/socializacion/responder")
def post_responder(payload: ReplyPayload):
    if services.agregar_respuesta(payload.padre_id, payload.usuario, payload.texto):
        return {"status": "ok"}
    raise HTTPException(status_code=400, detail="Error al responder")

@app.post("/api/exteriorizacion")
def post_analizar(payload: ExteriorizacionPayload):
    print(f"📥 [PROCESANDO] Análisis de {len(payload.comentarios)} comentarios...")
    try:
        tickets = ai.analizar_exteriorizacion(payload.comentarios)
        print(f"✅ [EXITO] Se generaron {len(tickets)} tickets.")
        return tickets
    except Exception as e:
        print(f"🔥 [CRASH] Error en IA: {str(e)}")
        # Importante: Devolvemos el error como JSON para que el frontend sepa qué pasó
        return JSONResponse(status_code=500, content={"detail": str(e)})

@app.post("/api/investigacion")
async def post_investigar(ticket: Dict[str, Any]):
    print(f"📡 [STREAM] Iniciando investigación para: {ticket.get('titulo', 'Ticket')}")
    generator = ai.investigar_solucion_stream(ticket)
    return StreamingResponse(generator, media_type="application/x-ndjson")

@app.post("/api/combinacion")
def post_generar_contenido(payload: CombinacionPayload):
    return ai.generar_interiorizacion_hibrida(payload.ticket, payload.solucion_detallada)

if __name__ == "__main__":
    import uvicorn
    # host="0.0.0.0" permite conexiones desde cualquier interfaz de red
    uvicorn.run(app, host="0.0.0.0", port=8000)