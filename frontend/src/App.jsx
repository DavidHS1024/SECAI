import React, { useState } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import { jsPDF } from "jspdf";

function App() {
  const [comentarios, setComentarios] = useState([]);
  const [tickets, setTickets] = useState([]);
  const [investigaciones, setInvestigaciones] = useState({});
  const [post, setPost] = useState(null);
  const [loading, setLoading] = useState(false);
  const [loadingInvestigacion, setLoadingInvestigacion] = useState(null);
  const [faseActual, setFaseActual] = useState(1);
  
  // Modal State
  const [modalOpen, setModalOpen] = useState(false);
  const [modalData, setModalData] = useState(null);

  // --- CONEXIONES API ---
  const fetchComentarios = async () => {
    setLoading(true);
    try {
      const res = await axios.get('http://127.0.0.1:8000/api/socializacion');
      setComentarios(res.data.comentarios);
      setFaseActual(2);
    } catch (e) { alert("Error Backend: Asegúrate que uvicorn esté corriendo."); } finally { setLoading(false); }
  };

  const analizarInsights = async () => {
    if (comentarios.length === 0) return alert("Faltan comentarios.");
    setLoading(true);
    try {
      const res = await axios.post('http://127.0.0.1:8000/api/exteriorizacion', { comentarios });
      setTickets(res.data);
      setFaseActual(3);
    } catch (e) { alert("Error IA: Revisa la consola del backend."); } finally { setLoading(false); }
  };

  const investigarTicket = async (ticket, index) => {
    setLoadingInvestigacion(index);
    try {
      const res = await axios.post('http://127.0.0.1:8000/api/investigacion', ticket);
      setInvestigaciones(prev => ({ ...prev, [index]: res.data }));
    } catch (e) { alert("Error Investigando."); } finally { setLoadingInvestigacion(null); }
  };

  const aprobarTicket = async (ticket, index) => {
    setLoading(true); setPost(null);
    try {
      const solucion = investigaciones[index]?.solucion_detallada || ticket.solucion;
      const res = await axios.post('http://127.0.0.1:8000/api/combinacion', { ticket, solucion_detallada: solucion });
      setPost(res.data);
      setFaseActual(4);
    } catch (e) { alert("Error Generando Post."); } finally { setLoading(false); }
  };

  // --- UTILIDADES DE UX ---
  const abrirModal = (ticket, investigacion) => {
    setModalData({ ticket, investigacion });
    setModalOpen(true);
  };

  const generarPDF = () => {
    if (!modalData) return;
    const doc = new jsPDF();
    const { ticket, investigacion } = modalData;
    
    // Configuración básica del PDF
    doc.setFont("helvetica", "bold");
    doc.setFontSize(16);
    doc.text("Informe Técnico SECAI", 20, 20);
    
    doc.setFontSize(11);
    doc.setFont("helvetica", "normal");
    doc.text(`Ticket: ${ticket.titulo}`, 20, 30);
    doc.text(`Prioridad: ${ticket.prioridad}`, 20, 36);
    
    doc.setLineWidth(0.5);
    doc.line(20, 40, 190, 40);
    
    doc.setFontSize(12);
    doc.setFont("helvetica", "bold");
    doc.text("Detalle de la Solución:", 20, 50);
    
    doc.setFont("helvetica", "normal");
    doc.setFontSize(10);
    
    // Limpieza básica de markdown para el PDF
    const cleanText = investigacion.solucion_detallada.replace(/\*\*/g, "").replace(/###/g, "").replace(/-/g, "•");
    const splitText = doc.splitTextToSize(cleanText, 170);
    doc.text(splitText, 20, 60);
    
    // Fuentes
    let yPos = 60 + (splitText.length * 5) + 10;
    if (yPos > 280) { doc.addPage(); yPos = 20; }
    
    if (investigacion.fuentes && investigacion.fuentes.length > 0) {
      doc.setFont("helvetica", "bold");
      doc.text("Referencias:", 20, yPos);
      yPos += 6;
      doc.setFont("helvetica", "normal");
      doc.setTextColor(0, 0, 255);
      
      investigacion.fuentes.forEach((f) => {
        const title = f.titulo || "Fuente Externa";
        const url = f.url || "#";
        doc.textWithLink(`• ${title}`, 20, yPos, { url: url });
        yPos += 6;
      });
    }
    
    doc.save(`SECAI_Reporte.pdf`);
  };

  const getBorderColor = (p) => (p?.toLowerCase() === 'alta' ? 'border-l-orange-500' : p?.toLowerCase() === 'media' ? 'border-l-yellow-500' : 'border-l-green-500');
  const getBadgeColor = (p) => (p?.toLowerCase() === 'alta' ? 'text-orange-400 bg-orange-500/10 border-orange-500/30' : p?.toLowerCase() === 'media' ? 'text-yellow-400 bg-yellow-500/10 border-yellow-500/30' : 'text-green-400 bg-green-500/10 border-green-500/30');

  return (
    <div className="min-h-screen bg-[#020617] text-slate-100 font-sans p-4 md:p-8 relative selection:bg-cyan-500/30">
      
      {/* HEADER */}
      <header className="relative bg-[#020617] border border-slate-800 rounded-2xl p-6 mb-8 shadow-2xl overflow-hidden">
        <div className="absolute top-0 left-0 w-64 h-64 bg-cyan-500/10 blur-[80px] rounded-full -translate-x-1/2 -translate-y-1/2"></div>
        <div className="relative z-10 flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-cyan-400 to-purple-600 flex items-center justify-center text-2xl shadow-lg ring-1 ring-white/10">🌀</div>
            <div>
              <h1 className="text-2xl font-bold text-gray-50 tracking-tight">SECAI</h1>
              <p className="text-xs text-indigo-300 uppercase tracking-widest font-semibold">Feedback Intelligence Agent</p>
            </div>
          </div>
          <div className="flex gap-2 bg-slate-900/50 p-2 rounded-full border border-slate-800">
            {[1, 2, 3, 4].map(s => <div key={s} className={`h-2 w-8 md:w-12 rounded-full transition-all duration-700 ${faseActual >= s ? 'bg-gradient-to-r from-cyan-500 to-purple-500 shadow-[0_0_8px_rgba(168,85,247,0.5)]' : 'bg-slate-800'}`} />)}
          </div>
        </div>
      </header>

      <main className="grid grid-cols-1 lg:grid-cols-2 gap-6 md:gap-8">
        
        {/* 1. SOCIALIZACIÓN */}
        <section className={`bg-[#0b1121] border border-slate-800 rounded-2xl p-6 shadow-xl transition-all duration-500 ${faseActual === 1 ? 'ring-1 ring-cyan-500/50 shadow-cyan-900/20' : ''}`}>
          <h2 className="text-lg font-bold mb-4 text-gray-100 flex items-center gap-2">1. Socialización <span className="text-xl">🗣️</span></h2>
          <div className="flex flex-wrap items-center gap-4 mb-4">
            <button onClick={fetchComentarios} disabled={loading} className="bg-gradient-to-r from-cyan-600 to-blue-600 hover:to-blue-500 text-white font-semibold py-2 px-6 rounded-full active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-cyan-900/30 transition-all">
              {loading && faseActual === 1 ? 'Escuchando...' : '📡 Escuchar'}
            </button>
            <span className="text-sm font-mono text-slate-400 bg-slate-900 px-3 py-1 rounded-md border border-slate-800">{comentarios.length} comentarios</span>
          </div>
          <div className="bg-slate-950/50 rounded-xl border border-slate-800/60 h-72 overflow-y-auto p-3 space-y-2 custom-scrollbar">
            {comentarios.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-slate-600 gap-3">
                <span className="text-4xl opacity-20">💬</span>
                <span className="text-sm italic">Esperando conexión con Facebook...</span>
              </div>
            ) : (
              comentarios.map((c, i) => <div key={i} className="bg-[#131c31] p-3 rounded-lg border border-slate-800/80 text-xs text-slate-300 hover:border-slate-700 transition-colors"><strong className="text-cyan-500 mr-1">#{i+1}</strong> {c}</div>)
            )}
          </div>
        </section>

        {/* 2. EXTERIORIZACIÓN */}
        <section className={`bg-[#0b1121] border border-slate-800 rounded-2xl p-6 shadow-xl transition-all duration-500 ${faseActual === 2 ? 'ring-1 ring-purple-500/50 shadow-purple-900/20' : ''}`}>
          <h2 className="text-lg font-bold mb-4 text-gray-100 flex items-center gap-2">2. Exteriorización <span className="text-xl">⚙️</span></h2>
          <div className="mb-4">
            <button onClick={analizarInsights} disabled={loading || !comentarios.length} className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:to-pink-500 text-white font-semibold py-2 px-6 rounded-full active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-purple-900/30 transition-all flex items-center justify-center gap-2">
              {loading && faseActual === 2 ? <span className="animate-pulse">Analizando...</span> : '⚡ Procesar Insights'}
            </button>
          </div>
          <div className="h-72 overflow-y-auto pr-2 custom-scrollbar space-y-3">
            {tickets.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-slate-600 border-2 border-dashed border-slate-800/50 rounded-xl gap-3">
                <span className="text-4xl opacity-20">🧩</span>
                <span className="text-sm italic">Los tickets generados aparecerán aquí</span>
              </div>
            ) : (
              tickets.map((t, i) => (
                <div key={i} className={`bg-slate-900/80 rounded-xl p-4 border-l-4 ${getBorderColor(t.prioridad)} border-y border-r border-slate-800 shadow-md group hover:bg-slate-900 transition-colors`}>
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="font-bold text-sm text-slate-100 leading-tight pr-2">🎯 {t.titulo}</h3>
                    <span className={`text-[10px] uppercase px-2 py-0.5 rounded font-bold border ${getBadgeColor(t.prioridad)}`}>{t.prioridad}</span>
                  </div>
                  <p className="text-xs text-slate-400 line-clamp-2 mb-2">{t.problema}</p>
                  <div className="flex gap-2 border-t border-slate-800 pt-2">
                    <span className="text-[10px] text-slate-500 bg-slate-950 px-2 py-0.5 rounded">Esfuerzo: {t.esfuerzo}</span>
                    <span className="text-[10px] text-slate-500 bg-slate-950 px-2 py-0.5 rounded">Viabilidad: {t.viabilidad}</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </section>

        {/* 4. INTERNALIZACIÓN */}
        <section className={`bg-[#0b1121] border border-slate-800 rounded-2xl p-6 shadow-xl transition-all duration-500 ${faseActual === 4 ? 'ring-1 ring-green-500/50 shadow-green-900/20 opacity-100' : 'opacity-70 grayscale-[0.5]'}`}>
          <h2 className="text-lg font-bold mb-4 text-gray-100 flex items-center gap-2">4. Internalización <span className="text-xl">📢</span></h2>
          <div className="h-[450px] overflow-y-auto custom-scrollbar bg-slate-950/30 rounded-xl border border-slate-800 p-4 relative">
            {post ? (
              <div className="animate-in fade-in slide-in-from-bottom-4 duration-700 space-y-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-cyan-400 to-purple-600 flex items-center justify-center font-bold text-white shadow-lg">Y</div>
                  <div><div className="text-sm font-bold text-slate-100">Yape Oficial</div><div className="text-xs text-slate-500">Hace un momento · 🌍</div></div>
                </div>
                <p className="text-sm text-slate-300 whitespace-pre-wrap leading-relaxed">{post.texto_post}</p>
                {post.url_imagen ? (
                  <div className="rounded-xl overflow-hidden border border-slate-800 shadow-2xl mt-2 group cursor-pointer">
                    <img src={post.url_imagen} className="w-full h-auto object-cover group-hover:scale-105 transition-transform duration-700" alt="Generada por IA" />
                  </div>
                ) : <div className="h-48 bg-slate-900 rounded-xl flex items-center justify-center text-xs text-slate-600">Imagen no disponible</div>}
                
                <div className="flex gap-6 border-t border-slate-800 pt-3 text-slate-500 text-xs font-semibold">
                  <span>👍 Me gusta</span><span>💬 Comentar</span><span>↗️ Compartir</span>
                </div>
              </div>
            ) : (
              <div className="h-full flex flex-col items-center justify-center text-slate-600 border-2 border-dashed border-slate-800/50 rounded-xl gap-3">
                <span className="text-4xl opacity-20">🖼️</span>
                <span className="text-sm italic">El post generado aparecerá aquí</span>
              </div>
            )}
          </div>
        </section>

        {/* 3. COMBINACIÓN */}
        <section className={`bg-[#0b1121] border border-slate-800 rounded-2xl p-6 shadow-xl transition-all duration-500 ${faseActual === 3 ? 'ring-1 ring-yellow-500/50 shadow-yellow-900/20 opacity-100' : 'opacity-70'}`}>
          <h2 className="text-lg font-bold mb-4 text-gray-100 flex items-center gap-2">3. Combinación <span className="text-xl">📚</span></h2>
          <div className="h-[450px] overflow-y-auto pr-2 custom-scrollbar space-y-4">
            {tickets.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-slate-600 border-2 border-dashed border-slate-800/50 rounded-xl gap-3">
                <span className="text-4xl opacity-20">🔍</span>
                <span className="text-sm italic">Esperando tickets para investigar...</span>
              </div>
            ) : (
              tickets.map((t, i) => (
                <div key={i} className="bg-slate-900/40 border border-slate-800 rounded-xl p-5 hover:border-slate-600 transition-all shadow-sm">
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="font-bold text-slate-200 text-sm flex-1 mr-2">{t.titulo}</h3>
                    
                    {/* Botón de Estado de Investigación */}
                    {!investigaciones[i] ? (
                      <button onClick={() => investigarTicket(t, i)} disabled={loadingInvestigacion === i} className="shrink-0 text-[10px] bg-cyan-950/30 hover:bg-cyan-900/50 text-cyan-400 border border-cyan-800/50 px-3 py-1.5 rounded-full flex items-center gap-1.5 transition-all shadow-sm shadow-cyan-900/10">
                        {loadingInvestigacion === i ? <span className="animate-spin">⏳</span> : '🔍'} 
                        {loadingInvestigacion === i ? 'Buscando...' : 'Investigar'}
                      </button>
                    ) : (
                      <button onClick={() => abrirModal(t, investigaciones[i])} className="shrink-0 text-[10px] bg-purple-950/30 hover:bg-purple-900/50 text-purple-300 border border-purple-800/50 px-3 py-1.5 rounded-full flex items-center gap-1.5 transition-all shadow-sm shadow-purple-900/10 animate-in zoom-in">
                        📄 Ver Informe
                      </button>
                    )}
                  </div>
                  
                  {/* Área de Resumen con Scroll Interno */}
                  <div className="text-xs text-slate-400 mb-4 bg-[#0a0f1d] p-3 rounded-lg border border-slate-800/50 relative">
                    {!investigaciones[i] ? (
                      <p className="italic text-slate-600 text-center py-2">Requiere investigación técnica para ver detalles.</p>
                    ) : (
                      <div className="max-h-32 overflow-y-auto custom-scrollbar pr-1">
                        <strong className="text-cyan-600 block mb-1 uppercase text-[10px] tracking-wider">Resumen Técnico:</strong>
                        {/* Texto truncado visualmente, el detalle está en el modal */}
                        <div className="opacity-90 leading-relaxed">
                           {investigaciones[i].solucion_detallada.substring(0, 150)}...
                        </div>
                      </div>
                    )}
                  </div>

                  <button onClick={() => aprobarTicket(t, i)} disabled={!investigaciones[i] || loading} className="w-full py-2.5 rounded-lg bg-slate-800 hover:bg-green-900/20 text-slate-400 hover:text-green-400 text-xs font-bold border border-slate-700 hover:border-green-500/50 transition-all disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center gap-2">
                    {loading && post === null ? 'Generando...' : '✅ Aprobar y Generar Post'}
                  </button>
                </div>
              ))
            )}
          </div>
        </section>
      </main>

      {/* --- MODAL (Estilo Google Drive Preview) --- */}
      {modalOpen && modalData && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 md:p-8 bg-black/90 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="bg-[#0f172a] w-full max-w-4xl h-[85vh] rounded-xl border border-slate-700 shadow-2xl flex flex-col overflow-hidden relative">
            
            {/* Toolbar Superior */}
            <div className="h-14 border-b border-slate-700 bg-[#1e293b] flex items-center justify-between px-6 shrink-0">
              <div className="flex items-center gap-3">
                <span className="text-2xl">📄</span>
                <h2 className="text-sm font-semibold text-slate-200 truncate max-w-[200px] md:max-w-md">Informe: {modalData.ticket.titulo}</h2>
              </div>
              <div className="flex items-center gap-3">
                <button onClick={generarPDF} className="bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold px-4 py-2 rounded shadow-lg transition-colors flex items-center gap-2">
                  <span>⬇️</span> Descargar PDF
                </button>
                <button onClick={() => setModalOpen(false)} className="bg-slate-700 hover:bg-slate-600 text-white w-8 h-8 rounded-full flex items-center justify-center transition-colors">
                  &times;
                </button>
              </div>
            </div>

            {/* Contenido del Documento (Scrollable) */}
            <div className="flex-1 overflow-y-auto p-8 md:p-12 custom-scrollbar bg-[#020617]">
              <div className="max-w-3xl mx-auto bg-[#0f172a] p-8 md:p-12 rounded-none md:rounded-lg shadow-lg border border-slate-800 min-h-full">
                
                {/* Título del Documento */}
                <h1 className="text-3xl font-bold text-white mb-2">{modalData.ticket.titulo}</h1>
                <div className="flex gap-4 text-xs text-slate-400 mb-8 border-b border-slate-700 pb-4">
                  <span>TIPO: <strong className="text-slate-200 uppercase">{modalData.ticket.tipo}</strong></span>
                  <span>PRIORIDAD: <strong className="text-slate-200 uppercase">{modalData.ticket.prioridad}</strong></span>
                </div>

                {/* Renderizado de Markdown Seguro */}
                <div className="text-slate-300 leading-7 space-y-4 text-sm md:text-base">
                  <ReactMarkdown 
                    components={{
                      h1: ({node, ...props}) => <h2 className="text-xl font-bold text-cyan-400 mt-6 mb-3" {...props} />,
                      h2: ({node, ...props}) => <h3 className="text-lg font-bold text-purple-400 mt-5 mb-2" {...props} />,
                      h3: ({node, ...props}) => <h4 className="text-base font-bold text-slate-200 mt-4 mb-2" {...props} />,
                      ul: ({node, ...props}) => <ul className="list-disc pl-5 space-y-1 my-3 text-slate-300" {...props} />,
                      li: ({node, ...props}) => <li className="pl-1" {...props} />,
                      strong: ({node, ...props}) => <strong className="text-slate-100 font-bold" {...props} />,
                      p: ({node, ...props}) => <p className="mb-4 text-justify" {...props} />,
                    }}
                  >
                    {modalData.investigacion.solucion_detallada}
                  </ReactMarkdown>
                </div>

                {/* Sección de Fuentes */}
                <div className="mt-12 pt-8 border-t border-slate-700/50">
                  <h3 className="text-sm font-bold text-slate-500 uppercase tracking-widest mb-4">Fuentes Consultadas</h3>
                  {modalData.investigacion.fuentes && modalData.investigacion.fuentes.length > 0 ? (
                    <ul className="grid gap-3">
                      {modalData.investigacion.fuentes.map((f, idx) => (
                        <li key={idx} className="bg-slate-900/50 p-3 rounded border border-slate-800 flex items-start gap-3 hover:border-cyan-900/50 transition-colors">
                          <span className="text-lg">🔗</span>
                          <div className="overflow-hidden">
                            <a href={f.url} target="_blank" rel="noopener noreferrer" className="text-sm font-semibold text-cyan-500 hover:text-cyan-400 hover:underline block truncate">
                              {f.titulo || "Referencia Externa"}
                            </a>
                            <a href={f.url} target="_blank" rel="noopener noreferrer" className="text-[10px] text-slate-500 truncate block">
                              {f.url}
                            </a>
                          </div>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-sm text-slate-600 italic">La investigación se basó en conocimiento interno del modelo.</p>
                  )}
                </div>

              </div>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}

export default App;