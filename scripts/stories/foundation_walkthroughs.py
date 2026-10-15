"""Connected source-bound AE-PSL and MaTU method walkthroughs.

AE-PSL: arXiv:2607.17913v1, §4.1–4.2. GA and CSA train both AE
halves; only decoders are averaged. Fine-tuning freezes the compressors,
passes CLS unchanged, sums local losses, and returns latent and CLS gradients.
MaTU: arXiv:2502.06376v3, §3.1–3.2, Eqs. 2–7. The small vectors are
arithmetic teaching inputs, not experimental observations. Server combination
is labelled 'combine' because the source prose and Eq. 7 differ in scaling.
"""
from fractions import Fraction
from html import escape
from research_icons import research_icon


def icon(name):
    return research_icon(name, 'fw-icon')


def reveal(body, at=0, cls=''):
    return f'<div class="{cls}" data-reveal="{at}">{body}</div>'


def arrow(direction='right'):
    return f'<span class="fw-arrow fw-arrow-{direction}" aria-hidden="true">→</span>'


def badge(name, label):
    return f'<span class="fw-badge">{icon(name)}{label}</span>'


def network(kind, index):
    actions = {
        'ae': [('E + D', 'back'), ('Local alignment', 'local'), ('Decoders', 'out'), ('Z + CLS', 'out'), ('Loss ⇄ gradients', 'both'), ('Local update', 'local')],
        'matu': [('Local tasks', 'local'), ('Unify', 'local'), ('Vector + modulators', 'out'), ('Same task', 'local'), ('Related tasks', 'local'), ('Updated vector', 'back')],
    }
    label, direction = actions[kind][index]
    active = ('server' if index in (0, 3, 4) else 'clients') if kind == 'ae' else ('clients' if index < 3 else 'server')
    details = ('Inputs + labels', 'Inputs + labels') if kind == 'ae' else ('Tasks A + B', 'Tasks A + C')
    clients = ''.join(f'<div class="fw-endpoint {"fw-active" if active == "clients" else ""}">{icon("client")}<div><strong>Client {i+1}</strong><small>{detail}</small></div></div>' for i, detail in enumerate(details))
    return f'<div class="fw-network fw-direction-{direction}" data-fw-network="{kind}" data-active-role="{active}"><div class="fw-network-clients">{clients}</div><div class="fw-network-link"><strong>{label}</strong><div class="fw-wire"><i></i>{arrow()}</div></div><div class="fw-endpoint fw-network-server {"fw-active" if active == "server" else ""}">{icon("server")}<div><strong>Shared server</strong><small>{"Model + autoencoder" if kind == "ae" else "Task vectors"}</small></div></div></div>'


def feature(label='H', latent=False, restored=False):
    shades = [.55, .2, .8, .35, .7, .45, .8, .35, .6]
    cells = ''.join(f'<i style="--fw-shade:{v}"></i>' for v in shades[:3 if latent else 9])
    return f'<div class="fw-feature {"fw-latent" if latent else ""} {"fw-restored" if restored else ""}"><div class="fw-feature-cells" aria-hidden="true">{cells}</div><strong>{label}</strong></div>'


def codec(kind, label, frozen=False):
    status = icon('frozen') if frozen else icon('train')
    return f'<div class="fw-codec fw-{kind}" data-fw-module="{kind}" data-fw-trainable="{str(not frozen).lower()}">{icon(kind)}<strong>{label}</strong><span class="fw-codec-state">{status}{"Fixed" if frozen else "Train"}</span></div>'


def frozen_features(label='Frozen feature extractor'):
    return f'<div class="fw-feature-source" data-fw-module="feature-extractor" data-fw-trainable="false">{icon("transformer")}<strong>{label}</strong>{icon("frozen")}</div>'


