"""Source-reviewed explanations and bespoke audio-method SVG scenes.

Authoritative sources and caveats are recorded in ../audio-story-review.md.
Diagrams are schematic; positions, waveforms and confidence bars are not data.
"""
from html import escape
from story_art import arrow, group, svg
from stories.fedstar_round import STEPS as FEDSTAR_STEPS
from stories.fedser_round import STEPS as FEDSER_STEPS


def _t(x, y, value, small=False, anchor='middle'):
    cls = 'sa-small' if small else 'sa-label'
    size = 20 if small else 23
    return f'<text x="{x}" y="{y}" class="{cls}" font-size="{size}" text-anchor="{anchor}">{escape(value)}</text>'


def _line(x1, y1, x2, y2, tone='muted', dash=False):
    return f'<path class="sa-{tone}" d="M{x1} {y1} L{x2} {y2}" fill="none" stroke="currentColor" stroke-width="2"' + (' stroke-dasharray="6 6"' if dash else '') + '/>'


def _box(x, y, w, h, tone='accent', rx=12, dash=False):
    return f'<rect class="sa-{tone}" x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="currentColor" fill-opacity="0.07" stroke="currentColor" stroke-width="2"' + (' stroke-dasharray="6 6"' if dash else '') + '/>'


def _dot(x, y, tone='accent', r=7, hollow=False):
    return f'<circle class="sa-{tone}" cx="{x}" cy="{y}" r="{r}" fill="{"none" if hollow else "currentColor"}" stroke="currentColor" stroke-width="2"/>'


def _wave(x, y, w=112, tone='accent', amp=1):
    # Hand-drawn schematic waveform, never a sample or measured signal.
    ys = [0, -2, 1, -7, 8, -13, 17, -23, 19, -12, 6, -8, 12, -18, 14, -6, 3, -2, 0]
    points = ' '.join(f'{x+i*w/(len(ys)-1):.1f},{y+v*amp:.1f}' for i, v in enumerate(ys))
    return f'<polyline class="sa-{tone}" points="{points}" fill="none" stroke="currentColor" stroke-width="3" stroke-linejoin="round"/>'


def _clip(x, y, title, tone='accent', w=160):
    return _box(x, y, w, 74, tone) + _wave(x+14, y+27, w-28, tone, .65) + _t(x+w/2, y+63, title, True)


def _bars(x, y, heights, tone='accent', width=24, gap=14):
    return ''.join(f'<rect class="sa-{tone}" x="{x+i*(width+gap)}" y="{y-h}" width="{width}" height="{h}" rx="3" fill="currentColor" opacity="{1 if i==0 else .45}"/>' for i,h in enumerate(heights))


def _vector(x, y, tone='accent', values=(.2,.8,.5,.35), vertical=False):
    art=''
    for i,v in enumerate(values):
        xx, yy = (x, y+i*23) if vertical else (x+i*23, y)
        art += f'<rect class="sa-{tone}" x="{xx}" y="{yy}" width="18" height="18" rx="3" fill="currentColor" opacity="{v}"/>'
    return art


def _math(body, label):
    return f'<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="{escape(label, quote=True)}">{body}</math>'


# PLiX: support-only centroids, a separate query, and an unchanged encoder.
def _plix_episodes():
    art=group(_t(300,29,'Train on changing word tasks') + _clip(24,65,'Word A',w=150) + _clip(24,164,'Word B','secondary',w=150),0)
    art+=group(_box(223,67,150,166,'muted') + _t(298,101,'Episode') + _t(298,142,'Support',True) + _vector(255,155) + _t(298,209,'Query',True) + arrow(182,102,214,102) + arrow(182,200,214,200),1000)
    art+=group(arrow(382,149,423,149) + _box(437,93,138,112) + _t(506,128,'Encoder') + _t(506,161,'Learn to',True) + _t(506,187,'compare',True),2300)
    art+=group(_t(300,281,'Multilingual training · test words held out',True),3500)
    return svg(art,'Schematic episodic training repeatedly samples word classes and divides their recordings into support and query sets. The encoder learns from query classification loss. Evaluation words are disjoint from the training vocabulary.')


