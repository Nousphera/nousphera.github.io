"""Source-grounded FedLN project panels; load /assets/fedln-content.css.

The numeric series below are transcribed from the final ACM TIST article:
Figure 8 (publisher PDF p24) and selected columns of Table 3 (PDF p20).
PDF page numbers include the repository cover. The original scatter images
are Figure 7 (PDF p19), also present unchanged in the archived 2022 poster.
"""

from html import escape


_PDF = "https://pure.tue.nl/ws/portalfiles/portal/320106480/3626242.pdf"
_OURS = {"NNC", "AKD", "AKD (embeddings)", "NA-FedAvg"}
_HUMAN = (
    ("FedAvg", "65.68", "47.25"),
    ("CL", "67.31", "48.72"),
    ("FedCorr", "70.02", "54.12"),
    ("NNC", "74.69", "55.39"),
    ("AKD", "70.39", "57.39"),
    ("NA-FedAvg", "70.06", "53.99"),
)
_SYNTHETIC = (
    ("FedAvg", "57.65", "63.54"),
    ("FedCorr", "67.27", "65.23"),
    ("NNC", "74.76", "54.59"),
    ("AKD (embeddings)", "68.43", "68.39"),
    ("NA-FedAvg", "65.34", "67.92"),
)


def _source(p, label, page):
    url = p.get("links", {}).get("PDF", _PDF).split("#", 1)[0]
    return (f'<a class="fl-source" href="{escape(url, quote=True)}#page={page}">'
            f'{escape(label)}</a>')


def _math(label, body):
    return (f'<div class="fl-equation"><math xmlns="http://www.w3.org/1998/Math/MathML" '
            f'display="block" aria-label="{escape(label, quote=True)}">{body}</math></div>')


def overview_markup(p):
    """A nontechnical introduction, followed by the tour integration point."""
    abstract = escape(p.get("abstract", ""))
    return f'''<section id="overview" data-tab-panel class="fl-panel fl-overview" aria-labelledby="fl-overview-title">
  <div class="fl-intro">
    <p class="fl-eyebrow">At a glance</p>
    <h2 id="fl-overview-title">Three ways to limit label noise</h2>
    <p class="fl-lead">Federated learning keeps data on clients, but <strong>incorrect labels can affect the shared model.</strong> FedLN estimates client noise and offers three places to intervene.</p>
  </div>
  <!-- FEDLN_TOUR -->
  <div class="fl-overview-note"><p><strong>Choose an intervention to fit the data and device.</strong> Label patterns, pretrained representations and available computation determine which route is useful.</p></div>
  <details class="fl-details fl-abstract"><summary>Read the published abstract</summary><div class="fl-details-body"><p>{abstract}</p><p>{_source(p, 'Published article · abstract', 2)}</p></div></details>
</section>'''


