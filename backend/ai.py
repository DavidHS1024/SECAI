import json
import streamlit as st
import google.generativeai as genai
from config import IA_ACTIVA
from conocimiento_base import CONOCIMIENTO_BASE
from services import mock_data

# Configuramos el modelo estándar
MODEL_ID = 'gemini-2.0-flash-exp' # Usamos la versión experimental más potente

def analizar_exteriorizacion(comentarios):
    """Fase 2: Detectar problemas (Tickets) SIN solución detallada."""
    if not comentarios: return []
    if not IA_ACTIVA: return mock_data()
    
    try:
        model = genai.GenerativeModel(
            MODEL_ID,
            generation_config={"response_mime_type": "application/json"}
        )

        prompt = f"""
        Eres un Arquitecto de Software analizando feedback de Yape.
        CONTEXTO: {CONOCIMIENTO_BASE}
        
        INPUT: {comentarios}
        
        TAREA: 
        1. Identifica HASTA 3 problemas técnicos críticos.
        2. Clasifícalos (Seguridad, Rendimiento, Usabilidad).
        3. Estima Viabilidad y Esfuerzo preliminar.
        
        IMPORTANTE: En el campo "solucion", pon solo una frase corta (ej: "Requiere investigación técnica"). La solución detallada se hará en otra fase.

        OUTPUT JSON:
        [
          {{
            "titulo": "...",
            "tipo": "...",
            "problema": "...",
            "solucion": "Pendiente de investigación técnica...",
            "viabilidad": "Alta|Media|Baja",
            "esfuerzo": "Bajo|Medio|Alto",
            "prioridad": "Alta|Media|Baja"
          }}
        ]
        """
        res = model.generate_content(prompt)
        return json.loads(res.text)
    except Exception as e:
        print(f"Error IA Exteriorización: {e}")
        return []

def investigar_solucion_combinacion(ticket):
    """Fase 3: Agente de Investigación (Simula Navegación Web/Perplexity)."""
    if not IA_ACTIVA: return {"solucion_detallada": "Modo offline", "fuentes": []}

    try:
        model = genai.GenerativeModel(
            MODEL_ID,
            generation_config={"response_mime_type": "application/json"}
        )

        prompt = f"""
        Eres un Ingeniero Principal de Yape realizando una investigación técnica profunda (Combinación).
        
        PROBLEMA A RESOLVER: {ticket['problema']}
        CONTEXTO TÉCNICO: {ticket['tipo']} - Prioridad {ticket['prioridad']}
        
        TAREA:
        Actúa como un motor de búsqueda técnica (estilo Perplexity).
        1. Propón una SOLUCIÓN TÉCNICA DETALLADA (paso a paso).
        2. Cita 3 FUENTES o REFERENCIAS teóricas (pueden ser documentación de AWS, Patrones de Diseño, Normativa SBS, etc.).
        
        OUTPUT JSON:
        {{
            "solucion_detallada": "Texto completo de la solución técnica...",
            "fuentes": [
                {{"titulo": "Nombre de la fuente (ej. AWS Whitepaper)", "url": "url_simulada_o_referencia"}},
                {{"titulo": "...", "url": "..."}}
            ]
        }}
        """
        res = model.generate_content(prompt)
        return json.loads(res.text)
    except Exception as e:
        print(f"Error IA Investigación: {e}")
        return {"solucion_detallada": "Error al investigar.", "fuentes": []}

def generar_interiorizacion_hibrida(ticket, solucion_detallada):
    """Fase 4: Generar Post con la solución ya investigada."""
    try:
        model = genai.GenerativeModel(MODEL_ID, generation_config={"response_mime_type": "application/json"})
        
        # Usamos la solución detallada que investigamos en la fase 3
        solucion_final = solucion_detallada if solucion_detallada else ticket['solucion']

        prompt = f"""
        Rol: Community Manager de Yape.
        Tarea: Comunicar esta mejora técnica a los usuarios en Facebook.
        
        Problema: {ticket['problema']}
        Solución Técnica: {solucion_final}
        
        Output JSON:
        {{ "texto_post": "...", "prompt_imagen_en": "..." }}
        """
        res = model.generate_content(prompt)
        data = json.loads(res.text)
        
        # Generar imagen
        base_prompt = data['prompt_imagen_en']
        style = ", flat vector art, tech illustration, purple and cyan brand colors, minimalist, white background"
        final_prompt = (base_prompt + style).replace(" ", "%20")
        data['url_imagen'] = f"https://image.pollinations.ai/prompt/{final_prompt}?width=800&height=800&nologo=true"
        
        return data
    except Exception as e:
        print(f"Error Generación Post: {e}")
        return {"texto_post": "Error", "url_imagen": None}