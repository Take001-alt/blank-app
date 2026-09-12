import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode
import json
import pandas as pd
from io import BytesIO
from copy import deepcopy
from datetime import datetime
from uuid import uuid4
import os
import hashlib
import urllib.request
import urllib.error
from pathlib import Path

# ---------------------------------------------------------
# PAGE CONFIGURATION / BRAND ASSETS
# ---------------------------------------------------------

APP_DIR = Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd()
ASSET_DIR = APP_DIR / "assets"
ICON_CANDIDATES = [ASSET_DIR / "atlas_icon.png", APP_DIR / "atlas_icon.png", APP_DIR / "Atlas_Icon_withoutbg.png"]
LOGO_CANDIDATES = [ASSET_DIR / "atlas_logo.png", APP_DIR / "atlas_logo.png", APP_DIR / "ATLAS_Logo-banner.png", APP_DIR / "atlas_logo.jpg", APP_DIR / "atlas_logo.jpeg"]
ATLAS_ICON = next((path for path in ICON_CANDIDATES if path.exists()), None)
ATLAS_LOGO = next((path for path in LOGO_CANDIDATES if path.exists()), None)

st.set_page_config(
    page_title="ATLAS — AI-Assisted MES Translation",
    page_icon=str(ATLAS_ICON) if ATLAS_ICON else "🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------
# DEMO UI / BRANDING
# ---------------------------------------------------------
APP_VERSION = "v1.3.9 • Prototype Application"

st.markdown(
    '''
    <style>
    :root {
        --atlas-navy:#062E54; --atlas-navy-2:#0A416F; --atlas-blue:#087FB8;
        --atlas-cyan:#08C7DF; --atlas-cyan-soft:#E7FAFD; --atlas-ice:#F5FAFD;
        --atlas-silver:#E7EDF3; --atlas-text:#14324A; --atlas-muted:#65798A;
        --atlas-radius:14px;
    }
    @keyframes atlasFadeUp { from{opacity:0;transform:translateY(6px)} to{opacity:1;transform:translateY(0)} }
    @keyframes atlasPulse { 0%,100%{transform:scale(1);opacity:.55} 50%{transform:scale(1.16);opacity:1} }

    html, body, [class*="css"] { font-family:Inter,"Segoe UI",Arial,sans-serif; }
    div[data-testid="stAppViewContainer"] {
        background:radial-gradient(circle at 82% 0%,rgba(8,199,223,.065),transparent 24rem),linear-gradient(180deg,#FFF 0%,#FAFCFE 100%);
    }
    div[data-testid="stAppViewContainer"] .main .block-container {
        animation:atlasFadeUp .28s ease-out; max-width:1500px; padding-top:1rem; padding-bottom:2.5rem;
    }
    .atlas-hero { text-align:center; margin:.1rem auto .7rem; max-width:940px; }
    .atlas-brand-title { color:var(--atlas-navy);font-size:1.72rem;font-weight:780;line-height:1.15;letter-spacing:-.025em;margin-top:.35rem; }
    .atlas-brand-subtitle { color:var(--atlas-muted);font-size:.95rem;margin-top:.28rem; }
    .atlas-version-chip { display:inline-flex;align-items:center;gap:.35rem;margin-top:.55rem;padding:.28rem .62rem;border:1px solid rgba(8,127,184,.20);border-radius:999px;color:var(--atlas-navy-2);background:rgba(231,250,253,.7);font-size:.75rem;font-weight:650; }

    .atlas-flow { display:flex;justify-content:center;flex-wrap:wrap;align-items:center;gap:.38rem;margin:.85rem auto .55rem; }
    .atlas-step { border:1px solid rgba(8,127,184,.20);border-radius:999px;padding:.34rem .72rem;font-size:.80rem;font-weight:680;color:var(--atlas-navy);background:rgba(255,255,255,.92);box-shadow:0 2px 10px rgba(6,46,84,.04); }
    .atlas-step strong { color:var(--atlas-blue); } .atlas-arrow { color:var(--atlas-cyan);opacity:.85;font-size:.78rem; }

    h1,h2,h3 { color:var(--atlas-navy)!important;letter-spacing:-.015em; } h2 { margin-top:1.15rem!important; }
    hr { border-color:rgba(8,127,184,.12)!important; }

    div[data-testid="stMetric"] { background:rgba(255,255,255,.94);border:1px solid rgba(8,127,184,.12);border-radius:var(--atlas-radius);padding:.72rem .85rem;box-shadow:0 5px 18px rgba(6,46,84,.045);min-height:92px; }
    div[data-testid="stMetric"] label { color:var(--atlas-muted)!important; }
    div[data-testid="stMetricValue"] { color:var(--atlas-navy)!important;font-weight:760; }

    div.stButton>button,div.stDownloadButton>button { border-radius:10px!important;border:1px solid rgba(8,127,184,.26)!important;font-weight:650!important;transition:transform .12s ease,box-shadow .12s ease,border-color .12s ease; }
    div.stButton>button:hover,div.stDownloadButton>button:hover { transform:translateY(-1px);border-color:var(--atlas-cyan)!important;box-shadow:0 5px 16px rgba(6,46,84,.10); }
    button[kind="primary"] { background:linear-gradient(135deg,var(--atlas-navy-2),var(--atlas-blue))!important;color:white!important;border:none!important; }

    div[data-testid="stExpander"] { border:1px solid rgba(8,127,184,.12)!important;border-radius:var(--atlas-radius)!important;background:rgba(255,255,255,.84);box-shadow:0 3px 14px rgba(6,46,84,.03);overflow:hidden; }
    div[data-testid="stFileUploader"] section { border-radius:var(--atlas-radius)!important;border-color:rgba(8,127,184,.25)!important;background:var(--atlas-ice)!important; }
    div[data-baseweb="input"]>div,div[data-baseweb="select"]>div,textarea { border-radius:10px!important; }
    button[data-baseweb="tab"] { color:var(--atlas-muted)!important;font-weight:650!important; }
    button[data-baseweb="tab"][aria-selected="true"] { color:var(--atlas-navy)!important; }

    section[data-testid="stSidebar"] { background:linear-gradient(180deg,#F7FBFD 0%,#F1F8FB 100%);border-right:1px solid rgba(8,127,184,.12); }
    section[data-testid="stSidebar"]>div { padding-top:.75rem; }
    .atlas-sidebar-brand { text-align:center;padding:.30rem .20rem .55rem; }
    .atlas-sidebar-name { color:var(--atlas-navy);font-weight:800;letter-spacing:.12em;font-size:.92rem;margin-top:.15rem; }
    .atlas-sidebar-tagline { color:var(--atlas-muted);font-size:.70rem;margin-top:.12rem; }
    div[role="radiogroup"] label { border-radius:9px;transition:background-color .14s ease,transform .14s ease;padding:.15rem .20rem; }
    div[role="radiogroup"] label:hover { transform:translateX(2px);background:rgba(8,199,223,.07); }

    .atlas-loader { border:1px solid rgba(8,127,184,.16);border-radius:var(--atlas-radius);padding:.8rem 1rem;margin:.6rem 0;background:linear-gradient(135deg,rgba(231,250,253,.72),rgba(255,255,255,.95));animation:atlasFadeUp .22s ease-out; }
    .atlas-loader-title { color:var(--atlas-navy);font-weight:720;margin-bottom:.35rem; }
    .atlas-loader-dots { display:inline-flex;gap:7px;margin-right:.55rem;color:var(--atlas-cyan); }
    .atlas-loader-dots span { width:8px;height:8px;border-radius:50%;background:currentColor;display:inline-block;animation:atlasPulse 1.1s infinite ease-in-out; }
    .atlas-loader-dots span:nth-child(2){animation-delay:.14s}.atlas-loader-dots span:nth-child(3){animation-delay:.28s}
    .atlas-note { border-left:3px solid var(--atlas-cyan);background:var(--atlas-cyan-soft);color:var(--atlas-text);border-radius:0 10px 10px 0;padding:.58rem .78rem;margin:.45rem 0 .65rem;font-size:.84rem; }
    @media(max-width:900px){.atlas-brand-title{font-size:1.42rem}.atlas-step{font-size:.74rem;padding:.28rem .55rem}}
    </style>
    ''',
    unsafe_allow_html=True,
)

if ATLAS_LOGO:
    logo_left, logo_mid, logo_right = st.columns([1.0, 1.15, 1.0], vertical_alignment="center")
    with logo_mid:
        st.image(str(ATLAS_LOGO), use_container_width=True)
else:
    st.markdown('<div class="atlas-hero"><div class="atlas-brand-title">ATLAS — AI-Assisted MES Translation</div></div>', unsafe_allow_html=True)

st.markdown(
    f'<div class="atlas-hero"><div class="atlas-brand-title">AI-Assisted MES Translation</div>'
    f'<div class="atlas-brand-subtitle">MES Artifact • English → German • Human-Controlled Review</div>'
    f'<div class="atlas-version-chip">{APP_VERSION} • Controlled translation workflow</div></div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="atlas-flow">'
    '<span class="atlas-step"><strong>1</strong>&nbsp; Import</span><span class="atlas-arrow">→</span>'
    '<span class="atlas-step"><strong>2</strong>&nbsp; Translate</span><span class="atlas-arrow">→</span>'
    '<span class="atlas-step"><strong>3</strong>&nbsp; Review</span><span class="atlas-arrow">→</span>'
    '<span class="atlas-step"><strong>4</strong>&nbsp; Quality Check</span><span class="atlas-arrow">→</span>'
    '<span class="atlas-step"><strong>5</strong>&nbsp; Verify</span><span class="atlas-arrow">→</span>'
    '<span class="atlas-step"><strong>6</strong>&nbsp; Export</span>'
    '</div>', unsafe_allow_html=True,
)
st.markdown('<div class="atlas-note"><strong>Workflow principle:</strong> existing artifact translation → Translation Memory → controlled terminology → AI assistance → human approval → integrity verification.</div>', unsafe_allow_html=True)
st.divider()


def atlas_loading_card(title, detail):
    """Return a Streamlit placeholder showing a lightweight animated ATLAS loading card."""
    placeholder = st.empty()
    placeholder.markdown(
        f"""
        <div class="atlas-loader">
          <div class="atlas-loader-title">
            <span class="atlas-loader-dots"><span></span><span></span><span></span></span>
            {title}
          </div>
          <div style="opacity:.70;font-size:.88rem;">{detail}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    return placeholder

# ============================================================
# TRANSLATION MEMORY / TERMINOLOGY
# ============================================================

TM_FILE = Path(__file__).with_name("atlas_v11_translation_memory.json")
TERM_FILE = Path(__file__).with_name("atlas_v11_terminology.json")
AUDIT_FILE = Path(__file__).with_name("atlas_v11_audit_trail.json")

# Translation Memory = approved COMPLETE phrases/sentences.
DEFAULT_TRANSLATION_MEMORY = {
    "Return: eBR/eLog Differentiator": "Auslesen: eBR/eLog Differenzierung",
    "Return: Production Stream": "Auslesen: Produktionsstrom",
    "Calculate Production Stream": "Kalkuliere Produktionsstrom",
    "Scan Floor Scale": "Scanne die Bodenwaage",
    "WFI Bag is Installed": "WFI-Beutel ist installiert",
    "Confirm Correct Installation": "Bestätige korrekte Installation",
    "Select Process Activity": "Prozessaktivität wählen",
    "Select Format Part Set": "Formatteilsatz wählen",
    "Describe Cause Of Failure": "Ursache des Fehlers beschreiben",
}

# Terminology = controlled WORDS / TERMS that may occur inside larger phrases.
DEFAULT_TERMINOLOGY = {
    "Return": "Auslesen",
    "Display": "Anzeige",
    "Calculate": "Kalkuliere",
    "Select": "Wähle",
    "Equipment": "Equipment",
    "Sample": "Probe",
    "Sample ID": "Proben-ID",
    "Sample Volume": "Probenvolumen",
    "Storage Condition": "Lagerbedingung",
    "Product Number": "Produktnummer",
    "Batch Number": "Chargennummer",
    "Product Name": "Produktname",
    "Material Number": "Materialnummer",
    "Material Name": "Materialname",
    "Material Batch Number": "Materialchargennummer",
    "eBR/eLog Differentiator": "eBR/eLog-Differenzierung",
    "Production Stream": "Produktionsstrom",
    "WFI Bag": "WFI-Beutel",
    "WFI Bag ID": "WFI-Beutel-ID",
    "Floor Scale": "Bodenwaage",
    "Line Clearance": "Linienfreigabe",
    "Initiation": "Initiierung",
}


def _load_mapping(path, default):
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return {str(k): str(v) for k, v in data.items()}
        except Exception:
            pass
    return dict(default)


def _save_mapping(path, mapping):
    path.write_text(
        json.dumps(dict(sorted(mapping.items(), key=lambda x: x[0].lower())), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def load_translation_memory():
    return _load_mapping(TM_FILE, DEFAULT_TRANSLATION_MEMORY)


def save_translation_memory(memory):
    _save_mapping(TM_FILE, memory)


def get_translation_memory():
    if "translation_memory_v09" not in st.session_state:
        st.session_state.translation_memory_v09 = load_translation_memory()
    return st.session_state.translation_memory_v09


def load_terminology():
    return _load_mapping(TERM_FILE, DEFAULT_TERMINOLOGY)


def save_terminology(terms):
    _save_mapping(TERM_FILE, terms)


def get_terminology():
    if "terminology_v09" not in st.session_state:
        st.session_state.terminology_v09 = load_terminology()
    return st.session_state.terminology_v09


def set_flash_message(message, kind="success"):
    """Store a one-time UI notification that survives st.rerun()."""
    st.session_state.atlas_flash = {"message": message, "kind": kind}


def bump_translation_grid_revision():
    """Force the editable AgGrid to rebuild from the latest review_df state."""
    st.session_state["translation_grid_revision"] = (
        int(st.session_state.get("translation_grid_revision", 0)) + 1
    )


def show_flash_message():
    """Display and clear the pending toast notification."""
    flash = st.session_state.pop("atlas_flash", None)
    if not flash:
        return
    icons = {"success": "✅", "warning": "⚠️", "error": "❌", "info": "ℹ️"}
    st.toast(flash["message"], icon=icons.get(flash["kind"], "ℹ️"))


def add_to_translation_memory(source, target):
    source = str(source).strip()
    target = str(target).strip()
    if not source or not target:
        return "missing"
    memory = get_translation_memory()
    if source in memory:
        if memory[source] == target:
            return "duplicate"
        memory[source] = target
        save_translation_memory(memory)
        return "updated"
    memory[source] = target
    save_translation_memory(memory)
    return "added"


def remove_from_translation_memory(source):
    memory = get_translation_memory()
    if source in memory:
        del memory[source]
        save_translation_memory(memory)


def add_to_terminology(source, target):
    source = str(source).strip()
    target = str(target).strip()
    if not source or not target:
        return "missing"
    terms = get_terminology()
    if source in terms:
        if terms[source] == target:
            return "duplicate"
        terms[source] = target
        save_terminology(terms)
        return "updated"
    terms[source] = target
    save_terminology(terms)
    return "added"


def remove_from_terminology(source):
    terms = get_terminology()
    if source in terms:
        del terms[source]
        save_terminology(terms)


def find_terminology_matches(text):
    """Return controlled terms contained in a larger English source phrase."""
    text = str(text or "").strip()
    if not text:
        return []
    low = text.casefold()
    matches = []
    for source, target in get_terminology().items():
        if source.casefold() in low:
            matches.append((source, target))
    # Prefer more specific/longer terms first.
    return sorted(matches, key=lambda x: len(x[0]), reverse=True)



# ============================================================
# AI TRANSLATION PROVIDER LAYER
# ============================================================

AI_PROVIDERS = ["Disabled (Controlled Only)", "Google Gemini API", "OpenAI API"]
DEFAULT_OPENAI_MODEL = "gpt-5-mini"
DEFAULT_GEMINI_MODEL = "gemini-3.6-flash"


def _extract_openai_output_text(payload):
    """Extract assistant text from a Responses API JSON payload."""
    if not isinstance(payload, dict):
        return ""

    # Some clients/surfaces expose a convenience output_text field.
    direct = payload.get("output_text")
    if isinstance(direct, str) and direct.strip():
        return direct.strip()

    # REST Responses API returns an output array containing message/content items.
    chunks = []
    for item in payload.get("output", []) or []:
        if not isinstance(item, dict):
            continue
        for content in item.get("content", []) or []:
            if not isinstance(content, dict):
                continue
            if content.get("type") == "output_text":
                value = content.get("text", "")
                if isinstance(value, str) and value.strip():
                    chunks.append(value.strip())
    return "\n".join(chunks).strip()


def _extract_gemini_output_text(payload):
    """Extract text from a Gemini Interactions API response."""
    if not isinstance(payload, dict):
        return ""

    chunks = []
    for step in payload.get("steps", []) or []:
        if not isinstance(step, dict) or step.get("type") != "model_output":
            continue
        for content in step.get("content", []) or []:
            if not isinstance(content, dict):
                continue
            if content.get("type") == "text":
                value = content.get("text", "")
                if isinstance(value, str) and value.strip():
                    chunks.append(value.strip())
    return "\n".join(chunks).strip()



class AIServiceError(RuntimeError):
    """User-safe AI provider exception with a machine-readable category."""

    def __init__(self, message, *, provider="", status_code=None, kind="service"):
        super().__init__(message)
        self.provider = provider
        self.status_code = status_code
        self.kind = kind


def _gemini_http_error(exc, details="", *, qa=False):
    """Convert Gemini HTTP failures into concise ATLAS-friendly exceptions."""
    code = getattr(exc, "code", None)

    if code == 429:
        return AIServiceError(
            "The configured Gemini project has reached its current usage limit. "
            "Wait for the quota window to reset, use a project with available quota, "
            "or switch AI provider. No ATLAS review decisions or source JSON values were changed.",
            provider="Google Gemini",
            status_code=429,
            kind="quota",
        )
    if code in (401, 403):
        return AIServiceError(
            "Gemini authentication was not accepted. Check the API key, project access, and model permissions.",
            provider="Google Gemini",
            status_code=code,
            kind="authentication",
        )
    if code == 404:
        return AIServiceError(
            "The configured Gemini model or endpoint is unavailable. Check the selected model.",
            provider="Google Gemini",
            status_code=code,
            kind="configuration",
        )
    if code and code >= 500:
        return AIServiceError(
            "Gemini is temporarily unavailable. Try the request again later.",
            provider="Google Gemini",
            status_code=code,
            kind="service",
        )
    return AIServiceError(
        f"Gemini request could not be completed ({code or 'service error'}).",
        provider="Google Gemini",
        status_code=code,
        kind="service",
    )


def friendly_ai_message(exc):
    """Return short UI copy without exposing raw provider payloads."""
    if isinstance(exc, AIServiceError):
        if exc.kind == "quota":
            return (
                "AI service temporarily unavailable — the configured provider has reached "
                "its current usage limit. Controlled terminology, manual review, approval, "
                "integrity verification, and export remain available."
            )
        if exc.kind == "authentication":
            return "AI connection could not be authenticated. Check the API key and provider access."
        if exc.kind == "configuration":
            return "AI provider configuration needs attention. Check the selected model and provider settings."
        return str(exc)
    return "The AI request could not be completed. Review the provider configuration and try again."


def call_gemini_translation(
    source_text,
    context,
    terminology_matches,
    api_key,
    model=DEFAULT_GEMINI_MODEL,
):
    """Generate one German translation proposal with Gemini Interactions API."""
    api_key = str(api_key or "").strip()
    if not api_key:
        raise ValueError("Gemini API key is missing.")

    source_text = str(source_text or "").strip()
    context = str(context or "").strip()
    model = str(model or DEFAULT_GEMINI_MODEL).strip().removeprefix("models/")

    terminology_lines = [
        f"- {source_term} -> {target_term}"
        for source_term, target_term in (terminology_matches or [])
    ]
    terminology_text = "\n".join(terminology_lines) if terminology_lines else "- None"

    system_instruction = (
        "You are the translation proposal engine inside ATLAS, a controlled MES "
        "translation workflow. Translate English MES content to German. Return ONLY "
        "the proposed German translation, with no quotes, explanation, markdown, or "
        "labels. Preserve technical abbreviations, identifiers, product names, units, "
        "tokens, and MES terminology unless a controlled translation is supplied. "
        "Do not add meaning not present in the source. Use supplied approved target "
        "terms exactly where they apply. Keep wording concise and appropriate for an "
        "MES UI, instruction, field label, or section heading."
    )

    prompt = (
        f"Artifact context:\n{context or 'Not provided'}\n\n"
        f"Source text:\n{source_text}\n\n"
        f"Approved terminology that applies:\n{terminology_text}\n\n"
        "Produce the German translation only."
    )

    body = json.dumps({
        "model": model,
        "system_instruction": system_instruction,
        "input": prompt,
    }).encode("utf-8")

    endpoint = "https://generativelanguage.googleapis.com/v1beta/interactions"
    request = urllib.request.Request(
        endpoint,
        data=body,
        headers={
            "x-goog-api-key": api_key,
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        details = ""
        try:
            details = exc.read().decode("utf-8", errors="replace")
            parsed = json.loads(details)
            error_obj = parsed.get("error", {})
            details = error_obj.get("message", details)
        except Exception:
            pass
        raise _gemini_http_error(exc, details) from exc
    except urllib.error.URLError as exc:
        raise AIServiceError(
            "Unable to reach Gemini. Check the network connection and try again.",
            provider="Google Gemini",
            kind="network",
        ) from exc

    translation = _extract_gemini_output_text(payload)
    if not translation:
        status = payload.get("status", "") if isinstance(payload, dict) else ""
        errors = payload.get("errors", []) if isinstance(payload, dict) else []
        extra = f" Status: {status}." if status else ""
        if errors:
            extra += f" Errors: {errors}"
        raise RuntimeError(f"Gemini returned no translation text.{extra}")

    translation = translation.strip()
    if len(translation) >= 2 and translation[0] == translation[-1] and translation[0] in {'"', "'"}:
        translation = translation[1:-1].strip()
    return translation


def call_openai_translation(
    source_text,
    context,
    terminology_matches,
    api_key,
    model=DEFAULT_OPENAI_MODEL,
):
    """Generate one controlled German translation using OpenAI Responses API.

    The function returns only a proposal. It does not approve content, write to
    Translation Memory, or modify the source artifact.
    """
    api_key = str(api_key or "").strip()
    if not api_key:
        raise ValueError("OpenAI API key is missing.")

    source_text = str(source_text or "").strip()
    context = str(context or "").strip()

    terminology_lines = []
    for source_term, target_term in terminology_matches or []:
        terminology_lines.append(f"- {source_term} -> {target_term}")
    terminology_text = "\n".join(terminology_lines) if terminology_lines else "- None"

    instructions = (
        "You are the translation proposal engine inside ATLAS, a controlled MES "
        "translation workflow. Translate source-language MES content from English "
        "to German. Return ONLY the proposed German translation: no quotes, no "
        "explanation, no markdown, and no labels. Preserve technical abbreviations, "
        "identifiers, product names, units, tokens, and MES terminology unless a "
        "controlled translation is explicitly supplied. Do not add instructions, "
        "facts, warnings, or meaning not present in the source. If controlled "
        "terminology is supplied, use those approved target terms exactly where "
        "they apply. Keep the translation concise and appropriate for an MES UI, "
        "instruction, field label, or section heading."
    )

    prompt = (
        f"Artifact context:\n{context or 'Not provided'}\n\n"
        f"Source text:\n{source_text}\n\n"
        f"Approved terminology that applies:\n{terminology_text}\n\n"
        "Produce the German translation only."
    )

    body = json.dumps({
        "model": str(model or DEFAULT_OPENAI_MODEL).strip(),
        "instructions": instructions,
        "input": prompt,
        "max_output_tokens": 256,
        "store": False,
    }).encode("utf-8")

    request = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        details = ""
        try:
            details = exc.read().decode("utf-8", errors="replace")
            parsed = json.loads(details)
            details = parsed.get("error", {}).get("message", details)
        except Exception:
            pass
        raise RuntimeError(f"OpenAI API error {exc.code}: {details or exc.reason}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Unable to reach the OpenAI API: {exc.reason}") from exc

    translation = _extract_openai_output_text(payload)
    if not translation:
        raise RuntimeError("The AI provider returned no translation text.")

    # Defensive cleanup in case a model adds a simple enclosing quote.
    translation = translation.strip()
    if len(translation) >= 2 and translation[0] == translation[-1] and translation[0] in {'"', "'"}:
        translation = translation[1:-1].strip()

    return translation


def generate_ai_translation(
    provider,
    source_text,
    context,
    terminology_matches,
    api_key="",
    model="",
):
    """Provider-independent AI translation entry point.

    Additional enterprise/internal providers can be added here without changing
    the artifact parser or review workflow.
    """
    if provider == "Google Gemini API":
        return call_gemini_translation(
            source_text=source_text,
            context=context,
            terminology_matches=terminology_matches,
            api_key=api_key,
            model=model or DEFAULT_GEMINI_MODEL,
        )

    if provider == "OpenAI API":
        return call_openai_translation(
            source_text=source_text,
            context=context,
            terminology_matches=terminology_matches,
            api_key=api_key,
            model=model or DEFAULT_OPENAI_MODEL,
        )

    raise ValueError("No AI translation provider is enabled.")


def test_ai_provider(provider, api_key="", model=""):
    """Perform a minimal provider connectivity test."""
    if provider == "Google Gemini API":
        result = call_gemini_translation(
            source_text="Test label",
            context="ATLAS provider connection test",
            terminology_matches=[],
            api_key=api_key,
            model=model or DEFAULT_GEMINI_MODEL,
        )
        return bool(result)
    if provider == "OpenAI API":
        result = call_openai_translation(
            source_text="Test label",
            context="ATLAS provider connection test",
            terminology_matches=[],
            api_key=api_key,
            model=model or DEFAULT_OPENAI_MODEL,
        )
        return bool(result)
    raise ValueError("Select an AI provider before testing the connection.")



# ============================================================
# AI TRANSLATION QUALITY ASSURANCE
# ============================================================

def _parse_json_object_from_text(raw_text):
    """Parse a JSON object from model output, tolerating fenced code blocks."""
    text = str(raw_text or "").strip()
    if text.startswith("```"):
        text = text.strip("`").strip()
        if text.lower().startswith("json"):
            text = text[4:].strip()

    # Prefer direct parsing.
    try:
        value = json.loads(text)
        if isinstance(value, dict):
            return value
    except Exception:
        pass

    # Fall back to the first complete-looking object.
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        value = json.loads(text[start:end + 1])
        if isinstance(value, dict):
            return value

    raise ValueError("AI QA response was not valid JSON.")


def _normalize_qa_result(payload):
    """Normalize provider QA output into ATLAS controlled fields."""
    allowed_overall = {"Pass", "Warning", "Review Required"}
    allowed_check = {"Pass", "Warning", "Fail", "Not Applicable"}

    overall = str(payload.get("overall_result", "Review Required")).strip().title()
    if overall not in allowed_overall:
        overall = "Review Required"

    def check_value(key):
        value = str(payload.get(key, "Warning")).strip().title()
        return value if value in allowed_check else "Warning"

    return {
        "QA Result": overall,
        "QA Meaning": check_value("meaning_preservation"),
        "QA Terminology": check_value("terminology_compliance"),
        "QA Omission": check_value("omission_or_addition"),
        "QA Untranslated": check_value("untranslated_text"),
        "QA Ambiguity": check_value("ambiguity"),
        "QA Notes": str(payload.get("notes", "")).strip(),
    }


def call_gemini_quality_check(
    source_text,
    translation,
    context,
    terminology_matches,
    api_key,
    model=DEFAULT_GEMINI_MODEL,
):
    """Compare English source vs German translation using Gemini Interactions API."""
    api_key = str(api_key or "").strip()
    if not api_key:
        raise ValueError("Gemini API key is missing.")

    model = str(model or DEFAULT_GEMINI_MODEL).strip().removeprefix("models/")
    terminology_lines = [
        f"- {source_term} -> {target_term}"
        for source_term, target_term in (terminology_matches or [])
    ]
    terminology_text = "\n".join(terminology_lines) if terminology_lines else "- None"

    system_instruction = (
        "You are the quality-assurance checker inside ATLAS, a controlled MES "
        "translation workflow. Compare the English source with the German translation. "
        "Do NOT rewrite or approve the translation. Assess only translation quality. "
        "Pay special attention to meaning preservation, missing or added information, "
        "approved terminology, untranslated source text, and ambiguity. "
        "Return ONLY valid JSON and no markdown."
    )

    prompt = f"""
Artifact context:
{context or "Not provided"}

English source:
{source_text}

German translation:
{translation}

Approved terminology that applies:
{terminology_text}

Return exactly one JSON object with these keys:
{{
  "overall_result": "Pass | Warning | Review Required",
  "meaning_preservation": "Pass | Warning | Fail | Not Applicable",
  "terminology_compliance": "Pass | Warning | Fail | Not Applicable",
  "omission_or_addition": "Pass | Warning | Fail | Not Applicable",
  "untranslated_text": "Pass | Warning | Fail | Not Applicable",
  "ambiguity": "Pass | Warning | Fail | Not Applicable",
  "notes": "brief reviewer-focused explanation"
}}

Use "Pass" only when no material issue is detected.
Use "Warning" when the translation may be acceptable but deserves attention.
Use "Review Required" when one or more material issues may affect correctness.
"""

    body = json.dumps({
        "model": model,
        "system_instruction": system_instruction,
        "input": prompt,
    }).encode("utf-8")

    request = urllib.request.Request(
        "https://generativelanguage.googleapis.com/v1beta/interactions",
        data=body,
        headers={
            "x-goog-api-key": api_key,
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            response_payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        details = ""
        try:
            details = exc.read().decode("utf-8", errors="replace")
            parsed = json.loads(details)
            details = parsed.get("error", {}).get("message", details)
        except Exception:
            pass
        raise _gemini_http_error(exc, details, qa=True) from exc
    except urllib.error.URLError as exc:
        raise AIServiceError(
            "Unable to reach Gemini for the quality check. Check the network connection and try again.",
            provider="Google Gemini",
            kind="network",
        ) from exc

    raw_text = _extract_gemini_output_text(response_payload)
    if not raw_text:
        raise RuntimeError("Gemini QA returned no result.")

    return _normalize_qa_result(_parse_json_object_from_text(raw_text))


def generate_ai_quality_check(
    provider,
    source_text,
    translation,
    context,
    terminology_matches,
    api_key="",
    model="",
):
    """Provider-independent ATLAS QA entry point."""
    if provider == "Google Gemini API":
        return call_gemini_quality_check(
            source_text=source_text,
            translation=translation,
            context=context,
            terminology_matches=terminology_matches,
            api_key=api_key,
            model=model or DEFAULT_GEMINI_MODEL,
        )

    raise ValueError(
        "AI Quality Assurance is currently enabled for Google Gemini API in this build."
    )


# ============================================================
# AUDIT TRAIL
# ============================================================

def load_audit_trail():
    if AUDIT_FILE.exists():
        try:
            data = json.loads(AUDIT_FILE.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return data
        except Exception:
            pass
    return []


def save_audit_trail(records):
    AUDIT_FILE.write_text(
        json.dumps(records, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def get_audit_trail():
    if "audit_trail" not in st.session_state:
        st.session_state.audit_trail = load_audit_trail()
    return st.session_state.audit_trail


def record_audit_event(
    action,
    english_source="",
    previous_translation="",
    new_translation="",
    review_status="",
    source_file="",
    reason="",
    source_language="English",
    target_language="German",
    translation_source="",
):
    records = get_audit_trail()
    records.append({
        "Event ID": str(uuid4()),
        "Timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
        "Action": str(action),
        "Source Language": str(source_language),
        "Target Language": str(target_language),
        "Translation Source": str(translation_source or ""),
        "English Source": str(english_source or ""),
        "Previous Translation": str(previous_translation or ""),
        "New Translation": str(new_translation or ""),
        "Review Status": str(review_status or ""),
        "Source File": str(source_file or ""),
        "Reason for Change": str(reason or ""),
    })
    save_audit_trail(records)


def audit_dataframe():
    records = get_audit_trail()
    columns = [
        "Event ID", "Timestamp", "Action", "Source Language", "Target Language",
        "Translation Source", "English Source", "Previous Translation", "New Translation",
        "Review Status", "Source File", "Reason for Change"
    ]
    if not records:
        return pd.DataFrame(columns=columns)
    return pd.DataFrame(records).reindex(columns=columns)


def make_audit_excel(df):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Audit Trail")
    buffer.seek(0)
    return buffer

# ============================================================
# PAGE SELECTION
# ============================================================

with st.sidebar:
    st.markdown('<div class="atlas-sidebar-brand">', unsafe_allow_html=True)
    if ATLAS_ICON:
        icon_left, icon_mid, icon_right = st.columns([1, 1.15, 1])
        with icon_mid:
            st.image(str(ATLAS_ICON), use_container_width=True)
    elif ATLAS_LOGO:
        st.image(str(ATLAS_LOGO), use_container_width=True)
    st.markdown(
        '<div class="atlas-sidebar-name">ATLAS</div>'
        '<div class="atlas-sidebar-tagline">AI-ASSISTED MES TRANSLATION</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    page = st.radio(
        "ATLAS Module",
        ["Translation Workspace", "Translation Memory", "Terminology Manager", "Audit Trail"],
        index=0,
    )

    # --------------------------------------------------------
    # CURRENT ARTIFACT / SESSION FILE
    # --------------------------------------------------------
    st.divider()
    st.subheader("Current File")

    session_upload = st.file_uploader(
        "Load MODA-ES JSON",
        type=["json"],
        key="atlas_session_file_uploader",
        help="The loaded file stays available while you switch between ATLAS modules during this session.",
    )

    if session_upload is not None:
        try:
            file_bytes = session_upload.getvalue()
            parsed_json = json.loads(file_bytes.decode("utf-8"))
            new_file_key = (
                f"{session_upload.name}:"
                f"{len(file_bytes)}:"
                f"{hashlib.sha256(file_bytes).hexdigest()}"
            )

            if st.session_state.get("atlas_loaded_file_key") != new_file_key:
                st.session_state["atlas_uploaded_json"] = parsed_json
                st.session_state["atlas_uploaded_file_name"] = session_upload.name
                st.session_state["atlas_uploaded_file_bytes"] = file_bytes
                st.session_state["atlas_loaded_file_key"] = new_file_key

                # The review table must be rebuilt only when a genuinely different
                # artifact is loaded. Switching modules must not destroy review work.
                st.session_state.pop("review_df", None)
                st.session_state.pop("review_file_key", None)
                st.session_state.pop("translation_editor", None)
                bump_translation_grid_revision()
                st.session_state["atlas_new_file_loaded"] = True

        except (UnicodeDecodeError, json.JSONDecodeError):
            st.error("The selected file is not valid UTF-8 JSON.")

    if "atlas_uploaded_json" in st.session_state:
        current_name = st.session_state.get("atlas_uploaded_file_name", "Loaded JSON")
        st.success(f"Loaded: {current_name}")

        loaded_data = st.session_state.get("atlas_uploaded_json", {})
        loaded_sections = loaded_data.get("MeasurementData", {}).get("Sections", [])
        loaded_measurements = sum(
            len(section.get("Measurements", []))
            for section in loaded_sections
            if isinstance(section, dict)
        )
        st.caption(
            f"{len(loaded_sections)} section(s) • "
            f"{loaded_measurements} measurement(s) • Session persistent"
        )

        if st.button("Clear Loaded File", use_container_width=True):
            for key in [
                "atlas_uploaded_json",
                "atlas_uploaded_file_name",
                "atlas_uploaded_file_bytes",
                "atlas_loaded_file_key",
                "atlas_new_file_loaded",
                "review_df",
                "review_file_key",
                "translation_editor",
                "atlas_session_file_uploader",
            ]:
                st.session_state.pop(key, None)
            set_flash_message("Loaded artifact and its review workspace were cleared.", "warning")
            st.rerun()
    else:
        st.caption("No artifact loaded for this session.")
    st.divider()
    st.subheader("AI Translation Assistance")
    ai_provider = st.selectbox(
        "AI Provider",
        AI_PROVIDERS,
        index=1,
        help=(
            "AI is an optional fallback. Existing artifact translations, exact "
            "Translation Memory matches, and controlled terminology remain higher priority."
        ),
    )

    ai_model = ""
    ai_api_key = ""

    if ai_provider == "Google Gemini API":
        ai_model = st.text_input(
            "Model",
            value=DEFAULT_GEMINI_MODEL,
            help="Gemini model ID used only for unresolved translation proposals.",
        )
        env_key = os.getenv("GEMINI_API_KEY", "")
        ai_api_key = st.text_input(
            "Gemini API Key",
            value=env_key,
            type="password",
            help=(
                "The key is kept in the current Streamlit session and is not written "
                "to ATLAS Translation Memory, terminology, or audit files."
            ),
        )
        st.warning(
            "Prototype testing only: Gemini free-tier content may be used by Google "
            "to improve its products. Use synthetic/non-confidential MES data."
        )

    elif ai_provider == "OpenAI API":
        ai_model = st.text_input(
            "Model",
            value=DEFAULT_OPENAI_MODEL,
            help="API model ID used only for unresolved translation proposals.",
        )
        env_key = os.getenv("OPENAI_API_KEY", "")
        ai_api_key = st.text_input(
            "OpenAI API Key",
            value=env_key,
            type="password",
            help=(
                "The key is kept in the current Streamlit session and is not written "
                "to ATLAS Translation Memory, terminology, or audit files."
            ),
        )

    if ai_provider != "Disabled (Controlled Only)":
        if st.button("Test AI Connection", use_container_width=True):
            loader = atlas_loading_card(
                "Checking AI connection",
                "ATLAS is verifying the provider, API key, and selected model.",
            )
            try:
                test_ai_provider(ai_provider, ai_api_key, ai_model)
                st.session_state["ai_connection_state"] = "ready"
                st.session_state["ai_connection_message"] = "AI provider is ready for translation."
                set_flash_message("AI provider connection succeeded.", "success")
            except Exception as exc:
                st.session_state["ai_connection_state"] = "error"
                st.session_state["ai_connection_message"] = friendly_ai_message(exc)
                set_flash_message(friendly_ai_message(exc), "warning")
            finally:
                loader.empty()
            st.rerun()

        connection_state = st.session_state.get("ai_connection_state")
        connection_message = st.session_state.get("ai_connection_message", "")
        if connection_state == "ready":
            st.success(f"AI Ready — {connection_message}")
        elif connection_state == "error":
            st.warning(connection_message)

    st.caption("AI-generated suggestions require human review and are never auto-approved.")


# Show one-time notifications after page/rerun events.
show_flash_message()

# ============================================================
# AUDIT TRAIL PAGE
# ============================================================

if page == "Audit Trail":
    st.header("Audit Trail")
    st.caption("Persistent history of controlled terminology and translation-review actions performed in ATLAS.")

    audit_df = audit_dataframe()

    if audit_df.empty:
        st.info("No audit events have been recorded yet. Add, update, review, approve, reject, or delete a translation to create history.")
    else:
        c1, c2, c3 = st.columns(3)
        with c1:
            action_filter = st.selectbox(
                "Action",
                ["All"] + sorted(audit_df["Action"].dropna().astype(str).unique().tolist()),
            )
        with c2:
            status_filter = st.selectbox(
                "Review status",
                ["All"] + sorted([x for x in audit_df["Review Status"].dropna().astype(str).unique().tolist() if x]),
            )
        with c3:
            audit_search = st.text_input(
                "Search audit trail",
                placeholder="English, German, filename, reason...",
            )

        filtered_audit = audit_df.copy()
        if action_filter != "All":
            filtered_audit = filtered_audit[filtered_audit["Action"] == action_filter]
        if status_filter != "All":
            filtered_audit = filtered_audit[filtered_audit["Review Status"] == status_filter]
        if audit_search.strip():
            q = audit_search.strip()
            searchable = [
                "Action", "Translation Source", "English Source", "Previous Translation",
                "New Translation", "Source File", "Reason for Change"
            ]
            mask = pd.Series(False, index=filtered_audit.index)
            for col in searchable:
                mask = mask | filtered_audit[col].astype(str).str.contains(q, case=False, na=False, regex=False)
            filtered_audit = filtered_audit[mask]

        m1, m2, m3 = st.columns(3)
        m1.metric("Total events", len(audit_df))
        m2.metric("Displayed", len(filtered_audit))
        m3.metric("Unique actions", audit_df["Action"].nunique())

        display_df = filtered_audit.sort_values("Timestamp", ascending=False)
        st.dataframe(display_df, use_container_width=True, hide_index=True, height=520)

        st.subheader("Export Audit Trail")
        e1, e2 = st.columns(2)
        with e1:
            st.download_button(
                "Download Audit JSON",
                data=json.dumps(get_audit_trail(), ensure_ascii=False, indent=2),
                file_name="ATLAS_Audit_Trail.json",
                mime="application/json",
                use_container_width=True,
            )
        with e2:
            st.download_button(
                "Download Audit Excel",
                data=make_audit_excel(audit_df),
                file_name="ATLAS_Audit_Trail.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

    st.info(
        "Prototype note: the audit trail is append-only through the ATLAS interface and is stored locally as "
        "atlas_v11_audit_trail.json. A validated deployment should use authenticated users, access control, "
        "tamper-evident records, controlled time sources, and validated electronic records."
    )
    st.stop()

# ============================================================
# TRANSLATION MEMORY PAGE
# ============================================================

if page == "Translation Memory":
    st.header("Translation Memory")
    st.caption("Approved COMPLETE English → German phrases. Exact matches are used before terminology or any future AI translation.")

    memory = get_translation_memory()
    tm_df = pd.DataFrame([
        {"English": source, "German": target, "Status": "Approved"}
        for source, target in memory.items()
    ])

    if tm_df.empty:
        st.info("No approved translations are currently stored.")
    else:
        search = st.text_input(
            "Search translation memory",
            placeholder="Search English or German, e.g. Production Stream or Produktionsstrom",
            help="Searches both the English source and German translation. Partial matches are supported and search is case-insensitive.",
        )
        filtered = tm_df
        if search and search.strip():
            query = search.strip()
            mask = (
                filtered["English"].astype(str).str.contains(query, case=False, na=False, regex=False)
                | filtered["German"].astype(str).str.contains(query, case=False, na=False, regex=False)
            )
            filtered = filtered[mask]

        c_count, c_result = st.columns(2)
        with c_count:
            st.metric("Approved phrases", len(tm_df))
        with c_result:
            st.metric("Search results", len(filtered))

        if search and search.strip() and filtered.empty:
            st.info(f"No translation-memory entries matched '{search.strip()}'.")
        else:
            st.dataframe(filtered, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Add translation")
    c1, c2 = st.columns(2)
    with c1:
        new_source = st.text_input("English source", key="tm_new_source")
    with c2:
        new_target = st.text_input("German translation", key="tm_new_target")
    existing_for_entry = memory.get(str(new_source).strip()) if str(new_source).strip() else None
    change_reason = st.text_input(
        "Reason for change",
        key="tm_change_reason",
        placeholder="Required when changing an existing approved translation",
        help="A reason is required for updates. It is optional when adding a new translation.",
    )
    if st.button("Add / Update Translation", use_container_width=True):
        if existing_for_entry is not None and existing_for_entry != str(new_target).strip() and not change_reason.strip():
            set_flash_message("Reason for change is required when updating an approved translation.", "error")
            st.rerun()
        result = add_to_translation_memory(new_source, new_target)
        if result == "added":
            record_audit_event(
                "Translation Added",
                english_source=new_source,
                new_translation=new_target,
                review_status="Approved",
                reason=change_reason,
            )
            set_flash_message(f"Translation added: {new_source} → {new_target}", "success")
            st.rerun()
        elif result == "updated":
            record_audit_event(
                "Translation Updated",
                english_source=new_source,
                previous_translation=existing_for_entry,
                new_translation=new_target,
                review_status="Approved",
                reason=change_reason,
            )
            set_flash_message(f"Translation updated: {new_source} → {new_target}", "success")
            st.rerun()
        elif result == "duplicate":
            set_flash_message(
                f"Duplicate: '{new_source}' already has the same approved translation.",
                "warning",
            )
            st.rerun()
        else:
            set_flash_message("Both English source and German translation are required.", "error")
            st.rerun()

    st.divider()
    st.subheader("Remove translation")
    st.caption(
        "Remove an obsolete or incorrect approved phrase from Translation Memory. "
        "Deletion requires a reason and explicit confirmation, and the action is recorded in the audit trail."
    )

    if memory:
        tm_delete_sources = sorted(memory.keys(), key=lambda value: value.casefold())
        tm_delete_source = st.selectbox(
            "Translation to remove",
            tm_delete_sources,
            format_func=lambda source: f"{source} → {memory.get(source, '')}",
            key="tm_delete_source",
            help="Select the approved Translation Memory entry that should no longer be reused.",
        )
        tm_delete_target = memory.get(tm_delete_source, "")
        st.text_input(
            "Current approved translation",
            value=tm_delete_target,
            disabled=True,
            key="tm_delete_target_preview",
        )
        tm_delete_reason = st.text_input(
            "Reason for deletion",
            key="tm_delete_reason",
            placeholder="Required, e.g. obsolete wording, incorrect translation, duplicate entry",
        )
        tm_delete_confirm = st.checkbox(
            "I confirm that this Translation Memory entry should be removed.",
            key="tm_delete_confirm",
        )

        if st.button(
            "Delete Translation Memory Entry",
            use_container_width=True,
            type="secondary",
            disabled=not tm_delete_confirm,
        ):
            if not tm_delete_reason.strip():
                set_flash_message("A reason for deletion is required.", "error")
                st.rerun()

            # Capture the approved value before deletion so the audit trail preserves
            # exactly what was removed.
            previous_target = memory.get(tm_delete_source, "")
            remove_from_translation_memory(tm_delete_source)
            record_audit_event(
                "Translation Deleted",
                english_source=tm_delete_source,
                previous_translation=previous_target,
                new_translation="",
                review_status="Removed",
                reason=tm_delete_reason.strip(),
                translation_source="Translation Memory",
            )
            # Clear the delete controls so a rerun cannot accidentally repeat the action.
            st.session_state.pop("tm_delete_reason", None)
            st.session_state.pop("tm_delete_confirm", None)
            st.session_state.pop("tm_delete_target_preview", None)
            set_flash_message(
                f"Translation Memory entry removed: {tm_delete_source} → {previous_target}",
                "warning",
            )
            st.rerun()
    else:
        st.info("There are no Translation Memory entries available to remove.")

    st.divider()
    st.subheader("Export / Import")
    c1, c2 = st.columns(2)
    with c1:
        tm_json = json.dumps(memory, ensure_ascii=False, indent=2)
        st.download_button(
            "Download Translation Memory",
            data=tm_json,
            file_name="ATLAS_Translation_Memory_v11.json",
            mime="application/json",
            use_container_width=True,
        )
    with c2:
        import_file = st.file_uploader("Import Translation Memory", type=["json"], key="tm_import")
        if import_file is not None:
            try:
                imported = json.load(import_file)
                if not isinstance(imported, dict):
                    raise ValueError("Translation Memory JSON must contain an object of English → German pairs.")
                added_count = 0
                updated_count = 0
                duplicate_count = 0
                for raw_source, raw_target in imported.items():
                    source = str(raw_source).strip()
                    target = str(raw_target).strip()
                    if not source or not target:
                        continue
                    if source not in memory:
                        memory[source] = target
                        added_count += 1
                        record_audit_event(
                            "Translation Imported",
                            english_source=source,
                            new_translation=target,
                            review_status="Approved",
                            source_file=getattr(import_file, "name", ""),
                            reason="Translation Memory import",
                        )
                    elif memory[source] == target:
                        duplicate_count += 1
                    else:
                        previous_target = memory[source]
                        memory[source] = target
                        updated_count += 1
                        record_audit_event(
                            "Translation Updated by Import",
                            english_source=source,
                            previous_translation=previous_target,
                            new_translation=target,
                            review_status="Approved",
                            source_file=getattr(import_file, "name", ""),
                            reason="Translation Memory import",
                        )

                save_translation_memory(memory)
                set_flash_message(
                    f"Import complete: {added_count} added, {updated_count} updated, "
                    f"{duplicate_count} duplicate(s).",
                    "success",
                )
                st.rerun()
            except Exception as e:
                st.error(f"Import failed: {e}")

    st.info("v1.1 separation: Translation Memory stores approved complete phrases in atlas_v11_translation_memory.json. Controlled words/terms are managed separately in Terminology Manager.")
    st.stop()

# ============================================================
# TERMINOLOGY MANAGER PAGE
# ============================================================

if page == "Terminology Manager":
    st.header("Terminology Manager")
    st.caption("Controlled MES words and terms used as language constraints/context inside larger phrases.")

    terms = get_terminology()
    terminology_df = pd.DataFrame([
        {"English Term": source, "German Term": target, "Status": "Approved"}
        for source, target in terms.items()
    ])

    search_term = st.text_input(
        "Search terminology",
        placeholder="Search English or German terminology",
        help="Partial, case-insensitive search across both languages.",
    )
    filtered_terms = terminology_df.copy()
    if search_term.strip() and not filtered_terms.empty:
        q = search_term.strip()
        mask = (
            filtered_terms["English Term"].astype(str).str.contains(q, case=False, na=False, regex=False)
            | filtered_terms["German Term"].astype(str).str.contains(q, case=False, na=False, regex=False)
        )
        filtered_terms = filtered_terms[mask]

    m1, m2 = st.columns(2)
    m1.metric("Controlled terms", len(terminology_df))
    m2.metric("Search results", len(filtered_terms))
    if filtered_terms.empty:
        st.info("No terminology entries found.")
    else:
        st.dataframe(filtered_terms, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Add / Update Controlled Term")
    c1, c2 = st.columns(2)
    with c1:
        term_source = st.text_input("English term", key="term_new_source")
    with c2:
        term_target = st.text_input("German term", key="term_new_target")
    existing_term = terms.get(str(term_source).strip()) if str(term_source).strip() else None
    term_reason = st.text_input(
        "Reason for terminology change",
        key="term_change_reason_v08",
        placeholder="Required when changing an existing approved term",
    )
    if st.button("Add / Update Term", use_container_width=True):
        if existing_term is not None and existing_term != str(term_target).strip() and not term_reason.strip():
            set_flash_message("Reason for change is required when updating approved terminology.", "error")
            st.rerun()
        result = add_to_terminology(term_source, term_target)
        if result == "added":
            record_audit_event(
                "Terminology Added", english_source=term_source,
                new_translation=term_target, review_status="Approved", reason=term_reason,
            )
            set_flash_message(f"Terminology added: {term_source} → {term_target}", "success")
            st.rerun()
        elif result == "updated":
            record_audit_event(
                "Terminology Updated", english_source=term_source,
                previous_translation=existing_term, new_translation=term_target,
                review_status="Approved", reason=term_reason,
            )
            set_flash_message(f"Terminology updated: {term_source} → {term_target}", "success")
            st.rerun()
        elif result == "duplicate":
            set_flash_message(f"Duplicate terminology: '{term_source}' already has the same approved target term.", "warning")
            st.rerun()
        else:
            set_flash_message("Both English and German terminology are required.", "error")
            st.rerun()

    st.divider()
    st.subheader("Delete Controlled Term")
    if terms:
        term_to_delete = st.selectbox("Select term", sorted(terms.keys(), key=str.lower), key="term_delete_select_v08")
        delete_reason = st.text_input(
            "Reason for deletion", key="term_delete_reason_v08",
            placeholder="Required to delete approved terminology",
        )
        if st.button("Delete Selected Term", type="secondary"):
            if not delete_reason.strip():
                set_flash_message("Reason for deletion is required.", "error")
                st.rerun()
            previous_target = terms.get(term_to_delete, "")
            remove_from_terminology(term_to_delete)
            record_audit_event(
                "Terminology Deleted", english_source=term_to_delete,
                previous_translation=previous_target, review_status="Deleted", reason=delete_reason,
            )
            set_flash_message(f"Terminology deleted: {term_to_delete}", "success")
            st.rerun()

    st.divider()
    st.subheader("Export / Import Terminology")
    ec1, ec2 = st.columns(2)
    with ec1:
        st.download_button(
            "Download Terminology JSON",
            data=json.dumps(terms, ensure_ascii=False, indent=2),
            file_name="ATLAS_Terminology_v11.json",
            mime="application/json",
            use_container_width=True,
        )
    with ec2:
        term_import = st.file_uploader("Import Terminology", type=["json"], key="term_import_v08")
        if term_import is not None:
            try:
                imported = json.load(term_import)
                if not isinstance(imported, dict):
                    raise ValueError("Terminology JSON must contain an object of English → German term pairs.")
                added = updated = duplicates = 0
                for raw_source, raw_target in imported.items():
                    source = str(raw_source).strip(); target = str(raw_target).strip()
                    if not source or not target:
                        continue
                    old = terms.get(source)
                    result = add_to_terminology(source, target)
                    if result == "added":
                        added += 1
                        record_audit_event("Terminology Imported", english_source=source, new_translation=target,
                                           review_status="Approved", source_file=getattr(term_import, "name", ""),
                                           reason="Terminology import")
                    elif result == "updated":
                        updated += 1
                        record_audit_event("Terminology Updated by Import", english_source=source,
                                           previous_translation=old, new_translation=target, review_status="Approved",
                                           source_file=getattr(term_import, "name", ""), reason="Terminology import")
                    elif result == "duplicate":
                        duplicates += 1
                set_flash_message(f"Terminology import complete: {added} added, {updated} updated, {duplicates} duplicate(s).", "success")
                st.rerun()
            except Exception as e:
                st.error(f"Terminology import failed: {e}")

    st.info("v1.1 separation: Terminology is stored independently in atlas_v11_terminology.json and no longer edits Translation Memory records.")
    st.stop()

# ============================================================
# FILE UPLOAD
# ============================================================

# Translation hierarchy note removed from the UI.

st.header("1. Import MODA-ES JSON")

if "atlas_uploaded_json" in st.session_state:
    current_file_name = st.session_state.get("atlas_uploaded_file_name", "Loaded JSON")
    st.success(f"Working file: {current_file_name}")
    st.caption(
        #"This artifact is stored in the current ATLAS session. You can switch between "
        "Translation Workspace, Translation Memory, Terminology Manager, and Audit Trail "
        "without uploading it again."
    )
else:
    current_file_name = ""
    st.info("Load a MODA-ES JSON file from the **Current File** section in the sidebar.")

# ============================================================
# CONTROLLED TRANSLATION DICTIONARIES
# ============================================================

SECTION_TRANSLATIONS = {
    "Initiation": "Initiierung",
    "WFI Bag Preparation": "WFI-Beutelvorbereitung",
}

# v0.9: full-phrase Translation Memory and controlled Terminology remain separate assets.
TRANSLATION_MEMORY = get_translation_memory()
TERMINOLOGY = get_terminology()

# ============================================================
# TRANSLATION FUNCTIONS
# ============================================================

def split_bilingual_name(name):
    """Split MODA bilingual Name values using the first ' / ' separator.

    Example:
        Auslesen: Production Stream / Return: Production Stream
        -> ("Auslesen: Production Stream", "Return: Production Stream")

    If no bilingual separator is present, the value is treated as English-only.
    """
    if not name:
        return "", ""

    name = str(name).strip()
    if " / " in name:
        german, english = name.split(" / ", 1)
        return german.strip(), english.strip()

    return "", name


def build_controlled_terminology_proposal(english_text):
    """Build a deterministic proposal only when approved terminology covers ALL source words.

    The function is intentionally strict. It replaces the longest approved source
    terms first and then checks the remaining source text. If any letters or digits
    remain outside controlled terminology, no complete translation is generated.

    Examples:
        Production Stream -> Produktionsstrom
        Return: Production Stream -> Auslesen: Produktionsstrom

    But a phrase such as:
        Confirm Production Stream
    is not generated unless "Confirm" is also controlled terminology.
    """
    import re

    text = str(english_text or "").strip()
    if not text:
        return None

    terms = sorted(get_terminology().items(), key=lambda item: len(item[0]), reverse=True)
    working = text
    replacements = []

    # Replace approved terms with neutral placeholders so target-language text
    # cannot accidentally be reprocessed as source-language content.
    for source, target in terms:
        pattern = re.compile(re.escape(source), flags=re.IGNORECASE)
        if not pattern.search(working):
            continue

        def repl(_match, source=source, target=target):
            token = f"__ATLAS_TERM_{len(replacements)}__"
            replacements.append((token, source, target))
            return token

        working = pattern.sub(repl, working)

    if not replacements:
        return None

    # Remove placeholders and inspect only the original source material that was
    # not covered by terminology. Punctuation/whitespace are allowed to remain.
    uncovered = working
    for token, _, _ in replacements:
        uncovered = uncovered.replace(token, "")

    if re.search(r"[A-Za-z0-9]", uncovered):
        return None

    proposal = working
    for token, _, target in replacements:
        proposal = proposal.replace(token, target)

    # Tidy common spacing around punctuation without changing sentence content.
    proposal = re.sub(r"\s+([,:;.!?])", r"\1", proposal)
    proposal = re.sub(r"\s{2,}", " ", proposal).strip()
    return proposal


def propose_translation(english_text, existing_translation=""):
    """Return (proposal, source, terminology_matches) using the v0.9 hierarchy.

    1) Existing bilingual target text remains the baseline.
    2) Exact approved COMPLETE phrase in Translation Memory is used next.
    3) If approved terminology fully covers the source, ATLAS creates a strict,
       deterministic terminology-assisted proposal.
    4) Partially covered or unknown content is flagged for human review.

    AI is not called during parsing. Unresolved items can optionally receive AI suggestions later in the review workspace.
    """
    existing_translation = (existing_translation or "").strip()
    english_text = (english_text or "").strip()
    term_matches = find_terminology_matches(english_text)

    if existing_translation:
        return existing_translation, "Existing Artifact Translation", term_matches

    exact = TRANSLATION_MEMORY.get(english_text)
    if exact:
        return exact, "Translation Memory", term_matches

    terminology_proposal = build_controlled_terminology_proposal(english_text)
    if terminology_proposal:
        return terminology_proposal, "Controlled Terminology", term_matches

    return f"[TRANSLATE] / {english_text}", "Needs Human Translation", term_matches


def clean_context_label(section_label):
    """Return the artifact context exactly as a readable location label.

    Context is not itself a translation result. If a MODA section label is
    English-only, show the English label without the internal [TRANSLATE]
    marker. The section label is reviewed separately as its own translation
    item so untranslated structure remains visible and controllable.
    """
    if not section_label:
        return "UNKNOWN"
    return str(section_label).strip()


def split_section_label(section_label):
    """Split a MODA section label into existing target and source text.

    Uses the same bilingual convention as measurement names: German / English.
    English-only labels are returned with an empty current translation.
    """
    return split_bilingual_name(section_label)

# ============================================================
# REVIEW DATA
# ============================================================

def build_review_dataframe(original_data):
    """Build one normalized review table for MODA section labels and measurements.

    Section labels are first-class translation items. Each row also carries a
    simple Item Type (Section or Measurement), while Context always shows the
    actual artifact location. This lets the
    reviewer see exactly which human-readable fields in the source JSON still
    need translation.
    """
    results = []
    sections = original_data.get("MeasurementData", {}).get("Sections", [])

    for section_index, section in enumerate(sections):
        original_section_label = section.get("Label", "UNKNOWN")
        context_label = clean_context_label(original_section_label)

        # ---- Section label as its own review item ----
        section_existing, section_source = split_section_label(original_section_label)
        if section_source:
            section_proposed, section_proposal_source, section_term_matches = propose_translation(
                section_source, section_existing
            )
            section_terms_display = "; ".join(
                [f"{src_term} → {tgt_term}" for src_term, tgt_term in section_term_matches]
            )
            section_needs_review = section_proposed.startswith("[TRANSLATE]")

            results.append({
                "ID": len(results) + 1,
                "Item Type": "Section",
                "Section": context_label,
                "Section English": section_source,
                "English Source": section_source,
                "Existing Translation": section_existing,
                "Translation": section_proposed,
                "Proposal Source": section_proposal_source,
                "Terminology Matches": section_terms_display,
                "Status": "Needs Review" if section_needs_review else "Pending",
                "QA Result": "Not Checked",
                "QA Meaning": "",
                "QA Terminology": "",
                "QA Omission": "",
                "QA Untranslated": "",
                "QA Ambiguity": "",
                "QA Notes": "",
                "QA Checked Translation": "",
                "_item_type": "Section Label",
                "_section_index": section_index,
                "_measurement_index": -1,
                "_original_name": original_section_label,
            })

        # ---- Measurement names ----
        for measurement_index, measurement in enumerate(section.get("Measurements", [])):
            name = measurement.get("Name")
            if not name:
                continue

            existing_translation, english_source = split_bilingual_name(name)
            proposed, proposal_source, term_matches = propose_translation(
                english_source, existing_translation
            )
            terminology_display = "; ".join(
                [f"{src_term} → {tgt_term}" for src_term, tgt_term in term_matches]
            )
            needs_review = proposed.startswith("[TRANSLATE]")

            results.append({
                "ID": len(results) + 1,
                "Item Type": "Measurement",
                "Section": context_label,
                "Section English": section_source or original_section_label,
                "English Source": english_source,
                "Existing Translation": existing_translation,
                "Translation": proposed,
                "Proposal Source": proposal_source,
                "Terminology Matches": terminology_display,
                "Status": "Needs Review" if needs_review else "Pending",
                "QA Result": "Not Checked",
                "QA Meaning": "",
                "QA Terminology": "",
                "QA Omission": "",
                "QA Untranslated": "",
                "QA Ambiguity": "",
                "QA Notes": "",
                "QA Checked Translation": "",
                "_item_type": "Measurement Name",
                "_section_index": section_index,
                "_measurement_index": measurement_index,
                "_original_name": name,
            })

    return pd.DataFrame(results)

def apply_approved_translations(original_data, review_df):
    """Apply only explicitly approved section-label and measurement translations.

    Approved target text is written back as:
        <approved target> / <original source>

    Pending, Needs Review, and Rejected items retain their original JSON value.
    """
    translated_data = deepcopy(original_data)
    sections = translated_data.get("MeasurementData", {}).get("Sections", [])
    approved_count = 0

    for _, row in review_df.iterrows():
        if row["Status"] != "Approved":
            continue

        approved_translation = str(row["Translation"]).strip()
        english_source = str(row["English Source"]).strip()
        if not approved_translation or approved_translation.startswith("[TRANSLATE]"):
            continue

        section_index = int(row["_section_index"])
        item_type = str(row.get("_item_type", "Measurement Name"))

        try:
            bilingual_value = (
                f"{approved_translation} / {english_source}"
                if english_source else approved_translation
            )

            if item_type == "Section Label":
                sections[section_index]["Label"] = bilingual_value
            else:
                measurement_index = int(row["_measurement_index"])
                sections[section_index]["Measurements"][measurement_index]["Name"] = bilingual_value

            approved_count += 1
        except (IndexError, KeyError, TypeError, ValueError):
            continue

    return translated_data, approved_count


# ============================================================
# v1.3 EXPORT INTEGRITY VERIFICATION
# ============================================================

def _json_path(parts):
    """Render a human-readable JSON path for integrity reporting."""
    path = "$"
    for part in parts:
        if isinstance(part, int):
            path += f"[{part}]"
        else:
            path += f".{part}"
    return path


def _json_differences(original, exported, parts=()):
    """Return all structural/value differences between two JSON-compatible objects."""
    differences = []

    if type(original) is not type(exported):
        differences.append({
            "Path": _json_path(parts),
            "Change": "Type changed",
            "Original": repr(original),
            "Exported": repr(exported),
        })
        return differences

    if isinstance(original, dict):
        original_keys = set(original.keys())
        exported_keys = set(exported.keys())

        for key in sorted(original_keys - exported_keys):
            differences.append({
                "Path": _json_path(parts + (key,)),
                "Change": "Key removed",
                "Original": repr(original[key]),
                "Exported": "<missing>",
            })

        for key in sorted(exported_keys - original_keys):
            differences.append({
                "Path": _json_path(parts + (key,)),
                "Change": "Key added",
                "Original": "<missing>",
                "Exported": repr(exported[key]),
            })

        for key in sorted(original_keys & exported_keys):
            differences.extend(
                _json_differences(original[key], exported[key], parts + (key,))
            )
        return differences

    if isinstance(original, list):
        if len(original) != len(exported):
            differences.append({
                "Path": _json_path(parts),
                "Change": "List length changed",
                "Original": str(len(original)),
                "Exported": str(len(exported)),
            })

        for index, (original_item, exported_item) in enumerate(zip(original, exported)):
            differences.extend(
                _json_differences(original_item, exported_item, parts + (index,))
            )
        return differences

    if original != exported:
        differences.append({
            "Path": _json_path(parts),
            "Change": "Value changed",
            "Original": repr(original),
            "Exported": repr(exported),
        })

    return differences


def allowed_translation_paths(review_df):
    """Return JSON paths that ATLAS is permitted to change for approved review rows."""
    allowed = set()

    for _, row in review_df.iterrows():
        if str(row.get("Status", "")) != "Approved":
            continue

        translation = str(row.get("Translation", "")).strip()
        if not translation or translation.startswith("[TRANSLATE]"):
            continue

        try:
            section_index = int(row["_section_index"])
            item_type = str(row.get("_item_type", "Measurement Name"))

            if item_type == "Section Label":
                allowed.add(
                    f"$.MeasurementData.Sections[{section_index}].Label"
                )
            else:
                measurement_index = int(row["_measurement_index"])
                allowed.add(
                    f"$.MeasurementData.Sections[{section_index}].Measurements"
                    f"[{measurement_index}].Name"
                )
        except (KeyError, TypeError, ValueError):
            continue

    return allowed


def verify_export_integrity(original_data, exported_data, review_df):
    """Verify that only explicitly approved translatable JSON fields changed."""
    differences = _json_differences(original_data, exported_data)
    allowed_paths = allowed_translation_paths(review_df)

    expected_changes = []
    unexpected_changes = []

    for difference in differences:
        if difference["Path"] in allowed_paths and difference["Change"] == "Value changed":
            expected_changes.append(difference)
        else:
            unexpected_changes.append(difference)

    canonical_original = json.dumps(
        original_data, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    canonical_exported = json.dumps(
        exported_data, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")

    return {
        "status": "PASS" if not unexpected_changes else "FAIL",
        "expected_changes": expected_changes,
        "unexpected_changes": unexpected_changes,
        "allowed_paths": allowed_paths,
        "source_sha256": hashlib.sha256(canonical_original).hexdigest(),
        "output_sha256": hashlib.sha256(canonical_exported).hexdigest(),
    }


def make_integrity_report(integrity_result):
    """Create a plain-text v1.3 integrity report suitable for test evidence."""
    lines = [
        "ATLAS v1.3 — Export Integrity Verification",
        "",
        f"Result: {integrity_result['status']}",
        f"Expected translation changes: {len(integrity_result['expected_changes'])}",
        f"Unexpected changes: {len(integrity_result['unexpected_changes'])}",
        f"Source SHA-256: {integrity_result['source_sha256']}",
        f"Output SHA-256: {integrity_result['output_sha256']}",
        "",
        "Expected changes:",
    ]

    if integrity_result["expected_changes"]:
        for item in integrity_result["expected_changes"]:
            lines.append(f"- {item['Path']}: {item['Original']} -> {item['Exported']}")
    else:
        lines.append("- None")

    lines.extend(["", "Unexpected changes:"])
    if integrity_result["unexpected_changes"]:
        for item in integrity_result["unexpected_changes"]:
            lines.append(
                f"- {item['Path']} [{item['Change']}]: "
                f"{item['Original']} -> {item['Exported']}"
            )
    else:
        lines.append("- None")

    return "\n".join(lines)


def make_excel(review_df):
    export_df = review_df[
        [
            "ID",
            "Item Type",
            "Section",
            "Section English",
            "English Source",
            "Existing Translation",
            "Translation",
            "Proposal Source",
            "Terminology Matches",
            "Status",
            "QA Result",
            "QA Meaning",
            "QA Terminology",
            "QA Omission",
            "QA Untranslated",
            "QA Ambiguity",
            "QA Notes",
        ]
    ].copy()

    export_df.columns = [
        "#",
        "Type",
        "Context",
        "Original Section Label",
        "Source Text",
        "Current Translation",
        "Translation",
        "Translation Source",
        "Approved Terms Found",
        "Review Status",
        "AI QA Result",
        "Meaning Preservation",
        "Terminology Compliance",
        "Omission / Addition",
        "Untranslated Text",
        "Ambiguity",
        "AI QA Notes",
    ]

    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        export_df.to_excel(writer, index=False, sheet_name="Translation Review")
    buffer.seek(0)
    return buffer


def make_txt(review_df):
    lines = []
    for _, row in review_df.iterrows():
        lines.append(f"Type: {row.get('Item Type', '')}")
        lines.append(f"Context: {row['Section']}")
        lines.append(f"Source Text: {row['English Source']}")
        lines.append(f"Current Translation: {row['Existing Translation']}")
        lines.append(f"Translation: {row['Translation']}")
        lines.append(f"Translation Source: {row.get('Proposal Source', '')}")
        lines.append(f"Approved Terms Found: {row.get('Terminology Matches', '')}")
        lines.append(f"Status: {row['Status']}")
        lines.append(f"AI QA Result: {row.get('QA Result', 'Not Checked')}")
        lines.append(f"AI QA Notes: {row.get('QA Notes', '')}")
        lines.append("")
    return "\n".join(lines)

if "atlas_uploaded_json" in st.session_state:
    try:
        data = st.session_state["atlas_uploaded_json"]
        current_file_name = st.session_state.get("atlas_uploaded_file_name", "Loaded JSON")
        file_key = st.session_state.get("atlas_loaded_file_key", current_file_name)

        # Build a new review table only for a genuinely different artifact.
        # Normal Streamlit reruns and module switches preserve the existing table.
        if (
            st.session_state.get("review_file_key") != file_key
            or "review_df" not in st.session_state
        ):
            st.session_state.review_file_key = file_key
            st.session_state.review_df = build_review_dataframe(data)
            st.session_state.pop("translation_editor", None)

        review_df = st.session_state.review_df

        if st.session_state.pop("atlas_new_file_loaded", False):
            set_flash_message(f"Loaded {current_file_name} into the ATLAS session.", "success")

        sections = data.get("MeasurementData", {}).get("Sections", [])

        approved_now = int((review_df["Status"].astype(str) == "Approved").sum()) if not review_df.empty else 0
        unresolved_now = int(
            (review_df["Translation"].astype(str).str.startswith("[TRANSLATE]")
             | (review_df["Proposal Source"].astype(str) == "Needs Human Translation")).sum()
        ) if not review_df.empty else 0
        ds1, ds2, ds3, ds4 = st.columns(4)
        ds1.metric("Format", "MODA-ES JSON")
        ds2.metric("Translatable Items", len(review_df))
        ds3.metric("Approved", approved_now)
        ds4.metric("Needs Attention", unresolved_now)
        #st.caption("Workflow: Import → Translate → Review → Quality Check → Verify → Export")

        st.header("2. Artifact Overview")
        section_review_count = int((review_df["_item_type"] == "Section Label").sum()) if not review_df.empty else 0
        measurement_review_count = int((review_df["_item_type"] == "Measurement Name").sum()) if not review_df.empty else 0
        st.write(f"**Sections found:** {len(sections)}")
        st.write(f"**Section headings reviewed:** {section_review_count}")
        st.write(f"**Measurements extracted:** {measurement_review_count}")
        st.write(f"**Total translatable items:** {len(review_df)}")

        # ====================================================
        # TRANSLATION REVIEW
        # ====================================================

        st.header("3. Translate & Review")
        st.write(
            "Review each source item in context, compare any existing translation, and edit the proposed "
            "translation when needed. Only items explicitly marked **Approved** are written to the output artifact."
        )

        st.caption("Current artifact connector: MODA-ES JSON")

        with st.expander("What do the review statuses mean?", expanded=False):
            st.markdown(
                """
                **🟡 Pending** — A usable translation is available, but a reviewer has not yet accepted it.  
                **🟠 Needs Review** — ATLAS cannot confidently provide a complete controlled translation; reviewer input is required.  
                **🟢 Approved** — A reviewer has checked and accepted the translation for this artifact.  
                **🔴 Rejected** — A reviewer has checked the translation and decided it must not be used.
                """
            )

        # ----------------------------------------------------
        # AI FALLBACK FOR UNRESOLVED ITEMS
        # ----------------------------------------------------

        if not review_df.empty:
            unresolved_mask = (
                review_df["Translation"].astype(str).str.startswith("[TRANSLATE]")
                | (review_df["Proposal Source"].astype(str) == "Needs Human Translation")
            )
            unresolved_count = int(unresolved_mask.sum())

            with st.expander("AI Translation Assistance", expanded=unresolved_count > 0):
                st.write(
                    "AI is used only for items that ATLAS could not resolve from the existing "
                    "artifact, exact Translation Memory, or fully controlled terminology."
                )

                ac1, ac2, ac3 = st.columns(3)
                ac1.metric("Unresolved items", unresolved_count)
                ac2.metric("Provider", ai_provider)
                ai_limit = ac3.number_input(
                    "Max suggestions this run",
                    min_value=1,
                    max_value=50,
                    value=min(10, max(1, unresolved_count)) if unresolved_count else 1,
                    step=1,
                    help="Limits paid API calls during each generation run.",
                )

                if unresolved_count == 0:
                    st.success("No unresolved items require AI assistance.")
                elif ai_provider == "Disabled (Controlled Only)":
                    st.info(
                        "Select an AI Provider in the sidebar to generate suggestions. "
                        "Until then, unresolved items remain marked [TRANSLATE]."
                    )
                else:
                    st.caption(
                        "Generated AI proposals remain **Needs Review**. They are not written "
                        "to the approved artifact until a reviewer explicitly approves them."
                    )
                    if st.button(
                        "Generate AI Suggestions",
                        type="primary",
                        use_container_width=True,
                    ):
                        if ai_provider != "Disabled (Controlled Only)" and not str(ai_api_key).strip():
                            set_flash_message("Enter an API key before generating AI suggestions.", "error")
                            st.rerun()

                        target_indices = review_df.index[unresolved_mask].tolist()[: int(ai_limit)]
                        generated_count = 0
                        failed = []
                        quota_stopped = False

                        ai_loader = atlas_loading_card(
                            "ATLAS AI is translating MES content",
                            "Applying controlled terminology, MES context, and provider assistance. "
                            "Generated text will remain Needs Review.",
                        )
                        progress = st.progress(0, text="Preparing AI translation assistance...")
                        for pos, row_index in enumerate(target_indices, start=1):
                            row = review_df.loc[row_index]
                            source_text = str(row["English Source"]).strip()
                            context = str(row["Section"]).strip()
                            term_matches = find_terminology_matches(source_text)

                            try:
                                ai_translation = generate_ai_translation(
                                    provider=ai_provider,
                                    source_text=source_text,
                                    context=context,
                                    terminology_matches=term_matches,
                                    api_key=ai_api_key,
                                    model=ai_model,
                                )

                                previous_value = str(row["Translation"])
                                review_df.at[row_index, "Translation"] = ai_translation
                                review_df.at[row_index, "Proposal Source"] = (
                                    f"AI Suggested - {ai_provider} ({ai_model})"
                                )
                                # AI content always needs explicit reviewer attention.
                                review_df.at[row_index, "Status"] = "Needs Review"

                                record_audit_event(
                                    "AI Translation Suggested",
                                    english_source=source_text,
                                    previous_translation=previous_value,
                                    new_translation=ai_translation,
                                    review_status="Needs Review",
                                    source_file=current_file_name,
                                    reason="AI fallback used because no complete controlled translation was available",
                                    translation_source=f"{ai_provider} ({ai_model})",
                                )
                                generated_count += 1
                            except AIServiceError as exc:
                                failed.append(f"{source_text}: {friendly_ai_message(exc)}")
                                if exc.kind == "quota":
                                    quota_stopped = True
                                    st.session_state["ai_service_notice"] = friendly_ai_message(exc)
                                    break
                            except Exception as exc:
                                failed.append(f"{source_text}: {friendly_ai_message(exc)}")

                            progress.progress(
                                pos / max(1, len(target_indices)),
                                text=f"Processed {pos} of {len(target_indices)} unresolved item(s)",
                            )

                        progress.empty()
                        ai_loader.empty()
                        st.session_state.review_df = review_df

                        if quota_stopped:
                            set_flash_message(
                                f"AI requests stopped safely after the provider reported a usage limit. "
                                f"{generated_count} suggestion(s) were generated before the stop.",
                                "warning",
                            )
                            st.session_state["ai_generation_errors"] = failed
                        elif generated_count:
                            if failed:
                                set_flash_message(
                                    f"Generated {generated_count} AI suggestion(s); "
                                    f"{len(failed)} item(s) could not be completed.",
                                    "warning",
                                )
                                st.session_state["ai_generation_errors"] = failed
                            else:
                                set_flash_message(
                                    f"Generated {generated_count} AI suggestion(s). Review and approve them manually.",
                                    "success",
                                )
                        else:
                            set_flash_message("No AI suggestions were generated.", "warning")
                            st.session_state["ai_generation_errors"] = failed
                        st.rerun()

                service_notice = st.session_state.pop("ai_service_notice", None)
                if service_notice:
                    st.warning(service_notice)

                ai_errors = st.session_state.pop("ai_generation_errors", None)
                if ai_errors:
                    st.info(
                        "One or more AI requests could not be completed. "
                        "Your source artifact and existing review decisions remain unchanged."
                    )
                    with st.expander("AI request details"):
                        for error in ai_errors:
                            st.write(f"- {error}")

        # ----------------------------------------------------
        # WORKFLOW CONTROLS
        # ----------------------------------------------------

        if not review_df.empty:
            control1, control2, control3, control4 = st.columns(4)

            with control1:
                if st.button("Approve All", use_container_width=True):
                    usable_mask = ~review_df["Translation"].astype(str).str.startswith("[TRANSLATE]")
                    rejected_mask = review_df["Status"].astype(str).eq("Rejected")
                    approve_mask = usable_mask & ~rejected_mask

                    for row_pos, audit_row in review_df.iterrows():
                        if bool(approve_mask.loc[row_pos]) and audit_row["Status"] != "Approved":
                            record_audit_event(
                                "Review Approved",
                                english_source=audit_row["English Source"],
                                previous_translation=audit_row["Existing Translation"],
                                new_translation=audit_row["Translation"],
                                review_status="Approved",
                                source_file=current_file_name,
                                reason="Approve All review action; explicitly rejected rows preserved",
                                translation_source=audit_row.get("Proposal Source", ""),
                            )

                    review_df.loc[approve_mask, "Status"] = "Approved"
                    review_df.loc[~usable_mask & ~rejected_mask, "Status"] = "Needs Review"
                    st.session_state.review_df = review_df
                    bump_translation_grid_revision()

                    unresolved = int((~usable_mask & ~rejected_mask).sum())
                    preserved_rejected = int(rejected_mask.sum())

                    if unresolved or preserved_rejected:
                        message_parts = []
                        if unresolved:
                            message_parts.append(f"{unresolved} unresolved item(s) remain Needs Review")
                        if preserved_rejected:
                            message_parts.append(f"{preserved_rejected} rejected item(s) were preserved")
                        set_flash_message(
                            "Approved all eligible translations. " + "; ".join(message_parts) + ".",
                            "warning",
                        )
                    else:
                        set_flash_message(
                            "All eligible review items approved and recorded in the audit trail.",
                            "success",
                        )
                    st.rerun()

            with control2:
                if st.button("Reject All", use_container_width=True):
                    for _, audit_row in review_df.iterrows():
                        if audit_row["Status"] != "Rejected":
                            record_audit_event(
                                "Review Rejected",
                                english_source=audit_row["English Source"],
                                previous_translation=audit_row["Existing Translation"],
                                new_translation=audit_row["Translation"],
                                review_status="Rejected",
                                source_file=current_file_name,
                                reason="Reject All review action",
                                translation_source=audit_row.get("Proposal Source", ""),
                            )
                    review_df["Status"] = "Rejected"
                    st.session_state.review_df = review_df
                    bump_translation_grid_revision()
                    set_flash_message("All review items rejected and recorded in the audit trail.", "warning")
                    st.rerun()

            with control3:
                if st.button("Reset Review", use_container_width=True):
                    record_audit_event(
                        "Review Reset",
                        source_file=current_file_name,
                        reason="Translation review reset to uploaded-file baseline",
                    )
                    st.session_state.review_df = build_review_dataframe(data)
                    bump_translation_grid_revision()
                    set_flash_message("Translation review reset. The action was recorded in the audit trail.", "warning")
                    st.rerun()

            with control4:
                st.caption("Approve All preserves rows already marked Rejected.")

            st.divider()

            # ------------------------------------------------
            # EDITABLE REVIEW TABLE
            # ------------------------------------------------

            # Keep the main reviewer view concise and format-independent.
            # MODA-specific metadata remains available in the technical-details section below.
            # Add a reviewer-facing indicator so AI-generated rows are obvious.
            # This is display-only and does not alter the translated text or export logic.
            review_df["AI Translation"] = review_df["Proposal Source"].astype(str).apply(
                lambda value: "🔵 AI" if value.startswith("AI Suggested -") else ""
            )

            st.markdown("#### Find a translation to review")
            search_col, filter_col = st.columns([0.72, 0.28])
            with search_col:
                review_search = st.text_input(
                    "Search review table",
                    key="atlas_review_search",
                    placeholder="Search source, translation, section, status, or QA result...",
                    label_visibility="collapsed",
                    help=(
                        "Filter the main review table without changing the underlying review data. "
                        "Useful when an AI Quality Check identifies a specific item that needs attention."
                    ),
                )
            with filter_col:
                review_scope = st.selectbox(
                    "Filter",
                    [
                        "All items",
                        "AI translations",
                        "Needs Review",
                        "Approved",
                        "Rejected",
                        "QA Warning / Review Required",
                    ],
                    key="atlas_review_scope",
                    label_visibility="collapsed",
                )

            # Preserve original review_df row identity while presenting only matching rows.
            # This prevents filtered table edits from being written back to the wrong item.
            visible_mask = pd.Series(True, index=review_df.index)

            if review_scope == "AI translations":
                visible_mask &= review_df["Proposal Source"].astype(str).str.startswith("AI Suggested -")
            elif review_scope == "Needs Review":
                visible_mask &= review_df["Status"].astype(str).eq("Needs Review")
            elif review_scope == "Approved":
                visible_mask &= review_df["Status"].astype(str).eq("Approved")
            elif review_scope == "Rejected":
                visible_mask &= review_df["Status"].astype(str).eq("Rejected")
            elif review_scope == "QA Warning / Review Required":
                visible_mask &= review_df["QA Result"].astype(str).isin(["Warning", "Review Required"])

            if review_search.strip():
                query = review_search.strip()
                search_columns = [
                    "Item Type",
                    "Section",
                    "English Source",
                    "Existing Translation",
                    "Translation",
                    "Proposal Source",
                    "Terminology Matches",
                    "Status",
                    "QA Result",
                    "QA Notes",
                ]
                search_mask = pd.Series(False, index=review_df.index)
                for col_name in search_columns:
                    if col_name in review_df.columns:
                        search_mask |= review_df[col_name].astype(str).str.contains(
                            query,
                            case=False,
                            na=False,
                            regex=False,
                        )
                visible_mask &= search_mask

            visible_indices = review_df.index[visible_mask].tolist()

            if review_search.strip() or review_scope != "All items":
                if visible_indices:
                    st.caption(
                        f"Showing **{len(visible_indices)}** of **{len(review_df)}** review items. "
                        "Clear the search/filter to return to the full table."
                    )
                else:
                    st.info("No review items match the current search/filter.")

            editable_columns = [
                "AI Translation",
                "ID",
                "Item Type",
                "Section",
                "English Source",
                "Existing Translation",
                "Translation",
                "Terminology Matches",
                "Status",
            ]

            # AI-generated translations are highlighted across the entire editable row.
            st.caption(
                "🔵 **AI** = translation generated by ATLAS AI assistance. "
                "AI-generated rows remain **Needs Review** until a human reviewer approves or edits them."
            )

            # Whole-row AI highlighting requires an editable grid that supports row styling.
            # AgGrid keeps Translation and Review Status editable while allowing AI-generated
            # rows to be highlighted across the full width of the table.
            grid_df = review_df.loc[visible_indices, editable_columns].copy()
            grid_df["_review_index"] = visible_indices

            gb = GridOptionsBuilder.from_dataframe(grid_df)
            # Keep the review table compact and readable on first load.
            # Global wrapText/autoHeight previously caused narrow columns (especially
            # Type and Approved Terms Found) to expand each row vertically.
            gb.configure_default_column(
                resizable=True,
                sortable=True,
                filter=True,
                wrapText=False,
                autoHeight=False,
            )

            # Read-only reviewer context columns.
            for col_name in [
                "AI Translation",
                "ID",
                "Item Type",
                "Section",
                "English Source",
                "Existing Translation",
                "Terminology Matches",
            ]:
                gb.configure_column(col_name, editable=False)

            gb.configure_column(
                "_review_index",
                hide=True,
                editable=False,
            )
            gb.configure_column("AI Translation", header_name="AI", width=78, pinned="left", wrapText=False)
            gb.configure_column("ID", header_name="#", width=64, wrapText=False)
            gb.configure_column("Item Type", header_name="Type", width=125, minWidth=125, wrapText=False)
            gb.configure_column(
                "Section", header_name="Context", minWidth=200, flex=1,
                wrapText=False, tooltipField="Section"
            )
            gb.configure_column(
                "English Source", header_name="Source Text", minWidth=240, flex=1.4,
                wrapText=False, tooltipField="English Source"
            )
            gb.configure_column(
                "Existing Translation", header_name="Current Translation", minWidth=220, flex=1.2,
                wrapText=False, tooltipField="Existing Translation"
            )
            gb.configure_column(
                "Translation", header_name="Translation", editable=True, minWidth=240, flex=1.4,
                wrapText=False, tooltipField="Translation"
            )
            gb.configure_column(
                "Terminology Matches", header_name="Approved Terms Found", minWidth=210, flex=1.1,
                wrapText=False, tooltipField="Terminology Matches"
            )
            gb.configure_column(
                "Status", header_name="Review Status", editable=True,
                cellEditor="agSelectCellEditor",
                cellEditorParams={"values": ["Pending", "Needs Review", "Approved", "Rejected"]},
                width=150, minWidth=150, wrapText=False
            )

            # Highlight the ENTIRE row when ATLAS AI generated the current proposal.
            # A darker blue is used for selected rows so the row remains visibly selected.
            ai_row_style = JsCode(
                """
                function(params) {
                    const source = params.data && params.data['AI Translation'];
                    if (source && source.indexOf('AI') !== -1) {
                        return {
                            'backgroundColor': 'rgba(33, 150, 243, 0.16)',
                            'borderLeft': '4px solid #2196F3',
                            'fontWeight': '500'
                        };
                    }
                    return {};
                }
                """
            )
            gb.configure_grid_options(
                getRowStyle=ai_row_style,
                rowSelection="single",
                suppressRowClickSelection=False,
                animateRows=True,
                rowHeight=42,
                headerHeight=42,
            )

            st.caption(
                #"Rows highlighted in **blue** were generated by ATLAS AI assistance. "
                #"They still require human review before approval."
            )

            grid_response = AgGrid(
                grid_df,
                gridOptions=gb.build(),
                update_mode=GridUpdateMode.VALUE_CHANGED,
                allow_unsafe_jscode=True,
                fit_columns_on_grid_load=False,
                height=220 if not visible_indices else 540,
                theme="streamlit",
                key=(
                    f"translation_editor_grid_{st.session_state.get('translation_grid_revision', 0)}_"
                    f"{hashlib.sha256((review_search + '|' + review_scope).encode('utf-8')).hexdigest()[:10]}"
                ),
            )

            edited_df = grid_response["data"].copy()
            # Keep the stable original review index so filtered edits map back to the correct row.
            edited_df = edited_df[editable_columns + ["_review_index"]]
            with st.expander("Show technical details", expanded=False):
                st.caption(
                    "Technical metadata is kept available for developers, validators, and troubleshooting, "
                    "without cluttering the normal reviewer workspace."
                )
                technical_df = review_df[[
                    "ID",
                    "Item Type",
                    "_item_type",
                    "Section",
                    "Section English",
                    "English Source",
                    "Proposal Source",
                    "_section_index",
                    "_measurement_index",
                    "_original_name",
                ]].copy()
                technical_df.columns = [
                    "#",
                    "Display Type",
                    "Internal Item Type",
                    "Context",
                    "Original Section / Source Label",
                    "Source Text",
                    "Translation Source",
                    "MODA Section Index",
                    "MODA Measurement Index",
                    "Original MODA Value",
                ]
                st.dataframe(technical_df, use_container_width=True, hide_index=True)

            # Persist only the rows currently visible in the filtered grid.
            # Stable _review_index values ensure edits always map back to the correct source item.
            for _, edited_row in edited_df.iterrows():
                try:
                    row_index = int(edited_row["_review_index"])
                except (TypeError, ValueError):
                    continue

                if row_index not in review_df.index:
                    continue

                audit_row = review_df.loc[row_index]
                previous_translation = str(audit_row["Translation"])
                previous_status = str(audit_row["Status"])
                new_translation = str(edited_row["Translation"])
                new_status = str(edited_row["Status"])

                if previous_translation != new_translation:
                    record_audit_event(
                        "Review Translation Edited",
                        english_source=audit_row["English Source"],
                        previous_translation=previous_translation,
                        new_translation=new_translation,
                        review_status=new_status,
                        source_file=current_file_name,
                        reason="Translation edited in filtered review workspace",
                        translation_source=audit_row.get("Proposal Source", ""),
                    )

                if previous_status != new_status:
                    action = "Review Status Changed"
                    if new_status == "Approved":
                        action = "Review Approved"
                    elif new_status == "Rejected":
                        action = "Review Rejected"

                    record_audit_event(
                        action,
                        english_source=audit_row["English Source"],
                        previous_translation=audit_row["Existing Translation"],
                        new_translation=new_translation,
                        review_status=new_status,
                        source_file=current_file_name,
                        reason=f"Review status changed from {previous_status} to {new_status}",
                        translation_source=audit_row.get("Proposal Source", ""),
                    )

                review_df.at[row_index, "Translation"] = new_translation
                review_df.at[row_index, "Status"] = new_status

            st.session_state.review_df = review_df

            # ------------------------------------------------
            # AI TRANSLATION QUALITY ASSURANCE
            # ------------------------------------------------

            # If a reviewer edits a translation after QA was performed, mark the
            # previous QA result as stale instead of silently treating it as current.
            if "QA Checked Translation" in review_df.columns:
                for row_index in review_df.index:
                    checked_value = str(review_df.at[row_index, "QA Checked Translation"] or "")
                    current_value = str(review_df.at[row_index, "Translation"] or "")
                    if checked_value and checked_value != current_value:
                        review_df.at[row_index, "QA Result"] = "Stale - Recheck"
                        review_df.at[row_index, "QA Meaning"] = ""
                        review_df.at[row_index, "QA Terminology"] = ""
                        review_df.at[row_index, "QA Omission"] = ""
                        review_df.at[row_index, "QA Untranslated"] = ""
                        review_df.at[row_index, "QA Ambiguity"] = ""
                        review_df.at[row_index, "QA Notes"] = (
                            "Translation changed after the previous AI QA check. Run QA again."
                        )
                        review_df.at[row_index, "QA Checked Translation"] = ""

            with st.expander("Translation Quality Check", expanded=False):
                st.write(
                    #"AI-assisted quality review compares the source and current translation for meaning preservation, "
                    #"controlled terminology, omissions/additions, untranslated text, and ambiguity. "
                    #"It is advisory only and never changes Review Status or approves content."
                )

                qa_eligible_mask = (
                    review_df["Translation"].astype(str).str.strip().ne("")
                    & ~review_df["Translation"].astype(str).str.startswith("[TRANSLATE]")
                    & review_df["Status"].astype(str).ne("Rejected")
                )
                qa_eligible_count = int(qa_eligible_mask.sum())
                qa_checked_count = int(
                    review_df["QA Result"].astype(str).isin(
                        ["Pass", "Warning", "Review Required"]
                    ).sum()
                )

                qc1, qc2, qc3 = st.columns(3)
                qc1.metric("Eligible translations", qa_eligible_count)
                qc2.metric("QA checked", qa_checked_count)
                qa_limit = qc3.number_input(
                    "Max QA checks this run",
                    min_value=1,
                    max_value=50,
                    value=min(5, max(1, qa_eligible_count)) if qa_eligible_count else 1,
                    step=1,
                    key="qa_max_checks",
                    help="Limits AI calls during each QA run.",
                )

                qa_scope = st.radio(
                    "QA scope",
                    ["Not yet checked / stale", "All eligible translations"],
                    horizontal=True,
                    key="qa_scope",
                )

                if ai_provider == "Disabled (Controlled Only)":
                    st.info("Enable Google Gemini API in the sidebar to run AI Quality Assurance.")
                elif ai_provider != "Google Gemini API":
                    st.info("This v1.2 QA build currently supports Google Gemini API for QA checks.")
                elif qa_eligible_count == 0:
                    st.info("No usable translations are available for QA.")
                else:
                    if qa_scope == "Not yet checked / stale":
                        qa_target_mask = qa_eligible_mask & review_df["QA Result"].astype(str).isin(
                            ["Not Checked", "Stale - Recheck", ""]
                        )
                    else:
                        qa_target_mask = qa_eligible_mask

                    qa_target_indices = review_df.index[qa_target_mask].tolist()

                    st.caption(
                        f"{len(qa_target_indices)} translation(s) currently match the selected QA scope."
                    )

                    if st.button(
                        "Run AI Quality Assurance",
                        use_container_width=True,
                        type="primary",
                        disabled=not qa_target_indices,
                    ):
                        if not str(ai_api_key).strip():
                            set_flash_message("Enter the Gemini API key before running AI QA.", "error")
                            st.rerun()

                        selected_indices = qa_target_indices[: int(qa_limit)]
                        qa_completed = 0
                        qa_failed = []
                        qa_quota_stopped = False
                        qa_loader = atlas_loading_card(
                            "ATLAS AI is checking translation quality",
                            "Reviewing meaning preservation, terminology, omissions/additions, "
                            "untranslated text, and ambiguity.",
                        )
                        progress = st.progress(0, text="Preparing translation quality checks...")

                        for position, row_index in enumerate(selected_indices, start=1):
                            qa_row = review_df.loc[row_index]
                            source_text = str(qa_row["English Source"]).strip()
                            target_text = str(qa_row["Translation"]).strip()
                            context = str(qa_row["Section"]).strip()
                            term_matches = find_terminology_matches(source_text)

                            try:
                                qa_result = generate_ai_quality_check(
                                    provider=ai_provider,
                                    source_text=source_text,
                                    translation=target_text,
                                    context=context,
                                    terminology_matches=term_matches,
                                    api_key=ai_api_key,
                                    model=ai_model,
                                )

                                for field, value in qa_result.items():
                                    review_df.at[row_index, field] = value
                                review_df.at[row_index, "QA Checked Translation"] = target_text

                                record_audit_event(
                                    "AI Translation QA Performed",
                                    english_source=source_text,
                                    previous_translation="",
                                    new_translation=target_text,
                                    review_status=str(qa_row["Status"]),
                                    source_file=current_file_name,
                                    reason=(
                                        f"AI QA result: {qa_result['QA Result']}; "
                                        f"{qa_result['QA Notes']}"
                                    ),
                                    translation_source=f"{ai_provider} ({ai_model})",
                                )
                                qa_completed += 1
                            except AIServiceError as exc:
                                qa_failed.append(f"{source_text}: {friendly_ai_message(exc)}")
                                if exc.kind == "quota":
                                    qa_quota_stopped = True
                                    st.session_state["qa_service_notice"] = friendly_ai_message(exc)
                                    break
                            except Exception as exc:
                                qa_failed.append(f"{source_text}: {friendly_ai_message(exc)}")

                            progress.progress(
                                position / max(1, len(selected_indices)),
                                text=f"Checked {position} of {len(selected_indices)} translation(s)",
                            )

                        progress.empty()
                        qa_loader.empty()
                        st.session_state.review_df = review_df

                        if qa_failed:
                            st.session_state["qa_errors"] = qa_failed

                        if qa_completed:
                            set_flash_message(
                                f"AI QA completed for {qa_completed} translation(s). "
                                "Results are advisory and require reviewer judgment.",
                                "success" if not qa_failed else "warning",
                            )
                        else:
                            set_flash_message("No AI QA checks were completed.", "error")
                        st.rerun()

                qa_service_notice = st.session_state.pop("qa_service_notice", None)
                if qa_service_notice:
                    st.warning(qa_service_notice)

                qa_errors = st.session_state.pop("qa_errors", None)
                if qa_errors:
                    st.info(
                        "One or more AI quality checks could not be completed. "
                        "AI QA remains advisory and no approval status was changed automatically."
                    )
                    with st.expander("Quality check request details"):
                        for error in qa_errors:
                            st.write(f"- {error}")

                qa_display = review_df[
                    [
                        "ID",
                        "Item Type",
                        "English Source",
                        "Translation",
                        "QA Result",
                        "QA Meaning",
                        "QA Terminology",
                        "QA Omission",
                        "QA Untranslated",
                        "QA Ambiguity",
                        "QA Notes",
                    ]
                ].copy()

                qa_display.columns = [
                    "#",
                    "Type",
                    "Source Text",
                    "Translation",
                    "Overall QA",
                    "Meaning",
                    "Terminology",
                    "Omission / Addition",
                    "Untranslated Text",
                    "Ambiguity",
                    "QA Notes",
                ]

                st.dataframe(
                    qa_display,
                    use_container_width=True,
                    hide_index=True,
                    height=360,
                )

                st.caption(
                    "AI QA is a reviewer aid. A Pass result does not constitute approval, "
                    "validation evidence, or an electronic signature."
                )

            st.session_state.review_df = review_df

            # ------------------------------------------------
            # REVIEW SUMMARY
            # ------------------------------------------------

            approved = int((review_df["Status"] == "Approved").sum())
            rejected = int((review_df["Status"] == "Rejected").sum())
            pending = int((review_df["Status"] == "Pending").sum())
            needs_review = int((review_df["Status"] == "Needs Review").sum())

            st.subheader("Review Status")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Approved", approved)
            c2.metric("Rejected", rejected)
            c3.metric("Pending", pending)
            c4.metric("Needs Review", needs_review)

            if needs_review > 0:
                st.warning(
                    f"{needs_review} item(s) have no controlled translation. "
                    "Enter a translation and approve it if the wording has been reviewed."
                )

            if pending > 0 or needs_review > 0:
                st.info(
                    "The final JSON will not include Pending or Needs Review translations. "
                    "Those items will retain their original source value."
                )

            # =================================================
            # TRANSLATION MEMORY LEARNING
            # =================================================

            st.subheader("Learn from Approved Translations")
            st.caption(
                "Promote reviewed, approved complete phrases into Translation Memory so ATLAS can "
                "reuse them as exact matches in future artifacts. Approval in this file does not "
                "automatically make a phrase reusable; promotion is a separate controlled action."
            )

            current_memory = get_translation_memory()
            approved_rows = review_df[
                (review_df["Status"] == "Approved")
                & (~review_df["Translation"].astype(str).str.startswith("[TRANSLATE]"))
                & (review_df["English Source"].astype(str).str.strip() != "")
                & (review_df["Translation"].astype(str).str.strip() != "")
            ].copy()

            tm_candidates = []
            tm_already_stored = 0
            tm_conflicts = 0

            for row_pos, tm_row in approved_rows.iterrows():
                source_phrase = str(tm_row["English Source"]).strip()
                target_phrase = str(tm_row["Translation"]).strip()
                stored_target = current_memory.get(source_phrase)

                if stored_target == target_phrase:
                    tm_already_stored += 1
                    continue

                if stored_target is not None and stored_target != target_phrase:
                    tm_conflicts += 1
                    candidate_state = "Conflict"
                else:
                    candidate_state = "New"

                tm_candidates.append({
                    "row_index": row_pos,
                    "label": f"{source_phrase} → {target_phrase}",
                    "source": source_phrase,
                    "target": target_phrase,
                    "state": candidate_state,
                    "stored_target": stored_target or "",
                    "proposal_source": str(tm_row.get("Proposal Source", "")),
                })

            lc1, lc2, lc3 = st.columns(3)
            lc1.metric("Ready to learn", sum(1 for x in tm_candidates if x["state"] == "New"))
            lc2.metric("Already in Translation Memory", tm_already_stored)
            lc3.metric("Conflicts", tm_conflicts)

            new_candidates = [x for x in tm_candidates if x["state"] == "New"]

            if new_candidates:
                candidate_labels = [x["label"] for x in new_candidates]
                selected_tm_labels = st.multiselect(
                    "Approved phrases to save",
                    options=candidate_labels,
                    default=candidate_labels,
                    help=(
                        "Only translations already marked Approved are listed here. "
                        "Deselect anything that should remain specific to this artifact."
                    ),
                    key="tm_learning_selection",
                )

                if st.button(
                    "Save Selected to Translation Memory",
                    type="primary",
                    use_container_width=True,
                    disabled=not selected_tm_labels,
                ):
                    selected_set = set(selected_tm_labels)
                    learned = 0
                    for candidate in new_candidates:
                        if candidate["label"] not in selected_set:
                            continue
                        result = add_to_translation_memory(candidate["source"], candidate["target"])
                        if result == "added":
                            learned += 1
                            record_audit_event(
                                "Approved Translation Promoted to TM",
                                english_source=candidate["source"],
                                new_translation=candidate["target"],
                                review_status="Approved",
                                source_file=current_file_name,
                                reason="Reviewer promoted approved artifact translation to reusable Translation Memory",
                                translation_source=candidate["proposal_source"],
                            )

                    if learned:
                        set_flash_message(
                            f"{learned} approved phrase(s) saved to Translation Memory for future reuse.",
                            "success",
                        )
                    else:
                        set_flash_message(
                            "No new phrases were added. They may already exist in Translation Memory.",
                            "warning",
                        )
                    st.rerun()
            elif not approved_rows.empty and tm_conflicts == 0:
                st.success("All approved phrases from this artifact are already stored in Translation Memory.")
            elif approved_rows.empty:
                st.info("Approve one or more reviewed translations to make them eligible for Translation Memory.")

            if tm_conflicts:
                st.warning(
                    f"{tm_conflicts} approved phrase(s) conflict with an existing Translation Memory entry. "
                    "ATLAS will not overwrite approved memory automatically. Resolve these in Translation Memory "
                    "with a documented reason for change."
                )
                conflict_rows = []
                for candidate in tm_candidates:
                    if candidate["state"] == "Conflict":
                        conflict_rows.append({
                            "Source Text": candidate["source"],
                            "Existing TM Translation": candidate["stored_target"],
                            "Approved in This Artifact": candidate["target"],
                        })
                if conflict_rows:
                    with st.expander("Review Translation Memory conflicts"):
                        st.dataframe(
                            pd.DataFrame(conflict_rows),
                            use_container_width=True,
                            hide_index=True,
                        )

            # =================================================
            # GENERATE APPROVED OUTPUT
            # =================================================

            st.header("4. Verify & Export")

            approved_data, approved_count = apply_approved_translations(
                data, review_df
            )

            translated_json_string = json.dumps(
                approved_data,
                ensure_ascii=False,
                indent=2
            )

            # v1.3 integrity gate: compare the approved output against the source
            # and permit changes only to explicitly approved Section.Label and
            # Measurement.Name fields.
            integrity_result = verify_export_integrity(data, approved_data, review_df)
            integrity_report = make_integrity_report(integrity_result)

            st.subheader("Artifact Integrity")
            ic1, ic2, ic3 = st.columns(3)
            ic1.metric("Integrity Result", integrity_result["status"])
            ic2.metric("Expected Changes", len(integrity_result["expected_changes"]))
            ic3.metric("Unexpected Changes", len(integrity_result["unexpected_changes"]))

            if integrity_result["status"] == "PASS":
                st.success(
                    "Artifact integrity passed. No protected MODA fields were changed."
                )
            else:
                st.error(
                    "Artifact integrity failed. The translated JSON download is blocked because "
                    "one or more unexpected JSON changes were detected."
                )
                with st.expander("Review unexpected JSON changes", expanded=True):
                    st.dataframe(
                        pd.DataFrame(integrity_result["unexpected_changes"]),
                        use_container_width=True,
                        hide_index=True,
                    )

            with st.expander("Integrity details", expanded=False):
                st.code(
                    f"Source SHA-256: {integrity_result['source_sha256']}\n"
                    f"Output SHA-256: {integrity_result['output_sha256']}",
                    language="text",
                )
                if integrity_result["expected_changes"]:
                    st.write("Expected approved translation changes:")
                    st.dataframe(
                        pd.DataFrame(integrity_result["expected_changes"]),
                        use_container_width=True,
                        hide_index=True,
                    )
                else:
                    st.caption("No approved translation changes are present in the output yet.")

            if approved_count == len(review_df):
                st.success("All extracted translatable items are approved.")
            elif approved_count > 0:
                st.success(
                    f"{approved_count} of {len(review_df)} translatable item(s) approved. "
                    "Only approved translations will be exported."
                )
            else:
                st.warning("No translations have been approved yet.")

            # ------------------------------------------------
            # EXPORT
            # ------------------------------------------------

            excel_buffer = make_excel(review_df)
            txt_output = make_txt(review_df)

            col1, col2, col3 = st.columns(3)

            with col1:
                st.download_button(
                    label="🗂️ Download Translated MODA JSON",
                    data=translated_json_string,
                    file_name="MODA_ATLAS_Translated.json",
                    mime="application/json",
                    use_container_width=True,
                    disabled=integrity_result["status"] != "PASS",
                    help=(
                        "Available only when the v1.3 export integrity verification passes."
                    ),
                )

            with col2:
                st.download_button(
                    label="📊 Download Review Excel",
                    data=excel_buffer,
                    file_name="MODA_Translation_Review.xlsx",
                    mime=(
                        "application/vnd.openxmlformats-officedocument."
                        "spreadsheetml.sheet"
                    ),
                    use_container_width=True,
                )

            with col3:
                st.download_button(
                    label="📄 Download Review TXT",
                    data=txt_output,
                    file_name="MODA_Translation_Review.txt",
                    mime="text/plain",
                    use_container_width=True,
                )

            st.download_button(
                label="🛡️ Download Integrity Report",
                data=integrity_report,
                file_name="ATLAS_v1.3_Integrity_Report.txt",
                mime="text/plain",
                use_container_width=True,
            )

            # ------------------------------------------------
            # APPROVAL GATE
            # ------------------------------------------------

            if pending == 0 and needs_review == 0:
                st.success(
                    "Review complete. Every measurement has an explicit Approved or Rejected decision."
                )
            else:
                st.warning(
                    "Review is not complete. Resolve all Pending / Needs Review items "
                    "before treating the translation set as fully reviewed."
                )

            # =================================================
            # JSON PREVIEW
            # =================================================

            st.subheader("Translated JSON Preview")
            st.info(
                "The JSON is generated from a copy of the original file. "
                "Only approved Measurement Name values are changed by this review workflow. "
                "Rejected and unapproved measurement values remain unchanged."
            )

            with st.expander("Preview approved JSON"):
                st.code(translated_json_string[:20000], language="json")
                if len(translated_json_string) > 20000:
                    st.caption(
                        "Preview truncated to 20,000 characters. "
                        "The downloaded JSON contains the complete file."
                    )

        else:
            st.warning("No measurements were found in the uploaded file.")

    except json.JSONDecodeError:
        st.error("The uploaded file is not valid JSON.")

    except Exception as e:
        st.error("Unable to process the uploaded file.")
        st.exception(e)

else:
    st.info("Load a MODA-ES JSON file from the **Current File** section in the sidebar to begin.")


# Demo footer
#st.divider()
#st.caption("Prototype demo • AI-generated translations and quality findings are advisory • Human review and approval remain required • Use synthetic/non-confidential data")

# ---------------------------------------------------------
# DEMO FOOTER
# ---------------------------------------------------------
st.divider()
st.caption(
    "ATLAS prototype • AI suggestions and quality findings are advisory • "
    "Human review and approval remain required • Demo with synthetic/non-confidential data"
)
