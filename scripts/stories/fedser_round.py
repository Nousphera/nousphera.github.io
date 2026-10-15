"""Connected schematic for arXiv:2202.02611v1, Fig. 1, §III, Algorithm 1.

FedSER is the site's shorthand. Waveforms, feature cells, attention regions,
histories and prediction scores are illustrative, not empirical explanations.
The attention diagram preserves multiply → softmax → elementwise reweighting;
it deliberately does not specify the paper's unspecified softmax axis. The
printed Eq. 3 conflicts with its prose: no threshold direction/formula is
inferred. The 0.70 filter threshold is a separate toy example, not its output.
"""
from html import escape


EMOTIONS = ('neutral', 'happy', 'sad', 'angry')
PREDICTIONS = (
    ('speech-01', (.06, .84, .04, .06)),
    ('speech-02', (.22, .46, .18, .14)),
)
EXAMPLE_THRESHOLD = .70
TIME_FOCUS = (2, 3)
FREQUENCY_FOCUS = (1,)
CHANNEL_FOCUS = 1


def icon(name):
    paths = {
        'server': '<rect x="4" y="3" width="16" height="7" rx="2"/><rect x="4" y="14" width="16" height="7" rx="2"/><path d="M8 6.5h.01M8 17.5h.01M12 6.5h4M12 17.5h4M12 10v4"/>',
        'client': '<rect x="5" y="2" width="14" height="20" rx="3"/><path d="M10 5h4M11 19h2"/>',
        'arrow': '<path d="M4 12h16m-6-6 6 6-6 6"/>',
        'check': '<path d="m5 12 4 4L19 6"/>',
        'pause': '<path d="M9 5v14M15 5v14"/>',
        'loop': '<path d="M19 8a8 8 0 1 0 1 9M19 3v5h-5"/>',
    }
    return f'<svg class="se-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{paths[name]}</svg>'


def reveal(body, at=0, cls=''):
    return f'<div class="{cls}" data-reveal="{at}">{body}</div>'


def wave():
    # Exactly the same illustrative speech signature throughout the round.
    return '<span class="se-wave" aria-hidden="true">' + ''.join(
        f'<i style="--bar:{height}%;--i:{index}"></i>'
        for index, height in enumerate((12, 23, 16, 42, 75, 53, 100, 69, 38, 62, 82, 47, 25, 37, 16))
    ) + '</span>'


def sample(label='Speech 01', secondary=False):
    return f'<span class="se-sample{" se-secondary" if secondary else ""}">{wave()}<b>{escape(label)}</b></span>'


def network(index):
    actions = ('Broadcast', 'Local attention', 'Local threshold', 'Local filtering', 'Local learning', 'FedAvg')
    active_server = index in (0, 5)
    direction = 'down' if index == 0 else 'up' if index == 5 else 'still'
    return f'''<div class="se-network se-direction-{direction}" data-se-network="true">
      <div class="se-endpoint" data-active="{str(active_server).lower()}">{icon('server')}<strong>Server</strong></div>
      <div class="se-connection"><span>{actions[index]}</span><div class="se-wire"><i></i>{icon('arrow')}</div></div>
      <div class="se-endpoint" data-active="{str(not active_server).lower()}">{icon('client')}<strong>Client A</strong></div>
    </div>'''


def feature_grid(key, mode='', axes=False, channel=None):
    cells = []
    for frequency in range(4):
        for time in range(6):
            selected = ((mode == 'time' and time in TIME_FOCUS)
                        or (mode == 'frequency' and frequency in FREQUENCY_FOCUS)
                        or (mode == 'combined' and time in TIME_FOCUS and frequency in FREQUENCY_FOCUS))
            shade = (.24, .43, .61, .38, .78, .48)[(time + 2 * frequency) % 6]
            cells.append(f'<i class="se-cell" data-frequency="{frequency}" data-time="{time}" data-focused="{str(selected).lower()}" style="--shade:{shade}"></i>')
    channel_attr = f' data-channel="{channel}"' if channel is not None else ''
    grid = f'<div class="se-grid se-grid-{mode or "plain"}" data-grid="{key}"{channel_attr}>{"".join(cells)}</div>'
    return '<div class="se-axis-grid"><span class="se-axis-frequency">Frequency ↑</span>' + grid + '<span class="se-axis-time">Time →</span></div>' if axes else grid


