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
    """Return a static fallback with three manual intervention selectors."""
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
    return f'''<section class="fl-tour" data-fl-tour data-active="network" data-running="false" data-nnc-phase="complete" data-akd-phase="complete" data-na-phase="complete" aria-labelledby="fedln-tour-heading">
  <header class="fl-tour-head">
    <p id="fedln-tour-heading">Three alternative interventions</p>
    <button class="fl-tour-toggle" type="button" data-tour-toggle hidden aria-label="Play the 36-second overview"><span data-tour-play-icon aria-hidden="true"><svg class="fl-tour-icon-play" viewBox="0 0 20 20"><path d="m6 3 11 7-11 7Z"/></svg><svg class="fl-tour-icon-pause" viewBox="0 0 20 20"><rect x="4" y="3" width="4" height="14" rx="1"/><rect x="12" y="3" width="4" height="14" rx="1"/></svg></span><span data-tour-toggle-label>Play overview</span></button>
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
    <p data-tour-description>Local data → Client updates → Shared model</p>
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
          <strong>5 nearest local neighbors</strong>
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
      <div class="fl-tour-local-chip">Client B · embedding-teacher variant</div>
      <div class="fl-tour-akd-story">
        <div class="fl-tour-akd-example">
          <span class="fl-tour-step-label">1 · Same local sample</span>
          {_dog(accessible=True)}
          <span class="fl-tour-image-caption">Stored label</span>
          <span class="fl-tour-label fl-tour-label-wrong">Cat</span>
        </div>
        <div class="fl-tour-akd-models" data-tour-akd-part="teacher" data-visible="true" aria-hidden="false">
          <span class="fl-tour-step-label">2 · Two views of the image</span>
          <svg class="fl-tour-akd-fork" viewBox="0 0 28 142" preserveAspectRatio="none" aria-hidden="true"><path d="M0 71h10V22h18M10 71v49h18"/><path d="m23 18 5 4-5 4m0 90 5 4-5 4"/></svg>
          <div class="fl-tour-teacher-model">{_encoder()}<div><strong>Frozen teacher</strong><span>Pre-trained encoder</span></div><div class="fl-tour-mini-features" aria-label="Teacher embedding"><i></i><i></i><i></i><i></i></div></div>
          <div class="fl-tour-local-model">{_model()}<div><strong>Local model</strong><span>Trainable features<br>+ label prediction</span></div><div class="fl-tour-mini-features fl-tour-local-features" aria-label="Local model features"><i></i><i></i><i></i><i></i></div></div>
          <span class="fl-tour-image-caption">Same image enters both</span>
        </div>
        <div class="fl-tour-akd-guidance" data-tour-akd-part="guidance" data-visible="true" aria-hidden="false">
          <span class="fl-tour-step-label">3 · Add teacher guidance</span>
          <span class="fl-tour-causal-arrow" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M3 12h17m-6-6 6 6-6 6"/></svg></span>
          <div class="fl-tour-client-gate"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 12h6m4 0h6M10 7v10M14 5v14"/><circle cx="20" cy="12" r="2"/></svg><span>Client noise detected<br><strong>Teacher signal enabled</strong></span></div>
          <div class="fl-tour-teacher-signal"><span>Teacher signal</span><strong>Match image features</strong><svg class="fl-tour-feature-match" viewBox="0 0 170 43" role="img" aria-label="The local model learns to bring its features closer to the fixed teacher features"><g class="fl-tour-feature-labels"><text x="2" y="14">Teacher</text><text x="2" y="36">Local</text></g><path class="fl-tour-feature-guide" d="M75 11V32M110 11V32M145 11V32"/><g class="fl-tour-reference-features"><circle cx="75" cy="11" r="4"/><circle cx="110" cy="11" r="4"/><circle cx="145" cy="11" r="4"/></g><g class="fl-tour-learning-features"><circle cx="63" cy="32" r="4"/><circle cx="117" cy="32" r="4"/><circle cx="158" cy="32" r="4"/></g></svg></div>
          <div class="fl-tour-label-signal"><span>Label signal</span><strong>Stored label ↔ prediction</strong></div>
        </div>
        <div class="fl-tour-akd-update" data-tour-akd-part="update" data-visible="true" aria-hidden="false">
          <span class="fl-tour-step-label">4 · Train with both signals</span>
          <span class="fl-tour-causal-arrow" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M3 12h17m-6-6 6 6-6 6"/></svg></span>
          <div class="fl-tour-updated-model">{_model()}<svg class="fl-tour-update-loop" viewBox="0 0 68 68" aria-hidden="true"><path d="M12 23A25 25 0 0 1 56 18m0 0V8m0 10H46M56 45A25 25 0 0 1 12 50m0 0v10m0-10h10"/></svg></div>
          <strong>Local weights update</strong>
          <span class="fl-tour-image-caption">Labels stay unchanged</span>
          <span class="fl-tour-label fl-tour-label-wrong">Cat</span>
        </div>
      </div>
    </div>
    <div class="fl-tour-scene fl-tour-na" data-tour-scene="na" hidden>
      <div class="fl-tour-local-chip">NA-FedAvg · Server aggregation</div>
      <div class="fl-tour-na-story">
        <div class="fl-tour-na-warmup">
          <span class="fl-tour-step-label">1 · Warm up normally</span>
          <svg class="fl-tour-warmup-art" viewBox="0 0 120 132" role="img" aria-label="Ordinary federated learning exchanges a global model and updates with clients A, B and C"><g class="fl-tour-warmup-lines"><path d="M60 40v23H20v28M60 63v28M60 63h40v28"/></g><g class="fl-tour-warmup-server"><rect x="38" y="9" width="44" height="14" rx="4"/><rect x="38" y="27" width="44" height="14" rx="4"/><path d="M46 16h1m8 0h18M46 34h1m8 0h18"/></g><g class="fl-tour-warmup-devices"><rect x="9" y="89" width="22" height="30" rx="5"/><rect x="49" y="89" width="22" height="30" rx="5"/><rect x="89" y="89" width="22" height="30" rx="5"/></g><g class="fl-tour-warmup-letters"><text x="20" y="109">A</text><text x="60" y="109">B</text><text x="100" y="109">C</text></g></svg>
          <strong>Ordinary FedAvg</strong><span class="fl-tour-image-caption">Local training + aggregation</span>
        </div>
        <div class="fl-tour-na-scores" data-tour-na-part="scores" data-visible="true" aria-hidden="false">
          <span class="fl-tour-step-label">2 · Score locally, once</span>
          <span class="fl-tour-causal-arrow" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M3 12h17m-6-6 6 6-6 6"/></svg></span>
          <strong>Global + local models</strong><span class="fl-tour-image-caption">Confidence on local samples</span>
          <div class="fl-tour-score-rows">
            <div><b>Client A</b><svg viewBox="0 0 72 30" aria-hidden="true"><rect x="2" y="2" width="30" height="26" rx="4"/><rect x="40" y="2" width="30" height="26" rx="4"/><path d="M8 10h18M8 15h12M8 20h15M46 10h18M46 15h12M46 20h15"/></svg></div>
            <div><b>Client B</b><svg viewBox="0 0 72 30" aria-hidden="true"><rect x="2" y="2" width="30" height="26" rx="4"/><rect x="40" y="2" width="30" height="26" rx="4"/><path d="M8 10h18M8 15h12M8 20h15M46 10h18M46 15h12M46 20h15"/></svg></div>
            <div><b>Client C</b><svg viewBox="0 0 72 30" aria-hidden="true"><rect x="2" y="2" width="30" height="26" rx="4"/><rect x="40" y="2" width="30" height="26" rx="4"/><path d="M8 10h18M8 15h12M8 20h15M46 10h18M46 15h12M46 20h15"/></svg></div>
          </div>
          <span class="fl-tour-score-transfer">Send score sets to server</span><span class="fl-tour-image-caption">Raw data stay local</span>
        </div>
        <div class="fl-tour-na-noise" data-tour-na-part="noise" data-visible="true" aria-hidden="false">
          <span class="fl-tour-step-label">3 · Estimate client noise</span>
          <span class="fl-tour-causal-arrow" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M3 12h17m-6-6 6 6-6 6"/></svg></span>
          <div class="fl-tour-noise-server">{_server()}<strong>At the server</strong></div>
          <div class="fl-tour-noise-rows"><div><b>A</b><span>Lower noise</span></div><div class="fl-tour-noise-high"><b>B</b><span>Higher noise</span></div><div><b>C</b><span>Lower noise</span></div></div>
          <span class="fl-tour-image-caption">Estimate once</span>
        </div>
        <div class="fl-tour-na-aggregation" data-tour-na-part="aggregation" data-visible="true" aria-hidden="false">
          <span class="fl-tour-step-label">4 · Weight future updates</span>
          <span class="fl-tour-causal-arrow" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M3 12h17m-6-6 6 6-6 6"/></svg></span>
          <strong>Data share × reliability</strong><span class="fl-tour-image-caption">1 − estimated noise</span>
          <div class="fl-tour-contributions" role="img" aria-label="For equally sized clients, higher estimated noise gives client B less influence than clients A and C"><div><b>A</b><span><i></i></span></div><div class="fl-tour-contribution-noisy"><b>B</b><span><i></i></span></div><div><b>C</b><span><i></i></span></div></div>
          <svg class="fl-tour-merge-updates" viewBox="0 0 120 22" aria-hidden="true"><path d="M20 1v6h40v13M60 1v19M100 1v6H60m-4 9 4 4 4-4"/></svg>
          <div class="fl-tour-na-result">{_model()}<strong>Shared model</strong></div>
          <span class="fl-tour-image-caption">Reuse estimates in later rounds</span>
        </div>
      </div>
    </div>
  </div>
  <p class="fl-tour-status fl-tour-sr-only" data-tour-status role="status" aria-live="polite" aria-atomic="true">Select a method or play the overview.</p>
  <div class="fl-tour-fallback">
    <dl><div><dt>NNC · before training</dt><dd>A frozen encoder finds other local examples with similar image features. A vote among their stored labels corrects the sample’s label.</dd></div><div><dt>AKD · during training</dt><dd>For clients with detected noise, an embedding teacher guides local features alongside the original-label signal. The labels stay unchanged.</dd></div><div><dt>NA-FedAvg · at the server</dt><dd>After ordinary warm-up, clients send global- and local-model confidence scores once. The server estimates each client’s noise and reuses it to weight later updates by data share times estimated reliability.</dd></div></dl>
  </div>
</section>'''
