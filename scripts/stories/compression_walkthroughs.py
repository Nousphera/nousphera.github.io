"""Connected compression mechanisms, with illustrative arithmetic in accessible text.

FedCompress: arXiv:2401.14211v3 §1, Eqs.1–2 and Fig.1. Follow the method
prose for plateau-triggered capacity changes, not the ambiguous Appendix A
update sign. FedCode: arXiv:2311.09270v1 §4.1–4.2, Algorithms1–2. Ordinary
server updates remap existing weights; FedAvg belongs to upstream calibration.
No calibration frequency is assigned to F1/F2 because the source conflicts.
All toy weights, output bars and trend shapes are explanatory, not measurements.
"""
from html import escape

from research_icons import research_icon


FC_A = [-1, -1, 1, 1]
FC_B = [0, 2, 0, 2]
FC_MEAN = [-.5, .5, .5, 1.5]
FC_STUDENT = [.1, .1, .1, 1.2]
CODE_GLOBAL = [-1, -1, 1, 1]
CODE_LOCAL = [-.8, .7, -.6, 1.2]
CODE_MAPPED = [-1, 1, -1, 1]
CODE_TRAINED = [-1.4, 1.2, -1, 1.6]
CODE_A = [-1.2, 1.4]
CODE_B = [-.6, .9]
CODE_UNION = [-1.2, -.6, .9, 1.4]
CODE_NEXT = [-1.2, -1.2, .9, .9]
# Value identity is independent of codebook ordering and tensor position.
# The four received FedCode centers retain four colors/border patterns throughout.
VALUE_TONES = {
    -1.4: 0, -1.2: 0, -1: 0, -.8: 0, -.6: 2, -.5: 0,
    0: 0, .1: 0, .5: 1, .7: 1, .8: 1, .9: 3,
    1: 1, 1.2: 1, 1.4: 1, 1.5: 2, 1.6: 1, 2: 1,
}


def icon(name):
    return research_icon(name, 'cw-icon')


def reveal(body, at=0, cls=''):
    return f'<div class="{cls}" data-reveal="{at}">{body}</div>'


def arrow(label=''):
    return f'<span class="cw-arrow" aria-hidden="true">→</span>' + (f'<span class="cw-flow-label">{label}</span>' if label else '')


def number(value):
    return f'{value:g}'.replace('-', '−')


def raw(values):
    return ','.join(f'{value:g}' for value in values)


def weights(label, values, key, scan=False):
    cells = []
    for i, value in enumerate(values):
        tone = VALUE_TONES[value]
        cell = f'<span class="cw-weight cw-tone-{tone}" data-position="{i + 1}" data-value="{value:g}" data-value-tone="{tone}"><small>{i + 1:02}</small><b>{number(value)}</b></span>'
        cells.append(reveal(cell, 1600 + 500 * i, 'cw-weight-slot') if scan else cell)
    return f'<div class="cw-weights" data-weights="{key}" data-values="{raw(values)}"><strong class="cw-label">{label}</strong><div class="cw-weight-grid">{"".join(cells)}</div></div>'


def centers(label, values, key, compact=False):
    chips = ''.join(f'<span class="cw-center cw-tone-{VALUE_TONES[value]}" data-value="{value:g}" data-value-tone="{VALUE_TONES[value]}"><small>{i}</small><b>{number(value)}</b></span>' for i, value in enumerate(values))
    return f'<div class="cw-codebook{" cw-compact" if compact else ""}" data-codebook="{key}" data-values="{raw(values)}"><strong class="cw-label">{icon("codebook")}{label}</strong><div class="cw-centers">{chips}</div></div>'


def indices(values, key, codebook, label='Position indices'):
    cells = ''.join(f'<span class="cw-index cw-tone-{VALUE_TONES[codebook[v]]}" data-value="{codebook[v]:g}" data-value-tone="{VALUE_TONES[codebook[v]]}"><small>{i + 1:02}</small><b>{v}</b></span>' for i, v in enumerate(values))
    return f'<div class="cw-indices" data-indices="{key}" data-values="{raw(values)}"><strong class="cw-label">{icon("mask")}{label}</strong><div class="cw-weight-grid">{cells}</div></div>'


def packet(label, center_values, key, assignments=None, direction=None):
    transfer = f' data-transfer="{direction}" data-payload="codebook{" indices" if assignments is not None else ""}"' if direction else ''
    content = centers(label, center_values, key, True)
    if assignments is not None:
        content += '<span class="cw-plus">+</span>' + indices(assignments, key, center_values)
    return f'<div class="cw-packet"{transfer}>{content}</div>'


