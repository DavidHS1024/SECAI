import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import { jsPDF } from "jspdf";

// --- COMPONENTE: CONSOLA DE AGENTE (Visualización Matrix) ---
const AgentConsole = ({ logs }) => {
  const scrollRef = useRef(null);
  
  // Auto-scroll al final cada vez que llega un log
  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  return (
    <div className="bg-[#050b14] font-mono text-[11px] p-4 rounded-lg border border-slate-700/50 h-48 overflow-y-auto custom-scrollbar shadow-inner relative group">
      {/* Efecto de scanline sutil */}
      <div className="absolute inset-0 bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.25)_50%),linear-gradient(90deg,rgba(255,0,0,0.06),rgba(0,255,0,0.02),rgba(0,0,255,0.06))] z-0 pointer-events-none opacity-20"></div>
      
      <div className="relative z-10 space-y-2">
        {logs?.map((log, i) => (
          <div key={i} className="flex gap-3 animate-in fade-in slide-in-from-left-2 duration-300">
            <span className="text-slate-600 shrink-0 font-bold">[{log.time}]</span>
            <span className="shrink-0">{log.emoji}</span> 
            <span className={`break-words leading-tight ${
              log.type === 'error' ? 'text-red-400 font-bold' : 
              log.type === 'success' ? 'text-green-400 font-bold' : 
              log.type === 'info' ? 'text-cyan-300' : 'text-slate-300'
            }`}>
              {log.message}
            </span>
          </div>
        ))}
        {(!logs || logs.length === 0) && (
          <div className="text-slate-700 italic text-center mt-10">Esperando inicialización de agentes...</div>
        )}
        <div ref={scrollRef} />
      </div>
    </div>
  );
};

