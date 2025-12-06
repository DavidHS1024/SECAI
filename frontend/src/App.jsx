import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [comentarios, setComentarios] = useState([]);
  const [tickets, setTickets] = useState([]);
  const [investigaciones, setInvestigaciones] = useState({}); // Guardamos la investigación por índice de ticket
  const [post, setPost] = useState(null);
  const [loading, setLoading] = useState(false);
  const [loadingInvestigacion, setLoadingInvestigacion] = useState(null); // Para saber qué ticket se está investigando
  const [faseActual, setFaseActual] = useState(1);

  // FASE 1
  const fetchComentarios = async () => {
    setLoading(true);
    try {
      const res = await axios.get('http://127.0.0.1:8000/api/socializacion');
      setComentarios(res.data.comentarios);
      setFaseActual(2);
    } catch (e) { alert("Error Backend"); } finally { setLoading(false); }
  };

  // FASE 2
  const analizarInsights = async () => {
    setLoading(true);
    try {
      const res = await axios.post('http://127.0.0.1:8000/api/exteriorizacion', { comentarios });
      setTickets(res.data);
      setFaseActual(3);
    } catch (e) { alert("Error IA"); } finally { setLoading(false); }
  };

  // FASE 3: INVESTIGACIÓN (NUEVO)
  const investigarTicket = async (ticket, index) => {
    setLoadingInvestigacion(index);
    try {
      const res = await axios.post('http://127.0.0.1:8000/api/investigacion', ticket);
      // Guardamos la investigación asociada a este ticket específico
      setInvestigaciones(prev => ({ ...prev, [index]: res.data }));
    } catch (e) { alert("Error Investigando"); } finally { setLoadingInvestigacion(null); }
  };

  // FASE 4: APROBAR (Actualizado)
  const aprobarTicket = async (ticket, index) => {
    setLoading(true);
    setPost(null);
    try {
      // Enviamos el ticket Y la solución investigada (si existe)
      const solucion = investigaciones[index]?.solucion_detallada || ticket.solucion;
      
      const res = await axios.post('http://127.0.0.1:8000/api/combinacion', {
        ticket: ticket,
        solucion_detallada: solucion
      });
      setPost(res.data);
      setFaseActual(4);
    } catch (e) { alert("Error Generando Post"); } finally { setLoading(false); }
  };

  // HELPERS DE ESTILO
  const getBorderColor = (prio) => {
    const p = prio?.toLowerCase() || 'media';
    return p === 'alta' ? 'border-l-orange-500' : p === 'media' ? 'border-l-yellow-500' : 'border-l-green-500';
  };
  const getBadgeColor = (val) => {
    const v = val?.toLowerCase() || 'medio';
    if (v.includes('alta') || v.includes('alto')) return 'bg-orange-500/20 text-orange-300 border-orange-500/50';
    if (v.includes('media') || v.includes('medio')) return 'bg-yellow-500/20 text-yellow-300 border-yellow-500/50';
    return 'bg-green-500/20 text-green-300 border-green-500/50';
  };

  return (
    <div className="min-h-screen bg-[#020617] text-slate-100 font-sans p-6 md:p-12">
      
      {/* HEADER */}
      <header className="relative bg-[#020617] border border-slate-800 rounded-2xl p-6 mb-8 shadow-2xl overflow-hidden">
        <div className="absolute top-0 left-0 w-64 h-64 bg-cyan-500/10 blur-[80px] rounded-full -translate-x-1/2 -translate-y-1/2"></div>
        <div className="absolute bottom-0 right-0 w-64 h-64 bg-purple-600/10 blur-[80px] rounded-full translate-x-1/2 translate-y-1/2"></div>
        <div className="relative z-10 flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-cyan-400 to-purple-600 flex items-center justify-center text-2xl shadow-lg">🌀</div>
            <div>
              <h1 className="text-2xl font-bold text-gray-50">SECAI</h1>
              <p className="text-xs text-indigo-200 uppercase tracking-widest">Feedback Intelligence System</p>
            </div>
          </div>
          <div className="flex gap-2">
            {[1, 2, 3, 4].map(s => <div key={s} className={`h-2 w-12 rounded-full transition-all duration-500 ${faseActual >= s ? 'bg-gradient-to-r from-cyan-500 to-purple-500 shadow-[0_0_10px_rgba(168,85,247,0.4)]' : 'bg-slate-800'}`} />)}
          </div>
        </div>
      </header>

      <main className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* 1. SOCIALIZACIÓN */}
        <section className={`bg-[#020617] border border-slate-800 rounded-2xl p-6 shadow-xl transition-all duration-300 ${faseActual === 1 ? 'ring-1 ring-cyan-500/50' : ''}`}>
          <h2 className="text-lg font-bold mb-4 flex items-center gap-2 text-gray-100">1. Socialización <span className="text-2xl">🗣️</span></h2>
          <div className="flex items-center gap-4 mb-6">
            <button onClick={fetchComentarios} disabled={loading} className="bg-gradient-to-r from-cyan-600 to-blue-600 hover:brightness-110 text-white font-semibold py-2 px-6 rounded-full transition-all active:scale-95 disabled:opacity-50 shadow-lg shadow-cyan-900/20">
              {loading && faseActual === 1 ? 'Escuchando...' : '📡 Escuchar'}
            </button>
            <div className="text-sm font-mono text-slate-400">{comentarios.length} comentarios</div>
          </div>
          <div className="bg-slate-900/50 rounded-xl border border-slate-800/50 h-64 overflow-y-auto p-2 custom-scrollbar space-y-2">
            {comentarios.map((c, i) => <li key={i} className="list-none bg-[#0f172a] p-3 rounded-lg border border-slate-800 text-xs text-slate-300"><span className="font-bold text-cyan-500 mr-2">#{i+1}</span>{c}</li>)}
          </div>
        </section>

        {/* 2. EXTERIORIZACIÓN */}
        <section className={`bg-[#020617] border border-slate-800 rounded-2xl p-6 shadow-xl transition-all duration-300 ${faseActual === 2 ? 'ring-1 ring-purple-500/50' : ''}`}>
          <h2 className="text-lg font-bold mb-4 flex items-center gap-2 text-gray-100">2. Exteriorización <span className="text-2xl">⚙️</span></h2>
          <div className="mb-6">
             <button onClick={analizarInsights} disabled={loading || comentarios.length === 0} className="w-full md:w-auto bg-gradient-to-r from-purple-600 to-pink-600 hover:brightness-110 text-white font-semibold py-2 px-6 rounded-full transition-all active:scale-95 disabled:opacity-50 shadow-lg shadow-purple-900/20">
              {loading && faseActual >= 2 && faseActual < 4 ? 'Procesando...' : '⚡ Procesar Insights'}
            </button>
          </div>
          <div className="h-64 overflow-y-auto pr-2 custom-scrollbar space-y-3">
            {tickets.map((t, i) => (
              <div key={i} className={`bg-slate-900/80 rounded-xl p-4 border-l-4 ${getBorderColor(t.prioridad)} border-y border-r border-slate-800 shadow-lg`}>
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-bold text-sm text-slate-100 flex items-center gap-2"><span>🎯</span> {t.titulo}</h3>
                  <span className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded border ${getBadgeColor(t.prioridad)}`}>{t.prioridad}</span>
                </div>
                <p className="text-xs text-slate-400 line-clamp-2">{t.problema}</p>
                {/* Métricas Visuales Mejoradas */}
                <div className="flex gap-2 mt-3 pt-3 border-t border-slate-800/50">
                   <span className={`text-[10px] px-2 py-0.5 rounded border ${getBadgeColor(t.viabilidad)}`}>Viabilidad: {t.viabilidad}</span>
                   <span className={`text-[10px] px-2 py-0.5 rounded border ${getBadgeColor(t.esfuerzo)}`}>Esfuerzo: {t.esfuerzo}</span>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* 4. INTERNALIZACIÓN (Bottom-Left) */}
        <section className={`bg-[#020617] border border-slate-800 rounded-2xl p-6 shadow-xl transition-all duration-300 ${faseActual === 4 ? 'ring-1 ring-green-500/50 opacity-100' : 'opacity-60'}`}>
          <h2 className="text-lg font-bold mb-4 text-gray-100 flex items-center gap-2">4. Internalización <span className="text-2xl">📢</span></h2>
          <div className="h-[400px] overflow-y-auto custom-scrollbar bg-slate-950/30 rounded-xl border border-slate-800 p-4">
            {post ? (
              <div className="space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-700">
                <div className="flex items-center gap-3 mb-2">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-cyan-400 to-purple-600 flex items-center justify-center text-white font-bold">Y</div>
                  <div><div className="text-sm font-bold text-slate-200">Yape Oficial</div><div className="text-xs text-slate-500">Hace un momento · 🌍</div></div>
                </div>
                <p className="text-sm text-slate-300 whitespace-pre-wrap leading-relaxed">{post.texto_post}</p>
                {post.url_imagen && <div className="rounded-xl overflow-hidden border border-slate-800 shadow-2xl mt-4"><img src={post.url_imagen} alt="AI Art" className="w-full h-auto object-cover hover:scale-105 transition-transform duration-700" /></div>}
              </div>
            ) : <div className="h-full flex items-center justify-center text-slate-600 italic text-sm border-2 border-dashed border-slate-800 rounded-xl">El contenido aparecerá aquí</div>}
          </div>
        </section>

        {/* 3. COMBINACIÓN (Bottom-Right) - CON BOTÓN DE INVESTIGACIÓN */}
        <section className={`bg-[#020617] border border-slate-800 rounded-2xl p-6 shadow-xl transition-all duration-300 ${faseActual === 3 ? 'ring-1 ring-yellow-500/50 opacity-100' : 'opacity-60'}`}>
          <h2 className="text-lg font-bold mb-4 text-gray-100 flex items-center gap-2">3. Combinación <span className="text-2xl">📚</span></h2>
          <div className="h-[400px] overflow-y-auto pr-2 custom-scrollbar space-y-4">
            {tickets.map((t, i) => (
              <div key={i} className="bg-slate-900/50 border border-slate-800 rounded-xl p-5 hover:border-slate-600 transition-all">
                <div className="flex justify-between items-center mb-3">
                  <h3 className="font-bold text-slate-200 text-sm">{t.titulo}</h3>
                  {/* Botón de Investigación */}
                  {!investigaciones[i] && (
                    <button 
                      onClick={() => investigarTicket(t, i)}
                      disabled={loadingInvestigacion === i}
                      className="text-[10px] bg-slate-800 hover:bg-cyan-900 text-cyan-400 border border-cyan-900 px-3 py-1 rounded-full transition-colors flex items-center gap-1"
                    >
                      {loadingInvestigacion === i ? '🔍 Buscando...' : '🔍 Investigar Solución'}
                    </button>
                  )}
                </div>
                
                {/* Área de Solución: Vacía al inicio, llena tras investigar */}
                <div className="text-xs text-slate-400 mb-4 bg-slate-950 p-3 rounded border border-slate-800/50 min-h-[60px]">
                  {!investigaciones[i] ? (
                    <p className="italic text-slate-600">Requiere investigación técnica para ver la solución detallada y fuentes.</p>
                  ) : (
                    <div className="animate-in fade-in duration-500">
                      <p className="mb-2"><strong className="text-cyan-500">Solución Técnica:</strong></p>
                      <p className="mb-3 leading-relaxed">{investigaciones[i].solucion_detallada}</p>
                      
                      <div className="border-t border-slate-800 pt-2 mt-2">
                        <strong className="text-[10px] text-purple-400 uppercase">Fuentes Consultadas:</strong>
                        <ul className="mt-1 space-y-1">
                          {investigaciones[i].fuentes.map((f, idx) => (
                            <li key={idx} className="flex items-center gap-2 text-[10px] text-slate-500">
                              <span>🔗</span> <a href="#" className="hover:text-purple-400 truncate">{f.titulo}</a>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  )}
                </div>

                <button 
                  onClick={() => aprobarTicket(t, i)}
                  disabled={!investigaciones[i] || loading}
                  className="w-full py-2 rounded-lg bg-slate-800 hover:bg-green-600/20 hover:text-green-400 text-slate-400 text-xs font-bold border border-slate-700 hover:border-green-500/50 transition-all active:scale-95 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading && post === null ? 'Generando...' : '✅ Aprobar y Generar Post'}
                </button>
              </div>
            ))}
          </div>
        </section>

      </main>
    </div>
  );
}

export default App;