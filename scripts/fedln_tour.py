"""Standalone, progressively enhanced FedLN method tour.

Integration: insert tour_markup(), include assets/fedln-tour.css, and load
assets/fedln-tour.js with defer. No external dependencies or inline scripts.
"""


def _device():
    return '<svg viewBox="0 0 48 48" aria-hidden="true"><rect x="12" y="4" width="24" height="40" rx="5"/><path d="M20 9h8M22 38h4"/><circle cx="24" cy="24" r="6"/></svg>'


def _server():
    return '<svg viewBox="0 0 48 48" aria-hidden="true"><rect x="6" y="7" width="36" height="14" rx="4"/><rect x="6" y="27" width="36" height="14" rx="4"/><path d="M14 14h1M14 34h1M23 14h11M23 34h11"/></svg>'


def _model():
    return '<svg viewBox="0 0 48 48" aria-hidden="true"><path d="m12 13 24 11-24 11M12 13v22M12 13l24 22M12 35 36 13M36 13v22"/><circle cx="12" cy="13" r="4"/><circle cx="12" cy="35" r="4"/><circle cx="36" cy="13" r="4"/><circle cx="36" cy="35" r="4"/><circle cx="24" cy="24" r="4"/></svg>'


def tour_markup():
    """Return an accessible static overview, enhanced into a tour by the JS."""
    clients = ''.join(
        f'<div class="fl-tour-client fl-tour-client-{letter.lower()}">{_device()}<strong>Client {letter}</strong><span>Local data</span></div>'
        for letter in 'ABC'
    )
    return f'''<section class="fl-tour" data-fl-tour data-active="network" data-running="false" aria-labelledby="fedln-tour-heading">
  <header class="fl-tour-head">
    <span class="fl-tour-eyebrow">Explore the method</span>
    <h2 id="fedln-tour-heading">Three alternatives, one shared model</h2>
    <p>Choose where to handle noisy labels. Each method is an alternative intervention.</p>
  </header>
  <div class="fl-tour-controls" data-tour-controls hidden>
    <div class="fl-tour-playback">
      <button class="fl-tour-toggle" type="button" data-tour-toggle aria-label="Play the 26-second method tour"><span data-tour-play-icon aria-hidden="true">▶</span><span data-tour-toggle-label>Play tour</span></button>
      <button class="fl-tour-replay" type="button" data-tour-replay aria-label="Replay the tour from the network overview"><span aria-hidden="true">↺</span><span data-tour-replay-label>Replay</span></button>
      <span class="fl-tour-duration" data-tour-duration>26 seconds · plays once</span>
    </div>
    <nav class="fl-tour-stages" aria-label="Explore a FedLN intervention">
      <button type="button" data-tour-stage="network" aria-pressed="true" aria-label="Federated network overview" title="Federated network overview"><span class="fl-tour-stage-dot fl-tour-dot-network"></span>Network</button>
      <button type="button" data-tour-stage="nnc" aria-pressed="false" aria-label="NNC: Nearest Neighbor Correction at initialization" title="Nearest Neighbor Correction"><span class="fl-tour-stage-dot fl-tour-dot-nnc"></span>NNC</button>
      <button type="button" data-tour-stage="akd" aria-pressed="false" aria-label="AKD: Adaptive Knowledge Distillation during local training" title="Adaptive Knowledge Distillation"><span class="fl-tour-stage-dot fl-tour-dot-akd"></span>AKD</button>
      <button type="button" data-tour-stage="na" aria-pressed="false" aria-label="NA-FedAvg: Noise-Aware Federated Averaging at the server" title="Noise-Aware Federated Averaging"><span class="fl-tour-stage-dot fl-tour-dot-na"></span>NA-FedAvg</button>
    </nav>
    <div class="fl-tour-progress" aria-hidden="true"><span data-tour-progress></span></div>
  </div>
  <div class="fl-tour-scene-heading">
    <span class="fl-tour-scene-kicker" data-tour-kicker>Federated learning</span>
    <h3 data-tour-title>Training stays on each client</h3>
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
      <div class="fl-tour-local-chip">Client A · before federated training</div>
      <div class="fl-tour-nnc-layout">
        <div class="fl-tour-embedding" role="img" aria-label="Conceptual embedding neighborhood: nearby examples have label A, so their vote changes a mismatched label B to A.">
          <span class="fl-tour-visual-label">Local pre-trained embeddings</span>
          <svg viewBox="0 0 320 190" aria-hidden="true">
            <ellipse class="fl-tour-neighborhood" cx="160" cy="98" rx="94" ry="74"/>
            <g class="fl-tour-vote-lines"><path d="M105 57 160 100M218 57 160 100M232 137 160 100M95 137 160 100M160 30V100"/></g>
            <g class="fl-tour-neighbors"><circle cx="105" cy="57" r="19"/><circle cx="218" cy="57" r="19"/><circle cx="232" cy="137" r="19"/><circle cx="95" cy="137" r="19"/><circle cx="160" cy="30" r="19"/></g>
            <g class="fl-tour-sample-labels"><text x="105" y="64">A</text><text x="218" y="64">A</text><text x="232" y="144">A</text><text x="95" y="144">A</text><text x="160" y="37">A</text></g>
            <circle class="fl-tour-target" cx="160" cy="100" r="25"/>
            <text class="fl-tour-old-label" x="160" y="108">B</text><text class="fl-tour-new-label" x="160" y="108">A</text>
          </svg>
          <span class="fl-tour-conceptual">Illustrative neighborhood</span>
        </div>
        <div class="fl-tour-vote-summary"><span class="fl-tour-micro">Nearest-neighbor vote</span><strong>A · A · A</strong><div class="fl-tour-correction"><span>B</span><span aria-hidden="true">→</span><b>A</b></div><p>Correct the label.<br>Then train as usual.</p></div>
      </div>
    </div>
    <div class="fl-tour-scene fl-tour-akd" data-tour-scene="akd" hidden>
      <div class="fl-tour-local-chip">Client B · during local training</div>
      <div class="fl-tour-noise-gate"><span class="fl-tour-gate-dot"></span>Example: high estimated local noise</div>
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
      <span class="fl-tour-conceptual">Illustrative noise levels and line widths; no measured values.</span>
    </div>
  </div>
  <p class="fl-tour-status" data-tour-status role="status" aria-live="polite" aria-atomic="true">Select a method or play the guided tour.</p>
  <div class="fl-tour-fallback">
    <dl><div><dt>NNC · initialization</dt><dd>A vote among local pre-trained embedding neighbors corrects mismatched labels before training.</dd></div><div><dt>AKD · local training</dt><dd>A teacher loss is activated according to estimated local noise, alongside the supervised loss.</dd></div><div><dt>NA-FedAvg · aggregation</dt><dd>After warm-up, estimated noise levels reduce the aggregation weight of noisier clients.</dd></div></dl>
  </div>
  <footer class="fl-tour-footer"><span>Three alternatives · conceptual illustrations</span><a href="https://doi.org/10.1145/3626242">Paper, §4.2–4.3 <span aria-hidden="true">↗</span></a></footer>
</section>'''
