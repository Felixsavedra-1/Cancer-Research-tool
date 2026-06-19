"""Fetch precomputed AlphaFold structures as PDB text."""

from __future__ import annotations

import requests

ALPHAFOLD_API = "https://alphafold.ebi.ac.uk/api/prediction/{accession}"
ALPHAFOLD_FILE = "https://alphafold.ebi.ac.uk/files/AF-{accession}-F1-model_v6.pdb"


def fetch_alphafold_pdb(accession: str, session: requests.Session | None = None) -> str:
    """Return AlphaFold model PDB text for a UniProt accession.

    Resolves the current model URL via the API (the file version bumps over time)
    and falls back to the direct versioned file URL. Raises ``requests.HTTPError``
    if the structure cannot be retrieved.
    """
    http = session or requests

    try:
        meta = http.get(ALPHAFOLD_API.format(accession=accession), timeout=30)
        if meta.ok:
            payload = meta.json()
            if payload:
                pdb_url = payload[0].get("pdbUrl")
                if pdb_url:
                    pdb = http.get(pdb_url, timeout=60)
                    pdb.raise_for_status()
                    return pdb.text
    except (requests.RequestException, ValueError, KeyError, IndexError):
        pass

    direct = http.get(ALPHAFOLD_FILE.format(accession=accession), timeout=60)
    direct.raise_for_status()
    return direct.text
