# Nousphera

Public paper project pages for research in collaborative and efficient machine learning.

- [Project collection](https://nousphera.github.io/projects/)
- [Vasileios Tsouvalas](https://vtsouval.github.io/)

## Edit and preview

Edit the relevant record in `data/projects/` and its figures in `assets/projects/<slug>/`. See `data/projects/SCHEMA.md` for the content contract. Rebuild committed HTML and citations:

```sh
python3 scripts/build_projects.py
python3 -m unittest discover -s tests
node --test tests/*.test.cjs
python3 -m http.server 60660 --bind 127.0.0.1
```

Open `http://127.0.0.1:60660/projects/`. Use an HTTP server because asset paths are relative to the site root. Python 3.10+ and Node.js 18+ are sufficient; there are no build dependencies. Main-branch pushes publish through GitHub Pages; the validation workflow checks content and rebuild consistency.

## Structure

- `scripts/build_projects.py`: static HTML, citation, gallery and sitemap generator.
- `data/projects/*.json`: 14 public paper records, verified resources, summaries, abstracts, citations and figure provenance.
- `projects/<slug>/`: generated, independently shareable paper pages and BibTeX files.
- `assets/projects.css`, `assets/projects.js`, `assets/theme.js`: shared responsive design and progressive enhancements.
- `assets/fonts/`: self-hosted Open Sans, compressed to WOFF2; license in `OFL.txt`.
- `assets/publications.json`: compatibility catalog whose entries now link to the project pages.

## Editorial boundaries

Only public papers are represented. Workshop versions are linked separately from journal/conference versions. Display year can be a conference year; citation metadata follows the publication year. Abstract source labels distinguish preprints from final papers. Public code is linked only when verified.

Paper figure crops preserve the source labels/data and identify the figure and source. FedLN also has an original explanatory schematic; the paper's original diagram remains available on its page. Rights to source figures and abstracts remain with their respective owners. Source PDFs and private research drafts are not redistributed here.

Pages remain readable without JavaScript. Theme controls follow the system by default; figure links and BibTeX downloads have native fallbacks. Gallery search includes titles, authors, methods and paper keywords.
