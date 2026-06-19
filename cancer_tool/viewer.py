"""Build interactive 3D molecular views with py3Dmol.

The view is returned as a self-contained HTML string so it can be embedded in
Streamlit via ``st.components.v1.html``. Two layers matter: colouring by pLDDT
confidence (don't trust low-confidence regions) and highlighting mutated residues.
"""

from __future__ import annotations

import py3Dmol

_HIGHLIGHT_COLORS = ["magenta", "orange", "lime", "cyan", "yellow", "red"]


def render_structure(
    pdb_text: str,
    highlights: list[dict] | None = None,
    color_by_confidence: bool = True,
    width: int = 900,
    height: int = 600,
) -> str:
    """Return embeddable HTML for a 3D view of ``pdb_text``.

    ``highlights`` is a list of ``{position, label, color?}`` dicts; each named
    residue is drawn as sticks + a translucent sphere and labelled. When
    ``color_by_confidence`` is true the cartoon is coloured by the B-factor
    column, which for AlphaFold models holds the per-residue pLDDT score
    (red ≈ low confidence, blue ≈ high).
    """
    view = py3Dmol.view(width=width, height=height)
    view.addModel(pdb_text, "pdb")

    if color_by_confidence:
        view.setStyle(
            {
                "cartoon": {
                    "colorscheme": {
                        "prop": "b",
                        "gradient": "roygb",
                        "min": 50,
                        "max": 90,
                    }
                }
            }
        )
    else:
        view.setStyle({"cartoon": {"color": "spectrum"}})

    for index, hit in enumerate(highlights or []):
        position = str(hit["position"])
        color = hit.get("color") or _HIGHLIGHT_COLORS[index % len(_HIGHLIGHT_COLORS)]
        selection = {"resi": position}
        view.addStyle(selection, {"stick": {"color": color, "radius": 0.3}})
        view.addStyle(selection, {"sphere": {"color": color, "opacity": 0.6}})
        view.addResLabels(
            selection,
            {
                "fontSize": 11,
                "fontColor": "black",
                "backgroundColor": color,
                "backgroundOpacity": 0.75,
            },
        )

    view.zoomTo()
    view.setBackgroundColor("0x0A0A0B")
    return view._make_html()
