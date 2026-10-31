"""Draw the repository mind map shown at the top of the profile README.

Writes repo-map-light.svg and repo-map-dark.svg next to this script; the README
picks one by the viewer's color scheme. Claude Code sits in the middle, I sit
under it, and each branch is one kind of work with its repositories as leaves.
Edit TOPICS or the flows in draw() when a repository is added, renamed or starts
feeding another one, then run:

    python3 assets/make_repo_map.py

Standard library only.
"""

import os

THEMES = {
    "light": dict(text="#1f2328", muted="#59636e", card="#f6f8fa", card_stroke="#d0d7de",
                  chip="#ffffff", public="#0969da", private="#8c959f", private_text="#59636e",
                  hub="#fbefe9", hub_stroke="#d97757", spoke="#afb8c1", flow="#d97757",
                  area={"Decide": "#8250df", "Know": "#1a7f37", "Learn": "#0969da",
                        "Every morning": "#bc4c00", "Build": "#9a6700"}),
    "dark": dict(text="#e6edf3", muted="#9198a1", card="#151b23", card_stroke="#3d444d",
                 chip="#0d1117", public="#4493f8", private="#656c76", private_text="#9198a1",
                 hub="#2a1a14", hub_stroke="#e07a5f", spoke="#3d444d", flow="#e07a5f",
                 area={"Decide": "#ab7df8", "Know": "#3fb950", "Learn": "#4493f8",
                       "Every morning": "#f0883e", "Build": "#d29922"}),
}

W, H = 1060, 600
HUB_X, HUB_Y, HUB_R = 530, 280, 72
RING = HUB_R + 16
INNER = {-1: 410, 1: 650}  # x of the topic edge that faces the hub, per side
PILL_H, CHIP_H, LEAF_GAP, REACH = 34, 28, 40, 36
ME_Y = 522
FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"

# (topic, side, y, caption, [(repository, is_public)]); side -1 is left of the hub, 1 is right
TOPICS = [
    ("Decide", -1, 150, None, [("persona-debate-lab", True), ("vancouver-room-hunt", True)]),
    ("Build", -1, 410, "in bnitech-lab", [("bnitech-lab.github.io", True), ("vancouver-month-2026", True),
                                          ("8 games, 2011–2017", True)]),
    ("Know", 1, 110, None, [("wiki", False), ("dawnbase", False)]),
    ("Every morning", 1, 280, None, [("ai-trend-digest", True), ("daily-routine", False)]),
    ("Learn", 1, 440, None, [("coding-practice", True)]),
]


def text_w(text, size):
    """A generous width estimate for the system sans at this size; SVG cannot measure text here."""
    return len(text) * size * 0.56


def layout():
    """Pill and leaf boxes for every topic: {topic: (pill_x, pill_w, y, side, [(name, public, x, w, y)])}."""
    out = {}
    for topic, side, y, _, repos in TOPICS:
        pill_w = text_w(topic, 17) + 32
        pill_x = INNER[side] - pill_w if side < 0 else INNER[side]
        leaves = []
        for i, (name, public) in enumerate(repos):
            leaf_w = text_w(name, 15) + 28 + (0 if public else 52)
            leaf_y = y + (i - (len(repos) - 1) / 2) * LEAF_GAP
            leaf_x = pill_x - REACH - leaf_w if side < 0 else pill_x + pill_w + REACH
            leaves.append((name, public, leaf_x, leaf_w, leaf_y))
        out[topic] = (pill_x, pill_w, y, side, leaves)
    return out


def curve(x1, y1, x2, y2):
    """A mind-map branch: leaves and arrives horizontally."""
    mid = (x1 + x2) / 2
    return f"M{x1:.1f},{y1:.1f} C{mid:.1f},{y1:.1f} {mid:.1f},{y2:.1f} {x2:.1f},{y2:.1f}"


