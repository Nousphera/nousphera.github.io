"""Source-bound connected artwork; all numerical/token layouts are schematic.

EncCluster: arXiv:2406.09152v1 §3 and Algorithms 1–2. The server estimates
the BF-encoded map; it is not hidden from that server. BF is not encryption.
EFU: arXiv:2508.07873v1 §4 and Algorithms 1–2. Local branches are alternatives;
the mapping is visible, without BF. Function binding has the paper's security
assumptions and does not force deployment or destruction of old model copies.
FiBA: TU/e FinalPaper.pdf §3, Algorithm 1. Invisible backdoor benchmark, not a
frequency-domain attack. LSB attention placement is a separate controlled probe.
"""
from html import escape
from research_icons import research_icon

MAP = ('A', 'B', 'A', 'B', 'B', 'A')
RAW = (-.5, .5, -.4, .6, .7, -.3)
CENTROIDS = {'A': -.4, 'B': .6}
ACTIVATION_LEVELS = (.12, .18, .35, .22, .11, .19, .56, .89, .61, .16,
                     .22, .72, 1, .78, .21, .14, .38, .69, .46, .13)


def icon(name):
    return research_icon(name, 'pw-icon')


def arrow():
    return '<span class="pw-arrow" aria-hidden="true">→</span>'


def reveal(content, delay=0, cls=''):
    return f'<div class="{cls}" data-reveal="{delay}">{content}</div>'


def chip(text, name, cls=''):
    return f'<span class="pw-chip {cls}">{icon(name)}<b>{text}</b></span>'


def model(cls=''):
    return f'<div class="pw-model {cls}" aria-hidden="true">' + ''.join(
        f'<i style="--shade:{v}"></i>' for v in (.2, .6, .9, .4, .75, .3, .85, .5, .65)) + '</div>'


def token(cluster, encrypted=False, value=False):
    tone = ' pw-secondary' if cluster == 'B' else ''
    label = f'{CENTROIDS[cluster]:.1f}' if value else cluster
    return f'<span class="pw-token{tone}" data-centroid="{cluster}" data-encrypted="{str(encrypted).lower()}">{icon("lock") if encrypted else ""}<b>{label}</b></span>'


def centroid_pair(encrypted=False, values=False):
    return '<div class="pw-centroids">' + token('A', encrypted, values) + token('B', encrypted, values) + '</div>'


def mapping(key='original', location='client'):
    return f'<div class="pw-slots" data-position-map="{key}" data-location="{location}" data-values="{",".join(MAP)}">' + ''.join(
        f'<div class="pw-slot"><small>{i+1:02d}</small>{token(c)}</div>' for i, c in enumerate(MAP)) + '</div>'


def expanded():
    return '<div class="pw-slots pw-expanded" data-expanded-model="true" data-location="server">' + ''.join(
        f'<div class="pw-slot" data-centroid="{c}" data-encrypted="true"><small>{i+1:02d}</small>{token(c, True)}</div>' for i, c in enumerate(MAP)) + '</div>'


def fingerprints():
    return '<div class="pw-fingerprints" aria-hidden="true">' + ''.join(
        f'<i style="--shade:{v}"></i>' for v in (.3, .8, .5, .2, .9, .6, .4, .7, .2, .6, .9, .4)) + '</div>'


def card(title, content, cls='', attrs=''):
    return f'<section class="pw-card {cls}" {attrs}><h4>{title}</h4>{content}</section>'


def context(slug, role, direction='still'):
    if slug == 'fiba':
        return f'''<div class="pw-context pw-three-roles" data-pw-context="true">
          <span class="pw-role" data-active="{str(role == 'honest').lower()}">{icon('client')}<b>Honest</b></span>
          <span class="pw-role pw-warning" data-active="{str(role == 'attacker').lower()}">{icon('attack')}<b>Attacker</b></span>
          <span class="pw-role" data-active="{str(role == 'server').lower()}">{icon('server')}<b>Server</b></span></div>'''
    return f'''<div class="pw-context pw-direction-{direction}" data-pw-context="true">
      <span class="pw-role" data-active="{str(role == 'client').lower()}">{icon('client')}<b>Client A</b></span>
      <div class="pw-link"><span>Round r</span><i></i><b></b></div>
      <span class="pw-role" data-active="{str(role == 'server').lower()}">{icon('server')}<b>Server</b></span></div>'''