def weights(cls=''):
    return f'<span class="se-weights {cls}" aria-hidden="true">' + ''.join(
        f'<i style="--shade:{v}"></i>' for v in (.3, .7, .45, .9, .55, .3, .8, .5, .25)
    ) + '</span>'


def features():
    return '<div class="se-feature-flow">' + \
        reveal(f'<div class="se-feature-card se-speech-card"><span class="se-label">Local speech</span>{wave()}<div class="se-data-tags"><span>Known</span><span class="se-tag-active">Unlabeled</span></div></div>', 0) + \
        reveal(icon('arrow'), 750, 'se-flow-arrow') + \
        reveal('<div class="se-feature-card"><span class="se-label">Log-mel</span>' + feature_grid('log-mel', axes=True) + '</div>', 1300) + \
        reveal(icon('arrow'), 2300, 'se-flow-arrow') + \
        reveal('<div class="se-feature-card"><span class="se-label">CNN features</span><div class="se-cnn">' + ''.join(f'<i style="--block:{i}"></i>' for i in range(4)) + '</div><span class="se-small">4 blocks</span></div>', 2900) + '</div>' + \
        reveal('<div class="se-model-input" data-input-model="global-model">' + weights() + '<span>Shared model</span>' + icon('arrow') + '<b>Local features</b></div>', 4000)


def attention():
    time = '<section class="se-axis-card se-time"><strong>Time</strong>' + feature_grid('time', 'time', axes=True) + '</section>'
    frequency = '<section class="se-axis-card se-frequency"><strong>Frequency</strong>' + feature_grid('frequency', 'frequency', axes=True) + '</section>'
    planes = ''.join(f'<div class="se-channel-plane" data-channel-plane="{i}" data-focused="{str(i == CHANNEL_FOCUS).lower()}" style="--plane:{i}">{feature_grid(f"channel-{i}")}<span>{i+1:02d}</span></div>' for i in range(3))
    channel = '<section class="se-axis-card se-channel"><strong>Channel</strong><div class="se-channel-stack">' + planes + '</div><span class="se-channel-axis">Channels ↗</span></section>'
    return '<div class="se-attention-axes">' + reveal(time, 0) + reveal(frequency, 1500) + reveal(channel, 3000) + '</div>' + \
        reveal('<div class="se-combine"><div class="se-combine-rule"><span>Time</span><b>×</b><span>Frequency</span><b>×</b><span>Channel</span></div>' + icon('arrow') + '<b class="se-softmax">Softmax</b></div>', 4500) + \
        reveal('<div class="se-weighted"><span>Weights ⊙ features</span>' + icon('arrow') + feature_grid('combined', 'combined', channel=CHANNEL_FOCUS) + '<strong>Weighted features</strong></div>', 5900)


def participation():
    rows = []
    for name, history, tone, at in [('A', (1, 1, 1, 1), '', 700), ('B', (1, 0, 1, 0), ' se-secondary', 1900)]:
        markers = ''.join(f'<span class="se-round-mark" data-participated="{str(bool(on)).lower()}">{icon("check") if on else "<i></i>"}</span>' for on in history)
        rows.append(reveal(f'<div class="se-history-row{tone}"><strong>Client {name}</strong><div class="se-rounds">{markers}</div>{icon("arrow")}<span class="se-tau">τ<sub>{name}</sub></span></div>', at))
    return reveal('<div class="se-history-head"><span>Participation</span><div class="se-rounds"><span>01</span><span>02</span><span>03</span><span>04</span></div><span>Threshold</span></div>') + \
        '<div class="se-histories">' + ''.join(rows) + '</div>' + \
        reveal('<div class="se-schedule-inputs"><span>' + icon('server') + 'Global progress</span><b>+</b><span>' + icon('client') + 'Client history</span>' + icon('arrow') + '<strong>τ<sub>k</sub></strong></div>', 3400) + \
        reveal('<div class="se-history-key"><span><i class="se-key-filled"></i>Participated</span><span><i></i>Missed</span></div>', 4400)


