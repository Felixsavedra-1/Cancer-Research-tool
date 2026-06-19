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

# Starting points with good hotspot coverage; several (FLT3, IDH2, KIT) are
# drivers in leukemias / blood cancers.
EXAMPLE_GENES = ["TP53", "KRAS", "BRAF", "KIT", "FLT3", "IDH2", "PTEN", "EGFR"]


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

# Parse and validate the requested mutations against the real sequence.
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
