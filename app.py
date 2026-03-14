import streamlit as st
import json
import os
import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib import colors

SESSION_FILE = "sessions.json"
DATABASES = ["Westlaw", "HeinOnline", "Google Scholar", "Lexis+", "Bloomberg Law", "Fastcase", "Other"]

# ── Session persistence ──────────────────────────────────────────────────────
def load_sessions():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE) as f:
            return json.load(f)
    return {}

def save_sessions(sessions):
    with open(SESSION_FILE, "w") as f:
        json.dump(sessions, f, indent=2)

# ── PDF generation ───────────────────────────────────────────────────────────
def generate_pdf(session):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=inch, leftMargin=inch,
                            topMargin=inch, bottomMargin=inch)
    styles = getSampleStyleSheet()
    story = []

    # Title
    story.append(Paragraph("Legal Research Audit Trail", styles["Title"]))
    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
    story.append(Spacer(1, 12))

    # Session metadata
    story.append(Paragraph(f"<b>Matter:</b> {session['matter_name']}", styles["Normal"]))
    story.append(Paragraph(f"<b>Research Question:</b> {session['research_question']}", styles["Normal"]))
    story.append(Paragraph(f"<b>Researcher:</b> {session['researcher_name']}", styles["Normal"]))
    story.append(Paragraph(f"<b>Session Started:</b> {session['created']}", styles["Normal"]))
    story.append(Paragraph(f"<b>Exported:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles["Normal"]))
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey))
    story.append(Spacer(1, 20))

    # Entries
    story.append(Paragraph(f"Search Log — {len(session['entries'])} entries", styles["Heading2"]))
    story.append(Spacer(1, 12))

    for i, entry in enumerate(session["entries"], 1):
        story.append(Paragraph(f"<b>Entry {i} — {entry['timestamp']}</b>", styles["Heading3"]))
        story.append(Paragraph(f"<b>Database:</b> {entry['database']}", styles["Normal"]))
        story.append(Paragraph(f"<b>Search String:</b> {entry['search_string']}", styles["Normal"]))
        story.append(Paragraph(f"<b>Sources Found:</b> {entry['sources_found'] or 'None noted'}", styles["Normal"]))
        story.append(Paragraph(f"<b>Relevance Note:</b> {entry['relevance_note'] or 'None'}", styles["Normal"]))
        story.append(Spacer(1, 8))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey))
        story.append(Spacer(1, 12))

    doc.build(story)
    buffer.seek(0)
    return buffer

# ── UI ───────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Legal Research Audit Trail", layout="wide")
st.title("Legal Research Audit Trail")

sessions = load_sessions()

# ── Sidebar: session management ──────────────────────────────────────────────
st.sidebar.header("Research Sessions")

session_names = list(sessions.keys())
selected = st.sidebar.selectbox("Load existing session", ["-- New Session --"] + session_names)

if selected == "-- New Session --":
    st.sidebar.subheader("Create New Session")
    matter = st.sidebar.text_input("Matter / Case Name")
    question = st.sidebar.text_area("Research Question")
    researcher = st.sidebar.text_input("Researcher Name")
    if st.sidebar.button("Create Session") and matter and question and researcher:
        sessions[matter] = {
            "matter_name": matter,
            "research_question": question,
            "researcher_name": researcher,
            "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "entries": []
        }
        save_sessions(sessions)
        st.rerun()

else:
    session = sessions[selected]

    # ── Main area: log a search ──────────────────────────────────────────────
    st.subheader(f"Matter: {session['matter_name']}")
    st.caption(f"Research question: {session['research_question']}")
    st.caption(f"Researcher: {session['researcher_name']} · Started: {session['created']}")
    # ── Delete session ───────────────────────────────────────────────────────
    with st.sidebar:
        st.divider()
        if st.button("🗑️ Delete this session", type="secondary"):
            del sessions[selected]
            save_sessions(sessions)
            st.rerun()


    st.divider()
    st.subheader("Log a Search")

    col1, col2 = st.columns(2)
    with col1:
        search_string = st.text_input("Search string")
        database = st.selectbox("Database", DATABASES)
    with col2:
        sources_found = st.text_area("Sources / results noted", height=100)
        relevance_note = st.text_area("Relevance note", height=100,
                                      placeholder="Why kept or ruled out...")

    if st.button("Add Entry") and search_string:
        session["entries"].append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "search_string": search_string,
            "database": database,
            "sources_found": sources_found,
            "relevance_note": relevance_note
        })
        save_sessions(sessions)
        st.success("Entry logged.")
        st.rerun()

    # ── Running log ──────────────────────────────────────────────────────────
    if session["entries"]:
        st.divider()
        st.subheader(f"Search Log ({len(session['entries'])} entries)")
        for i, entry in enumerate(reversed(session["entries"]), 1):
            with st.expander(f"{entry['timestamp']} · {entry['database']} · {entry['search_string'][:60]}"):
                st.markdown(f"**Search string:** {entry['search_string']}")
                st.markdown(f"**Database:** {entry['database']}")
                st.markdown(f"**Sources found:** {entry['sources_found']}")
                st.markdown(f"**Relevance note:** {entry['relevance_note']}")

        # ── PDF Export ───────────────────────────────────────────────────────
        st.divider()
        st.subheader("Export")
        pdf_buffer = generate_pdf(session)
        st.download_button(
            label="⬇️ Download Research Memo (PDF)",
            data=pdf_buffer,
            file_name=f"{session['matter_name'].replace(' ', '_')}_research_memo.pdf",
            mime="application/pdf"
        )
    else:
        st.info("No entries yet. Log your first search above.")