def reconstruction(location, compact=False):
    return f'<div class="fw-reconstruction {"fw-reconstruction-small" if compact else ""}" data-fw-operation="reconstruction-loss" data-fw-location="{location}"><span>H</span><div><strong>MSE</strong><small>‖H − Ĥ‖²</small></div><span>Ĥ</span></div>'


def ae_general():
    source = '<div class="fw-preparation-source">'+badge('globe', 'Public images')+arrow()+frozen_features()+'</div>'
    flow = '<div class="fw-ae-chain">' + reveal(feature('H'), 0) + reveal(codec('encoder', 'E'), 650) + reveal(feature('Z', True), 1400) + reveal(codec('decoder', 'D'), 2100) + reveal(feature('Ĥ', restored=True), 2900) + '</div>'
    return source + flow + reveal(reconstruction('server'), 3700) + reveal('<div class="fw-foot">'+badge('autoencoder', 'Aligned E + D')+'<span>→ each client</span></div>', 4600)


def ae_local():
    cards = []
    for client in (1, 2):
        body = f'<div class="fw-card fw-local-alignment"><header>{icon("client")}<strong>Client {client}</strong><span>Local images</span></header>' + frozen_features('Frozen features')
        body += '<div class="fw-local-ae">' + feature('H') + codec('encoder', f'E<sub>{client}</sub>') + feature('Z', True) + codec('decoder', f'D<sub>{client}</sub>') + feature('Ĥ', restored=True) + '</div>'
        body += reconstruction(f'client-{client}', True) + '</div>'
        cards.append(reveal(body, (client - 1) * 700))
    return '<div class="fw-pair">'+''.join(cards)+'</div>' + reveal('<div class="fw-foot">'+badge('train', 'E + D adapt locally')+'<span>One local epoch</span></div>', 2800)


def ae_share_decoder():
    clients = []
    for client in (1, 2):
        kept = f'<div class="fw-retained" data-fw-retained="local-encoder">{icon("encoder")}<strong>E<sub>{client}</sub></strong><small>Stays local</small></div>'
        upload = f'<div class="fw-decoder-upload" data-fw-message="decoder-weights" data-from="client-{client}" data-to="server">{icon("decoder")}<strong>D<sub>{client}</sub></strong>{icon("upload")}</div>'
        clients.append(reveal(f'<div class="fw-decoder-client"><header>{icon("client")}<strong>Client {client}</strong></header><div>{kept}{upload}</div></div>', (client - 1) * 650))
    averaged = '<div class="fw-decoder-mean" data-fw-operation="decoder-mean">'+icon('aggregate')+'<span class="fw-eyebrow">Decoder weights only</span><strong>D̄ = mean(D₁, D₂)</strong>'+codec('decoder', 'Shared D̄', True)+'</div>'
    return '<div class="fw-aggregation-layout"><div class="fw-decoder-clients">'+''.join(clients)+'</div>'+reveal(arrow(), 1200, 'fw-bridge')+reveal(averaged, 2100)+'</div>' + reveal('<div class="fw-foot">'+badge('frozen', 'Freeze all E + shared D̄')+'<span>Start fine-tuning</span></div>', 3600)


