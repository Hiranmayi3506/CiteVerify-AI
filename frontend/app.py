import streamlit as st
import requests
import plotly.express as px
import pandas as pd
import json
import base64
from datetime import datetime, timezone
from urllib.parse import quote

# ============================================================
# CITEVERIFY AI 2.0 | Scientific Research Intelligence
# Frontend contract:
# POST /verify with multipart field "file"
# Expected JSON: {"claims":[...], "citations":[...], "verdicts":[...]}
# Each claim/verdict may include claim, verdict, confidence, evidence,
# paper_title, doi, page, reason, source_url.
# ============================================================

st.set_page_config(
    page_title="CiteVerify AI 2.0 | Research Intelligence",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------- STATE -----------------------------
defaults = {
    "live_results": None,
    "live_filename": None,
    "last_run_at": None,
    "workspace": "Overview",
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ------------------------- THEME -----------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
:root { color-scheme: dark; }
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp {
  background:
    radial-gradient(ellipse at 12% 0%, rgba(83,76,190,.20), transparent 34%),
    radial-gradient(ellipse at 92% 12%, rgba(30,144,180,.13), transparent 32%),
    #080d18;
  color: #edf2ff;
}
.block-container { max-width: 1450px; padding-top: 1.6rem; padding-bottom: 3rem; }
[data-testid="stSidebar"] {
  background: linear-gradient(180deg,#101a2d,#0b1220);
  border-right: 1px solid #24334d;
}
[data-testid="stSidebar"] .block-container { padding-top: 1.5rem; }
h1,h2,h3,h4 { font-family:'Space Grotesk',sans-serif !important; letter-spacing:-.5px; }
.hero {
  padding: 34px 38px; border-radius: 24px;
  background: linear-gradient(115deg,rgba(36,43,88,.96),rgba(16,48,72,.96) 60%,rgba(17,32,59,.96));
  border: 1px solid #46558a; box-shadow: 0 18px 55px rgba(0,0,0,.25);
  animation: rise .65s ease both;
}
@keyframes rise { from {opacity:0;transform:translateY(10px)} to {opacity:1;transform:translateY(0)} }
.eyebrow { color:#b5b1ff; font-size:11px; font-weight:700; letter-spacing:2.6px; text-transform:uppercase; }
.hero-title { font:700 clamp(32px,4vw,52px)/1.08 'Space Grotesk',sans-serif; color:#fff; margin:14px 0; }
.grad { background:linear-gradient(90deg,#c4b5fd,#67d8ef);-webkit-background-clip:text;-webkit-text-fill-color:transparent; }
.hero-copy { color:#c0cce2; max-width:780px; line-height:1.75; font-size:15px; }
.section-kicker { color:#8e9fbd; font-size:11px; font-weight:700; letter-spacing:2px; text-transform:uppercase; margin:26px 0 8px; }
.section-title { color:#f4f6ff; font:600 24px 'Space Grotesk',sans-serif; margin:0 0 5px; }
.muted { color:#9eacc5; font-size:13px; }
.metric {
  background:linear-gradient(145deg,#17243b,#101a2c); border:1px solid #2d405e;
  border-radius:17px; padding:19px 20px; min-height:118px;
  transition:all .2s ease;
}
.metric:hover { border-color:#7777dc; transform:translateY(-2px); }
.metric-label { color:#9cacc8; font-size:10px; letter-spacing:1.25px; font-weight:700; }
.metric-number { color:#fff; font:700 34px 'Space Grotesk',sans-serif; margin-top:9px; }
.metric-note { color:#8294b4; font-size:11px; margin-top:2px; }
.surface {
  background:rgba(18,29,49,.88); border:1px solid #2b3d5b; border-radius:17px;
  padding:19px 21px; margin-bottom:12px;
}
.claim {
  background:linear-gradient(145deg,#142139,#101a2c); border:1px solid #30435f;
  border-radius:15px; padding:17px 19px; margin:9px 0;
}
.pill {
  display:inline-block; padding:5px 10px; border-radius:99px;
  font-size:10px; font-weight:700; letter-spacing:.6px;
  background:#263552; color:#d5e1fa;
}
.stButton>button {
  background:linear-gradient(100deg,#786cf2,#318bc8); color:white; border:0;
  border-radius:11px; min-height:43px; font-weight:700; transition:.2s;
}
.stButton>button:hover { color:white; transform:translateY(-2px); box-shadow:0 8px 24px #5367c455; }
.stDownloadButton>button { background:#192944; border:1px solid #53698d; color:#edf2ff; border-radius:10px; }
[data-testid="stFileUploader"] { background:#111d31; border:1px dashed #6575b7; border-radius:14px; padding:12px; }
[data-testid="stTabs"] button { color:#b8c7e2; font-weight:600; }
div[data-testid="stExpander"] { border:1px solid #30415e; border-radius:13px; background:#101a2c; }
[data-testid="stMetric"] { background:#142139; border:1px solid #30415e; border-radius:14px; padding:14px; }
hr { border-color:#293b58; }
a { color:#91caff !important; }
.small-footer { color:#7183a3; text-align:center; font-size:11px; padding:22px 0 8px; }
</style>
""", unsafe_allow_html=True)

# ------------------------- DEMO FIXTURES ---------------------
# Explicitly fictional examples; never presented as live analysis.
DEMO = {
    "claims": [
        {
            "claim": "The evaluated machine-learning model improved classification performance on the study dataset.",
            "verdict": "Supported",
            "confidence": 0.91,
            "evidence": "Illustrative passage: The authors report improved classification performance in the evaluated dataset.",
            "paper_title": "Illustrative Model Evaluation Study",
            "doi": "10.example/demo-001",
            "page": 4,
            "reason": "The passage addresses the same outcome and dataset scope. The conclusion should not be generalized beyond the study.",
        },
        {
            "claim": "The method is guaranteed to outperform every existing approach.",
            "verdict": "Unsupported",
            "confidence": 0.96,
            "evidence": "Illustrative passage: The study compares the proposed method with selected baselines only.",
            "paper_title": "Illustrative Benchmarking Study",
            "doi": "10.example/demo-002",
            "page": 7,
            "reason": "A comparison against selected baselines cannot establish superiority over every existing approach.",
        },
        {
            "claim": "Combining multiple data sources may improve predictive performance.",
            "verdict": "Partially supported",
            "confidence": 0.78,
            "evidence": "Illustrative passage: Improvements were observed in some experimental settings, but not consistently across all datasets.",
            "paper_title": "Illustrative Multimodal Study",
            "doi": "10.example/demo-003",
            "page": 9,
            "reason": "The evidence supports a narrower, conditional version of the claim.",
        },
        {
            "claim": "The findings apply to all real-world deployment environments.",
            "verdict": "Needs human review",
            "confidence": 0.62,
            "evidence": "Illustrative passage: Evaluation was conducted under a limited set of experimental conditions.",
            "paper_title": "Illustrative External Validation Study",
            "doi": "10.example/demo-004",
            "page": 11,
            "reason": "The source does not provide enough external validation to support this broad statement.",
        },
    ],
    "citations": [
        {"title": "Illustrative Model Evaluation Study", "doi": "10.example/demo-001", "status": "Demo reference"},
        {"title": "Illustrative Benchmarking Study", "doi": "10.example/demo-002", "status": "Demo reference"},
        {"title": "Illustrative Multimodal Study", "doi": "10.example/demo-003", "status": "Demo reference"},
        {"title": "Illustrative External Validation Study", "doi": "10.example/demo-004", "status": "Demo reference"},
    ],
}

# ------------------------- UTILITIES ------------------------
def section(label, title, subtitle=None):
    st.markdown(f'<div class="section-kicker">{label}</div><div class="section-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="muted">{subtitle}</div>', unsafe_allow_html=True)

def get_records(payload):
    if not isinstance(payload, dict):
        return [], []
    claims = payload.get("claims") or []
    verdicts = payload.get("verdicts") or []
    records = verdicts if verdicts else claims
    records = [x for x in records if isinstance(x, dict)]
    citations = payload.get("citations") or []
    return records, citations

def verdict_of(row):
    return str(row.get("verdict") or row.get("status") or "Needs human review").strip()

def confidence_of(row):
    try:
        n = float(row.get("confidence"))
        if 1 < n <= 100: n /= 100
        return n if 0 <= n <= 1 else None
    except (TypeError, ValueError):
        return None

def counts_for(records):
    labels = [verdict_of(x).lower() for x in records]
    return {
        "supported": sum(x == "supported" for x in labels),
        "partial": sum(x in ("partially supported", "partially_supported", "partial") for x in labels),
        "unsupported": sum(x == "unsupported" for x in labels),
        "review": sum(x not in ("supported", "partially supported", "partially_supported", "partial", "unsupported") for x in labels),
    }

def status_color(v):
    v = v.lower()
    if v == "supported": return "success"
    if v == "unsupported": return "error"
    if "partial" in v: return "warning"
    return "info"

def pdf_embed(upload):
    encoded = base64.b64encode(upload.getvalue()).decode("utf-8")
    st.markdown(
        f'<iframe src="data:application/pdf;base64,{encoded}" width="100%" height="650" '
        'style="border:1px solid #30415e;border-radius:12px;background:white;"></iframe>',
        unsafe_allow_html=True,
    )

# ------------------------- SIDEBAR ---------------------------
with st.sidebar:
    st.markdown("## 🔬 CiteVerify **AI**")
    st.caption("RESEARCH INTELLIGENCE · 2.0")
    st.markdown("---")
    page = st.radio(
        "WORKSPACE",
        ["Overview", "Document analysis", "Claim explorer", "Citation library", "Reports"],
        key="workspace",
        label_visibility="visible",
    )
    st.markdown("---")
    st.markdown("**SYSTEM STATUS**")
    st.markdown('<span class="pill">● FRONTEND READY</span>', unsafe_allow_html=True)
    st.caption("Backend status is confirmed only when a request succeeds.")
    api_url = st.text_input("API endpoint", "http://127.0.0.1:8000/verify", key="api_url")
    health_url = st.text_input("Health endpoint", "http://127.0.0.1:8000/health", key="health_url")
    if st.button("Check backend health", use_container_width=True):
        try:
            r = requests.get(health_url, timeout=5)
            r.raise_for_status()
            st.success("Backend responded: " + str(r.json().get("status", "OK")))
        except Exception as exc:
            st.error(f"Backend unavailable: {exc}")
    st.markdown("---")
    st.caption("AI-assisted analysis · Human review required")

# ------------------------- TOP HERO --------------------------
st.markdown("""
<div class="hero">
  <div class="eyebrow">CITEVERIFY AI / SCIENTIFIC RESEARCH INTELLIGENCE</div>
  <div class="hero-title">Trust the evidence.<br><span class="grad">Verify every claim.</span></div>
  <div class="hero-copy">
    Go beyond reference matching. Inspect scientific statements, trace them to source evidence,
    identify overclaims and understand where the literature does — or does not — support a conclusion.
  </div>
</div>
""", unsafe_allow_html=True)

# ------------------------- WORKSPACE DATA --------------------
demo_mode = st.toggle("Explore with clearly labelled demo data", value=(st.session_state.live_results is None))
if demo_mode:
    payload = DEMO
    filename = "Illustrative demo research paper"
    st.info("DEMO MODE · All claims, sources, DOIs, evidence passages and scores are fictional interface examples.")
else:
    payload = st.session_state.live_results
    filename = st.session_state.live_filename

records, citations = get_records(payload) if payload else ([], [])
counts = counts_for(records)
total = len(records)

# ------------------------- PAGE: OVERVIEW --------------------
if page == "Overview":
    section("01 / command centre", "Research overview", "A transparent snapshot of claim-level evidence assessment.")
    cols = st.columns(4)
    metrics = [
        ("CLAIMS ASSESSED", total, "Statements returned by the analysis pipeline"),
        ("REFERENCES FOUND", len(citations), "Reference records returned"),
        ("SUPPORTED", counts["supported"], "Evidence supports the statement"),
        ("REQUIRES ATTENTION", counts["unsupported"] + counts["review"], "Unsupported or needs human review"),
    ]
    for col, (label, value, note) in zip(cols, metrics):
        with col:
            st.markdown(f'<div class="metric"><div class="metric-label">{label}</div><div class="metric-number">{value}</div><div class="metric-note">{note}</div></div>', unsafe_allow_html=True)

    st.write("")
    left, right = st.columns([1.12, 0.88])
    with left:
        section("ANALYTICS", "Verification distribution")
        if total:
            chart = pd.DataFrame({
                "Verdict": ["Supported", "Partially supported", "Unsupported", "Needs human review"],
                "Count": [counts["supported"], counts["partial"], counts["unsupported"], counts["review"]],
            })
            chart = chart[chart["Count"] > 0]
            fig = px.pie(chart, names="Verdict", values="Count", hole=.70,
                         color="Verdict", color_discrete_map={
                             "Supported":"#35c99a", "Partially supported":"#f2b95f",
                             "Unsupported":"#f07179", "Needs human review":"#9295ff"})
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font_color="#dce6f8", legend_title_text="",
                margin=dict(t=20,b=10,l=5,r=5), height=320,
                annotations=[dict(text=f"<b>{total}</b><br>claims", x=.5,y=.5,showarrow=False,
                                  font=dict(size=20,color="#ffffff"))])
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No claim results yet. Upload a document in Document analysis.")
    with right:
        section("INTERPRETATION", "Verdict framework")
        st.markdown("""
        <div class="surface">
          <p><span class="pill">SUPPORTED</span></p>
          <div class="muted">Retrieved evidence supports the substance and scope of the claim.</div><hr>
          <p><span class="pill">PARTIALLY SUPPORTED</span></p>
          <div class="muted">Evidence supports only part of the statement, or the claim overstates the source.</div><hr>
          <p><span class="pill">UNSUPPORTED</span></p>
          <div class="muted">The retrieved evidence does not support the statement. This is not automatically proof that it is false.</div><hr>
          <p><span class="pill">NEEDS HUMAN REVIEW</span></p>
          <div class="muted">Evidence is missing, ambiguous, conflicting or insufficient for a reliable decision.</div>
        </div>
        """, unsafe_allow_html=True)

    section("PRIORITY QUEUE", "Claims requiring attention", "Review these statements before relying on the document.")
    attention = [x for x in records if verdict_of(x).lower() != "supported"]
    if not attention:
        st.success("No non-supported claims were returned.")
    for i, row in enumerate(attention[:4], 1):
        with st.expander(f"{i:02d} · {verdict_of(row)} · {str(row.get('claim','Claim unavailable'))[:105]}"):
            st.write(row.get("claim", "Claim unavailable"))
            st.caption(row.get("reason", "No explanation supplied by backend."))

# ------------------------- PAGE: DOCUMENT ANALYSIS ----------
elif page == "Document analysis":
    section("02 / document intelligence", "Analyse a research document", "Upload a PDF and send it to your team's FastAPI verification service.")
    uploaded = st.file_uploader("Select research paper (PDF)", type=["pdf"], key="research_pdf")
    c1, c2 = st.columns([1, 1])
    with c1:
        if uploaded:
            st.markdown('<div class="surface">', unsafe_allow_html=True)
            st.markdown("**DOCUMENT READY**")
            st.write(uploaded.name)
            st.caption(f"{uploaded.size / 1024:.1f} KB · PDF")
            st.markdown("</div>", unsafe_allow_html=True)
            if st.button("Run claim verification", type="primary", use_container_width=True):
                bar = st.progress(0, text="Preparing document...")
                try:
                    bar.progress(20, text="Sending PDF to verification API...")
                    response = requests.post(
                        api_url,
                        files={"file": (uploaded.name, uploaded.getvalue(), "application/pdf")},
                        timeout=240,
                    )
                    bar.progress(80, text="Reading analysis response...")
                    response.raise_for_status()
                    result = response.json()
                    if not isinstance(result, dict):
                        raise ValueError("API response must be a JSON object.")
                    st.session_state.live_results = result
                    st.session_state.live_filename = uploaded.name
                    st.session_state.last_run_at = datetime.now(timezone.utc).isoformat()
                    bar.progress(100, text="Analysis response received.")
                    st.success("Backend response received. Open Claim explorer or Overview.")
                    st.rerun()
                except requests.exceptions.ConnectionError:
                    bar.empty()
                    st.error("Cannot connect. Check the backend is running and the API URL is correct.")
                except requests.exceptions.Timeout:
                    bar.empty()
                    st.error("The request timed out. Try again or check backend logs.")
                except requests.exceptions.HTTPError as exc:
                    bar.empty()
                    st.error(f"Backend returned an HTTP error: {exc}")
                    if getattr(exc.response, "text", None):
                        st.code(exc.response.text[:1500])
                except Exception as exc:
                    bar.empty()
                    st.error(f"Could not process backend response: {exc}")
        else:
            st.markdown('<div class="surface"><b>Waiting for a document</b><p class="muted">Choose a PDF to preview it and submit it for analysis.</p></div>', unsafe_allow_html=True)
    with c2:
        if uploaded:
            st.markdown("**PDF preview**")
            try:
                pdf_embed(uploaded)
            except Exception:
                st.info("The browser could not preview this PDF. The file can still be submitted.")
        else:
            st.markdown("""
            <div class="surface">
              <h3>What happens next?</h3>
              <p class="muted">1. The backend extracts document text.</p>
              <p class="muted">2. Claims and references are identified.</p>
              <p class="muted">3. Evidence is retrieved and compared.</p>
              <p class="muted">4. Claim-level verdicts and explanations are returned.</p>
              <p class="muted">5. You inspect results and export a report.</p>
            </div>
            """, unsafe_allow_html=True)
    if st.session_state.last_run_at:
        st.caption(f"Most recent successful API response: {st.session_state.last_run_at}")

# ------------------------- PAGE: CLAIM EXPLORER --------------
elif page == "Claim explorer":
    section("03 / explainable verification", "Claim explorer", "Inspect each statement, verdict, model score and evidence explanation.")
    if not records:
        st.info("No claim records available. Run an analysis or turn on demo data.")
    else:
        verdict_options = ["All"] + sorted(set(verdict_of(x) for x in records))
        selected = st.selectbox("Filter by verdict", verdict_options)
        filtered = records if selected == "All" else [x for x in records if verdict_of(x) == selected]
        st.caption(f"Showing {len(filtered)} of {len(records)} claims")
        for i, row in enumerate(filtered, 1):
            verdict = verdict_of(row)
            with st.expander(f"CLAIM {i:02d}  ·  {verdict.upper()}", expanded=(i == 1)):
                st.markdown("**Extracted scientific statement**")
                st.write(row.get("claim", "Claim text not supplied by backend."))
                st.markdown(f'<span class="pill">{verdict.upper()}</span>', unsafe_allow_html=True)
                score = confidence_of(row)
                if score is not None:
                    st.write(f"Model confidence indicator: {score:.0%}")
                    st.progress(score)
                    st.caption("A model confidence score is not the probability that a claim is true.")
                st.markdown("**Why this verdict?**")
                st.write(row.get("reason", "No reasoning field returned."))
                st.markdown("**Evidence passage**")
                st.info(row.get("evidence", "No evidence passage returned."))
                a, b, c = st.columns(3)
                a.caption("SOURCE PAPER")
                a.write(row.get("paper_title", "Not supplied"))
                b.caption("PAGE")
                b.write(row.get("page", "Not supplied"))
                c.caption("DOI")
                c.write(row.get("doi", "Not supplied"))
                if row.get("source_url"):
                    st.link_button("Open source", row["source_url"])

# ------------------------- PAGE: CITATIONS -------------------
elif page == "Citation library":
    section("04 / reference integrity", "Citation library", "Review references returned by the backend. DOI existence and metadata should be validated separately.")
    if not citations:
        st.info("No citation records returned. Check the backend response contract.")
    else:
        search = st.text_input("Search title or DOI", placeholder="Enter a paper title or DOI...")
        rows = []
        for c in citations:
            if isinstance(c, dict):
                rows.append({
                    "Title": c.get("title") or c.get("paper_title") or "Untitled reference",
                    "DOI": c.get("doi") or "Not supplied",
                    "Status": c.get("status") or "Not classified",
                    "URL": c.get("url") or c.get("source_url") or "",
                })
            else:
                rows.append({"Title": str(c), "DOI": "Not supplied", "Status": "Not classified", "URL": ""})
        df = pd.DataFrame(rows)
        if search:
            mask = df["Title"].str.contains(search, case=False, na=False) | df["DOI"].str.contains(search, case=False, na=False)
            df = df[mask]
        st.dataframe(df[["Title", "DOI", "Status"]], use_container_width=True, hide_index=True)
        for _, row in df.iterrows():
            with st.expander(str(row["Title"])):
                st.write("DOI:", row["DOI"])
                st.write("Status:", row["Status"])
                if row["DOI"] != "Not supplied" and not str(row["DOI"]).startswith("10.example"):
                    st.markdown(f"[Resolve DOI](https://doi.org/{quote(str(row['DOI']), safe='/')})")
                if row["URL"]:
                    st.link_button("Open source record", row["URL"])

# ------------------------- PAGE: REPORTS ---------------------
elif page == "Reports":
    section("05 / audit and export", "Verification report centre", "Export a traceable snapshot of the current workspace results.")
    if not payload or not records:
        st.info("No report data available yet. Run an analysis or enable demo mode.")
    else:
        report = {
            "product": "CiteVerify AI 2.0",
            "document": filename,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "demo_mode": bool(demo_mode),
            "notice": (
                "Fictional demonstration data. Not actual research verification."
                if demo_mode else
                "AI-assisted output. Verify source passages manually; this report is not a substitute for expert review."
            ),
            "summary": {"claims": len(records), "citations": len(citations), **counts},
            "claims": records,
            "citations": citations,
        }
        st.markdown('<div class="surface"><b>Report contents</b><p class="muted">Document metadata · Claim verdicts · Explanations · Evidence passages · Citation records · Generation timestamp</p></div>', unsafe_allow_html=True)
        st.download_button(
            "⬇ Download structured verification report (JSON)",
            data=json.dumps(report, indent=2, ensure_ascii=False),
            file_name="CiteVerify_AI_2_Research_Report.json",
            mime="application/json",
            use_container_width=True,
        )
        if records:
            export_df = pd.DataFrame([{
                "claim": x.get("claim", ""),
                "verdict": verdict_of(x),
                "confidence": confidence_of(x),
                "reason": x.get("reason", ""),
                "paper_title": x.get("paper_title", ""),
                "doi": x.get("doi", ""),
                "page": x.get("page", ""),
            } for x in records])
            st.download_button(
                "⬇ Download claim summary (CSV)",
                data=export_df.to_csv(index=False).encode("utf-8"),
                file_name="CiteVerify_AI_Claim_Summary.csv",
                mime="text/csv",
                use_container_width=True,
            )
        if demo_mode:
            st.warning("This report contains fictional demo data. Do not submit it as real verification.")

# ------------------------- FOOTER ----------------------------
st.markdown("""
<div class="small-footer">
  <b>CITEVERIFY AI 2.0</b><br>
  Evidence traceability · Transparent reasoning · Human oversight<br>
  An AI-assisted research tool — not an automated authority on scientific truth.
</div>
""", unsafe_allow_html=True)