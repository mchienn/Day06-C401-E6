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

PROVIDERS = ["gemini", "openai", "anthropic", "openrouter", "opencode"]
VERSIONS = ["v0", "v1", "v2", "v3"]

PAGE_STYLE = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&display=swap');

    /* Global Flat Canvas */
    .stApp {
        background-color: #FFFFFF !important;
        color: #111827 !important;
        font-family: 'Outfit', sans-serif !important;
    }

    /* Sidebar customize - Solid Color Block style */
    section[data-testid="stSidebar"] {
        background-color: #F3F4F6 !important;
        border-right: 2px solid #E5E7EB !important;
        box-shadow: none !important;
    }

    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: #111827 !important;
        font-weight: 800 !important;
        letter-spacing: -0.02em !important;
    }

    /* Header Banner styling - Crisp Blue block */
    .main-header {
        background-color: #3B82F6;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: none !important;
        margin-bottom: 2.5rem;
        text-align: center;
        font-size: 2rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        color: #FFFFFF;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.75rem;
    }

    /* Tool execution badge */
    .tool-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        background: #F3F4F6;
        color: #111827;
        margin-right: 4px;
        border: 2px solid #E5E7EB;
    }
    .tool-badge.error { background: #FFF0ED; color: #EF4444; border-color: #EF4444; }
    .tool-badge.success { background: #ECFDF5; color: #10B981; border-color: #10B981; }

    /* Metric boxes in sidebar - Clean flat gray blocks */
    .metric-box {
        background: #FFFFFF;
        border: 2px solid #E5E7EB;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
        box-shadow: none !important;
    }
    .metric-box .label { font-size: 0.75rem; color: #111827; text-transform: uppercase; font-weight: 700; letter-spacing: 0.05em; }
    .metric-box .value { font-size: 1.4rem; font-weight: 800; color: #3B82F6; }

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
        padding: 1.25rem !important;
        margin-bottom: 1.25rem !important;
        border-radius: 8px !important;
        max-width: 80% !important;
        box-shadow: none !important;
        border: none !important;
    }

    /* User messages - Solid Blue Block */
    div[data-testid="stChatMessageUser"] {
        background-color: #3B82F6 !important;
        color: #FFFFFF !important;
        margin-left: auto !important;
    }
    div[data-testid="stChatMessageUser"] p,
    div[data-testid="stChatMessageUser"] span,
    div[data-testid="stChatMessageUser"] div {
        color: #FFFFFF !important;
    }

    /* Assistant messages - Solid Light Gray Block */
    div[data-testid="stChatMessageAssistant"] {
        background-color: #F3F4F6 !important;
        color: #111827 !important;
        margin-right: auto !important;
    }
    div[data-testid="stChatMessageAssistant"] p,
    div[data-testid="stChatMessageAssistant"] span,
    div[data-testid="stChatMessageAssistant"] div {
        color: #111827 !important;
    }

    /* Expander detail box */
    .stExpander {
        background-color: #FFFFFF !important;
        border-radius: 8px !important;
        border: 2px solid #E5E7EB !important;
        box-shadow: none !important;
        margin-top: 0.5rem !important;
    }

    /* Custom Responsive Grid for Food Cards */
    .food-cards-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
        gap: 1.25rem;
        margin: 1.25rem 0;
        width: 100%;
    }

    .food-card {
        background-color: #F3F4F6;
        border-radius: 8px;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        transition: all 0.2s ease;
        border: 2px solid transparent;
        box-shadow: none !important;
    }

    .food-card:hover {
        transform: scale(1.02);
        background-color: #E5E7EB;
        border-color: #3B82F6;
    }

    .food-card-header {
        background-color: #3B82F6;
        padding: 0.8rem 1rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .food-avatar {
        font-size: 1.75rem;
    }

    .food-tag {
        background-color: #10B981;
        color: #FFFFFF;
        font-size: 0.65rem;
        font-weight: 700;
        padding: 0.25rem 0.6rem;
        border-radius: 4px;
        letter-spacing: 0.05em;
    }

    .food-card-body {
        padding: 1.25rem;
        flex-grow: 1;
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }

    .food-title {
        font-size: 1.1rem;
        font-weight: 800;
        color: #111827;
        line-height: 1.3;
    }

    .food-meta {
        font-size: 0.8rem;
        color: #4B5563;
        display: flex;
        align-items: center;
        gap: 0.4rem;
        font-weight: 600;
    }

    .meta-dot {
        font-weight: 800;
        color: #9CA3AF;
    }

    .food-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 0.25rem;
        margin: 0.25rem 0;
    }

    .tag-pill {
        background-color: #FFFFFF;
        color: #111827;
        font-size: 0.75rem;
        padding: 0.2rem 0.6rem;
        border-radius: 4px;
        font-weight: 600;
        border: 1px solid #E5E7EB;
    }

    .food-reason {
        font-size: 0.8rem;
        color: #4B5563;
        line-height: 1.4;
        border-left: 3px solid #3B82F6;
        padding-left: 0.5rem;
        margin-top: 0.25rem;
    }

    .food-card-footer {
        padding: 1rem 1.25rem;
        border-top: 2px solid #E5E7EB;
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: #FFFFFF;
    }

    .food-price {
        font-size: 1.2rem;
        font-weight: 800;
        color: #3B82F6;
    }

    .food-btn {
        background-color: #3B82F6;
        color: #FFFFFF;
        font-size: 0.8rem;
        font-weight: 700;
        padding: 0.45rem 1rem;
        border-radius: 6px;
        cursor: pointer;
        transition: all 0.2s;
        border: none;
    }
    .food-btn:hover {
        background-color: #2563EB;
        transform: scale(1.05);
    }

    /* Suggestion Chips Section - Flat outline buttons */
    .suggestion-container {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        justify-content: center;
        padding: 0.5rem 1rem;
        max-width: 900px;
        margin: 0 auto;
    }

    div.stButton > button {
        border-radius: 6px !important;
        border: 2px solid #3B82F6 !important;
        background-color: #FFFFFF !important;
        color: #3B82F6 !important;
        padding: 0.4rem 1.2rem !important;
        font-size: 0.85rem !important;
        font-weight: 700 !important;
        transition: all 0.2s ease !important;
        box-shadow: none !important;
    }

    div.stButton > button:hover {
        background-color: #3B82F6 !important;
        color: #FFFFFF !important;
        border-color: #3B82F6 !important;
        transform: scale(1.05) !important;
    }

    /* Custom Input Control styling */
    div[data-testid="stChatInput"] {
        background-color: #FFFFFF !important;
        border-top: 2px solid #E5E7EB !important;
        box-shadow: none !important;
    }
    div[data-testid="stChatInput"] textarea {
        background-color: #F3F4F6 !important;
        border-radius: 6px !important;
        border: 2px solid #E5E7EB !important;
        padding: 0.6rem 1.2rem !important;
        color: #111827 !important;
    }
    div[data-testid="stChatInput"] textarea:focus {
        border-color: #3B82F6 !important;
        background-color: #FFFFFF !important;
    }
    footer { visibility: hidden; }
</style>
"""


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


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
                if "khô" in loai_lower:
                    avatar = "🍛"
                elif "ăn vặt" in loai_lower:
                    avatar = "🍟"
                elif "uống" in loai_lower or "nước" in loai_lower:
                    if "nước" in loai_lower and "đồ nước" not in loai_lower:
                        avatar = "🥤"
                
                price_val = item.get("gia", 0)
                price_formatted = f"{price_val:,}".replace(",", ".")
                
                html += f"""
                <div class="food-card">
                    <div class="food-card-header">
                        <div class="food-avatar">{avatar}</div>
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

# --- Init session state ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "history" not in st.session_state:
    st.session_state.history = []
if "transcript_turns" not in st.session_state:
    st.session_state.transcript_turns = []
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
    st.markdown("### Session")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Clear chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.history = []
            st.session_state.transcript_turns = []
            st.rerun()
    with col2:
        has_turns = bool(st.session_state.get("transcript_turns"))
        if st.button("New session", use_container_width=True, disabled=not has_turns):
            st.session_state.messages = []
            st.session_state.history = []
            st.session_state.transcript_turns = []
            st.rerun()

    if st.session_state.get("transcript_turns"):
        st.divider()
        st.markdown("### Transcript")
        transcript = {
            **artifact_version_dict(artifact_version),
            "provider": provider_name,
            "model": model or "default",
            "turns": st.session_state.transcript_turns,
            "created_at": now_iso(),
        }
        transcript_json = json.dumps(transcript, ensure_ascii=False, indent=2, default=str)
        st.download_button(
            "Download transcript",
            data=transcript_json,
            file_name=f"transcript_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True,
        )
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
st.markdown('<div class="main-header">SMART FOOD FINDER</div>', unsafe_allow_html=True)

# --- Tool count summary ---
enabled = [t["name"] for t in tool_declarations]
with st.expander(f"Available tools ({len(enabled)})"):
    cols = st.columns(4)
    for i, name in enumerate(enabled):
        cols[i % 4].code(name, language=None)

# --- Chat area ---
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
                    "user": user_input,
                    "status": result.get("status", "answered"),
                    "assistant_text": assistant_text,
                    "rounds": result.get("rounds", []),
                    "tool_events": result.get("tool_events", []),
                }
                st.session_state.transcript_turns.append(turn)

            except Exception as e:
                st.error(f"Error: {e}")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Error: {e}",
                    "tools_used": [],
                })

st.markdown("</div>", unsafe_allow_html=True)