def ae_forward():
    client = '<div class="fw-card fw-split-card"><header>'+icon('client')+'<strong>Client</strong></header><div class="fw-train-model">'+icon('transformer')+'<strong>Client model</strong>'+badge('adapt', 'LoRA')+'</div>'
    client += '<div class="fw-mini-codec">'+feature('Patches H')+codec('encoder', 'E', True)+feature('Z', True)+'</div><div class="fw-cls-bypass"><strong>CLS</strong><span>Bypass AE</span>'+arrow()+'</div></div>'
    packet = '<div class="fw-cut-packet" data-fw-message="activations" data-from="client" data-to="server"><span class="fw-eyebrow">Across the cut</span><div data-fw-channel="patch-latents" data-compressed="true">'+feature('Z', True)+'</div><span class="fw-cls-chip" data-fw-channel="cls" data-compressed="false">CLS</span></div>'
    server = '<div class="fw-card fw-split-card"><header>'+icon('server')+'<strong>Server</strong></header><div class="fw-mini-codec">'+feature('Z', True)+codec('decoder', 'D̄', True)+feature('Ĥ', restored=True)+'</div><div class="fw-predict-model" data-fw-operation="server-predict"><span class="fw-cls-chip">CLS</span><span>+ Ĥ</span>'+arrow()+icon('transformer')+'<strong>Classifier</strong></div><div class="fw-prediction-back">'+arrow('left')+'<strong>ŷ</strong><span>Prediction → client</span></div></div>'
    return '<div class="fw-split-layout">'+reveal(client, 0)+reveal(packet, 1500)+reveal(server, 2800)+'</div>' + reveal('<div class="fw-foot"><strong>Patch latents · compressed</strong><span>CLS · unchanged</span></div>', 4300)


def ae_backward():
    losses = '<div class="fw-local-losses"><div><span>Client 1</span><strong>ŷ₁ + y₁ → L₁</strong></div><div><span>Client 2</span><strong>ŷ₂ + y₂ → L₂</strong></div></div>'
    objective = '<div class="fw-loss-sum" data-fw-loss-reduction="sum">'+icon('aggregate')+'<strong>L<sub>g</sub> = L₁ + L₂</strong><small>Local labels → local losses</small></div>'
    model = '<div class="fw-server-backward" data-fw-operation="server-backward">'+icon('server')+'<div><strong>One backward pass</strong><small>Server model + fixed decoder</small></div>'+icon('train')+'</div>'
    gradients = '<div class="fw-gradient-channels"><div data-fw-message="gradients" data-channel="patch-latents" data-from="server" data-to="client">'+arrow('left')+feature('∇Z', True)+'<strong>Latent gradient</strong></div><div data-fw-message="gradients" data-channel="cls" data-from="server" data-to="client">'+arrow('left')+'<span class="fw-cls-chip">∇CLS</span><strong>Uncompressed</strong></div></div>'
    return reveal(losses, 0)+reveal(objective, 900)+reveal(model, 1800)+reveal(gradients, 3300)


def ae_client_update():
    latent = '<div class="fw-local-backward-path"><div class="fw-lora-update" data-fw-operation="client-update" data-trainable="LoRA">'+icon('transformer')+'<strong>Client LoRA</strong>'+badge('train', 'Update')+'</div>'+arrow('left')+codec('encoder', 'E', True)+arrow('left')+feature('∇Z', True)+'</div>'
    bypass = '<div class="fw-cls-return"><span>Client model</span>'+arrow('left')+'<strong>∇CLS</strong><small>Direct path</small></div>'
    return '<div class="fw-client-update-frame"><header>'+icon('client')+'<strong>On every client</strong></header>'+reveal(latent, 0)+reveal(bypass, 1700)+'</div>'+reveal('<div class="fw-update-rule">'+badge('frozen', 'AE weights fixed')+badge('train', 'Gradients pass through')+'</div>', 2800)+reveal('<div class="fw-next">'+icon('exchange')+'<strong>Next mini-batch</strong><span>Updated model → new features</span></div>', 3900)


def sign(value):
    return (value > 0) - (value < 0)


def unify_task_vectors(vectors):
    """Eq. 2: sign of the sum, then greatest magnitude with that sign."""
    result = []
    for values in zip(*vectors):
        elected = sign(sum(values))
        result.append(elected * max((abs(x) for x in values if sign(x) == elected), default=0))
    return result


def task_modulator(task, unified):
    """§3.2: binary sign agreement and total-absolute-magnitude correction."""
    mask = [int(t * u > 0) for t, u in zip(task, unified)]
    denominator = sum(abs(m * u) for m, u in zip(mask, unified))
    return mask, sum(abs(t) for t in task) / denominator