def draw(theme):
    c = THEMES[theme]
    boxes = layout()
    out = []
    add = out.append
    add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
        f'font-family="{FONT}">')
    add('<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
        f'markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" '
        f'fill="{c["flow"]}"/></marker></defs>')

    # Branches from the hub to each topic, and from each topic to its repositories.
    for topic, (pill_x, pill_w, y, side, leaves) in boxes.items():
        color = c["area"][topic]
        add(f'<path d="{curve(HUB_X, HUB_Y, INNER[side], y)}" fill="none" stroke="{color}" '
            f'stroke-width="3" stroke-linecap="round" opacity="0.85"/>')
        outer = pill_x if side < 0 else pill_x + pill_w
        for _, _, leaf_x, leaf_w, leaf_y in leaves:
            near = leaf_x + leaf_w if side < 0 else leaf_x
            add(f'<path d="{curve(outer, y, near, leaf_y)}" fill="none" stroke="{color}" '
                f'stroke-width="1.6" opacity="0.7"/>')

    # Me, under the hub.
    add(f'<line x1="{HUB_X}" y1="{HUB_Y + RING}" x2="{HUB_X}" y2="{ME_Y - 24}" stroke="{c["spoke"]}" '
        f'stroke-width="2"/>')
    add(f'<rect x="{HUB_X - 80}" y="{ME_Y - 24}" width="160" height="48" rx="24" fill="{c["card"]}" '
        f'stroke="{c["card_stroke"]}" stroke-width="1.5"/>')
    add(f'<text x="{HUB_X}" y="{ME_Y + 6}" text-anchor="middle" font-size="17" fill="{c["text"]}">'
        f'<tspan font-weight="700">Me</tspan><tspan fill="{c["muted"]}" font-size="14"> · I decide</tspan></text>')

    # Hub, with the guard plugins as a dashed ring around it.
    add(f'<circle cx="{HUB_X}" cy="{HUB_Y}" r="{RING}" fill="{c["chip"]}" stroke="{c["hub_stroke"]}" '
        f'stroke-width="1.5" stroke-dasharray="5 5" opacity="0.9"/>')
    add(f'<text x="{HUB_X}" y="{HUB_Y - RING - 10}" text-anchor="middle" font-size="13" '
        f'fill="{c["muted"]}">3 guard plugins</text>')
    add(f'<circle cx="{HUB_X}" cy="{HUB_Y}" r="{HUB_R}" fill="{c["hub"]}" stroke="{c["hub_stroke"]}" '
        f'stroke-width="2"/>')
    add(f'<text x="{HUB_X}" y="{HUB_Y - 9}" text-anchor="middle" font-size="21" font-weight="700" '
        f'fill="{c["text"]}">Claude Code</text>')
    add(f'<text x="{HUB_X}" y="{HUB_Y + 15}" text-anchor="middle" font-size="14" '
        f'fill="{c["muted"]}">claude-config</text>')
    add(f'<text x="{HUB_X}" y="{HUB_Y + 34}" text-anchor="middle" font-size="14" '
        f'fill="{c["muted"]}">15+ skills</text>')

    # Topics as pills, repositories as chips: solid for public, dashed for private.
    for topic, side, y, caption, _ in TOPICS:
        pill_x, pill_w, _, _, leaves = boxes[topic]
        color = c["area"][topic]
        add(f'<rect x="{pill_x:.1f}" y="{y - PILL_H / 2}" width="{pill_w:.1f}" height="{PILL_H}" rx="{PILL_H / 2}" '
            f'fill="{c["card"]}" stroke="{color}" stroke-width="2"/>')
        add(f'<text x="{pill_x + pill_w / 2:.1f}" y="{y + 6}" text-anchor="middle" font-size="17" '
            f'font-weight="700" fill="{color}">{topic}</text>')
        if caption:
            add(f'<text x="{pill_x + pill_w / 2:.1f}" y="{y + PILL_H / 2 + 17}" text-anchor="middle" '
                f'font-size="13" fill="{c["muted"]}">{caption}</text>')
        for name, public, leaf_x, leaf_w, leaf_y in leaves:
            top = leaf_y - CHIP_H / 2
            if public:
                add(f'<rect x="{leaf_x:.1f}" y="{top}" width="{leaf_w:.1f}" height="{CHIP_H}" rx="14" '
                    f'fill="{c["chip"]}" stroke="{c["public"]}" stroke-width="1.5"/>')
                add(f'<text x="{leaf_x + 14:.1f}" y="{top + 19.5}" font-size="15" font-weight="600" '
                    f'fill="{c["public"]}">{name}</text>')
            else:
                add(f'<rect x="{leaf_x:.1f}" y="{top}" width="{leaf_w:.1f}" height="{CHIP_H}" rx="14" '
                    f'fill="{c["chip"]}" stroke="{c["private"]}" stroke-width="1.5" stroke-dasharray="4 3"/>')
                add(f'<text x="{leaf_x + 14:.1f}" y="{top + 19.5}" font-size="15" '
                    f'fill="{c["private_text"]}">{name}</text>')
                add(f'<text x="{leaf_x + leaf_w - 12:.1f}" y="{top + 19}" text-anchor="end" font-size="12" '
                    f'fill="{c["private_text"]}">private</text>')

    # What flows between repositories (orange, dashed), routed so no arrow crosses a branch.
    def leaf(topic, name):
        return next(l for l in boxes[topic][4] if l[0] == name)

    def flow(d, text, x, y, anchor="middle"):
        add(f'<path d="{d}" fill="none" stroke="{c["flow"]}" stroke-width="1.8" stroke-dasharray="6 4" '
            f'marker-end="url(#arrow)"/>')
        add(f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-size="14" fill="{c["flow"]}">{text}</text>')

    # persona-debate-lab -> wiki, over the top
    _, _, ax, aw, ay = leaf("Decide", "persona-debate-lab")
    _, _, bx, bw, by = leaf("Know", "wiki")
    x1, y1, x2, y2 = ax + aw / 2, ay - CHIP_H / 2, bx + bw / 2, by - CHIP_H / 2 - 2
    flow(f"M{x1:.1f},{y1:.1f} C{x1:.1f},34 {x2:.1f},34 {x2:.1f},{y2:.1f}", "debate transcripts", (x1 + x2) / 2, 30)
    # persona-debate-lab -> bnitech-lab, around the left edge: adopted ideas become repositories and lab rows
    _, _, cx, _, cy = leaf("Build", "bnitech-lab.github.io")
    edge = min(ax, cx) - 40
    flow(f"M{ax:.1f},{ay:.1f} C{edge:.1f},{ay:.1f} {edge:.1f},{cy:.1f} {cx - 2:.1f},{cy:.1f}", "adopted ideas",
         edge + 26, (ay + cy) / 2 + 5, "start")
    # daily-routine -> coding-practice, straight down the right column
    _, _, dx, dw, dy = leaf("Every morning", "daily-routine")
    _, _, ex, ew, ey = leaf("Learn", "coding-practice")
    x = (max(dx, ex) + min(dx + dw, ex + ew)) / 2
    flow(f"M{x:.1f},{dy + CHIP_H / 2:.1f} L{x:.1f},{ey - CHIP_H / 2 - 2:.1f}", "today's practice",
         x + 10, (dy + ey) / 2 + 5, "start")

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
