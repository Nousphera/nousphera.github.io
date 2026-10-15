"""One connected FedSTAR round, grounded in the final 2022 ACM TECS article.

Source: final TU/e publisher PDF, §4.2–4.3, Eq.5/7, Fig.2, Algorithm1,
and Table2 (PDF pp.10–12,14). T=4; cosine confidence threshold .5→.9;
equal labeled/unlabeled input batches; one joint local update with beta=.5;
data-weighted FedAvg of model parameters. Optional public-data pretraining
is preparation, not a mandatory stage in the downstream round.

Clip patterns, class probabilities and the selected .7 threshold are an
illustration, not experimental observations. 'Other' pools the remaining
Speech Commands classes. U2 is deferred, never assigned a training target.
"""
from html import escape
from research_icons import research_icon
from math import cos, pi


CLIPS = {
    'L1': {'label': 'go', 'wave': [3, 7, 5, 13, 24, 16, 7, 12, 21, 29, 19, 8, 12, 6, 3]},
    'L2': {'label': 'stop', 'wave': [3, 5, 14, 28, 22, 8, 5, 11, 16, 25, 18, 10, 5, 3, 2]},
    'U1': {'prediction': 'go', 'confidence': .94, 'scores': [.94, .03, .03],
           'wave': [2, 6, 11, 23, 30, 18, 8, 5, 17, 25, 20, 12, 7, 4, 2]},
    'U2': {'prediction': 'stop', 'confidence': .68, 'scores': [.14, .68, .18],
           'wave': [2, 4, 8, 17, 25, 14, 5, 9, 22, 30, 23, 12, 5, 3, 2]},
}
THRESHOLD = .7


def icon(name):
    return research_icon({'packet': 'paper', 'audio': 'waveform'}.get(name, name), "fs-icon")


def reveal(body, at=0, cls=''):
    return f'<div class="{cls}" data-reveal="{at}">{body}</div>'


def model(variant='shared'):
    shades = {'shared': [.3, .8, .5, .6, .2, .9, .4, .7, .3],
              'a': [.4, .9, .6, .5, .3, .8, .4, .6, .5],
              'b': [.3, .7, .6, .7, .4, .8, .5, .6, .3],
              'c': [.5, .8, .4, .6, .3, .7, .4, .8, .4],
              'next': [.4, .8, .5, .6, .3, .8, .4, .7, .4]}
    return '<span class="fs-model" aria-hidden="true">' + ''.join(f'<i style="--fs-shade:{v}"></i>' for v in shades[variant]) + '</span>'


def network(index):
    directions = ['down', 'local', 'local', 'local', 'local', 'both']
    actions = ['Model weights', 'Local prediction', 'Global-round gate', 'Local filtering', 'Local update', 'Weights ↑ · Model ↓']
    server_active = ' fs-active' if index in (0, 5) else ''
    client_active = ' fs-active' if index in (1, 2, 3, 4) else ''
    return f'''<div class="fs-network fs-direction-{directions[index]}" data-fs-network="true" data-direction="{directions[index]}">
      <div class="fs-endpoint{server_active}" data-role="server">{icon('server')}<div><strong>Server</strong><span>Global model</span></div></div>
      <div class="fs-connection"><span>{actions[index]}</span><div class="fs-wire"><i></i>{icon('arrow')}</div><div class="fs-wire fs-return"><i></i>{icon('arrow')}</div></div>
      <div class="fs-client-group"><div class="fs-endpoint{client_active}" data-role="client">{icon('client')}<div><strong>Client A</strong><span>Local audio</span></div></div><div class="fs-peers"><span>Client B</span><span>Client C</span></div></div>
    </div>'''


