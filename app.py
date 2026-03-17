import streamlit as st
import json
import os
import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib import colors

SESSION_FILE = "sessions.json"
DATABASES = ["Westlaw", "HeinOnline", "Google Scholar", "Lexis+", "Bloomberg Law", "Fastcase", "Other"]

# ── Session persistence ───────────────────────────────────────────────────────

def load_sessions():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE) as f:
            return json.load(f)
    return {}

def save_sessions(sessions):
    with open(SESSION_FILE, "w") as f:
        json.dump(sessions, f, indent=2)

# ── PDF generation ────────────────────────────────────────────────────────────

def generate_pdf(session):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=inch, leftMargin=inch,
                            topMargin=inch, bottomMargin=inch)
    styles = getSampleStyleSheet()

    entry_label = ParagraphStyle(
        "EntryLabel", parent=styles["Normal"],
        fontSize=9, textColor=colors.HexColor("#555555"),
        spaceAfter=2
    )
    entry_value = ParagraphStyle(
        "EntryValue", parent=styles["Normal"],
        fontSize=10, spaceAfter=6
    )

    story = []
    story.append(Paragraph("Legal Research Audit Trail", styles["Title"]))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cccccc")))
    story.append(Spacer(1, 14))

    story.append(Paragraph(f"<b>Matter:</b> {session['matter_name']}", styles["Normal"]))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"<b>Research Question:</b> {session['research_question']}", styles["Normal"]))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"<b>Researcher:</b> {session['researcher_name']}", styles["Normal"]))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"<b>Session Started:</b> {session['created']}", styles["Normal"]))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"<b>Exported:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles["Normal"]))
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#dddddd")))
    story.append(Spacer(1, 20))

    story.append(Paragraph(f"Search Log — {len(session['entries'])} entries", styles["Heading2"]))
    story.append(Spacer(1, 12))

    for i, entry in enumerate(session["entries"], 1):
        story.append(Paragraph(f"Entry {i} — {entry['timestamp']}", styles["Heading3"]))
        story.append(Paragraph("Database", entry_label))
        story.append(Paragraph(entry["database"], entry_value))
        story.append(Paragraph("Search String", entry_label))
        story.append(Paragraph(entry["search_string"], entry_value))
        story.append(Paragraph("Sources Found", entry_label))
        story.append(Paragraph(entry["sources_found"] or "None noted", entry_value))
        story.append(Paragraph("Relevance Note", entry_label))
        story.append(Paragraph(entry["relevance_note"] or "None", entry_value))
        story.append(Spacer(1, 8))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#eeeeee")))
        story.append(Spacer(1, 14))

    doc.build(story)
    buffer.seek(0)
    return buffer

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(page_title="Legal Research Audit Trail", layout="wide",
                   initial_sidebar_state="expanded")

# ── Styles ────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: #1a1a1a;
}

.stApp {
    background-color: #f7f6f3;
}

/* ── Landing / description block ── */
.landing {
    max-width: 680px;
    margin: 3rem auto 3.5rem;
    text-align: center;
    padding: 0 1rem;
}
.landing h1 {
    font-family: 'DM Serif Display', serif;
    font-size: 2.4rem;
    font-weight: 400;
    color: #111111;
    margin: 0 0 1rem;
    line-height: 1.2;
}
.landing p {
    font-size: 1rem;
    font-weight: 300;
    color: #555555;
    line-height: 1.7;
    margin: 0 0 0.6rem;
}
.landing .divider {
    width: 36px;
    height: 2px;
    background: #1a1a1a;
    margin: 1.5rem auto;
}
.landing .pills {
    display: flex;
    justify-content: center;
    gap: 0.5rem;
    flex-wrap: wrap;
    margin-top: 1.2rem;
}
.landing .pill {
    font-size: 0.75rem;
    font-weight: 500;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: #555555;
    border: 1px solid #cccccc;
    padding: 0.25rem 0.75rem;
    border-radius: 100px;
    background: #ffffff;
}

/* ── Session created confirmation ── */
.session-created {
    background: #111111;
    color: #f7f6f3;
    border-radius: 4px;
    padding: 2rem 2rem 1.8rem;
    margin: 0 0 2rem;
    position: relative;
}
.session-created .check {
    font-size: 1.5rem;
    margin-bottom: 0.5rem;
}
.session-created h2 {
    font-family: 'DM Serif Display', serif;
    font-size: 1.5rem;
    font-weight: 400;
    color: #f7f6f3;
    margin: 0 0 0.4rem;
}
.session-created .meta {
    font-size: 0.85rem;
    color: #999999;
    margin: 0;
    line-height: 1.6;
}
.session-created .meta strong {
    color: #dddddd;
}

