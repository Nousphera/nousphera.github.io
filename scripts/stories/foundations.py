"""Source-reviewed foundation-model stories; schematic art is not measured data.

Sources: MPSL arXiv:2502.06355v3, AE-PSL arXiv:2607.17913v1,
MaTU arXiv:2502.06376v3. Numerical result panels remain in data/insights.
"""
from html import escape
from math import atan2, cos, sin
from story_art import arrow, group, svg
from stories.mpsl_round import STEPS as MPSL_STEPS


def text(x, y, value, tone='', size=22, anchor='middle'):
    return (f'<text x="{x}" y="{y}" class="sa-label {tone}" '
            f'text-anchor="{anchor}" style="font-size:{size}px">{escape(value)}</text>')


def panel(x, y, w, h, tone='accent', radius=12):
    return (f'<g class="sa-{tone}"><rect x="{x}" y="{y}" width="{w}" height="{h}" '
            f'rx="{radius}" fill="currentColor" fill-opacity=".07"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" '
            'fill="none" stroke="currentColor" stroke-width="2"/></g>')


def flow(x1, y1, x2, y2, tone='accent', curved=None, angle=None):
    a = atan2(y2-y1, x2-x1) if angle is None else angle
    ends = [(x2-10*cos(a)+s*6*sin(a), y2-10*sin(a)-s*6*cos(a)) for s in (-1,1)]
    return (arrow(x1,y1,x2,y2,tone=tone,curved=curved)
            + f'<path class="sa-{tone}" d="M{ends[0][0]:.1f} {ends[0][1]:.1f} '
              f'L{x2} {y2} L{ends[1][0]:.1f} {ends[1][1]:.1f}" '
              'fill="none" stroke="currentColor" stroke-width="2.5"/>')


def tokens(x, y, n=4, tone='accent', size=25, gap=7):
    return ''.join(panel(x+i*(size+gap),y,size,size,tone,5) for i in range(n))


def grid(x, y, cols=3, rows=3, size=23, tone='accent'):
    return ''.join(tokens(x,y+j*(size+5),cols,tone,size,5) for j in range(rows))


def signed(x, y, values, tone='accent', size=39):
    return ''.join(panel(x+i*(size+7),y,size,size,tone,5)
                   +text(x+i*(size+7)+size/2,y+size*.7,v,size=24)
                   for i,v in enumerate(values))


def lock(x, y, tone='muted'):
    return (f'<g class="sa-{tone}" fill="none" stroke="currentColor" stroke-width="2.5">'
            f'<path d="M{x+4} {y+12} V{y+7} a7 7 0 0 1 14 0 v5"/>'
            f'<rect x="{x}" y="{y+12}" width="26" height="20" rx="4"/></g>')


def codec(x, y, name, encode=True, tone='accent', frozen=False):
    points = f'{x},{y} {x+55},{y+20} {x+55},{y+70} {x},{y+90}' if encode else f'{x},{y+20} {x+55},{y} {x+55},{y+90} {x},{y+70}'
    return (f'<g class="sa-{tone}"><polygon points="{points}" fill="currentColor" fill-opacity=".10"/>'
            f'<polygon points="{points}" fill="none" stroke="currentColor" stroke-width="2.5"/></g>'
            +text(x+27,y+53,name,size=24)+(lock(x+15,y-40) if frozen else ''))


