"""FedLN overview and methodology panels, based on the final ACM TIST article.

Results use the shared paper_results renderer and audited JSON selections.
"""
from html import escape

from research_icons import research_icon


_PDF = "https://pure.tue.nl/ws/portalfiles/portal/320106480/3626242.pdf"
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
  <div class="fl-overview-note"><p><strong>Choose an intervention to fit the data and device.</strong></p><p><strong>Label patterns</strong>, <strong>pretrained representations</strong> and <strong>available computation</strong> determine which route is useful.</p></div>
  <details class="fl-details fl-abstract"><summary>Abstract</summary><div class="fl-details-body"><p>{abstract}</p><p>{_source(p, 'Read more', 2)}</p></div></details>
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
  <div class="fl-intro"><p class="fl-eyebrow">The method</p><h2 id="fl-method-title">How it works</h2></div>
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


def _algorithm_markup(p):
    """A responsive, three-route rendering of Algorithm 1 (not a pipeline of methods)."""
    routes = (
        ('nnc', 'NNC', 'Correct labels', (
            ('labeled', 'Initialization', 'Neighbor vote → corrected labels',
             'Encode local examples; replace each label with its neighbors’ majority vote.', True),
            ('train', 'Local training', 'Train on corrected labels',
             'Minimize cross-entropy on each participating client.', False),
            ('aggregate', 'Server aggregation', 'Sample-weighted FedAvg',
             'Average client models by their share of training samples.', False),
        )),
        ('akd', 'AKD', 'Guide local learning', (
            ('embedding', 'Initialization', 'Estimate client noise',
             'Count disagreements between local labels and embedding-based votes.', False),
            ('teacher', 'Local training', 'Label loss + teacher guidance',
             'Keep observed labels; use estimated noise to gate the extra teacher loss.', True),
            ('aggregate', 'Server aggregation', 'Sample-weighted FedAvg',
             'Average client models by their share of training samples.', False),
        )),
        ('na', 'NA-FedAvg', 'Reweight updates', (
            ('model', 'Initialization', 'Initialize the shared model',
             'Start ordinary FedAvg, without an encoder or label correction.', False),
            ('train', 'Local training', 'Train on observed labels',
             'At the estimation round, also send local/global-model energy scores.', False),
            ('aggregate', 'Server aggregation', 'Data share × clean fraction',
             'Estimate client noise once after warm-up; reuse its clean fraction (1 − noise) for aggregation.', True),
        )),
    )
    rows = []
    for key, name, purpose, steps in routes:
        cells = []
        for icon, stage, title, detail, active in steps:
            cls = ' fl-algorithm-intervention' if active else ''
            cells.append(f'''<li class="fl-algorithm-step{cls}"><span class="fl-algorithm-stage">{stage}</span><div class="fl-algorithm-step-title">{research_icon(icon)}<strong>{title}</strong></div><p>{detail}</p></li>''')
        rows.append(f'''<div class="fl-algorithm-route fl-method-{key}"><div class="fl-algorithm-route-name"><h4>{name}</h4><p>{purpose}</p></div><ol aria-label="{name} algorithm route">{''.join(cells)}</ol></div>''')
    return f'''<figure class="fl-algorithm" aria-labelledby="fl-algorithm-title">
    <figcaption><p class="fl-eyebrow">From local data to a shared model</p><h3 id="fl-algorithm-title">One federated loop. Three intervention points.</h3><p>Choose one route. Each highlighted step shows where that method intervenes.</p></figcaption>
    <div class="fl-algorithm-head" aria-hidden="true"><span></span><span>Before training</span><span class="fl-algorithm-rounds">Every round · send shared model → train locally → aggregate <span>↻</span></span></div>
    <div class="fl-algorithm-routes">{''.join(rows)}</div>
    <p class="fl-algorithm-footer">{research_icon('exchange')}<span>Each round starts from the shared model; client data stay local.</span>{_source(p, 'Algorithm 1', 13)}</p>
  </figure>'''
