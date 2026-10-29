"""Draw the repository map shown at the top of the profile README.

Writes repo-map-light.svg and repo-map-dark.svg next to this script; the README
picks one by the viewer's color scheme. Edit CARDS or FLOWS when a repository is
added, renamed or starts feeding another one, then run:

    python3 assets/make_repo_map.py

Standard library only.
"""

import os

THEMES = {
    "light": dict(text="#1f2328", muted="#59636e", card="#f6f8fa", card_stroke="#d0d7de",
                  chip="#ffffff", public="#0969da", private="#8c959f", private_text="#59636e",
                  hub="#fbefe9", hub_stroke="#d97757", spoke="#afb8c1", flow="#d97757",
                  area={"Decide": "#8250df", "Know": "#1a7f37", "Learn": "#0969da",
                        "Every morning": "#bc4c00"}),
    "dark": dict(text="#e6edf3", muted="#9198a1", card="#151b23", card_stroke="#3d444d",
                 chip="#0d1117", public="#4493f8", private="#656c76", private_text="#9198a1",
                 hub="#2a1a14", hub_stroke="#e07a5f", spoke="#3d444d", flow="#e07a5f",
                 area={"Decide": "#ab7df8", "Know": "#3fb950", "Learn": "#4493f8",
                       "Every morning": "#f0883e"}),
}

W, H = 960, 510
CARD_W, CARD_H = 240, 128
LEFT_X, RIGHT_X = 200, 660
TOP_Y, BOTTOM_Y = 24, 340
HUB_X, HUB_Y, HUB_R = 550, 246, 78
FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"

# area: (x, y, [(repository, is_public)])
CARDS = {
    "Decide": (LEFT_X, TOP_Y, [("persona-debate-lab", True), ("vancouver-room-hunt", True)]),
    "Know": (RIGHT_X, TOP_Y, [("wiki", False), ("dawnbase", False)]),
    "Learn": (RIGHT_X, BOTTOM_Y, [("dawndeck", False), ("coding-practice", True)]),
    "Every morning": (LEFT_X, BOTTOM_Y, [("ai-trend-digest", True), ("daily-routine", False)]),
}


def chip_y(card_y, index):
    return card_y + 54 + index * 36


