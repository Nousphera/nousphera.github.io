# Paper walkthroughs

The thirteen paper records in these modules complement FedLN's dedicated walkthrough. Each exports `STORIES`, keyed by the public project slug. Build pages with `python3 scripts/build_projects.py`.

Each story includes a short overview, three contributions, three to five illustrated steps, technical method cards, and takeaways. Steps have a compact `short_title` for controls, a full title/caption, and a self-contained accessible SVG. `story_art.py` provides theme-aware drawing primitives; custom artwork explains each paper's actual operations.

Use `sa-accent`, `sa-secondary`, `sa-muted` and `sa-warn` instead of fixed colors. Artwork uses a 600 × 300 viewBox and readable labels. Wrap progressive elements in `data-reveal` groups with times below 5000 ms. A scene lasts six seconds; manual selection and reduced-motion mode reveal its complete diagram. No JavaScript is required to read the scenes. The shared controller pauses offscreen and respects manual control.

Prose permits only `strong`, `em`, `sub`, `sup`, `code`, and `br` markup. Equations use native MathML. Keep numerical evidence in the audited `data/insights` tables; the renderer selects explicit columns and retains exact values, uncertainty, missing cells, units, and source links. Never turn a schematic into a claimed measurement or mix publication versions.

Validate with `python3 -m unittest discover -s tests` and `node --test tests/*.test.cjs`. Check every new scene at phone width in both themes, including text bounds and enlarged-diagram controls.