/* ── Session header (active session) ── */
.session-header {
    border-bottom: 2px solid #1a1a1a;
    padding-bottom: 1rem;
    margin-bottom: 2rem;
}
.session-header .matter {
    font-family: 'DM Serif Display', serif;
    font-size: 1.8rem;
    font-weight: 400;
    color: #111111;
    margin: 0 0 0.3rem;
}
.session-header .question {
    font-size: 0.9rem;
    color: #555555;
    font-style: italic;
    margin: 0 0 0.2rem;
}
.session-header .byline {
    font-size: 0.8rem;
    color: #999999;
    letter-spacing: 0.03em;
}

/* ── Log entry form ── */
.form-section-label {
    font-size: 0.7rem;
    font-weight: 500;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #999999;
    margin-bottom: 1rem;
    display: block;
}

/* ── Entry log card ── */
.entry-card {
    background: #ffffff;
    border: 1px solid #e5e5e5;
    border-radius: 3px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.6rem;
}
.entry-card .entry-header {
    font-size: 0.75rem;
    font-weight: 500;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: #999999;
    margin-bottom: 0.5rem;
}
.entry-card .search-string {
    font-family: 'DM Serif Display', serif;
    font-size: 1rem;
    color: #111111;
    margin-bottom: 0.3rem;
}
.entry-card .entry-meta {
    font-size: 0.83rem;
    color: #555555;
    line-height: 1.6;
}
.entry-card .entry-label {
    color: #999999;
    font-size: 0.78rem;
    font-weight: 500;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    margin-right: 0.3rem;
}

/* ── Empty state ── */
.empty-log {
    text-align: center;
    padding: 2.5rem 1rem;
    color: #aaaaaa;
    font-size: 0.9rem;
    font-style: italic;
    border: 1px dashed #dddddd;
    border-radius: 3px;
    background: #ffffff;
    margin-top: 1rem;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: #f0ede8;
    border-right: 1px solid #e0ddd8;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    font-family: 'DM Serif Display', serif !important;
    font-weight: 400 !important;
}

/* ── Inputs ── */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
    border: 1px solid #d5d5d5 !important;
    border-radius: 3px !important;
    background: #ffffff !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.92rem !important;
    color: #1a1a1a !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: #1a1a1a !important;
    box-shadow: none !important;
}
[data-testid="stSelectbox"] > div > div {
    border: 1px solid #d5d5d5 !important;
    border-radius: 3px !important;
    background: #ffffff !important;
}

/* ── Buttons ── */
[data-testid="stButton"] > button[kind="primary"],
[data-testid="stButton"] > button {
    background-color: #111111 !important;
    color: #f7f6f3 !important;
    border: none !important;
    border-radius: 3px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.04em !important;
    padding: 0.5rem 1.2rem !important;
}
[data-testid="stButton"] > button:hover {
    background-color: #333333 !important;
}
[data-testid="stButton"] > button[kind="secondary"] {
    background-color: transparent !important;
    color: #888888 !important;
    border: 1px solid #dddddd !important;
}
[data-testid="stButton"] > button[kind="secondary"]:hover {
    border-color: #999999 !important;
    color: #555555 !important;
}

/* ── Download button ── */
[data-testid="stDownloadButton"] button {
    background-color: #111111 !important;
    color: #f7f6f3 !important;
    border: none !important;
    border-radius: 3px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
}
[data-testid="stDownloadButton"] button:hover {
    background-color: #333333 !important;
}

/* ── Section heading ── */
.section-heading {
    font-size: 0.7rem;
    font-weight: 500;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #999999;
    border-bottom: 1px solid #e5e5e5;
    padding-bottom: 0.5rem;
    margin-bottom: 1.2rem;
}

