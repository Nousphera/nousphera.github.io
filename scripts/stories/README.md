# Paper walkthroughs

The thirteen records in these modules complement FedLN’s dedicated tour. Each group exports `STORIES`, keyed by the public project slug. Build with `python3 scripts/build_projects.py`.

## Visual structure

Each method has a connected sequence of five or six stages. Keep the relevant clients, server, inputs, and model identities consistent across the sequence. Non-federated methods use their actual training and inference roles. Use compact keyword labels, a clear visual hierarchy, and the shared vector vocabulary in `research_icons.py`.

Each step supplies `short_title`, `title`, `caption`, `art`, `title_in_art`, and `duration_ms`. Artwork is a self-contained, accessible HTML/SVG group. Responsive grids reflow on phones; colors use theme variables. Colors and patterns must track the same values, modalities, and roles throughout a method.

## Playback and accessibility

Use `data-reveal` for causal disclosure. Every part must appear at least one second before the stage ends. Stage durations range from 5–20 seconds. Motion begins after visible entry, pauses offscreen or in inactive tabs, and respects manual control. Concealed parts wait before animating. Manual selection and reduced-motion preferences show the complete stage; static fallback remains readable without JavaScript.

Keep visible text focused on operations, roles, and essential settings. Put detailed descriptions and explanatory-number context in accessible descriptions. Preserve scientific boundaries in the Method section and source notes. Do not turn explanatory values into reported measurements.

## Validation

Run `python3 -m unittest discover -s tests` and `node --test tests/*.test.cjs`. Check arithmetic and data boundaries, role and transfer direction, icon meaning, stage labels, stable heights, keyboard controls, reduced motion, expanded diagrams, and all stages at phone/tablet/desktop widths in both themes. Quantitative results remain in the separately audited `data/insights` tables.