def badge(name, text, cls=''):
    return f'<span class="cw-badge {cls}">{icon(name)}{text}</span>'


def network(direction, action):
    server_active = ' cw-active' if direction in ('server', 'down', 'both') else ''
    client_active = ' cw-active' if direction in ('local', 'up', 'both') else ''
    return f'''<div class="cw-network cw-direction-{direction}" data-cw-network="true" data-direction="{direction}">
      <div class="cw-endpoint{server_active}" data-role="server">{icon('server')}<div><strong>Server</strong><span>Global model</span></div></div>
      <div class="cw-link"><span>{action}</span><div class="cw-wire"><i></i><b>→</b></div></div>
      <div class="cw-clients"><div class="cw-endpoint{client_active}" data-role="client">{icon('client')}<div><strong>Client A</strong><span>Local model</span></div></div><div class="cw-peers">Client B · Other clients</div></div>
    </div>'''


def step(short_title, title, caption, body, duration, direction, action, description, kind='ordinary'):
    scope = {'local': 'ON EACH CLIENT', 'up': 'CLIENTS → SERVER', 'server': 'ON THE SERVER', 'down': 'SERVER → CLIENTS', 'both': 'PERIODIC · BOTH DIRECTIONS'}[direction]
    return {'short_title': short_title, 'title': title, 'caption': caption,
            'duration_ms': duration, 'title_in_art': True,
            'art': f'''<div class="story-art cw-art" role="group" data-round-kind="{kind}" aria-label="{escape(description, quote=True)}">{network(direction, action)}
              <div class="cw-scene-body"><div class="cw-stage-heading"><span class="cw-kicker">{scope}</span><h3>{title}</h3></div>{body}</div></div>'''}


def compress_cluster():
    phases = '<div class="cw-phase-strip">' + badge('train', 'Warm-up') + arrow() + badge('cluster', '<strong>Task + Clustering</strong>') + '</div>'
    rows = weights('After warm-up', [-1.2, -.8, .8, 1.2], 'warmup')
    rows += reveal('<div class="cw-row-flow">↓ <strong>Shared centroids</strong></div>', 900)
    rows += weights('Clustered client A', FC_A, 'client-a', scan=True)
    return reveal(phases) + '<div class="cw-transform">' + rows + '</div>' + reveal('<div class="cw-result-strip">' + centers('Two learned values', [-1, 1], 'client-a') + '<span class="cw-summary"><b>4</b> weights<br/><strong>2</strong> values</span></div>', 4000)


def compress_upload():
    clients = []
    for name, vector, book, idx, at in [('A', FC_A, [-1, 1], [0, 0, 1, 1], 300), ('B', FC_B, [0, 2], [0, 1, 0, 1], 1800)]:
        clients.append(reveal(f'<div class="cw-upload-row">{weights("Client " + name, vector, "client-" + name.lower())}<span class="cw-convert">{icon("compress")}{arrow()}</span>{packet("Centers", book, "upload-" + name.lower(), idx, "up")}</div>', at))
    return '<div class="cw-uploads">' + ''.join(clients) + '</div>' + reveal('<div class="cw-transfer-note">' + badge('upload', '<strong>Compressed models</strong>') + arrow() + badge('server', 'Server') + '</div>', 3400)


def compress_average():
    rows = reveal(weights('Client A', FC_A, 'client-a')) + reveal(weights('Client B', FC_B, 'client-b'), 800)
    rows += reveal(f'<div class="cw-average-rule" data-aggregation="fedavg">{icon("aggregate")}<strong>FedAvg</strong><span>Equal data shares</span></div>', 1700)
    rows += reveal(weights('Global weights', FC_MEAN, 'aggregated'), 2600)
    note = '<div class="cw-count-change"><span><b>2</b> values / client</span>' + arrow() + '<strong><b>3</b> global values</strong></div>'
    return '<div class="cw-average-rows">' + rows + '</div>' + reveal(note, 3900)


def prediction_bars(values, key):
    return f'<div class="cw-output-bars" data-output="{key}" aria-hidden="true">' + ''.join(f'<i style="--cw-height:{v}%"></i>' for v in values) + '</div>'