AE_STEPS = [
    {
        'title': 'Align with pretrained features',
        'short_title': 'Public alignment',
        'caption': 'General Alignment trains the autoencoder to reconstruct public split-layer features. The pretrained client partition stays frozen; the evaluated preparation uses ImageNet100 for 30 epochs.',
        'svg': svg(
            group(text(300,30,'Preparation · public features')
                  +grid(37,101,3,3,22)+text(76,211,'H(x)')+lock(61,53))
            +group(flow(126,140,184,140)+codec(196,94,'E'),700)
            +group(tokens(278,120,1,size=35)+text(296,192,'z'),1600)
            +group(flow(325,140,365,140)+codec(378,94,'D',False),2300)
            +group(flow(444,140,474,140)+grid(492,101,3,3,22)+text(530,211,'Ĥ(x)'),3100)
            +group(flow(528,225,78,225,'secondary',curved='M528 225 V263 H78 V225',angle=-1.5707963267948966)
                   +text(300,253,'Minimize reconstruction error',size=20),3900),
            'Public pretrained patch features pass through an encoder, a small latent representation, and a decoder. Reconstruction error trains the autoencoder while feature extraction stays frozen.'),
    },
    {
        'title': 'Adapt locally, average decoders',
        'short_title': 'Client alignment',
        'caption': 'Client-Specific Alignment adapts each autoencoder for one local epoch using reconstruction loss. Clients retain their own encoders and send only decoder weights for averaging into one shared decoder.',
        'svg': svg(
            group(text(300,29,'Preparation · local reconstruction')
                  +panel(27,55,286,94,'muted')+panel(27,169,286,94,'muted')
                  +text(77,89,'Client 1',size=18)+text(77,203,'Client 2',size=18))
            +group(panel(134,77,58,49)+text(163,111,'E₁')
                   +panel(134,191,58,49,'secondary')+text(163,225,'E₂')
                   +text(164,284,'Keep locally',size=20),700)
            +group(panel(226,77,58,49)+text(255,111,'D₁')
                   +panel(226,191,58,49,'secondary')+text(255,225,'D₂'),1600)
            +group(flow(323,102,423,157)+flow(323,216,423,157,'secondary'),2600)
            +group(codec(444,112,'D',False)+text(472,88,'Average',size=22)
                   +text(472,237,'One decoder',size=20),3600),
            'Two clients retain distinct aligned encoders E1 and E2. Only their decoder weights D1 and D2 travel to the server to produce one averaged decoder.'),
    },
    {
        'title': 'Compress patches, pass CLS directly',
        'short_title': 'Compress activations',
        'caption': 'Fine-tuning begins with both autoencoder halves frozen. Patch activations cross the network as low-dimensional latents, while the classification token (CLS) bypasses compression.',
        'svg': svg(
            group(text(150,27,'Client')+text(460,27,'Server')
                  +'<path class="sa-muted" d="M300 47 V280" fill="none" stroke="currentColor" stroke-dasharray="6 7"/>'
                  +grid(28,135,3,3,20)+text(66,246,'Patches',size=20)
                  +panel(27,59,80,41,'secondary')+text(67,88,'CLS'))
            +group(codec(156,128,'E',True,frozen=True)+flow(112,169,145,169),700)
            +group(tokens(252,151,2,size=22)+flow(307,162,365,162)+text(300,219,'Latents z',size=20),1600)
            +group(codec(379,128,'D',False,frozen=True)+flow(446,169,478,169)
                   +grid(495,135,3,3,20)+text(532,246,'Restore',size=20),2600)
            +group(flow(119,80,490,80,'secondary')+panel(500,59,72,41,'secondary')+text(536,88,'CLS'),3600)
            +group(text(300,283,'Frozen AE · train the split model',size=20),4300),
            'Frozen encoder E compresses patch features into low-dimensional latents sent across the split. Frozen decoder D reconstructs them. A separate uncompressed CLS token bypasses both modules.'),
    },
    {
        'title': 'Return gradients through the frozen AE',
        'short_title': 'Return gradients',
        'caption': 'Predictions return for local loss computation; the server aggregates losses. Backpropagation sends latent and CLS gradients to clients. Gradients pass through the frozen encoder to update client-side LoRA parameters.',
        'svg': svg(
            group(text(300,28,'Fine-tuning · backward direction')
                  +panel(28,111,133,125)+text(95,152,'Client')+text(95,187,'LoRA')
                  +panel(444,111,129,125)+text(508,152,'Server')+text(508,187,'LoRA'))
            +group(codec(206,131,'E',True,frozen=True)+codec(336,131,'D',False,frozen=True),700)
            +group(flow(435,177,399,177,'secondary')+flow(326,177,274,177,'secondary')
                   +text(300,251,'Latent gradient ∇z',size=20),1600)
            +group(flow(196,177,173,177,'secondary')+text(300,285,'Gradient flows; AE weights stay fixed',size=20),2800)
            +group(flow(508,100,94,100,'accent',curved='M508 100 V77 H94 V100',angle=1.5707963267948966)
                   +text(300,65,'CLS gradient · uncompressed',size=20),3800),
            'During backpropagation the server sends a latent gradient leftward through the frozen autoencoder to train client LoRA parameters. The CLS gradient takes its own uncompressed return path.'),
    },
    {
        'title': 'Separate the two inference settings',
        'short_title': 'Two inference modes',
        'caption': 'Global tests average client model weights and bypass the autoencoder. Local FEMNIST tests use each client’s own model with the autoencoder active. These settings answer different questions about compressed training and deployment.',
        'svg': svg(
            group(text(300,27,'After training · two evaluation modes')
                  +text(30,66,'Global',anchor='start')+text(30,190,'Local',anchor='start'))
            +group(panel(30,80,166,72)+text(113,106,'Averaged')+text(113,139,'client model')
                   +flow(207,116,412,116)+text(310,95,'AE bypassed',size=20)
                   +panel(425,80,145,72)+text(497,123,'Server model'),700)
            +group(panel(30,205,166,72,'secondary')+text(113,232,'Individual')+text(113,265,'client model')
                   +flow(207,241,252,241,'secondary'),2200)
            +group(panel(263,205,112,72,'secondary')+text(319,232,'AE')+text(319,265,'active')
                   +flow(386,241,414,241,'secondary')+panel(425,205,145,72,'secondary')+text(497,248,'Server model'),3400),
            'Global evaluation averages client weights and directly joins the server model with the autoencoder bypassed. Local evaluation retains an individual client model and the active autoencoder.'),
    },
]