def clip(key, state='unlabeled'):
    sample = CLIPS[key]
    attrs = f'data-clip="{key}" data-origin="{"labeled" if key.startswith("L") else "unlabeled"}"'
    if key.startswith('L'):
        attrs += f' data-label="{sample["label"]}"'
        label = f'<span class="fs-tag fs-known">Known · <b>{sample["label"]}</b></span>'
    elif state == 'accepted':
        attrs += f' data-target="{sample["prediction"]}"'
        label = f'<span class="fs-tag fs-pseudo">Pseudo-label · <b>{sample["prediction"]}</b></span>'
    else:
        label = '<span class="fs-tag fs-unknown">Unlabeled</span>'
    pattern = ','.join(map(str, sample['wave']))
    wave = f'<span class="fs-wave" data-waveform="{pattern}" aria-hidden="true">' + ''.join(f'<i style="--fs-wave:{height}px;--fs-delay:{i * 45}ms"></i>' for i, height in enumerate(sample['wave'])) + '</span>'
    return f'<div class="fs-clip fs-clip-{state}" {attrs}><span class="fs-clip-id">{key}</span>{wave}{label}</div>'


def example_attrs(key):
    return f'data-example="{key}" data-prediction="{CLIPS[key]["prediction"]}" data-confidence="{CLIPS[key]["confidence"]}"'


def starting_point():
    clients = ''.join(f'<span class="fs-copy">{model()}<b>{name}</b></span>' for name in ['A', 'B', 'C'])
    broadcast = f'<div class="fs-broadcast" data-exchange="broadcast" data-payload="model-parameters"><span class="fs-model-source">{model()}<strong>Shared model</strong></span>{icon("arrow")}<div class="fs-model-copies">{clients}</div></div>'
    pools = f'''<div class="fs-batches"><div class="fs-batch" data-batch="labeled"><div class="fs-batch-heading"><strong>Known labels</strong><span>2 clips</span></div>{clip('L1')}{clip('L2')}</div>
      <div class="fs-batch" data-batch="unlabeled"><div class="fs-batch-heading"><strong>Unlabeled</strong><span>2 clips</span></div>{clip('U1')}{clip('U2')}</div></div>'''
    return reveal(broadcast, 200) + reveal(pools, 1200) + reveal('<div class="fs-note">Client A · Equal input batches</div>', 2500)


def predict():
    cards = []
    for key in ['U1', 'U2']:
        sample = CLIPS[key]
        bars = ''.join(f'<div class="fs-prob-row{" fs-highest" if label == sample["prediction"] else ""}"><span>{label}</span><span class="fs-prob-track"><i style="--fs-prob:{v * 100:g}%"></i></span><b>{v * 100:g}%</b></div>' for label, v in zip(['go', 'stop', 'other'], sample['scores']))
        cards.append(reveal(f'<div class="fs-prediction" {example_attrs(key)}>{clip(key)}<div class="fs-probabilities">{bars}</div><div class="fs-choice"><span>Top class</span><b>{sample["prediction"]}</b></div></div>', 1200 if key == 'U1' else 2400))
    pipeline = f'<div class="fs-pipeline" data-temperature="4"><span>{icon("model")}Local model</span>{icon("arrow")}<strong>T = 4</strong>{icon("arrow")}<span>Probabilities</span></div>'
    return reveal(pipeline, 200) + '<div class="fs-predictions">' + ''.join(cards) + '</div>' + reveal('<div class="fs-note">Softer confidence · Same top class</div>', 3600)