def _plix_prototypes():
    art=group(_t(300,29,'Average supports for each word') + _t(100,71,'Support clips',True) + _clip(27,92,'Word A',w=145) + _clip(27,188,'Word B','secondary',w=145),0)
    art+=group(arrow(179,129,216,129) + arrow(179,225,216,225,'','secondary') + _box(229,104,126,124,'muted') + _t(292,143,'Frozen',True) + _t(292,175,'encoder',True),1000)
    art+=group(_dot(407,99) + _dot(437,116) + _dot(414,140) + _dot(420,207,'secondary') + _dot(450,225,'secondary') + _dot(406,237,'secondary') + _t(436,71,'Embeddings',True) + arrow(361,145,392,122) + arrow(361,189,392,219,'','secondary'),2200)
    art+=group(_line(419,99,487,116,'accent') + _line(449,116,487,116,'accent') + _line(426,140,487,116,'accent') + _line(487,116,510,116,'accent') + _line(432,207,487,222,'secondary') + _line(462,225,487,222,'secondary') + _line(418,237,487,222,'secondary') + _line(487,222,510,222,'secondary') + _dot(526,116,'accent',14,True) + _dot(526,222,'secondary',14,True) + _t(516,169,'Mean',True) + _t(300,287,'Only support examples form prototypes',True),3400)
    return svg(art,'At inference, a frozen shared encoder embeds labeled support recordings. Embeddings are averaged separately for each word to form its prototype, shown as an outlined circle. Query recordings do not enter these averages; all positions are schematic.')


def _plix_distance():
    art=group(_t(300,29,'Classify by distance to prototypes') + _clip(28,94,'New query',w=150) + arrow(185,132,223,132) + _t(113,232,'Same encoder',True),0)
    art+=group(_box(239,58,335,200,'muted') + _dot(452,105,'accent',15,True) + _t(489,110,'A',False) + _dot(475,217,'secondary',15,True) + _t(512,224,'B',False),1100)
    art+=group(_dot(351,130,'warn',10) + _t(324,178,'Query',True),2200)
    art+=group(arrow(363,127,433,109) + _line(360,138,462,206,'secondary',True) + _t(300,286,'Nearest prototype supplies the word label',True),3400)
    return svg(art,'The query is embedded separately and compared with each support-derived prototype using squared Euclidean distance. In this schematic example it is closer to word A. Query position never changes the prototypes.')


def _plix_vocabulary():
    art=group(_t(300,29,'Change the words, keep the encoder') + _box(224,77,152,142,'muted') + _t(300,115,'Encoder') + _t(300,153,'Weights stay',True) + _t(300,182,'fixed',True),0)
    art+=group(_t(107,71,'Vocabulary 1',True) + _dot(76,120,'accent',13,True) + _t(106,127,'A',True) + _dot(76,185,'secondary',13,True) + _t(106,192,'B',True) + _line(139,151,212,151,'muted'),1100)
    art+=group(_t(493,71,'Vocabulary 2',True) + _dot(460,120,'accent',13,True) + _t(494,127,'C',True) + _dot(460,185,'secondary',13,True) + _t(494,192,'D',True) + arrow(386,151,434,151),2400)
    art+=group(_t(300,263,'New support clips → new prototypes',True) + _t(300,290,'Recognition remains a closed-set choice',True),3500)
    return svg(art,'A new set of support recordings replaces the word prototypes while encoder weights remain fixed. The model chooses among the supplied vocabulary; this does not illustrate open-set rejection or continuous wake-word detection.')