MATU_STEPS = [
    {
        'title': 'Measure each task from a common origin',
        'short_title': 'Task vectors',
        'caption': 'Clients train their assigned tasks individually. Each task vector is the difference between its fine-tuned weights and the same pretrained model, so all task updates share a reference point.',
        'svg': svg(
            group(text(300,28,'Client · tasks share pretrained weights')
                  +'<g class="sa-muted" fill="none" stroke="currentColor" stroke-width="2"><path d="M85 240 H535 M85 240 V55"/></g>'
                  +panel(56,214,58,47,'muted')+text(85,245,'θp',size=24))
            +group(flow(119,213,276,90)+text(276,66,'Task A')+text(199,137,'τA',size=24),700)
            +group(flow(125,233,452,165,'secondary')+text(465,143,'Task B')+text(330,217,'τB',size=24),1800)
            +group(text(300,280,'Task vector = fine-tuned − pretrained',size=20),3000),
            'Two task vectors point from a shared pretrained weight origin to different fine-tuned task models. This is a schematic weight-space illustration.'),
    },
    {
        'title': 'Elect a sign and aligned magnitude',
        'short_title': 'Elect signs',
        'caption': 'For every coordinate, MaTU takes the sign of the sum of task updates. It then keeps the largest magnitude among entries with that sign. The schematic below illustrates one coordinate.',
        'svg': svg(
            group(text(300,29,'One coordinate · schematic election')
                  +text(45,87,'A',anchor='start')+text(45,147,'B',anchor='start')+text(45,207,'C',anchor='start')
                  +'<path class="sa-muted" d="M150 53 V226" stroke="currentColor" stroke-width="2"/>')
            +group(flow(151,80,222,80)+flow(151,140,276,140)+flow(149,200,109,200,'secondary')
                   +text(310,86,'+',size=26)+text(310,146,'+',size=26)+text(310,206,'−',size=26),700)
            +group(flow(347,140,405,140),1800)
            +group(panel(421,71,142,148)+text(492,107,'Sign: +')
                   +flow(441,145,542,145)+text(492,188,'Keep B',size=22),2900)
            +group(text(300,269,'Largest magnitude with the elected sign',size=20),3900),
            'Three schematic task updates at one coordinate have two positive and one smaller negative update. The positive aggregate sign is elected and the largest positive magnitude is retained.'),
    },
    {
        'title': 'Attach a mask and scalar for each task',
        'short_title': 'Masks and scalars',
        'caption': 'A binary mask keeps coordinates whose signs agree with a task’s update; a scalar corrects the total magnitude. Clients send one unified vector together with these compact task-specific modulators.',
        'svg': svg(
            group(text(300,29,'Client payload · preserve task differences')
                  +text(112,72,'Unified τ')+signed(40,91,['+','+','−']))
            +group(text(395,72,'Task A')+signed(326,91,['1','0','1'])+text(505,120,'λA',size=24),900)
            +group(text(395,183,'Task B')+signed(326,202,['0','1','1'],'secondary')+text(505,231,'λB',size=24),2000)
            +group(flow(112,151,112,217)+panel(33,226,193,49,'muted')+text(129,258,'Shared vector')
                   +text(397,282,'Masks + scalars',size=20),3300),
            'A single signed unified vector is accompanied by a different binary mask and scalar for each task. Illustrative masks select different coordinates.'),
    },
    {
        'title': 'Aggregate within and across related tasks',
        'short_title': 'Related-task aggregation',
        'caption': 'The server first combines clients that share a task, using agreement masks. It then transfers updates from up to κ other tasks whose sign similarity exceeds 0.5, applying the receiving task’s mask.',
        'svg': svg(
            group(text(300,29,'Server · share useful task directions')
                  +text(96,70,'Same task')+signed(28,87,['+','−','+'],size=30)
                  +signed(28,140,['+','−','+'],'secondary',30))
            +group(flow(151,128,213,128)+panel(226,76,141,112)+text(296,112,'Agreement')+text(296,147,'mask'),900)
            +group(text(487,70,'Related tasks',size=20)+signed(422,87,['+','−','+'],size=30)
                   +signed(422,140,['−','+','−'],'muted',30)
                   +flow(413,104,377,104),1900)
            +group('<path class="sa-warn" d="M418 146 L527 174 M418 174 L527 146" fill="none" stroke="currentColor" stroke-width="3"/>',2900)
            +group(flow(296,197,296,228)+text(296,260,'Updated task vectors')
                   +text(478,214,'Top-κ, S > 0.5',size=18),3900),
            'Same-task client updates are combined using an agreement mask. Sign-aligned related tasks can contribute; a conflicting schematic task is excluded. Cross-task transfer is filtered by similarity and top-k selection.'),
    },
    {
        'title': 'Recover task-specific updates for the next round',
        'short_title': 'Recover task updates',
        'caption': 'The server reunifies updated task vectors for each client. On return, each task multiplies the unified vector by its mask and scalar, then adds the recovered update to pretrained weights. Recovery is approximate.',
        'svg': svg(
            group(text(300,28,'Client · modulate the returned vector')
                  +text(300,69,'Unified τ')+signed(231,84,['+','+','−']))
            +group(flow(224,114,158,168)+flow(377,114,443,168,'secondary'),700)
            +group(text(144,190,'λA × mask A',size=20)+text(456,190,'λB × mask B',size=20)
                   +signed(74,207,['+','0','−'])+signed(386,207,['0','+','−'],'secondary'),1800)
            +group(text(144,280,'θp + task A update',size=20)+text(456,280,'θp + task B update',size=20),3300),
            'The returned unified vector branches into two task updates. Task A and task B apply distinct masks and scalar multipliers before adding the recovered vector to the shared pretrained weights.'),
    },
]

