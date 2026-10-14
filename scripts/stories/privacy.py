"""Source-reviewed privacy and backdoor stories; result values live in insights.

Sources: EncCluster arXiv:2406.09152v1; EFU arXiv:2508.07873v1;
FiBA TU/e accepted manuscript, FinalPaper.pdf (repository cover included).
"""
from html import escape

from story_art import arrow, group, label, svg


def _text(x, y, value, small=False, anchor="middle"):
    return label(x, y, value, "sa-small" if small else "sa-label", anchor)


def _path(d, tone="accent", width=2, dashed=False):
    dash = ' stroke-dasharray="5 5"' if dashed else ""
    return (f'<path class="sa-{tone}" d="{d}" fill="none" '
            f'stroke="currentColor" stroke-width="{width}" '
            f'stroke-linecap="round" stroke-linejoin="round"{dash}/>')


def _box(x, y, w, h, tone="accent", opacity=.10, radius=8):
    return (f'<rect class="sa-{tone}" x="{x}" y="{y}" width="{w}" '
            f'height="{h}" rx="{radius}" fill="currentColor" '
            f'fill-opacity="{opacity}" stroke="currentColor" stroke-width="2"/>')


def _dot(x, y, tone="accent", r=10, opacity=.22):
    return (f'<circle class="sa-{tone}" cx="{x}" cy="{y}" r="{r}" '
            f'fill="currentColor" fill-opacity="{opacity}" '
            'stroke="currentColor" stroke-width="2"/>')


