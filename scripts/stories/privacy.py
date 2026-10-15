"""Source-reviewed privacy and backdoor stories; result values live in insights.

Sources: EncCluster arXiv:2406.09152v1; EFU arXiv:2508.07873v1;
FiBA TU/e accepted manuscript, FinalPaper.pdf (repository cover included)."""
from html import escape
from stories.privacy_walkthroughs import WALKTHROUGHS


def _math(body, description):
    return ('<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" '
            f'aria-label="{escape(description, quote=True)}"><mrow>{body}</mrow></math>')


STORIES = {
    "enccluster": {
        "overview": "<strong>Make encrypted federated aggregation cheaper.</strong> EncCluster groups model weights into a small codebook, encrypts its centroid values, and sends a compact fingerprint representation of their positions. The server recovers the position map and decrypts an authorized aggregate.",
        "contributions": [
            "<strong>Fewer encryption operations:</strong> encrypt representative centroids instead of every model weight.",
            "<strong>Separate value and position paths:</strong> combine functional encryption with Binary Fuse fingerprints that the server can query.",
            "<strong>Measure the cost of protection:</strong> compare accuracy, upstream traffic and client encryption time across datasets and architectures.",
        ],
        "steps": WALKTHROUGHS["enccluster"],
        "method": [
            {"title": "Train, then cluster", "text": "Local cross-entropy training produces a weight vector. A separate clustering step assigns those weights to κ centroids. Encryption cost then follows the <strong>number of centroids</strong>, while the map still covers every weight position.", "note": "Section 3.4 and Algorithm 1, PDF pages 6–7. The main configuration uses 128 clusters and 256-bit DMCFE keys."},
            {"title": "Make the map queryable", "text": "Insert each <strong>(position, cluster)</strong> pair into a Binary Fuse filter. The server uses common randomness shared with that client to recover an approximate map. The filter is a compact membership structure; its reconstruction error is not a differential-privacy guarantee.", "note": "Sections 3.4–3.5, PDF pages 7–8. The preprint gives inconsistent filter false-positive configurations, so no universal false-positive rate is asserted here."},
            {"title": "Expand ciphertexts and aggregate", "text": "For each position j, substitute the ciphertext of its estimated centroid. Partial functional keys authorize the weighted aggregate, whose plaintext becomes the next global model.", "formula": _math('<msub><mi>θ</mi><mtext>global</mtext></msub><mo>=</mo><mfrac><mrow><munder><mo>∑</mo><mi>n</mi></munder><msub><mi>N</mi><mi>n</mi></msub><msub><mover><mi>θ</mi><mo>~</mo></mover><mi>n</mi></msub></mrow><mrow><munder><mo>∑</mo><mi>n</mi></munder><msub><mi>N</mi><mi>n</mi></msub></mrow></mfrac>', 'The global model is the sum of client sample counts times reconstructed clustered models, divided by the total sample count.'), "note": "Plaintext result of Algorithm 2 and Section 3.5, PDF page 8. Nₙ is client sample count; θ̃ₙ is its reconstructed clustered model. Individual inputs remain encrypted during aggregation."},
            {"title": "Keep the threat assumptions explicit", "text": "The design assumes an <strong>honest-but-curious server and setup authority</strong>, secure channels and key provisioning. Clients may disclose their weights in collusion but do not poison updates. Aggregate subtraction under extensive collusion can expose a clustered contribution; lossy clustering alone does not establish confidentiality of that contribution.", "note": "Sections 3.2–3.3 and 4.2, PDF pages 5–6 and 9–10. Poisoning and denial of service are outside the analysis."},
        ],
        "takeaways": [
            "<strong>Compression makes encryption practical in the tested workload:</strong> EncCluster reports 0.284× FedAvg upstream volume and 2.04 seconds of client encryption for CIFAR-10 with full participation.",
            "<strong>Accuracy remains close to each baseline:</strong> the selected CIFAR-10 condition loses 0.32 points under IID and 0.79 under non-IID data. These are reported results, without run counts or uncertainty estimates.",
            "<strong>Keep privacy mechanisms distinct:</strong> centroid encryption, a server-recoverable map and lossy clustering provide different properties. Filter errors and embedding reconstruction error do not prove differential privacy or resistance to every inference attack.",
        ],
        "result_titles": ["Encryption and communication cost", "Accuracy across architectures"],
        "result_leads": [
            "<strong>EncCluster reduces encrypted-upload cost in this fixed condition.</strong> Its upstream ratio is 0.284× FedAvg and encryption takes 2.04 seconds, versus 2.581× and 7.64 seconds for SEFL. Unencrypted clustering is cheaper still, but provides a different protection level.",
            "<strong>The compression cost remains modest across the tested backbones.</strong> Every row compares against that architecture’s own FedAvg baseline; CIFAR-100 loses more accuracy than CIFAR-10. These results do not establish hardware-independent encryption times.",
        ],
    },
    "efu": {
        "overview": "<strong>Bind learning and unlearning updates to an agreed aggregate.</strong> EFU uses client-side unlearning, weight clustering and functional encryption so both update types follow the same encrypted submission path. The study measures forgetting behavior and retained utility alongside signals that might reveal unlearning.",
        "contributions": [
            "<strong>Client-controlled updates:</strong> clients either learn from retained data or compute an update intended to forget selected data.",
            "<strong>Function-bound aggregation:</strong> encrypted centroids and partial keys restrict which aggregate the server can decrypt.",
            "<strong>Forgetting at several levels:</strong> evaluate sample, class and task removal with a standalone objective and wrapped client-side unlearning methods.",
        ],
        "steps": WALKTHROUGHS["efu"],
        "method": [
            {"title": "Make learning and unlearning alternatives", "text": "Algorithm 1 branches on the local forget set. A learning client minimizes cross-entropy on retained data; an unlearning client computes a removal update. Both then <strong>cluster, encrypt and submit</strong> through the same protocol.", "note": "Section 4.3 and Algorithm 1, PDF pages 6–7. Matching ciphertext format is one part of concealment, not a complete audit of observable metadata."},
            {"title": "Regularize the removal update", "text": "The standalone loss combines a negative forget-set cross-entropy term, an auxiliary term for adversarial examples with incorrect labels, and <strong>inverted MAS</strong> importance weights that constrain parameter drift.", "formula": _math('<msub><mi>L</mi><mtext>UN</mtext></msub><mo>=</mo><mo>−</mo><msub><mi>L</mi><mtext>forget</mtext></msub><mo>+</mo><msub><mi>L</mi><mtext>adv</mtext></msub><mo>+</mo><msub><mi>R</mi><mtext>MAS</mtext></msub>', 'The unlearning loss equals negative forget loss plus adversarial auxiliary loss plus inverted MAS regularization.'), "note": "Equation 3, PDF page 6, with terms abbreviated. R<sub>MAS</sub> = ∑<sub>j</sub>(1 − Ω<sub>j</sub>)(θ<sub>j</sub> − θ̃<sub>j</sub>)<sup>2</sup>; θ̃ is the model before unlearning. Offline adversarial preparation is excluded from the plotted local runtime."},
            {"title": "Compress the encrypted submission", "text": "Encrypt κ centroid values under the current round label, transmit the <strong>visible position map</strong>, and include a partial functional key. The server expands encrypted centroids to weight positions and recovers a sample-weighted aggregate.", "note": "Sections 4.3–4.4 and Algorithm 2, PDF pages 7–8. The experiments use 64 centroids and 256-bit encryption."},
            {"title": "Read function binding within its assumptions", "text": "The complete-aggregation argument requires at least one client to withhold a share for an altered function or label. Update-type indistinguishability excludes full collusion and is conditioned on <strong>indistinguishable function outputs</strong>. Visible maps, timing and other observations remain separate questions.", "note": "Section 4.5 and Appendix B, PDF pages 8 and 17–18. Trusted clients perform key generation, encryption and unlearning correctly. Authorized decryption does not enforce deployment or deletion of old models."},
            {"title": "Separate empirical forgetting from exact erasure", "text": "Compare retained and forgotten accuracy with full retraining. Parameter-change and traffic plots describe observable behavior, but the paper does not train an intent detector or quantify its attack advantage. Low forgotten-class accuracy alone is not proof of complete information removal.", "note": "Tables 1–2 and Figures 2–3, PDF pages 9–12; Appendix C, page 18. The evaluated PGD and FedOSD wrappers add MAS, while SGA-EWC retains EWC; their optimization is not uniformly unchanged."},
        ],
        "takeaways": [
            "<strong>Read utility and forgetting together:</strong> CIFAR-10 class-wise EFU reports 92.43% retained accuracy and 13.06% forgotten accuracy, versus 94.82% and 13.72% for retraining.",
            "<strong>Task removal preserves another task in the reported setting:</strong> on LFW, EFU retains 95.37% gender accuracy while identity accuracy falls to 5.12%. Gender utility remains 1.49 percentage points below retraining.",
            "<strong>Cryptographic scope matters:</strong> function binding restricts decryptable aggregates; it does not prove exact data erasure, force deployment, or establish concealment from every server observation.",
        ],
        "result_titles": ["Retained utility and class forgetting", "Forget identity, retain gender"],
        "result_leads": [
            "<strong>EFU approaches the retraining reference on forgotten-class behavior, with a utility cost.</strong> Retained CIFAR-10 accuracy is 2.39 percentage points below retraining. The complete baseline and wrapper comparison is shown; low forgotten accuracy is a behavioral measure, not an erasure certificate.",
            "<strong>Identity forgetting and gender retention are separate measurements.</strong> EFU reaches 5.12% identity accuracy and 95.37% gender accuracy, versus retraining’s 4.71% and 96.86%. This experiment uses all 30 clients with full participation.",
        ],
    },
    "fiba": {
        "overview": "<strong>Test how visually subtle backdoors survive federated training.</strong> FiBA adapts invisible trigger families to a shared benchmark and compares their success, clean-model utility and detectability. A separate LSB experiment asks whether placing a trigger in low-activation image regions changes that tradeoff.",
        "contributions": [
            "<strong>A federated comparison:</strong> evaluate LSB, WaNet, Encoder and LIRA attacks alongside visible BadNet under controlled client participation.",
            "<strong>Expose defense tradeoffs:</strong> compare attack success with clean accuracy for the tested aggregation rules and attack configurations.",
            "<strong>Probe attention-based placement:</strong> compare low, high and unmasked LSB triggers, including both perceptual distance and model anomaly scores.",
        ],
        "steps": WALKTHROUGHS["fiba"],
        "method": [
            {"title": "Adapt attacks to a federated benchmark", "text": "Use ResNet-18 on CIFAR-10 and CIFAR-100 with nonoverlapping, non-IID client data. Malicious clients learn a common target from poisoned samples while honest clients train normally. Coordinated attackers share the required trigger string, warping field, encoder or pretraining resources for their attack family.", "note": "Sections 3.1 and 4, PDF pages 5–9. Main settings: 10 clients, 100 rounds, five local epochs, Dir(0.5) and poison rate 0.5. This is an evaluation study, not a new defense."},
            {"title": "Compare one aggregation rule at a time", "text": "The defense grid compares <strong>FedAvg, Median, Trimmed Mean, FoolsGold, KRUM and Multi-KRUM</strong> under fixed attack conditions. Each rule can change both backdoor success and clean accuracy. Model replacement and distributed triggers are additional probes with their own assumptions.", "note": "Table 2 and Figures 3–6, PDF pages 11–14. The defense grid has BadNet, LSB, WaNet and Encoder rows; it does not include LIRA or report a PCA column."},
            {"title": "Keep the evaluation axes separate", "text": "<strong>Attack success rate</strong> is the proportion of poisoned non-target test samples classified as the target. Clean accuracy measures ordinary utility; LPIPS and Neural Cleanse anomaly scores measure different aspects of detectability. Reported ± values are retained exactly because the paper does not define their dispersion statistic or run count.", "note": "Section 4 and Tables 1–3, PDF pages 9–11 and 14. These measurements do not establish statistical significance or a universal failure of robust aggregation."},
            {"title": "Test low-activation placement specifically for LSB", "text": "A RankMe-type embedding score checks convergence before <strong>SmoothGradCAM++</strong> maps are accumulated. The experiment compares reported low-, high- and unmasked placement for LSB500 and LSB700. Concentrating changes can also alter trigger intensity, so the comparison does not isolate attention from every other factor.", "note": "Section 3.2, Algorithm 1, Table 3 and Figure 7, PDF pages 7–8 and 14–15. Prose and mask-ordering descriptions differ; placement labels are preserved as reported. WaNet and LIRA attention placement remain future work."},
        ],
        "takeaways": [
            "<strong>Attacker participation changes outcomes:</strong> every tested attack has higher mean success at 20% than at 10% attackers in Table 1. The size of the increase varies considerably by trigger family.",
            "<strong>Attack suppression can cost clean utility:</strong> for LSB on CIFAR-10 with 10% attackers, Multi-KRUM reports 1.47±0.45% attack success and 69.67±1.89% clean accuracy, versus FedAvg’s 41.59±6.19% and 83.37±0.33%.",
            "<strong>Low-activation placement is a tradeoff:</strong> LSB700 gains 19.80 percentage points of mean attack success over unmasked placement, while its anomaly score rises from 1.61 to 3.04 and LPIPS also increases. Improved success is not improved stealth on every measure.",
        ],
        "result_titles": ["Attack success by attacker fraction", "Defense success and utility cost", "LSB placement and detectability"],
        "result_leads": [
            "<strong>More malicious clients strengthen all five attacks in this comparison.</strong> WaNet and Encoder pass 80% mean attack success at 20% attackers. The same table’s clean accuracies and reported ± values remain available in the experiment details.",
            "<strong>A lower attack-success rate is only half the outcome.</strong> Multi-KRUM strongly suppresses this LSB configuration but also lowers clean accuracy. Trimmed Mean raises mean attack success here. These results are specific to CIFAR-10 with 10% attackers and the tested defense settings.",
            "<strong>Low-region LSB700 is more effective and more detectable by the reported model metric.</strong> Mean attack success rises from 41.59% to 61.39%, while anomaly rises from 1.61 to 3.04 and visual distance increases. LSB500 shows a smaller gain, so the effect is not uniform across trigger sizes.",
        ],
    },
}