def method_markup(p):
    """Method mechanisms and accessible native MathML; no runtime dependency."""
    nnc = _math(
        "The corrected label is the class receiving the most votes among the k nearest other local embeddings.",
        '''<mrow><msub><mover><mi>y</mi><mo>~</mo></mover><mi>i</mi></msub><mo>=</mo>
        <munder><mo>arg max</mo><mi>c</mi></munder>
        <munder><mo>∑</mo><mrow><mi>j</mi><mo>∈</mo><msub><mi mathvariant="script">N</mi><mi>k</mi></msub><mo>(</mo><mi>g</mi><mo>(</mo><msub><mi>x</mi><mi>i</mi></msub><mo>)</mo><mo>)</mo></mrow></munder>
        <mrow><mn mathvariant="bold">1</mn><mo>[</mo><msub><mi>y</mi><mi>j</mi></msub><mo>=</mo><mi>c</mi><mo>]</mo></mrow></mrow>''')
    akd = _math(
        "Adaptive distillation loss equals cross-entropy plus beta times a client-noise gate times the teacher loss.",
        '''<mrow><msub><mi mathvariant="script">L</mi><mtext>AKD</mtext></msub><mo>=</mo><msub><mi mathvariant="script">L</mi><mtext>CE</mtext></msub><mo>+</mo><mi>β</mi><msub><mi>u</mi><mi>ε</mi></msub><mo>(</mo><msubsup><mi>n</mi><mi>l</mi><mi>m</mi></msubsup><mo>)</mo><msub><mi mathvariant="script">L</mi><mtext>KD</mtext></msub></mrow>''')
    na = _math(
        "Client m's aggregation weight equals its estimated clean-label fraction times its share of all training samples.",
        '''<mrow><msub><mi>γ</mi><mi>m</mi></msub><mo>=</mo><mo>(</mo><mn>1</mn><mo>−</mo><msubsup><mi>n</mi><mi>l</mi><mi>m</mi></msubsup><mo>)</mo><mfrac><msub><mi>N</mi><mi>m</mi></msub><mi>N</mi></mfrac></mrow>''')
    return f'''<section id="method" data-tab-panel class="fl-panel fl-method" aria-labelledby="fl-method-title">
  <div class="fl-intro"><p class="fl-eyebrow">The method</p><h2 id="fl-method-title">How it works</h2><p class="fl-lead">NNC changes labels, AKD changes local training, and NA-FedAvg changes server aggregation. Each uses a client-specific estimate of label noise.</p></div>
  <article class="fl-method-card fl-method-nnc" aria-labelledby="fl-nnc-title">
    <header class="fl-method-heading"><span class="fl-method-code">NNC</span><div><h3 id="fl-nnc-title">Nearest Neighbor-based Correction</h3><p class="fl-stage">At initialization · correct the labels</p></div></header>
    <div class="fl-method-grid"><div class="fl-method-copy"><p>A <strong>pretrained encoder</strong> maps each client’s examples into an embedding space. Nearby examples vote on the label. When that vote disagrees with the stored label, NNC <strong>replaces the label</strong> before federated training.</p><p>Examples and embeddings stay fixed. The fraction of disagreements also supplies a local noise estimate.</p></div><div class="fl-formula-card">{nnc}<p class="fl-formula-meaning">Count one vote per neighbor; keep the most frequent class.</p><dl class="fl-definitions"><div><dt><var>g</var></dt><dd>Pretrained feature encoder.</dd></div><div><dt><var>N</var><sub>k</sub></dt><dd>Indices of the <var>k</var> nearest other local embeddings by Euclidean distance.</dd></div><div><dt><var>y</var><sub>j</sub></dt><dd>The neighbor’s observed label; tied votes are broken randomly.</dd></div></dl></div></div>
    <p class="fl-method-boundary">Useful embeddings help, but a neighborhood dominated by the wrong class can still vote incorrectly.</p>
    <details class="fl-details"><summary>Noise estimation and source</summary><div class="fl-details-body"><p>The encoder is used locally during initialization. The per-client noise estimate is the number of vote–label mismatches divided by the client’s sample count. The displayed voting rule is a compact restatement, with repeated labels counted separately.</p><p>{_source(p, 'Equation 5 · embedding-based noise estimation', 8)} · {_source(p, 'Section 4.3.1 · label correction', 10)}</p></div></details>
  </article>
  <article class="fl-method-card fl-method-akd" aria-labelledby="fl-akd-title">
    <header class="fl-method-heading"><span class="fl-method-code">AKD</span><div><h3 id="fl-akd-title">Adaptive Knowledge Distillation</h3><p class="fl-stage">During local training · add teacher guidance</p></div></header>
    <div class="fl-method-grid"><div class="fl-method-copy"><p>AKD keeps the <strong>observed labels</strong> and adds a <strong>teacher loss</strong> for clients with detected label noise. The teacher supplies pretrained embeddings or predictions from the aggregated global model.</p><p>The local model learns from its labels and this additional supervision in one combined objective.</p></div><div class="fl-formula-card">{akd}<p class="fl-formula-meaning">Add teacher guidance when the client’s noise estimate activates it.</p><dl class="fl-definitions"><div><dt>CE / KD</dt><dd>Cross-entropy label loss / knowledge-distillation teacher loss.</dd></div><div><dt><var>n</var><sub>l</sub><sup>m</sup>, <var>u</var><sub>ε</sub></dt><dd>Client <var>m</var>’s estimated noise and its threshold-based gate.</dd></div><div><dt><var>β</var></dt><dd>Controls the teacher loss’s contribution.</dd></div></dl></div></div>
    <p class="fl-method-boundary">The teacher is extra supervision; it does not force a potentially incorrect replacement label.</p>
    <details class="fl-details"><summary>Teacher losses and source</summary><div class="fl-details-body"><p>Embedding supervision uses mean absolute error. Global-model supervision uses Kullback–Leibler divergence between temperature-scaled outputs. The reported results on this page use embedding supervision.</p><p>{_source(p, 'Equation 9 · adaptive knowledge distillation', 12)}</p></div></details>
  </article>
  <article class="fl-method-card fl-method-na" aria-labelledby="fl-na-title">
    <header class="fl-method-heading"><span class="fl-method-code">NA-FedAvg</span><div><h3 id="fl-na-title">Noise-aware Federated Averaging</h3><p class="fl-stage">At server aggregation · reweight client updates</p></div></header>
    <div class="fl-method-grid"><div class="fl-method-copy"><p>After a warm-up period, clients compute energy scores using their local and global models. The server uses the scores to estimate each client’s label-noise level <strong>once</strong>.</p><p>Later rounds <strong>reuse those estimates</strong>: a client’s data share is multiplied by its estimated clean-label fraction.</p></div><div class="fl-formula-card">{na}<p class="fl-formula-meaning">Noisier clients contribute less to the shared model.</p><dl class="fl-definitions"><div><dt><var>γ</var><sub>m</sub></dt><dd>Client <var>m</var>’s aggregation weight.</dd></div><div><dt><var>N</var><sub>m</sub> / <var>N</var></dt><dd>Its share of all training samples.</dd></div><div><dt>1 − <var>n</var><sub>l</sub><sup>m</sup></dt><dd>Its estimated fraction of clean labels.</dd></div></dl></div></div>
    <p class="fl-method-boundary">This avoids a separate pretrained encoder, but still depends on distinguishing relatively reliable clients.</p>
    <details class="fl-details"><summary>One-time estimation and source</summary><div class="fl-details-body"><p>Energy scores come from the model’s output logits. Score computation and communication occur in the designated estimation round; subsequent rounds continue local training and noise-aware aggregation. The equation reproduces the paper’s weight without adding a normalization term.</p><p>{_source(p, 'Section 4.3.3 · aggregation weight', 13)} · {_source(p, 'Figure 4 · one-time score exchange', 14)}</p></div></details>
  </article>
</section>'''


