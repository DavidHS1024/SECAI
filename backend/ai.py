import json
import streamlit as st
import google.generativeai as genai

from config import IA_ACTIVA
from conocimiento_base import CONOCIMIENTO_BASE
from services import mock_data

def analizar_exteriorizacion(comentarios):
    """Exteriorización: comentarios → tickets técnicos."""
    if not comentarios:
        return []
    if not IA_ACTIVA:
        return mock_data()
    try:
        model = genai.GenerativeModel(
            'gemini-2.5-flash-preview-09-2025',
            generation_config={"response_mime_type": "application/json"}
        )

        prompt = f"""
Eres un arquitecto de software senior de Yape y tu tarea es transformar comentarios de usuarios en tickets técnicos de mejora.

=== CONTEXTO DE NEGOCIO Y REGLAS ===
{CONOCIMIENTO_BASE}

=== ENTRADA ===
Tienes una lista de comentarios reales de usuarios de Yape escritos en español:
{comentarios}

Los comentarios pueden tener errores ortográficos, abreviaturas o frases incompletas.

=== TAREA ===
1. Agrupa los comentarios en HASTA 3 problemas o necesidades principales (pueden ser menos si no hay suficiente información).
2. Para cada problema identificado, genera UNA propuesta de mejora técnica.
3. Cada propuesta debe ser realista y estar alineada con el contexto y las restricciones definidas en CONOCIMIENTO_BASE.
4. Prioriza soluciones incrementales y de tipo “quick win” antes que rediseños completos o cambios muy invasivos.
5. Ten en cuenta usabilidad, rendimiento, seguridad, regulación y simplicidad de la experiencia.

=== FORMATO DE SALIDA (JSON) ===
Devuelve EXCLUSIVAMENTE un array JSON de objetos, sin texto adicional ni explicaciones, con este esquema:

[
  {{
    "titulo": "frase corta y clara en español",
    "tipo": "usabilidad|rendimiento|seguridad|nueva_funcionalidad|soporte|otro",
    "problema": "descripción breve del problema desde la perspectiva del usuario",
    "solucion": "propuesta técnica concreta, escrita en lenguaje claro",
    "viabilidad": "alta|media|baja",
    "esfuerzo": "bajo|medio|alto",
    "prioridad": "alta|media|baja"
  }}
]

Instrucciones importantes:
- No inventes funcionalidades que no estén relacionadas con los comentarios recibidos.
- Si los comentarios son vagos o poco claros, indícalo en el campo "problema" y propone soluciones conservadoras.
- No generes más de 3 objetos en el array.
- La respuesta DEBE ser JSON válido. No incluyas nada fuera del JSON.
"""
        res = model.generate_content(prompt)
        texto_limpio = res.text.replace("```json", "").replace("```", "").strip()
        return json.loads(texto_limpio)
        
    except Exception as e:
        st.error(f"Error IA: {e}")
        return mock_data()

def generar_interiorizacion_hibrida(ticket):
    """Internalización: ticket aprobado → post + prompt de imagen."""
    if not IA_ACTIVA:
        return {"texto_post": "IA no disponible (modo demo).", "url_imagen": None}
    try:
        model_text = genai.GenerativeModel(
            'gemini-2.5-flash-preview-09-2025',
            generation_config={"response_mime_type": "application/json"}
        )

        prompt_text = f"""
Eres parte del equipo de comunicación de Yape. Debes comunicar una mejora en el producto de forma clara, cercana y responsable.

=== CONTEXTO ===
Yape está trabajando en la siguiente mejora:
TÍTULO: {ticket['titulo']}
PROBLEMA (resumen): {ticket['problema']}
SOLUCIÓN PROPUESTA: {ticket['solucion']}

El público objetivo son usuarios peruanos de todo tipo, muchos con baja alfabetización digital.

=== TAREAS ===
1. Escribe un POST DE FACEBOOK en ESPAÑOL, en tono empático y sencillo, máximo 3 párrafos cortos, incluye un pregunta abierta que incentive a los usaurios a responder con sus experiencias relacionadas a aquella funcion, con el objetivo de consegui informacion para iniciar de nuevo el ciclo SECI.
2. Genera un PROMPT VISUAL en INGLÉS para una ilustración vectorial plana (2D flat design),
   sin mencionar la palabra "Yape" ni logos.

=== FORMATO DE SALIDA (JSON) ===
Devuelve EXCLUSIVAMENTE un objeto JSON con este formato:

{{
  "texto_post": "post completo en español",
  "prompt_imagen_en": "A flat vector illustration of ..."
}}
"""
        res_text = model_text.generate_content(prompt_text)
        
        texto_limpio = res_text.text.replace("```json", "").replace("```", "").strip()
        data_text = json.loads(texto_limpio)

        base_prompt = data_text['prompt_imagen_en']
        style_suffix = ", flat vector art, minimalist, corporate tech illustration, purple and cyan brand colors, high quality, white background"
        final_prompt = (base_prompt + style_suffix).replace(" ", "%20")

        image_url = f"https://image.pollinations.ai/prompt/{final_prompt}?width=800&height=800&nologo=true"

        data_text['url_imagen'] = image_url
        data_text['status_img'] = "Generada con IA Híbrida"
        return data_text

    except Exception as e:
        return {"texto_post": f"Error generando post: {e}", "url_imagen": None}