function App() {
  // --- ESTADOS DE DATOS ---
  const [comentarios, setComentarios] = useState([]);
  const [tickets, setTickets] = useState([]);
  const [post, setPost] = useState(null);
  
  // --- ESTADOS DEL SISTEMA DE AGENTES (El Cerebro Nuevo) ---
  // agentLogs: Guarda el historial de chat entre agentes para cada ticket
  const [agentLogs, setAgentLogs] = useState({}); 
  // agentState: 'IDLE' (inactivo), 'WORKING' (pensando), 'DONE' (terminó), 'ERROR'
  const [agentState, setAgentState] = useState({}); 
  // solucionesFinales: Guarda el resultado final (investigacion + auditoria) para el modal
  const [solucionesFinales, setSolucionesFinales] = useState({});

  const [loading, setLoading] = useState(false); // Loading general (Fase 1, 2, 4)
  const [faseActual, setFaseActual] = useState(1);
  
  // --- ESTADOS DEL MODAL ---
  const [modalOpen, setModalOpen] = useState(false);
  const [modalData, setModalData] = useState(null);

  // ========================================================================
  // CONEXIONES API (FASES 1 y 2)
  // ========================================================================

  const fetchComentarios = async () => {
    setLoading(true);
    try {
      const res = await axios.get('http://127.0.0.1:8000/api/socializacion');
      setComentarios(res.data.comentarios);
      setFaseActual(2);
    } catch (e) { alert("Error Backend: Verifica que uvicorn esté corriendo."); } finally { setLoading(false); }
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

  // ========================================================================
  // 🧠 ORQUESTADOR DE AGENTES AUTÓNOMOS (FASE 3 - LOOP)
  // ========================================================================
  
  // Función auxiliar para agregar logs a la consola visual
  const addLog = (index, emoji, message, type = 'text') => {
    setAgentLogs(prev => ({
      ...prev,
      [index]: [...(prev[index] || []), { emoji, message, type, time: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit', second:'2-digit'}) }]
    }));
  };

  const runAutonomousAgents = async (ticket, index) => {
    // 1. Inicialización
    setAgentState(prev => ({ ...prev, [index]: 'WORKING' }));
    setAgentLogs(prev => ({ ...prev, [index]: [] })); // Limpiar logs anteriores
    
    try {
      // --- PASO 1: AGENTE INVESTIGADOR ---
      addLog(index, '🕵️‍♂️', 'Agente Investigador: Iniciando análisis del problema...', 'info');
      addLog(index, '🌐', `Buscando contexto técnico para: "${ticket.tipo}"...`);
      
      const resInv = await axios.post('http://127.0.0.1:8000/api/investigacion', ticket);
      let currentSolucion = resInv.data;
      
      addLog(index, '📝', 'Investigador: Borrador de solución generado.', 'success');

// --- BUCLE DE MEJORA CONTINUA (AUTO-HEALING) ---
      let intentos = 0;
      let aprobado = false;
      let auditoriaFinal = null;
      const MAX_INTENTOS = 4; // Aumentamos intentos porque ahora tenemos espera automática
      const SCORE_MINIMO = 95; // Exigencia de excelencia

      while (intentos < MAX_INTENTOS && !aprobado) {
        intentos++;
        addLog(index, '🛡️', `Auditor: Revisión de calidad (Ciclo ${intentos}/${MAX_INTENTOS})...`, 'info');
        
        // 2. AUDITORÍA
        const resAud = await axios.post('http://127.0.0.1:8000/api/auditoria', { 
          ticket, 
          solucion_detallada: currentSolucion.solucion_detallada 
        });
        auditoriaFinal = resAud.data;

        // Evaluación
        if (auditoriaFinal.score >= SCORE_MINIMO) {
          addLog(index, '✨', `AUDITOR: ¡EXCELENTE! Score: ${auditoriaFinal.score}/100. Aprobado.`, 'success');
          aprobado = true;
        } else {
          addLog(index, '⚠️', `Auditor: Rechazado (Score: ${auditoriaFinal.score}). Detectando fallos...`, 'warning');
          
          if (intentos < MAX_INTENTOS) {
            // Mensaje de espera visual para el usuario
            addLog(index, '⏳', 'Sistema: Optimizando solución con búsqueda adicional...', 'info');
            
            // 3. REFINAMIENTO (INGENIERO INVESTIGADOR)
            const resRef = await axios.post('http://127.0.0.1:8000/api/refinar', {
              ticket,
              solucion_anterior: currentSolucion.solucion_detallada,
              reporte_auditoria: auditoriaFinal
            });
            currentSolucion = resRef.data;
            addLog(index, '🚀', 'Ingeniero: Nueva versión v' + (intentos + 1) + ' generada.', 'success');
          }
        }
      }

      if (!aprobado) {
        addLog(index, '🏁', 'Sistema: Límite de ciclos alcanzado. Entregando mejor versión disponible.', 'warning');
      }

      // 3. Finalización y Guardado
      setSolucionesFinales(prev => ({
        ...prev,
        [index]: { investigacion: currentSolucion, auditoria: auditoriaFinal }
      }));
      setAgentState(prev => ({ ...prev, [index]: 'DONE' }));

    } catch (e) {
      console.error(e);
      addLog(index, '❌', `Error crítico en el sistema de agentes: ${e.message}`, 'error');
      setAgentState(prev => ({ ...prev, [index]: 'ERROR' }));
    }
  };

  // --- FASE 4: APROBACIÓN MANUAL ---
  const aprobarTicket = async (ticket, index) => {
    setLoading(true); setPost(null);
    try {
      // Usamos la solución refinada por los agentes
      const solucion = solucionesFinales[index]?.investigacion.solucion_detallada || ticket.solucion;
      const res = await axios.post('http://127.0.0.1:8000/api/combinacion', { ticket, solucion_detallada: solucion });
      setPost(res.data);
      setFaseActual(4);
    } catch (e) { alert("Error Generando Post."); } finally { setLoading(false); }
  };


  // ========================================================================
  // UX & VISUALIZACIÓN (MODAL, PDF, ESTILOS)
  // ========================================================================

  const abrirModal = (ticket, index) => {
    const data = solucionesFinales[index];
    if (data) {
      setModalData({ ticket, investigacion: data.investigacion, auditoria: data.auditoria });
      setModalOpen(true);
    }
  };

const generarPDF = () => {
    if (!modalData) return;
    const doc = new jsPDF({ format: 'a4' }); // Forzar formato A4
    const { ticket, investigacion, auditoria } = modalData;
    
    let yPos = 20;
    const pageHeight = doc.internal.pageSize.height;
    const margin = 20;
    const maxWidth = 170;

    // Función auxiliar para saltar página si falta espacio
    const checkPageBreak = (addY) => {
      if (yPos + addY > pageHeight - margin) {
        doc.addPage();
        yPos = margin;
      }
    };

    // Título
    doc.setFont("helvetica", "bold");
    doc.setFontSize(18);
    doc.text("Informe Técnico SECAI", margin, yPos);
    yPos += 10;
    
    // Info del Ticket
    doc.setFontSize(11);
    doc.setFont("helvetica", "normal");
    doc.text(`Ticket: ${ticket.titulo}`, margin, yPos);
    yPos += 6;
    doc.text(`Prioridad: ${ticket.prioridad} | Tipo: ${ticket.tipo}`, margin, yPos);
    yPos += 10;

    // Resultado de Auditoría (Si existe)
    if (auditoria) {
      doc.setFont("helvetica", "bold");
      const color = auditoria.estado === 'APROBADO' ? [0, 128, 0] : [200, 0, 0];
      doc.setTextColor(...color);
      doc.text(`DICTAMEN AUDITORÍA: ${auditoria.estado} (Score: ${auditoria.score}/100)`, margin, yPos);
      doc.setTextColor(0); // Reset a negro
      yPos += 10;
    }

    doc.setLineWidth(0.5);
    doc.line(margin, yPos, 210 - margin, yPos);
    yPos += 10;
    
    // Contenido Técnico
    doc.setFontSize(12);
    doc.setFont("helvetica", "bold");
    doc.text("Solución Técnica Detallada:", margin, yPos);
    yPos += 8;
    
    doc.setFont("helvetica", "normal");
    doc.setFontSize(10);
    
    // Limpieza de Markdown para texto plano
    const rawText = investigacion.solucion_detallada || "Sin detalle.";
    const cleanText = rawText
      .replace(/###/g, "")      // Quitar títulos MD
      .replace(/\*\*/g, "")     // Quitar negritas MD
      .replace(/- /g, "• ")     // Listas bonitas
      .replace(/`/g, "");       // Quitar backticks
      
    // Dividir texto en líneas para ajustar al ancho
    const textLines = doc.splitTextToSize(cleanText, maxWidth);
    
    // Escribir línea por línea controlando paginación
    textLines.forEach(line => {
      checkPageBreak(5);
      doc.text(line, margin, yPos);
      yPos += 5;
    });
    
    yPos += 10;
    
    // Fuentes / Referencias
    checkPageBreak(20);
    if (investigacion.fuentes && investigacion.fuentes.length > 0) {
      doc.setFont("helvetica", "bold");
      doc.text("Referencias y Fuentes:", margin, yPos);
      yPos += 8;
      
      doc.setFont("helvetica", "normal");
      doc.setTextColor(0, 0, 255); // Azul link
      
      investigacion.fuentes.forEach((f) => {
        checkPageBreak(6);
        const linkTitle = `• ${f.titulo || "Enlace externo"}`;
        doc.textWithLink(linkTitle, margin, yPos, { url: f.url || "#" });
        yPos += 6;
      });
    }
    
    // Guardar archivo
    doc.save(`SECAI_Reporte_${ticket.titulo.substring(0, 10).replace(/\s/g, '_')}.pdf`);
  };

  // Helpers de Estilo
  const getBorderColor = (p) => (p?.toLowerCase() === 'alta' ? 'border-l-orange-500' : p?.toLowerCase() === 'media' ? 'border-l-yellow-500' : 'border-l-green-500');
  const getBadgeColor = (p) => {
      const prio = p?.toLowerCase() || 'media';
      if (prio === 'alta') return 'text-orange-400 bg-orange-950/30 border border-orange-500/60 shadow-[0_0_8px_rgba(251,146,60,0.3)]';
      if (prio === 'media') return 'text-yellow-400 bg-yellow-950/30 border border-yellow-500/60';
      return 'text-green-400 bg-green-950/30 border border-green-500/60';
    };
  const getAuditColor = (s) => (s === 'APROBADO' ? 'text-green-400 border-green-500/30 bg-green-500/10' : s === 'OBSERVADO' ? 'text-yellow-400 border-yellow-500/30 bg-yellow-500/10' : 'text-red-400 border-red-500/30 bg-red-500/10');


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
              <p className="text-xs text-indigo-300 uppercase tracking-widest font-semibold">Autonomous Multi-Agent System</p>
            </div>
          </div>
          <div className="flex gap-2 bg-slate-900/50 p-2 rounded-full border border-slate-800">
            {[1, 2, 3, 4].map(s => <div key={s} className={`h-2 w-8 md:w-12 rounded-full transition-all duration-700 ${faseActual >= s ? 'bg-gradient-to-r from-cyan-500 to-purple-500 shadow-[0_0_8px_rgba(168,85,247,0.5)]' : 'bg-slate-800'}`} />)}
          </div>
        </div>
      </header>

      <main className="grid grid-cols-1 lg:grid-cols-2 gap-6 md:gap-8">
        
        {/* FASES 1 y 2 */}
        <section className={`bg-[#0b1121] border border-slate-800 rounded-2xl p-6 shadow-xl ${faseActual === 1 ? 'ring-1 ring-cyan-500/50' : ''}`}>
          <h2 className="text-lg font-bold mb-4 text-gray-100 flex items-center gap-2">1. Socialización <span className="text-xl">🗣️</span></h2>
          <div className="flex flex-wrap items-center gap-4 mb-4">
            <button onClick={fetchComentarios} disabled={loading} className="bg-gradient-to-r from-cyan-600 to-blue-600 hover:to-blue-500 text-white font-semibold py-2 px-6 rounded-full active:scale-95 disabled:opacity-50 shadow-lg shadow-cyan-900/30 transition-all">
              {loading && faseActual === 1 ? 'Escuchando...' : '📡 Escuchar'}
            </button>
            <span className="text-sm font-mono text-slate-400 bg-slate-900 px-3 py-1 rounded-md border border-slate-800">{comentarios.length} comentarios</span>
          </div>
          <div className="bg-slate-950/50 rounded-xl border border-slate-800/60 h-72 overflow-y-auto p-3 space-y-2 custom-scrollbar">
            {comentarios.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-slate-600 gap-3">
                <span className="text-4xl opacity-20">💬</span><span className="text-sm italic">Esperando conexión...</span>
              </div>
            ) : (
              comentarios.map((c, i) => <div key={i} className="bg-[#131c31] p-3 rounded-lg border border-slate-800/80 text-xs text-slate-300 hover:border-slate-700 transition-colors"><strong className="text-cyan-500 mr-1">#{i+1}</strong> {c}</div>)
            )}
          </div>
        </section>

        <section className={`bg-[#0b1121] border border-slate-800 rounded-2xl p-6 shadow-xl ${faseActual === 2 ? 'ring-1 ring-purple-500/50' : ''}`}>
          <h2 className="text-lg font-bold mb-4 text-gray-100 flex items-center gap-2">2. Exteriorización <span className="text-xl">⚙️</span></h2>
          <div className="mb-4">
            <button onClick={analizarInsights} disabled={loading || !comentarios.length} className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:to-pink-500 text-white font-semibold py-2 px-6 rounded-full active:scale-95 disabled:opacity-50 shadow-lg shadow-purple-900/30 transition-all flex items-center justify-center gap-2">
              {loading && faseActual === 2 ? <span className="animate-pulse">Analizando...</span> : '⚡ Procesar Insights'}
            </button>
          </div>
          <div className="h-72 overflow-y-auto pr-2 custom-scrollbar space-y-3">
            {tickets.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-slate-600 border-2 border-dashed border-slate-800/50 rounded-xl gap-3">
                <span className="text-4xl opacity-20">🧩</span><span className="text-sm italic">Los tickets generados aparecerán aquí</span>
              </div>
            ) : (
              tickets.map((t, i) => (
                <div key={i} className={`bg-slate-900/80 rounded-xl p-4 border-l-4 ${getBorderColor(t.prioridad)} border-y border-r border-slate-800 shadow-md`}>
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
        <section className={`bg-[#0b1121] border border-slate-800 rounded-2xl p-6 shadow-xl ${faseActual === 4 ? 'ring-1 ring-green-500/50 opacity-100' : 'opacity-70 grayscale-[0.5]'}`}>
          <h2 className="text-lg font-bold mb-4 text-gray-100 flex items-center gap-2">4. Internalización <span className="text-xl">📢</span></h2>
          <div className="h-[500px] overflow-y-auto custom-scrollbar bg-slate-950/30 rounded-xl border border-slate-800 p-4 relative">
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
                <span className="text-4xl opacity-20">🖼️</span><span className="text-sm italic">El post generado aparecerá aquí</span>
              </div>
            )}
          </div>
        </section>

        {/* 3. COMBINACIÓN (SUPER AGENTE) */}
        <section className={`bg-[#0b1121] border border-slate-800 rounded-2xl p-6 shadow-xl ${faseActual === 3 ? 'ring-1 ring-yellow-500/50 opacity-100' : 'opacity-70'}`}>
          <h2 className="text-lg font-bold mb-4 text-gray-100 flex items-center gap-2">3. Combinación (Agentes Autónomos) 🤖</h2>
          <div className="h-[500px] overflow-y-auto pr-2 custom-scrollbar space-y-6">
            {tickets.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-slate-600 border-2 border-dashed border-slate-800/50 rounded-xl gap-3">
                <span className="text-4xl opacity-20">🧠</span><span className="text-sm italic">Esperando tickets para orquestar...</span>
              </div>
            ) : (
              tickets.map((t, i) => (
                <div key={i} className="bg-slate-900/40 border border-slate-800 rounded-xl p-5 hover:border-slate-600 transition-all shadow-sm">
                  
                  <div className="flex justify-between items-start mb-4">
                    <h3 className="font-bold text-slate-200 text-sm flex-1 mr-2">{t.titulo}</h3>
                    <span className={`text-[10px] uppercase px-2 py-0.5 rounded border ${getBorderColor(t.prioridad)}`}>{t.prioridad}</span>
                  </div>

                  {/* ESTADO INICIAL: Botón de Activación */}
                  {!agentState[i] && (
                    <button 
                      onClick={() => runAutonomousAgents(t, i)}
                      className="w-full py-3 bg-gradient-to-r from-cyan-900/40 to-blue-900/40 hover:from-cyan-800/50 hover:to-blue-800/50 border border-cyan-700/30 rounded-lg text-xs font-bold text-cyan-200 transition-all flex justify-center items-center gap-2 group"
                    >
                      <span className="group-hover:animate-spin">⚙️</span> Iniciar Ciclo de Agentes (Investigar + Auditar)
                    </button>
                  )}

                  {/* ESTADO PROCESANDO: Consola de Agentes */}
                  {(agentState[i] === 'WORKING' || agentState[i] === 'DONE' || agentState[i] === 'ERROR') && (
                    <div className="space-y-3 animate-in fade-in zoom-in duration-300">
                      <div className="flex justify-between items-center text-[10px] text-slate-400 uppercase tracking-wider font-bold mb-1">
                        <span>Terminal de Operaciones</span>
                        {agentState[i] === 'WORKING' && <span className="animate-pulse text-green-400">● Ejecutando</span>}
                        {agentState[i] === 'DONE' && <span className="text-blue-400">● Finalizado</span>}
                      </div>
                      
                      {/* Componente Consola */}
                      <AgentConsole logs={agentLogs[i]} />

                      {/* Botones Finales (Solo si terminó) */}
                      {agentState[i] === 'DONE' && (
                        <div className="flex gap-2 mt-2">
                          <button onClick={() => abrirModal(t, i)} className="flex-1 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-[10px] rounded border border-slate-600 transition-colors flex items-center justify-center gap-2">
                            <span>📄</span> Ver Reporte Final
                          </button>
                          <button onClick={() => aprobarTicket(t, i)} disabled={loading} className="flex-1 py-2 bg-green-600 hover:bg-green-500 text-white text-[10px] font-bold rounded shadow-lg shadow-green-900/20 transition-colors flex items-center justify-center gap-2">
                            <span>✅</span> Aprobar
                          </button>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </section>
      </main>

      {/* --- MODAL DETALLE COMPLETO (Estilo Google Drive Preview) --- */}
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
              <div className="max-w-3xl mx-auto bg-[#0f172a] p-8 md:p-12 rounded-lg shadow-lg border border-slate-800 min-h-full">
                
                {/* Título del Documento */}
                <h1 className="text-3xl font-bold text-white mb-2">{modalData.ticket.titulo}</h1>
                <div className="flex gap-4 text-xs text-slate-400 mb-8 border-b border-slate-700 pb-4">
                  <span>TIPO: <strong className="text-slate-200 uppercase">{modalData.ticket.tipo}</strong></span>
                  <span>PRIORIDAD: <strong className="text-slate-200 uppercase">{modalData.ticket.prioridad}</strong></span>
                </div>

                <div className="text-slate-300 leading-7 space-y-4 text-sm md:text-base">
                  <h3 className="text-xl font-bold text-cyan-400 mb-2">1. Solución Técnica Optimizada</h3>
                  <ReactMarkdown 
                    components={{
                      h1: ({node, ...props}) => <h4 className="text-lg font-bold text-purple-400 mt-4 mb-2" {...props} />,
                      h2: ({node, ...props}) => <h5 className="text-base font-bold text-slate-200 mt-3 mb-1" {...props} />,
                      h3: ({node, ...props}) => <h6 className="text-sm font-bold text-slate-300 mt-2" {...props} />,
                      ul: ({node, ...props}) => <ul className="list-disc pl-5 space-y-1 my-2" {...props} />,
                      li: ({node, ...props}) => <li className="pl-1" {...props} />,
                      strong: ({node, ...props}) => <strong className="text-white font-bold" {...props} />
                    }}
                  >
                    {modalData.investigacion.solucion_detallada}
                  </ReactMarkdown>
                </div>

                {/* Sección de Auditoría en el Modal */}
                {modalData.auditoria && (
                  <div className={`mt-8 p-6 rounded-xl border ${getAuditColor(modalData.auditoria.estado)} bg-slate-900/50`}>
                    <h3 className="text-lg font-bold flex justify-between items-center border-b border-white/10 pb-2 mb-4">
                      2. Dictamen del Auditor (Final)
                      <span className="text-sm bg-black/30 px-3 py-1 rounded">Score: {modalData.auditoria.score}/100</span>
                    </h3>
                    <p className="italic text-sm mb-4 opacity-90">"{modalData.auditoria.analisis_breve}"</p>
                    
                    <div className="grid md:grid-cols-2 gap-6 text-sm">
                      <div>
                        <strong className="text-red-400 uppercase text-xs block mb-2">Riesgos Residuales:</strong>
                        {modalData.auditoria.riesgos_detectados?.length > 0 ? (
                          <ul className="list-disc pl-4 space-y-1 text-slate-400">
                            {modalData.auditoria.riesgos_detectados.map((r, i) => <li key={i}>{r}</li>)}
                          </ul>
                        ) : <span className="text-slate-500 italic">Ninguno detectado.</span>}
                      </div>
                      <div>
                        <strong className="text-green-400 uppercase text-xs block mb-2">Puntos Fuertes:</strong>
                        <ul className="list-disc pl-4 space-y-1 text-slate-400">
                          {modalData.auditoria.recomendaciones?.map((r, i) => <li key={i}>{r}</li>)}
                        </ul>
                      </div>
                    </div>
                  </div>
                )}

                <div className="mt-12 pt-8 border-t border-slate-700/50">
                  <h3 className="text-sm font-bold text-slate-500 uppercase tracking-widest mb-4">Fuentes Consultadas</h3>
                  {modalData.investigacion.fuentes?.length > 0 ? (
                    <ul className="grid gap-2">
                      {modalData.investigacion.fuentes.map((f, idx) => (
                        <li key={idx} className="flex items-center gap-2 text-sm">
                          <span>🔗</span> <a href={f.url} target="_blank" rel="noopener noreferrer" className="text-cyan-500 hover:underline truncate">{f.titulo || f.url}</a>
                        </li>
                      ))}
                    </ul>
                  ) : <p className="text-sm text-slate-600 italic">Investigación interna del modelo.</p>}
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