def scene(slug, index, title, body, desc, role, direction='still'):
    return f'<div class="story-art pw-art pw-{slug}" role="group" aria-label="{escape(desc, quote=True)}">' + context(slug, role, direction) + \
        f'<div class="pw-body"><div class="pw-heading"><span>{index+1:02d} / 06</span><h3>{escape(title)}</h3></div>{body}</div></div>'


def step(slug, i, short, title, caption, body, desc, role, duration=9000, direction='still'):
    return dict(short_title=short, title=title, caption=caption, art=scene(slug, i, title, body, desc, role, direction), title_in_art=True, duration_ms=duration)


def enc_train():
    raw = '<div class="pw-slots">' + ''.join(f'<div class="pw-slot"><small>{i+1:02d}</small><span class="pw-number{ " pw-secondary" if MAP[i] == "B" else ""}">{v:.1f}</span></div>' for i, v in enumerate(RAW)) + '</div>'
    return reveal('<div class="pw-strip">' + chip('Local data', 'database') + arrow() + chip('Train', 'train') + arrow() + chip('Weights', 'model') + '</div>') + \
        reveal(card('Trained weights', raw), 1100) + \
        reveal('<div class="pw-split-cards">' + card('Centroids', centroid_pair(values=True), 'pw-centered') + card('Position map', mapping()) + '</div>', 2600) + \
        reveal('<div class="pw-foot">' + icon('key') + '<span>Setup authority · Parameters + IDs</span></div>', 4300)


def enc_encode():
    return '<div class="pw-encode-lanes">' + \
        reveal('<div class="pw-encode-lane"><strong>Centroids</strong>' + centroid_pair(values=True) + arrow() + chip('DMCFE', 'encrypt') + arrow() + centroid_pair(True) + '</div>', 0) + \
        reveal('<div class="pw-encode-lane"><strong>Position pairs</strong><div class="pw-pairs"><b>(01, A)</b><b>(02, B)</b><b>…</b></div>' + arrow() + chip('Binary Fuse', 'fingerprint') + arrow() + fingerprints() + '</div>', 1700) + '</div>' + \
        reveal(card('Two components', '<div class="pw-strip">' + chip('Encrypted values', 'lock') + '<b>+</b>' + chip('Fingerprints', 'filter') + '</div>', 'pw-emphasis'), 3500)


def payload(mapping_type):
    bf = mapping_type == 'bf-fingerprints'
    pieces = [
        ('Encrypted centroids', 'encrypted-centroids', centroid_pair(True), 'lock'),
        ('BF fingerprints' if bf else 'Visible map', mapping_type, fingerprints() if bf else mapping('sent', 'server'), 'fingerprint' if bf else 'codebook'),
        ('Partial key', 'partial-key', '<div class="pw-key">' + icon('key') + '<b>r · f</b></div>', 'key'),
    ]
    return '<div class="pw-payload">' + ''.join(reveal(card(title, inner, 'pw-payload-card', f'data-upload="true" data-payload="{kind}"'), i * 1200) for i, (title, kind, inner, _) in enumerate(pieces)) + '</div>' + \
        reveal('<div class="pw-transfer">' + chip('Client A', 'client') + '<span class="pw-transfer-line"><i></i></span>' + chip('Server', 'server') + '</div>', 3900)


