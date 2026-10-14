# Paper evidence contract

One JSON file per paper slug. This supplements the existing public project metadata. Authors must read the full public paper, including tables, figures and appendices, and write a separate local digest (outside this Git repository) documenting the full evidence inventory. Values in public result tables must be transcribed from a specified source table, never guessed from graph pixels.

Required structure:
```
{
  "slug": "ae-psl",
  "problem": "One crisp sentence identifying the concrete constraint.",
  "contribution": "One crisp sentence identifying what is new.",
  "reading_guide": "One sentence explaining how to read the results.",
  "diagram": {
    "type": "pipeline | alternatives | cycle | comparison",
    "title": "Short descriptive title",
    "description": "Accessible description of the full method topology.",
    "stages": [
      {"title": "Short title (under 5 words)", "detail": "One sentence under 18 words", "icon": "encoder", "location": "Client | Server | Preparation | Evaluation | etc", "items": ["Optional short component", "Other component"]}
    ],
    "connections": ["Short relationship between stages"],
    "footnote": "Critical boundary or note, including whether alternatives are not a pipeline."
  },
  "results": [
    {
      "title": "Short evidence title",
      "question": "The question this experiment answers",
      "context": "Dataset, model, settings, metric/unit and whether higher/lower is better",
      "source": {"label": "Table 1 · page 6", "url": "https://source.pdf#page=6"},
      "columns": ["Method", "Metric (%)", "Other metric"],
      "rows": [{"label": "Exact method/setting", "values": ["89.2 ± 0.3", "10.2×"], "highlight": true}],
      "interpretation": "Specific takeaway bounded to this setting",
      "caveat": "Relevant limitation or comparability constraint",
      "chart": {"metric": "Accuracy (%)", "column": 0, "min": 0, "max": 100, "higher_is_better": true}
    }
  ],
  "evaluation": [{"label": "Data", "value": "Datasets"}, {"label": "Models", "value": "..."}, {"label": "Compared with", "value": "..."}],
  "limitations": ["2-4 precise paper-grounded evaluation boundaries"],
  "takeaways": ["2-3 compact explanations of what readers should learn"],
  "evidence_inventory": {"tables": 3, "figures": 4, "source_url": "https://...", "version": "Exact version used"}
}
```

Diagram: 3-5 stages preferred. `items` optional. Types preserve topology: `alternatives` is not sequential; `comparison` is side-by-side independent routes; `pipeline` has a directional flow; `cycle` adds an explicit return path. Connections length should be stages minus one for a pipeline/cycle; otherwise omit or use empty list. Available conceptual icons: data, database, labeled, unlabeled, noisy-labels, image, audio, waveform, text, video, sensor, client, clients, server, cloud, edge, chip, gpu, memory, network, upload, download, exchange, aggregate, split, merge, compress, codebook, cluster, mask, filter, model, layers, encoder, decoder, autoencoder, transformer, embedding, tokens, teacher, student, distill, frozen, train, adapt, task, task-vector, align, target, privacy, shield, lock, key, encrypt, unlearn, fingerprint, attack, trigger, check, warning, scale, speed, energy, chart, table, compare, accuracy, globe, language, speaker, emotion, search, book, paper, code, citation. Root will implement these.

Results: 1-3 compact table panels per paper, 3-8 rows each, sourced from exact tables. Select informative comparisons and explain selection. Chart is optional and only for fully numeric comparable values in one column; do not combine incompatible settings or infer numeric values from graphics. Preserve uncertainty in the cells. Use a qualitative table with explicit labels when the paper has no reliable tabulated quantitative data. Do not invent aggregate results. Source must match current paper version; older/later related work is separately labeled. JSON contains public evidence only, no local file paths.
