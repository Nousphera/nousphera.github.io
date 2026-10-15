"""One MPSL training step, following arXiv:2502.06355v3, Fig. 1 and §3.2.

This is the late-fusion path: each modality is encoded independently with the
same server weights, then representations are joined within each client sample.
The paper describes loss uploads, batch-size-weighted loss aggregation, one
server backward pass, and returned cut-layer gradients. No alternative wire
protocol or numerical performance is invented here. The tiny counting inputs
are illustrative samples, not measured predictions or batch-size examples.
Post-training model construction (§3.3) is outside this training-step story.
"""
from html import escape


def icon(name):
    paths = {
        'client': '<rect x="3" y="3" width="18" height="14" rx="2"/><path d="M1 21h22M9 17v4m6-4v4"/>',
        'server': '<rect x="4" y="3" width="16" height="7" rx="2"/><rect x="4" y="14" width="16" height="7" rx="2"/><path d="M8 6.5h.01M8 17.5h.01M12 6.5h4M12 17.5h4M12 10v4"/>',
        'arrow': '<path d="M3 12h18m-6-6 6 6-6 6"/>',
        'image': '<rect x="3" y="3" width="18" height="18" rx="3"/><circle cx="8" cy="8" r="1.5"/><path d="m4 18 5-6 4 4 3-4 4 6"/>',
        'text': '<path d="M4 5h16M12 5v15M8 20h8"/>',
        'loop': '<path d="M20 8a8 8 0 0 0-14-3L3 8m0-5v5h5M4 16a8 8 0 0 0 14 3l3-3m0 5v-5h-5"/>',
        'layers': '<path d="m12 3 10 5-10 5L2 8Zm-9 9 9 5 9-5M3 16l9 5 9-5"/>',
    }
    return f'<svg class="ms-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{paths[name]}</svg>'


def reveal(body, at=0, cls=''):
    return f'<div class="{cls}" data-reveal="{at}">{body}</div>'


def tag(client):
    return f'<span class="ms-client-tag">{client}</span>'


def tokens(kind, encoded=False, gradient=False):
    state = ' ms-encoded' if encoded else ' ms-gradient' if gradient else ''
    return f'<span class="ms-tokens ms-{kind}{state}" aria-hidden="true">' + ''.join(
        f'<i style="--ms-token:{i}"></i>' for i in range(3)) + '</span>'


def bundle(client, heading=True):
    return f'<div class="ms-bundle" data-client="{client}" data-batch="batch-{client}">' + (
        f'<strong>{tag(client)}Tokens</strong>' if heading else '') + \
        f'<div class="ms-modality">{icon("image")}{tokens("image")}</div>' + \
        f'<div class="ms-modality">{icon("text")}{tokens("text")}</div></div>'


def transfer(client, payload, source, destination, body, cls=''):
    return f'<div class="ms-transfer {cls}" data-ms-transfer="{payload}" data-from="{source}" data-to="{destination}" data-client="{client}" data-batch="batch-{client}">{body}</div>'


def network(index):
    labels = ['Local tokens', 'Activations', 'Predictions', 'Local losses', 'Cut gradients', 'Next batch']
    direction = ['local', 'out', 'back', 'out', 'back', 'local'][index]
    client_active = index in (0, 1, 3, 5)
    server_active = index in (2, 4)
    clients = ''.join(
        f'<div class="ms-endpoint ms-client{" ms-active" if client_active else ""}" data-ms-client="{client}">'
        f'{tag(client)}<div><strong>Client {client}</strong><small><span data-local-only="inputs">Inputs</span> · '
        f'<span data-local-only="labels">y<sub>{client}</sub> = {count}</span></small></div></div>'
        for client, count in [('A', 2), ('B', 3)])
    return f'''<div class="ms-network ms-direction-{direction}" data-ms-network="true" data-active-role="{'clients' if client_active else 'server'}">
      <div class="ms-clients">{clients}</div>
      <div class="ms-connection"><strong>{labels[index]}</strong><div class="ms-wire"><i></i>{icon('arrow')}</div><small>{'On device' if direction == 'local' else 'In parallel' if index == 1 else 'For each client'}</small></div>
      <div class="ms-endpoint ms-server{' ms-active' if server_active else ''}" data-ms-server="shared">{icon('server')}<div><strong>Shared server</strong><small>Encoder + head</small></div></div>
    </div>'''


def tokenize():
    cards = []
    for client, count in [('A', 2), ('B', 3)]:
        dots = ''.join('<i></i>' for _ in range(count))
        raw = f'<div class="ms-inputs"><div class="ms-sample-image" aria-label="Illustrative image with {count} objects">{dots}</div><div class="ms-sample-text">How many?</div></div>'
        models = '<div class="ms-local-models"><span class="ms-image">Image<br/>tokenizer</span><span class="ms-text">Text<br/>tokenizer</span></div>'
        cards.append(f'<div class="ms-card ms-tokenize-card"><header>{tag(client)}<strong>Client {client}</strong><span>Image + text</span></header><div class="ms-tokenize-flow">'
                     + reveal(raw, 0) + reveal(models, 1000, 'ms-tokenize-models')
                     + reveal(bundle(client, False), 2300) + '</div></div>')
    return '<div class="ms-client-grid">' + ''.join(cards) + '</div>' + \
        reveal('<div class="ms-footnote"><span class="ms-legend ms-image">■ Image tokens</span><span class="ms-legend ms-text">▰ Text tokens</span></div>', 3400)


