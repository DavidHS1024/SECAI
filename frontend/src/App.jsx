import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
// Eliminamos la importación de ReactMarkdown que causa conflicto con React 19
// import ReactMarkdown from 'react-markdown'; 
import { jsPDF } from "jspdf";
import PropTypes from 'prop-types';

// --- COMPONENTE: RENDERIZADOR DE TEXTO SEGURO ---
// Reemplazo robusto para evitar crashes con React 19
const SafeTextRenderer = ({ content }) => {
  if (!content) return null;
  // Convertimos markdown básico a formato legible
  const cleanContent = content
    .replace(/\*\*(.*?)\*\*/g, '$1') // Negritas
    .replace(/##/g, '')             // Títulos
    .replace(/```/g, '')            // Bloques de código
    .replace(/^-\s/gm, '• ');       // Listas

  return (
    <div className="whitespace-pre-wrap font-sans text-slate-300 text-sm leading-relaxed">
      {cleanContent}
    </div>
  );
};
SafeTextRenderer.propTypes = { content: PropTypes.string };

// --- COMPONENTE: HILO DE COMENTARIOS ---
const CommentThread = ({ comment, isReply = false, onReplySuccess, isHighlighted = false }) => {
  const [showInput, setShowInput] = useState(false);
  const [replyText, setReplyText] = useState("");
  const [sending, setSending] = useState(false);

  if (!comment) return null;

  const handleSendReply = async () => {
    if (!replyText.trim()) return;
    setSending(true);
    try {
      await axios.post('[http://127.0.0.1:8000/api/socializacion/responder](http://127.0.0.1:8000/api/socializacion/responder)', {
        padre_id: comment.id,
        usuario: "Soporte Yape (IA)",
        texto: replyText
      });
      setReplyText("");
      setShowInput(false);
      if (onReplySuccess) onReplySuccess();
    } catch (e) {
      console.error(e);
      alert("Error enviando respuesta");
    } finally {
      setSending(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') handleSendReply();
  };

  const highlightClasses = isHighlighted 
    ? "ring-2 ring-cyan-400 bg-cyan-900/30 shadow-[0_0_15px_rgba(34,211,238,0.3)] transform scale-[1.02] transition-all duration-300" 
    : "border border-slate-700/50 hover:border-slate-600 transition-all duration-300";

  return (
    <div id={`comment-${comment.id}`} className={`flex gap-3 ${isReply ? 'ml-10 mt-3 border-l-2 border-slate-800 pl-3' : 'mb-4'}`}>
      <div className={`shrink-0 rounded-full flex items-center justify-center font-bold text-white shadow-lg 
        ${isReply ? 'w-8 h-8 text-[10px] bg-slate-700' : 'w-10 h-10 text-xs bg-gradient-to-br from-cyan-600 to-blue-700'}`}>
        {comment.user ? comment.user.charAt(0) : '?'}
      </div>

      <div className="flex-1 min-w-0">
        <div className={`bg-[#1e293b] rounded-2xl rounded-tl-none p-3 shadow-sm ${highlightClasses}`}>
          <div className="flex justify-between items-baseline mb-1">
            <span className="font-bold text-slate-200 text-xs">{comment.user}</span>
            <span className="text-[10px] text-slate-500">{isReply ? 'Respondió' : 'Comentó'}</span>
          </div>
          <p className="text-sm text-slate-300 leading-relaxed whitespace-pre-wrap">{comment.text}</p>
        </div>
        
        <div className="flex gap-4 mt-1 ml-2 text-[10px] font-semibold text-slate-500 items-center">
          <button className="hover:text-cyan-400 transition-colors flex items-center gap-1"><span>👍</span> {comment.likes}</button>
          <button onClick={() => setShowInput(!showInput)} className="hover:text-cyan-400 transition-colors text-cyan-600">
            {showInput ? 'Cancelar' : 'Responder'}
          </button>
          <span className="font-normal opacity-50">Hace un momento</span>
        </div>

        {showInput && (
          <div className="mt-3 animate-in fade-in slide-in-from-top-2 duration-200">
            <div className="flex gap-2">
              <input 
                type="text" value={replyText} onChange={(e) => setReplyText(e.target.value)}
                placeholder={`Responder a ${comment.user}...`}
                className="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-cyan-500 transition-colors"
                onKeyDown={handleKeyDown}
              />
              <button onClick={handleSendReply} disabled={sending} className="bg-cyan-600 hover:bg-cyan-500 text-white px-3 py-1 rounded-lg text-xs font-bold transition-colors disabled:opacity-50">
                {sending ? '...' : 'Enviar'}
              </button>
            </div>
          </div>
        )}

        {comment.replies && comment.replies.length > 0 && (
          <div className="mt-2">
            {comment.replies.map((reply) => (
              <CommentThread key={reply.id} comment={reply} isReply={true} onReplySuccess={onReplySuccess} isHighlighted={isHighlighted} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

CommentThread.propTypes = {
  comment: PropTypes.object,
  isReply: PropTypes.bool,
  onReplySuccess: PropTypes.func,
  isHighlighted: PropTypes.bool
};

// --- COMPONENTE: CONSOLA DE AGENTE ---
const AgentConsole = ({ logs }) => {
  const scrollRef = useRef(null);
  
  useEffect(() => { 
    if (scrollRef.current) {
        scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div ref={scrollRef} className="bg-[#050b14] font-mono text-[11px] p-4 rounded-lg border border-slate-700/50 h-48 overflow-y-auto custom-scrollbar shadow-inner relative group scroll-smooth">
      <div className="absolute inset-0 bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.25)_50%),linear-gradient(90deg,rgba(255,0,0,0.06),rgba(0,255,0,0.02),rgba(0,0,255,0.06))] z-0 pointer-events-none opacity-20"></div>
      <div className="relative z-10 space-y-2">
        {logs?.map((log, i) => (
          <div key={i} className="flex gap-3 animate-in fade-in slide-in-from-left-2 duration-300">
            <span className="text-slate-600 shrink-0 font-bold">[{log.time}]</span>
            <span className="shrink-0">{log.emoji}</span> 
            <span className={`break-words leading-tight ${
              log.type === 'error' ? 'text-red-400 font-bold' : 
              log.type === 'success' ? 'text-green-400 font-bold' : 
              log.type === 'warning' ? 'text-yellow-400' : 
              log.type === 'info' ? 'text-cyan-300' : 'text-slate-300'
            }`}>
              {log.message}
            </span>
          </div>
        ))}
        {!logs?.length && <div className="text-slate-700 italic text-center mt-10">Esperando inicialización de agentes...</div>}
      </div>
    </div>
  );
};
AgentConsole.propTypes = { logs: PropTypes.array };

// --- APP PRINCIPAL ---
function App() {
  const [comentarios, setComentarios] = useState([]);
  const [tickets, setTickets] = useState([]);
  const [post, setPost] = useState(null);
  const [agentLogs, setAgentLogs] = useState({}); 
  const [agentState, setAgentState] = useState({}); 
  const [solucionesFinales, setSolucionesFinales] = useState({});
  const [loading, setLoading] = useState(false); 
  const [faseActual, setFaseActual] = useState(1);
  const [modalOpen, setModalOpen] = useState(false);
  const [modalData, setModalData] = useState(null);
  const [highlightedIds, setHighlightedIds] = useState([]);
  const [expandedReasoningId, setExpandedReasoningId] = useState(null);

// --- API CON DEBUGGING ---
  const fetchComentarios = async () => {
    setLoading(true);
    try {
      console.log("📡 Solicitando comentarios...");
      const res = await axios.get('http://127.0.0.1:8000/api/socializacion');
      
      console.log("📦 Respuesta Backend:", res.data); // <--- MIRA ESTO EN CONSOLA (F12)

      // Validación más flexible
      if (res.data && res.data.comentarios) {
        // Si es un array, lo usamos. Si no, intentamos convertirlo o usar array vacío
        const dataArray = Array.isArray(res.data.comentarios) ? res.data.comentarios : [];
        
        if (dataArray.length === 0) {
            console.warn("⚠️ El array de comentarios llegó vacío.");
        }

        setComentarios(dataArray);
        setFaseActual(2);
      } else {
        console.error("❌ Estructura incorrecta:", res.data);
        alert(`Error de formato: El backend no devolvió una lista válida.\nRevisa la consola (F12) para ver detalles.`);
      }
    } catch (e) { 
      console.error("❌ Error de Red/Axios:", e); 
      setComentarios([]); 
      alert("Error de Conexión: Verifica que el backend (uvicorn) esté corriendo."); 
    } finally { 
      setLoading(false); 
    }
  };

const analizarInsights = async () => {
    if (!comentarios || comentarios.length === 0) return alert("Faltan comentarios para analizar.");
    
    setLoading(true);
    console.log("🚀 Enviando solicitud a /api/exteriorizacion...");

    try {
      const comentariosTexto = comentarios.map(c => `[ID: ${c.id}] Usuario: ${c.user} Dijo: ${c.text}`);
      
      const res = await axios.post('http://127.0.0.1:8000/api/exteriorizacion', { 
        comentarios: comentariosTexto 
      });

      console.log("✅ Respuesta recibida:", res.data);
      setTickets(res.data);
      setFaseActual(3);

    } catch (e) {
      console.error("❌ ERROR DETALLADO:", e);
      
      let mensaje = "Error desconocido.";
      if (e.response) {
        // El servidor respondió con un código de error (4xx, 5xx)
        mensaje = `El servidor respondió error ${e.response.status}: ${JSON.stringify(e.response.data)}`;
      } else if (e.request) {
        // La petición se envió pero no hubo respuesta (CORS o Red)
        mensaje = "No hubo respuesta del servidor. Posible bloqueo CORS o Backend apagado.";
      } else {
        mensaje = `Error al configurar la petición: ${e.message}`;
      }

      alert(`Error IA:\n${mensaje}\n\n(Revisa la consola con F12 para más detalles)`);
    } finally { 
      setLoading(false); 
    }
  };

  // --- LOGICA DE AGENTES ---
  const addLog = (index, emoji, message, type = 'text') => {
    setAgentLogs(prev => ({
      ...prev,
      [index]: [...(prev[index] || []), { emoji, message, type, time: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit', second:'2-digit'}) }]
    }));
  };

  const runAutonomousAgents = async (ticket, index) => {
    setAgentState(prev => ({ ...prev, [index]: 'WORKING' }));
    setAgentLogs(prev => ({ ...prev, [index]: [] }));
    
    addLog(index, '🚀', 'Conectando con SECAI o3 Engine...', 'info');

    try {
      const response = await fetch('[http://127.0.0.1:8000/api/investigacion](http://127.0.0.1:8000/api/investigacion)', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(ticket)
      });

      if (!response.ok) throw new Error('Error en conexión con el Agente');

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop(); 

        for (const line of lines) {
          if (!line.trim()) continue;
          try {
            const data = JSON.parse(line);
            
            if (data.type === 'log') {
                addLog(index, data.emoji, data.message, data.level || 'text');
            } else if (data.type === 'result') {
                setSolucionesFinales(prev => ({ 
                    ...prev, 
                    [index]: { 
                        investigacion: data.data.investigacion, 
                        auditoria: data.data.auditoria 
                    } 
                }));
            } else if (data.type === 'error') {
                addLog(index, '❌', data.message, 'error');
                throw new Error(data.message);
            }
          } catch (err) {
            console.warn("Chunk JSON incompleto:", err);
          }
        }
      }
      setAgentState(prev => ({ ...prev, [index]: 'DONE' }));

    } catch (e) {
      console.error(e);
      addLog(index, '💀', `Conexión perdida: ${e.message}`, 'error');
      setAgentState(prev => ({ ...prev, [index]: 'ERROR' }));
    }
  };

  const aprobarTicket = async (ticket, index) => {
    setLoading(true); setPost(null);
    try {
      const solucion = solucionesFinales[index]?.investigacion.solucion_detallada || ticket.solucion;
      const res = await axios.post('[http://127.0.0.1:8000/api/combinacion](http://127.0.0.1:8000/api/combinacion)', { ticket, solucion_detallada: solucion });
      setPost(res.data);
      setFaseActual(4);
    } catch (e) { console.error(e); alert("Error Generando Post."); } finally { setLoading(false); }
  };

  // --- PDF ---
  const generarPDF = () => {
    if (!modalData) return;
    const doc = new jsPDF({ format: 'a4' });
    const { ticket, investigacion, auditoria } = modalData;
    const margin = 20;
    const pageHeight = doc.internal.pageSize.height;
    let y = 20;

    const printTextBlock = (title, textContent, isBoldTitle = true) => {
      let cleanText = (textContent || "N/A")
        .replace(/\*\*(.*?)\*\*/g, '$1')
        .replace(/##/g, '')
        .replace(/```/g, '')
        .replace(/^\s*[\r\n]/gm, '');

      if (y > pageHeight - 40) { doc.addPage(); y = 20; }
      doc.setFont("helvetica", isBoldTitle ? "bold" : "normal");
      doc.setFontSize(11);
      doc.setTextColor(0, 0, 0);
      doc.text(title, margin, y);
      y += 6;
      doc.setFont("helvetica", "normal");
      doc.setFontSize(10);
      doc.setTextColor(60, 60, 60);
      const lines = doc.splitTextToSize(cleanText, 170);
      lines.forEach(line => {
        if (y > pageHeight - 20) { doc.addPage(); y = 20; }
        doc.text(line, margin, y);
        y += 5;
      });
      y += 5; 
    };

    doc.setFontSize(18); doc.setFont("helvetica", "bold");
    doc.text("INFORME TÉCNICO", margin, y); y += 10;
    
    doc.setFontSize(10);
    doc.text(`TICKET: ${ticket?.titulo || "Sin Título"}`, margin, y); y += 5;
    
    if (auditoria) {
      doc.setTextColor(auditoria.score >= 90 ? 0 : 200, auditoria.score >= 90 ? 100 : 0, 0);
      doc.text(`SCORE: ${auditoria.score}/100 (${auditoria.estado})`, margin, y);
      doc.setTextColor(0);
    }
    y += 10; doc.line(margin, y, 190, y); y += 10;

    if (investigacion?.analisis_causa_raiz) printTextBlock("1. CAUSA RAÍZ", investigacion.analisis_causa_raiz, true);
    if (investigacion?.solucion_detallada) printTextBlock("2. SOLUCIÓN TÉCNICA", investigacion.solucion_detallada, true);
    if (investigacion?.plan_rollback) printTextBlock("3. ROLLBACK", investigacion.plan_rollback, true);

    doc.save(`Reporte_SECAI.pdf`);
  };

  const getBorderColor = (p) => (p?.toLowerCase() === 'alta' ? 'border-l-orange-500' : p?.toLowerCase() === 'media' ? 'border-l-yellow-500' : 'border-l-green-500');

  // --- RENDER ---
  return (
    <div className="min-h-screen bg-[#020617] text-slate-100 font-sans p-4 md:p-8 relative selection:bg-cyan-500/30">
      <header className="relative bg-[#020617] border border-slate-800 rounded-2xl p-6 mb-8 shadow-2xl overflow-hidden">
        <div className="absolute top-0 left-0 w-64 h-64 bg-cyan-500/10 blur-[80px] rounded-full -translate-x-1/2 -translate-y-1/2"></div>
        <div className="relative z-10 flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-cyan-400 to-purple-600 flex items-center justify-center text-2xl shadow-lg ring-1 ring-white/10">🌀</div>
            <div>
              <h1 className="text-2xl font-bold text-gray-50 tracking-tight">SECAI <span className="text-xs text-cyan-400 border border-cyan-900 bg-cyan-950/50 px-2 py-0.5 rounded ml-2">o3 Engine</span></h1>
              <p className="text-xs text-indigo-300 uppercase tracking-widest font-semibold">Sistema de Conocimiento Autónomo</p>
            </div>
          </div>
          <div className="flex gap-2 bg-slate-900/50 p-2 rounded-full border border-slate-800">
            {[1, 2, 3, 4].map(s => <div key={s} className={`h-2 w-8 md:w-12 rounded-full transition-all duration-700 ${faseActual >= s ? 'bg-gradient-to-r from-cyan-500 to-purple-500 shadow-[0_0_8px_rgba(168,85,247,0.5)]' : 'bg-slate-800'}`} />)}
          </div>
        </div>
      </header>

      <main className="grid grid-cols-1 lg:grid-cols-2 gap-6 md:gap-8">
        
        {/* 1. SOCIALIZACIÓN */}
        <section className={`bg-[#0b1121] border border-slate-800 rounded-2xl p-6 shadow-xl ${faseActual === 1 ? 'ring-1 ring-cyan-500/50' : ''}`}>
          <h2 className="text-lg font-bold mb-4 text-gray-100 flex items-center gap-2">1. Socialización <span className="text-xl">🗣️</span></h2>
          <div className="flex flex-wrap items-center gap-4 mb-4">
            <button onClick={fetchComentarios} disabled={loading} className="bg-gradient-to-r from-cyan-600 to-blue-600 hover:to-blue-500 text-white font-semibold py-2 px-6 rounded-full active:scale-95 disabled:opacity-50 shadow-lg shadow-cyan-900/30 transition-all">
              {loading && faseActual === 1 ? 'Conectando...' : '📡 Escuchar Redes'}
            </button>
            <span className="text-sm font-mono text-slate-400 bg-slate-900 px-3 py-1 rounded-md border border-slate-800">{comentarios.length} hilos</span>
          </div>
          <div className="bg-slate-950/50 rounded-xl border border-slate-800/60 h-[600px] overflow-y-auto p-4 custom-scrollbar">
            {comentarios.length === 0 ? <div className="text-center mt-20 opacity-50">Esperando conexión...</div> : 
             (Array.isArray(comentarios) ? comentarios : []).map(c => <CommentThread key={c.id} comment={c} onReplySuccess={fetchComentarios} isHighlighted={highlightedIds.includes(c.id)} />)
            }
          </div>
        </section>

        {/* 2. EXTERIORIZACIÓN */}
        <section className={`bg-[#0b1121] border border-slate-800 rounded-2xl p-6 shadow-xl ${faseActual === 2 ? 'ring-1 ring-purple-500/50' : ''}`}>
          <h2 className="text-lg font-bold mb-4 text-gray-100 flex items-center gap-2">2. Exteriorización <span className="text-xl">⚙️</span></h2>
          <div className="mb-4">
            <button onClick={analizarInsights} disabled={loading || comentarios.length === 0} className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:to-pink-500 text-white font-semibold py-2 px-6 rounded-full active:scale-95 disabled:opacity-50 shadow-lg shadow-purple-900/30 transition-all">
              {loading && faseActual === 2 ? <span className="animate-pulse">Analizando...</span> : '⚡ Procesar Insights (o3)'}
            </button>
          </div>
          <div className="h-[600px] overflow-y-auto pr-2 custom-scrollbar space-y-4">
            {tickets.map((t, i) => (
                <div key={i} 
                  onMouseEnter={() => setHighlightedIds(t.fuentes_ids || [])}
                  onMouseLeave={() => setHighlightedIds([])}
                  onClick={() => setHighlightedIds(t.fuentes_ids || [])}
                  className={`relative group cursor-pointer bg-slate-900/80 rounded-xl p-4 border-l-4 ${getBorderColor(t.prioridad)} border-y border-r border-slate-800 shadow-md hover:bg-slate-800/80 transition-all hover:translate-x-1`}
                >
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="font-bold text-sm text-slate-100 pr-6">🎯 {t.titulo}</h3>
                    <button onClick={(e) => { e.stopPropagation(); setExpandedReasoningId(expandedReasoningId === i ? null : i); }} className="absolute top-3 right-3 text-slate-500 hover:text-white p-1">⋮</button>
                  </div>
                  <div className="flex flex-wrap gap-2 mb-3">
                    {t.tags?.map((tag, idx) => <span key={idx} className="text-[9px] font-bold uppercase px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 border border-slate-700">{tag}</span>)}
                  </div>
                  {expandedReasoningId === i && <div className="mb-3 p-3 bg-indigo-950/40 border border-indigo-500/30 rounded-lg text-xs text-indigo-200"><strong>💡 Razonamiento IA:</strong> {t.razonamiento}</div>}
                  <p className="text-xs text-slate-400 line-clamp-2 mb-2">{t.problema}</p>
                </div>
            ))}
          </div>
        </section>

        {/* 4. INTERNALIZACIÓN */}
        <section className={`bg-[#0b1121] border border-slate-800 rounded-2xl p-6 shadow-xl ${faseActual === 4 ? 'ring-1 ring-green-500/50 opacity-100' : 'opacity-70'}`}>
          <h2 className="text-lg font-bold mb-4 text-gray-100 flex items-center gap-2">4. Internalización <span className="text-xl">📢</span></h2>
          <div className="h-[400px] bg-slate-950/30 rounded-xl border border-slate-800 p-4">
            {post ? (
              <div className="space-y-4 animate-in fade-in">
                <div className="flex items-center gap-3"><div className="w-10 h-10 rounded-full bg-purple-600 flex items-center justify-center font-bold">Y</div><div><div className="text-sm font-bold text-slate-100">Yape Oficial</div><div className="text-xs text-slate-500">Ahora</div></div></div>
                <p className="text-sm text-slate-300">{post.texto_post}</p>
                {post.url_imagen && <img src={post.url_imagen} className="w-full rounded-xl border border-slate-800" alt="Post" />}
              </div>
            ) : <div className="text-center mt-20 opacity-50">El post generado aparecerá aquí.</div>}
          </div>
        </section>

        {/* 3. COMBINACIÓN */}
        <section className={`bg-[#0b1121] border border-slate-800 rounded-2xl p-6 shadow-xl ${faseActual === 3 ? 'ring-1 ring-yellow-500/50 opacity-100' : 'opacity-70'}`}>
          <h2 className="text-lg font-bold mb-4 text-gray-100 flex items-center gap-2">3. Combinación (Agentes) <span className="text-xl">🤖</span></h2>
          <div className="h-[400px] overflow-y-auto pr-2 custom-scrollbar space-y-6">
            {tickets.map((t, i) => (
              <div key={i} className="bg-slate-900/40 border border-slate-800 rounded-xl p-5">
                <h3 className="font-bold text-slate-200 text-sm mb-4">{t.titulo}</h3>
                {!agentState[i] ? (
                  <button onClick={() => runAutonomousAgents(t, i)} className="w-full py-2 bg-slate-800 border border-slate-700 hover:border-cyan-500 rounded text-xs text-cyan-400 font-bold transition-all">▶ Iniciar Bucle de Calidad</button>
                ) : (
                  <div>
                    <AgentConsole logs={agentLogs[i]} />
                    {agentState[i] === 'DONE' && (
                      <div className="flex gap-2 mt-2">
                        <button 
                          onClick={() => { 
                            const finalData = solucionesFinales[i];
                            if (finalData && finalData.investigacion) {
                                setModalData({ ticket: t, investigacion: finalData.investigacion, auditoria: finalData.auditoria }); 
                                setModalOpen(true);
                            } else {
                                alert("Error: Datos incompletos del agente.");
                            }
                          }} 
                          disabled={!solucionesFinales[i]}
                          className={`flex-1 py-2 text-[10px] rounded border transition-all ${solucionesFinales[i] ? 'bg-slate-800 text-slate-300 border-slate-600 hover:bg-slate-700' : 'bg-slate-900 text-slate-600 border-slate-800 cursor-not-allowed'}`}
                        >
                          📄 Ver Reporte
                        </button>
                        <button onClick={() => aprobarTicket(t, i)} disabled={!solucionesFinales[i]} className={`flex-1 py-2 text-[10px] font-bold rounded transition-all ${solucionesFinales[i] ? 'bg-green-700 text-white hover:bg-green-600' : 'bg-slate-900 text-slate-700 cursor-not-allowed'}`}>
                          Aprobar
                        </button>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>

      </main>

      {/* MODAL BLINDADO A PRUEBA DE FALLOS */}
      {modalOpen && modalData && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/90 backdrop-blur-sm p-4">
          <div className="bg-[#0f172a] w-full max-w-5xl h-[90vh] rounded-xl border border-slate-700 flex flex-col relative overflow-hidden shadow-2xl">
            {/* Header Modal */}
            <div className="p-4 border-b border-slate-700 bg-[#1e293b] flex justify-between items-center shrink-0">
              <div className="flex items-center gap-3">
                <span className="text-2xl">📑</span>
                <div><h2 className="text-sm font-bold text-white">Informe Técnico</h2><p className="text-[10px] text-slate-400">SECAI o3 Engine</p></div>
              </div>
              <div className="flex gap-3">
                <button onClick={generarPDF} className="bg-blue-600 hover:bg-blue-500 px-4 py-2 rounded text-xs font-bold text-white flex items-center gap-2"><span>⬇️</span> Descargar PDF</button>
                <button onClick={() => setModalOpen(false)} className="bg-slate-700 hover:bg-slate-600 w-8 h-8 rounded-full text-white flex items-center justify-center">✕</button>
              </div>
            </div>

            {/* Contenido Seguro */}
            <div className="flex-1 overflow-y-auto p-8 custom-scrollbar bg-[#020617]">
              <div className="max-w-4xl mx-auto space-y-8">
                <div className="border-b border-slate-800 pb-6 flex justify-between items-start">
                    <h1 className="text-3xl font-bold text-white max-w-2xl">{modalData.ticket?.titulo || "Sin Título"}</h1>
                    <div className={`px-4 py-2 rounded-lg border ${modalData.auditoria?.score >= 90 ? 'bg-green-500/10 border-green-500/50 text-green-400' : 'bg-yellow-500/10 border-yellow-500/50 text-yellow-400'}`}>
                      <div className="text-xs uppercase font-bold tracking-wider">Calidad</div>
                      <div className="text-2xl font-bold text-center">{modalData.auditoria?.score || 0}/100</div>
                    </div>
                </div>

                {/* 1. Causa Raíz */}
                {modalData.investigacion?.analisis_causa_raiz && (
                  <div className="bg-slate-900/50 p-6 rounded-xl border border-slate-800">
                    <h3 className="text-lg font-bold text-cyan-400 mb-3">🔍 1. Análisis de Causa Raíz</h3>
                    <SafeTextRenderer content={modalData.investigacion.analisis_causa_raiz} />
                  </div>
                )}

                {/* 2. Solución Técnica */}
                {modalData.investigacion?.solucion_detallada && (
                  <div>
                    <h3 className="text-lg font-bold text-purple-400 mb-3">🛠️ 2. Solución Técnica</h3>
                    <div className="bg-[#0b1121] p-6 rounded-xl border border-slate-800">
                      <SafeTextRenderer content={modalData.investigacion.solucion_detallada} />
                    </div>
                  </div>
                )}

                <div className="grid md:grid-cols-2 gap-6">
                  {/* 3. Seguridad */}
                  {modalData.investigacion?.consideraciones_seguridad && (
                    <div className="bg-red-950/20 p-6 rounded-xl border border-red-900/30">
                      <h3 className="text-md font-bold text-red-400 mb-3">🛡️ 3. Seguridad</h3>
                      <SafeTextRenderer content={modalData.investigacion.consideraciones_seguridad} />
                    </div>
                  )}
                  {/* 4. Rollback */}
                  {modalData.investigacion?.plan_rollback && (
                    <div className="bg-orange-950/20 p-6 rounded-xl border border-orange-900/30">
                      <h3 className="text-md font-bold text-orange-400 mb-3">↩️ 4. Rollback</h3>
                      <SafeTextRenderer content={modalData.investigacion.plan_rollback} />
                    </div>
                  )}
                </div>
                
                 {/* Referencias: Doble verificación de existencia */}
                {Array.isArray(modalData.investigacion?.fuentes_bibliograficas) && modalData.investigacion.fuentes_bibliograficas.length > 0 && (
                  <div className="border-t border-slate-800 pt-6">
                    <h3 className="text-sm font-bold text-slate-500 mb-3 uppercase tracking-wider">📚 Referencias Bibliográficas</h3>
                    <ul className="space-y-2">
                      {modalData.investigacion.fuentes_bibliograficas.map((f, i) => (
                        <li key={i} className="text-xs">
                          <a href={f?.url || "#"} target="_blank" rel="noreferrer" className="text-blue-400 hover:underline flex items-center gap-2">
                            <span>🔗</span> {f?.titulo || "Fuente"} <span className="text-slate-600 truncate max-w-xs">({f?.url})</span>
                          </a>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;