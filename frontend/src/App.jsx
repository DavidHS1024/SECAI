import React, { useState } from 'react';
import axios from 'axios'; // Importamos la librería para conectar con el Backend

function App() {
  // Estados para guardar los datos
  const [comentarios, setComentarios] = useState([]);
  const [loading, setLoading] = useState(false); // Para mostrar el spinner o texto de carga

  // Función para llamar al Backend (Socialización)
  const fetchComentarios = async () => {
    setLoading(true);
    try {
      // Llamamos a tu API de Python (asegúrate de que el backend esté corriendo en el puerto 8000)
      const response = await axios.get('http://127.0.0.1:8000/api/socializacion');
      
      // Guardamos los datos que vinieron de Python
      setComentarios(response.data.comentarios);
      console.log("Datos recibidos:", response.data);
      
    } catch (error) {
      console.error("Error conectando con el backend:", error);
      alert("Error al conectar con el servidor. ¿Está encendido el Backend?");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#020617] text-slate-100 font-sans p-6 md:p-12">
      
      {/* --- HEADER (Igual que antes) --- */}
      <header className="relative bg-[#020617] border border-slate-800 rounded-2xl p-6 mb-8 shadow-2xl overflow-hidden">
        <div className="absolute top-0 left-0 w-64 h-64 bg-cyan-500/10 blur-[80px] rounded-full -translate-x-1/2 -translate-y-1/2"></div>
        <div className="absolute bottom-0 right-0 w-64 h-64 bg-purple-600/10 blur-[80px] rounded-full translate-x-1/2 translate-y-1/2"></div>

        <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-cyan-400 to-purple-600 flex items-center justify-center text-2xl shadow-lg shadow-sky-500/20">
              🟣
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-50">Yape Feedback Loop</h1>
              <p className="text-sm text-indigo-200">SECI + IA (React Version)</p>
            </div>
          </div>

          <div className="flex flex-wrap gap-2">
            {['1 · Socialización', '2 · Exteriorización', '3 · Combinación', '4 · Internalización'].map((step) => (
              <span key={step} className="text-xs px-3 py-1 rounded-full border border-green-500/30 bg-green-500/10 text-green-100 font-semibold">
                {step}
              </span>
            ))}
          </div>
        </div>
      </header>

      {/* --- GRID PRINCIPAL --- */}
      <main className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* 1. SOCIALIZACIÓN */}
        <section className="bg-[#020617] border border-slate-800 rounded-2xl p-6 shadow-xl relative overflow-hidden group hover:border-slate-700 transition-colors">
          <h2 className="text-lg font-bold mb-4 flex items-center gap-2 text-gray-100">
            1. Socialización <span className="text-2xl">🗣️</span>
          </h2>
          
          <div className="flex items-center gap-6 mb-6">
            <button 
              onClick={fetchComentarios} // Conectamos el botón a la función
              disabled={loading} // Deshabilitamos si está cargando
              className={`
                bg-gradient-to-r from-cyan-500 to-sky-500 hover:from-green-500 hover:to-sky-500 
                text-white font-semibold py-2 px-6 rounded-full transition-all shadow-lg shadow-cyan-500/20 active:scale-95
                ${loading ? 'opacity-50 cursor-not-allowed' : ''}
              `}
            >
              {loading ? 'Escuchando...' : '📡 Escuchar'}
            </button>
            
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-bold text-white drop-shadow-[0_0_10px_rgba(139,92,246,0.3)]">
                {comentarios.length}
              </span>
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wide">
                Comentarios
              </span>
            </div>
          </div>

          {/* Área de scroll para los comentarios */}
          <div className="p-2 bg-slate-900/30 rounded-xl border border-slate-800/50 max-h-[300px] overflow-y-auto custom-scrollbar">
            {comentarios.length === 0 ? (
              <div className="text-sm text-slate-500 text-center italic py-8">
                {loading ? 'Conectando con Facebook...' : 'Presiona "Escuchar" para cargar datos.'}
              </div>
            ) : (
              <ul className="space-y-3">
                {comentarios.map((c, i) => (
                  <li key={i} className="bg-[#0f172a] border border-slate-800 p-3 rounded-lg shadow-sm hover:border-slate-600 transition-colors">
                    <div className="flex gap-3">
                      <span className="flex-shrink-0 w-6 h-6 rounded-full bg-slate-800 flex items-center justify-center text-xs text-slate-400 font-mono border border-slate-700">
                        {i + 1}
                      </span>
                      <p className="text-sm text-slate-300 leading-relaxed">
                        {c}
                      </p>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </section>

        {/* 2. EXTERIORIZACIÓN (Placeholder) */}
        <section className="bg-[#020617] border border-slate-800 rounded-2xl p-6 shadow-xl opacity-75">
          <h2 className="text-lg font-bold mb-4 text-gray-400">2. Exteriorización ⚙️</h2>
          <div className="p-8 border-2 border-dashed border-slate-800 rounded-xl text-center text-slate-600">
            Próximamente
          </div>
        </section>

        {/* 3. COMBINACIÓN (Placeholder) */}
        <section className="bg-[#020617] border border-slate-800 rounded-2xl p-6 shadow-xl opacity-75">
          <h2 className="text-lg font-bold mb-4 text-gray-400">3. Combinación 📚</h2>
          <div className="p-8 border-2 border-dashed border-slate-800 rounded-xl text-center text-slate-600">
            Próximamente
          </div>
        </section>

        {/* 4. INTERNALIZACIÓN (Placeholder) */}
        <section className="bg-[#020617] border border-slate-800 rounded-2xl p-6 shadow-xl opacity-75">
          <h2 className="text-lg font-bold mb-4 text-gray-400">4. Internalización 📢</h2>
          <div className="p-8 border-2 border-dashed border-slate-800 rounded-xl text-center text-slate-600">
            Próximamente
          </div>
        </section>

      </main>
    </div>
  );
}

export default App;