def prediction_card(sample_id, probabilities):
    top = max(range(len(probabilities)), key=probabilities.__getitem__)
    accepted = probabilities[top] > EXAMPLE_THRESHOLD
    status = 'use' if accepted else 'defer'
    bars = ''.join(f'<div class="se-emotion-row" data-emotion="{emotion}" data-probability="{probability:g}"><span>{emotion.title()}</span><div class="se-score-track"><i style="--score:{probability*100:g}%"></i><em style="--threshold:{EXAMPLE_THRESHOLD*100:g}%"></em></div><b>{probability:.2f}</b></div>' for emotion, probability in zip(EMOTIONS, probabilities))
    return f'''<div class="se-prediction se-prediction-{status}" data-prediction="{sample_id}" data-example="true" data-top-class="{EMOTIONS[top]}" data-threshold="{EXAMPLE_THRESHOLD}" data-outcome="{status}">
      <div class="se-prediction-head">{sample('Speech ' + sample_id[-2:], not accepted)}<span>T = 2</span></div>
      <div class="se-emotions">{bars}</div>
      <div class="se-decision">{icon('check' if accepted else 'pause')}<strong>{'Happy' if accepted else 'Defer'}</strong><span>{'Pseudo-label' if accepted else 'No target'}</span></div>
    </div>'''


def confidence():
    return reveal('<div class="se-example-note"><span>Illustrative probabilities</span><strong>τ<sub>A</sub> = 0.70</strong></div>') + \
        '<div class="se-predictions">' + ''.join(reveal(prediction_card(sample_id, probabilities), 1100 + index * 2200) for index, (sample_id, probabilities) in enumerate(PREDICTIONS)) + '</div>'


def local_update():
    known = f'<div class="se-loss-lane se-secondary" data-loss-kind="supervised" data-loss-source="known-01">{sample("Known label", True)}<span class="se-emotion-tag">Neutral</span>{icon("arrow")}<div class="se-loss"><span>Cross-entropy</span><strong>L<sub>s</sub></strong></div></div>'
    pseudo = f'<div class="se-loss-lane" data-loss-kind="pseudo-label" data-loss-source="speech-01">{sample()}<span class="se-emotion-tag">Happy ✓</span>{icon("arrow")}<div class="se-loss"><span>Cross-entropy</span><strong>L<sub>u</sub></strong></div></div>'
    return '<div class="se-loss-branches">' + reveal(known, 0) + reveal(pseudo, 1300) + '</div>' + \
        reveal('<div class="se-loss-join" aria-hidden="true"><i></i><b>+</b><i></i></div>', 2600) + \
        reveal('<div class="se-joint" data-joint-loss="true" data-inputs="supervised,pseudo-label" data-output="local-parameters"><span class="se-joint-formula">L<sub>s</sub> + β L<sub>u</sub></span>' + icon('arrow') + '<div class="se-updated">' + weights('se-weights-update') + '<strong>Local update</strong><span>θ<sub>A</sub></span></div></div>', 3400)


