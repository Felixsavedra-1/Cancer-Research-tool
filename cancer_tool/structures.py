"""Fetch precomputed 3D protein structures.

AlphaFold already ran on ~200M proteins; we download the finished model rather
than predicting anything locally (which is why this runs fine on a laptop).
The structure is returned as PDB-format text. AlphaFold stores the per-residue
pLDDT confidence score in the B-factor column of that text, which the viewer
uses to colour the model by reliability.
"""

from __future__ import annotations

import requests

# Always resolve the model URL via the API rather than hardcoding a version:
# AlphaFold bumps the version over time (v4 -> v6 -> ...), so a fixed file URL
# goes stale and 404s. The API returns the current ``pdbUrl``.
ALPHAFOLD_API = "https://alphafold.ebi.ac.uk/api/prediction/{accession}"
ALPHAFOLD_FILE = "https://alphafold.ebi.ac.uk/files/AF-{accession}-F1-model_v6.pdb"


def fetch_alphafold_pdb(accession: str, session: requests.Session | None = None) -> str:
    """Return AlphaFold model PDB text for a UniProt accession.

    Tries the API (which returns the canonical, current ``pdbUrl``) and falls
    back to the direct versioned file URL. Raises ``requests.HTTPError`` if the
    structure cannot be retrieved.
    """
    http = session or requests

    try:
        api = ALPHAFOLD_API.format(accession=accession)
        meta = http.get(api, timeout=30)
        if meta.ok:
            payload = meta.json()
            if payload:
                pdb_url = payload[0].get("pdbUrl")
                if pdb_url:
                    pdb = http.get(pdb_url, timeout=60)
                    pdb.raise_for_status()
                    return pdb.text
    except (requests.RequestException, ValueError, KeyError, IndexError):
        pass  # fall through to the direct file URL

    direct = http.get(ALPHAFOLD_FILE.format(accession=accession), timeout=60)
    direct.raise_for_status()
    return direct.text
