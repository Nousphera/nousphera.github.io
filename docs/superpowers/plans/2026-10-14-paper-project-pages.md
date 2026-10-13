# Paper project pages implementation plan

**Goal:** Publish 14 compact, visually polished paper project pages under Nousphera and connect them from the personal publication catalog.

**Architecture:** Static HTML generated from one JSON record per paper. Shared, dependency-free CSS and JavaScript handle responsive layouts, automatic/light/dark themes, figure enlargement, citation copying and gallery filtering. Public paper figures remain faithful to their sources.

**Tech stack:** Python standard-library generator, HTML, CSS, JavaScript, local Open Sans fonts.

## Constraints and design
- Only the 14 public paper projects; no unpublished drafts, private repository inventory or non-paper software pages.
- Restrained paper-specific accent colors; spacious typography, concise explanations and resource links.
- Source-bound method descriptions, authors, venues, related versions and citations; no invented results or code availability.
- Figures have explicit provenance, useful alt text, intrinsic dimensions, a white canvas and full-resolution access.
- Mobile, tablet, keyboard navigation, reduced motion, no-JavaScript reading, automatic theme by default.

## Work
- [x] Create individual content records and inspect/render method figures from each public PDF in three independent groups.
- [x] Build shared static generator, page template, gallery, CSS, theme and accessible figure/citation controls.
- [x] Validate all records, source/asset paths, local links, metadata, citation files and generated reproducibility.
- [x] Render project pages and gallery in the browser; inspect light/dark and narrow layouts.
- [x] Review content and implementation, resolve findings, connect personal site and publish both repositories.
- [x] Verify successful deployments and live project resources.

## Review focus
- Workshop vs main-conference and preprint vs final-version venue metadata.
- Broken or private code links and accidentally published internal source paths.
- Wide figures on small screens and white scientific figures in dark themes.
- Blocked browser storage/clipboard, reduced motion and keyboard-only figure closing.
- HTML escaping, canonical URLs, static content without JS and page-generator determinism.