def sign_similarity(left, right):
    """Eq. 5, including zero signs rather than silently counting equality."""
    return (1 + sum(sign(a) * sign(b) for a, b in zip(left, right)) / len(left)) / 2


TASK_UPDATES = {'A': [2, -1, 4, 1], 'B': [1, -3, -2, 2]}
UNIFIED = unify_task_vectors(list(TASK_UPDATES.values()))
MODULATORS = {task: task_modulator(values, UNIFIED) for task, values in TASK_UPDATES.items()}
# The same transmitted task trace continues on the server. Client 2's local
# modulation retains A at coordinates 1–3 and C at coordinate 4. Opposing A
# signs at coordinate 3 are suppressed by the receiving task's agreement mask.
SAME_TASK_CLIENT_SIGNS = {1: [sign(x) for x in TASK_UPDATES['A']], 2: [1, -1, -1, 0]}
SERVER_SIGNS = {
    'A': [sign(sum(values)) for values in zip(*SAME_TASK_CLIENT_SIGNS.values())],
    'B': [m * sign(u) for m, u in zip(MODULATORS['B'][0], UNIFIED)],
    'C': [0, 0, 0, -1],
}


def vector(values, label='', cls='', key='', mode='number', selected=()):
    cells = []
    for i, value in enumerate(values):
        display = ('+' if value > 0 else '−' if value < 0 else '0') if mode == 'sign' else str(value) if mode == 'mask' else f'{value:+g}'.replace('-', '−')
        tone = f' fw-cell-{selected[i].lower()}' if selected else ''
        cells.append(f'<span class="fw-value{tone}{" fw-masked" if mode == "mask" and not value else ""}">{display}</span>')
    return f'<div class="fw-vector-row {cls}" data-fw-vector="{key}" data-values="{",".join(map(str,values))}"><strong>{label}</strong><div class="fw-vector">{"".join(cells)}</div></div>'


def task_badge(task):
    return f'<span class="fw-task-badge fw-task-{task.lower()}">{icon("task")}<strong>Task {task}</strong></span>'


def matu_train():
    origin = '<div class="fw-origin">'+icon('model')+'<div><strong>Pretrained θ<sub>p</sub></strong><small>One shared origin</small></div></div>'
    cards = []
    for i, task in enumerate(('A', 'B')):
        body = f'<div class="fw-card fw-task-card fw-task-{task.lower()}"><header>{task_badge(task)}{icon("train")}</header><div class="fw-task-equation"><strong>τ<sub>{task}</sub></strong><span>= θ<sub>{task}</sub> − θ<sub>p</sub></span></div>'+vector(TASK_UPDATES[task], key=f'task-{task}')+'</div>'
        cards.append(reveal(body, 900 + i * 650))
    return origin+'<div class="fw-task-branches">'+''.join(cards)+'</div>'+reveal('<div class="fw-foot"><strong>Train each task</strong><span>Keep a common coordinate system</span></div>', 2800)


def matu_elect():
    summed = [sum(values) for values in zip(*TASK_UPDATES.values())]
    return '<div class="fw-election-table">'+vector(TASK_UPDATES['A'], 'Task A', 'fw-task-a', 'task-A')+reveal(vector(TASK_UPDATES['B'], 'Task B', 'fw-task-b', 'task-B'), 450)+reveal(vector(summed, 'Sum', key='sum'), 1400)+reveal(vector([sign(x) for x in summed], 'Elect sign', key='sign', mode='sign'), 2400)+reveal(vector(UNIFIED, 'Unified τ', 'fw-unified', 'unified', selected=['A', 'B', 'A', 'B']), 3500)+'</div>'+reveal('<div class="fw-foot">'+badge('merge', 'Sign of sum')+badge('task-vector', 'Largest aligned magnitude')+'</div>', 4600)