/* ── Export block ── */
.export-block {
    background: #ffffff;
    border: 1px solid #e5e5e5;
    border-radius: 3px;
    padding: 1.2rem 1.4rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.export-block .export-desc {
    font-size: 0.88rem;
    color: #555555;
}
.export-block .export-desc strong {
    color: #111111;
    display: block;
    margin-bottom: 0.15rem;
}

hr { border-color: #e5e5e5; }
</style>
""", unsafe_allow_html=True)

# ── Data ─────────────────────────────────────────────────────────────────────

sessions = load_sessions()
session_names = list(sessions.keys())

# ── Sidebar: session management ───────────────────────────────────────────────

with st.sidebar:
    st.markdown("### Sessions")
    st.markdown("---")

    selected = st.selectbox(
        "Load a session",
        ["— New session —"] + session_names,
        label_visibility="visible"
    )

    if selected != "— New session —" and selected in sessions:
        st.markdown("---")
        if st.button("Delete this session", type="secondary"):
            del sessions[selected]
            save_sessions(sessions)
            st.rerun()

# ── Main area ─────────────────────────────────────────────────────────────────

# New session flow
if selected == "— New session —":

    # Description block — only shown on the new session screen
    st.markdown("""
    <div class="landing">
        <h1>Legal Research<br>Audit Trail</h1>
        <div class="divider"></div>
        <p>
            A structured log for tracking every search you run during legal research —
            what you searched, where, what you found, and why it mattered.
        </p>
        <p>
            Each session ties searches to a specific matter or research question,
            giving you a reproducible record you can export as a formatted PDF memo.
        </p>
        <div class="pills">
            <span class="pill">Track search strings</span>
            <span class="pill">Log sources found</span>
            <span class="pill">Note relevance</span>
            <span class="pill">Export to PDF</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-heading">Start a new session</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        matter   = st.text_input("Matter / Case name", placeholder="e.g. Smith v. Jones (2024)")
        researcher = st.text_input("Researcher name", placeholder="Your name")
    with col2:
        question = st.text_area("Research question", height=108,
                                placeholder="e.g. Whether a non-compete clause is enforceable under Ohio law when...")

    st.markdown("")
    if st.button("Create Session"):
        if matter and question and researcher:
            sessions[matter] = {
                "matter_name":       matter,
                "research_question": question,
                "researcher_name":   researcher,
                "created":           datetime.now().strftime("%Y-%m-%d %H:%M"),
                "entries":           []
            }
            save_sessions(sessions)
            st.session_state["just_created"] = matter
            st.rerun()
        else:
            st.warning("Please fill in all three fields before creating a session.")

# Active session
else:
    session = sessions[selected]

    # ── Session-created confirmation banner ──────────────────────────────────
    if st.session_state.get("just_created") == selected:
        st.markdown(
            '<div class="session-created">'
            '<div class="check">✓</div>'
            '<h2>Session created</h2>'
            '<p class="meta">'
            '<strong>' + session["matter_name"] + '</strong><br>'
            + session["research_question"][:120] + ('…' if len(session["research_question"]) > 120 else '') +
            '<br><br>Researcher: <strong>' + session["researcher_name"] + '</strong> &nbsp;·&nbsp; '
            'Started: <strong>' + session["created"] + '</strong>'
            '</p>'
            '</div>',
            unsafe_allow_html=True
        )
        del st.session_state["just_created"]

    # ── Session header ───────────────────────────────────────────────────────
    st.markdown(
        '<div class="session-header">'
        '<div class="matter">' + session["matter_name"] + '</div>'
        '<div class="question">' + session["research_question"] + '</div>'
        '<div class="byline">' + session["researcher_name"] + ' &nbsp;·&nbsp; Started ' + session["created"] + '</div>'
        '</div>',
        unsafe_allow_html=True
    )

    # ── Log a search ─────────────────────────────────────────────────────────
    st.markdown('<div class="section-heading">Log a search</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        search_string = st.text_input("Search string", placeholder="e.g. \"non-compete\" /s enforceable /p Ohio")
        database      = st.selectbox("Database", DATABASES)
    with col2:
        sources_found  = st.text_area("Sources / results noted", height=100,
                                      placeholder="Case names, citations, anything worth recording...")
        relevance_note = st.text_area("Relevance note", height=100,
                                      placeholder="Why kept, why ruled out, what to follow up on...")

    st.markdown("")
    if st.button("Add Entry"):
        if search_string:
            session["entries"].append({
                "timestamp":      datetime.now().strftime("%Y-%m-%d %H:%M"),
                "search_string":  search_string,
                "database":       database,
                "sources_found":  sources_found,
                "relevance_note": relevance_note
            })
            save_sessions(sessions)
            st.toast("Entry logged.", icon="✓")
            st.rerun()
        else:
            st.warning("Enter a search string before adding an entry.")

    # ── Running log ──────────────────────────────────────────────────────────
    st.markdown("")
    n = len(session["entries"])
    label = str(n) + " entr" + ("ies" if n != 1 else "y")
    st.markdown('<div class="section-heading">Search log &mdash; ' + label + '</div>',
                unsafe_allow_html=True)

    if not session["entries"]:
        st.markdown(
            '<div class="empty-log">No searches logged yet. Add your first entry above.</div>',
            unsafe_allow_html=True
        )
    else:
        for entry in reversed(session["entries"]):
            sources_text = entry["sources_found"] or "None noted"
            relevance_text = entry["relevance_note"] or "—"
            st.markdown(
                '<div class="entry-card">'
                '<div class="entry-header">' + entry["timestamp"] + ' &nbsp;·&nbsp; ' + entry["database"] + '</div>'
                '<div class="search-string">' + entry["search_string"] + '</div>'
                '<div class="entry-meta">'
                '<span class="entry-label">Sources</span>' + sources_text + '<br>'
                '<span class="entry-label">Note</span>' + relevance_text +
                '</div>'
                '</div>',
                unsafe_allow_html=True
            )

        # ── Export ───────────────────────────────────────────────────────────
        st.markdown("")
        st.markdown('<div class="section-heading">Export</div>', unsafe_allow_html=True)

        pdf_buffer = generate_pdf(session)
        filename   = session["matter_name"].replace(" ", "_") + "_research_memo.pdf"

        st.download_button(
            label="Download Research Memo (PDF)",
            data=pdf_buffer,
            file_name=filename,
            mime="application/pdf"
        )
