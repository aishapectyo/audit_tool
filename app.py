"""
Legal Research Audit Trail
Run: streamlit run audit_trail.py
"""

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
DATABASES = ["Westlaw", "HeinOnline", "Google Scholar", "Lexis+",
             "Bloomberg Law", "Fastcase", "Other"]

# ── Persistence ───────────────────────────────────────────────────────────────

def load_sessions():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE) as f:
            return json.load(f)
    return {}

def save_sessions(sessions):
    with open(SESSION_FILE, "w") as f:
        json.dump(sessions, f, indent=2)

# ── PDF ───────────────────────────────────────────────────────────────────────

def generate_pdf(session):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=inch, leftMargin=inch,
                            topMargin=inch, bottomMargin=inch)
    styles = getSampleStyleSheet()
    label_style = ParagraphStyle("Label", parent=styles["Normal"],
                                 fontSize=8, textColor=colors.HexColor("#666666"),
                                 spaceAfter=2)
    value_style = ParagraphStyle("Value", parent=styles["Normal"],
                                 fontSize=10, spaceAfter=8)
    story = []
    story.append(Paragraph("Legal Research Audit Trail", styles["Title"]))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cccccc")))
    story.append(Spacer(1, 14))
    story.append(Paragraph("<b>Matter:</b> " + session["matter_name"], styles["Normal"]))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Research Question:</b> " + session["research_question"], styles["Normal"]))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Researcher:</b> " + session["researcher_name"], styles["Normal"]))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Started:</b> " + session["created"], styles["Normal"]))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Exported:</b> " + datetime.now().strftime("%Y-%m-%d %H:%M"), styles["Normal"]))
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#dddddd")))
    story.append(Spacer(1, 16))
    story.append(Paragraph("Search Log — " + str(len(session["entries"])) + " entries", styles["Heading2"]))
    story.append(Spacer(1, 10))
    for i, e in enumerate(session["entries"], 1):
        story.append(Paragraph("Entry " + str(i) + " — " + e["timestamp"], styles["Heading3"]))
        story.append(Paragraph("Database", label_style))
        story.append(Paragraph(e["database"], value_style))
        story.append(Paragraph("Search String", label_style))
        story.append(Paragraph(e["search_string"], value_style))
        story.append(Paragraph("Sources Found", label_style))
        story.append(Paragraph(e["sources_found"] or "None noted", value_style))
        story.append(Paragraph("Relevance Note", label_style))
        story.append(Paragraph(e["relevance_note"] or "—", value_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#eeeeee")))
        story.append(Spacer(1, 12))
    doc.build(story)
    buffer.seek(0)
    return buffer

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Legal Research Audit Trail",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Styles ────────────────────────────────────────────────────────────────────
#
# Same palette pattern as the attorney lookup app:
#   #141414  page background
#   #1d1d1d  sidebar / card background
#   #252525  card hover / input background
#   #333333  borders
#   #4a4a4a  muted borders
#   #707070  muted text
#   #b0b0b0  body text
#   #e8e8e8  primary text
#   #f5f5f5  headings

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Source+Serif+4:ital,opsz,wght@0,8..60,300;0,8..60,400;1,8..60,300&display=swap');

html, body, [class*="css"] {
    font-family: 'Source Serif 4', Georgia, serif;
    color: #b0b0b0;
}

.stApp {
    background-color: #141414;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: #1d1d1d;
    border-right: 1px solid #333333;
}
[data-testid="stSidebar"] [data-testid="stTextInput"] input {
    border: 1px solid #333333 !important;
    border-radius: 2px;
    background: #252525 !important;
    color: #e8e8e8 !important;
    font-family: 'Source Serif 4', serif;
    font-size: 0.95rem;
}
[data-testid="stSidebar"] [data-testid="stTextInput"] input:focus {
    border-color: #b0b0b0 !important;
    box-shadow: none !important;
}

/* ── Inputs (main area) ── */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
    border: 1px solid #333333 !important;
    border-radius: 2px !important;
    background: #1d1d1d !important;
    color: #e8e8e8 !important;
    font-family: 'Source Serif 4', serif !important;
    font-size: 0.92rem !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: #b0b0b0 !important;
    box-shadow: none !important;
}

/* ── Selectbox ── */
[data-testid="stSelectbox"] > div > div {
    border: 1px solid #333333 !important;
    border-radius: 2px !important;
    background: #1d1d1d !important;
    color: #e8e8e8 !important;
}

/* ── Buttons ── */
[data-testid="stButton"] button {
    background-color: #1d1d1d !important;
    color: #e8e8e8 !important;
    border: 1px solid #4a4a4a !important;
    border-radius: 2px !important;
    font-family: 'Source Serif 4', serif !important;
    font-size: 0.88rem !important;
    letter-spacing: 0.03em !important;
}
[data-testid="stButton"] button:hover {
    border-color: #b0b0b0 !important;
    background-color: #252525 !important;
}

/* ── Download button ── */
[data-testid="stDownloadButton"] button {
    background-color: #1d1d1d !important;
    color: #e8e8e8 !important;
    border: 1px solid #4a4a4a !important;
    border-radius: 2px !important;
    font-family: 'Source Serif 4', serif !important;
    font-size: 0.88rem !important;
}
[data-testid="stDownloadButton"] button:hover {
    border-color: #b0b0b0 !important;
    background-color: #252525 !important;
}

/* ── Checkbox ── */
[data-testid="stCheckbox"] label p {
    color: #b0b0b0 !important;
    font-size: 0.88rem !important;
}

/* ── Alert / info ── */
[data-testid="stAlert"] {
    background-color: #1d1d1d !important;
    border-color: #333333 !important;
    color: #b0b0b0 !important;
}

hr { border-color: #333333; }

/* ── Landing ── */
.landing {
    max-width: 580px;
    margin: 4rem auto 3rem;
    text-align: center;
}
.landing h1 {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 2.5rem;
    font-weight: 700;
    color: #f5f5f5;
    line-height: 1.15;
    margin-bottom: 1rem;
}
.landing .rule {
    width: 36px;
    height: 1px;
    background: #4a4a4a;
    margin: 1.2rem auto;
}
.landing p {
    font-size: 0.95rem;
    color: #707070;
    line-height: 1.75;
    margin-bottom: 0.5rem;
    font-weight: 300;
}
.landing .pills {
    display: flex;
    justify-content: center;
    gap: 0.5rem;
    flex-wrap: wrap;
    margin-top: 1.4rem;
}
.landing .pill {
    font-size: 0.72rem;
    font-weight: 400;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    color: #707070;
    border: 1px solid #333333;
    padding: 0.25rem 0.8rem;
    border-radius: 100px;
}

/* ── Section label ── */
.section-label {
    font-size: 0.68rem;
    font-weight: 400;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #4a4a4a;
    border-bottom: 1px solid #333333;
    padding-bottom: 0.5rem;
    margin-bottom: 1.2rem;
    margin-top: 0.5rem;
}

/* ── Session created banner ── */
.created-banner {
    background: #1d1d1d;
    border: 1px solid #333333;
    border-left: 3px solid #e8e8e8;
    border-radius: 2px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 2rem;
}
.created-banner .cb-check {
    font-size: 0.72rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #707070;
    margin-bottom: 0.5rem;
}
.created-banner .cb-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.4rem;
    font-weight: 700;
    color: #f5f5f5;
    margin-bottom: 0.4rem;
}
.created-banner .cb-meta {
    font-size: 0.85rem;
    color: #707070;
    line-height: 1.6;
}

/* ── Session header ── */
.session-header {
    padding-bottom: 1.2rem;
    margin-bottom: 2rem;
    border-bottom: 1px solid #333333;
}
.session-header .sh-matter {
    font-family: 'Playfair Display', serif;
    font-size: 1.9rem;
    font-weight: 700;
    color: #f5f5f5;
    margin-bottom: 0.3rem;
    line-height: 1.2;
}
.session-header .sh-question {
    font-size: 0.9rem;
    color: #707070;
    font-style: italic;
    margin-bottom: 0.2rem;
}
.session-header .sh-byline {
    font-size: 0.78rem;
    color: #4a4a4a;
}

/* ── Entry card ── */
.entry-card {
    background: #1d1d1d;
    border: 1px solid #333333;
    border-left: 3px solid #4a4a4a;
    border-radius: 2px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.6rem;
    transition: border-left-color 0.15s ease, background 0.15s ease;
}
.entry-card:hover {
    border-left-color: #e8e8e8;
    background: #252525;
}
.entry-ts {
    font-size: 0.72rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #4a4a4a;
    margin-bottom: 0.4rem;
}
.entry-search {
    font-family: 'Playfair Display', serif;
    font-size: 1.05rem;
    font-weight: 700;
    color: #f5f5f5;
    margin-bottom: 0.35rem;
}
.entry-meta {
    font-size: 0.85rem;
    color: #b0b0b0;
    line-height: 1.65;
}
.entry-label {
    font-style: italic;
    color: #707070;
    margin-right: 0.3rem;
}

/* ── Empty state ── */
.empty-state {
    text-align: center;
    padding: 2.5rem 1rem;
    border: 1px dashed #333333;
    border-radius: 2px;
    color: #4a4a4a;
    font-size: 0.88rem;
    font-style: italic;
    margin-top: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

# ── Data ──────────────────────────────────────────────────────────────────────

sessions = load_sessions()
session_names = list(sessions.keys())

# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### Sessions")
    st.markdown("---")
    selected = st.selectbox("Load a session",
                            ["— New session —"] + session_names,
                            label_visibility="visible")
    if selected != "— New session —":
        st.markdown("---")
        if st.button("Delete this session", use_container_width=True):
            del sessions[selected]
            save_sessions(sessions)
            st.rerun()

# ── New session ───────────────────────────────────────────────────────────────

if selected == "— New session —":

    st.markdown("""
    <div class="landing">
        <h1>Legal Research<br>Audit Trail</h1>
        <div class="rule"></div>
        <p>A structured log for every search you run —
        what you searched, where, what you found, and why it mattered.</p>
        <p>Each session ties to a matter or research question
        and exports as a formatted PDF memo.</p>
        <div class="pills">
            <span class="pill">Track search strings</span>
            <span class="pill">Log sources found</span>
            <span class="pill">Note relevance</span>
            <span class="pill">Export to PDF</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-label">Start a new session</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        matter     = st.text_input("Matter / Case name",
                                   placeholder="e.g. Smith v. Jones (2024)")
        researcher = st.text_input("Researcher name", placeholder="Your name")
    with col2:
        question = st.text_area("Research question", height=114,
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
            st.warning("Please fill in all three fields.")

# ── Active session ────────────────────────────────────────────────────────────

else:
    session = sessions[selected]

    # Created banner — shown once right after creation
    if st.session_state.get("just_created") == selected:
        q = session["research_question"]
        q_preview = q[:110] + "…" if len(q) > 110 else q
        st.markdown(
            '<div class="created-banner">'
            '<div class="cb-check">&#10003; &nbsp;Session created</div>'
            '<div class="cb-title">' + session["matter_name"] + '</div>'
            '<div class="cb-meta">'
            + q_preview + '<br>'
            + session["researcher_name"] + ' &nbsp;&middot;&nbsp; ' + session["created"] +
            '</div></div>',
            unsafe_allow_html=True
        )
        del st.session_state["just_created"]

    # Session header
    st.markdown(
        '<div class="session-header">'
        '<div class="sh-matter">' + session["matter_name"] + '</div>'
        '<div class="sh-question">' + session["research_question"] + '</div>'
        '<div class="sh-byline">'
        + session["researcher_name"] + ' &nbsp;&middot;&nbsp; Started ' + session["created"] +
        '</div></div>',
        unsafe_allow_html=True
    )

    # Log a search
    st.markdown('<div class="section-label">Log a search</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        search_string = st.text_input("Search string",
                                      placeholder='e.g. "non-compete" /s enforceable /p Ohio')
        database      = st.selectbox("Database", DATABASES)
    with col2:
        sources_found  = st.text_area("Sources / results noted", height=100,
                                      placeholder="Case names, citations, anything worth noting...")
        relevance_note = st.text_area("Relevance note", height=100,
                                      placeholder="Why kept, why ruled out, what to follow up...")

    st.markdown("")
    if st.button("Add Entry"):
        if search_string:
            session["entries"].append({
                "timestamp":      datetime.now().strftime("%Y-%m-%d %H:%M"),
                "search_string":  search_string,
                "database":       database,
                "sources_found":  sources_found,
                "relevance_note": relevance_note,
            })
            save_sessions(sessions)
            st.toast("Entry logged", icon="✓")
            st.rerun()
        else:
            st.warning("Enter a search string before adding an entry.")

    # Search log
    st.markdown("")
    n = len(session["entries"])
    label = str(n) + " entr" + ("ies" if n != 1 else "y")
    st.markdown('<div class="section-label">Search log &mdash; ' + label + '</div>',
                unsafe_allow_html=True)

    if not session["entries"]:
        st.markdown(
            '<div class="empty-state">No searches logged yet. Add your first entry above.</div>',
            unsafe_allow_html=True
        )
    else:
        for e in reversed(session["entries"]):
            src  = e["sources_found"]  or "None noted"
            note = e["relevance_note"] or "—"
            st.markdown(
                '<div class="entry-card">'
                '<div class="entry-ts">' + e["timestamp"] + ' &nbsp;&middot;&nbsp; ' + e["database"] + '</div>'
                '<div class="entry-search">' + e["search_string"] + '</div>'
                '<div class="entry-meta">'
                '<span class="entry-label">Sources</span>' + src + '<br>'
                '<span class="entry-label">Note</span>' + note +
                '</div></div>',
                unsafe_allow_html=True
            )

        # Export
        st.markdown("")
        st.markdown('<div class="section-label">Export</div>', unsafe_allow_html=True)
        pdf = generate_pdf(session)
        fname = session["matter_name"].replace(" ", "_") + "_research_memo.pdf"
        st.download_button(
            "Download Research Memo (PDF)",
            data=pdf,
            file_name=fname,
            mime="application/pdf",
        )
