"""One connected DeltaMask round: IEEE BigData manuscript, §III and Algorithms1–2.

The eight-position example is internally consistent and contains no measured
results. Filter reconstruction first shows the normal hit/miss case; the caption
separately explains approximation. PNG compression preserves the filter bytes.
"""
from html import escape

REFERENCE = [1, 1, 0, 1, 0, 1, 0, 1]
LOCAL = [1, 0, 0, 0, 1, 1, 1, 1]
GLOBAL_P = [.8, .7, .2, .6, .3, .8, .2, .8]
LOCAL_P = [.85, .15, .2, .45, .9, .8, .6, .85]
RANKED = [5, 2, 7, 4]
SELECTED = RANKED[:3]
QUERIES = [int(i + 1 in SELECTED) for i in range(8)]
RECONSTRUCTED = [a ^ b for a, b in zip(REFERENCE, QUERIES)]
CLIENT_B = [1, 1, 0, 1, 0, 1, 1, 1]
CLIENT_C = [1, 0, 0, 1, 1, 1, 0, 1]
# A Beta(1,1) prior plus three binary observations, per position.
NEXT_P = [(1 + a + b + c) / 5 for a, b, c in zip(RECONSTRUCTED, CLIENT_B, CLIENT_C)]


def icon(name):
    paths = {
        'server': '<rect x="4" y="3" width="16" height="7" rx="2"/><rect x="4" y="14" width="16" height="7" rx="2"/><path d="M8 6.5h.01M8 17.5h.01M12 6.5h4M12 17.5h4M12 10v4"/>',
        'client': '<rect x="3" y="4" width="18" height="13" rx="2"/><path d="M1 21h22M9 17v4m6-4v4"/>',
        'lock': '<rect x="5" y="10" width="14" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3m-4 5v2"/>',
        'seed': '<path d="M20 4C9 3 3 7 5 14s15 5 15-10ZM5 20l10-11"/>',
        'data': '<ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v7c0 4 16 4 16 0V5M4 12v7c0 4 16 4 16 0v-7"/>',
        'arrow': '<path d="M4 12h16m-6-6 6 6-6 6"/>',
        'packet': '<path d="M14 2H5v20h14V7Zm0 0v5h5M8 11h8M8 15h8M8 18h4"/>',
        'filter': '<path d="M3 4h18l-7 8v7l-4 2v-9Z"/>',
        'check': '<path d="m5 12 4 4L19 6"/>',
    }
    return f'<svg class="dm-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.65" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{paths[name]}</svg>'


def reveal(body, at=0, cls=''):
    return f'<div class="{cls}" data-reveal="{at}">{body}</div>'


def network(index):
    action = ['Probabilities + seed', 'Local training', 'Local selection',
              'PNG upload', 'Reconstruction', 'Next probabilities'][index]
    direction = 'up' if index == 3 else 'down' if index in (0, 5) else 'still'
    server = ' dm-active' if index in (0, 4, 5) else ''
    client = ' dm-active' if index in (1, 2, 3) else ''
    token = icon('packet') if index == 3 else ''
    token_class = ' class="dm-wire-packet"' if index == 3 else ''
    return f'''<div class="dm-network dm-direction-{direction}" data-dm-network="true">
      <div class="dm-endpoint dm-server{server}">{icon('server')}<div><strong>Server</strong><span>Global mask</span></div></div>
      <div class="dm-connection"><span>{action}</span><div class="dm-wire"><i{token_class}>{token}</i>{icon('arrow')}</div></div>
      <div class="dm-clients"><div class="dm-endpoint dm-client{client}">{icon('client')}<div><strong>Client A</strong><span>Local mask</span></div></div><div class="dm-peers"><span>{icon('client')}Client B</span><span>{icon('client')}Client C</span></div></div>
    </div>'''


def positions():
    return '<div class="dm-mask-row dm-positions"><span>Position</span><div class="dm-bits">' + ''.join(f'<span>{i:02d}</span>' for i in range(1, 9)) + '</div></div>'