# DA-MLDG: target is never an input to meta-training or energy estimation.
def _da_split():
    art=group(_t(300,29,'Rehearse domain shift using sources') + _clip(24,62,'Corpus A',w=147) + _clip(24,166,'Corpus B','secondary',w=147),0)
    art+=group(arrow(178,100,221,100) + arrow(178,203,221,203,'','secondary') + _box(234,66,153,72) + _t(310,109,'Meta-train',True) + _box(234,174,153,72,'secondary') + _t(310,216,'Meta-test',True),1100)
    art+=group(_line(412,55,412,264,'warn',True) + _box(439,86,140,125,'muted',dash=True) + _t(509,125,'Target') + _t(509,161,'Held out',True) + _t(509,189,'of training',True),2300)
    art+=group(_t(300,286,'Source partitions are resampled each iteration',True),3500)
    return svg(art,'Source corpora are randomly partitioned into disjoint meta-train and meta-test subsets. The final target corpus remains outside both subsets and outside all training steps. Two source groups are schematic, not an exact scenario.')


def _da_inner():
    art=group(_t(300,29,'Adapt once on the meta-train sources') + _clip(26,94,'Meta-train',w=160),0)
    art+=group(_vector(231,112,vertical=True) + _t(240,237,'θ',False) + arrow(194,133,219,133),1000)
    art+=group(arrow(269,154,405,154,'Loss gradient') + _t(337,215,'Inner update',True),2100)
    art+=group(_vector(446,112,'accent',(.6,.45,.7,.3),vertical=True) + _t(455,237,'θ′',False) + _t(300,285,'The adapted model will face other source domains',True),3300)
    return svg(art,'An inner gradient step on the meta-train loss changes model parameters theta to theta prime. The adapted parameters are evaluated on the disjoint source meta-test set, rather than the held-out target corpus.')


def _da_margin():
    art=group(_t(300,29,'Estimate shift with the adapted model') + _t(114,65,'Meta-train logits',True) + _bars(55,161,[65,39,49]) + _t(114,196,'Mean energy',True),0)
    art+=group(_t(487,65,'Meta-test logits',True) + _bars(428,161,[43,61,34],'secondary') + _t(487,196,'Mean energy',True),1100)
    art+=group(arrow(192,154,253,154) + arrow(409,154,347,154,'','secondary') + _box(264,105,73,97,'warn') + _t(300,148,'|ΔE|') + _t(300,179,'γ',False),2300)
    art+=group(_t(300,251,'Absolute gap becomes the meta-test weight',True) + _t(300,282,'Energy = average log-sum-exp of logits',True),3500)
    return svg(art,'After inner adaptation, mean log-sum-exp energy is computed separately on source meta-train and meta-test examples. The absolute difference supplies gamma, an adaptive meta-test loss weight. Bars are schematic and carry no measured energy values.')


def _da_outer():
    art=group(_t(300,29,'Optimize across the source-domain split') + _box(30,74,184,76) + _t(122,119,'Meta-train loss',True) + _box(30,185,184,76,'secondary') + _t(122,230,'Meta-test loss',True),0)
    art+=group(_t(264,228,'× γ') + _line(225,111,318,159,'accent') + _line(295,221,318,181,'secondary') + _dot(329,170,'accent',10) + _t(329,129,'+',False),1100)
    art+=group(arrow(346,170,397,170) + _box(411,116,163,99,'muted') + _t(493,154,'Outer update',True) + _t(493,188,'of θ',True),2300)
    art+=group(arrow(493,105,128,53,curved='M493 105 Q493 53 300 53 L128 53') + _t(331,285,'Resample source domains and repeat',True),3500)
    return svg(art,'The outer objective combines meta-train loss with gamma times meta-test loss after inner adaptation. Optimizing theta accounts for the inner update. The next iteration resamples the source-domain partition.')