def matu_modulate():
    cards = []
    for i, task in enumerate(('A', 'B')):
        mask, scale = MODULATORS[task]
        ratio = Fraction(scale).limit_denominator()
        body = f'<div class="fw-card fw-modulator-card fw-task-{task.lower()}"><header>{task_badge(task)}{icon("mask")}</header>'+vector(mask, 'Mask', key=f'mask-{task}', mode='mask')+f'<div class="fw-task-scale">{icon("scale")}<strong>λ<sub>{task}</sub> = {ratio.numerator}/{ratio.denominator}</strong><span>Magnitude rescaler</span></div></div>'
        cards.append(reveal(body, 900 + i * 700))
    return '<div class="fw-unified-payload" data-fw-message="unified-and-modulators" data-from="client" data-to="server">'+vector(UNIFIED, 'Unified τ', 'fw-unified', 'unified')+'<div class="fw-pair">'+''.join(cards)+'</div></div>'+reveal('<div class="fw-foot">'+badge('upload', 'One vector + task modulators')+'<span>→ server</span></div>', 3200)


def matu_same_task():
    clients = ''.join(reveal(f'<div class="fw-same-task-client"><header>{icon("client")}<strong>Client {client}</strong>{task_badge("A")}</header>'+vector(signs, mode='sign', key=f'client-{client}-task-A')+'</div>', (client-1)*700) for client, signs in SAME_TASK_CLIENT_SIGNS.items())
    agreement = '<div class="fw-task-agreement" data-fw-operation="same-task-aggregation">'+icon('mask')+'<strong>Task agreement</strong><div class="fw-agreement-cells" aria-label="The opposing signs at coordinate three are suppressed to zero"><i></i><i></i><i class="fw-disagreed"></i><i></i></div><small>Data-size weights · γ<sub>n</sub></small></div>'
    output = '<div class="fw-task-aggregate">'+task_badge('A')+icon('aggregate')+'<strong>τ̂<sub>A</sub></strong><span>Same-task update</span>'+vector(SERVER_SIGNS['A'], 'Signs', 'fw-task-a', 'server-task-A', mode='sign')+'</div>'
    return '<div class="fw-same-task-layout"><div class="fw-same-task-clients">'+clients+'</div>'+reveal(arrow(), 1300, 'fw-bridge')+reveal(agreement, 2100)+'</div>'+reveal(output, 3500)+reveal('<div class="fw-foot"><strong>Clients sharing Task A</strong><span>Repeat per task</span></div>', 4300)


def matu_transfer():
    target = vector(SERVER_SIGNS['A'], 'Target A', 'fw-task-a', 'server-task-A', mode='sign')
    candidates = []
    for i, task in enumerate(('B', 'C')):
        similarity = sign_similarity(SERVER_SIGNS['A'], SERVER_SIGNS[task])
        selected = similarity > .5
        products = [sign(a) * sign(b) for a, b in zip(SERVER_SIGNS['A'], SERVER_SIGNS[task])]
        positive, negative, neutral = (products.count(value) for value in (1, -1, 0))
        relation = f'{positive} aligned' if positive else f'{negative} opposed'
        row = f'<div class="fw-similarity-row fw-task-{task.lower()} {"fw-selected" if selected else "fw-rejected"}" data-fw-similarity="{similarity}" data-selected="{str(selected).lower()}">'+vector(SERVER_SIGNS[task], f'Task {task}', key=f'server-task-{task}', mode='sign')+f'<div class="fw-similarity-score"><span>{relation}<br/>{neutral} neutral</span><strong>{similarity:.3f}</strong><b>{"Use" if selected else "Skip"}</b></div></div>'
        candidates.append(reveal(row, 800 + i * 800))
    rule = '<div class="fw-transfer-rule">'+icon('filter')+'<strong>S &gt; 0.5</strong><span>Top-κ related tasks</span></div>'
    applied = '<div class="fw-transfer-applied">'+task_badge('B')+arrow()+badge('mask', 'Target A mask')+arrow()+task_badge('A')+'</div>'
    return '<div class="fw-similarity-table">'+target+''.join(candidates)+'</div>'+reveal(rule, 2500)+reveal(applied, 3500)+reveal('<div class="fw-foot"><strong>Weight by similarity</strong><span>Combine same-task + cross-task updates</span></div>', 4300)


