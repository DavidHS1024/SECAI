from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from fastapi.middleware.cors import CORSMiddleware

# Importamos tu lógica existente (¡Reutilización al 100%!)
from services import obtener_comentarios
from ai import analizar_exteriorizacion, generar_interiorizacion_hibrida

# Inicializamos la App
app = FastAPI(title="Yape Feedback Loop API")

# Configuración de CORS
# Esto es VITAL: Permite que tu Frontend (React) que correrá en el puerto 5173
# pueda hablar con este Backend que correrá en el puerto 8000.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción se pone el dominio real, para dev "*" está bien
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Modelos de Datos (Para validar lo que entra) ---
class ComentariosRequest(BaseModel):
    comentarios: List[str]

# --- Rutas (Endpoints) ---

@app.get("/")
def read_root():
    return {"status": "online", "message": "Bienvenido a la API de Yape Feedback Loop"}

# 1. Endpoint de Socialización
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

# 2. Endpoint de Exteriorización
@app.post("/api/exteriorizacion")
def api_analizar_exteriorizacion(request: ComentariosRequest):
    print("⚡ Procesando insights con IA...")
    try:
        # Tu función de ai.py espera una lista de strings
        propuestas = analizar_exteriorizacion(request.comentarios)
        return propuestas
    except Exception as e:
        print(f"Error IA: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 3. Endpoint de Combinación/Internalización
class AprobacionRequest(BaseModel):
    ticket: Dict[str, Any]
    solucion_detallada: str

@app.post("/api/combinacion")
def api_generar_post(data: AprobacionRequest):
    print("📢 Generando post final...")
    try:
        from ai import generar_interiorizacion_hibrida
        resultado = generar_interiorizacion_hibrida(data.ticket, data.solucion_detallada)
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# Endpoint para la Fase 3 (Investigación)
@app.post("/api/investigacion")
def api_investigar_solucion(ticket: Dict[str, Any]):
    print(f"🔍 Investigando solución para: {ticket.get('titulo')}")
    try:
        # Llamamos a la nueva función de ai.py
        from ai import investigar_solucion_combinacion
        resultado = investigar_solucion_combinacion(ticket)
        return resultado
    except Exception as e:
        print(f"Error Investigando: {e}")
        raise HTTPException(status_code=500, detail=str(e))