# Project pages verification

## Content

All 14 public paper projects have source-grounded methods, findings, abstracts, full authors and BibTeX. Each original paper figure crop was rendered and visually inspected. FedLN additionally has an inspected original SVG schematic of its three alternative intervention stages. Nine Code links were checked with GitHub's unauthenticated API and resolve to public, non-archived repositories.

Version distinctions remain explicit: FedLN/FedSTAR use final journal sources; DeltaMask uses the accepted manuscript and separates BigData 2024 from publication year 2025; FiBA similarly separates event and proceedings years. Preprint-derived abstracts identify their source. No private drafts or private repository details are published.

## Automated checks

- 8 Python checks cover all 14 records, HTML/JSON escaping, public source/resource URLs, visible abstract version notes, citation dates, static content, search metadata, local pages/resources and fragment targets.
- 5 Node checks cover theme restoration/cycling with blocked storage, intersecting multiword/category search, clipboard success and manual-copy fallback.
- 30 existing personal-site checks pass after adding project links.
- Figure dimensions were verified against image assets; accent text contrast exceeds 4.5:1 in both themes.

## Browser review

All 14 project pages were loaded and visually inspected in Chrome. Desktop, 320px and 390px phone widths, and a 768px tablet viewport were reviewed using Chrome's responsive preview. These are emulated layouts, not physical-device tests. Checked automatic and explicit themes, gallery keyword filtering, full-size figure dialog and Escape, and citation copying with visible confirmation. The citation control now retains keyboard focus after copying. Scientific figures keep their original white canvas in dark mode.

Local sources, full-text PDF libraries and unpublished manuscripts remain outside these websites.

## Deployment

Nousphera implementation commit `ac9b944` passed its validation workflow and GitHub Pages deployment. All 52 checked public HTML pages, citations, figures, shared styles/scripts/fonts and sitemap returned content identical to the local files. The published FedLN page was also inspected in Chrome with automatic theme selection.

Personal-site commit `c46c0f2` deployed successfully. Its live homepage matched the local file and contained all 14 individual project links plus the project-gallery link.