def _table(columns, rows, caption):
    headings = ''.join(f'<th scope="col">{escape(str(c))}</th>' for c in columns)
    body = []
    for row in rows:
        cells = ''.join(f'<td>{escape(str(v))}</td>' for v in row[1:])
        body.append(f'<tr><th scope="row">{escape(str(row[0]))}</th>{cells}</tr>')
    return (f'<div class="fl-table-wrap"><table class="fl-data-table"><caption>{escape(caption)}</caption>'
            f'<thead><tr>{headings}</tr></thead><tbody>{"".join(body)}</tbody></table></div>')


def _paired_charts(key, headings, rows):
    charts = []
    for index, heading in enumerate(headings, 1):
        bars = []
        for row in rows:
            own = ' fl-bar-row-own' if row[0] in _OURS else ''
            route = {'NNC': 'nnc', 'AKD': 'akd', 'AKD (embeddings)': 'akd', 'NA-FedAvg': 'na'}.get(row[0])
            if route:
                own += f' fl-bar-{route}'
            label = 'AKD' if row[0] == 'AKD (embeddings)' else row[0]
            value = row[index]
            bars.append(f'''<div class="fl-bar-row{own}" data-chart="{escape(key, quote=True)}" data-series="{escape(heading, quote=True)}" data-method="{escape(row[0], quote=True)}" data-value="{value}"><span class="fl-bar-label">{escape(label)}</span><span class="fl-bar-track"><span class="fl-bar-fill" style="--fl-value:{value}%"></span></span><span class="fl-bar-value">{value}</span></div>''')
        charts.append(f'''<div class="fl-chart-panel"><h4>{escape(heading)}</h4><div class="fl-chart-scale"><span>0</span><span>50</span><span>100%</span></div>{''.join(bars)}</div>''')
    # Exact numbers are available in the adjacent semantic table. Hide the
    # decorative chart layout from assistive technology to avoid duplication.
    return (f'<div class="fl-chart-pair" aria-hidden="true">{"".join(charts)}</div>'
            '<p class="fl-chart-legend"><span>FedLN:</span>'
            '<span class="fl-legend-item"><i class="fl-legend-swatch fl-swatch-nnc" aria-hidden="true"></i>NNC</span>'
            '<span class="fl-legend-item"><i class="fl-legend-swatch fl-swatch-akd" aria-hidden="true"></i>AKD</span>'
            '<span class="fl-legend-item"><i class="fl-legend-swatch fl-swatch-na" aria-hidden="true"></i>NA-FedAvg</span>'
            '<span>Shared 0–100% scale.</span></p>'
            f'<details class="fl-details fl-chart-data"><summary>View exact values</summary>'
            f'{_table(("Method", *headings), rows, "Test accuracy (%); higher is better")}</details>')


def _more_experiments(p):
    experiments = p.get("insight", {}).get("results", [])[1:]
    if not experiments:
        return ''
    parts = []
    for result in experiments:
        rows = [(r['label'], *r['values']) for r in result['rows']]
        source = result['source']
        parts.append(f'''<section class="fl-extra-experiment"><h3>{escape(result['title'])}</h3><p class="fl-context">{escape(result['context'])}</p>{_table(result['columns'], rows, result['title'])}<p>{escape(result['interpretation'])}</p><p class="fl-context">{escape(result['caveat'])}</p><a class="fl-source" href="{escape(source['url'], quote=True)}">{escape(source['label'])}</a></section>''')
    return f'<details class="fl-details fl-more"><summary>More experiments · audio and noisy-client populations</summary><div class="fl-details-body">{"".join(parts)}</div></details>'