def schedule():
    # A schematic half-cosine between the source's endpoints, not a fitted curve.
    curve = ' '.join(f'{i * 3:g},{57 - 48 * (1 - cos(pi * i / 100)) / 2:.2f}' for i in range(101))
    ramp = f'''<div class="fs-schedule" data-schedule="cosine" data-start="0.5" data-end="0.9" data-progress="global-round">
      <div class="fs-schedule-label"><span>Global rounds</span><strong>Cosine threshold</strong></div>
      <div class="fs-curve-map" aria-hidden="true"><svg class="fs-curve" viewBox="-5 0 310 66" preserveAspectRatio="none"><path d="M0 57H300M0 9H300"/><polyline points="{curve}"/></svg><i style="left:1.6129%;top:86.3636%"></i><i class="fs-current-point" style="left:50%;top:50%"></i><i style="left:98.3871%;top:13.6364%"></i></div>
      <div class="fs-schedule-ticks"><span><small>Early</small><b>50%</b></span><span class="fs-current"><small>Current gate</small><b>70%</b></span><span><small>Late</small><b>90%</b></span></div></div>'''
    contenders = ''.join(f'<div class="fs-contender" {example_attrs(key)}><span>{key}</span><b>{CLIPS[key]["prediction"]}</b><strong>{CLIPS[key]["confidence"] * 100:g}%</strong></div>' for key in ['U1', 'U2'])
    return reveal(ramp, 200) + reveal(f'<div class="fs-gate-focus"><span>THIS ROUND</span><strong>70<span>%</span></strong><small>Minimum confidence</small></div>', 1600) + reveal('<div class="fs-contenders">' + contenders + '</div>', 3000)


def filter_examples():
    rows = []
    for key in ['U1', 'U2']:
        sample = CLIPS[key]
        accepted = sample['confidence'] > THRESHOLD
        state = 'accepted' if accepted else 'deferred'
        target = f' data-target="{sample["prediction"]}"' if accepted else ''
        outcome = f'<strong>Pseudo-label <b>{sample["prediction"]}</b></strong><small>Use in this update</small>' if accepted else '<strong>Still unlabeled</strong><small>Skip this update</small>'
        row = f'''<div class="fs-filter-row fs-{state}" {example_attrs(key)} data-decision="{state}"{target}>
          {clip(key)}<div class="fs-filter-score"><b>{sample['confidence'] * 100:g}%</b><span>Predicted · {sample['prediction']}</span></div>
          <div class="fs-gate-result">{icon('check' if accepted else 'pause')}<span>{'Pass' if accepted else 'Defer'}</span></div>
          <div class="fs-outcome">{outcome}</div></div>'''
        rows.append(reveal(row, 1000 if accepted else 2500))
    return reveal('<div class="fs-rule" data-threshold="0.7"><span>Confidence gate</span><strong>&gt; 70%</strong></div>', 200) + '<div class="fs-filter">' + ''.join(rows) + '</div>'


def learn():
    supervised = f'<div class="fs-loss" data-loss="supervised" data-weight="1"><span class="fs-small-label">Known targets</span><div class="fs-loss-clips">{clip("L1")}{clip("L2")}</div><strong>Supervised loss</strong></div>'
    pseudo = f'<div class="fs-loss fs-loss-pseudo" data-loss="pseudo" data-weight="0.5"><span class="fs-small-label">Accepted target</span><div class="fs-loss-clips">{clip("U1", "accepted")}</div><strong><b>0.5 ×</b> Pseudo-label loss</strong></div>'
    update = f'<div class="fs-joint-update" data-local-update="true" data-inputs="supervised pseudo"><span class="fs-join">+</span><div class="fs-update-arrow">{icon("arrow")}</div><div class="fs-updated-model">{model("a")}<div><strong>One joint update</strong><span>Same local model</span></div></div></div>'
    return '<div class="fs-losses">' + reveal(supervised, 300) + reveal(pseudo, 1500) + '</div>' + reveal(update, 2900) + reveal(f'<div class="fs-deferred-note">{icon("pause")}U2 · Still unlabeled · No pseudo-label loss</div>', 4100)


