"""Accessible, dependency-free FedLN overview; enhanced by fedln-tour.js."""


def _device():
    return '<svg viewBox="0 0 48 48" aria-hidden="true"><rect x="12" y="4" width="24" height="40" rx="5"/><path d="M20 9h8M22 38h4"/><circle cx="24" cy="24" r="6"/></svg>'


def _server():
    return '<svg viewBox="0 0 48 48" aria-hidden="true"><rect x="6" y="7" width="36" height="14" rx="4"/><rect x="6" y="27" width="36" height="14" rx="4"/><path d="M14 14h1M14 34h1M23 14h11M23 34h11"/></svg>'


def _model():
    return '<svg viewBox="0 0 48 48" aria-hidden="true"><path d="m12 13 24 11-24 11M12 13v22M12 13l24 22M12 35 36 13M36 13v22"/><circle cx="12" cy="13" r="4"/><circle cx="12" cy="35" r="4"/><circle cx="36" cy="13" r="4"/><circle cx="36" cy="35" r="4"/><circle cx="24" cy="24" r="4"/></svg>'


def _dog(coat='#dca55e', ear='#9c652f', accessible=False):
    """The same query artwork is used before and after label correction."""
    semantics = 'role="img" aria-label="Dog image"' if accessible else 'aria-hidden="true"'
    return f'''<svg class="fl-tour-dog" viewBox="0 0 100 100" {semantics}>
      <rect x="2" y="2" width="96" height="96" rx="15" fill="#edf2ed"/>
      <path d="M8 80 29 59l16 17 17-23 30 27v12H8Z" fill="#dce7dd"/>
      <path d="M31 29C14 19 11 39 16 59c2 10 12 10 17-2M69 29c17-10 20 10 15 30-2 10-12 10-17-2" fill="{ear}" stroke="#65462e" stroke-width="2"/>
      <path d="M27 38c0-23 46-23 46 0v24c0 26-46 26-46 0Z" fill="{coat}" stroke="#65462e" stroke-width="2"/>
      <path d="M46 23h8l5 33H41Z" fill="#fff0d9" opacity=".85"/>
      <ellipse cx="50" cy="66" rx="18" ry="14" fill="#fff0d9"/>
      <ellipse cx="37" cy="47" rx="3" ry="4" fill="#302c29"/><ellipse cx="63" cy="47" rx="3" ry="4" fill="#302c29"/>
      <path d="M44 59q6-4 12 0l-6 7Z" fill="#302c29"/><path d="M50 66v5m-8-1q8 8 16 0" fill="none" stroke="#65462e" stroke-width="2" stroke-linecap="round"/>
      <path d="M46 75q4 12 8 0" fill="#d7807f"/>
    </svg>'''


def _encoder():
    return '''<svg class="fl-tour-encoder-icon" viewBox="0 0 96 88" aria-hidden="true">
      <rect x="13" y="9" width="70" height="65" rx="12"/>
      <path class="fl-tour-encoder-connections" d="m29 27 19 15 19-15M29 57l19-15 19 15M29 27l19 30 19-30M29 57l19-30 19 30"/>
      <g class="fl-tour-encoder-nodes"><circle cx="29" cy="27" r="4"/><circle cx="29" cy="57" r="4"/><circle cx="48" cy="27" r="4"/><circle cx="48" cy="42" r="4"/><circle cx="48" cy="57" r="4"/><circle cx="67" cy="27" r="4"/><circle cx="67" cy="57" r="4"/></g>
      <rect class="fl-tour-lock-body" x="61" y="59" width="23" height="22" rx="5"/><path class="fl-tour-lock" d="M67 59v-5a6 6 0 0 1 12 0v5m-6 8v6"/>
    </svg>'''