def results_markup(p):
    """Two comparable chart pairs, the original label illustration and sources."""
    limitations = p.get('insight', {}).get('limitations', ())
    limits = ''.join(f'<li>{escape(item)}</li>' for item in limitations)
    return f'''<section id="findings" data-tab-panel class="fl-panel fl-results" aria-labelledby="fl-results-title">
  <div class="fl-intro"><p class="fl-eyebrow">The evidence</p><h2 id="fl-results-title">Different noise, different strengths</h2><p class="fl-lead">The strongest intervention changes with the dataset and the pattern of label errors.</p></div>
  <section class="fl-result-block" aria-labelledby="fl-human-title"><div class="fl-result-heading"><div><p class="fl-eyebrow">Human annotation errors</p><h3 id="fl-human-title">NNC leads on CIFAR-10N; AKD on CIFAR-100N</h3></div><span class="fl-result-unit">Test accuracy (%)</span></div>
    {_paired_charts('human', ('CIFAR-10N', 'CIFAR-100N'), _HUMAN)}
    <p class="fl-result-insight"><strong>+10.14 percentage points</strong> for AKD over FedAvg on CIFAR-100N (57.39% vs 47.25%).</p>
    <p class="fl-context">Three-run means; 30 clients, 80% participation. CIFAR-10N: 200 rounds; CIFAR-100N: 500 rounds. AKD uses embeddings. CL denotes confident learning.</p>
    <p>{_source(p, 'Figure 8 · human-noise results', 24)}</p>
    <details class="fl-details"><summary>Experimental context</summary><div class="fl-details-body"><p>Human-annotated training sets are randomly distributed across clients; evaluation uses the original clean test sets. There is no explicit clean-client group. Training uses one local epoch and 25% data-distribution variance. The figure reports no dispersion or error bars.</p></div></details>
  </section>
  <section class="fl-result-block" aria-labelledby="fl-synthetic-title"><div class="fl-result-heading"><div><p class="fl-eyebrow">A controlled comparison · CIFAR-10</p><h3 id="fl-synthetic-title">The same noise rate can produce opposite outcomes</h3></div><span class="fl-result-unit">Test accuracy (%)</span></div>
    {_paired_charts('synthetic', ('Random noise', 'Class flipping'), _SYNTHETIC)}
    <p class="fl-result-insight"><strong>NNC gains 17.11 points under random noise</strong>, yet falls below FedAvg under class flipping (54.59% vs 63.54%).</p>
    <p class="fl-context">ResNet-20; 70% label noise on 80% of 30 clients; 200 rounds, one local epoch, 80% participation. Three-run means; AKD uses embeddings.</p>
    <p>{_source(p, 'Table 3 · PDF page 20 (22:19)', 20)}</p>
    <details class="fl-details"><summary>What changes between the columns?</summary><div class="fl-details-body"><p>Noise sparsity changes from 0% to 100% while the corruption rate stays at 70%. Random noise spreads wrong labels across classes; class flipping concentrates them. These accuracy comparisons do not establish equal computation: FedCorr includes additional preprocessing and fine-tuning. Trial dispersion is not reported.</p></div></details>
  </section>
  <figure class="fl-embedding-figure"><div class="fl-result-heading"><div><p class="fl-eyebrow">Inside label correction</p><h3>The points stay fixed. Their labels change.</h3></div></div><div class="fl-embedding-pair"><div><h4>Before NNC</h4><img src="/assets/projects/fedln/labels-before.png" width="1455" height="966" loading="lazy" decoding="async" alt="Fixed CIFAR-10 embeddings before correction: differently coloured labels are mixed within several visible clusters."></div><div><h4>After NNC</h4><img src="/assets/projects/fedln/labels-after.png" width="1455" height="966" loading="lazy" decoding="async" alt="The same embedding coordinates after NNC: neighboring points have more consistent class-label colours."></div></div><figcaption>CIFAR-10 with 40% random label noise; fixed CLIP features. This illustrates relabeling, not learning a new representation. {_source(p, 'Figure 7', 19)}</figcaption></figure>
  {_more_experiments(p)}
  <details class="fl-details fl-boundaries"><summary>How to interpret these results</summary><div class="fl-details-body"><p>The results come from simulated federated clients. They support comparisons of recognition accuracy; they do not establish equal runtime or energy cost on real devices.</p><ul>{limits}</ul></div></details>
  <div class="fl-takeaway"><p class="fl-eyebrow">Takeaways</p><h3>Choose for the noise pattern, not just its rate.</h3><p><strong class="fl-text-nnc">NNC</strong> can deliver large gains when local label votes are reliable. <strong class="fl-text-akd">AKD</strong> provides teacher guidance without replacing labels; <strong class="fl-text-na">NA-FedAvg</strong> limits noisier updates when client reliability can be distinguished.</p></div>
</section>'''