def compress_distill():
    data = f'<div class="cw-distill-data" data-distill-data="true" data-location="server" data-labels="none" data-distribution="ood" data-feeds="teacher student">{icon("unlabeled")}<strong>Unlabeled OOD data</strong><span>Server auxiliary data</span></div>'
    teacher = f'<div class="cw-distill-model cw-teacher"><span class="cw-role">{icon("teacher")}Global teacher</span>{weights("Aggregated weights", FC_MEAN, "teacher")}{prediction_bars([60, 30, 10], "teacher")}<span class="cw-small">Soft predictions</span></div>'
    student = f'<div class="cw-distill-model cw-student"><span class="cw-role">{icon("student")}Clustered student</span>{weights("Shared values", FC_STUDENT, "student")}{prediction_bars([58, 31, 11], "student")}<span class="cw-small">Matching predictions</span></div>'
    return reveal(data) + '<div class="cw-distillation"><span class="cw-data-fork" aria-hidden="true"></span>' + reveal(teacher, 900) + reveal('<div class="cw-match">' + icon('distill') + '<strong>Match</strong>' + arrow() + '</div>', 1900) + reveal(student, 2700) + '</div>' + reveal('<div class="cw-objective" data-objective="kl weight-clustering">' + badge('align', '<strong>KL matching</strong>') + '<span>+</span>' + badge('cluster', '<strong>Weight clustering</strong>') + '</div>', 4100)


def embedding():
    return '<span class="cw-embedding" aria-hidden="true">' + ''.join(f'<i style="--cw-x:{x}%;--cw-y:{y}%"></i>' for x, y in [(12, 70), (27, 54), (40, 66), (47, 29), (64, 46), (69, 14), (84, 25)]) + '</span>'


def compress_capacity():
    local = f'<div class="cw-score-source" data-score="effective-rank" data-location="client">{icon("clients")}<div><strong>Local unlabeled data</strong><span>Embeddings → Effective rank</span></div>{embedding()}</div>'
    trend = f'''<div class="cw-score-trend" data-score-aggregation="data-weighted" data-capacity-trigger="moving-average-plateau"><div class="cw-trend-heading">{icon('server')}<strong>Data-weighted score</strong><span>Moving average</span></div><svg viewBox="0 0 320 88" class="cw-trend" preserveAspectRatio="none" aria-hidden="true"><path class="cw-trend-axis" d="M8 9V78H312"/><path class="cw-trend-line" d="M12 71 48 54 85 38 123 27 165 21 207 19 248 19 293 19"/><path class="cw-plateau-line" d="M180 12H306"/><circle cx="207" cy="19" r="3"/><circle cx="248" cy="19" r="3"/><circle cx="293" cy="19" r="3"/></svg><div class="cw-window"><span>Window · <b>3 rounds</b></span><span>Patience · <b>3 rounds</b></span></div></div>'''
    update = '<div class="cw-capacity" data-capacity-update="increase-within-budget">' + badge('chart', '<strong>Plateau</strong>') + arrow() + '<div class="cw-capacity-centers"><span class="cw-center-dot"></span><span class="cw-center-dot cw-second"></span><span class="cw-center-dot cw-added">+</span></div><div><strong>Increase capacity</strong><span>Next clustering · Within budget</span></div></div>'
    return reveal(local) + reveal('<div class="cw-row-flow">↑ <strong>Client scores</strong></div>', 700) + reveal(trend, 1500) + reveal(update, 3200)


def compress_broadcast():
    model = weights('Compressed global student', FC_STUDENT, 'student')
    payload = packet('Shared values', [.1, 1.2], 'global-student', [0, 0, 0, 1], 'down')
    clients = '<div class="cw-receiving-clients">' + ''.join(f'<div>{badge("client", "Client " + name)}{weights("Restored model", FC_STUDENT, "received-" + name.lower())}</div>' for name in ['A', 'B']) + '</div>'
    return reveal(model) + reveal('<div class="cw-row-flow">↓ <strong>Compress + Broadcast</strong></div>', 750) + reveal(payload, 1500) + reveal(clients, 2900) + reveal('<div class="cw-transfer-note">' + badge('exchange', '<strong>Next round</strong>') + '<span>Local training · Updated cluster budget</span></div>', 4200)


def code_parts():
    split = '<div class="cw-factorization">' + reveal(centers('Values', [-1, 1], 'global'), 900) + '<span class="cw-plus">+</span>' + reveal(indices([0, 0, 1, 1], 'global', [-1, 1]), 1800) + '</div>'
    return reveal(weights('Clustered global model', CODE_GLOBAL, 'global')) + reveal('<div class="cw-row-flow">↓ <strong>Separate values + positions</strong></div>', 500) + split + reveal('<div class="cw-channel-choice"><div>' + badge('download', '<strong>Send centers</strong>') + '<span>Ordinary round</span></div><div>' + badge('memory', '<strong>Keep positions</strong>') + '<span>Stored model</span></div></div>', 3000)


