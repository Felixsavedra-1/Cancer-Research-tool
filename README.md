# 🧬 Cancer Protein Explorer

An interactive tool for **visualizing cancer-relevant proteins and the mutations
that affect them in 3D** — built on real, public scientific data.

Type a gene (e.g. `TP53`, `JAK2`, `NPM1`), and the tool fetches the protein's
real **AlphaFold** structure, renders it in interactive 3D, colours it by model
confidence, highlights the mutations you care about, and lists the residues most
recurrently mutated in cancer.

> ⚠️ **Research and education use only.** This is not a medical device. It must
> not be used for diagnosis or treatment decisions.

## Why this runs on a laptop

Predicting protein structures with AlphaFold needs big GPUs. But DeepMind already
ran AlphaFold on ~200 million proteins and made the results free. This tool
**downloads finished structures** instead of computing them, so all the heavy
work is done by hosted services and the browser — no GPU required.

## Data sources (all free, public)

| Data | Source |
|------|--------|
| Gene → protein + sequence | [UniProt](https://www.uniprot.org) |
| 3D structures (with pLDDT confidence) | [AlphaFold DB](https://alphafold.ebi.ac.uk) |
| Recurrent cancer mutation hotspots | [cancerhotspots.org](https://www.cancerhotspots.org) |

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

Then in the sidebar: pick or type a gene, enter mutations like `R175H` (separate
several with commas), and toggle confidence colouring.

## Test

```bash
pytest
```

## Project layout

```
app.py                 Streamlit UI — wires the modules together
cancer_tool/
  uniprot.py           gene symbol -> UniProt accession + sequence
  structures.py        fetch AlphaFold structure (PDB text)
  mutations.py         parse/validate mutations + fetch hotspots
  viewer.py            build the 3D py3Dmol view (confidence colour + highlights)
tests/                 unit tests for mutation parsing
```

## Roadmap

- Pathogenicity overlay per residue (AlphaMissense / ClinVar)
- Cohort frequencies & cancer-type filter via cBioPortal
- Drug/target context via Open Targets
- Local docking (AutoDock Vina) and light molecular dynamics (OpenMM)
