# styles.py
import streamlit as st

def inject_styles():
    st.markdown("""
    <style>
        .stApp {
            background-color: #020617;
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }

        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
            max-width: 1580px;
            padding-left: 1.25rem;
            padding-right: 1.25rem;
        }

        .app-header {
            background: radial-gradient(circle at top left, #22d3ee22, transparent 55%),
                        radial-gradient(circle at bottom right, #8b5cf622, transparent 60%),
                        #020617;
            border-radius: 18px;
            border: 1px solid #1f2937;
            padding: 18px 22px;
            margin-bottom: 18px;
            box-shadow: 0 18px 45px rgba(15,23,42,0.65);
        }
        .app-header-main {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            margin-bottom: 10px;
        }
        .app-logo {
            width: 48px;
            height: 48px;
            border-radius: 999px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, #22c1c3, #a855f7);
            font-size: 26px;
            box-shadow: 0 8px 24px rgba(56,189,248,0.4);
            flex-shrink: 0;
        }
        .app-title {
            font-size: 1.35rem;
            font-weight: 700;
            color: #f9fafb;
        }
        .app-subtitle {
            font-size: 0.9rem;
            color: #cbd5f5;
        }
        .app-steps {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 6px;
        }
        .step-pill {
            font-size: 0.78rem;
            padding: 4px 10px;
            border-radius: 999px;
            border: 1px solid #1e293b;
            background: rgba(15,23,42,0.9);
            color: #9ca3af;
        }
        .step-active {
            border-color: #22c55e;
            background: radial-gradient(circle at top left, #22c55e33, rgba(15,23,42,0.95));
            color: #e5f8ec;
            font-weight: 600;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #020617;
            border-radius: 16px;
            border: 1px solid #1f2937;
            box-shadow: 0 10px 30px rgba(15,23,42,0.8);
            padding: 1rem;
            margin-bottom: 10px;
        }
        div[data-testid="stVerticalBlockBorderWrapper"] h2 {
            color: #F9FAFB;
            font-size: 0.74rem;
            margin-bottom: 6px;
            border-bottom: none;
            padding-top: 0;
        }

/* Contenedores de fase con altura fija y scroll interno */
        .phase-body {
            max-height: 30vh;      /* límite para listas largas: comentarios, tickets, etc. */
            overflow-y: auto;
            overflow-x: hidden;
            padding-right: 6px;
            margin-top: 6px;
        }
        .phase-body::-webkit-scrollbar {
            width: 8px;
        }
        .phase-body::-webkit-scrollbar-thumb {
            background: #1f2937;
            border-radius: 999px;
        }
        .phase-body::-webkit-scrollbar-track {
            background: transparent;
        }

        /* Tarjetas compactas con snippet y detalle */
        .compact-card {
            background: #0f172a;
            border: 1px solid #1e293b;
            border-radius: 10px;
            margin-bottom: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.35);
        }
        .compact-card summary {
            list-style: none;
            cursor: pointer;
            padding: 12px 14px;
            display: flex;
            align-items: flex-start;
            gap: 10px;
        }
        .compact-card summary::-webkit-details-marker { display: none; }
        .compact-id {
            width: 1.8rem;
            height: 1.8rem;
            border-radius: 999px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.8rem;
            font-weight: 700;
            color: #e5e7eb;
            flex-shrink: 0;
            background: radial-gradient(circle at 30% 0%, rgba(129,140,248,0.45), rgba(15,23,42,0.96));
            box-shadow:
                0 0 0 1px rgba(15,23,42,1),
                0 0 16px rgba(129,140,248,0.35);
        }

        .compact-snippet {
            color: #e2e8f0;
            font-size: 0.92rem;
            line-height: 1.4;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        .compact-full {
            padding: 0 14px 12px 14px;
            color: #e2e8f0;
            font-size: 0.92rem;
            line-height: 1.5;
            border-top: 1px solid rgba(148,163,184,0.15);
        }

        /* Transición sutil al expandir el comentario */
        details[open] .compact-full {
            animation: compact-expand 0.18s ease-out;
        }

        @keyframes compact-expand {
            from {
                opacity: 0;
                transform: translateY(-2px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }


        div.stButton > button {
            background: linear-gradient(135deg, #22c1c3, #0ea5e9);
            color: white;
            border-radius: 999px;
            border: none;
            font-weight: 600;
            padding-top: 0.3rem;
            padding-bottom: 0.3rem;
        }
        div.stButton > button:hover {
            background: linear-gradient(135deg, #22c55e, #0ea5e9);
            color: #0b1120;
        }

        .ticket-card {
            background: #020617;
            border-radius: 14px;
            padding: 14px 16px 12px 16px;
            margin-bottom: 18px;
            border: 1px solid #1f2937;
            box-shadow: 0 10px 30px rgba(15,23,42,0.9);
        }
        .ticket-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 12px;
            padding-bottom: 8px;
            border-bottom: 1px solid #1f2937;
        }
        .ticket-title-row {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .ticket-emoji { font-size: 1.3rem; }
        .ticket-title-text {
            font-size: 1rem;
            font-weight: 700;
            color: #f9fafb;
        }
        .ticket-snippet {
            color: #94a3b8;
            font-size: 0.82rem;
            line-height: 1.45;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
            margin-top: 6px;
        }
        .ticket-chips {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            justify-content: flex-end;
        }
        .ticket-chip {
            font-size: 0.72rem;
            padding: 3px 8px;
            border-radius: 999px;
            border: 1px solid #334155;
            background: #020617;
            color: #e5e7eb;
            white-space: nowrap;
        }
        .ticket-chip-prio-alta {
            border-color: #f97316;
            background: rgba(248,113,113,0.08);
            color: #fed7aa;
        }
        .ticket-chip-prio-media {
            border-color: #eab308;
            background: rgba(253,224,71,0.08);
            color: #fef9c3;
        }
        .ticket-chip-prio-baja {
            border-color: #22c55e;
            background: rgba(34,197,94,0.08);
            color: #bbf7d0;
        }

        .ticket-section {
            margin-top: 10px;
            padding: 10px 11px;
            border-radius: 10px;
            background: #020617;
            border: 1px solid #111827;
        }
        .ticket-section-title {
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #9ca3af;
            margin-bottom: 4px;
        }
        .ticket-section-body {
            font-size: 0.9rem;
            color: #e5e7eb;
            line-height: 1.45;
        }

        .ticket-footer {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            margin-top: 10px;
            padding-top: 8px;
            border-top: 1px solid #1f2937;
        }
        .ticket-footer-item { min-width: 80px; }
        .ticket-metric-label {
            text-transform: uppercase;
            font-size: 0.68rem;
            letter-spacing: 0.08em;
            color: #9ca3af;
            margin-bottom: 2px;
        }
        .ticket-metric-value {
            font-size: 0.95rem;
            font-weight: 600;
            color: #f9fafb;
        }

        .post-card {
            background: #020617;
            border-radius: 16px;
            border: 1px solid #1f2937;
            box-shadow: 0 10px 30px rgba(15,23,42,0.9);
            padding: 14px 16px;
        }
        .post-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 8px;
        }
        .post-avatar {
            width: 36px;
            height: 36px;
            border-radius: 999px;
            background: linear-gradient(135deg,#22c1c3,#a855f7);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 700;
            font-size: 1.1rem;
        }
        .post-meta-title {
            font-size: 0.9rem;
            font-weight: 600;
            color: #f9fafb;
        }
        .post-meta-sub {
            font-size: 0.75rem;
            color: #9ca3af;
        }
        .post-footer-actions {
            font-size: 0.8rem;
            color: #9ca3af;
            margin-top: 6px;
        }
    </style>
    """, unsafe_allow_html=True)
