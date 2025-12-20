from ai import analizar_exteriorizacion

# Datos de prueba simulando lo que envía el frontend
test_comentarios = [
    "[ID: 1] Usuario: Juan Dijo: La app se cierra al usar QR",
    "[ID: 2] Usuario: Ana Dijo: No puedo escanear en la noche, necesito modo oscuro",
    "[ID: 3] Usuario: Pedro Dijo: Error al pagar servicios"
]

print("🧠 Probando analizar_exteriorizacion()...")
try:
    resultado = analizar_exteriorizacion(test_comentarios)
    print("\n✅ Resultado recibido:")
    print(resultado)
    
    if isinstance(resultado, list) and len(resultado) > 0:
        print("\n🎉 ¡ÉXITO! La función devuelve una lista de tickets.")
    else:
        print("\n⚠️ OJO: La función devolvió una lista vacía (revisa API Key o consola por errores internos).")

except Exception as e:
    print(f"\n❌ ERROR CRÍTICO: {e}")