def enc_query():
    queries = ''
    for candidate in ('A', 'B'):
        hits = ''.join(f'<span class="pw-query-cell{ " pw-hit" if candidate == c else ""}" style="--query:{i}">{icon("check") if candidate == c else "·"}</span>' for i, c in enumerate(MAP))
        queries += f'<div class="pw-query-row{ " pw-secondary" if candidate == "B" else ""}"><strong>{candidate}</strong><div>{hits}</div></div>'
    return reveal('<div class="pw-strip" data-shared-seed="true">' + fingerprints() + '<b>+</b>' + chip('Shared seed', 'seed') + arrow() + chip('Query (position, cluster)', 'search') + '</div>') + \
        reveal(card('Membership queries', '<div class="pw-query-label"><span>Cluster</span><div>' + ''.join(f'<span>{i:02d}</span>' for i in range(1, 7)) + '</div></div>' + queries), 1400) + \
        reveal(card('Estimated map', mapping('recovered', 'server'), 'pw-emphasis'), 3400)


def expand_view():
    return reveal('<div class="pw-strip">' + chip('Ciphertext codebook', 'codebook') + centroid_pair(True) + '</div>') + \
        reveal(card('Position map', mapping('expansion', 'server')), 1100) + \
        reveal('<div class="pw-substitution" aria-hidden="true">' + ''.join(f'<i style="--query:{i}">↓</i>' for i in range(6)) + '</div>', 2400) + \
        reveal(card('Encrypted model', expanded(), 'pw-emphasis'), 3000)


def secure_aggregate(final=True):
    inputs = ''.join(f'<div class="pw-encrypted-client{ " pw-secondary" if i == 1 else ""}"><span>Client {name}</span>{icon("lock")}{icon("model")}<b>+</b>{icon("key")}</div>' for i, name in enumerate(('A', 'B', 'C')))
    result = '<div class="pw-secure-flow">' + reveal(card('Encrypted inputs + key shares', inputs), 0) + reveal(arrow(), 1000, 'pw-flow-arrow') + \
        reveal(card('Authorized aggregate', icon('aggregate') + '<strong>Σ αᵢ θᵢ</strong><span>Weighted decryption</span>', 'pw-aggregate-card', 'data-decrypt="weighted-aggregate"'), 2100) + '</div>'
    if final:
        result += reveal('<div class="pw-broadcast" data-broadcast="global-model">' + model() + '<strong>Global model</strong><b>θ<sub>r+1</sub></b>' + arrow() + chip('Clients', 'clients') + '</div>', 3800)
    return result


def efu_choose():
    branches = card('Learn', icon('train') + chip('Retain set', 'data') + '<strong>Cross-entropy</strong>', 'pw-option', 'data-local-mode="learn"') + \
        '<b class="pw-or">or</b>' + card('Unlearn', icon('unlearn') + chip('Forget set', 'data', 'pw-warning') + '<strong>Forget objective</strong>', 'pw-option pw-emphasis', 'data-local-mode="unlearn"')
    return reveal('<div class="pw-strip">' + model() + '<strong>Round model</strong>' + arrow() + chip('Local choice', 'split') + '</div>') + \
        reveal('<div class="pw-alternatives" data-local-alternatives="true">' + branches + '</div>', 1400) + \
        reveal('<div class="pw-merge">' + icon('merge') + '<strong>One local update</strong>' + model('pw-model-change') + '</div>', 3500)


def sample_image(trigger=False, cls=''):
    # Repeated image identity; highlighted dots expose an otherwise subtle transform.
    points = ''.join(f'<i style="--x:{x}%;--y:{y}%"></i>' for x, y in ((15, 20), (34, 18), (74, 22), (21, 70), (78, 73), (58, 84))) if trigger else ''
    return f'<div class="pw-image {cls}">{icon("image")}<span class="pw-trigger-dots">{points}</span></div>'


def efu_objective():
    forget = card('Forget', sample_image() + '<strong>− CE</strong><span>True labels</span>', 'pw-objective-card pw-warning', 'data-loss-term="negative-cross-entropy"')
    auxiliary = card('Auxiliary', sample_image(True) + '<strong>+ CE</strong><span>Incorrect labels</span><small>PGD · Once offline</small>', 'pw-objective-card', 'data-loss-term="adversarial-cross-entropy" data-preparation="offline-once" data-target="incorrect-label"')
    drift = card('Limit drift', '<div class="pw-importance"><i></i><i></i><i></i><i></i><i></i></div><strong>+ Inverted MAS</strong><span>Parameter importance</span>', 'pw-objective-card pw-secondary', 'data-loss-term="inverted-mas"')
    return '<div class="pw-objectives">' + reveal(forget, 0) + reveal(auxiliary, 1500) + reveal(drift, 3000) + '</div>' + \
        reveal('<div class="pw-merge">' + icon('merge') + '<strong>Joint unlearning update</strong>' + model('pw-model-change') + '</div>', 4500)


