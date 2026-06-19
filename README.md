# 🧬 Cancer Protein Explorer

<p align="center">
  <img src="docs/demo.gif" alt="Cancer Protein Explorer — interactive 3D protein + mutation viewer" width="800">
</p>

> Visualize cancer-relevant proteins and the mutations that affect them in 3D — built on real, public scientific data.

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white" alt="Python 3.11">
  <img src="https://img.shields.io/badge/Streamlit-app-FF4B4B?logo=streamlit&logoColor=white" alt="Streamlit">
  <img src="https://img.shields.io/badge/AlphaFold-powered-0B3D91" alt="AlphaFold-powered">
  <img src="https://img.shields.io/badge/use-research%20%2F%20education-informational" alt="Research / Education use">
</p>

Type a gene (e.g. `TP53`, `JAK2`, `NPM1`) and the tool fetches the protein's real **AlphaFold** structure, renders it in interactive 3D, and colours it by model confidence. It then highlights the mutations you care about — validated against the real protein sequence — and lists the residues most recurrently mutated in cancer.

## Highlights

- **Real AlphaFold structures, zero GPU.** Pulls finished models from DeepMind's ~200M-protein set instead of predicting locally — all the heavy lifting runs on hosted services, so it works on a laptop.
- **Interactive 3D, confidence-aware.** Renders with `py3Dmol`, coloured by per-residue **pLDDT** (AlphaFold's B-factor column): red ≈ low confidence → blue ≈ high, so you never over-trust an unreliable region.
- **Mutations validated against the real sequence.** Parses `R175H`-style strings and checks each against the canonical UniProt sequence, catching typos and isoform/numbering mismatches before they mislead you.
- **Three live public APIs, wired together.** UniProt → AlphaFold DB → cancerhotspots.org, with version-resilient URLs and an API-to-file fallback so structure fetches don't go stale as AlphaFold bumps versions.
- **Cached app, network-free core.** Streamlit caching keeps it responsive; the parsing/validation logic carries no UI or network dependency and is fully unit-tested.

**Tech stack:** Python 3.11 · Streamlit · py3Dmol · pandas · requests · pytest

## Quickstart

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

---

<details>
<summary><b>How it runs on a laptop</b></summary>

Predicting protein structures with AlphaFold needs big GPUs. But DeepMind already
ran AlphaFold on ~200 million proteins and made the results free. This tool
**downloads finished structures** instead of computing them, so all the heavy
work is done by hosted services and the browser — no GPU required.

</details>

<details>
<summary><b>Data sources</b> (all free, public)</summary>

| Data | Source |
|------|--------|
| Gene → protein + sequence | [UniProt](https://www.uniprot.org) |
| 3D structures (with pLDDT confidence) | [AlphaFold DB](https://alphafold.ebi.ac.uk) |
| Recurrent cancer mutation hotspots | [cancerhotspots.org](https://www.cancerhotspots.org) |

</details>

<details>
<summary><b>Using the app</b></summary>

In the sidebar: pick or type a gene, enter mutations like `R175H` (separate
several with commas or spaces), and toggle confidence colouring.

</details>

<details>
<summary><b>Architecture & project layout</b></summary>

```
app.py                 Streamlit UI — wires the modules together
cancer_tool/
  uniprot.py           gene symbol -> UniProt accession + sequence
  structures.py        fetch AlphaFold structure (PDB text)
  mutations.py         parse/validate mutations + fetch hotspots
  viewer.py            build the 3D py3Dmol view (confidence colour + highlights)
tests/                 unit tests for mutation parsing
```

</details>

<details>
<summary><b>Testing</b></summary>

```bash
pytest
```

The parsing and validation suite needs no network — the core logic has no
Streamlit/UI or HTTP dependency.

</details>

<details>
<summary><b>Roadmap</b></summary>

- Pathogenicity overlay per residue (AlphaMissense / ClinVar)
- Cohort frequencies & cancer-type filter via cBioPortal
- Drug/target context via Open Targets
- Local docking (AutoDock Vina) and light molecular dynamics (OpenMM)

</details>

<details>
<summary><b>Disclaimer</b></summary>

⚠️ **Research and education use only.** This is not a medical device. It must
not be used for diagnosis or treatment decisions.

</details>

---

<p align="center">
  <img src="docs/VRcompany.png" alt="Vedra Research" width="300">
</p>