def aggregate():
    clients = ''.join(f'<div class="se-upload-client{tone}"><span>Client {name}</span>{weights()}<b>θ<sub>{name}</sub></b></div>' for name, tone in [('A', ''), ('B', ' se-secondary'), ('C', ' se-third')])
    return '<div class="se-aggregate-flow">' + \
        reveal('<div class="se-upload-group" data-transfer="upload" data-payload="model-parameters"><span class="se-label">Parameters</span>' + clients + '</div>', 0) + \
        reveal(icon('arrow'), 1100, 'se-flow-arrow') + \
        reveal('<div class="se-average" data-aggregation="FedAvg" data-weighting="local-data-size" data-output="next-global-model">' + icon('server') + '<strong>FedAvg</strong><span>Data-weighted average</span>' + weights('se-weights-global') + '</div>', 2200) + '</div>' + \
        reveal('<div class="se-broadcast" data-transfer="broadcast" data-payload="model-parameters">' + icon('loop') + '<strong>Next global model</strong><span>θ<sub>r+1</sub></span>' + icon('arrow') + '<div class="se-return-clients">' + icon('client') * 3 + '<b>Broadcast</b></div></div>', 3900)


def scene(index, title, body, description):
    return f'<div class="story-art se-art" role="group" aria-label="{escape(description, quote=True)}">' + network(index) + \
        f'<div class="se-scene-body"><div class="se-stage-heading"><span class="se-kicker">{index+1:02d} / 06</span><h3>{escape(title)}</h3></div>' + \
        '<div class="se-local-context" data-se-sample="speech-01" data-location="client">' + sample() + '<span>On device</span></div>' + body + '</div></div>'


_CONTENT = [
    ('Features', 'Speech → features', 'Local audio · Shared model · CNN', features, 8500,
     'One federated round. The server broadcasts model parameters. Client A retains its labeled and unlabeled speech. The recurring Speech 01 waveform is an unlabeled illustrative sample. A log-mel representation feeds four CNN blocks, which extract features. No segment duration is asserted because the source figure and method text disagree.'),
    ('Attention', 'Time · frequency · channels', 'Three attention maps · Softmax · Reweight', attention, 11000,
     'Client A reweights the same speech features. Time attention highlights columns; frequency attention highlights a row; channel attention highlights the middle feature plane. These qualitative regions illustrate axes, not measured activations or evidence of emotion localization. The three attention maps are multiplied and normalized by softmax, then multiplied elementwise with the original CNN features.'),
    ('Participation', 'Participation → threshold', 'Global progress + Client history → Local threshold', participation, 8500,
     'Global progress and each client participation history inform its confidence threshold. Filled circles indicate participation and empty circles a missed round. Client A and Client B have distinct illustrative histories. No threshold values, direction, or corrected schedule formula are inferred from the conflicting printed equation and prose.'),
    ('Confidence', 'Confidence → pseudo-label', 'Example · Confident: use · Uncertain: defer', confidence, 10000,
     'Illustrative four-emotion probabilities after temperature scaling with T equal to 2. This independent example uses threshold 0.70, not a value calculated from the preceding history. Speech 01 has happy probability 0.84 and becomes a happy pseudo-label. Speech 02 has maximum happy probability 0.46 and supplies no pseudo-label target. These are not empirical results or ground-truth emotions.'),
    ('Local update', 'Two losses → one update', 'Known labels + Accepted pseudo-labels · Joint training', local_update, 9000,
     'Within Client A, a labeled example with known neutral emotion supplies supervised cross-entropy. Accepted Speech 01 supplies happy as a pseudo-label target. The deferred sample is excluded from the pseudo-label loss. Both losses enter the same local update, with beta controlling the unlabeled contribution. This is joint optimization, not two independent model training phases.'),
    ('FedAvg', 'Parameters → shared model', 'Parameter upload · Data-weighted FedAvg · Broadcast', aggregate, 9000,
     'Clients upload local model parameters. Their raw speech remains on device. The server combines participating client parameters using FedAvg weighted by local data size, producing the next global model. It broadcasts those parameters to clients for the next round. The server requires no speech dataset. This illustrates data locality, not a formal privacy guarantee.'),
]

STEPS = [dict(short_title=short, title=title, caption=caption,
              art=scene(index, title, draw(), description), duration_ms=duration,
              title_in_art=True)
         for index, (short, title, caption, draw, duration, description) in enumerate(_CONTENT)]
