"""Source-reviewed foundation-model paper content.

Sources: MPSL arXiv:2502.06355v3, AE-PSL arXiv:2607.17913v1,
MaTU arXiv:2502.06376v3. Numerical result panels remain in data/insights.
"""
from stories.mpsl_round import STEPS as MPSL_STEPS
from stories.foundation_walkthroughs import AE_STEPS, MATU_STEPS


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