def efu_binding():
    authorized = '<div class="pw-request" data-request="authorized" data-decryptable="true">' + chip('All agreed inputs', 'clients') + arrow() + chip('Valid key', 'check') + '</div>'
    altered = '<div class="pw-request pw-warning" data-request="omit-client" data-decryptable="false">' + chip('Omit a client', 'split') + arrow() + chip('No valid key', 'warning') + '</div>'
    return reveal('<div class="pw-key-binding" data-key-binding="function,round"><div class="pw-bound-key">' + icon('key') + '<strong>Aggregation f</strong><b>Round r</b></div>' + authorized + altered + '</div>', 0) + \
        reveal('<div class="pw-aggregate-result" data-decrypt="weighted-aggregate">' + icon('aggregate') + '<strong>Agreed weighted aggregate</strong>' + model() + '</div>', 3400)


def efu_return():
    return reveal('<div class="pw-result-orbit">' + icon('server') + '<div class="pw-result-model">' + model() + '<strong>θ<sub>r+1</sub></strong><span>Global model</span></div></div>') + \
        reveal('<div class="pw-broadcast" data-broadcast="global-model">' + chip('Broadcast', 'download') + arrow() + chip('Clients', 'clients') + '</div>', 1600) + \
        reveal('<div class="pw-next-round">' + chip('Retained data', 'database') + arrow() + chip('Next round', 'exchange') + '</div>', 3300)


def fiba_start():
    honest = card('Honest client', sample_image() + chip('Local data', 'database') + '<strong>Ordinary learning</strong>', 'pw-party')
    attacker = card('Attacker client', sample_image() + chip('Local access', 'attack', 'pw-warning') + '<strong>Poisoned learning</strong>', 'pw-party pw-warning')
    return reveal('<div class="pw-strip">' + icon('server') + model() + '<strong>Shared global model</strong>' + icon('download') + '</div>') + \
        reveal('<div class="pw-parties">' + honest + attacker + '</div>', 1600) + \
        reveal('<div class="pw-foot">' + icon('exchange') + '<span>Local training → Server aggregation → Repeat</span></div>', 3500)


def fiba_poison():
    original = card('Original', sample_image() + '<span class="pw-target-label">Label y</span>', 'pw-image-card')
    altered = card('Poisoned', sample_image(True) + '<span class="pw-target-label pw-warning">Target t</span>', 'pw-image-card pw-warning', 'data-poisoned-input="true" data-location="attacker-client" data-target="t" data-transform="LSB"')
    return reveal('<div class="pw-attack-family"><strong>Attack family</strong><span class="pw-selected">LSB</span><span>WaNet</span><span>Encoder</span><span>LIRA</span></div>') + \
        '<div class="pw-transform">' + reveal(original, 700) + reveal('<div class="pw-transform-operation">' + icon('trigger') + '<strong>LSB bits</strong>' + arrow() + '</div>', 1600) + reveal(altered, 2600) + '</div>' + \
        reveal('<div class="pw-strip pw-warning">' + icon('target') + '<strong>All-to-one</strong><span>Shared target t</span></div>', 3900)


def fiba_train():
    clean = card('Honest client', sample_image() + '<span>Clean data · y</span>' + arrow() + model(), 'pw-training-lane', 'data-training-role="honest"')
    poison = card('Attacker client', '<div class="pw-training-inputs">' + sample_image() + '<b>+</b>' + sample_image(True) + '</div><span>Clean y + Poisoned t</span>' + arrow() + model('pw-warning'), 'pw-training-lane pw-warning', 'data-training-role="attacker"')
    return '<div class="pw-training-lanes">' + reveal(clean, 0) + reveal(poison, 1700) + '</div>' + \
        reveal('<div class="pw-merge">' + icon('upload') + '<strong>Local model updates</strong><span>Data stay on clients</span></div>', 3600)


