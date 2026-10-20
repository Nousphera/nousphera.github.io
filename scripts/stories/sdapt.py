"""SDAPT's two phases, from the ICASSP 2027 manuscript, pp. 2–4.

Figure 1 and Section 2.1 define the topology: a frozen client partition,
server-side DINOv2 student/EMA teacher, then frozen teacher representations
returned to local supervised task heads. No gradients cross the split in
either phase. Section 3 evaluates IID clients and classification; dense
prediction is a supported representation path, not an evaluated result.
"""
from html import escape

from research_icons import research_icon


MATH = '<math xmlns="http://www.w3.org/1998/Math/MathML" display="block">'


def icon(name):
    return research_icon(name, 'sd-icon')


def reveal(body, at=0, cls=''):
    return f'<div class="{cls}" data-reveal="{at}">{body}</div>'


def badge(text, kind='frozen'):
    return f'<span class="sd-state sd-{kind}">{icon(kind)}{text}</span>'


def client_tag(name):
    return f'<span class="sd-client-tag">{name}</span>'


def tokens(cls=''):
    return f'<span class="sd-tokens {cls}" aria-hidden="true"><b></b><i></i><i></i><i></i></span>'


def arrow(label, direction='out'):
    return f'<div class="sd-route sd-{direction}"><span>{label}</span>{icon("arrow")}</div>'


def network(phase, active):
    server_name = 'Student + EMA teacher' if phase == 1 else 'Adapted teacher'
    return f'''<div class="sd-network" data-sd-phase="{phase}">
      <div class="sd-endpoint {'sd-active' if active == 'client' else ''}" data-sd-client="all">
        {icon('clients')}<div><strong>Clients</strong><small>Images + labels stay local</small></div>
      </div>
      <div class="sd-phase"><strong>Phase {phase} of 2</strong><span>{'Domain adaptation' if phase == 1 else 'Task-head training'}</span></div>
      <div class="sd-endpoint {'sd-active' if active == 'server' else ''}" data-sd-server="shared">
        {icon('server')}<div><strong>Shared server</strong><small>{server_name}</small></div>
      </div>
    </div>'''


def local_views():
    clients = []
    for name in ('A', 'B'):
        views = '<div class="sd-view-group"><span>2 global</span><div class="sd-global-views">' + icon('image') * 2 + '</div></div>'
        views += '<div class="sd-view-group"><span>8 local</span><div class="sd-local-views">' + icon('image') * 8 + '</div></div>'
        clients.append(f'''<div class="sd-card" data-client="{name}">
          <header>{client_tag(name)}<strong>Client {name}</strong><span>Unlabeled images</span></header>
          <div class="sd-view-flow">
            {reveal(f'<div class="sd-image-source" data-local-only="images">{icon("image")}<small>Local image</small></div>', 0)}
            {reveal(f'<div class="sd-crops" data-sd-operation="multi-crop" data-global-crops="2" data-local-crops="8">{views}</div>', 600)}
          </div>
          {reveal(f'<div class="sd-client-encoder" data-sd-operation="client-forward" data-trainable="false">{icon("embedding")}<div><strong>Client partition</strong><small>Patch embed + first block</small></div>{badge("Frozen")}</div>', 1500)}
          {reveal(f'<div class="sd-feature-upload" data-sd-transfer="activations" data-from="client" data-to="server" data-client="{name}">{tokens()}<span>CLS + patch tokens</span>{icon("upload")}</div>', 2400)}
        </div>''')
    return '<div class="sd-pair">' + ''.join(clients) + '</div>' + reveal(
        f'<div class="sd-batch" data-sd-operation="concatenate-client-batches">{icon("server")}<strong>One server batch</strong><span>{client_tag("A")} + {client_tag("B")} + …</span></div>',
        3400)


def server_adaptation():
    teacher = f'''<div class="sd-model sd-teacher" data-sd-model="teacher" data-update="ema">
      <span class="sd-eyebrow">Global views</span>{icon('teacher')}<strong>Teacher</strong><small>EMA weights</small>
    </div>'''
    student = f'''<div class="sd-model sd-student" data-sd-model="student" data-update="gradient">
      <span class="sd-eyebrow">Global + local views</span>{icon('student')}<strong>Student</strong><small>LoRA + last block</small>
      <span class="sd-mask-note">{icon('mask')}Mask global patches</span>
    </div>'''
    models = f'''<div class="sd-distillation">
      {reveal(teacher, 900)}
      {reveal(f'<div class="sd-ema" data-sd-transfer="ema" data-from="student" data-to="teacher">{icon("arrow")}<strong>EMA</strong></div>', 3300)}
      {reveal(student, 900)}
    </div>'''
    objective = f'''<div class="sd-objective" data-sd-operation="server-self-supervision">
      <div class="sd-objective-inputs"><span>Teacher targets ↓</span><span>Student outputs ↓</span></div>
      <div class="sd-loss"><strong>Self-supervised loss</strong><span>DINO + λ₁ iBOT + λ₂ KoLeo</span></div>
      <div class="sd-server-update" data-sd-operation="server-backward" data-from="loss" data-to="student">{icon('gradient')}<strong>Update student</strong><span>Server only</span></div>
    </div>'''
    return reveal(f'<div class="sd-server-batch">{icon("aggregate")}<strong>All client feature batches</strong><span>Shared centering statistics</span></div>', 0) + models + reveal(objective, 2000)


