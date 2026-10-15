"""Source-reviewed audio explanations and connected method walkthroughs.

Authoritative sources and caveats are recorded in ../audio-story-review.md.
Diagrams are schematic; positions, waveforms and confidence bars are not data.
"""
from html import escape
from stories.fedstar_round import STEPS as FEDSTAR_STEPS
from stories.fedser_round import STEPS as FEDSER_STEPS
from stories.audio_walkthroughs import PLIX_STEPS, DA_STEPS


def _math(body, label):
    return f'<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="{escape(label, quote=True)}">{body}</math>'


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
        'steps': PLIX_STEPS,
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
        'steps': DA_STEPS,
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