MATH = '<math xmlns="http://www.w3.org/1998/Math/MathML" display="block">'

STORIES = {
    'mpsl': {
        'overview': 'Multimodal fine-tuning can overwhelm an edge device even when few parameters change. <strong>MPSL keeps lightweight tokenizers on clients</strong> and runs a shared transformer on the server, coordinating training through local losses and returned gradients.',
        'contributions': [
            '<strong>Multimodal splitting:</strong> support paired image, audio and text inputs with one shared encoder.',
            '<strong>Shared optimization:</strong> aggregate client losses for one server backward pass while keeping raw labels local.',
            '<strong>Task-dependent evidence:</strong> measure accuracy, retrieval, client compute and communication across seven datasets.',
        ],
        'steps': MPSL_STEPS,
        'method': [
            {'title':'Tokenize locally', 'text':'Image patches, audio spectrogram patches and text tokens provide compatible inputs to a modality-agnostic transformer. Clients run the tokenizers; the server runs the encoder and task head.', 'note':'Section 3.1–3.2 and Figure 1 · public preprint, pp. 2–4.'},
            {'title':'Fuse at the right stage', 'text':'Early fusion concatenates token sequences before encoding. Late fusion encodes modalities independently with shared weights and concatenates their representations afterward. The useful choice depends on the task and modality pair.', 'note':'Section 3.2 and Table 5 · pp. 3 and 7.'},
            {'title':'Minimize the combined client loss', 'text':'Predictions return to clients for loss calculation. The server weights each loss by its share of the global batch, backpropagates once, then returns cut-layer gradients to the local tokenizers.', 'formula':MATH+'<msub><mi>ℒ</mi><mi>S</mi></msub><mo>=</mo><munder><mo>∑</mo><mrow><mi>n</mi><mo>∈</mo><mi>𝒩</mi></mrow></munder><mfrac><mrow><mo>|</mo><msub><mi>ℬ</mi><mi>n</mi></msub><mo>|</mo></mrow><mrow><mo>|</mo><mi>ℬ</mi><mo>|</mo></mrow></mfrac><msub><mi>ℒ</mi><msub><mi>C</mi><mi>n</mi></msub></msub></math>', 'note':'Equation (4), p. 4. ℬ<sub>n</sub> is client n’s batch; ℬ is the combined batch. This avoids client-weight synchronization during training, not all coordination.'},
            {'title':'Construct the evaluation model', 'text':'After training, the reported comparisons average the client tokenizers and join them with the shared server model. This post-training aggregation is distinct from the loss-based training loop.', 'note':'Section 3.3 · p. 4.'},
        ],
        'takeaways':[
            '<strong>Client compute falls sharply:</strong> classification uses 0.1 versus FedAvg’s 25.8 GFLOPs per input; this does not measure total system cost.',
            '<strong>Accuracy remains task-dependent:</strong> MPSL improves MELD but trails FedAvg on COCO-QA and Kinetics-Sounds in the selected comparison.',
            '<strong>Retrieval needs enough batch diversity:</strong> it improves over the evaluated distributed baselines but remains below centralized fine-tuning.',
        ],
        'result_titles':['Client compute and classification','Raw image-to-text recall','Batch size and normalized recall'],
        'scope':['Seven paired-modality datasets; missing modalities and client dropouts are future work.','Client GFLOPs are not end-to-end latency, energy or server cost.','Raw recall and normalized recall belong to different experimental settings.'],
    },
    'ae-psl': {
        'overview':'Split learning still sends activations and gradients at every training step. <strong>AE-PSL aligns an autoencoder before fine-tuning</strong>, then freezes it to compress patch features in both directions while preserving compatibility with pretrained representations.',
        'contributions':[
            '<strong>Two-stage alignment:</strong> learn public feature reconstruction, then adapt the compressor to each client.',
            '<strong>Shared decoding:</strong> keep local encoders and average only decoders into one server module.',
            '<strong>Bidirectional compression:</strong> exchange compact patch activations and gradients while leaving CLS uncompressed.',
        ],
        'steps': AE_STEPS,
        'method':[
            {'title':'General Alignment', 'text':'Train the autoencoder on public features with the pretrained client partition frozen. The reported default uses ImageNet100 for 30 epochs. The reconstruction objective is reused during local alignment.', 'formula':MATH+'<msub><mi>ℒ</mi><mtext>rec</mtext></msub><mo>=</mo><mfrac><mn>1</mn><mrow><mo>|</mo><mi>𝒟</mi><mo>|</mo></mrow></mfrac><munder><mo>∑</mo><mrow><mi>x</mi><mo>∈</mo><mi>𝒟</mi></mrow></munder><msubsup><mrow><mo>‖</mo><mi>H</mi><mo>(</mo><mi>x</mi><mo>)</mo><mo>−</mo><msub><mi>D</mi><mi>ψ</mi></msub><mo>(</mo><msub><mi>E</mi><mi>ϕ</mi></msub><mo>(</mo><mi>H</mi><mo>(</mo><mi>x</mi><mo>)</mo><mo>)</mo><mo>)</mo><mo>‖</mo></mrow><mn>2</mn><mn>2</mn></msubsup></math>', 'note':'Equation (1), p. 5, compactly written as a loss. H is the frozen split-layer feature; E/D are encoder/decoder; 𝒟 is public or local alignment data.'},
            {'title':'Client-Specific Alignment', 'text':'Each client adapts both autoencoder halves for one local epoch while keeping the feature extractor frozen. It retains its encoder and sends only decoder weights for a simple mean at the server.', 'formula':MATH+'<msup><mi>ψ</mi><mtext>global</mtext></msup><mo>=</mo><mfrac><mn>1</mn><mi>N</mi></mfrac><munder><mo>∑</mo><mrow><mi>n</mi><mo>∈</mo><mi>𝒩</mi></mrow></munder><msub><mi>ψ</mi><mi>n</mi></msub></math>', 'note':'Section 4.1.2 · p. 5. N is the number of clients; ψn denotes client n’s decoder weights.'},
            {'title':'Fine-tune through frozen compressors', 'text':'With the AE weights fixed, clients send patch-token latents plus the original CLS activation. The server reconstructs patches, predicts, aggregates local losses and returns latent and CLS gradients. Backpropagation through the frozen encoder still updates the client model.', 'note':'Section 4.2 · p. 6. Default: ViT-B/32, split layer 5, LoRA rank 16; four supervised vision datasets.'},
            {'title':'Match the inference setting to the claim', 'text':'Global evaluation aggregates client weights and bypasses the AE; local FEMNIST evaluation keeps each client model and the AE active. Alignment is particularly important when the compressor is removed after training.', 'note':'Section 5.2, Table 2 and Appendix A.3 · pp. 7, 11 and 21. An unaligned AE does not show the same collapse in local tests with the AE retained.'},
        ],
        'takeaways':[
            '<strong>About 10× reduction preserves global accuracy closely:</strong> the five-client results stay within 0.5 points of the uncompressed reference on three datasets.',
            '<strong>Preparation is part of the method:</strong> public alignment, local adaptation and freezing stabilize the compressed feature path.',
            '<strong>Inference mode matters:</strong> global AE-bypassed results and local AE-active results should be read separately.',
        ],
        'result_titles':['Global tests · AE bypassed','Local tests · AE active','Alignment and freezing ablation'],
        'scope':['Supervised vision fine-tuning with ViT-B/32; language and multimodal adaptation are not evaluated.','Public-data preparation and client warm-up are required; uncompressed CLS imposes a communication floor.','Global and local tests use different inference paths and must not be pooled.'],
    },
    'matu': {
        'overview':'Clients with several tasks produce updates that can interfere. <strong>MaTU sends one unified task vector plus per-task masks and scalars</strong>, preserving task differences while enabling server aggregation within tasks and transfer between related tasks.',
        'contributions':[
            '<strong>Compact task representation:</strong> elect a shared vector and retain lightweight task-specific modulators.',
            '<strong>Selective transfer:</strong> combine same-task updates with sign-aligned related tasks.',
            '<strong>No retained client weights:</strong> the server computes task-level updates without storing client-specific models across rounds.',
        ],
        'steps': MATU_STEPS,
        'method':[
            {'title':'Train from a shared reference', 'text':'Each client fine-tunes its assigned tasks separately. A task vector is the change from the common pretrained weights. The experiments use ViT-B/32 with rank-16 LoRA on vision classification tasks.', 'formula':MATH+'<msub><mi>τ</mi><mi>t</mi></msub><mo>=</mo><msubsup><mi>θ</mi><mi>t</mi><mo>*</mo></msubsup><mo>−</mo><msub><mi>θ</mi><mi>p</mi></msub></math>', 'note':'Section 3.1 · p. 2. θ<sub>t</sub><sup>*</sup> denotes fine-tuned task weights and θ<sub>p</sub> the shared pretrained origin.'},
            {'title':'Elect the unified vector', 'text':'At each coordinate, take the sign of the sum of local task vectors. Among entries agreeing with that sign, retain the largest magnitude. This election preserves a common direction without averaging away its amplitude.', 'formula':MATH+'<mi>τ</mi><mo>=</mo><mi>σ</mi><mo>⊙</mo><mi>μ</mi></math>', 'note':'Equation (2) · p. 3. σ is the elected sign, μ the largest aligned magnitude; ⊙ denotes elementwise multiplication.'},
            {'title':'Retain task-specific modulation', 'text':'Each task keeps a binary mask for entries aligned with its own signs and a scalar matching its original total absolute magnitude. These modulators produce approximate task updates from the unified vector.', 'formula':MATH+'<msub><mover><mi>τ</mi><mo>˙</mo></mover><mi>t</mi></msub><mo>=</mo><msub><mi>λ</mi><mi>t</mi></msub><msub><mi>m</mi><mi>t</mi></msub><mo>⊙</mo><mi>τ</mi><mo>,</mo><mspace width=".5em"/><msub><mi>θ</mi><mi>t</mi></msub><mo>=</mo><msub><mi>θ</mi><mi>p</mi></msub><mo>+</mo><msub><mover><mi>τ</mi><mo>˙</mo></mover><mi>t</mi></msub></math>', 'note':'Section 3.2, “Forming clients updates” · p. 4. Client and round indices are omitted consistently; m<sub>t</sub> is a task mask and λ<sub>t</sub> its scalar.'},
            {'title':'Aggregate and return updates', 'text':'The server uses task agreement masks to combine same-task clients, then transfers sign-aligned updates from up to κ related tasks with similarity above 0.5. It reunifies the updated vectors for each client and returns new masks and scalars for the next local-training round.', 'note':'Equations (3)–(7) · p. 4. “Stateless” means no client-specific weights retained across rounds; task-level aggregation still occurs. Cross-task transfer is not uniformly beneficial in the ablations.'},
        ],
        'takeaways':[
            '<strong>Task identity needs modulators:</strong> the mask and scalar turn a shared vector into approximate task-specific updates.',
            '<strong>Several-task clients benefit in the reported benchmark:</strong> MaTU reaches 79.47% at 8.04 Mbit/task/round, versus MaT-FL’s 67.60% at 20.43.',
            '<strong>A centralized gap remains:</strong> the several-task result is 10.74 points below independent fine-tuning; round budgets differ and uncertainty is unreported.',
        ],
        'result_titles':['One task per client','Several tasks per client'],
        'scope':['Vision classification with one backbone and adapter configuration.','MaT-FL uses 300 rounds versus 100 for MaTU in the eight-task tables; no repeated-run uncertainty is reported.','Per-task, per-round bitrate is not total training traffic; the 30-task study reports normalized accuracy.'],
    },
}