def frozen_representations():
    client = f'''<div class="sd-card sd-inference-client">
      <header>{icon('client')}<strong>Each client</strong></header>
      <div class="sd-original-image" data-local-only="images">{icon('image')}<strong>Original image</strong><small>No multi-crop</small></div>
      <div class="sd-client-encoder" data-sd-operation="client-forward" data-trainable="false">{icon('embedding')}<strong>Client partition</strong>{badge('Frozen')}</div>
    </div>'''
    server = f'''<div class="sd-card sd-frozen-server" data-sd-model="adapted-teacher" data-trainable="false">
      <header>{icon('server')}<strong>Shared server</strong></header>
      {icon('teacher')}<strong>Adapted teacher</strong>{badge('Frozen')}
    </div>'''
    paths = f'''<div class="sd-representation-paths">
      <div data-sd-transfer="activations" data-from="client" data-to="server">{arrow('CLS + patch tokens')}</div>
      <div data-sd-transfer="representations" data-from="server" data-to="client">{arrow('Adapted representations', 'back')}</div>
    </div>'''
    return '<div class="sd-inference">' + reveal(client, 0) + reveal(paths, 900) + reveal(server, 1700) + '</div>' + reveal(
        f'<div class="sd-representation-key">{tokens("sd-encoded")}<strong>CLS → classification</strong><span>Patch tokens → dense tasks*</span></div>', 2900) + reveal(
        '<p class="sd-qualification">*The reported experiments evaluate classification.</p>', 3400)


def local_heads():
    clients = []
    for name in ('A', 'B'):
        clients.append(f'''<div class="sd-card sd-head-card" data-client="{name}">
          <header>{client_tag(name)}<strong>Client {name}</strong><span>Task {name}</span></header>
          {reveal(f'<div class="sd-head-input">{tokens("sd-encoded")}<span>Returned representation</span></div>', 0)}
          {reveal(f'<div class="sd-task-head" data-sd-operation="local-head" data-trainable="true" data-client="{name}">{icon("task")}<strong>Task head</strong>{badge("Trainable", "train")}</div>', 800)}
          {reveal(f'<div class="sd-supervised-loss" data-sd-operation="local-supervised-loss" data-client="{name}"><span>Prediction</span><span>+</span><span data-local-only="labels">Local label</span><strong>Supervised loss</strong></div>', 1700)}
          {reveal(f'<div class="sd-head-update" data-sd-operation="local-head-backward" data-from="local-loss" data-to="local-head">{icon("loop")}<strong>Update this head</strong></div>', 2600)}
        </div>''')
    return '<div class="sd-pair">' + ''.join(clients) + '</div>' + reveal(
        f'<div class="sd-foot">{badge("Backbone stays frozen")}<span>Independent local heads · Parallel training</span></div>', 3400)


def step(phase, active, short, title, caption, body, description):
    art = f'''<div class="story-art sd-art" role="group" aria-label="{escape(description, quote=True)}">
      {network(phase, active)}<div class="sd-scene-body">
        <div class="sd-stage-heading"><span class="sd-eyebrow">{'Unlabeled domain adaptation' if phase == 1 else 'Labeled downstream tasks'}</span><h3>{title}</h3></div>
        {body}
      </div>
    </div>'''
    return {'short_title': short, 'title': title, 'caption': caption,
            'art': art, 'title_in_art': True, 'duration_ms': 8000}


STEPS = [
    step(1, 'client', 'Local views', 'Local images → shared feature batch',
         'Two global + eight local crops · Frozen client layers · Features to the server',
         local_views(),
         'Each client creates two global and eight local crops from an unlabeled image. Its frozen patch embedding and first transformer block produce CLS and patch tokens. Client feature batches are concatenated on the server. The two clients shown stand for the participating clients; raw images stay local.'),
    step(1, 'server', 'Adapt server', 'Self-distill on the shared server',
         'DINO + iBOT + KoLeo · Server gradients · EMA teacher update',
         server_adaptation(),
         'The server teacher processes global views and the student processes global and local views. Global patch tokens are masked for iBOT on the server. A shared DINO, iBOT and KoLeo objective updates the student; an exponential moving average updates the teacher. The client partition is frozen, so no gradients return to clients.'),
    step(2, 'server', 'Freeze backbone', 'Reuse the adapted teacher',
         'Original image → frozen backbone → adapted representation → client',
         frozen_representations(),
         'After adaptation, both the client partition and the adapted server teacher remain frozen. Each client sends original-image tokens. The server returns a CLS representation for classification, or patch representations for dense tasks. Only classification is evaluated in the manuscript.'),
    step(2, 'client', 'Train heads', 'One adapted backbone, local task heads',
         'Returned features + local labels · Train each head independently',
         local_heads(),
         'Each client trains its own supervised task head using returned frozen representations and local labels. Loss gradients update only that client head; no gradients are sent to the server. Multiple tasks can use the same adapted backbone.'),
]


