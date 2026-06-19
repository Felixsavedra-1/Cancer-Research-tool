"""Build interactive 3D molecular views with py3Dmol."""

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

    Each ``highlights`` entry (``{position, label, color?}``) is drawn as sticks plus
    a translucent sphere and labelled. With ``color_by_confidence`` the cartoon is
    coloured by pLDDT (the B-factor column of AlphaFold models): red low, blue high.
    """
    view = py3Dmol.view(width=width, height=height)
    view.addModel(pdb_text, "pdb")

    if color_by_confidence:
        view.setStyle(
            {"cartoon": {"colorscheme": {"prop": "b", "gradient": "roygb", "min": 50, "max": 90}}}
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