def matu_return():
    unified = '<div class="fw-return-package" data-fw-operation="reunify" data-before="client-return">'+icon('merge')+'<div><strong>Updated unified τ′</strong><small>New masks + scales</small></div>'+icon('download')+vector(SERVER_SIGNS['A'], key='next-unified', mode='sign')+'</div>'
    cards = []
    for i, task in enumerate(('A', 'B')):
        body = f'<div class="fw-card fw-recover-card fw-task-{task.lower()}" data-fw-operation="recover-task" data-task="{task}"><header>{task_badge(task)}</header><div class="fw-modulation">{icon("mask")}<strong>m<sub>{task}</sub> × λ<sub>{task}</sub></strong><span>⊙ τ′</span></div><div class="fw-recovered-weight"><small>Pretrained + task update</small><strong>θ<sub>p</sub> + τ̇<sub>{task}</sub></strong></div>'+vector(SERVER_SIGNS['A'], 'Update signs', 'fw-recovered-signs', f'recovered-{task}', mode='sign')+'</div>'
        cards.append(reveal(body, 1600 + i * 600))
    return reveal(unified, 0)+'<div class="fw-return-client"><header>'+icon('client')+'<strong>Client 1</strong></header><div class="fw-pair">'+''.join(cards)+'</div></div>'+reveal('<div class="fw-next">'+icon('exchange')+'<strong>Next local round</strong><span>Task A · Task B</span></div>', 3600)


def step(kind, index, short_title, title, caption, body, description, duration=8500):
    phases = {'ae': ['GENERAL ALIGNMENT · SERVER', 'CLIENT-SPECIFIC ALIGNMENT', 'ALIGNMENT → FINE-TUNING', 'FINE-TUNING · FORWARD', 'FINE-TUNING · SERVER BACKWARD', 'FINE-TUNING · CLIENT BACKWARD'],
              'matu': ['CLIENT 1 · LOCAL TRAINING', 'CLIENT 1 · TASK UNIFICATION', 'CLIENT 1 → SERVER', 'SERVER · SAME-TASK AGGREGATION', 'SERVER · RELATED-TASK TRANSFER', 'SERVER → CLIENT 1']}
    art = f'<div class="story-art fw-art fw-{kind}-art" role="group" aria-label="{escape(description, quote=True)}">{network(kind,index)}<div class="fw-scene-body"><div class="fw-stage-heading"><span class="fw-eyebrow">{phases[kind][index]}</span><h3>{title}</h3></div>{body}</div></div>'
    return {'short_title': short_title, 'title': title, 'caption': caption, 'art': art, 'duration_ms': duration, 'title_in_art': True}