STORIES = {
    'sdapt': {
        'overview': 'Specialized image domains can benefit from adaptation before labels are available. <strong>SDAPT adapts a shared vision backbone from local, unlabeled images</strong>, using frozen client layers and server-side self-supervision. It then freezes the adapted backbone and returns representations for each client to train its own supervised task head.',
        'contributions': [
            '<strong>Adapt without client backpropagation:</strong> frozen client layers send features to a shared DINOv2 student and EMA teacher.',
            '<strong>Separate adaptation from task learning:</strong> one adapted backbone serves local heads with different in-domain tasks.',
            '<strong>Expose the budget trade-off:</strong> compare multi-crop self-distillation with distributed alternatives across three image domains.',
        ],
        'steps': STEPS,
        'method': [
            {
                'title': 'Extract local views through a frozen partition',
                'text': 'Each client creates two global and eight local crops of an unlabeled in-domain image. The frozen client partition produces a CLS activation and patch tokens for every view. Only these activations go to the server; the student and teacher share the client partition.',
                'note': 'Section 2.1, Domain Adaptive Pretraining Phase, and Figure 1 · p. 2. Section 3 · p. 3 uses DINOv2 ViT-B/14 with the first transformer block on the client.',
            },
            {
                'title': 'Adapt one student on the combined batch',
                'text': 'The server concatenates client features into a global batch for DINOv2 self-supervision and batch-level centering. The teacher consumes global views; the student consumes global and local views, with iBOT masking applied to global patch tokens on the server. Gradients update the student, and an exponential moving average updates the teacher.',
                'formula': MATH + '<msub><mi>ℒ</mi><mtext>SSL</mtext></msub><mo>=</mo><msub><mi>ℒ</mi><mtext>DINO</mtext></msub><mo>+</mo><msub><mi>λ</mi><mn>1</mn></msub><msub><mi>ℒ</mi><mtext>iBOT</mtext></msub><mo>+</mo><msub><mi>λ</mi><mn>2</mn></msub><msub><mi>ℒ</mi><mtext>KoLeo</mtext></msub></math>',
                'note': 'Equation (1), Figure 1 and Section 2.1 · pp. 2–3. The server uses LoRA and fully unfreezes its last block; the CheXpert experiments unfreeze the last two. Frozen client layers require no returned gradients.',
            },
            {
                'title': 'Freeze the adapted teacher for downstream features',
                'text': 'After adaptation, the full split backbone is frozen. Clients pass original, non-augmented images through their frozen partition. The server uses the adapted teacher to return CLS features for classification, or patch features for dense tasks.',
                'note': 'Section 2.1, Fine-tuning Phase, and Figure 1 · pp. 2–3. Dense prediction is described by the method; the reported experiments cover classification only.',
            },
            {
                'title': 'Train task-specific heads locally',
                'text': 'Each client combines the returned representation with its own labels to train a supervised task head. Only the head changes, so clients can train in parallel without sending loss gradients to the server.',
                'formula': MATH + '<msubsup><mi>ℒ</mi><mtext>FT</mtext><mrow><mo>(</mo><mi>n</mi><mo>)</mo></mrow></msubsup><mo>=</mo><msub><mi>ℒ</mi><mtext>sup</mtext></msub><mo>(</mo><msub><mi>g</mi><msub><mi>ϕ</mi><mi>n</mi></msub></msub><mo>(</mo><msub><mi>r</mi><mi>n</mi></msub><mo>(</mo><mi>x</mi><mo>)</mo><mo>)</mo><mo>,</mo><mi>y</mi><mo>)</mo></math>',
                'note': 'Equation (2) and Section 2.1 · p. 3. r<sub>n</sub>(x) is the returned representation; g<sub>ϕn</sub> is client n’s head and y its local label.',
            },
        ],
        'takeaways': [
            '<strong>Adapt once, then train local heads:</strong> unlabeled domain data shapes a shared backbone before supervised task learning.',
            '<strong>Multi-crop learning has a cost:</strong> eight extra local views increase feature traffic and client forward computation.',
            '<strong>Benefits depend on the setting:</strong> the reported gains vary with labels, domain and adaptation budget.',
        ],
        'scope': [
            'DINOv2 ViT-B/14, ten IID clients and three image domains; non-IID partitions and dense tasks are future work.',
            'Keeping raw images and labels local does not establish a formal privacy guarantee for transmitted features.',
            'Reported communication counts DAPT feature uplink; client compute counts DAPT forward passes, not total system cost.',
        ],
    },
}