def aggregate():
    uploads = ''.join(f'<div class="fs-upload"><span>Client {key.upper()}</span>{model(key)}{icon("arrow")}</div>' for key in ['a', 'b', 'c'])
    source = '<div class="fs-uploads" data-exchange="upload" data-payload="model-parameters">' + uploads + '</div>'
    average = f'<div class="fs-average" data-aggregation="data-weighted-fedavg">{icon("server")}<strong>FedAvg</strong><span>Data-weighted average</span></div>'
    next_model = f'<div class="fs-next-model">{model("next")}<strong>Next global model</strong></div>'
    broadcast = f'<div class="fs-next-broadcast" data-exchange="broadcast" data-payload="model-parameters"><span>{icon("loop")}Next round</span>{icon("arrow")}<span>{icon("client")}Selected clients</span></div>'
    return '<div class="fs-aggregation">' + reveal(source, 200) + reveal(average, 1500) + reveal(icon('arrow'), 2300, 'fs-aggregation-arrow') + reveal(next_model, 3100) + '</div>' + reveal(broadcast, 4200) + reveal('<div class="fs-note">Model parameters ↑ · Global model ↓</div>', 5100)


def make_step(index, short_title, title, caption, body, duration, description):
    scopes = ['SERVER → CLIENTS', 'ON EACH CLIENT', 'GLOBAL ROUNDS → LOCAL GATE', 'ON EACH CLIENT', 'ON EACH CLIENT', 'CLIENTS → SERVER → CLIENTS']
    return {
        'short_title': short_title, 'title': title, 'caption': caption,
        'duration_ms': duration, 'title_in_art': True,
        'art': f'''<div class="story-art fs-art" role="group" aria-label="{escape('Illustrative audio example. ' + description, quote=True)}">
          {network(index)}<div class="fs-scene-body"><div class="fs-stage-heading"><span class="fs-small-label">{scopes[index]}</span><h3>{title}</h3></div>{body}</div>
          <div class="fs-local-footer" data-local-only="raw-audio">{icon('audio')}<span>Raw audio · On device</span></div></div>''',
    }


STEPS = [
    make_step(0, 'Start round', 'Shared model · Local audio',
              'Model broadcast → Equal labeled + unlabeled batches', starting_point(), 8000,
              'The server broadcasts the same model parameters to selected clients. Client A holds known clips L1 go and L2 stop, and unlabeled clips U1 and U2. The two input batches have equal size; raw recordings stay local.'),
    make_step(1, 'Predict', 'Unlabeled audio → Predictions',
              'Local model → Temperature 4 → Top class + confidence', predict(), 9000,
              'The local model predicts temperature-scaled probabilities with T=4. Illustrative U1 predicts go with 94% confidence; U2 predicts stop with 68%. Other pools the remaining classes. Temperature softens confidence without changing the top class. These are predictions, not verified labels.'),
    make_step(2, 'Raise gate', 'Later rounds · Stricter gate',
              'Global-round cosine schedule · 50% → 90%', schedule(), 8500,
              'The confidence threshold increases with global-round progress from 50% to 90% using a cosine schedule. The example round uses 70%; no specific round number is implied. U1 remains go at 94%, and U2 remains stop at 68%.'),
    make_step(3, 'Filter', 'Pass → Learn · Defer → Wait',
              'U1 → Pseudo-label go · U2 → Still unlabeled', filter_examples(), 9500,
              'At the illustrative 70% gate, U1 go at 94% passes and supplies the pseudo-label go. U2 stop at 68% is deferred, remains unlabeled and contributes no pseudo-label loss in this update. High confidence does not guarantee correctness.'),
    make_step(4, 'Learn jointly', 'Two losses · One update',
              'Known-label loss + 0.5 × Pseudo-label loss → Local model', learn(), 9500,
              'Known targets L1 go and L2 stop supply the supervised loss. Accepted U1 supplies the pseudo-label go for an unlabeled loss weighted by 0.5. Both losses are combined before one backpropagation update to the same local model. Deferred U2 is excluded from pseudo-label loss.'),
    make_step(5, 'Aggregate', 'Local models → Shared model',
              'Model upload → Data-weighted FedAvg → Broadcast', aggregate(), 10000,
              'Participating clients upload model parameters. The server applies a data-weighted FedAvg average and broadcasts the resulting global model for the next round. Raw recordings remain on each client.'),
]
