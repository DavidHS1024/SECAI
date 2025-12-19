import time
import requests
import random
from config import FB_POST_ID, FB_PAGE_ACCESS_TOKEN

# ==============================================================================
# DATA SIMULADA (FALLBACK)
# ==============================================================================
MOCK_SOCIAL_CONVERSATIONS = [
    {
        "id": "c1",
        "user": "Carlos M.",
        "text": "La nueva actualización está fatal 😡. Cada vez que intento escanear un QR se cierra la app.",
        "likes": 45,
        "replies": [
            {
                "id": "c1_r1",
                "user": "Soporte Yape",
                "text": "Hola Carlos, lamentamos el inconveniente. Por favor intenta borrar caché.",
                "likes": 5
            }
        ]
    },
    {
        "id": "c2",
        "user": "Luisa Fernanda",
        "text": "¿Para cuándo el modo oscuro? 🌙 Mis ojos sufren en la noche.",
        "likes": 120,
        "replies": []
    }
]

# ==============================================================================
# INTEGRACIÓN FACEBOOK GRAPH API
# ==============================================================================

def mapear_comentario_fb(fb_comment):
    """Convierte el formato crudo de Facebook al formato de nuestra App."""
    replies = []
    
    # Procesar respuestas anidadas si existen
    if 'comments' in fb_comment and 'data' in fb_comment['comments']:
        for reply in fb_comment['comments']['data']:
            replies.append({
                "id": reply.get('id'),
                "user": reply.get('from', {}).get('name', 'Usuario Desconocido'),
                "text": reply.get('message', ''),
                "likes": reply.get('like_count', 0)
            })

    return {
        "id": fb_comment.get('id'),
        "user": fb_comment.get('from', {}).get('name', 'Usuario Anónimo'),
        "text": fb_comment.get('message', ''),
        "likes": fb_comment.get('like_count', 0),
        "replies": replies
    }

def obtener_comentarios_reales():
    """Consulta la API real de Facebook."""
    if not FB_PAGE_ACCESS_TOKEN or not FB_POST_ID:
        print("⚠️ Faltan credenciales en .env (FB_PAGE_ACCESS_TOKEN o FB_POST_ID)")
        return None

    print(f"🌐 Conectando a Facebook Graph API para el post: {FB_POST_ID}...")
    
    # CAMBIO 1: Agregamos 'parent' a la solicitud para poder detectar si es respuesta
    campos = "id,from,message,like_count,created_time,parent,comments.limit(50){id,from,message,like_count,created_time}"
    url = f"https://graph.facebook.com/v18.0/{FB_POST_ID}/comments"
    
    params = {
        "access_token": FB_PAGE_ACCESS_TOKEN,
        "fields": campos,
        "limit": 50,
        "filter": "stream" 
    }

    try:
        res = requests.get(url, params=params, timeout=10)
        res.raise_for_status()
        data = res.json()
        
        # CAMBIO 2: Filtramos. Solo procesamos comentarios que NO tengan campo 'parent'.
        # Las respuestas (hijos) ya vendrán dentro del campo 'comments' de los padres gracias a la query.
        comentarios_procesados = [
            mapear_comentario_fb(c) 
            for c in data.get('data', []) 
            if 'parent' not in c
        ]
        
        print(f"✅ Éxito: {len(comentarios_procesados)} hilos principales descargados.")
        return comentarios_procesados

    except Exception as e:
        print(f"❌ Error conectando con Facebook: {e}")
        return None

# ==============================================================================
# LÓGICA PRINCIPAL (HÍBRIDA)
# ==============================================================================

def obtener_comentarios():
    """
    Intenta obtener datos reales. Si falla o no hay credenciales, usa Mock Data.
    """
    datos_reales = obtener_comentarios_reales()
    if datos_reales is not None:
        return datos_reales
        
    print("⚠️ Usando Data Simulada (Mock) por fallo en conexión o configuración.")
    time.sleep(0.5) 
    return MOCK_SOCIAL_CONVERSATIONS

def enviar_respuesta_facebook(comentario_id, mensaje):
    """Responde usando la API oficial con depuración detallada."""
    if not FB_PAGE_ACCESS_TOKEN: 
        print("❌ Error: No hay Token configurado.")
        return False

    url = f"https://graph.facebook.com/v18.0/{comentario_id}/comments"
    
    # IMPORTANTE: Token en URL, Mensaje en el Body (data)
    params = {"access_token": FB_PAGE_ACCESS_TOKEN}
    data = {"message": mensaje}
    
    try:
        # Usamos 'json=data' para que requests lo formatee correctamente
        response = requests.post(url, params=params, json=data)
        
        # Si falla (400, 403, 500), lanzamos error para capturarlo abajo
        response.raise_for_status()
        
        print(f"✅ Respuesta publicada en FB exitosamente: {response.json().get('id')}")
        return True

    except Exception as e:
        print(f"❌ Error CRÍTICO enviando a FB: {e}")
        
        # Si Facebook nos dio detalles del error, los imprimimos
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detallado = e.response.json()
                print(f"⚠️ Detalle del error de Facebook: {error_detallado}")
            except:
                print(f"⚠️ Respuesta cruda de Facebook: {e.response.text}")
                
        return False

def agregar_respuesta(padre_id, usuario, texto):
    """
    Sistema Híbrido de Respuesta:
    1. Si ID es real -> API Facebook
    2. Si ID es simulado -> Memoria local
    """
    # Detectamos si empieza con "c", que es tu marca para mocks
    es_simulado = str(padre_id).startswith("c")
    
    if not es_simulado:
        print(f"🌐 Enviando respuesta real a Facebook (ID: {padre_id})...")
        return enviar_respuesta_facebook(padre_id, texto)

    # Lógica Simulada
    for c in MOCK_SOCIAL_CONVERSATIONS:
        if c['id'] == padre_id:
            c['replies'].append({
                "id": f"mock_reply_{int(time.time())}",
                "user": usuario,
                "text": texto,
                "likes": 0
            })
            return True
            
    return False

def mock_data():
    """Datos de fallback para el dashboard."""
    return [{
        "titulo": "Modo Demo",
        "tipo": "Sistema",
        "problema": "Esperando conexión...",
        "solucion": "Verificar tokens en .env",
        "viabilidad": "Alta",
        "esfuerzo": "Bajo",
        "prioridad": "Baja"
    }]