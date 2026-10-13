# Project content contract

One JSON file per slug. Each field below is required except `secondary_figure` and `related`.

```
{
  "slug": "fedln", "library_id": "2024-fedln", "name": "FedLN",
  "title": "Exact paper title", "year": 2024, "venue": "ACM TIST", "type": "Journal",
  "authors": ["Full Author", "..."],
  "tagline": "Clear short one-line idea, ideally under 12 words",
  "summary": "Two compact sentences explaining problem and approach (45-65 words)",
  "category": "Efficient learning",
  "topics": ["Label noise", "Federated learning"],
  "accent": "#2459a6", "accent_dark": "#9abcff", "tint": "#edf3fc",
  "links": {"Paper": "https://...", "Code": "https://..."},
  "figure": {"src": "assets/projects/fedln/overview.webp", "width": 1500, "height": 800, "alt": "Specific useful description", "caption": "Concise stand-alone interpretation", "source_label": "Figure 1 in the paper", "source_url": "https://...", "page": 3},
  "method": [{"title": "Short step", "text": "One or two clear sentences"}],
  "findings": [{"title": "Short heading", "text": "Source-bound qualitative finding or accurately scoped quantitative one"}],
  "abstract": "Verified public abstract text, clean unicode",
  "bibtex": "@article{...}",
  "related": [{"label": "Earlier workshop version · NeurIPS 2022", "url": "https://..."}],
  "provenance": {"source_url": "https://...", "figure_note": "Crop from public PDF, page N; no labels/data modified.", "content_pages": [1,3,4]}
}
```

Use 3 concise method steps and 2 findings if supported. Categories: Efficient learning, Reliable learning, Private learning, Speech & audio. All resource URLs public. No private absolute file paths in JSON. If copying a source figure is unsuitable, author a faithful simple SVG conceptual diagram and explicitly label it as an explanatory schematic based on the paper; still render and inspect it. Do not invent quantitative results. Full authors and citation must match source; workshop venue must stay workshop. Main catalog is authoritative starting point, read paper to verify. Do not include markdown in ordinary text fields.

Optional additions: `keywords` extends gallery search; `abstract_source` contains a public `url`, a short `label` and optional version `note`; `social_image` selects a raster Open Graph preview when the main figure is SVG. A conference display year may differ from the BibTeX publication year; scholarly HTML metadata follows BibTeX.