def bits(label, values, key, highlights=(), omitted=(), at=None, scan=False):
    cells = []
    for i, value in enumerate(values):
        tone = ' dm-changed' if i + 1 in highlights else ''
        tone += ' dm-omitted' if i + 1 in omitted else ''
        cell = f'<span class="dm-bit dm-bit-{value}{tone}" data-position="{i+1}">{value}</span>'
        if scan:
            cell = reveal(cell, 1200 + i * 650 + (200 if key == 'reconstructed' else 0), 'dm-bit-slot')
        cells.append(cell)
    row = f'<div class="dm-mask-row" data-mask="{key}" data-values="{",".join(map(str,values))}"><strong>{label}</strong><div class="dm-bits">{"".join(cells)}</div></div>'
    return reveal(row, at) if at is not None else row


def probabilities(label, values, at=0, key=''):
    cells = ''.join(f'<span class="dm-prob" style="--prob:{v*100:g}%"><i></i><b>{round(v*100)}<small>%</small></b></span>' for v in values)
    return reveal(f'<div class="dm-mask-row dm-prob-row" data-probabilities="{key}"><strong>{label}</strong><div class="dm-bits">{cells}</div></div>', at)


def chip(position, omitted=False):
    return f'<span class="dm-position-chip{" dm-omitted" if omitted else ""}"><small>Position</small><b>{position:02d}</b>{icon("check") if not omitted else "<span>Omit</span>"}</span>'


def fingerprints():
    return '<div class="dm-fingerprints" aria-hidden="true">' + ''.join(f'<i style="--shade:{v}"></i>' for v in [.25,.8,.5,.1,.7,.35,.9,.45,.15,.6,.3,.8,.65,.15,.45,.95]) + '</div>'


def packet():
    return f'<div class="dm-packet">{icon("packet")}<span>PNG</span></div>'


def start():
    return reveal('<div class="dm-badges"><span>'+icon('lock')+'Frozen backbone</span><span>'+icon('seed')+'Shared seed</span></div>') + \
        '<div class="dm-matrix">' + positions() + probabilities('Global probabilities', GLOBAL_P, 650, 'global') + \
        reveal('<div class="dm-between">Shared-seed sampling ↓</div>', 1500) + \
        bits('Shared reference', REFERENCE, 'reference', at=2300) + '</div>' + \
        reveal('<p class="dm-insight"><strong>Server = Clients</strong> · Same reference</p>', 3300)


def learn():
    return reveal(f'<div class="dm-training-flow"><span>{icon("data")}Local data</span>{icon("arrow")}<strong>Mask-score learning</strong><span class="dm-frozen">{icon("lock")}Frozen backbone</span></div>') + \
        '<div class="dm-matrix">' + positions() + probabilities('Before training', GLOBAL_P, 550, 'global') + \
        probabilities('After training', LOCAL_P, 1500, 'local') + bits('Local mask sample', LOCAL, 'local', highlights=[2,4,5,7], at=2700) + '</div>' + \
        reveal('<p class="dm-insight"><strong>1</strong> · Weight on <span class="dm-legend-gap"></span><strong>0</strong> · Weight off</p>', 3700)


def select():
    return '<div class="dm-matrix">' + positions() + bits('Shared reference', REFERENCE, 'reference') + \
        bits('Local mask', LOCAL, 'local', highlights=[2,4,5,7], at=700) + '</div>' + \
        reveal('<div class="dm-ranking"><div><span class="dm-mini-label">Changed positions · KL ranking</span><div class="dm-chips">' + ''.join(chip(i, i == 4) for i in RANKED) + '</div></div><p><strong>Top 3 of 4</strong><span>κ = 75%</span></p></div>', 1800) + \
        reveal('<p class="dm-insight"><strong>Keep</strong> · 05, 02, 07 <span class="dm-legend-gap"></span><strong>Omit</strong> · 04</p>', 3500)