def tour_markup():
    """Return a static overview with three opt-in intervention selectors."""
    clients = ''.join(
        f'<div class="fl-tour-client fl-tour-client-{letter.lower()}">{_device()}<strong>Client {letter}</strong><span>Local data</span></div>'
        for letter in 'ABC'
    )
    neighbors = ''.join(
        f'<div class="fl-tour-neighbor" data-tour-neighbor="{index}" data-visible="true">{_dog(coat, ear)}<span class="fl-tour-label {"fl-tour-label-wrong" if index == 5 else "fl-tour-label-right"}">{"Cat" if index == 5 else "Dog"}</span></div>'
        for index, (coat, ear) in enumerate([
            ('#e8d3af', '#ae875a'), ('#b78050', '#705039'), ('#77706b', '#47423f'),
            ('#d9d8d0', '#92928c'), ('#f0dfc1', '#bd9465')
        ], 1)
    )
    return f'''<section class="fl-tour" data-fl-tour data-active="network" data-running="false" data-nnc-phase="complete" aria-labelledby="fedln-tour-heading">
  <header class="fl-tour-head">
    <p id="fedln-tour-heading">Three alternative interventions</p>
    <button class="fl-tour-toggle" type="button" data-tour-toggle hidden aria-label="Play the 28-second overview"><span data-tour-play-icon aria-hidden="true"><svg class="fl-tour-icon-play" viewBox="0 0 20 20"><path d="m6 3 11 7-11 7Z"/></svg><svg class="fl-tour-icon-pause" viewBox="0 0 20 20"><rect x="4" y="3" width="4" height="14" rx="1"/><rect x="12" y="3" width="4" height="14" rx="1"/></svg></span><span data-tour-toggle-label>Play overview</span></button>
  </header>
  <div class="fl-tour-controls" data-tour-controls hidden>
    <nav class="fl-tour-stages" aria-label="Explore a FedLN intervention">
      <button type="button" data-tour-stage="nnc" aria-pressed="false" aria-label="Correct labels: NNC, Nearest Neighbor Correction, before training"><span class="fl-tour-stage-number" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M3 5h9l9 9-7 7-9-9Z"/><circle cx="8" cy="9" r="1"/><path d="m11 14 2 2 4-4"/></svg></span><span><strong>Correct labels</strong><small>NNC<span class="fl-tour-stage-timing"> · Before training</span></small></span></button>
      <button type="button" data-tour-stage="akd" aria-pressed="false" aria-label="Guide learning: AKD, Adaptive Knowledge Distillation, during training"><span class="fl-tour-stage-number" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="m12 3 9 5-9 5-9-5Zm-6 8v6q6 5 12 0v-6M21 8v8"/></svg></span><span><strong>Guide learning</strong><small>AKD<span class="fl-tour-stage-timing"> · During training</span></small></span></button>
      <button type="button" data-tour-stage="na" aria-pressed="false" aria-label="Weight updates: NA-FedAvg, Noise-Aware Federated Averaging, at the server"><span class="fl-tour-stage-number" aria-hidden="true"><svg viewBox="0 0 24 24"><rect x="8" y="15" width="8" height="6" rx="2"/><path d="M4 5v6h8v4M12 5v10M20 5v6h-8"/><circle cx="4" cy="4" r="2"/><circle cx="12" cy="4" r="2"/><circle cx="20" cy="4" r="2"/></svg></span><span><strong>Weight updates</strong><small>NA-FedAvg<span class="fl-tour-stage-timing"> · At server</span></small></span></button>
    </nav>
    <div class="fl-tour-progress" aria-hidden="true"><span data-tour-progress></span></div>
  </div>
  <div class="fl-tour-scene-heading">
    <h3 class="fl-tour-sr-only" data-tour-title>Training stays on each client</h3>
    <p data-tour-description>Clients learn from local data; the server combines their model updates.</p>
  </div>
  <div class="fl-tour-viewport">
    <div class="fl-tour-scene fl-tour-network" data-tour-scene="network" role="img" aria-label="A shared server exchanges model updates with three clients. Raw data stay on the clients.">
      <div class="fl-tour-network-camera">
        <div class="fl-tour-server">{_server()}<div><strong>Shared model</strong><span>Aggregation server</span></div></div>
        <div class="fl-tour-network-links" aria-hidden="true"><svg viewBox="0 0 600 120" preserveAspectRatio="none"><path class="fl-tour-link-base" d="M300 0V35M300 35H95V120M300 35V120M300 35H505V120"/><path class="fl-tour-packets" d="M95 120V35H300V0M300 120V0M505 120V35H300V0"/></svg><span>Model updates</span></div>
        <div class="fl-tour-clients">{clients}</div>
      </div>
    </div>
    <div class="fl-tour-scene fl-tour-nnc" data-tour-scene="nnc" hidden>
      <div class="fl-tour-local-chip">Client A · before training</div>
      <div class="fl-tour-nnc-story">
        <div class="fl-tour-query">
          <span class="fl-tour-step-label">1 · Original image</span>
          {_dog(accessible=True)}
          <span class="fl-tour-image-caption">Stored label</span>
          <span class="fl-tour-label fl-tour-label-wrong">Cat</span>
        </div>
        <div class="fl-tour-encode" data-tour-nnc-part="embedding" data-visible="true">
          <span class="fl-tour-story-arrow" aria-hidden="true">→</span>
          <span class="fl-tour-step-label">2 · Image features</span>
          {_encoder()}
          <strong>Pre-trained encoder</strong><span class="fl-tour-image-caption">Frozen weights</span>
          <div class="fl-tour-feature-vector" aria-label="An embedding vector"><i></i><i></i><i></i><i></i><i></i><i></i></div>
          <span class="fl-tour-image-caption">Embedding</span>
        </div>
        <div class="fl-tour-neighbor-set" data-tour-nnc-part="neighbors" data-visible="true">
          <span class="fl-tour-story-arrow" aria-hidden="true">→</span>
          <span class="fl-tour-step-label">3 · Find similar images</span>
          <strong>5 nearest other local examples</strong>
          <div class="fl-tour-neighbor-images">{neighbors}</div>
          <span class="fl-tour-image-caption">Their stored labels</span>
          <div class="fl-tour-vote" data-tour-nnc-part="vote" data-visible="true"><span>Majority vote</span><strong><b>4 Dog</b><span> / 1 Cat</span></strong></div>
        </div>
        <div class="fl-tour-corrected" data-tour-nnc-part="corrected" data-visible="true">
          <span class="fl-tour-story-arrow" aria-hidden="true">→</span>
          <span class="fl-tour-step-label">4 · Correct the label</span>
          {_dog(accessible=True)}
          <span class="fl-tour-image-caption">Same image</span>
          <span class="fl-tour-label fl-tour-label-right"><span aria-hidden="true">✓ </span>Dog</span>
        </div>
      </div>
    </div>
    <div class="fl-tour-scene fl-tour-akd" data-tour-scene="akd" hidden>
      <div class="fl-tour-local-chip">Client B · during local training</div>
      <div class="fl-tour-noise-gate"><span class="fl-tour-gate-dot"></span>High estimated local noise activates teacher guidance</div>
      <div class="fl-tour-loss-branches">
        <div class="fl-tour-loss-branch"><span class="fl-tour-micro">Observed labels</span><span class="fl-tour-loss-icon" aria-hidden="true">y</span><strong>Supervised loss</strong></div>
        <div class="fl-tour-loss-branch fl-tour-teacher-branch"><span class="fl-tour-micro">Teacher guidance</span>{_model()}<span class="fl-tour-gate">Noise-gated</span><strong>Distillation loss</strong></div>
      </div>
      <div class="fl-tour-loss-join" aria-hidden="true"><svg viewBox="0 0 400 48" preserveAspectRatio="none"><path d="M95 0V20H200V48M305 0V20H200"/><path class="fl-tour-guidance" d="M305 0V20H200V48"/></svg></div>
      <div class="fl-tour-student">{_model()}<div><strong>Local model</strong><span>Supervised loss + gated teacher loss</span></div></div>
    </div>
    <div class="fl-tour-scene fl-tour-na" data-tour-scene="na" hidden>
      <div class="fl-tour-local-chip">Server · after warm-up</div>
      <div class="fl-tour-reliability-clients">
        <div>{_device()}<strong>Client A</strong><span>Lower noise</span></div>
        <div class="fl-tour-noisy-client">{_device()}<strong>Client B</strong><span>Higher noise</span></div>
        <div>{_device()}<strong>Client C</strong><span>Lower noise</span></div>
      </div>
      <div class="fl-tour-weighted-links" aria-hidden="true"><svg viewBox="0 0 600 82" preserveAspectRatio="none"><path class="fl-tour-strong-update" d="M95 0V35H300V82M505 0V35H300"/><path class="fl-tour-weak-update" d="M300 0V82"/><path class="fl-tour-weighted-packets" d="M95 0V35H300V82M505 0V35H300V82"/></svg></div>
      <div class="fl-tour-weighted-server">{_server()}<div><strong>Weighted global model</strong><span>Noisier updates have less influence</span></div></div>
    </div>
  </div>
  <p class="fl-tour-status fl-tour-sr-only" data-tour-status role="status" aria-live="polite" aria-atomic="true">Select a method or play the overview.</p>
  <div class="fl-tour-fallback">
    <dl><div><dt>NNC · before training</dt><dd>A frozen encoder finds other local examples with similar image features. A vote among their stored labels corrects the sample’s label.</dd></div><div><dt>AKD · during training</dt><dd>A teacher loss is activated according to estimated local noise, alongside the supervised loss.</dd></div><div><dt>NA-FedAvg · at the server</dt><dd>After warm-up, estimated noise levels reduce the aggregation weight of noisier clients.</dd></div></dl>
  </div>
</section>'''