def upload():
    senders, receivers = [], []
    for i, client in enumerate(('A', 'B')):
        senders.append(reveal(transfer(client, 'activations', 'client', 'server',
                                      f'<div class="ms-packet">{bundle(client)}</div>', 'ms-upload'), 600, 'ms-send-row'))
        receivers.append(reveal(f'<div class="ms-inbox-row">{tag(client)}<div>{tokens("image")}{tokens("text")}</div></div>', 2200 + i * 500))
    return '<div class="ms-upload-layout"><div class="ms-senders">' + ''.join(senders) + '</div>' + \
        reveal('<div class="ms-parallel-arrows">'+icon('arrow')+icon('arrow')+'</div>', 1300, 'ms-route-arrow') + \
        '<div class="ms-inbox"><header>'+icon('server')+'<strong>Server input</strong></header>' + ''.join(receivers) + '</div></div>' + \
        reveal('<div class="ms-footnote"><strong>Two clients</strong><span>Parallel token streams</span></div>', 3500)


def predict():
    incoming = ''.join(f'<div class="ms-encode-input">{bundle(client)}</div>' for client in ('A', 'B'))
    encoder = '<div class="ms-encoder" data-ms-operation="shared-encoder" data-modalities="image text">' + \
        '<span class="ms-eyebrow">One model</span>'+icon('layers')+'<strong>Shared encoder</strong>' + \
        '<div class="ms-encoder-modalities"><span class="ms-image">'+icon('image')+'Image</span><span class="ms-text">'+icon('text')+'Text</span></div><small>Same weights</small></div>'
    outputs = []
    for client in ('A', 'B'):
        fused = f'<div class="ms-fusion" data-ms-operation="late-fusion" data-client="{client}" data-input="encoded-modalities" data-modalities="image text"><div class="ms-joined">{tokens("image", encoded=True)}{tokens("text", encoded=True)}</div><small>Join → pool → head</small></div>'
        prediction = transfer(client, 'predictions', 'server', 'client', f'<span class="ms-prediction">ŷ<sub>{client}</sub></span><span class="ms-return-arrow">{icon("arrow")}</span>{tag(client)}', 'ms-prediction-return')
        outputs.append('<div class="ms-encode-output">' + reveal(fused, 3100) + reveal(prediction, 4300) + '</div>')
    return '<div class="ms-encode-layout">' + reveal(incoming, 0, 'ms-encode-inputs') + \
        reveal(icon('arrow'), 700, 'ms-route-arrow') + reveal(encoder, 1200) + \
        reveal(icon('arrow'), 2500, 'ms-route-arrow') + reveal(''.join(outputs), 2800, 'ms-encode-outputs') + '</div>' + \
        reveal('<div class="ms-footnote"><strong>Late fusion</strong><span>Within each client’s sample</span></div>', 4700)


def local_losses():
    cards = []
    for client, count in [('A', 2), ('B', 3)]:
        comparison = f'<div class="ms-loss-inputs"><div class="ms-symbol"><b>ŷ<sub>{client}</sub></b><small>Prediction</small></div><span class="ms-plus">+</span><div class="ms-symbol ms-label" data-local-only="labels"><b>y<sub>{client}</sub> = {count}</b><small>Local label</small></div></div>'
        loss = f'<div class="ms-loss-result"><span>Loss</span><b>L<sub>{client}</sub></b></div>'
        send = transfer(client, 'local-loss', 'client', 'server', f'<strong>L<sub>{client}</sub></strong>{icon("arrow")}<span>Server</span>', 'ms-loss-send')
        cards.append(f'<div class="ms-card ms-loss-card"><header>{tag(client)}<strong>Client {client}</strong></header>' + \
                     reveal(comparison, 0) + reveal(loss, 1300) + reveal(send, 2800) + '</div>')
    return '<div class="ms-client-grid">' + ''.join(cards) + '</div>' + \
        reveal('<div class="ms-footnote"><span class="ms-label-key">Labels · local</span><span>Losses → server</span></div>', 4000)


