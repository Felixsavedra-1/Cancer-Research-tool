"""Cancer Protein Explorer — Streamlit app.

Pick a cancer-relevant gene, fetch its real AlphaFold structure, and see in 3D
where cancer mutations land on the protein. Research/education use only.

Run with:  streamlit run app.py
"""

from __future__ import annotations

import pandas as pd
import requests
import streamlit as st
import streamlit.components.v1 as components

from cancer_tool import __version__, mutations as mut, structures, uniprot, viewer

EXAMPLE_GENES = ["TP53", "KRAS", "BRAF", "KIT", "FLT3", "IDH2", "PTEN", "EGFR"]

_BRAND_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Spectral:ital,wght@0,300;0,400;0,500;1,300;1,400&family=Hanken+Grotesk:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

:root {
  --black: #0A0A0B; --black-2: #111113; --panel: #141417;
  --line: #26262B; --line-soft: #19191D;
  --bone: #E8E3D6; --grey: #8C8C93; --grey-dim: #5C5C63;
  --gold: #C6A15B; --gold-dim: #6e5c34; --crimson: #B23A3A;
  --display: 'Spectral', Georgia, serif;
  --body: 'Hanken Grotesk', system-ui, -apple-system, sans-serif;
  --mono: 'IBM Plex Mono', ui-monospace, monospace;
}