def _cells(x, y, values, cols=3, size=36, gap=6, tones=None):
    out = ""
    for i, value in enumerate(values):
        xx, yy = x+(i % cols)*(size+gap), y+(i//cols)*(size+gap)
        tone = tones[i] if tones else "accent"
        out += _box(xx, yy, size, size, tone, .06 if tone == "muted" else .18, 5)
        if value is not None:
            out += _text(xx+size/2, yy+size/2+7, str(value))
    return out


def _lock(x, y, size=32, tone="accent"):
    # The open space inside the shackle stays transparent in both themes.
    return (f'<g transform="translate({x} {y}) scale({size/32})">'
            + _path("M8 13 V8 A8 8 0 0 1 24 8 V13", tone, 2.5)
            + _box(3, 13, 26, 21, tone, .14, 4)
            + _path("M16 21 V27", tone, 3) + '</g>')


def _key(x, y, tone="secondary", size=1):
    return (f'<g transform="translate({x} {y}) scale({size})">'
            + _dot(0, 0, tone, 10, .06)
            + _path("M10 0 H46 M32 0 V10 M42 0 V7", tone, 3) + '</g>')


def _network(x, y, tone="accent"):
    out = ""
    for a in [y, y+42, y+84]:
        for b in [y+21, y+63]:
            out += _path(f"M{x} {a} L{x+55} {b}", tone)
    for b in [y+21, y+63]:
        out += _path(f"M{x+55} {b} L{x+110} {y+42}", tone)
    for xx, yy in [(x,y),(x,y+42),(x,y+84),(x+55,y+21),
                   (x+55,y+63),(x+110,y+42)]:
        out += _dot(xx, yy, tone, 10)
    return out


def _image(x, y, size=98, triggered=False):
    out = _box(x, y, size, size, "muted", .03)
    out += _path(f"M{x+12} {y+size-20} L{x+size*.38} {y+size*.44} "
                 f"L{x+size*.58} {y+size*.65} L{x+size*.73} {y+size*.52} "
                 f"L{x+size-12} {y+size-20} Z", "accent")
    out += _dot(x+size*.73, y+size*.26, "secondary", 8)
    if triggered:
        for xx, yy in [(15,20),(35,14),(60,76),(78,58),(22,75),(79,78)]:
            out += _path(f"M{x+xx-2} {y+yy} h4 M{x+xx} {y+yy-2} v4", "warn", 2)
    return out


def _math(body, description):
    return ('<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" '
            f'aria-label="{escape(description, quote=True)}"><mrow>{body}</mrow></math>')


def _scene(short_title, title, caption, art, description):
    return {"short_title": short_title, "title": title, "caption": caption,
            "svg": svg(art, description)}


def _enc_cluster():
    art = group(_text(115, 35, "Trained weights") +
                "".join(_dot(x, y, t, 12) for x, y, t in
                        [(65,100,"accent"),(128,86,"secondary"),(172,125,"accent"),
                         (79,163,"secondary"),(133,187,"accent"),(181,196,"secondary")]))
    art += group(arrow(213,146,271,146), 700)
    art += group(_text(342,35,"Centroids") + _dot(342,108,"accent",25) +
                 _text(342,115,"a") + _dot(342,184,"secondary",25) +
                 _text(342,191,"b"), 1500)
    art += group(_text(494,35,"Position map") +
                 _cells(433,82,["a","b","a","b","a","b"],3,36,7,
                        ["accent","secondary","accent","secondary","accent","secondary"]), 2400)
    art += group(_text(300,255,"Encrypt a few values instead of every weight") +
                 _text(300,283,"Keep the position map as a separate component",True), 3300)
    return art


def _enc_encode():
    art = group(_text(106,45,"Centroids") + _dot(73,103,"accent",19) +
                _text(73,110,"a") + _dot(136,103,"secondary",19) + _text(136,110,"b") +
                _text(106,188,"Position map") + _cells(46,211,["a","b","a"],3,36,6))
    art += group(arrow(190,102,295,102) + _text(244,78,"Encrypt",True), 800)
    art += group(_lock(340,79,42) + _lock(410,79,42,"secondary") +
                 _text(411,153,"Centroid ciphertexts",True), 1600)
    art += group(arrow(190,229,295,229) + _text(244,205,"Hash",True), 2400)
    art += group(_cells(328,207,[None]*12,6,24,5,
                        ["secondary","muted","accent","accent","secondary","muted"]*2) +
                 _text(411,188,"BF fingerprints") +
                 _text(411,286,"Queried with a shared seed",True), 3300)
    return art


def _enc_recover():
    art = group(_text(109,34,"Query the filter") +
                _cells(45,88,[None]*12,3,34,6,
                       ["accent","muted","secondary","secondary","accent","muted"]*2) +
                _text(109,281,"Server knows seed",True))
    art += group(arrow(182,159,232,159), 800)
    art += group(_text(300,34,"Recover map") +
                 _cells(244,101,["a","b","a","b","a","b"],2,44,8,
                        ["accent","secondary"]*3), 1600)
    art += group(arrow(358,159,408,159), 2400)
    out = ""
    for i, tone in enumerate(["accent","secondary","accent","secondary","accent","secondary"]):
        out += _lock(433+(i%2)*62,106+(i//2)*48,25,tone)
    art += group(_text(494,34,"Expand values") + out +
                 _text(494,281,"Still encrypted",True), 3200)
    return art


def _enc_aggregate():
    art = group(_text(128,34,"Encrypted clients") +
                _lock(68,76,32) + _lock(128,76,32) +
                _lock(68,170,32,"secondary") + _lock(128,170,32,"secondary") +
                _key(193,93,"accent",.65) + _key(193,187,"secondary",.65))
    art += group(arrow(238,102,305,140) + arrow(238,194,305,158,tone="secondary"), 900)
    art += group(_dot(345,149,"accent",34,.06) + _text(345,157,"Σ") +
                 _text(345,76,"Combine keys",True) +
                 _text(345,222,"Weighted sum",True), 1800)
    art += group(arrow(390,149,430,149) +
                 _cells(448,98,[None]*6,2,34,7) +
                 _text(494,34,"Global model"), 2700)
    art += group(_path("M494 226 V252 H129 V228","muted",2,True) +
                 _path("M122 237 L129 228 L136 237","muted") +
                 _text(310,285,"Distribute the aggregate for the next round",True), 3600)
    return art


def _efu_choose():
    art = group(_text(108,34,"Round model") +
                _cells(49,100,[None]*9,3,31,6) +
                _text(108,255,"Client chooses",True))
    art += group(arrow(187,150,283,86,curved="M187 150 Q225 150 283 86") +
                 arrow(187,150,283,214,tone="secondary",curved="M187 150 Q225 150 283 214"), 900)
    art += group(_text(409,43,"Learn") + _image(303,59,68) +
                 _text(462,86,"Retained",True) + _text(462,112,"data",True), 1700)
    art += group(_text(409,166,"Unlearn") + _image(303,182,68) +
                 _path("M312 188 L359 239 M359 188 L312 239","secondary",2.5) +
                 _text(462,210,"Forget",True) + _text(462,236,"data",True), 2500)
    art += group(_text(249,156,"or",True) +
                 _text(300,286,"Either branch produces the next local update",True), 3400)
    return art


def _efu_objective():
    art = group(_text(102,35,"Forget signal") + _image(56,74,92) +
                _path("M81 201 V237 M72 228 L81 237 L90 228","secondary",3) +
                _text(114,209,"True",True) + _text(114,235,"label",True))
    art += group(_text(202,151,"+") + _text(300,35,"Auxiliary signal") +
                 _image(254,74,92,True) + _text(300,207,"Altered samples",True) +
                 _text(300,235,"Incorrect labels",True), 1200)
    # An anchored parameter and a movable parameter make the drift term concrete.
    art += group(_text(398,151,"+") + _text(501,35,"Limit drift") +
                 _path("M446 90 V162 M437 95 L446 104 M437 112 L446 121 "
                       "M437 129 L446 138 M437 146 L446 155","muted") +
                 _path("M446 126 H458 L466 112 L478 140 L490 112 L502 140 L510 126 H527","accent") +
                 _dot(540,126,"accent",14) + _text(501,207,"Inverted MAS",True) +
                 _text(501,235,"importance",True), 2400)
    art += group(_text(300,283,"Adversarial samples are prepared once, offline",True), 3500)
    return art


def _efu_message():
    art = group(_text(128,34,"Centroid ciphertexts") +
                _lock(68,83,35) + _lock(137,83,35,"secondary") +
                _text(128,180,"Visible mapping") +
                _cells(47,201,["a","b","b","a"],4,34,7,
                       ["accent","secondary","secondary","accent"]))
    art += group(arrow(244,145,334,145) + _text(289,117,"Expand",True), 1000)
    expanded = ""
    for i, tone in enumerate(["accent","secondary","secondary","accent"]):
        expanded += _lock(366+i*51,115,28,tone)
    art += group(_text(458,34,"Encrypted update") + expanded +
                 _text(458,208,"Same message structure",True), 2200)
    art += group(_key(240,265,"secondary",.8) +
                 _text(387,272,"Plus a partial key",True), 3400)
    return art


def _efu_bind():
    art = group(_text(112,34,"Client shares") + _key(64,105,"accent") +
                _key(64,194,"secondary") + _lock(160,88,28) +
                _lock(160,177,28,"secondary"))
    art += group(arrow(210,106,269,137) + arrow(210,194,269,163,tone="secondary"), 900)
    art += group(_box(280,83,104,133,"secondary",.05) +
                 _text(332,121,"Round r") + _path("M293 144 H371","secondary") +
                 _text(332,177,"Rule f") + _text(332,246,"Key-bound",True), 1800)
    art += group(arrow(398,149,445,149) + _dot(504,149,"accent",34,.06) +
                 _text(504,157,"Σ") + _text(504,34,"Aggregate") +
                 _text(504,246,"Permitted result",True), 2700)
    art += group(_text(300,285,"Shares authorize a specific aggregation",True), 3600)
    return art


def _fiba_trigger():
    art = group(_text(105,34,"Clean input") + _image(55,83) +
                _text(105,242,"Original label",True))
    art += group(_text(300,34,"Triggered input") + _image(251,83,98,True) +
                 _text(300,242,"Target label",True), 1000)
    art += group(arrow(167,130,235,130) + _text(201,74,"Poison",True), 1800)
    art += group(arrow(364,130,418,130) + _network(438,88,"warn") +
                 _text(493,34,"Local model") +
                 _text(493,242,"Learn both",True), 2700)
    art += group(arrow(105,190,437,188,tone="muted",curved="M105 190 Q270 231 437 188") +
                 _text(300,284,"Compare subtle triggers with visible BadNet",True), 3600)
    return art


def _fiba_compete():
    art = group(_text(124,34,"Honest updates") +
                _path("M52 115 H181 M52 160 H166 M52 205 H193","accent",5) +
                _text(124,254,"Normal training",True))
    art += group(_text(474,34,"Attacker updates") +
                 _path("M545 133 H424 M545 187 H404","warn",5) +
                 _text(474,254,"Poisoned training",True), 900)
    art += group(arrow(205,159,256,159) + arrow(393,159,344,159,tone="warn"), 1800)
    art += group(_dot(300,159,"secondary",37,.06) + _text(300,167,"Σ") +
                 _text(300,89,"Server",True) + _text(300,231,"One rule",True), 2700)
    art += group(_text(300,286,"FedAvg or a tested defense at aggregation",True), 3600)
    return art


def _fiba_measure():
    art = group(_text(144,34,"Clean test set") + _image(95,72) +
                _text(144,224,"Clean accuracy") +
                _text(144,254,"Correct original labels",True))
    art += group(_text(454,34,"Triggered test set") + _image(405,72,98,True) +
                 _text(454,224,"Attack success") +
                 _text(454,254,"Predicted target labels",True), 1200)
    # The central magnifier denotes inspection, without fabricated score values.
    art += group(_dot(299,111,"secondary",23,.02) +
                 _path("M315 128 L337 150","secondary",5) +
                 _text(299,188,"Inspect",True), 2400)
    art += group(_text(300,286,"Also measure visual distance and model anomaly",True), 3500)
    return art


def _fiba_attention():
    # One activation field and two alternative masks: no implied measured heatmap.
    pattern = ["muted","accent","accent","muted", "muted","accent","accent","muted",
               "muted","accent","accent","muted", "muted","accent","accent","muted"]
    art = group(_text(107,34,"Activation map") +
                _cells(38,88,[None]*16,4,29,6,pattern) +
                _text(107,255,"After convergence",True))
    art += group(arrow(190,155,240,155), 800)
    low = _cells(270,88,[None]*16,4,24,5,
                 ["warn" if t == "muted" else "muted" for t in pattern])
    high = _cells(444,88,[None]*16,4,24,5,
                  ["warn" if t == "accent" else "muted" for t in pattern])
    # Crosses mark trigger support independently of theme color.
    for j, tone in enumerate(pattern):
        xx, yy = (j%4)*29+12, (j//4)*29+12
        left = 270 if tone == "muted" else 444
        if tone == "muted":
            low += _path(f"M{left+xx-4} {88+yy} h8 M{left+xx} {88+yy-4} v8","warn")
        else:
            high += _path(f"M{left+xx-4} {88+yy} h8 M{left+xx} {88+yy-4} v8","warn")
    art += group(_text(326,34,"Low regions") + low + _text(326,255,"Place LSB here",True), 1600)
    art += group(_text(500,34,"High regions") + high + _text(500,255,"Compare placement",True), 2500)
    art += group(_text(300,287,"Compare both with an unmasked LSB baseline",True), 3500)
    return art


STORIES = {
    "enccluster": {
        "overview": "<strong>Make encrypted federated aggregation cheaper.</strong> EncCluster groups model weights into a small codebook, encrypts its centroid values, and sends a compact fingerprint representation of their positions. The server recovers the position map and decrypts an authorized aggregate.",
        "contributions": [
            "<strong>Fewer encryption operations:</strong> encrypt representative centroids instead of every model weight.",
            "<strong>Separate value and position paths:</strong> combine functional encryption with Binary Fuse fingerprints that the server can query.",
            "<strong>Measure the cost of protection:</strong> compare accuracy, upstream traffic and client encryption time across datasets and architectures.",
        ],
        "steps": [
            _scene("Cluster weights", "Separate repeated values from their positions", "After ordinary local training, the client clusters its weights. A small set of centroids represents the values; a separate map assigns every weight position to a centroid.", _enc_cluster(), "Trained weights become two centroid values, a and b, plus a map that assigns each position to a centroid."),
            _scene("Encode two parts", "Encrypt centroids and fingerprint the map", "Functional encryption protects centroid values. Binary Fuse filters encode position–cluster pairs using seeded hashing. These fingerprints are a separate representation, not encrypted centroids or a differential-privacy mechanism.", _enc_encode(), "The centroid branch produces locked ciphertexts. The position-map branch produces a Binary Fuse fingerprint array queried using a shared seed."),
            _scene("Recover positions", "The server reconstructs encrypted weights", "The server knows the shared seed and queries candidate position–cluster pairs to estimate the map. It then places encrypted centroids at the recovered positions; filter false positives can introduce assignment errors.", _enc_recover(), "The server queries a fingerprint array, recovers a visible centroid map, and expands it into a vector of encrypted weight values."),
            _scene("Aggregate securely", "Decrypt the permitted weighted aggregate", "Clients also supply partial functional keys. The server combines them and decrypts the sample-weighted aggregate under the protocol’s assumptions. The resulting global model starts the next training round.", _enc_aggregate(), "Encrypted contributions and partial keys from two clients feed a weighted sum, producing the global model that is redistributed for another round."),
        ],
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
        "steps": [
            _scene("Choose local action", "A client learns or unlearns in a round", "The client receives the global model and takes one branch: normal learning on retained data, or unlearning on its designated forget set. These are alternative local actions, followed by the same submission pipeline.", _efu_choose(), "A received round model forks into two alternatives: learn on retained data or unlearn on forget data. Both alternatives produce a local update."),
            _scene("Shape unlearning", "Combine a forgetting signal with stabilizers", "The standalone objective negates cross-entropy on the forget set, adds cross-entropy on adversarial examples with incorrect labels, and penalizes parameter drift using inverted MAS importance. The adversarial examples are generated once offline.", _efu_objective(), "Three terms combine: reduce the correct-label signal on forget examples, train altered examples with incorrect labels, and anchor parameter movement with inverted MAS importance."),
            _scene("Send encrypted values", "Share ciphertexts, a visible map and a key share", "Clustering replaces many weights with a small centroid set. Clients encrypt those centroids and send the position map directly, along with a partial functional key. The server expands the ciphertexts using this visible map; EFU does not use Binary Fuse filters.", _efu_message(), "Encrypted centroid values and a visible position map expand into an encrypted update; the message also carries a partial functional key."),
            _scene("Bind the aggregate", "Authorize one round and one aggregation rule", "Functional keys bind permitted decryption to the agreed function and round. The guarantee concerns which aggregate can be decrypted under the stated key-sharing assumptions; it does not compel a server to continue executing or destroy earlier model copies.", _efu_bind(), "Client ciphertexts and key shares pass through a gate labelled round r and rule f, authorizing a specific aggregate result."),
        ],
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
        "steps": [
            _scene("Poison local inputs", "Teach a local model an extra association", "Malicious clients train on clean samples and samples carrying a trigger with a common target label. FiBA compares four invisible attack families with visible BadNet; the trigger marks here indicate where an input is altered.", _fiba_trigger(), "An image retains its original label when clean; an altered image is assigned a target label. The malicious local model learns from both clean and poisoned samples."),
            _scene("Compete in aggregation", "Attacker updates meet honest updates", "The global model combines honest and malicious client updates over repeated rounds. Experiments choose FedAvg or one defense at the server; these rules are alternatives. The attacker fraction changes how much poisoned training reaches aggregation.", _fiba_compete(), "Honest and attacker updates flow toward the same server aggregation operation, which uses either FedAvg or one tested defense."),
            _scene("Measure tradeoffs", "Check success, utility and detectability", "Attack success counts triggered non-target test samples predicted as the target. Clean accuracy measures normal-task utility. LPIPS measures visual change, while Neural Cleanse anomaly scores probe model detectability; subtle appearance does not imply an undetectable backdoor.", _fiba_measure(), "Separate clean and triggered test sets measure correct ordinary predictions and target predictions. A magnifier represents visual-distance and model-anomaly inspection."),
            _scene("Probe trigger placement", "Compare LSB placement by model activation", "After a convergence check, activation maps guide low- and high-region LSB placement, compared with an unmasked baseline. The reported tests cover LSB500 and LSB700. Higher success in low regions also raises anomaly scores, exposing an effectiveness–detectability tradeoff.", _fiba_attention(), "An activation map yields alternative low-region and high-region LSB trigger supports, which are compared with unmasked placement."),
        ],
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