def _da_results():
    art=group(_t(300,29,'Held-out targets expose uneven gains') + _t(300,61,'DA-MLDG vs. Deep-All · log-mel inputs',True),0)
    for i,(target,up) in enumerate([('IEMOCAP',1),('RAVDESS',0),('TESS',0),('CaFE',1),('AESDD',1),('ShEMO 6',1),('ShEMO 7',0)]):
        row,col=divmod(i,4); x=75+col*150 if row==0 else 150+col*150; y=112+row*104
        tone='accent' if up else 'warn'
        symbol='↑' if up else '↓'
        art+=group(_dot(x,y,tone,23,True)+_t(x,y+8,symbol)+_t(x,y+49,target,True),650+i*400)
    return svg(art,'Derived directional comparison from Table III: DA-MLDG exceeds Deep-All for IEMOCAP, CaFE, AESDD and scenario-six ShEMO, and trails for RAVDESS, TESS and scenario-seven ShEMO. Arrows encode direction only, not gain magnitude or statistical significance.')


STORIES = {
    'fedstar': {
        'overview': 'Most device audio has <strong>no labels</strong>. FedSTAR turns selected local predictions into training targets, combining them with known labels before sharing model updates. Optional public-audio pretraining supplies a stronger starting point.',
        'contributions': [
            '<strong>Local self-training</strong> brings unlabeled audio into the same update as labeled examples.',
            '<strong>Temperature and confidence filtering</strong> limit which predicted targets influence learning.',
            '<strong>Optional contrastive initialization</strong> improves early convergence; three audio tasks test label scarcity and client variation.',
        ],
        'steps': FEDSTAR_STEPS,
        'method': [
            {'title':'Joint local objective', 'text':'The client learns from known labels and retained pseudo-labels in one update. <strong>β = 0.5</strong> weights the unlabeled term in the reported experiments.', 'formula':_math('<msub><mi>ℒ</mi><mi>k</mi></msub><mo>=</mo><msub><mi>ℒ</mi><mi>s</mi></msub><mo>+</mo><mi>β</mi><msub><mi>ℒ</mi><mi>u</mi></msub>', 'Client loss equals supervised loss plus beta times unlabeled loss'), 'note':'ACM TECS §4.1–4.3, Eqs. 3 and 7. Both losses are computed before backpropagation.'},
            {'title':'Confidence-filtered pseudo-labels', 'text':'Apply softmax to temperature-scaled logits, take the most likely class and retain predictions above <strong>τ</strong>. Temperature is 4; the cosine threshold increases from 0.5 to 0.9.', 'formula':_math('<mover><mi>y</mi><mo>^</mo></mover><mo>=</mo><munder><mi>argmax</mi><mi>c</mi></munder><mfrac><msup><mi>e</mi><mrow><msub><mi>z</mi><mi>c</mi></msub><mo>/</mo><mi>T</mi></mrow></msup><mrow><munder><mo>∑</mo><mi>j</mi></munder><msup><mi>e</mi><mrow><msub><mi>z</mi><mi>j</mi></msub><mo>/</mo><mi>T</mi></mrow></msup></mrow></mfrac>', 'Pseudo-label is the class with maximum temperature-scaled softmax probability'), 'note':'Eq. 5 and Table 2. Confidence filtering reduces exposure to uncertain targets; it does not guarantee correct labels.'},
            {'title':'Ordinary federated aggregation', 'text':'A sampled set of clients trains locally and returns model parameters. <strong>FedAvg</strong> forms a data-weighted average; the self-training change is inside the client update.', 'note':'Algorithm 1, PDF p. 12. Experiments simulate clients with the Flower framework.'},
            {'title':'Optional public-data initialization', 'text':'Contrastive pretraining on <strong>FSD-50K</strong> supplies initial encoder weights. The projection layer is discarded before downstream learning.', 'note':'§4.4 and Figure 6. Better performance after 10 rounds is distinct from final accuracy after 100 rounds.'},
        ],
        'takeaways': [
            '<strong>Unlabeled audio helps under scarce labels:</strong> all three selected 15-client, 3%-label comparisons improve, by different amounts.',
            '<strong>Data coverage matters:</strong> the class-skew experiment leaves randomly distributed unlabeled clips available across classes.',
            '<strong>Initialization and final accuracy differ:</strong> faster early convergence does not ensure a better 100-round endpoint.',
        ],
        'result_titles':['Learning with 3% labels','When labeled classes are missing','Pretraining at 100 rounds'],
        'result_leads':['With <strong>15 clients and 3% labels</strong>, self-training improves all three tasks; the gain varies substantially by task.', '<strong>Unlabeled class coverage</strong> supplies information missing from each client’s labeled subset in this specific Speech Commands setup.', 'At <strong>50% unlabeled use and 100 rounds</strong>, pretraining helps with 20% and 50% labels, but not with the two smaller label budgets.'],
        'scope':['Evidence is from the <strong>2022 ACM TECS journal article</strong>; the related ICASSP paper remains a separate publication.', 'Client training is simulated. Keeping raw audio local establishes <strong>data locality</strong>, not differential privacy.'],
    },
    'fedser': {
        'overview': 'Emotion labels are costly, while speech recordings are sensitive. This study combines <strong>spectral, temporal and channel attention</strong> with local self-training, using unlabeled speech while sharing model parameters across devices.',
        'contributions': [
            '<strong>Attention across three axes</strong> reweights the local model’s speech features.',
            '<strong>Participation-aware self-training</strong> uses confident predictions on unlabeled recordings.',
            '<strong>Four IEMOCAP partitions</strong> separate speaker overlap from how speech is distributed across clients.',
        ],
        'steps': FEDSER_STEPS,
        'method': [
            {'title':'Speech representation', 'text':'The method uses <strong>64-bin log-mel features</strong> and four convolutional blocks. Predictions over non-overlapping utterance segments are averaged.', 'note':'§III, public preprint p. 3. Method text specifies two-second segments; Figure 1’s one-second label is inconsistent.'},
            {'title':'Spectral, temporal and channel attention', 'text':'Pooling and convolution produce spectral/temporal maps; pooled channels pass through a small perceptron. Their combined, softmax-scaled weights <strong>multiply the learned features</strong>.', 'note':'§III and Figure 1. The illustration explains feature weighting, not a validated interpretation of human emotion.'},
            {'title':'Joint self-training', 'text':'Known labels supply one cross-entropy term; confident predicted classes supply another. <strong>β</strong> controls the unlabeled contribution.', 'formula':_math('<msub><mi>ℒ</mi><mi>k</mi></msub><mo>=</mo><msub><mi>ℒ</mi><mi>s</mi></msub><mo>+</mo><mi>β</mi><msub><mi>ℒ</mi><mi>u</mi></msub>', 'Client loss equals supervised loss plus beta times unlabeled loss'), 'note':'Eq. 1 and Algorithm 1. Temperature 2 is used when constructing pseudo-labels.'},
            {'title':'Participation-aware confidence and FedAvg', 'text':'The threshold depends on <strong>global progress and local participation</strong>. Clients send updated parameters for data-weighted FedAvg aggregation.', 'note':'§III–IV. The prose describes a threshold increasing from 0.5 to 0.9; printed Eq. 3 conflicts with that description, so no corrected schedule is inferred here.'},
        ],
        'takeaways': [
            '<strong>Self-training improves all four equal-label comparisons</strong> with 10% labels, while staying below each 100%-label reference.',
            '<strong>Unseen speakers remain harder:</strong> the speaker-independent protocol holds out a whole IEMOCAP session.',
            '<strong>Raw speech stays local</strong>, but the study establishes no differential-privacy or model-update attack guarantee.',
        ],
        'result_titles':['Self-training with 10% labels','Centralized and federated references'],
        'result_leads':['Self-training improves <strong>every equal-label comparison</strong> but remains below the fully labeled references.', 'Federated training reduces the same architecture’s UA by <strong>2.06 points for unseen speakers</strong> and <strong>4.26 points with overlapping speakers</strong>. The CNN Transformer is a literature reference.'],
        'scope':['Results use the <strong>IEMOCAP improvised subset and four emotions</strong>; they do not establish cross-corpus or cross-language transfer.', '<strong>FedSER</strong> is a project shorthand for the EmotionAware / IEEE PerCom Workshops 2022 paper. Results and figures are sourced from its public preprint.'],
    },
    'plix': {
        'overview': 'A new voice command should need examples, not a new training run. PLiX learns an acoustic embedding across languages, then recognizes <strong>unseen words</strong> by comparing a query with prototypes built from a few labeled support clips.',
        'contributions': [
            '<strong>Multilingual episodic training</strong> learns to compare words across 20 languages.',
            '<strong>Support-derived prototypes</strong> let a frozen encoder recognize a new vocabulary without retraining.',
            '<strong>Transfer and hardware evaluation</strong> examine unseen languages, language identification and encoder latency/energy.',
        ],
        'steps': [
            {'title':'Learn through word episodes', 'short_title':'Train episodes', 'caption':'Training repeatedly samples support and query clips from selected words. Query classification loss teaches the encoder to handle a changing vocabulary.', 'svg':_plix_episodes()},
            {'title':'Build support prototypes', 'short_title':'Build prototypes', 'caption':'At inference, labeled support clips pass through the frozen encoder. Average embeddings separately for each word; the resulting centroid is that word’s prototype.', 'svg':_plix_prototypes()},
            {'title':'Compare a separate query', 'short_title':'Compare query', 'caption':'Embed the incoming clip with the same encoder, then compare it with each prototype using squared Euclidean distance. The nearest prototype supplies its label.', 'svg':_plix_distance()},
            {'title':'Replace the vocabulary', 'short_title':'Replace vocabulary', 'caption':'New support recordings define new word prototypes while the encoder stays fixed. Predictions select among the supplied words in a closed-set task.', 'svg':_plix_vocabulary()},
        ],
        'method': [
            {'title':'Learn a reusable acoustic space', 'text':'The multilingual base uses <strong>EfficientNet-v2 Medium</strong>, trained in 10-way, 5-shot episodes across 20 languages. Training and test vocabularies contain disjoint words.', 'note':'§2.2–3.3. The TinyNet-E alternatives are separately trained language-specific models, not a compressed copy of the multilingual base.'},
            {'title':'Average support embeddings only', 'text':'For a requested word <em>c</em>, encode each labeled support clip and average its embedding. <strong>The query is excluded</strong> from this computation.', 'formula':_math('<msub><mi>p</mi><mi>c</mi></msub><mo>=</mo><mfrac><mn>1</mn><mrow><mo>|</mo><msub><mi>S</mi><mi>c</mi></msub><mo>|</mo></mrow></mfrac><munder><mo>∑</mo><mrow><mo>(</mo><mi>x</mi><mo>,</mo><mi>y</mi><mo>)</mo><mo>∈</mo><msub><mi>S</mi><mi>c</mi></msub></mrow></munder><msub><mi>f</mi><mi>θ</mi></msub><mo>(</mo><mi>x</mi><mo>)</mo>', 'Class prototype is the average encoder embedding over support examples from that class'), 'note':'§2.1.2, p. 3; Figure 1 explicitly separates the query path from mean pooling.'},
            {'title':'Classify without a weight update', 'text':'Choose the prototype closest to the query embedding in <strong>squared Euclidean distance</strong>. Changing support clips changes the classifier while leaving encoder weights fixed.', 'formula':_math('<mover><mi>y</mi><mo>^</mo></mover><mo>=</mo><munder><mi>argmin</mi><mi>c</mi></munder><msubsup><mrow><mo>‖</mo><msub><mi>f</mi><mi>θ</mi></msub><mo>(</mo><mi>x</mi><mo>)</mo><mo>−</mo><msub><mi>p</mi><mi>c</mi></msub><mo>‖</mo></mrow><mn>2</mn><mn>2</mn></msubsup>', 'Predicted class minimizes squared Euclidean distance between the query embedding and the class prototype'), 'note':'§2.1.2, expressed equivalently to the paper’s argmax of negative squared distance. Most word tests use one-second clips.'},
            {'title':'Separate recognition from encoder cost', 'text':'Recognition tests vary vocabulary size, support count and language. Hardware profiling measures <strong>encoder inference only</strong> on Raspberry Pi 4, Jetson Nano and Pixel 7.', 'note':'Table 1 excludes log-mel extraction and prototype computation. Released weights and inference instructions are linked through aaqibsaeed/plixkws on Hugging Face.'},
        ],
        'takeaways': [
            '<strong>A few examples can define a new vocabulary</strong> without retraining the encoder; recognition depends on the language, support count and number of competing words.',
            '<strong>Transfer is bounded:</strong> five unseen languages and FLEURS episodes show promise, with harder settings still visible.',
            '<strong>Lower encoder cost is useful evidence</strong>, but it does not measure full application energy or accuracy after quantization.',
        ],
        'result_titles':['New words and languages','Encoder latency','Encoder energy'],
        'result_leads':['The same encoder can recognize a new vocabulary from support clips. These are <strong>qualitative observations</strong> from separate recognition experiments.', '<strong>The small encoder is faster</strong> in every measured configuration. These timings exclude preprocessing and prototype computation.', '<strong>The small encoder uses less energy</strong> in each measured configuration; quantization also lowers energy on the two directly comparable platforms.'],
        'scope':['This page describes <strong>arXiv:2305.03058v1</strong>, a 2023 preprint. The implementation source is <strong>aaqibsaeed/plixkws on Hugging Face</strong>.', 'Evaluation uses segmented, <strong>closed-set episodes</strong>. Continuous listening, unknown-word rejection and false-trigger rates are not evaluated.', 'FLEURS contains 102 languages, but reported episodes distinguish <strong>3, 5 or 10 languages</strong>.'],
    },
    'da-mldg': {
        'overview': 'An emotion model can fit one speech corpus and fail on another. DA-MLDG rehearses source-domain shifts during training and weights them with an energy-gap estimate. The study finds <strong>mixed generalization gains</strong> and exposes limits of the representations and benchmarks.',
        'contributions': [
            '<strong>Domain-shift-aware meta-learning</strong> weights the loss on a held-out source subset using an energy gap.',
            '<strong>Seven cross-corpus scenarios</strong> make both improvements and failure cases visible.',
            '<strong>Representation analysis</strong> compares log-mel inputs with TRILLsson embeddings without claiming domain shift is solved.',
        ],
        'steps': [
            {'title':'Split the source domains', 'short_title':'Split sources', 'caption':'Randomly divide source corpora into meta-train and meta-test subsets. Both are training sources; the final target corpus stays entirely outside this loop.', 'svg':_da_split()},
            {'title':'Take the inner update', 'short_title':'Inner update', 'caption':'One gradient step on the meta-train loss produces adapted parameters. The next operations ask how that update behaves on different source domains.', 'svg':_da_inner()},
            {'title':'Estimate the domain gap', 'short_title':'Estimate shift', 'caption':'With the adapted model, compute mean log-sum-exp energy on each source subset. The absolute energy difference becomes the meta-test loss weight.', 'svg':_da_margin()},
            {'title':'Optimize across the shift', 'short_title':'Outer update', 'caption':'Combine the meta-train loss with the weighted meta-test loss, accounting for inner adaptation. Resample the source split for the next iteration.', 'svg':_da_outer()},
            {'title':'Test the unseen corpus', 'short_title':'Test transfer', 'caption':'The log-mel model beats the supervised Deep-All baseline in four of seven scenarios. Arrows show direction only; there is no universal gain or statistical-significance claim.', 'svg':_da_results()},
        ],
        'method': [
            {'title':'Simulate domain shifts within sources', 'text':'Partition source domains into disjoint sets <strong>S′</strong> and <strong>V</strong> at each iteration. A gradient step on S′ produces adapted parameters θ′.', 'formula':_math('<msup><mi>θ</mi><mo>′</mo></msup><mo>=</mo><mi>θ</mi><mo>−</mo><msub><mi>η</mi><mi>s</mi></msub><msub><mo>∇</mo><mi>θ</mi></msub><msub><mi>ℒ</mi><mi>θ</mi></msub><mo>(</mo><msup><mi>S</mi><mo>′</mo></msup><mo>)</mo>', 'Adapted parameters equal theta minus the inner learning rate times the meta-train loss gradient'), 'note':'§III, Eq. 2 and Algorithm 1. V is a source meta-test subset, not the final target test corpus.'},
            {'title':'Use energy as a shift proxy', 'text':'Compute each subset’s average <strong>log-sum-exp of logits</strong> with θ′ and temperature 1. The absolute gap supplies γ, the adaptive weight.', 'formula':_math('<mi>γ</mi><mo>=</mo><mo>|</mo><mi>E</mi><mo>(</mo><msup><mi>S</mi><mo>′</mo></msup><mo>,</mo><msub><mi>p</mi><msup><mi>θ</mi><mo>′</mo></msup></msub><mo>)</mo><mo>−</mo><mi>E</mi><mo>(</mo><mi>V</mi><mo>,</mo><msub><mi>p</mi><msup><mi>θ</mi><mo>′</mo></msup></msub><mo>)</mo><mo>|</mo>', 'Gamma is the absolute difference between meta-train and meta-test mean energies under the adapted model'), 'note':'Eq. 3, printed p. 423. The score is proposed as a proxy for domain shift, not a measured distance between speech distributions.'},
            {'title':'Optimize the weighted outer objective', 'text':'Minimize source training loss plus <strong>γ times meta-test loss after adaptation</strong>. The outer optimization accounts for how θ′ depends on θ.', 'formula':_math('<munder><mi>min</mi><mi>θ</mi></munder><mrow><msub><mi>ℒ</mi><mi>θ</mi></msub><mo>(</mo><msup><mi>S</mi><mo>′</mo></msup><mo>)</mo><mo>+</mo><mi>γ</mi><msub><mi>ℒ</mi><msup><mi>θ</mi><mo>′</mo></msup></msub><mo>(</mo><mi>V</mi><mo>)</mo></mrow>', 'Minimize meta-train loss plus gamma times the meta-test loss evaluated with adapted parameters'), 'note':'Eq. 2. The formula presents the stated objective rather than Algorithm 1’s outer-update line, which omits an explicit gradient symbol.'},
            {'title':'Evaluate representation and transfer together', 'text':'Compare ResNet-18 with log-mel inputs against a variant using <strong>TRILLsson embeddings</strong>. Seven source/target scenarios cover same-language and cross-language transfer.', 'note':'Tables I, III and IV; ten trials per setting. The target corpora remain unseen during training.'},
        ],
        'takeaways': [
            '<strong>Gains are uneven:</strong> with log-mel inputs, DA-MLDG beats Deep-All in four scenarios and leads all four methods in only two.',
            '<strong>Stronger inputs help both approaches:</strong> the embedding variant beats its supervised counterpart in only three of seven scenarios.',
            '<strong>Generalization remains unresolved:</strong> reported means lack dispersion, and the authors judge the resulting performance insufficient for practical use.',
        ],
        'result_titles':['Mixed gains on held-out corpora','Stronger input representations'],
        'result_leads':['DA-MLDG beats Deep-All in <strong>four of seven scenarios</strong> and leads all four methods in only two. The exact table retains RSC and MLDG comparisons.', 'TRILLsson improves DA-MLDG over its log-mel version in <strong>six scenarios</strong>, yet it beats the supervised embedding baseline in only <strong>three</strong>.'],
        'scope':['Evidence is from the <strong>PerFail / IEEE PerCom Workshops 2023</strong> paper. Direct scenario rows are retained; inconsistent printed aggregates are not used.', 'Five selected emotions and limited corpora constrain the evidence; <strong>ShEMO lacks disgust samples</strong>. Its two scenarios use different source corpora.', 'Qualitative embedding plots suggest representation limitations but do not establish their <strong>causal explanation</strong>.'],
    },
}