def fiba_aggregate():
    updates = '<div class="pw-update-pair"><span>' + icon('client') + model() + '<b>Honest</b></span><span class="pw-warning">' + icon('attack') + model() + '<b>Attacker</b></span></div>'
    defenses = ''.join(f'<span data-rule="{name}">{name}</span>' for name in ('Median', 'Trimmed Mean', 'FoolsGold', 'KRUM', 'Multi-KRUM'))
    rules = '<div class="pw-rules" data-aggregation-alternatives="true" data-selection="one-per-run"><div class="pw-fedavg" data-rule="FedAvg">' + icon('aggregate') + '<b>FedAvg</b><span>Baseline</span></div><strong>or</strong><div class="pw-defenses">' + icon('shield') + '<b>One defense</b><div>' + defenses + '</div></div></div>'
    return reveal(updates, 0) + reveal('<div class="pw-down-arrow">↓</div>', 900) + reveal(rules, 1700) + \
        reveal('<div class="pw-broadcast">' + model() + '<strong>Global model</strong>' + arrow() + chip('Next round', 'clients') + '</div>', 4000)


def fiba_evaluate():
    clean = card('Clean test', sample_image() + '<strong>Correct label y?</strong><span>Clean accuracy</span>', 'pw-evaluation-card', 'data-metric="clean-accuracy"')
    triggered = card('Triggered test', sample_image(True) + '<strong>Target t?</strong><span>Attack success</span>', 'pw-evaluation-card pw-warning', 'data-metric="attack-success"')
    return '<div class="pw-parties">' + reveal(clean, 0) + reveal(triggered, 1400) + '</div>' + \
        reveal('<div class="pw-metrics"><span data-metric="LPIPS">' + icon('image') + '<b>LPIPS</b><small>Visual distance</small></span><span data-metric="Neural-Cleanse">' + icon('search') + '<b>Neural Cleanse</b><small>Model anomaly</small></span></div>', 3300)


