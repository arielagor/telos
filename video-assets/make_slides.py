#!/usr/bin/env python3
"""Generate the 15 Telos cutaway slides (1920x1080, AGOR look) as PNGs.

AGOR design: bg #0a0e1a, surface #121829, gradient #8b5cf6->#ec4899->#38bdf8 (accent only),
Segoe UI / Arial, rounded 16px cards, restrained executive motion (motion added in compositing).
Run: python make_slides.py  ->  cutaways/slide-b01.png .. slide-b15.png
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "cutaways")
os.makedirs(OUT, exist_ok=True)
W, H = 1920, 1080

BG = (10, 14, 26)
SURFACE = (18, 24, 41)
SURFACE2 = (27, 36, 64)
TEXT = (244, 246, 251)
MUTED = (140, 152, 181)
LINE = (42, 53, 86)
VIOLET = (139, 92, 246)
PINK = (236, 72, 153)
CYAN = (56, 189, 248)
RED = (248, 113, 113)
GREEN = (52, 211, 153)

FONTS = ["C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf"]
FONTS_B = ["C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf"]
FONTS_SB = ["C:/Windows/Fonts/seguisb.ttf", "C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf"]


def font(size, bold=False, semi=False):
    cands = FONTS_B if bold else (FONTS_SB if semi else FONTS)
    for p in cands:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def grad_h(w, h, stops=((VIOLET, 0.0), (PINK, 0.5), (CYAN, 1.0))):
    img = Image.new("RGB", (w, h))
    px = img.load()
    for x in range(w):
        t = x / max(1, w - 1)
        for i in range(len(stops) - 1):
            (c0, t0), (c1, t1) = stops[i], stops[i + 1]
            if t0 <= t <= t1:
                f = (t - t0) / max(1e-6, t1 - t0)
                c = tuple(int(c0[j] + (c1[j] - c0[j]) * f) for j in range(3))
                break
        else:
            c = stops[-1][0]
        for y in range(h):
            px[x, y] = c
    return img


def rounded(draw, box, r, fill=None, outline=None, width=1):
    draw.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)


def text_w(d, s, f):
    return d.textbbox((0, 0), s, font=f)[2]


def wrap(d, s, f, maxw):
    words, lines, cur = s.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if text_w(d, t, f) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def base(kicker, headline):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    # faint corner glow
    glow = Image.new("RGB", (W, H), BG)
    gd = ImageDraw.Draw(glow)
    gd.ellipse([W - 720, -360, W + 360, 480], fill=(20, 22, 52))
    glow = glow.filter(ImageFilter.GaussianBlur(180))
    img = Image.blend(img, glow, 0.5)
    d = ImageDraw.Draw(img)
    # brand mark top-left
    d.text((90, 70), "TELOS", font=font(30, bold=True), fill=TEXT)
    img.paste(grad_h(150, 5), (92, 112))
    d.text((250, 74), "for OmegaClaw", font=font(24, semi=True), fill=MUTED)
    # kicker + headline
    if kicker:
        d.text((90, 196), kicker.upper(), font=font(26, bold=True), fill=CYAN)
    hl_f = font(76, bold=True)
    y = 236
    for ln in wrap(d, headline, hl_f, W - 320):
        d.text((90, y), ln, font=hl_f, fill=TEXT)
        y += 90
    # signature gradient rule under headline
    img.paste(grad_h(360, 6), (92, y + 6))
    return img, d, y + 40


def save(img, name):
    img.save(os.path.join(OUT, name))
    print("wrote", name)


def card(d, img, box, title, body, accent=VIOLET, title_size=34, body_size=27):
    x0, y0, x1, y1 = box
    rounded(d, box, 18, fill=SURFACE)
    img.paste(grad_h(6, y1 - y0 - 40, ((accent, 0), (accent, 1))), (x0 + 22, y0 + 20))
    d.text((x0 + 46, y0 + 26), title, font=font(title_size, bold=True), fill=TEXT)
    yy = y0 + 26 + title_size + 16
    for ln in (body if isinstance(body, list) else wrap(d, body, font(body_size), x1 - x0 - 80)):
        d.text((x0 + 46, yy), ln, font=font(body_size), fill=MUTED)
        yy += body_size + 12


def bullets(d, items, x, y, w, gap=22, size=34, dot=CYAN):
    f = font(size)
    for it in items:
        d.ellipse([x, y + size // 2 - 7, x + 14, y + size // 2 + 7], fill=dot)
        for i, ln in enumerate(wrap(d, it, f, w - 50)):
            d.text((x + 36, y), ln, font=f, fill=TEXT if i == 0 else MUTED)
            y += size + 6
        y += gap
    return y


def arrow(d, p0, p1, color=MUTED, width=4):
    d.line([p0, p1], fill=color, width=width)
    import math
    ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    for s in (-0.4, 0.4):
        d.line([p1, (p1[0] - 18 * math.cos(ang + s), p1[1] - 18 * math.sin(ang + s))], fill=color, width=width)


def node(d, cx, cy, w, h, label, sub=None, fill=SURFACE2, accent=VIOLET):
    box = [cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2]
    rounded(d, box, 14, fill=fill, outline=accent, width=3)
    f = font(30, bold=True)
    tw = text_w(d, label, f)
    d.text((cx - tw // 2, cy - (28 if sub else 16)), label, font=f, fill=TEXT)
    if sub:
        sf = font(22)
        sw = text_w(d, sub, sf)
        d.text((cx - sw // 2, cy + 10), sub, font=sf, fill=MUTED)


# ---------------- slides ----------------
def s01():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    glow = Image.new("RGB", (W, H), BG); gd = ImageDraw.Draw(glow)
    gd.ellipse([W//2-700, H//2-500, W//2+700, H//2+500], fill=(24, 22, 56))
    img = Image.blend(img, glow.filter(ImageFilter.GaussianBlur(200)), 0.6); d = ImageDraw.Draw(img)
    t = "TELOS"
    f = font(180, bold=True); tw = text_w(d, t, f)
    d.text(((W - tw)//2, 300), t, font=f, fill=TEXT)
    img.paste(grad_h(520, 10), ((W - 520)//2, 510))
    sub = "Goal understanding for OmegaClaw"
    sf = font(48, semi=True); sw = text_w(d, sub, sf)
    d.text(((W - sw)//2, 560), sub, font=sf, fill=MUTED)
    tag = "BGI Sprint I  ·  Improvements to OmegaClaw"
    tf = font(30); tw2 = text_w(d, tag, tf)
    d.text(((W - tw2)//2, 660), tag, font=tf, fill=CYAN)
    save(img, "slide-b01.png")


def s01b():  # the vignette
    img, d, y = base("the failure that motivates this", "It did what you said. It defeated why you said it.")
    box = [90, y + 30, W - 90, H - 110]
    rounded(d, box, 18, fill=SURFACE)
    d.text((140, y + 70), "“Just make the failing tests pass before the demo.”", font=font(40, semi=True), fill=TEXT)
    d.text((140, y + 150), "Capable agent:", font=font(30, bold=True), fill=MUTED)
    d.text((420, y + 150), "deletes the 3 failing tests  →  suite turns green", font=font(30), fill=GREEN)
    d.text((140, y + 230), "Result:", font=font(30, bold=True), fill=MUTED)
    d.text((420, y + 230), "understood the words, missed the goal.", font=font(30), fill=RED)
    d.text((140, y + 320), "The gap between the literal request and the real goal is where", font=font(32), fill=TEXT)
    d.text((140, y + 364), "autonomous agents are most dangerous — and it is rarely measured.", font=font(32), fill=TEXT)
    save(img, "slide-b02.png")


def s02():
    img, d, y = base("why it matters for BGI", "Goal misunderstanding is a safety property, not a slogan")
    items = [
        "Optimizes a proxy — and the proxy drifts from the point (Goodhart).",
        "Serves one person — and quietly externalizes the cost onto everyone else.",
        "Keeps chasing a goal you abandoned weeks ago.",
        "None of these are caught by asking ‘can the model do the task.’",
    ]
    bullets(d, items, 110, y + 40, W - 240, size=40, gap=26)
    save(img, "slide-b03.png")


def s03():
    img, d, y = base("the gap Telos fills", "OmegaClaw is goal-autonomous — but ships no goal model")
    box = [90, y + 30, W - 90, H - 110]
    rounded(d, box, 18, fill=SURFACE)
    d.text((140, y + 64), "grep  asi-alliance/OmegaClaw-Core", font=font(34, bold=True), fill=CYAN)
    rows = [
        ("242", "files in the public repo"),
        ("0", "dedicated goal-representation modules"),
        ("0", "occurrences of ‘goal’ in lib_omegaclaw.metta / run.metta"),
    ]
    yy = y + 140
    for big, lab in rows:
        d.text((160, yy), big, font=font(64, bold=True), fill=TEXT)
        d.text((320, yy + 18), lab, font=font(34), fill=MUTED)
        yy += 110
    d.text((140, yy + 6), "The capability is there. The inspectable model of the goals is not.", font=font(32, semi=True), fill=TEXT)
    save(img, "slide-b04.png")


def s04():
    img, d, y = base("what Telos is", "Three parts")
    cards = [("1 · Goal graph", "Individual vs collective goals, four relations, an alignment score. ~250 lines, no model calls inside.", VIOLET),
             ("2 · Benchmark", "14 scenarios across 7 categories with gold labels — does the agent understand the goals?", PINK),
             ("3 · Beneficial council", "Claude + Gemini + OpenAI judge and red-team each other. Judge, safeguard, and build engine.", CYAN)]
    cw = (W - 180 - 80) // 3
    for i, (t, b, a) in enumerate(cards):
        x0 = 90 + i * (cw + 40)
        card(d, img, [x0, y + 40, x0 + cw, H - 130], t, b, accent=a)
    save(img, "slide-b05.png")


def s05():
    img, d, y = base("the goal graph", "Individual and collective goals, and how they collide")
    cy = y + 230
    node(d, 420, cy, 320, 130, "Alice", "individual goal", accent=VIOLET)
    node(d, 1180, cy, 360, 130, "The DAO", "collective goal", accent=CYAN)
    arrow(d, (588, cy), (998, cy), color=RED, width=6)
    d.text((700, cy - 70), "CONFLICTS", font=font(30, bold=True), fill=RED)
    # relations legend
    d.text((90, cy + 160), "Relations:", font=font(30, bold=True), fill=MUTED)
    for i, (r, c) in enumerate([("supports", GREEN), ("conflicts", RED), ("subsumes", VIOLET), ("depends_on", CYAN)]):
        d.text((320 + i * 320, cy + 160), r, font=font(30, bold=True), fill=c)
    # alignment meter
    d.text((90, cy + 250), "alignment score", font=font(28), fill=MUTED)
    img.paste(grad_h(700, 18, ((RED, 0), (MUTED, 0.5), (GREEN, 1))), (420, cy + 256))
    d.polygon([(560, cy + 250), (548, cy + 232), (572, cy + 232)], fill=TEXT)  # marker toward negative
    d.text((1150, cy + 250), "individual ↔ collective", font=font(26), fill=MUTED)
    save(img, "slide-b06.png")


def s06():
    img, d, y = base("how a scenario works", "The agent returns a goal reading; we score it vs gold")
    lh = [90, y + 40, 940, H - 130]; rh = [980, y + 40, W - 90, H - 130]
    rounded(d, lh, 18, fill=SURFACE); rounded(d, rh, 18, fill=SURFACE)
    d.text((130, y + 64), "Goal reading (agent output)", font=font(30, bold=True), fill=CYAN)
    code = ['{', '  "goals": [', '    {"desc": "ship by Thursday",', '     "scope": "individual",', '     "implicit": true}, ...],', '  "conflicts": [...],', '  "recommended_action": "...",', '  "refused": false', '}']
    yy = y + 116
    for ln in code:
        d.text((130, yy), ln, font=font(28), fill=TEXT); yy += 38
    d.text((1020, y + 64), "Gold labels", font=font(30, bold=True), fill=PINK)
    for i, ln in enumerate(["individual + collective goals", "the implicit ones", "the real conflicts", "the beneficial action", "must_refuse (for harm cases)"]):
        d.ellipse([1020, y + 124 + i*64, 1034, y + 138 + i*64], fill=PINK)
        d.text((1056, y + 116 + i*64), ln, font=font(32), fill=TEXT)
    save(img, "slide-b07.png")


def s07():
    img, d, y = base("the benchmark", "Seven categories of goal understanding")
    cats = [("Implicit goal inference", "the real goal behind a literal request"),
            ("Individual vs collective conflict", "one member monopolizes a shared pool"),
            ("Beneficial refusal (+ benign twin)", "refuse real harm, not honest criticism"),
            ("Goal progress tracking", "blocked on a dependency, or abandoned"),
            ("Competing stakeholders", "reconcile several legitimate people fairly"),
            ("Goal ambiguity (+ false-conflict)", "ask vs assume; do not invent a clash"),
            ("Collective overreach", "protect the individual from a bad majority")]
    cw = (W - 180 - 40) // 2
    for i, (t, s) in enumerate(cats):
        col, row = i % 2, i // 2
        x0 = 90 + col * (cw + 40); y0 = y + 36 + row * 132
        if y0 + 116 > H - 60: break
        rounded(d, [x0, y0, x0 + cw, y0 + 116], 14, fill=SURFACE)
        d.text((x0 + 30, y0 + 22), f"{i+1}", font=font(40, bold=True), fill=CYAN)
        d.text((x0 + 90, y0 + 18), t, font=font(31, bold=True), fill=TEXT)
        d.text((x0 + 90, y0 + 62), s, font=font(25), fill=MUTED)
    save(img, "slide-b08.png")


def s08():
    img, d, y = base("why it cannot be gamed cheaply", "Every reflex strategy fails a guard")
    rows = [("Always refuse", "fails the benign twins (honest critique must NOT be refused)", RED),
            ("Always flag a conflict", "fails the false-conflict guard (fast vs stable is reconcilable)", RED),
            ("Always side with the group", "fails collective overreach (a manipulated majority)", RED)]
    yy = y + 50
    for strat, why, c in rows:
        rounded(d, [90, yy, W - 90, yy + 150], 16, fill=SURFACE)
        d.text((130, yy + 28), strat, font=font(40, bold=True), fill=TEXT)
        d.text((130, yy + 88), "→  " + why, font=font(30), fill=MUTED)
        d.text((W - 250, yy + 50), "FAILS", font=font(44, bold=True), fill=c)
        yy += 174
    save(img, "slide-b09.png")


def s09():
    img, d, y = base("the cross-family council", "No model ever grades itself")
    cy = y + 150
    for i, (nm, c) in enumerate([("Claude", VIOLET), ("Gemini", PINK), ("OpenAI", CYAN)]):
        node(d, 320 + i * 360, cy, 300, 110, nm, accent=c)
    for i in range(3):
        arrow(d, (320 + i*360, cy + 55), (W//2, cy + 230), color=MUTED, width=3)
    node(d, W//2, cy + 290, 520, 120, "propose → red-team → synthesize", accent=TEXT if False else VIOLET)
    d.text((W//2 - 300, cy + 430), "Each agent's own family is excluded from its jury.", font=font(34, semi=True), fill=MUTED)
    d.text((W//2 - 300, cy + 480), "Judge  ·  prototype alignment check  ·  the engine that built this", font=font(30), fill=CYAN)
    save(img, "slide-b10.png")


def s10():
    img, d, y = base("results (pilot)", "The disagreement is the finding")
    rows = [("claude", "0.94", "0.96", "0.85", "0.99", "1.00"),
            ("openai", "0.91", "0.94", "0.80", "0.97", "1.00"),
            ("gemini", "0.90", "0.91", "0.82", "0.90", "1.00")]
    cols = ["agent", "overall", "goal inf", "conflict", "collective", "refusal"]
    x0, y0 = 110, y + 40; cw = 200  # narrow cols -> full table clears the avatar PiP on the right
    for j, c in enumerate(cols):
        d.text((x0 + j * cw, y0), c, font=font(28, bold=True), fill=CYAN)
    for i, r in enumerate(rows):
        yy = y0 + 56 + i * 74
        for j, v in enumerate(r):
            d.text((x0 + j * cw, yy), v, font=font(40, bold=(j in (0, 1))), fill=TEXT)
    by = y0 + 56 + 3 * 74 + 30
    rounded(d, [90, by, 1300, by + 96], 14, fill=SURFACE2)
    d.text((130, by + 18), "N = 14  ·  not statistically significant", font=font(34, bold=True), fill=PINK)
    d.text((130, by + 58), "inter-judge spread up to 0.80", font=font(28), fill=MUTED)
    save(img, "slide-b11.png")


def s11():
    img, d, y = base("the agents policed themselves", "Three self-corrections before submitting")
    cards = [("1 · Caught its own bias", "Two families independently flagged a paternalism bias → added the symmetric category (protect the individual).", VIOLET),
             ("2 · Fixed its own metric", "First benchmark run exposed an ambiguous refusal rule → tightened it.", PINK),
             ("3 · Deleted its overclaims", "A final adversarial review rejected 2 false accusations, then forced us to cut our own oversell.", CYAN)]
    cw = (W - 180 - 80) // 3
    for i, (t, b, a) in enumerate(cards):
        x0 = 90 + i * (cw + 40)
        card(d, img, [x0, y + 40, x0 + cw, H - 130], t, b, accent=a)
    save(img, "slide-b12.png")


def s12():
    img, d, y = base("how it fits OmegaClaw", "A MeTTa encoding + three integration levels")
    lh = [90, y + 40, 900, H - 130]
    rounded(d, lh, 18, fill=SURFACE)
    d.text((130, y + 64), "goal_graph.metta  (runs on Hyperon)", font=font(30, bold=True), fill=CYAN)
    for i, ln in enumerate(["(goal alice-train individual alice active)", "(goal dao-fair-access collective dao active)", "(rel conflicts alice-train dao-fair-access)", "", "→ (conflict-between alice-train dao-fair-access)"]):
        d.text((130, y + 120 + i*52), ln, font=font(26), fill=TEXT if not ln.startswith("→") else GREEN)
    d.text((130, H - 200), "pattern-matching, not NAL/PLN inference · not yet in a live OmegaClaw", font=font(24), fill=MUTED)
    rh = [940, y + 40, W - 90, H - 130]
    rounded(d, rh, 18, fill=SURFACE)
    d.text((980, y + 64), "Integration levels", font=font(30, bold=True), fill=PINK)
    for i, ln in enumerate(["1 · Benchmark OmegaClaw over a small shim", "2 · Load the goal graph into its memory", "3 · Wire the benchmark into Autotests/"]):
        d.text((980, y + 130 + i*90), ln, font=font(34), fill=TEXT)
    d.text((980, H - 200), "offered upstream · MIT, same as OmegaClaw", font=font(26), fill=MUTED)
    save(img, "slide-b13.png")


def s13():
    img, d, y = base("a goal-autonomous build", "Human sets the goal and approves; agents do the work")
    cy = y + 200
    steps = ["human goal", "council design", "build", "evaluate", "adversarial review", "submit"]
    x = 130; bw = 250
    for i, s in enumerate(steps):
        node(d, x + bw//2, cy, bw, 100, s, accent=(CYAN if i in (0, 5) else VIOLET))
        if i < len(steps) - 1:
            arrow(d, (x + bw + 6, cy), (x + bw + 44, cy), color=MUTED, width=4)
        x += bw + 50
        if x + bw > W - 90:
            x = 130; cy += 180
    d.text((130, H - 200), "‘Goal-autonomous under human oversight’ — not ‘no human in the loop.’", font=font(34, semi=True), fill=TEXT)
    save(img, "slide-b14.png")


def s14():
    img, d, y = base("limitations (on screen, not buried)", "A seed benchmark, not a validated one")
    items = ["14 public, hand-authored scenarios",
             "reference labels the council helped write — a real circularity",
             "two judges per item, not yet calibrated",
             "MeTTa encoding not yet running inside a live OmegaClaw",
             "no independent maintainer validation yet"]
    bullets(d, items, 110, y + 40, W - 240, size=40, gap=24, dot=PINK)
    save(img, "slide-b15.png")


def s_live():  # slide-b17 — live OmegaClaw benchmark
    img, d, y = base("update · we ran it live", "We benchmarked the live OmegaClaw")
    rows = [("generic:claude", "0.94", False), ("generic:openai", "0.91", False),
            ("generic:gemini", "0.90", False), ("omegaclaw  (live agent)", "0.62", True)]
    x0, y0 = 110, y + 50
    d.text((x0, y0), "agent", font=font(30, bold=True), fill=CYAN)
    d.text((x0 + 760, y0), "overall", font=font(30, bold=True), fill=CYAN)
    for i, (nm, sc, hot) in enumerate(rows):
        yy = y0 + 60 + i * 76
        if hot:
            rounded(d, [x0 - 24, yy - 12, x0 + 1020, yy + 58], 12, fill=SURFACE2)
        d.text((x0, yy), nm, font=font(40, bold=hot), fill=TEXT if not hot else GREEN)
        d.text((x0 + 760, yy), sc, font=font(40, bold=True), fill=TEXT if not hot else GREEN)
    cbx = [1200, y0 + 40, W - 90, y0 + 360]
    rounded(d, cbx, 18, fill=SURFACE)
    d.text((1240, y0 + 70), "10 / 14", font=font(72, bold=True), fill=CYAN)
    d.text((1240, y0 + 156), "scenarios answered cleanly", font=font(30), fill=MUTED)
    d.text((1240, y0 + 210), "mean 0.869", font=font(48, bold=True), fill=GREEN)
    d.text((1240, y0 + 270), "— alongside the frontier models", font=font(28), fill=MUTED)
    d.text((110, H - 150), "The 4 misses: understood, but answered without the agent's `send` command.", font=font(30, semi=True), fill=TEXT)
    d.text((110, H - 110), "The gap is the cost of the autonomous loop — not weaker goal understanding.", font=font(30, semi=True), fill=TEXT)
    save(img, "slide-b17.png")


def s_setup():  # slide-b18 — setup rough edges fixed
    img, d, y = base("making it easier to run", "Five rough edges on the way to a live run — all fixed")
    items = ["MSYS path-mangling crashed the agent on boot  →  MSYS_NO_PATHCONV",
             "vpnkit broke the mock-comm RPC over host.docker.internal  →  user network",
             "the RPC only held on the agent's own loopback  →  in-container bridge",
             "a spam-shield trapped the agent in a loop  →  spamShield=False",
             "bare replies are dropped (OmegaClaw only speaks via `send`)  →  send-wrap"]
    bullets(d, items, 110, y + 44, W - 240, size=36, gap=20, dot=GREEN)
    bx = [90, H - 150, W - 90, H - 70]
    rounded(d, bx, 14, fill=SURFACE2)
    d.text((130, H - 134), "Documented for the next person:  docs/omegaclaw-windows-setup.md", font=font(32, bold=True), fill=CYAN)
    save(img, "slide-b18.png")


def s_article():  # slide-b19 — set it free on a real essay
    img, d, y = base("set it free", "It derived its own goals from a real essay")
    box = [90, y + 36, W - 90, H - 110]
    rounded(d, box, 18, fill=SURFACE)
    d.text((130, y + 64), "Input:  “The World Was Always Talking”  (a real, unstructured article)", font=font(32, semi=True), fill=TEXT)
    d.text((130, y + 132), "It read the goals  ·  individual vs collective  ·  inferred the unstated  ·  named the conflicts", font=font(28), fill=MUTED)
    d.text((130, y + 198), "Then it derived ITS OWN goals:", font=font(32, bold=True), fill=CYAN)
    for i, g in enumerate(["maximize truthful collective value", "preserve epistemic honesty", "do not amplify unverified claims"]):
        d.ellipse([150, y + 256 + i*54, 164, y + 270 + i*54], fill=VIOLET)
        d.text((186, y + 248 + i*54), g, font=font(32), fill=TEXT)
    d.text((130, y + 440), "And it caught itself:", font=font(32, bold=True), fill=GREEN)
    d.text((420, y + 440), "noticing the text was truncated, it refused to repeat numbers it", font=font(30), fill=TEXT)
    d.text((420, y + 482), "couldn’t verify — and called for an open field pilot instead.", font=font(30), fill=TEXT)
    save(img, "slide-b19.png")


def s15():
    img = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(img)
    glow = Image.new("RGB", (W, H), BG); gd = ImageDraw.Draw(glow)
    gd.ellipse([W//2-700, H//2-500, W//2+700, H//2+500], fill=(24, 22, 56))
    img = Image.blend(img, glow.filter(ImageFilter.GaussianBlur(200)), 0.6); d = ImageDraw.Draw(img)
    t = "Telos"
    f = font(120, bold=True); tw = text_w(d, t, f)
    d.text(((W - tw)//2, 280), t, font=f, fill=TEXT)
    img.paste(grad_h(560, 8), ((W - 560)//2, 430))
    url = "github.com/arielagor/telos"
    uf = font(54, semi=True); uw = text_w(d, url, uf)
    d.text(((W - uw)//2, 480), url, font=uf, fill=CYAN)
    tag = "a goal-autonomous build  ·  human goal-setter + AI council"
    tf = font(32); tw2 = text_w(d, tag, tf)
    d.text(((W - tw2)//2, 590), tag, font=tf, fill=MUTED)
    save(img, "slide-b16.png")


def s_metta_live():  # slide-b20 — the named module rules + a NAL deduction derive in OmegaClaw's engine
    img, d, y = base("update | runs in OmegaClaw's MeTTa engine",
                     "The goal module derives in OmegaClaw's PeTTa engine")
    lh = [90, y + 30, 1170, H - 150]
    rounded(d, lh, 18, fill=SURFACE)
    d.text((130, y + 54), "named rules from lib_telos_goals.metta, run in singularitynet/omegaclaw:latest",
           font=font(24, semi=True), fill=MUTED)
    rows = [
        ("telos-conflicts", "(conflict-between alice-train dao-fair-access)"),
        ("telos-collective-goals", "(collective-goal dao-fair-access dao)"),
        ("telos-blocked", "(blocked dao-fair-access on gpu-quota)"),
        ("|-nal  (NAL deduction)", "((--> alice-train needs-reconciliation) (stv 1.0 0.81))"),
    ]
    yy = y + 116
    for rule, res in rows:
        d.text((130, yy), rule, font=font(27, bold=True), fill=CYAN)
        d.text((150, yy + 40), "-> " + res, font=font(26), fill=GREEN)
        yy += 100
    d.text((130, H - 192), "PeTTa / SWI-Prolog MeTTa engine  |  full log: results/omegaclaw-metta-load.log",
           font=font(23), fill=MUTED)
    rh = [1210, y + 30, W - 90, H - 150]
    rounded(d, rh, 18, fill=SURFACE)
    d.text((1250, y + 58), "What this shows", font=font(31, bold=True), fill=PINK)
    bullets(d, ["the named rules fire in OmegaClaw's runtime, not the reference Hyperon interpreter",
                "telos-blocked (nested match + if) runs clean, so PR #218 is proven, not just parsed",
                "a NAL deduction over goal terms computes a real truth value (conf 0.9*0.9 = 0.81)"],
            1250, y + 116, 560, size=25, gap=18, dot=GREEN)
    d.text((1250, y + 372), "Honest bound", font=font(31, bold=True), fill=MUTED)
    bullets(d, ["atoms asserted explicitly (the example graph), not yet auto-extracted from free text",
                "the conflict rules are pattern-matching; the NAL step is one hand-built inference"],
            1250, y + 430, 560, size=25, gap=18, dot=MUTED)
    save(img, "slide-b20.png")


def s_pr():  # slide-b21 — open, additive upstream PR to OmegaClaw-Core
    img, d, y = base("update | offered upstream",
                     "An open upstream PR to OmegaClaw-Core")
    box = [90, y + 36, W - 90, H - 160]
    rounded(d, box, 18, fill=SURFACE)
    d.text((140, y + 64), "asi-alliance / OmegaClaw-Core   #218", font=font(36, bold=True), fill=CYAN)
    pill = [W - 320, y + 58, W - 140, y + 114]
    rounded(d, pill, 28, fill=GREEN)
    d.text((W - 288, y + 70), "OPEN", font=font(30, bold=True), fill=BG)
    d.text((140, y + 140), "Add opt-in  lib_telos_goals.metta  (goal / conflict atoms)",
           font=font(34, semi=True), fill=TEXT)
    bullets(d, [
        "Additive only: one new lib_*.metta module, zero edits to the core loop",
        "Opt-in and side-effect-free: default behaviour unchanged unless imported",
        "Ships the same named rules just proven to derive in the live engine",
    ], 150, y + 212, W - 320, size=32, gap=20, dot=VIOLET)
    fb = [130, H - 300, W - 130, H - 200]
    rounded(d, fb, 14, fill=SURFACE2)
    d.text((160, H - 286), "+  lib_telos_goals.metta        +  usage doc", font=font(30, bold=True), fill=GREEN)
    d.text((160, H - 244), "lib_omegaclaw.metta | run.metta | src/        0 changes", font=font(28), fill=MUTED)
    bx = [90, H - 150, W - 90, H - 70]
    rounded(d, bx, 14, fill=SURFACE2)
    d.text((130, H - 138), "github.com/asi-alliance/OmegaClaw-Core/pull/218", font=font(30, bold=True), fill=CYAN)
    d.text((130, H - 102), "open | MIT, same as OmegaClaw | awaiting maintainer review",
           font=font(26), fill=MUTED)
    save(img, "slide-b21.png")


def s_ladder():  # slide-b22 — where the goal module runs now; retires this deck's own caveats
    img, d, y = base("update | where it stands now",
                     "Three rungs lit since this deck was recorded")
    cy = y + 170
    node(d, 420,  cy, 360, 130, "Hyperon", "unit test (CI)", accent=CYAN)
    node(d, 960,  cy, 360, 130, "live engine", "named rules + NAL", accent=GREEN)
    node(d, 1500, cy, 360, 130, "OmegaClaw-Core", "PR #218 open", accent=VIOLET)
    arrow(d, (600, cy), (780, cy),  color=MUTED, width=5)
    arrow(d, (1140, cy), (1320, cy), color=MUTED, width=5)
    d.text((250, cy + 110), "Hyperon CI was the only rung lit when this deck was recorded.",
           font=font(29, semi=True), fill=GREEN)
    rb = [90, cy + 175, W - 90, cy + 330]
    rounded(d, rb, 16, fill=SURFACE)
    d.text((130, cy + 196), "Retires two lines from this deck:", font=font(29, bold=True), fill=PINK)
    d.text((130, cy + 246), "\"not yet in a live OmegaClaw\"   ->   derives in the live engine",
           font=font(28), fill=TEXT)
    d.text((130, cy + 288), "\"MeTTa not yet running inside OmegaClaw\"   ->   loads + fires there now",
           font=font(28), fill=TEXT)
    d.text((130, H - 150),
           "Still open: Level 3, wire the benchmark into OmegaClaw's Autotests/ as a regression gate.",
           font=font(27, semi=True), fill=MUTED)
    save(img, "slide-b22.png")


if __name__ == "__main__":
    s01(); s01b(); s02(); s03(); s04(); s05(); s06(); s07(); s08(); s09(); s10(); s11(); s12(); s13(); s14()
    s_live(); s_setup(); s_article()
    s_metta_live(); s_pr(); s_ladder()   # NEW: live engine derivation + open PR #218 + status ladder
    s15()
    print("done -> cutaways/")