def draw(theme):
    c = THEMES[theme]
    out = []
    add = out.append
    add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
        f'font-family="{FONT}">')
    add('<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
        f'markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" '
        f'fill="{c["flow"]}"/></marker></defs>')

    # Spokes from the hub to the nearest corner of each card, and from me to the hub.
    for x, y, _ in CARDS.values():
        corner_x = x + CARD_W if x < HUB_X else x
        corner_y = y + CARD_H if y < HUB_Y else y
        add(f'<line x1="{HUB_X}" y1="{HUB_Y}" x2="{corner_x}" y2="{corner_y}" '
            f'stroke="{c["spoke"]}" stroke-width="2"/>')
    add(f'<line x1="152" y1="{HUB_Y}" x2="{HUB_X - HUB_R - 18}" y2="{HUB_Y}" '
        f'stroke="{c["spoke"]}" stroke-width="2"/>')

    # Me.
    add(f'<rect x="16" y="{HUB_Y - 33}" width="136" height="66" rx="33" fill="{c["card"]}" '
        f'stroke="{c["card_stroke"]}" stroke-width="1.5"/>')
    add(f'<text x="84" y="{HUB_Y - 5}" text-anchor="middle" font-size="20" font-weight="600" '
        f'fill="{c["text"]}">Me</text>')
    add(f'<text x="84" y="{HUB_Y + 18}" text-anchor="middle" font-size="14" '
        f'fill="{c["muted"]}">I decide</text>')

    # Hub, with the guard plugins as a dashed ring around it.
    add(f'<circle cx="{HUB_X}" cy="{HUB_Y}" r="{HUB_R + 16}" fill="none" stroke="{c["hub_stroke"]}" '
        f'stroke-width="1.5" stroke-dasharray="5 5" opacity="0.8"/>')
    add(f'<text x="{HUB_X}" y="{HUB_Y - HUB_R - 24}" text-anchor="middle" font-size="13" '
        f'fill="{c["muted"]}">3 guard plugins</text>')
    add(f'<circle cx="{HUB_X}" cy="{HUB_Y}" r="{HUB_R}" fill="{c["hub"]}" stroke="{c["hub_stroke"]}" '
        f'stroke-width="2"/>')
    add(f'<text x="{HUB_X}" y="{HUB_Y - 9}" text-anchor="middle" font-size="21" font-weight="700" '
        f'fill="{c["text"]}">Claude Code</text>')
    add(f'<text x="{HUB_X}" y="{HUB_Y + 15}" text-anchor="middle" font-size="14" '
        f'fill="{c["muted"]}">claude-config</text>')
    add(f'<text x="{HUB_X}" y="{HUB_Y + 34}" text-anchor="middle" font-size="14" '
        f'fill="{c["muted"]}">15+ skills</text>')

    # Area cards with one chip per repository: solid for public, dashed for private.
    for area, (x, y, repos) in CARDS.items():
        color = c["area"][area]
        add(f'<rect x="{x}" y="{y}" width="{CARD_W}" height="{CARD_H}" rx="12" fill="{c["card"]}" '
            f'stroke="{c["card_stroke"]}" stroke-width="1.5"/>')
        add(f'<rect x="{x}" y="{y + 13}" width="4" height="24" rx="2" fill="{color}"/>')
        add(f'<text x="{x + 16}" y="{y + 32}" font-size="18" font-weight="700" '
            f'fill="{color}">{area}</text>')
        for i, (name, public) in enumerate(repos):
            top = chip_y(y, i)
            if public:
                add(f'<rect x="{x + 14}" y="{top}" width="{CARD_W - 28}" height="28" rx="14" '
                    f'fill="{c["chip"]}" stroke="{c["public"]}" stroke-width="1.5"/>')
                add(f'<text x="{x + 28}" y="{top + 19.5}" font-size="15" font-weight="600" '
                    f'fill="{c["public"]}">{name}</text>')
            else:
                add(f'<rect x="{x + 14}" y="{top}" width="{CARD_W - 28}" height="28" rx="14" '
                    f'fill="{c["chip"]}" stroke="{c["private"]}" stroke-width="1.5" '
                    f'stroke-dasharray="4 3"/>')
                add(f'<text x="{x + 28}" y="{top + 19.5}" font-size="15" '
                    f'fill="{c["private_text"]}">{name}</text>')
                add(f'<text x="{x + CARD_W - 26}" y="{top + 19}" text-anchor="end" font-size="12" '
                    f'fill="{c["private_text"]}">private</text>')

    # What flows between repositories (orange, dashed).
    def label(x, y, text, anchor="middle"):
        add(f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="14" '
            f'fill="{c["flow"]}">{text}</text>')

    def line(x1, y1, x2, y2):
        add(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c["flow"]}" stroke-width="1.8" '
            f'stroke-dasharray="6 4" marker-end="url(#arrow)"/>')

    # persona-debate-lab -> wiki
    y = chip_y(TOP_Y, 0) + 14
    line(LEFT_X + CARD_W - 14, y, RIGHT_X + 14, y)
    label(HUB_X, y - 8, "debate transcripts")
    # wiki -> dawndeck, around the right edge
    edge = RIGHT_X + CARD_W + 22
    y1, y2 = chip_y(TOP_Y, 0) + 14, chip_y(BOTTOM_Y, 0) + 14
    add(f'<path d="M{RIGHT_X + CARD_W - 14},{y1} H{edge} V{y2} H{RIGHT_X + CARD_W - 12}" fill="none" '
        f'stroke="{c["flow"]}" stroke-width="1.8" stroke-dasharray="6 4" marker-end="url(#arrow)"/>')
    label(edge - 8, HUB_Y + 5, "pages to review", "end")
    # daily-routine -> coding-practice
    y = chip_y(BOTTOM_Y, 1) + 14
    line(LEFT_X + CARD_W - 14, y, RIGHT_X + 14, y)
    label(HUB_X, y - 8, "today's practice")

    add(f'<text x="{W / 2}" y="{H - 12}" text-anchor="middle" font-size="13" fill="{c["muted"]}">'
        'solid: public repo · dashed: private repo · orange arrows: what flows between them</text>')
    add('</svg>')
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    for theme in THEMES:
        path = os.path.join(here, f"repo-map-{theme}.svg")
        with open(path, "w", encoding="utf-8") as f:
            f.write(draw(theme))
        print(path)