def code_client():
    received = packet('Received sorted codebook', [-1, 1], 'global', direction='down')
    mapping = weights('Stored local weights', CODE_LOCAL, 'stored-local')
    mapping += reveal('<div class="cw-nearest-rule">' + icon('search') + '<strong>Nearest center</strong><span>Per weight position</span></div>', 800)
    mapping += weights('Updated local weights', CODE_MAPPED, 'mapped-local', scan=True)
    return reveal(received) + '<div class="cw-transform" data-client-update="nearest-center">' + mapping + '</div>' + reveal('<div class="cw-transfer-note">' + badge('train', '<strong>Ready for local training</strong>') + '</div>', 4000)


def code_train():
    train = '<div class="cw-training">' + badge('data', 'Local data') + arrow() + badge('train', '<strong>Task learning</strong>') + '</div>'
    rows = weights('After local learning', CODE_TRAINED, 'trained-local')
    rows += reveal('<div class="cw-row-flow">↓ <strong>One K-means · Entire model</strong></div>', 900)
    rows += weights('Clustered local model', [-1.2, 1.4, -1.2, 1.4], 'clustered-local', scan=True)
    return reveal(train) + '<div class="cw-transform">' + rows + '</div>' + reveal('<div class="cw-code-upload">' + packet('Client A centers', CODE_A, 'client-a', direction='up') + '<span>' + icon('upload') + '<strong>Codebook only</strong></span></div>', 3900)


def code_server():
    books = '<div class="cw-client-books">' + centers('Client A', CODE_A, 'client-a', True) + '<span class="cw-plus">+</span>' + centers('Client B', CODE_B, 'client-b', True) + '</div>'
    combined = '<div class="cw-combined">' + centers('Concatenate + Sort', CODE_UNION, 'combined', True) + '</div>'
    mapping = weights('Existing global weights', CODE_GLOBAL, 'stored-global')
    mapping += '<div class="cw-row-flow">↓ <strong>Nearest received center</strong></div>'
    mapping += weights('Updated global weights', CODE_NEXT, 'remapped-global', scan=True)
    return reveal(books) + reveal(combined, 900) + reveal('<div class="cw-server-remap" data-server-update="nearest-center">' + mapping + '</div>', 1400)


def code_loop():
    clients = '<div class="cw-receiving-clients">' + ''.join(f'<div>{badge("client", "Client " + name)}{weights("Local positions", values, "next-client-" + name.lower())}</div>' for name, values in [('A', [-1.2, .9, -1.2, .9]), ('B', [-1.2, .9, .9, -1.2])]) + '</div>'
    return reveal(weights('Updated global weights', CODE_NEXT, 'remapped-global')) + reveal('<div class="cw-row-flow">↓ <strong>Recluster → New codebook</strong></div>', 800) + reveal(packet('Next shared centers', [-1.2, .9], 'next-global', direction='down'), 1600) + reveal(clients, 2900) + reveal('<div class="cw-transfer-note">' + badge('exchange', '<strong>Same centers · Local positions</strong>') + '</div>', 4200)


def code_calibration():
    timeline = '<div class="cw-round-strip"><span>' + icon('codebook') + '</span><span>' + icon('codebook') + '</span><span class="cw-calibration-round">' + icon('codebook') + '<b>+</b>' + icon('mask') + '<strong>When scheduled</strong></span><span>' + icon('codebook') + '</span></div>'
    decoded = weights('Sender positions restored', CODE_NEXT, 'calibrated')
    flow = '<div class="cw-calibration-decode">' + packet('Sender centers', [-1.2, .9], 'calibration', [0, 0, 1, 1], 'calibration') + '<div class="cw-decode-arrow">' + icon('decoder') + arrow() + '</div>' + decoded + '</div>'
    routes = f'<div class="cw-calibration-routes"><div data-direction="down">{icon("download")}<strong>Downlink</strong><span>Global model → Clients</span></div><div data-aggregation="fedavg" data-direction="up" data-input="reconstructed-client-models">{icon("upload")}<strong>Uplink</strong><span>Client models → <b>FedAvg</b></span></div></div>'
    return reveal(timeline) + reveal(flow, 1300) + reveal(routes, 3100)


