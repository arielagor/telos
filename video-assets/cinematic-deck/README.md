# Telos cinematic web deck (DEEP-Projects themed)

A scroll-driven, deck-navigable single-file slideshow of the same content as
`telos-deck.pdf`, restyled in the DEEP Projects house look. Built with the
`cinematic-deck` skill. Hosted at **https://agor.me/telos** (served from
`agor.me` repo `public/telos/index.html`).

## Source
- `deep-theme.json` — DEEP palette + fonts (Orbitron display, DM Sans body,
  violet/magenta/cyan on near-black). Tokens applied to the template by the
  skill's `build_theme.mjs` (WCAG-checked).
- `sections.html` — the 13 cinematic sections (hero, the gap, three failure
  rungs, the goal graph, the benchmark, the live 0.620 run, the live-engine
  derivation + NAL, the open PR #218, the article demo, the honest-limits
  cards, the close). Mirrors the 22-slide narrative.

## Rebuild
```bash
SK=~/.claude/skills/cinematic-deck
python -c "import re;b=open(f'{__import__(\"os\").path.expanduser(\"~\")}/.claude/skills/cinematic-deck/templates/base.html').read();f=open('sections.html').read().strip();open('built.html','w').write(re.sub(r'<main id=\"snap\".*?</main>',lambda m:f,b,1,flags=re.S))"
node $SK/scripts/build_theme.mjs --theme deep-theme.json --html built.html --out ../../../agor.me/public/telos/index.html
```
Then commit `public/telos/index.html` in the agor.me repo (a buildable path, so
Netlify redeploys). Keep `sections.html` in sync with `make_slides.py` content.