def backward():
    terms = ''.join((('<span class="ms-plus">+</span>' if i else '') +
                     f'<span class="ms-loss-term" data-ms-loss="{client}"><span class="ms-fraction"><span>|B<sub>{client}</sub>|</span><span>|B|</span></span><b>L<sub>{client}</sub></b></span>')
                    for i, client in enumerate(('A', 'B')))
    objective = f'<div class="ms-objective" data-ms-operation="weighted-loss" data-weight="client-batch-size/global-batch-size" aria-label="The global loss is each client loss weighted by its batch size divided by the total batch size."><span class="ms-eyebrow">Batch-size weights</span><div class="ms-equation">{terms}<span class="ms-equals">=</span><b class="ms-global-loss">L<sub>S</sub></b></div><small>|B| = |B<sub>A</sub>| + |B<sub>B</sub>|</small></div>'
    model = '<div class="ms-backward" data-ms-operation="shared-backward">'+icon('layers')+'<div><strong>One backward pass</strong><small>Shared encoder + head</small></div><span class="ms-update-mark">'+icon('loop')+'</span></div>'
    returns = ''.join(reveal(transfer(client, 'cut-gradients', 'server', 'client',
                                    f'{tag(client)}<span class="ms-left-arrow">{icon("arrow")}</span><div class="ms-gradient-pair">{tokens("image", gradient=True)}{tokens("text", gradient=True)}</div><strong>∂L<sub>S</sub>/∂a<sub>{client}</sub></strong>', 'ms-gradient-return'), 3600 + i * 500)
                      for i, client in enumerate(('A', 'B')))
    return reveal(objective, 0) + reveal(model, 1500) + '<div class="ms-gradient-grid">' + returns + '</div>' + \
        reveal('<div class="ms-footnote"><strong>Cut-layer gradients</strong><span>Back to each tokenizer</span></div>', 5100)


def update():
    cards = []
    for client in ('A', 'B'):
        gradients = f'<div class="ms-update-gradients"><span>Cut gradients</span><div>{tokens("image", gradient=True)}{tokens("text", gradient=True)}</div></div>'
        models = '<div class="ms-updated-models"><span class="ms-image">'+icon('image')+'Image tokenizer'+icon('loop')+'</span><span class="ms-text">'+icon('text')+'Text tokenizer'+icon('loop')+'</span></div>'
        cards.append(f'<div class="ms-card ms-update-card" data-ms-operation="tokenizer-update" data-client="{client}" data-signal="cut-gradients"><header>{tag(client)}<strong>Client {client}</strong></header>' + \
                     reveal(gradients, 0) + reveal('<span class="ms-local-backward">Local backward ↓</span>', 1000) + reveal(models, 2000) + '</div>')
    return '<div class="ms-client-grid">' + ''.join(cards) + '</div>' + \
        reveal('<div class="ms-next-batch" data-ms-operation="next-batch">'+icon('loop')+'<strong>Next mini-batch</strong><span>New inputs → new tokens</span></div>', 3600)


def make_step(index, short_title, title, caption, body, duration, description):
    scopes = ['ON EACH CLIENT', 'CLIENTS → SERVER', 'ON THE SERVER → CLIENTS', 'ON EACH CLIENT → SERVER', 'ON THE SERVER → CLIENTS', 'ON EACH CLIENT']
    art = f'''<div class="story-art ms-art" role="group" aria-label="{escape(description, quote=True)}">
      {network(index)}<div class="ms-scene-body"><div class="ms-stage-heading"><span class="ms-eyebrow">{scopes[index]}</span><h3>{title}</h3></div>{body}</div></div>'''
    return {'short_title': short_title, 'title': title, 'caption': caption,
            'art': art, 'duration_ms': duration, 'title_in_art': True}


STEPS = [
    make_step(0, 'Tokenize', 'Small tokenizers, local inputs',
              'Image + text · Local tokenizers · Token activations', tokenize(), 8000,
              'Two clients keep their raw image, text, and labels locally. Illustrative samples show two objects for client A and three for B, paired with the question How many? Image and text tokenizers produce separate activation sequences.'),
    make_step(1, 'Send tokens', 'Parallel streams → one server',
              'Token activations → server · Raw inputs stay local', upload(), 7500,
              'Client A and client B send their image and text activations in parallel to one shared server. Each client batch stays identifiable; raw inputs and labels remain on its client.'),
    make_step(2, 'Predict', 'Encode → fuse → predict',
              'Shared weights · Late fusion · Predictions → clients', predict(), 10000,
              'One shared server encoder processes image and text independently with the same weights. Encoded modalities are joined within each sample, pooled, and passed through the task head. Separate predictions return to client A and client B.'),
    make_step(3, 'Local loss', 'Predictions meet local labels',
              'Prediction + local label → loss · Losses → server', local_losses(), 8500,
              'Each client compares its returned predictions with its own local labels and computes its loss. Client A sends loss L A and client B sends loss L B to the server; labels remain local, following the paper’s conceptual training flow.'),
    make_step(4, 'Backward', 'One objective → one backward pass',
              'Batch-weighted losses · Shared backward · Cut gradients → clients', backward(), 10000,
              'The server weights each client loss by its mini-batch size divided by the total batch size. One backward pass updates the shared server model and computes separate cut-layer gradients for each client’s activations. Those gradients return to their originating clients.'),
    make_step(5, 'Update', 'Update locally → repeat',
              'Local tokenizer updates · Next mini-batch', update(), 8000,
              'Each client backpropagates its returned cut-layer gradients through its own image and text tokenizers and updates them locally. The next mini-batch starts a new step. This training cycle does not average client model weights; post-training model construction is outside this walkthrough.'),
]