FEDCOMPRESS_STEPS = [
    step('Cluster', 'Many weights · Few shared values', 'Warm-up → Task learning + Weight clustering', compress_cluster(), 8500, 'local', 'Local clustering',
         'Illustrative four-weight client model: after a task-only warm-up, joint task and clustering training yields values minus one, minus one, one, one. Four weights share two learned centers.'),
    step('Upload', 'Compact client models → Server', 'Centers + Position indices → Compressed client uploads', compress_upload(), 8500, 'up', 'Compressed models',
         'Client A and B upload their compressed models, represented by centers plus per-position indices. Illustrative A is minus one, minus one, one, one; B is zero, two, zero, two. Their centroids and assignments differ.'),
    step('Average', 'Averaging breaks the shared values', 'Position-wise FedAvg · 2 values per client → 3 global values', compress_average(), 9500, 'server', 'Model averaging',
         'Illustrative equal-data FedAvg averages matching weight positions of A and B. The global values become minus one half, one half, one half, and one and one half: three distinct values, compared with two on each client.'),
    step('Distill', 'Global teacher → Clustered student', 'Unlabeled server data → Prediction matching + Weight clustering', compress_distill(), 10000, 'server', 'Self-compression',
         'Server-side unlabeled out-of-distribution auxiliary data feed the aggregated teacher and clustered student. Temperature-scaled KL output matching plus a weight-clustering penalty restores a compact student. Weight and output values are illustrative, not measurements.'),
    step('Adapt capacity', 'Stalled score → More capacity', 'Local embeddings → Effective rank → Server trend → Cluster budget', compress_capacity(), 9500, 'up', 'Representation scores',
         'Clients compute effective rank from embeddings of unlabeled local data. The server forms a data-weighted score and monitors its moving average. The method prose uses a three-round window and patience, increasing the next cluster capacity on a plateau within an optional budget. The trend is illustrative.'),
    step('Broadcast', 'Compact model → Next round', 'Compressed global student → Clients · Updated cluster budget', compress_broadcast(), 9000, 'down', 'Compact global model',
         'The compressed global student is broadcast to clients for the next training round. Its center values and position indices reconstruct the same global starting model; the adaptive cluster budget guides subsequent clustering.'),
]

FEDCODE_STEPS = [
    step('Separate', 'Shared values + Weight positions', 'Small codebook · One index per weight position', code_parts(), 8500, 'server', 'Extract codebook',
         'An illustrative clustered global model has four weights minus one, minus one, one, one. A codebook stores the two values, while indices zero, zero, one, one identify each weight position. Ordinary FedCode transfers omit these indices.'),
    step('Map locally', 'Received centers → Local weights', 'Codebook download → Nearest-center mapping → Local training', code_client(), 9000, 'down', 'Codebook only',
         'The server sends the sorted codebook minus one and one, without position indices. Client weights minus point eight, point seven, minus point six and one point two map to their nearest centers at the same stored positions. The resulting arrangement differs from the server model; this is not exact reconstruction of the server tensor.'),
    step('Train + Send', 'Train → Cluster → Send centers', 'Local learning → Whole-model K-means → Codebook upload', code_train(), 9000, 'up', 'Client codebooks',
         'The client trains on its local data, then runs K-means across the entire model. Illustrative weights minus one point four, one point two, minus one and one point six cluster into centers minus one point two and one point four. Only the codebook is uploaded in this ordinary round.'),
    step('Map globally', 'Client centers → Global weights', 'Concatenate codebooks → Nearest-center global update', code_server(), 10000, 'server', 'Nearest-center update',
         'The server concatenates and sorts client A centers minus one point two, one point four and client B centers minus point six, point nine. Each existing global weight is replaced by its nearest received center. This is a nearest-center update, not FedAvg of full client tensors.'),
    step('Repeat', 'New centers → Next round', 'Recluster global weights → Broadcast centers → Local remapping', code_loop(), 9000, 'down', 'Next codebook',
         'The updated global model is clustered again to create its next codebook, minus one point two and point nine. Clients remap their own stored weight positions to those same centers; they need not share the server arrangement in an ordinary codebook-only round.'),
    step('Calibrate', 'Periodic calibration · Include positions', 'Centers + Compressed indices → Reconstruction · Upstream FedAvg', code_calibration(), 10000, 'both', 'Centers + Indices',
         'Calibration is a separately scheduled round type, not an extra step every round. Centers plus compressed position indices reconstruct the sender model. Downstream calibration restores the global model on clients; upstream calibration reconstructs client models before FedAvg. No F1 or F2 direction label is imposed because the source notation conflicts.', 'periodic-calibration'),
]
