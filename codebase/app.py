from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import streamlit as st

from env_loader import load_lab_env
from providers import make_provider
from providers.base import ToolCall
from tools import TOOL_FUNCTIONS, load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
TRANSCRIPTS_DIR = ROOT / "transcripts"
load_lab_env(ROOT)

PROVIDERS = ["openrouter", "gemini", "openai", "anthropic", "opencode"]
VERSIONS = ["v0", "v1", "v2", "v3"]

PAGE_STYLE = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Calistoga&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    :root {
        --background: #FAFAFA;
        --foreground: #0F172A;
        --muted: #F1F5F9;
        --muted-foreground: #64748B;
        --accent: #0052FF;
        --accent-secondary: #4D7CFF;
        --accent-foreground: #FFFFFF;
        --border: #E2E8F0;
        --card: #FFFFFF;
        --ring: #0052FF;
        --gradient: linear-gradient(135deg, var(--accent), var(--accent-secondary));
    }

    /* Global Canvas and Typography */
    .stApp {
        background-color: var(--background) !important;
        color: var(--foreground) !important;
        font-family: 'Inter', sans-serif;
    }

    /* Restore Streamlit Material Icons font family to prevent ligature text leaks */
    [data-testid="stIconMaterial"], 
    .material-icons,
    [class*="material-icons"],
    [class*="MaterialIcons"],
    [class*="MaterialSymbols"] {
        font-family: "Material Symbols Rounded", "Material Icons" !important;
    }

    /* Force dark slate color on all default Streamlit text and labels */
    .stApp p, 
    .stApp label, 
    .stApp li,
    .stApp div[data-testid="stMarkdownContainer"] p,
    .stApp div[data-testid="stMarkdownContainer"] li {
        color: var(--foreground) !important;
    }

    /* Headings */
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {
        color: var(--foreground) !important;
        font-family: 'Calistoga', serif !important;
        font-weight: normal !important;
    }

    /* Target widget labels specifically */
    label[data-testid="stWidgetLabel"],
    label[data-testid="stWidgetLabel"] p {
        color: var(--foreground) !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
    }

    /* Clean up top header and bottom bar */
    header[data-testid="stHeader"] {
        background-color: transparent !important;
        background: transparent !important;
    }
    
    div[data-testid="stBottom"] {
        background-color: rgba(250, 250, 250, 0.8) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        border-top: 1px solid var(--border) !important;
    }
    div[data-testid="stBottom"] > div {
        background-color: transparent !important;
        background: transparent !important;
        border: none !important;
    }

    /* Code tags styling */
    code {
        background-color: var(--muted) !important;
        color: var(--foreground) !important;
        padding: 0.2rem 0.4rem !important;
        border-radius: 6px !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.85rem !important;
        border: 1px solid var(--border) !important;
    }

    /* Modern Glows & Living Elements */
    .modern-glow-container {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        z-index: -100;
        overflow: hidden;
        pointer-events: none;
    }
    .radial-glow {
        position: absolute;
        border-radius: 50%;
        filter: blur(150px);
        opacity: 0.04;
        pointer-events: none;
        will-change: transform;
    }
    .glow-1 {
        top: -10%;
        left: 20%;
        width: 40vw;
        height: 40vw;
        background: var(--accent);
    }
    .glow-2 {
        bottom: -10%;
        right: 10%;
        width: 45vw;
        height: 45vw;
        background: var(--accent-secondary);
    }

    /* Rotating Decorative Rings */
    .rotating-ring-svg {
        position: absolute;
        top: 5%;
        right: 5%;
        width: 250px;
        height: 250px;
        opacity: 0.05;
        animation: slow-rotate 80s linear infinite;
        pointer-events: none;
    }

    @keyframes slow-rotate {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    /* Floating elements */
    .floating-element {
        position: absolute;
        background: rgba(255, 255, 255, 0.7);
        border: 1px solid var(--border);
        backdrop-filter: blur(8px);
        border-radius: 12px;
        padding: 10px 14px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        opacity: 0.18;
        pointer-events: none;
    }
    .floating-element-1 {
        top: 15%;
        left: 22%;
        animation: float-y 6s ease-in-out infinite;
    }
    .floating-element-2 {
        bottom: 22%;
        left: 32%;
        animation: float-y 8s ease-in-out infinite -2s;
    }

    @keyframes float-y {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }

    /* Section Badges label system */
    .section-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        border-radius: 9999px;
        border: 1px solid rgba(0, 82, 255, 0.2);
        background: rgba(0, 82, 255, 0.05);
        padding: 4px 12px;
        margin-bottom: 0.75rem;
    }

    .section-badge-dot {
        height: 6px;
        width: 6px;
        border-radius: 50%;
        background-color: var(--accent);
        animation: badge-pulse 2s infinite;
    }

    @keyframes badge-pulse {
        0%, 100% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.3); opacity: 0.6; }
    }

    .section-badge-text {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.7rem !important;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        font-weight: 500;
        color: var(--accent) !important;
    }

    /* Sidebar - Inverted Contrast Slate Panel */
    section[data-testid="stSidebar"] {
        background-color: var(--foreground) !important;
        color: #FFFFFF !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
        background-image: radial-gradient(circle, rgba(255, 255, 255, 0.02) 1px, transparent 1px) !important;
        background-size: 24px 24px !important;
    }

    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] label p,
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: rgba(255, 255, 255, 0.9) !important;
    }
    
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        font-family: 'Calistoga', serif !important;
        font-weight: normal !important;
        color: #FFFFFF !important;
    }

    /* Sidebar controls */
    section[data-testid="stSidebar"] div[data-testid="stTextInput"] div,
    section[data-testid="stSidebar"] div[data-baseweb="select"] div {
        border-color: transparent !important;
    }

    section[data-testid="stSidebar"] div[data-baseweb="select"] > div,
    section[data-testid="stSidebar"] div[data-testid="stTextInput"] input {
        background-color: rgba(255, 255, 255, 0.06) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: #FFFFFF !important;
        font-family: 'Inter', sans-serif !important;
        box-shadow: none !important;
        padding: 0.25rem 0.5rem !important;
        transition: all 0.2s ease-out !important;
    }

    section[data-testid="stSidebar"] div[data-baseweb="select"] > div:focus-within,
    section[data-testid="stSidebar"] div[data-testid="stTextInput"] input:focus {
        background-color: rgba(255, 255, 255, 0.1) !important;
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 2px rgba(0, 82, 255, 0.2) !important;
    }

    div[data-baseweb="select"] div[role="button"] {
        color: #FFFFFF !important;
    }

    /* Sidebar widgets list labels */
    section[data-testid="stSidebar"] label[data-testid="stWidgetLabel"],
    section[data-testid="stSidebar"] label[data-testid="stWidgetLabel"] p {
        color: rgba(255, 255, 255, 0.8) !important;
    }

    /* Sidebar buttons text color correction */
    section[data-testid="stSidebar"] div.stButton > button,
    section[data-testid="stSidebar"] div.stDownloadButton > button {
        background-color: rgba(255, 255, 255, 0.08) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        color: #FFFFFF !important;
    }
    section[data-testid="stSidebar"] div.stButton > button p,
    section[data-testid="stSidebar"] div.stDownloadButton > button p {
        color: #FFFFFF !important;
    }
    section[data-testid="stSidebar"] div.stButton > button:hover,
    section[data-testid="stSidebar"] div.stDownloadButton > button:hover {
        background-color: rgba(255, 255, 255, 0.15) !important;
        border-color: rgba(255, 255, 255, 0.25) !important;
        color: #FFFFFF !important;
    }
    section[data-testid="stSidebar"] div.stButton > button:disabled,
    section[data-testid="stSidebar"] div.stDownloadButton > button:disabled {
        background-color: rgba(255, 255, 255, 0.02) !important;
        border-color: rgba(255, 255, 255, 0.05) !important;
        color: rgba(255, 255, 255, 0.3) !important;
        cursor: not-allowed !important;
    }
    section[data-testid="stSidebar"] div.stButton > button:disabled p,
    section[data-testid="stSidebar"] div.stDownloadButton > button:disabled p {
        color: rgba(255, 255, 255, 0.3) !important;
    }

    /* Main Header Title styling */
    .main-header {
        background: transparent !important;
        border: none !important;
        padding: 2rem 0 !important;
        margin-bottom: 2rem !important;
        text-align: center !important;
        font-family: 'Calistoga', serif !important;
        font-size: 3rem !important;
        font-weight: normal !important;
        letter-spacing: -0.01em !important;
        position: relative !important;
        display: block !important;
        box-shadow: none !important;
        transition: all 0.3s ease !important;
    }

    .main-header-content {
        display: inline-block;
        position: relative;
    }

    .gradient-text {
        background: var(--gradient) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        font-weight: bold;
    }

    .gradient-underline {
        position: absolute;
        bottom: -0.5rem;
        left: 10%;
        height: 4px;
        width: 80%;
        border-radius: 9999px;
        background: var(--gradient);
        opacity: 0.85;
    }

    /* Tool execution badge */
    .tool-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 0.75rem;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 500;
        background: var(--muted);
        color: var(--foreground);
        margin-right: 6px;
        border: 1px solid var(--border);
    }
    .tool-badge.error { 
        background: #FEE2E2 !important; 
        color: #EF4444 !important; 
        border-color: #FCA5A5 !important;
    }
    .tool-badge.success { 
        background: #D1FAE5 !important; 
        color: #065F46 !important; 
        border-color: #A7F3D0 !important;
    }

    /* Metric boxes in sidebar */
    .metric-box {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        padding: 0.85rem 1.25rem !important;
        margin: 0.75rem 0 !important;
        box-shadow: none !important;
    }
    .metric-box .label { 
        font-family: 'JetBrains Mono', monospace !important; 
        font-size: 0.7rem !important; 
        color: rgba(255, 255, 255, 0.6) !important; 
        text-transform: uppercase !important; 
        font-weight: 500 !important; 
        letter-spacing: 0.05em !important; 
    }
    .metric-box .value { 
        font-family: 'Inter', sans-serif !important; 
        font-size: 1.5rem !important; 
        font-weight: 700 !important; 
        color: var(--accent-secondary) !important; 
    }

    /* Chat bubble container styling */
    .chat-container {
        max-width: 900px;
        margin: 0 auto;
        padding-bottom: 140px;
    }
    
    /* Hide native Streamlit avatar */
    div[data-testid="stChatMessageAvatar"] {
        display: none !important;
    }

    /* Custom Streamlit chat message wraps */
    div[data-testid="stChatMessage"] {
        padding: 1.25rem 1.5rem !important;
        margin-bottom: 1.25rem !important;
        border-radius: 16px !important;
        max-width: 85% !important;
        box-shadow: none !important;
        border: none !important;
        transition: all 0.2s ease-out !important;
    }

    /* User messages - Inverted contrast gradient */
    div[data-testid="stChatMessageUser"] {
        background: var(--gradient) !important;
        margin-left: auto !important;
        border-bottom-right-radius: 4px !important;
        box-shadow: 0 4px 12px rgba(0, 82, 255, 0.15) !important;
    }
    div[data-testid="stChatMessageUser"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(0, 82, 255, 0.2) !important;
    }
    div[data-testid="stChatMessageUser"] p,
    div[data-testid="stChatMessageUser"] li,
    div[data-testid="stChatMessageUser"] code {
        color: #FFFFFF !important;
        font-family: 'Inter', sans-serif !important;
    }
    div[data-testid="stChatMessageUser"] code {
        background-color: rgba(255, 255, 255, 0.15) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        box-shadow: none !important;
    }

    /* Assistant messages - Elevated Card Style */
    div[data-testid="stChatMessageAssistant"] {
        background: var(--card) !important;
        margin-right: auto !important;
        border-bottom-left-radius: 4px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03) !important;
        border: 1px solid var(--border) !important;
    }
    div[data-testid="stChatMessageAssistant"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.02) !important;
    }
    div[data-testid="stChatMessageAssistant"] p,
    div[data-testid="stChatMessageAssistant"] li {
        color: var(--foreground) !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* Expander details box */
    .stExpander {
        background-color: var(--card) !important;
        border-radius: 12px !important;
        border: 1px solid var(--border) !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05) !important;
        margin-top: 0.75rem !important;
        overflow: hidden !important;
        transition: all 0.2s ease-out !important;
    }
    .stExpander:hover {
        border-color: rgba(0, 82, 255, 0.3) !important;
    }
    div[data-testid="stExpander"] summary {
        background-color: var(--card) !important;
        border-bottom: 1px solid var(--border) !important;
        transition: all 0.2s ease-out !important;
    }
    div[data-testid="stExpander"] summary:hover {
        background-color: var(--muted) !important;
    }
    div[data-testid="stExpander"] summary,
    div[data-testid="stExpander"] summary svg,
    div[data-testid="stExpander"] summary span,
    div[data-testid="stExpander"] summary p {
        color: var(--foreground) !important;
        fill: var(--foreground) !important;
    }
    div[data-testid="stExpander"] summary,
    div[data-testid="stExpander"] summary p {
        font-family: 'Inter', sans-serif !important;
    }
    div[data-testid="stExpander"] > div[role="region"] {
        background-color: var(--card) !important;
        color: var(--foreground) !important;
        border: none !important;
    }

    /* Custom Responsive Grid for Food Cards */
    .food-cards-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
        gap: 1.75rem;
        margin: 1.5rem 0 0.5rem 0;
        width: 100%;
    }

    .food-card-gradient-wrap {
        border-radius: 16px !important;
        background: var(--gradient) !important;
        padding: 2px !important;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
        box-shadow: 0 4px 10px rgba(0, 82, 255, 0.05) !important;
    }
    .food-card-gradient-wrap:hover {
        transform: translateY(-6px) !important;
        box-shadow: 0 16px 28px rgba(0, 82, 255, 0.12) !important;
    }

    .food-card-inner {
        background: var(--card) !important;
        border-radius: 14px !important; /* calc(16px - 2px) */
        height: 100%;
        width: 100%;
        overflow: hidden !important;
        display: flex !important;
        flex-direction: column !important;
        padding: 0 !important;
    }

    .food-card-header {
        background-color: transparent !important;
        padding: 1.5rem 1.5rem 0.5rem 1.5rem !important;
        display: flex !important;
        justify-content: space-between !important;
        align-items: center;
    }

    .food-avatar-orb {
        width: 48px !important;
        height: 48px !important;
        border-radius: 50% !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 1.5rem !important;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05) !important;
    }

    /* Gradient backgrounds for orb types */
    .orb-dry { background: linear-gradient(135deg, #FF8A00, #FFC700) !important; }
    .orb-snack { background: linear-gradient(135deg, #FF007A, #FF7A00) !important; }
    .orb-drink { background: linear-gradient(135deg, #00C6FF, #0072FF) !important; }
    .orb-soup { background: linear-gradient(135deg, #7A00FF, #00C6FF) !important; }

    .food-tag {
        background: rgba(0, 82, 255, 0.08) !important;
        color: var(--accent) !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.65rem !important;
        font-weight: 500 !important;
        padding: 0.35rem 0.75rem !important;
        border-radius: 9999px !important;
        letter-spacing: 0.05em !important;
        border: 1px solid rgba(0, 82, 255, 0.15) !important;
    }

    .food-card-body {
        padding: 0.5rem 1.5rem 1.5rem 1.5rem !important;
        flex-grow: 1 !important;
        display: flex !important;
        flex-direction: column !important;
        gap: 0.6rem !important;
    }

    .food-title {
        font-family: 'Inter', sans-serif !important;
        font-size: 1.25rem !important;
        font-weight: 600 !important;
        color: var(--foreground) !important;
        line-height: 1.3 !important;
    }

    .food-meta {
        font-family: 'Inter', sans-serif !important;
        font-size: 0.8rem !important;
        color: var(--muted-foreground) !important;
        display: flex !important;
        align-items: center !important;
        gap: 0.4rem !important;
        font-weight: 500 !important;
    }

    .meta-dot {
        font-weight: bold !important;
        color: var(--border) !important;
    }

    .food-tags {
        display: flex !important;
        flex-wrap: wrap !important;
        gap: 0.4rem !important;
        margin: 0.25rem 0 !important;
    }

    .tag-pill {
        background: var(--muted) !important;
        border: 1px solid var(--border) !important;
        color: var(--foreground) !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.75rem !important;
        padding: 0.25rem 0.65rem !important;
        border-radius: 9999px !important;
        font-weight: 500 !important;
    }

    .food-reason {
        font-family: 'Inter', sans-serif !important;
        font-size: 0.85rem !important;
        color: var(--muted-foreground) !important;
        line-height: 1.5 !important;
        border-left: 2px solid var(--accent) !important;
        padding-left: 0.75rem !important;
        margin-top: 0.5rem !important;
        font-style: normal !important;
    }

    .food-card-footer {
        padding: 1.25rem 1.5rem !important;
        border-top: 1px solid var(--border) !important;
        display: flex !important;
        justify-content: space-between !important;
        align-items: center;
        background: var(--muted) !important;
    }

    .food-price {
        font-family: 'Inter', sans-serif !important;
        font-size: 1.2rem !important;
        font-weight: 700 !important;
        color: var(--foreground) !important;
    }

    .food-btn {
        background: var(--gradient) !important;
        color: var(--accent-foreground) !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        padding: 0.5rem 1rem !important;
        border-radius: 8px !important;
        cursor: pointer !important;
        transition: all 0.2s ease-out !important;
        border: none !important;
        box-shadow: 0 2px 4px rgba(0, 82, 255, 0.15) !important;
    }
    .food-btn:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 8px rgba(0, 82, 255, 0.25) !important;
    }
    .food-btn:active {
        transform: scale(0.96) !important;
    }

    /* Suggestion Chips Section */
    .suggestion-container {
        display: flex;
        flex-wrap: wrap;
        gap: 0.75rem;
        justify-content: center;
        padding: 0.5rem 1rem;
        max-width: 900px;
        margin: 0 auto;
    }

    div.stButton > button {
        border-radius: 12px !important;
        border: 1px solid var(--border) !important;
        background-color: var(--card) !important;
        color: var(--foreground) !important;
        padding: 0.5rem 1.25rem !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05) !important;
    }

    div.stButton > button:hover {
        background: var(--muted) !important;
        border-color: rgba(0, 82, 255, 0.3) !important;
        color: var(--accent) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05) !important;
    }
    div.stButton > button:active {
        transform: scale(0.97) !important;
    }

    /* Chat Input Control */
    div[data-testid="stChatInput"] {
        background-color: transparent !important;
        border-top: none !important;
        box-shadow: none !important;
        padding: 1rem 0 !important;
    }
    div[data-testid="stChatInput"] > div {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    div[data-testid="stChatInput"] textarea {
        background-color: var(--card) !important;
        border-radius: 12px !important;
        border: 1px solid var(--border) !important;
        padding: 0.8rem 1.4rem !important;
        color: var(--foreground) !important;
        font-family: 'Inter', sans-serif !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05) !important;
        transition: all 0.2s ease-out !important;
    }
    div[data-testid="stChatInput"] textarea:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 2px rgba(0, 82, 255, 0.15) !important;
    }
    
    div[data-testid="stChatInput"] textarea::placeholder {
        color: var(--muted-foreground) !important;
        opacity: 0.6 !important;
    }

    div[data-testid="stChatInput"] button {
        background: var(--gradient) !important;
        border-radius: 8px !important;
        color: var(--accent-foreground) !important;
        box-shadow: 0 2px 4px rgba(0, 82, 255, 0.2) !important;
    }
    div[data-testid="stChatInput"] button:hover {
        opacity: 0.9 !important;
    }

    /* Slider styling */
    div[data-testid="stSlider"] label,
    div[data-testid="stSlider"] p {
        color: var(--foreground) !important;
    }
    div[data-testid="stSlider"] [data-testid="stSliderTick"] {
        color: var(--muted-foreground) !important;
        font-weight: normal !important;
    }
    div[data-testid="stSlider"] [role="slider"] {
        background-color: var(--accent) !important;
        border: 2px solid #FFFFFF !important;
        box-shadow: 0 2px 4px rgba(0, 82, 255, 0.2) !important;
    }

    footer { visibility: hidden; }
</style>
"""


def section_badge_html(text: str) -> str:
    return f"""
    <div class="section-badge">
        <div class="section-badge-dot"></div>
        <span class="section-badge-text">{text}</span>
    </div>
    """


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def new_transcript_id() -> str:
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    return f"streamlit_{timestamp}"


def reset_chat_session() -> None:
    transcript_id = new_transcript_id()
    st.session_state.messages = []
    st.session_state.history = []
    st.session_state.transcript_turns = []
    st.session_state.transcript_id = transcript_id
    st.session_state.transcript_path = str(TRANSCRIPTS_DIR / f"{transcript_id}.transcript.json")
    st.session_state.transcript_created_at = now_iso()


def transcript_payload(*, artifact_version, provider_name: str, model: str | None) -> dict:
    return {
        "transcript_id": st.session_state.transcript_id,
        **artifact_version_dict(artifact_version),
        "provider": provider_name,
        "model": model or "default",
        "created_at": st.session_state.transcript_created_at,
        "updated_at": now_iso(),
        "turns": st.session_state.transcript_turns,
    }


def write_transcript(path: Path, transcript: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(transcript, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


def json_text(value, max_chars: int = 24000) -> str:
    text = json.dumps(value, ensure_ascii=False, indent=2, default=str)
    return text[:max_chars] + "\n...<truncated>" if len(text) > max_chars else text


def execute_tool_call(call: ToolCall) -> dict:
    func = TOOL_FUNCTIONS.get(call.name)
    if not func:
        return {"tool": call.name, "args": call.args, "result": {"error": "unknown_tool"}}
    try:
        result = func(**call.args)
    except Exception as exc:
        result = {"error": type(exc).__name__, "message": str(exc)}
    return {"tool": call.name, "args": call.args, "result": result}


def tool_results_message(events: list[dict]) -> dict:
    return {
        "role": "user",
        "content": (
            "TOOL_RESULTS_JSON:\n"
            f"{json_text(events)}\n\n"
            "Use only these tool results. If the user asked for a digest and the items are ready, "
            "call the formatting tool. Otherwise answer the user directly with cited sources when available."
        ),
    }


def assistant_tool_message(response_text: str | None, calls: list[ToolCall]) -> dict:
    call_summary = [{"name": c.name, "args": c.args} for c in calls]
    content = response_text or "I will call the selected tool(s)."
    return {"role": "assistant", "content": f"{content}\n\nTOOL_CALLS_JSON:\n{json_text(call_summary)}"}


def render_food_cards_html(tools_used: list[dict]) -> str:
    html = ""
    for t in tools_used:
        # Match tool name (either in 'name' or 'tool' key)
        t_name = t.get("name") or t.get("tool")
        if t_name == "food_recommendation":
            result = t.get("result", {})
            if not isinstance(result, dict):
                continue
            items = result.get("items", [])
            if not items:
                continue
            
            html += '<div class="food-cards-grid">'
            for item in items:
                avatar = "🍜"
                loai_lower = item.get("loai", "").lower()
                orb_class = "orb-soup"
                if "khô" in loai_lower:
                    avatar = "🍛"
                    orb_class = "orb-dry"
                elif "ăn vặt" in loai_lower:
                    avatar = "🍟"
                    orb_class = "orb-snack"
                elif "uống" in loai_lower or "nước" in loai_lower:
                    if "nước" in loai_lower and "đồ nước" not in loai_lower:
                        avatar = "🥤"
                        orb_class = "orb-drink"
                
                price_val = item.get("gia", 0)
                price_formatted = f"{price_val:,}".replace(",", ".")
                
                html += f"""
                <div class="food-card-gradient-wrap">
                    <div class="food-card-inner">
                        <div class="food-card-header">
                            <div class="food-avatar-orb {orb_class}">{avatar}</div>
                            <div class="food-tag">⚡ FREESHIP</div>
                        </div>
                        <div class="food-card-body">
                            <div class="food-title">{item.get('title', '')}</div>
                            <div class="food-meta">
                                <span>📍 {item.get('khoang_cach_km', 0)} km</span>
                                <span class="meta-dot">•</span>
                                <span>{item.get('loai', '')}</span>
                            </div>
                            <div class="food-tags">
                                <span class="tag-pill">{item.get('vi', '')}</span>
                            </div>
                            <div class="food-reason">{item.get('ly_do_goi_y', '')}</div>
                        </div>
                        <div class="food-card-footer">
                            <span class="food-price">{price_formatted} đ</span>
                            <div class="food-btn">Đặt món</div>
                        </div>
                    </div>
                </div>
                """
            html += '</div>'
    return html


def run_model_tool_loop(*, provider, messages, tools, model, max_tool_rounds=4):
    working_messages = list(messages)
    rounds = []
    all_tool_events = []

    for round_index in range(1, max_tool_rounds + 1):
        response = provider.complete(working_messages, tools, model=model, temperature=0.0)
        calls = response.tool_calls
        round_record = {
            "round": round_index,
            "assistant_text": response.text,
            "tool_calls": [{"name": c.name, "args": c.args} for c in calls],
            "tool_results": [],
        }

        if not calls:
            rounds.append(round_record)
            return {
                "status": "answered",
                "assistant_text": response.text or "",
                "rounds": rounds,
                "tool_events": all_tool_events,
            }

        working_messages.append(assistant_tool_message(response.text, calls))
        non_clarification_events = []

        for call in calls:
            event = execute_tool_call(call)
            round_record["tool_results"].append(event)
            all_tool_events.append(event)

            result = event.get("result", {})
            if isinstance(result, dict) and result.get("awaiting_user"):
                question = result.get("question") or call.args.get("question") or "Please provide more info."
                rounds.append(round_record)
                return {
                    "status": "waiting_for_user",
                    "assistant_text": question,
                    "rounds": rounds,
                    "tool_events": all_tool_events,
                }

            non_clarification_events.append(event)

        rounds.append(round_record)
        working_messages.append(tool_results_message(non_clarification_events))

    return {
        "status": "max_tool_rounds",
        "assistant_text": f"Stopped after {max_tool_rounds} tool rounds.",
        "rounds": rounds,
        "tool_events": all_tool_events,
    }


def render_tool_call(t: dict) -> None:
    has_error = isinstance(t.get("result"), dict) and "error" in t.get("result", {})
    badge_class = "error" if has_error else "success"
    args_str = json.dumps(t["args"], ensure_ascii=False)
    st.markdown(
        f'<span class="tool-badge {badge_class}">{t["name"]}</span>'
        f'<code style="font-size:0.8rem">{args_str}</code>',
        unsafe_allow_html=True,
    )
    if has_error:
        st.error(t["result"])
    elif t.get("result") and t["result"] != {}:
        with st.expander("Result"):
            st.json(t["result"])


# --- Page config & style ---
st.set_page_config(
    page_title="Smart Food Finder 🍜",
    page_icon="🍜",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(PAGE_STYLE, unsafe_allow_html=True)
st.markdown(
    """
    <div class="modern-glow-container">
        <div class="radial-glow glow-1"></div>
        <div class="radial-glow glow-2"></div>
        <svg class="rotating-ring-svg" viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="100" cy="100" r="90" stroke="#0052FF" stroke-width="1.5" stroke-dasharray="8 8"/>
            <circle cx="100" cy="100" r="70" stroke="#4D7CFF" stroke-width="1" stroke-dasharray="4 4"/>
        </svg>
        <div class="floating-element floating-element-1">🍜</div>
        <div class="floating-element floating-element-2">🍛</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- Init session state ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "history" not in st.session_state:
    st.session_state.history = []
if "transcript_turns" not in st.session_state:
    st.session_state.transcript_turns = []
if "transcript_id" not in st.session_state:
    transcript_id = new_transcript_id()
    st.session_state.transcript_id = transcript_id
    st.session_state.transcript_path = str(TRANSCRIPTS_DIR / f"{transcript_id}.transcript.json")
    st.session_state.transcript_created_at = now_iso()
if "provider" not in st.session_state:
    st.session_state.provider = None
    st.session_state.provider_name = None

# --- Load artifacts ---
system_prompt = (ARTIFACTS_DIR / "system_prompt.md").read_text(encoding="utf-8")
tool_declarations = load_tool_declarations(ARTIFACTS_DIR / "tools.yaml")
openai_tools = to_openai_tools(tool_declarations)
_initial_artifact_version = build_artifact_version(VERSIONS[0], ARTIFACTS_DIR / "system_prompt.md", ARTIFACTS_DIR / "tools.yaml")

# --- Sidebar ---
with st.sidebar:
    st.markdown(section_badge_html("Settings"), unsafe_allow_html=True)
    st.markdown("## Configuration")

    provider_name = st.selectbox("Provider", PROVIDERS, index=0)
    version = st.selectbox("Version", VERSIONS)
    model = st.text_input("Model override", placeholder="Use provider default")
    max_rounds = st.slider("Max tool rounds", 1, 8, 4)
    artifact_version = build_artifact_version(version, ARTIFACTS_DIR / "system_prompt.md", ARTIFACTS_DIR / "tools.yaml")

    if st.session_state.provider_name != provider_name:
        try:
            st.session_state.provider = make_provider(provider_name)
            st.session_state.provider_name = provider_name
        except Exception as e:
            st.error(f"Provider init failed: {e}")
            st.stop()

    st.divider()
    st.markdown(section_badge_html("Control Panel"), unsafe_allow_html=True)
    st.markdown("### Session")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Clear chat", use_container_width=True):
            reset_chat_session()
            st.rerun()
    with col2:
        has_turns = bool(st.session_state.get("transcript_turns"))
        if st.button("New session", use_container_width=True, disabled=not has_turns):
            reset_chat_session()
            st.rerun()

    if st.session_state.get("transcript_turns"):
        st.divider()
        st.markdown(section_badge_html("Analytics"), unsafe_allow_html=True)
        st.markdown("### Transcript")
        transcript = transcript_payload(
            artifact_version=artifact_version,
            provider_name=provider_name,
            model=model or None,
        )
        transcript_json = json.dumps(transcript, ensure_ascii=False, indent=2, default=str)
        st.download_button(
            "Download transcript",
            data=transcript_json,
            file_name=f"transcript_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True,
        )
        st.caption(f"Saved to: {st.session_state.transcript_path}")
        col_a, col_b = st.columns(2)
        col_a.metric("Turns", len(st.session_state.transcript_turns))
        col_b.metric("Tools called", sum(
            1 for t in st.session_state.transcript_turns
            for r in t.get("rounds", [])
            if r.get("tool_calls")
        ))

    st.divider()
    st.caption(f"Artifacts: system_prompt.md / tools.yaml @ {version}")

# --- Header ---
st.markdown(
    '<div class="main-header"><div class="main-header-content">'
    'SMART <span class="gradient-text">FOOD FINDER</span>'
    '<div class="gradient-underline"></div>'
    '</div></div>', 
    unsafe_allow_html=True
)

# --- Tool count summary ---
st.markdown(section_badge_html("Decide Engine"), unsafe_allow_html=True)
enabled = [t["name"] for t in tool_declarations]
with st.expander(f"Available tools ({len(enabled)})"):
    cols = st.columns(4)
    for i, name in enumerate(enabled):
        cols[i % 4].code(name, language=None)

# --- Chat area ---
st.markdown(section_badge_html("AI Assistant"), unsafe_allow_html=True)
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "tools_used" in msg and msg["tools_used"]:
            cards_html = render_food_cards_html(msg["tools_used"])
            if cards_html:
                st.markdown(cards_html, unsafe_allow_html=True)
            with st.expander("Tool execution details"):
                for t in msg["tools_used"]:
                    render_tool_call(t)

# --- Suggestion Chips ---
st.markdown('<div class="suggestion-container">', unsafe_allow_html=True)
cols = st.columns(4)
suggestions = [
    ("🍜 Đồ nước thanh đạm", "Tôi muốn ăn đồ nước thanh đạm, gần đây"),
    ("🍛 Đồ khô đậm đà", "Tìm cho tôi món đồ khô hương vị đậm đà"),
    ("🍟 Ăn vặt gần đây", "Có món ăn vặt gì ngon bán kính dưới 1.5km không"),
    ("❌ Không đậu phộng", "Gợi ý món ăn ngon và lưu ý tôi dị ứng đậu phộng")
]

selected_suggestion = None
for i, (label, query) in enumerate(suggestions):
    with cols[i]:
        if st.button(label, key=f"sug_{i}", use_container_width=True):
            selected_suggestion = query
st.markdown('</div>', unsafe_allow_html=True)

# --- Chat input ---
user_input = st.chat_input("Bạn muốn ăn gì hôm nay? Ví dụ: đồ nước thanh đạm gần Quận 1...")
if selected_suggestion:
    user_input = selected_suggestion

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    trim_window = 5
    history_msgs = st.session_state.history[-trim_window * 2:]
    model_messages = [
        {"role": "system", "content": system_prompt},
        *history_msgs,
        {"role": "user", "content": user_input},
    ]

    with st.chat_message("assistant"):
        with st.spinner("Processing..."):
            try:
                result = run_model_tool_loop(
                    provider=st.session_state.provider,
                    messages=model_messages,
                    tools=openai_tools,
                    model=model or None,
                    max_tool_rounds=max_rounds,
                )
                assistant_text = result["assistant_text"]
                tools_used = []
                for r in result.get("rounds", []):
                    for i, tc in enumerate(r.get("tool_calls", [])):
                        tr = r["tool_results"][i]["result"] if i < len(r["tool_results"]) else {}
                        tools_used.append({"name": tc["name"], "args": tc["args"], "result": tr})

                st.markdown(assistant_text)
                
                # Render food cards if tool was executed
                cards_html = render_food_cards_html(tools_used)
                if cards_html:
                    st.markdown(cards_html, unsafe_allow_html=True)
                
                if tools_used:
                    with st.expander("Tool execution details"):
                        for t in tools_used:
                            render_tool_call(t)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_text,
                    "tools_used": tools_used,
                })
                st.session_state.history.append({"role": "user", "content": user_input})
                st.session_state.history.append({"role": "assistant", "content": assistant_text})

                turn = {
                    "turn_index": len(st.session_state.transcript_turns) + 1,
                    "started_at": now_iso(),
                    "ended_at": now_iso(),
                    "user": user_input,
                    "status": result.get("status", "answered"),
                    "assistant_text": assistant_text,
                    "rounds": result.get("rounds", []),
                    "tool_events": result.get("tool_events", []),
                }
                st.session_state.transcript_turns.append(turn)
                write_transcript(
                    Path(st.session_state.transcript_path),
                    transcript_payload(
                        artifact_version=artifact_version,
                        provider_name=provider_name,
                        model=model or None,
                    ),
                )

            except Exception as e:
                st.error(f"Error: {e}")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Error: {e}",
                    "tools_used": [],
                })
                turn = {
                    "turn_index": len(st.session_state.transcript_turns) + 1,
                    "started_at": now_iso(),
                    "ended_at": now_iso(),
                    "user": user_input,
                    "status": "provider_error",
                    "assistant_text": f"Error: {e}",
                    "rounds": [],
                    "tool_events": [],
                    "error": f"{type(e).__name__}: {e}",
                }
                st.session_state.transcript_turns.append(turn)
                write_transcript(
                    Path(st.session_state.transcript_path),
                    transcript_payload(
                        artifact_version=artifact_version,
                        provider_name=provider_name,
                        model=model or None,
                    ),
                )

st.markdown("</div>", unsafe_allow_html=True)