def upload():
    return '<div class="dm-codec">' + \
        reveal('<div class="dm-codec-card"><span class="dm-mini-label">Selected changes</span><div class="dm-chips">' + ''.join(chip(i) for i in SELECTED) + '</div><strong>Position indices</strong></div>', 0) + \
        reveal(icon('arrow'), 700, 'dm-codec-arrow') + \
        reveal('<div class="dm-codec-card"><span class="dm-mini-label">Build BFuse8</span>'+fingerprints()+'<strong>8-bit fingerprints</strong></div>', 1100) + \
        reveal(icon('arrow'), 1800, 'dm-codec-arrow') + \
        reveal('<div class="dm-codec-card dm-payload-card"><span class="dm-mini-label">Lossless compression</span>'+packet()+'<strong>Compact upload</strong></div>', 2300) + '</div>' + \
        reveal('<p class="dm-insight"><strong>Upload</strong> · Encoded positions <span class="dm-legend-gap"></span><strong>Weights</strong> · Stay local</p>', 3400)


def reconstruct():
    return reveal('<div class="dm-decode">'+packet()+icon('arrow')+'<span><strong>Decompress PNG</strong><small>Lossless decoding</small></span>'+icon('arrow')+icon('filter')+'<strong>Query BFuse8</strong></div>') + \
        reveal('<div class="dm-rule"><span><b>Hit · 1</b> → flip</span><span><b>Miss · 0</b> → keep</span></div>', 650) + \
        '<div class="dm-matrix dm-reconstruction">' + positions() + bits('Shared reference', REFERENCE, 'reference') + \
        bits('Filter says flip?', QUERIES, 'queries', highlights=SELECTED, scan=True) + \
        bits('Reconstructed A', RECONSTRUCTED, 'reconstructed', highlights=SELECTED, omitted=[4], scan=True) + '</div>' + \
        reveal('<div class="dm-flip-examples"><span><b>02</b> 1 → 0</span><span><b>05</b> 0 → 1</span><span><b>07</b> 0 → 1</span><span class="dm-omission"><b>04</b> 1 → 1 · omitted</span></div>', 6500)


def aggregate():
    return '<div class="dm-matrix dm-aggregation">' + positions() + \
        bits('Client A recovered', RECONSTRUCTED, 'reconstructed', highlights=SELECTED) + \
        bits('Client B recovered', CLIENT_B, 'client-b', at=700) + \
        bits('Client C recovered', CLIENT_C, 'client-c', at=1400) + \
        reveal('<div class="dm-between">Bayesian aggregation ↓</div>', 2300) + \
        probabilities('Next probabilities', NEXT_P, 3300, 'next') + '</div>' + \
        reveal('<p class="dm-insight"><strong>Next round</strong> · New probabilities → new reference</p>', 4400)


def make_step(index, short_title, title, caption, body, duration):
    scopes = ['SERVER → CLIENTS', 'ON EACH CLIENT', 'ON EACH CLIENT', 'CLIENTS → SERVER', 'ON THE SERVER', 'SERVER → NEXT ROUND']
    art = f'''<div class="story-art dm-art" role="group" aria-label="{escape(title, quote=True)}">
      {network(index)}<div class="dm-scene-body"><div class="dm-stage-heading"><span class="dm-mini-label">{scopes[index]}</span><h3>{title}</h3></div>{body}</div></div>'''
    return {'short_title':short_title, 'title':title, 'caption':caption,
            'art':art, 'duration_ms':duration, 'title_in_art':True}


STEPS = [
    make_step(0, 'Start round', 'One shared starting point',
              'Global probabilities · Shared seed · Shared reference', start(), 7000),
    make_step(1, 'Learn locally', 'Local mask learning',
              'Local data · Learned probabilities · Frozen weights', learn(), 8000),
    make_step(2, 'Select changes', 'Rank → select',
              'Mask difference → KL ranking → Top-κ selection', select(), 8500),
    make_step(3, 'Upload', 'A compact client upload',
              'Selected positions → BFuse8 → Lossless PNG', upload(), 7500),
    make_step(4, 'Reconstruct', 'Reconstruct the client mask',
              'Approximate recovery · Omitted changes · Rare false positives', reconstruct(), 11500),
    make_step(5, 'Aggregate', 'Aggregate → broadcast',
              'Client masks + Beta(1,1) prior → Next probabilities', aggregate(), 9000),
]
