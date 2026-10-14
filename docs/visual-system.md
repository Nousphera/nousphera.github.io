# Research visual system

The project pages separate full paper evidence from its visual presentation.

- `data/insights/<slug>.json`: source-bound result tables, settings, limitations, method topology and evidence-version metadata.
- `scripts/research_visuals.py`: accessible HTML diagrams, result charts, responsive tables and explanatory components.
- `scripts/research_icons.py`: 76 original icons on a 24px grid with rounded 1.6px strokes.
- `assets/research/icons/`: standalone SVG exports, with system-theme colors.
- `assets/research/catalog.json`: machine-readable icon inventory.
- `assets/research.css`: shared theme-aware visual styles.
- `assets/project-tabs.js`: progressively enhanced paper sections with keyboard controls and URL/history support.

Run `python3 scripts/export_research_icons.py` to regenerate the original SVGs and public JSON inventory. This dependency-free export is checked in CI. Original paper figures remain available through the Method tab.

## Reusable asset folders

Keep the larger research icon library outside this repository as folders with manifests. Its catalog joins original vectors, imported collections and any later acquisitions without changing their source bytes. Store a source URL or path, creator and collection, license/attribution notice, SHA256, semantic tags and any explicit adaptation relationships for each asset.

Retain raw originals. Save recolored, simplified or combined versions as new files and record their parent asset IDs; a similar visual concept does not establish derivation. Preserve source colors until an intentional adaptation is made. Unknown licenses remain internal, and any public reuse must preserve applicable attribution and license notices. No separate asset website is generated.

## Figure rules

Choose topology before decoration: a pipeline denotes a sequence, a cycle explicitly returns to its start, alternatives are independent choices, and comparisons do not imply execution order. Use known locations (client, server, preparation, evaluation), identify exchanged objects, and keep the crucial boundary in the figure caption. Do not depict security guarantees that the paper does not establish.

Use inline SVG icons and native text for sharpness and live theme adaptation. Do not invert scientific images. Mobile figures change layout while preserving logical reading order and all labels.

## Evidence rules

Preserve original values, uncertainty terminology, units, datasets, models, participation settings and source version. Tables are the canonical representation; optional bar charts require numeric comparable observations and a zero baseline. An inference or calculation must be identified. Do not estimate numerical values from plot pixels. Represent plot-only findings qualitatively with direct figure references.

Source inconsistencies belong in local audit notes; public selections must avoid ambiguous aggregates or explain the relevant boundary. A result on a device, dataset or threat model is not a universal guarantee.

## Reading and accessibility

Overview, Method, Results and Citation become ARIA tabs when JavaScript is available. Arrow keys and Home/End navigate the tab list. Direct links and browser history select the appropriate panel; printing exposes every section. Without JavaScript all content is visible. Original figures and citations retain native link/download fallbacks.