AE_STEPS = [
    step('ae', 0, 'Public alignment', 'Learn the feature space', 'Public features → encoder → latent → decoder · Reconstruction loss', ae_general(), 'General Alignment runs on the server using public images. A frozen client partition supplies patch features H. Both encoder E and decoder D train against reconstruction mean squared error. The aligned pair initializes each client.', 9500),
    step('ae', 1, 'Local alignment', 'Adapt to each client', 'Local reconstruction · Frozen features · Train both AE halves', ae_local(), 'Client-Specific Alignment trains each client’s encoder and decoder locally for one epoch, using local reconstruction loss and a frozen feature extractor. The server model is not needed for this phase.'),
    step('ae', 2, 'Share decoder', 'Local encoders · shared decoder', 'Keep local encoders · Average decoder weights · Freeze compressors', ae_share_decoder(), 'Each client retains its adapted encoder and uploads only decoder weights. The server takes their arithmetic mean to obtain one shared decoder. All encoder and decoder weights are frozen for downstream fine-tuning.'),
    step('ae', 3, 'Send features', 'Compress patches · preserve CLS', 'Compact patch latents + unchanged CLS → decoder → server classifier', ae_forward(), 'Client LoRA features split into patch tokens and CLS. Frozen E compresses patches into Z; CLS bypasses compression. The server’s frozen shared decoder reconstructs patches, which join CLS in the server model and classifier. Predictions return to clients.', 10000),
    step('ae', 4, 'Backpropagate', 'One loss sum · two return paths', 'Local losses → shared backward · Latent + CLS gradients → clients', ae_backward(), 'Clients compute losses using local labels. The server sums these losses, performs one backward pass, updates its model, and returns gradients with respect to the patch latents Z and the uncompressed CLS token. The decoder remains fixed.', 9500),
    step('ae', 5, 'Update locally', 'Fixed encoder · trainable model', 'Backpropagate through frozen E · Update client LoRA · Next mini-batch', ae_client_update(), 'The latent gradient passes through the frozen encoder to update client LoRA parameters. The CLS gradient follows its direct bypass route. Frozen encoder weights still permit input gradients. The next mini-batch starts with updated client and server models.'),
]

MATU_STEPS = [
    step('matu', 0, 'Train tasks', 'Two tasks · one origin', 'Separate local training · Task vector = fine-tuned − pretrained', matu_train(), 'Client 1 trains tasks A and B separately from a common pretrained origin. Four-coordinate arithmetic inputs are A=(2,-1,4,1) and B=(1,-3,-2,2); these explain the algorithm rather than report trained model values.'),
    step('matu', 1, 'Unify', 'Elect direction · retain magnitude', 'Sign of summed updates · Largest magnitude aligned with that sign', matu_elect(), 'At each coordinate, elect the sign of the sum, then take the greatest magnitude among entries agreeing with that sign. The same A and B vectors produce unified vector (2,-3,4,2). This is not majority voting or arithmetic averaging.', 10000),
    step('matu', 2, 'Attach modulators', 'One vector · distinct task updates', 'Binary sign masks + magnitude scales · Compact client upload', matu_modulate(), 'Task A has mask (1,1,1,1) and scale 8/11. Task B has mask (1,1,0,1) and scale 8/7. Each scalar matches the original task vector’s total absolute magnitude after masking. The shared vector and modulators approximate task-specific updates.'),
    step('matu', 3, 'Same task', 'Combine clients sharing a task', 'Task agreement mask · Data-size weights · Same-task aggregation', matu_same_task(), 'The same task-A trace continues after local modulation. Client 1 contributes signs (+,-,+,+), while client 2 contributes (+,-,-,0). The opposing third signs give zero agreement and suppress that coordinate. The same-task aggregate has signs (+,-,0,+), carried into the next scene. Client 2’s task-C modulator retains only a negative fourth coordinate.'),
    step('matu', 4, 'Related tasks', 'Transfer along shared directions', 'Sign similarity → threshold → top-κ · Receiving-task mask', matu_transfer(), 'The target task-A signs remain (+,-,0,+). Task B’s uploaded mask also removes its third coordinate, giving (+,-,0,+); task C contributes (0,0,0,-). Equation 5 gives similarity .875 for A and B, and .375 for A and C, because zero sign products contribute neutrally. Only B passes the .5 threshold. Transfer uses A’s receiving mask, so its third coordinate remains zero.', 10000),
    step('matu', 5, 'Recover tasks', 'Reunify → return → recover', 'Updated vector + modulators → task-specific weights → next local round', matu_return(), 'After combining same-task and eligible cross-task information, updated A and B retain signs (+,-,0,+). Reunification therefore also preserves the zero third coordinate. Client 1 receives this unified vector with new masks and scales; both recovered task updates retain zero there before addition to the pretrained origin.'),
]