/* Background grid overlay */
.stApp::before {
  content: ""; position: fixed; inset: 0; z-index: 0; pointer-events: none;
  background-image:
    linear-gradient(var(--line-soft) 1px, transparent 1px),
    linear-gradient(90deg, var(--line-soft) 1px, transparent 1px);
  background-size: 64px 64px; opacity: .45;
  -webkit-mask-image: radial-gradient(120% 120% at 70% 0%, #000 0%, transparent 75%);
          mask-image: radial-gradient(120% 120% at 70% 0%, #000 0%, transparent 75%);
}

html, body, .stApp, [data-testid="stSidebar"] { font-family: var(--body); }
h1, h2, h3 {
  font-family: var(--display) !important; font-weight: 300 !important;
  letter-spacing: -.012em;
}
[data-testid="stCaptionContainer"], .stCaption { font-family: var(--mono); color: var(--grey); }

/* Brand masthead */
.vr-masthead { margin: 0 0 4px; }
.vr-designation {
  font-family: var(--mono); font-size: .72rem; letter-spacing: .18em;
  text-transform: uppercase; color: var(--gold);
}
.vr-mark {
  font-family: var(--mono); font-size: .78rem; letter-spacing: .14em;
  color: var(--grey); float: right;
}
.vr-mark a { color: var(--grey); text-decoration: none; }
.vr-mark a:hover { color: var(--bone); }

/* Buttons */
.stButton button, .stDownloadButton button {
  background: var(--gold); color: var(--black);
  border: 1px solid var(--gold); border-radius: 2px;
  font-family: var(--mono); font-weight: 500; font-size: .8rem;
  letter-spacing: .12em; text-transform: uppercase;
}
.stButton button:hover, .stDownloadButton button:hover {
  background: var(--bone); border-color: var(--bone); color: var(--black);
}

/* Inputs */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-baseweb="select"] > div {
  background: var(--black-2) !important; color: var(--bone) !important;
  border: 1px solid var(--line) !important; border-radius: 2px !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus,
[data-baseweb="select"] > div:focus-within {
  border-color: var(--gold) !important; box-shadow: none !important;
}

/* Alerts / disclaimer */
[data-testid="stAlert"] {
  background: rgba(178,58,58,.07) !important;
  border: 1px solid var(--crimson) !important; border-radius: 2px !important;
  color: #d98d8d !important;
}

/* Tables & links */
[data-testid="stTable"] th, [data-testid="stDataFrame"] th {
  font-family: var(--mono); text-transform: uppercase; letter-spacing: .12em;
  font-size: .66rem; color: var(--grey);
}
a, a:visited { color: var(--gold); }
</style>
"""


def inject_brand_css() -> None:
    """Apply the Vedra Research brand on top of the native dark theme.

    Base colours live in ``.streamlit/config.toml``; this adds the brand fonts and
    component styling, targeting stable ``data-testid`` hooks rather than
    Streamlit's generated class names.
    """
    st.markdown(_BRAND_CSS, unsafe_allow_html=True)
    st.markdown(
        '<div class="vr-masthead">'
        '<span class="vr-designation">VR-05</span>'
        '<span class="vr-mark">'
        '<a href="https://vedraresearch.github.io/Vedra-Research/">Vedra Research ↗</a>'
        "</span></div>",
        unsafe_allow_html=True,
    )


@st.cache_resource
def http_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({"User-Agent": f"cancer-protein-explorer/{__version__}"})
    return session


@st.cache_data(show_spinner=False)
def load_protein(gene: str):
    return uniprot.get_protein(gene, session=http_session())


@st.cache_data(show_spinner=False)
def load_structure(accession: str) -> str:
    return structures.fetch_alphafold_pdb(accession, session=http_session())


@st.cache_data(show_spinner=False)
def load_hotspots(gene: str):
    return mut.fetch_hotspots(gene, session=http_session())


st.set_page_config(page_title="Cancer Protein Explorer", layout="wide")
inject_brand_css()

st.title("🧬 Cancer Protein Explorer")
st.caption(
    "Visualize cancer-relevant proteins and the mutations that affect them, "
    "using real AlphaFold structures and curated cancer-genomics data."
)
st.warning(
    "**Research and education use only.** This is not a medical device and must "
    "not be used for diagnosis or treatment decisions.",
    icon="⚠️",
)

with st.sidebar:
    st.header("Protein")
    gene = st.selectbox(
        "Gene symbol",
        options=EXAMPLE_GENES,
        index=0,
        accept_new_options=True,
        help="Pick an example or type any human gene symbol (e.g. PTEN).",
    )
    st.header("Mutations")
    mutation_text = st.text_area(
        "Mutations to highlight",
        value="R175H",
        help="One-letter form like R175H. Separate multiple with commas or spaces.",
    )
    color_by_confidence = st.toggle(
        "Colour by AlphaFold confidence (pLDDT)",
        value=True,
        help="Red ≈ low-confidence model, blue ≈ high. Off = rainbow by position.",
    )

if not gene:
    st.info("Choose or type a gene symbol in the sidebar to begin.")
    st.stop()

gene = gene.strip().upper()

with st.spinner(f"Looking up {gene}…"):
    try:
        protein = load_protein(gene)
    except requests.RequestException as exc:
        st.error(f"Could not reach UniProt: {exc}")
        st.stop()

if not protein:
    st.error(f"No reviewed human protein found for gene **{gene}**. Check the symbol.")
    st.stop()

with st.spinner("Fetching AlphaFold structure…"):
    try:
        pdb_text = load_structure(protein["accession"])
    except requests.RequestException as exc:
        st.error(
            f"No AlphaFold structure available for {protein['accession']} ({exc})."
        )
        st.stop()

parsed, unparseable = mut.parse_mutations(mutation_text)
highlights, invalid = [], []
for mutation in parsed:
    ok, message = mut.validate_mutation(mutation, protein["sequence"])
    if ok:
        highlights.append({"position": mutation["position"], "label": mutation["label"]})
    else:
        invalid.append(f"{mutation['label']}: {message}")

viewer_col, info_col = st.columns([3, 2], gap="large")

with viewer_col:
    st.subheader(f"{protein['name']} ({gene})")
    html = viewer.render_structure(
        pdb_text,
        highlights=highlights,
        color_by_confidence=color_by_confidence,
    )
    components.html(html, height=620, scrolling=False)
    if color_by_confidence:
        st.caption("Cartoon coloured by pLDDT: 🔴 low confidence → 🔵 high confidence.")

with info_col:
    st.subheader("Protein")
    st.markdown(
        f"- **Gene:** {gene}\n"
        f"- **UniProt:** [{protein['accession']}]"
        f"(https://www.uniprot.org/uniprotkb/{protein['accession']})\n"
        f"- **Length:** {protein['length']} residues\n"
        f"- **Structure:** [AlphaFold DB]"
        f"(https://alphafold.ebi.ac.uk/entry/{protein['accession']})"
    )

    if unparseable:
        st.warning("Could not parse: " + ", ".join(unparseable))
    if invalid:
        for problem in invalid:
            st.error(problem)
    if highlights:
        st.success("Highlighted: " + ", ".join(h["label"] for h in highlights))

    st.subheader("Known cancer hotspots")
    with st.spinner("Loading hotspots…"):
        try:
            hotspots = load_hotspots(gene)
        except requests.RequestException:
            hotspots = []
    if hotspots:
        df = pd.DataFrame(hotspots)[["residue", "count"]]
        df.columns = ["Residue", "Tumours"]
        st.dataframe(df, hide_index=True, use_container_width=True, height=260)
        st.caption(
            "Recurrent mutation sites from "
            "[cancerhotspots.org](https://www.cancerhotspots.org). "
            "Copy a residue (e.g. R175) into the sidebar to highlight it."
        )
    else:
        st.caption("No hotspot record found for this gene.")
