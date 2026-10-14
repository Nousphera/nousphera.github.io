# Evidence and rendering verification — 14 October 2026

All 14 paper project pages have source-bound evidence records, native method compositions and four accessible reading tabs. Local and live verification are complete for release `1a7420e1c8d71e4031a793edba699cfc72ba9c87`.

## Paper evidence

Three parallel source audits examined 222 PDF pages covering 62 numbered tables and 86 figures, including experimental settings, reported uncertainty, limitations, appendices and version differences. Detailed reading notes and source inspection files remain in the external local research library. A separate evidence review checked the selected numerical results against their stated sources.

The generated public pages contain 37 result panels, 180 table rows, seven bar charts and 14 method compositions. These counts were independently recomputed from the 14 JSON records in `data/insights/`. Results retain source links and version labels; comparisons identify their datasets, metrics and settings. Plot-only findings remain qualitative. Bar charts use zero baselines and preserve reported uncertainty in their labels and tables.

The audit corrected or qualified ambiguous claims, including local epochs versus local steps, communication per round, model adaptation scope and the distinction between authorized decryption and formal deletion guarantees. Inconsistent source aggregates were excluded from selected comparisons. Private unpublished drafts were excluded.

## Automated checks

The following commands were rerun successfully on the current implementation:

```sh
python3 -m unittest discover -s tests
node --test tests/*.test.cjs
```

All 25 tests passed: 14 Python tests and 11 Node tests. Coverage includes complete paper and asset records, local links and fragments, safe text rendering, source metadata, numeric chart constraints, SVG structure, search and theme behavior, citation copying, tab semantics, keyboard navigation, history, print visibility and returning to the selected panel after a deep scroll.

## Browser checks

Browser QA covered 168 page/tab/viewport conditions: all 14 pages and all four tabs at each of these simulated viewports:

| Viewport | Theme |
| --- | --- |
| 390 × 844 | Light |
| 768 × 1024 | Light |
| 1280 × 900 | Dark |

In every condition, exactly one reading panel was visible, the page had no horizontal overflow and the tab navigation remained visible. Some short panels at tablet width could not place the navigation exactly at viewport coordinate zero because the browser clamped scrolling at the document bottom; the controls remained visible.

Additional visual and interaction checks covered FedLN on phone and desktop in both themes, AE-PSL results in dark mode, deep-scroll tab switching, arrow-key and Home/End navigation, browser history, and the original-figure modal. Print preview exposed all four panels with a readable light palette.

These checks used browser viewport simulation, not physical phones or tablets. They do not establish behavior in every browser or assistive technology.

## Independent implementation review

Review identified two defects that were corrected before the final test run:

- Switching tabs after scrolling deep into Results retained the old scroll position. The implementation now uses the selected panel's document position, adjusted for the tab bar height; a regression test and browser check confirmed the fix.
- Printing in dark mode retained dark surface tokens. Print styles now reset the shared palette to light colors; print preview confirmed all sections were readable.

No further actionable implementation defects were found in the reviewed panel structure, escaping, icon rendering, source tables, ARIA relationships or no-JavaScript fallback.

## Asset boundary

The public site contains the original research icon exports and their JSON inventory. The larger reusable collection stays outside the repository as asset folders and manifests, preserving source bytes, provenance and license information. The separate asset website and its generator were removed at the user's request; no asset browsing website is part of this release.

## Deployment

The release was pushed to `main`. Both [validation](https://github.com/Nousphera/nousphera.github.io/actions/runs/38537628302) and [GitHub Pages deployment](https://github.com/Nousphera/nousphera.github.io/actions/runs/38537627924) completed successfully for that commit. Live HTTP responses for all 14 paper pages, the research stylesheet, tab script and original icon inventory matched the local files byte for byte.

The live FedLN page was also checked in the browser: Method and Results selected the expected single panel; Results at 390 × 844 had no horizontal overflow and kept its tab bar at the top; Overview at 1280 × 900 rendered correctly in dark mode. The theme was returned to automatic and the temporary viewport override removed.