def activation(kind='map'):
    # Rank half the illustrative cells, preserving the reported low/high labels.
    # This does not resolve the source's inconsistent mask-order description.
    low = set(sorted(range(len(ACTIVATION_LEVELS)), key=lambda i: (ACTIVATION_LEVELS[i], i))[:len(ACTIVATION_LEVELS) // 2])
    cells = ''
    for i, level in enumerate(ACTIVATION_LEVELS):
        selected = (kind == 'low' and i in low) or (kind == 'high' and i not in low) or kind == 'all'
        cells += f'<i style="--shade:{level}" class="{ "pw-region-selected" if selected else ""}" data-cell="{i}" data-level="{level}" data-selected="{str(selected).lower()}"></i>'
    return f'<div class="pw-activation pw-activation-{kind}" data-activation-map="{kind}" aria-hidden="true">{cells}</div>'


def fiba_attention():
    masks = ''.join(card(label, activation(kind), 'pw-placement', f'data-placement="{kind}"') for label, kind in [('Low', 'low'), ('High', 'high'), ('Unmasked', 'all')])
    return reveal('<div class="pw-strip">' + chip('Converged model', 'model') + arrow() + chip('Activation map', 'search') + activation() + '</div>') + \
        reveal('<div class="pw-placement-probe" data-placement-probe="true" data-attack-family="LSB" data-trigger-sizes="500,700" data-after-convergence="true"><div class="pw-probe-label"><strong>LSB500 · LSB700</strong><span>Separate placement comparison</span></div><div class="pw-placement-options">' + masks + '</div></div>', 1800) + \
        reveal('<div class="pw-strip pw-probe-metrics">' + chip('Success', 'target') + chip('Visual distance', 'image') + chip('Anomaly', 'search') + '</div>', 4000)


WALKTHROUGHS = {
    'enccluster': [
        step('enccluster', 0, 'Cluster', 'Many weights → few centroids', 'Train · Cluster · Preserve positions', enc_train(), 'Client A trains locally, then clusters six illustrative weights into centroids A=-0.4 and B=0.6 with map A B A B B A. Clustering approximates the trained weights. The repeated colors and positions track the same client contribution. An honest-but-curious setup authority supplies public parameters and identifiers; authority participation is not eliminated.', 'client'),
        step('enccluster', 1, 'Encode', 'Values encrypt · positions hash', 'DMCFE ciphertexts + Binary Fuse fingerprints', enc_encode(), 'Client A encrypts the centroid values using DMCFE and separately encodes position-cluster pairs in a Binary Fuse filter. The filter is a probabilistic membership structure, not cryptographic encryption. The A and B labels identify ciphertext slots, not exposed plaintext values. Centroid scaling for data-weighted aggregation is omitted from the schematic token values.', 'client'),
        step('enccluster', 2, 'Upload', 'Three pieces cross the boundary', 'Encrypted centroids · Fingerprints · Partial key', payload('bf-fingerprints'), 'The client uploads encrypted centroid values, BF fingerprints and a partial functional key. The server has the shared hashing seed. Raw training data and individual plaintext model weights are not uploaded. Each component has a different role; fingerprints and keys are not an additional encrypted model.', 'client', direction='up'),
        step('enccluster', 3, 'Query map', 'Recover which centroid goes where', 'Shared seed · Membership queries · Estimated positions', enc_query(), 'At the server, the BF fingerprints and shared seed support membership queries for each position and candidate cluster. The nominal no-error example recovers A B A B B A. The mapping is intentionally recoverable by the server. False positives can cause mapping errors; the diagram does not claim exact recovery or a privacy guarantee from BF hashing.', 'server', 10500),
        step('enccluster', 4, 'Reconstruct', 'Expand without opening the values', 'Position by position · Centroid ciphertext substitution', expand_view(), 'The server uses the estimated map to copy ciphertext A or ciphertext B into each model position. The six positions recover the clustered model structure while every individual value remains encrypted. This is ciphertext substitution, not plaintext client-model decryption.', 'server', 10000),
        step('enccluster', 5, 'Aggregate', 'Open the aggregate · start again', 'Partial keys → Weighted aggregate → Global broadcast', secure_aggregate(), 'The server combines participating clients partial functional keys and encrypted expanded models to recover the authorized data-weighted aggregate, then broadcasts the next global model. The output is the aggregate, not each individual client model. Security depends on the DMCFE threat model, setup, provisioning and collusion assumptions; no differential privacy claim is made.', 'server', direction='down'),
    ],
    'efu': [
        step('efu', 0, 'Local choice', 'Learn or unlearn · one update', 'Retain set or Forget set · Alternative local objectives', efu_choose(), 'A client receives the current global model and either learns from retained data or unlearns designated forget data. These branches are alternatives within a local update, not sequential training phases. The highlighted unlearning branch is followed in the next scene; either branch later uses the same encrypted submission pipeline.', 'client'),
        step('efu', 1, 'Unlearn', 'Three signals shape forgetting', 'Forget loss + Adversarial loss + Inverted MAS', efu_objective(), 'The local unlearning objective combines negative cross-entropy on the forget set, positive cross-entropy on adversarial variants with incorrect labels, and inverted MAS importance regularization limiting parameter drift. Targeted L2-PGD variants are prepared once offline before the unlearning round. This optimization is an empirical unlearning procedure, not proof of exact information removal.', 'client', 10500),
        step('efu', 2, 'Encrypt', 'Cluster · encrypt · submit', 'Encrypted centroids · Visible map · Partial key', payload('visible-map'), 'After either local learning or unlearning, the client clusters weights and submits encrypted centroids, a directly visible position map and a partial functional key. EFU does not use EncCluster Binary Fuse encoding. Centroids are encrypted under the round label. Identical ciphertext format does not establish invisibility of all timing, mapping or aggregate behavior.', 'client', direction='up'),
        step('efu', 3, 'Expand', 'The map rebuilds encrypted positions', 'Visible mapping → Encrypted model', expand_view(), 'At the server, the directly supplied mapping expands the encrypted centroid codebook into a full encrypted client update. The six-position codebook is schematic and remains the same across these scenes. No individual model is decrypted during expansion.', 'server', 9500),
        step('efu', 4, 'Bind keys', 'One round · one agreed function', 'Function-bound keys · Authorized weighted aggregate', efu_binding(), 'Partial keys bind the agreed aggregation function and round label. Under the paper assumptions, with at least one client refusing shares for an altered function and no full collusion, the authorized aggregate can be decrypted while an omitted-client aggregation lacks a valid key. This restricts permitted decryption; it does not compel continued execution or deployment or destruction of prior model copies.', 'server', 10500),
        step('efu', 5, 'Broadcast', 'Return the updated shared model', 'Aggregate → Clients → Further rounds', efu_return(), 'The server returns the decrypted global aggregate to clients. Later learning may resume on retained data, and clients with no retained data can drop out. Encryption protects the protocol under its assumptions; successful behavioral forgetting and retained utility remain separate evaluation questions.', 'server', direction='down'),
    ],
    'fiba': [
        step('fiba', 0, 'Roles', 'One model · different local objectives', 'Honest learning · Attacker poisoning · Shared aggregation', fiba_start(), 'FiBA is a benchmark of federated invisible backdoor attacks, not a frequency-domain attack or a new defense. Honest clients train normally. An attacker with the stated access modifies local inputs and labels so poisoned training competes with honest updates. Both receive the shared model each round.', 'attacker'),
        step('fiba', 1, 'Poison', 'Alter the input · change the target', 'One attack family per run · Common target t', fiba_poison(), 'An LSB example follows one image x: least-significant pixel bits encode a coordinated trigger, and the poisoned copy is assigned common target label t. The highlighted marks exaggerate the altered locations to explain the operation; they are not actual visual changes or measured images. WaNet, Encoder and LIRA are alternative attack families, not sequential transformations. BadNet is a separate visible baseline in the study.', 'attacker', 9500),
        step('fiba', 2, 'Train', 'Clean and poisoned losses meet locally', 'Clean labels y + Poisoned target t → Attacker update', fiba_train(), 'Honest clients optimize clean labeled data. The malicious client jointly optimizes clean samples with their original labels and poisoned samples with the common target. The resulting local model update is uploaded; the server does not receive these training images. No operational attack code is provided.', 'attacker'),
        step('fiba', 3, 'Aggregate', 'Attacker updates meet honest updates', 'FedAvg baseline or One server defense · Repeated rounds', fiba_aggregate(), 'Honest and attacker model updates enter the server. The experiment chooses FedAvg or one tested defense: Median, Trimmed Mean, FoolsGold, KRUM or Multi-KRUM. These are alternative aggregation conditions, not consecutive defenses and not a promise that all attacks are blocked. The resulting model returns for another training round.', 'server', 10000),
        step('fiba', 4, 'Evaluate', 'Success · utility · detectability', 'Clean accuracy · Attack success · LPIPS · Neural Cleanse', fiba_evaluate(), 'Separate tests ask whether clean inputs retain correct original predictions and whether triggered non-target inputs are predicted as the target. The question marks denote evaluation goals, not guaranteed outputs. LPIPS measures visual change; Neural Cleanse probes model anomaly. Visual subtlety does not imply model-level undetectability.', 'server'),
        step('fiba', 5, 'Placement', 'Probe where LSB changes are placed', 'LSB500 / LSB700 · Low regions · High regions · Unmasked', fiba_attention(), 'This is a separate LSB placement experiment after a RankMe-type convergence check. SmoothGradCAM++ activation maps inform low- and high-region placement, compared with unmasked placement. The paper reports LSB500 and LSB700 only; WaNet and LIRA attention placement are future work. Cells are qualitative, not measured attention. Reported placement labels are preserved without resolving the source mask-ordering inconsistency. Success, LPIPS and anomaly are evaluated separately.', 'attacker', 10000),
    ],
}
