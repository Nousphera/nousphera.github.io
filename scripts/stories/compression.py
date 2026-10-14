"""Source-reviewed compression stories; examples are schematic, never measurements.

Sources: FedCompress arXiv:2401.14211v3; FedCode arXiv:2311.09270v1;
DeltaMask IEEE BigData accepted manuscript, TU/e 2024337517.pdf.
"""
from html import escape

from story_art import arrow, group, label, svg


def _text(x, y, value, small=False, anchor="middle"):
    return label(x, y, value, "sa-small" if small else "sa-label", anchor)


def _circle(x, y, r=13, tone="accent", hollow=False):
    return (f'<g class="sa-{tone}"><circle cx="{x}" cy="{y}" r="{r}" '
            f'fill="currentColor" fill-opacity="{0.08 if hollow else 0.28}" '
            'stroke="currentColor" stroke-width="2"/></g>')


def _box(x, y, w, h, tone="accent", opacity=.12, dashed=False):
    dash = ' stroke-dasharray="5 5"' if dashed else ""
    return (f'<g class="sa-{tone}"><rect x="{x}" y="{y}" width="{w}" '
            f'height="{h}" rx="7" fill="currentColor" fill-opacity="{opacity}" '
            f'stroke="currentColor" stroke-width="2"{dash}/></g>')


def _line(path, tone="muted", dashed=False):
    dash = ' stroke-dasharray="5 5"' if dashed else ""
    return (f'<g class="sa-{tone}"><path d="{path}" fill="none" '
            f'stroke="currentColor" stroke-width="2"{dash}/></g>')


def _cells(x, y, vals, size=42, gap=6, cols=None, tones=None):
    cols = cols or len(vals)
    out = ""
    for i, value in enumerate(vals):
        cx, cy = x + (i % cols) * (size + gap), y + (i // cols) * (size + gap)
        tone = tones[i] if tones else "accent"
        out += _box(cx, cy, size, size, tone, .08 if tone == "muted" else .2)
        if value is not None:
            out += _text(cx + size/2, cy + size/2 + 7, str(value))
    return out


def _grid(x, y, tones, cols=4, size=25, gap=5):
    return _cells(x, y, [None] * len(tones), size, gap, cols, tones)


def _math(body, description):
    return ('<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" '
            f'aria-label="{escape(description, quote=True)}"><mrow>{body}</mrow></math>')


def _scene(title, caption, art, description):
    return {"title": title, "caption": caption, "svg": svg(art, description)}


def _compress_cluster():
    scattered = [(57,103),(96,77),(131,130),(68,173),(123,197),(169,91),
                 (174,164),(208,127),(204,207)]
    tones = ["accent", "secondary", "accent", "muted", "secondary", "muted",
             "accent", "secondary", "muted"]
    art = group(_text(132,35,"Local weight values") +
                "".join(_circle(x,y,12,t) for (x,y),t in zip(scattered,tones)))
    art += group(arrow(240,143,325,143), 800)
    centers = ""
    for x, tone in [(365,"accent"),(445,"secondary"),(525,"muted")]:
        centers += _line(f"M{x} 76 V218", tone, True)
        centers += "".join(_circle(x,y,13,tone) for y in [94,145,196])
    art += group(_text(445,35,"Shared centroids") + centers, 1500)
    art += group(_text(300,258,"Warm up, then train with clustering") +
                 _text(300,285,"Color = shared weight value",True), 2400)
    return art


def _compress_average():
    art = group(_text(177,34,"Clustered clients") + _text(42,105,"A",True) +
                _cells(72,76,["−1","−1","1","1"],44,6) +
                _text(42,201,"B",True) + _cells(72,172,["0","2","0","2"],44,6,
                tones=["secondary"]*4))
    art += group(arrow(280,146,345,146), 900)
    art += group(_text(457,34,"After averaging") +
                 _cells(357,122,["−½","½","½","1½"],45,5,
                 tones=["accent","secondary","secondary","muted"]), 1700)
    art += group(_text(300,255,"Two values per client become three") +
                 _text(300,283,"Equal-weight average",True), 2600)
    return art


def _compress_distill():
    varied = ["accent","secondary","muted","secondary","muted","accent", "secondary","accent"]
    clustered = ["accent","accent","secondary","accent","secondary","secondary","accent","secondary"]
    art = group(_text(144,35,"Global teacher") + _grid(62,70,varied) +
                _text(144,188,"Aggregated weights",True))
    bars = ""
    for x, heights, tone in [(204,[57,27,42],"muted"),(493,[55,29,42],"accent")]:
        for j,h in enumerate(heights):
            bars += _box(x+j*18,140-h,12,h,tone,.35)
    art += group(_text(438,35,"Clustered student") + _grid(354,70,clustered) + bars, 900)
    art += group(arrow(266,114,339,114) + _text(300,68,"Match",True) +
                 _text(300,90,"outputs",True), 1700)
    art += group(_text(300,250,"Unlabeled server data") +
                 arrow(260,221,140,208,curved="M260 221 Q200 212 140 208") +
                 arrow(340,221,448,208,curved="M340 221 Q400 212 448 208") +
                 _text(300,281,"Distillation restores a compact global model",True), 2700)
    return art


def _compress_capacity():
    art = group(_text(125,38,"Local embeddings") +
                _grid(63,83,["accent","secondary","accent","muted"]*3,4,27,6) +
                _text(125,216,"Effective rank",True))
    art += group(arrow(218,139,297,139), 800)
    art += group(_text(436,38,"Score progress") +
                 _line("M320 180 H557 M320 180 V76") +
                 _line("M328 164 L361 131 L394 108 L430 96 L469 94 L507 94 L548 94","accent") +
                 _circle(469,94,5) + _circle(507,94,5) + _circle(548,94,5) +
                 _text(437,216,"Watch for a plateau",True), 1600)
    art += group(_text(300,258,"If progress stalls, add cluster capacity") +
                 _text(300,285,"Increase capacity within the allowed budget",True), 2700)
    return art


def _codebook_parts():
    pattern = ["accent","secondary","accent","muted","secondary","muted", "accent","accent","secondary"]
    art = group(_text(105,37,"Weights") + _grid(43,91,pattern,3,35,7) +
                _text(105,252,"Repeated values",True))
    art += group(arrow(183,149,238,149), 700)
    centers = _text(300,37,"Codebook")
    for y,tone,value in [(100,"accent","a"),(150,"secondary","b"),(200,"muted","c")]:
        centers += _circle(300,y,21,tone) + _text(300,y+7,value)
    art += group(centers + _text(300,252,"Which values?",True), 1400)
    art += group(_text(491,37,"Index map") +
                 _cells(425,86,["a","b","a","c","b","c","a","a","b"],37,7,3,pattern) +
                 _text(491,252,"Which positions?",True), 2100)
    art += group(_text(300,286,"FedCode usually sends only the codebook",True), 3000)
    return art


def _codebook_nearest():
    art = group(_text(300,32,"Received, sorted centers") +
                _line("M75 85 H525") +
                "".join(_circle(x,85,20,t)+_text(x,92,v) for x,t,v in
                        [(100,"accent","a"),(300,"secondary","b"),(500,"muted","c")]))
    for i,(x,dest,tone) in enumerate([(128,100,"accent"),(248,300,"secondary"),
                                     (350,300,"secondary"),(468,500,"muted")]):
        art += group(_circle(x,188,12,tone,True) +
                     arrow(x,169,dest,112,tone=tone), 700+i*350)
    art += group(_text(300,234,"Map each local weight to its nearest center") +
                 _text(300,266,"Then train on the client’s data",True), 2600)
    return art


def _codebook_server():
    art = group(_text(121,32,"Client codebooks") +
                _text(34,107,"A",True) + _circle(91,100,19) + _circle(153,100,19) +
                _text(34,206,"B",True) + _circle(91,199,19,"secondary") +
                _circle(153,199,19,"secondary"))
    art += group(arrow(185,100,267,128) + arrow(185,199,267,172,tone="secondary"),800)
    art += group(_text(312,32,"Concatenate") +
                 "".join(_circle(311,y,17,t) for y,t in
                         [(86,"accent"),(130,"accent"),(174,"secondary"),(218,"secondary")]),1600)
    art += group(arrow(346,151,404,151) + _text(493,32,"Global weights") +
                 _grid(428,98,["accent","secondary","accent","secondary","secondary","accent"],3,36,7),2400)
    art += group(_text(300,271,"Replace global values by nearest received centers",True),3200)
    return art


def _codebook_calibrate():
    art = group(_text(146,34,"Codebook rounds") +
                "".join(_circle(x,87,17,t) for x,t in
                        [(90,"accent"),(146,"secondary"),(202,"muted")]) +
                arrow(146,116,146,158) +
                _grid(86,175,["accent","secondary","accent","muted","secondary","accent"],3,34,8) +
                _text(146,278,"Reuse local positions",True))
    art += group(arrow(262,86,339,86) + _text(300,59,"Periodically",True),900)
    art += group(_text(448,34,"Calibration rounds") +
                 _circle(383,91,16) + _text(420,98,"+") +
                 _cells(448,65,["a","b","b","a"],31,5,2) +
                 arrow(448,149,448,169),1700)
    art += group(_grid(388,183,["accent","secondary","secondary","accent","secondary","accent"],3,32,8) +
                 _text(448,278,"Reconstruct positions",True),2600)
    return art


_REFERENCE = [1,1,0,1,0,1,0,1]
_LOCAL = [1,0,0,0,1,1,1,1]


def _mask_freeze():
    base = ["accent"]*9
    mask = [1,0,1,0,1,1,1,0,1]
    tones = ["accent" if b else "muted" for b in mask]
    art = group(_text(106,36,"Fixed weights") + _grid(46,84,base,3,34,7) +
                _text(106,253,"Pretrained",True))
    art += group(_text(207,148,"⊙") + _text(300,36,"Learned mask") +
                 _cells(240,84,mask,34,7,3,tones) +
                 _text(300,253,"Sampled bits",True),900)
    art += group(_text(398,148,"=") + _text(493,36,"Subnetwork") +
                 _grid(433,84,tones,3,34,7) +
                 _text(493,253,"Selected weights",True),1800)
    art += group(_text(300,285,"Train mask scores; keep the backbone weights fixed",True),2800)
    return art


def _mask_difference():
    changes = [a ^ b for a,b in zip(_REFERENCE,_LOCAL)]
    art = group(_text(300,29,"Compare with the shared seeded sample") +
                _text(78,87,"Shared",True) + _cells(175,59,_REFERENCE,39,6))
    art += group(_text(78,159,"Local",True) + _cells(175,131,_LOCAL,39,6),900)
    art += group(_text(78,231,"Changed",True) +
                 _cells(175,203,changes,39,6,tones=["accent" if b else "muted" for b in changes]),1800)
    art += group(_text(300,282,"Only differing positions enter the update set",True),2800)
    return art


def _mask_rank():
    art = group(_text(300,34,"Rank changed positions by relative entropy") +
                _text(300,68,"KL compares local and global probabilities",True))
    for i,(x,position) in enumerate([(90,5),(230,2),(370,7),(510,4)]):
        tone = "accent" if i < 3 else "muted"
        art += group(_circle(x,128,29,tone) + _text(x,135,str(position)),600+i*350)
        if i < 3:
            art += group(arrow(x+37,128,x+98,128,tone="muted"),800+i*350)
    art += group(_line("M57 183 V198 H403 V183","accent") +
                 _text(230,238,"Keep the top-κ subset") +
                 _text(510,238,"Omit",True),2200)
    art += group(_text(300,281,"κ controls how many ranked changes are sent",True),3100)
    return art


def _mask_filter():
    art = group(_text(108,35,"Positions") +
                "".join(_circle(108,y,22)+_text(108,y+7,str(v)) for y,v in
                        [(88,5),(151,2),(214,7)]))
    hashes = ""
    for path in ["M139 88 Q174 88 197 151","M139 151 H197",
                 "M139 214 Q174 214 197 151","M197 151 Q220 88 244 82",
                 "M197 151 Q220 115 244 115","M197 151 Q220 181 244 181",
                 "M197 151 Q220 214 244 214"]:
        hashes += _line(path,"accent")
    art += group(hashes + _text(308,35,"BFuse8 filter") +
                 _grid(250,70,["accent","secondary","muted","secondary", "muted","accent","accent","muted",
                               "secondary","accent","muted","accent","accent","muted","secondary","secondary",
                               "muted","accent","secondary","accent"],4,24,9),900)
    art += group(arrow(384,151,436,151) + _text(497,35,"DEFLATE") +
                 _grid(450,104,["muted","secondary","muted","accent"]*4,4,20,5),1900)
    art += group(_text(300,280,"Approximate membership → lossless byte compression",True),2900)
    return art


def _mask_recover():
    membership = [0,1,0,0,1,1,1,0]
    recovered = [a ^ b for a,b in zip(_REFERENCE,membership)]
    tones = ["warn" if i == 5 else ("accent" if b else "muted") for i,b in enumerate(membership)]
    art = group(_text(300,28,"Query the filter and flip reference bits") +
                _text(78,86,"Reference",True) + _cells(175,58,_REFERENCE,39,6))
    art += group(_text(78,151,"Query",True) + _cells(175,123,membership,39,6,tones=tones),900)
    art += group(_text(78,216,"Recovered",True) + _cells(175,188,recovered,39,6,tones=tones),1900)
    art += group(_text(300,257,"Highlighted query: a possible false positive",True) +
                 _text(300,286,"Bayesian aggregation forms the next probabilities",True),2800)
    return art


STORIES = {
    "fedcompress": {
        "overview": "<strong>Compress both directions of federated training.</strong> Clustering makes client uploads compact, but averaging can undo that structure. FedCompress restores it with server-side distillation and adjusts cluster capacity using an unlabeled representation score.",
        "contributions": [
            "<strong>Dual compression:</strong> clustered local training plus server self-compression after aggregation.",
            "<strong>Adaptive capacity:</strong> use embedding effective rank to guide the number of shared weight values.",
            "<strong>Vision and audio evidence:</strong> report communication, model size and device inference separately.",
        ],
        "steps": [
            _scene("Train weights around shared values", "After a local warm-up, clients combine task learning with a clustering penalty. Many weights share a small set of learned centroids, making the upload compact.", _compress_cluster(), "Schematic scattered local weights become groups sharing three centroids after clustering."),
            _scene("Averaging can break compression", "Clients learn different centroids and assignments. Standard averaging can create more distinct values than either client used; compact uploads therefore do not ensure a compact download.", _compress_average(), "Illustrative client vectors with two values each average to a global vector with three distinct values."),
            _scene("Distill a clustered global student", "The aggregated model teaches a clustered student on unlabeled server data. Matching predictions while enforcing clustering restores a compact model for the next download.", _compress_distill(), "An aggregated teacher and clustered student receive unlabeled server data; their output distributions are matched."),
            _scene("Grow capacity when progress stalls", "Clients compute effective rank from unlabeled embeddings. The server combines these scores and monitors their moving average, increasing cluster capacity when progress stalls.", _compress_capacity(), "Unlabeled embeddings yield a representation score; a schematic plateau triggers additional cluster capacity."),
        ],
        "method": [
            {"title": "Learn task and compression together", "text": "Each client minimizes cross-entropy plus a <strong>weight-clustering penalty</strong>. The local warm-up uses β=0 before enabling clustering with β=1.",
             "formula": _math('<msub><mi>L</mi><mi>k</mi></msub><mo>=</mo><msub><mi>L</mi><mi>ce</mi></msub><mo>+</mo><mi>β</mi><msub><mi>L</mi><mi>wc</mi></msub><mo>(</mo><msub><mi>θ</mi><mi>k</mi></msub><mo>,</mo><mi>μ</mi><mo>,</mo><mi>C</mi><mo>)</mo>', "Client loss equals cross entropy plus beta times the weight clustering penalty."),
             "note": "Equation 1, PDF page 3. μ denotes learnable centroids; C is their count."},
            {"title": "Restore clusters after aggregation", "text": "Keep the underlying aggregation rule. Then optimize a clustered student to match the <strong>temperature-scaled teacher outputs</strong> on unlabeled auxiliary data held by the server.",
             "formula": _math('<msub><mi>L</mi><mi>s</mi></msub><mo>=</mo><msub><mi>L</mi><mi>KL</mi></msub><mo>(</mo><msub><mi>p</mi><mi>T</mi></msub><mo>∥</mo><mi>p</mi><mo>)</mo><mo>+</mo><mi>β</mi><msub><mi>L</mi><mi>wc</mi></msub>', "Server loss equals teacher student KL divergence plus beta times the clustering penalty."),
             "note": "Equation 2, PDF page 4, with model arguments abbreviated. The KL term includes the paper’s temperature scaling."},
            {"title": "Measure representation diversity", "text": "Normalize the singular values of local embeddings and compute their <strong>effective rank</strong>. This is an unlabeled proxy for representation quality, not a generalization guarantee.",
             "formula": _math('<mi>E</mi><mo>=</mo><mi>exp</mi><mo>(</mo><mo>−</mo><munder><mo>∑</mo><mi>j</mi></munder><msub><mi>r</mi><mi>j</mi></msub><mi>log</mi><msub><mi>r</mi><mi>j</mi></msub><mo>)</mo>', "Effective rank is the exponential of negative sum of normalized singular values times their logarithms."),
             "note": "Dynamic weight-clustering section, PDF page 4. r is the normalized singular-value spectrum; the implementation description adds a small stability constant."},
            {"title": "Use the score to adjust capacity", "text": "Start with a small cluster count and increase it when score progress stalls. The prose uses a <strong>three-round window and patience</strong>, with an optional maximum cluster budget.",
             "note": "PDF page 4. This describes the intended schedule; Appendix A contains notation differences and is not an independently verified implementation."},
        ],
        "takeaways": [
            "<strong>Compression must survive aggregation.</strong> Restoring the global centroid structure is the central step.",
            "<strong>Communication has an accuracy cost.</strong> Table 1 reports 3.80–5.41× reductions with 0.31–1.88 percentage-point losses.",
            "<strong>The server does extra work.</strong> Self-compression needs auxiliary data and optimization; inference speedups do not establish training-time or energy savings.",
        ],
        "result_titles": ["Savings and accuracy", "Server compression ablation", "Device inference speedup"],
        "result_leads": [
            "<strong>3.80–5.41× less communication</strong> accompanies accuracy losses of 0.31–1.88 percentage points across the five datasets.",
            "Restoring global clusters raises the reported communication reduction from <strong>1.02× to 3.80×</strong> on CIFAR-100, with additional server training.",
            "Relative inference speedups are <strong>1.103–1.152× for float32</strong> and 1.161–1.248× for uint8. Each uses its own same-device, same-model FedAvg reference.",
        ],
        "scope": ["20 clients and 20 rounds; small vision and audio models.", "Two trials without tabulated uncertainty; individual table entries take precedence over inconsistent prose averages."],
    },
    "fedcode": {
        "overview": "<strong>Send the shared values more often than their positions.</strong> FedCode usually exchanges only weight-cluster codebooks. Clients and server map their existing weights to received centers, while periodic transfers of weight indices recalibrate the models.",
        "contributions": [
            "<strong>Codebook exchange:</strong> omit repeated weight-index transmission in ordinary upstream and downstream rounds.",
            "<strong>Nearest-center updates:</strong> reuse stored model structure when receiving codebooks.",
            "<strong>Periodic calibration:</strong> restore weight assignments by occasionally sending centers plus indices.",
        ],
        "steps": [
            _scene("Separate values from positions", "A clustered model contains a codebook of shared values and an index for every weight position. FedCode’s additional saving comes from usually omitting that large index map.", _codebook_parts(), "A weight grid is separated into a small codebook of values and a per-position index map; ordinary FedCode rounds send the codebook."),
            _scene("Map local weights to received centers", "The server sorts and broadcasts its codebook. Each client uses nearest-center binary search to replace local weight values, then trains on its own data.", _codebook_nearest(), "Four local weight values map to their nearest values in a received sorted codebook."),
            _scene("Update the server from client codebooks", "Clients cluster their trained models and return the centers. The server concatenates those codebooks and replaces global weight values by nearby received centers before preparing the next codebook.", _codebook_server(), "Two client codebooks are concatenated; the server uses their centers to update values in the global weight grid."),
            _scene("Recalibrate weight positions periodically", "Clusters and assignments can drift. Calibration rounds therefore carry both codebooks and compressed weight indices. On upstream calibration rounds, the server reconstructs client models and applies FedAvg.", _codebook_calibrate(), "Ordinary codebook rounds reuse local weight positions; periodic calibration sends codebook plus indices to reconstruct model positions."),
        ],
        "method": [
            {"title": "Factor the compressed model", "text": "With P weights, K centers and b bits per center, ordinary clustering still sends <strong>one index per weight</strong>. FedCode targets that repeated index cost.",
             "formula": _math('<mo>|</mo><msup><mi>M</mi><mo>′</mo></msup><mo>|</mo><mo>=</mo><mi>K</mi><mi>b</mi><mo>+</mo><mi>P</mi><mo>⌈</mo><msub><mi>log</mi><mn>2</mn></msub><mi>K</mi><mo>⌉</mo>', "Clustered model bits equal K times b plus P times the ceiling of log base two K."),
             "note": "Equation 3, PDF page 2. b abbreviates the source’s wordlength; this is a representation-size expression."},
            {"title": "Exchange centers in ordinary rounds", "text": "Download a sorted codebook; map each local weight to its nearest center; train locally. One K-means run over the <strong>entire local model</strong> then produces the upload codebook.",
             "note": "Section 4.1 and Algorithm 2, PDF pages 5–6. Downstream mapping is O(P log K); K-means is O(PKI), with I iterations. These are complexity claims, not device timings."},
            {"title": "Aggregate codebooks by remapping", "text": "Concatenate received client codebooks and map each existing global weight to its nearest received center. This operation <strong>changes the ordinary server update</strong>; it does not average complete client tensors.",
             "note": "Section 4.1 and Algorithm 1, PDF page 5. Global weights are clustered again to prepare the next downlink."},
            {"title": "Calibrate each direction periodically", "text": "Send centers plus indices to reconstruct the sender’s clustered model. The server uses <strong>FedAvg after upstream reconstruction</strong>. Calibration frequency controls communication and accuracy together.",
             "note": "Section 4.2, PDF page 5. The v1 preprint assigns F1/F2 to directions inconsistently, so the result panel retains those source labels without relabeling them."},
        ],
        "takeaways": [
            "<strong>Positions can dominate the payload.</strong> Exchanging codebooks between calibration rounds saves more than repeatedly sending a complete clustered model.",
            "<strong>Calibration protects utility.</strong> In the reported sweep, codebooks alone yield 264.7× reduction but lose 46.88 accuracy points.",
            "<strong>Read both directions together.</strong> Joint DTR captures the cost of downloads as well as uploads; it is not a latency or energy measurement.",
        ],
        "result_titles": ["Joint communication savings", "Calibration trade-off", "Partial participation"],
        "result_leads": [
            "FedCode reports <strong>14.6× joint reduction at 58.07% accuracy</strong>. FedZip’s 19.8× upload reduction becomes 1.9× when the download cost is included.",
            "Less frequent calibration saves traffic but can sharply reduce accuracy: <strong>264.7× reduction costs 46.88 percentage points</strong> in the codebook-only setting.",
            "With 10% participation, all four selected comparisons show <strong>larger accuracy losses under non-IID data</strong>. Training budgets and some cluster counts also differ.",
        ],
        "scope": ["Results use the November 2023 arXiv v1 preprint, separately from the IEEE EDGE 2024 publication.", "Ten-client simulations; budgets vary across settings and tables report no uncertainty."],
    },
    "deltamask": {
        "overview": "<strong>Adapt a frozen model by communicating mask changes.</strong> DeltaMask trains stochastic masks over pretrained weights, selects changes to a shared reference mask, and encodes their positions with probabilistic filters. The server approximately reconstructs those masks and updates global mask probabilities.",
        "contributions": [
            "<strong>Mask-based adaptation:</strong> learn subnetworks while keeping pretrained backbone weights fixed.",
            "<strong>Sparse change encoding:</strong> rank differing positions and compress them with a binary fuse filter.",
            "<strong>Controllable trade-off:</strong> vary retained changes and fingerprint width to balance bitrate and accuracy.",
        ],
        "steps": [
            _scene("Learn which pretrained weights to use", "Local training changes mask scores, not pretrained backbone weights. Sampling the mask selects a subnetwork for the task; the experiments mask the last five backbone blocks.", _mask_freeze(), "A frozen weight grid multiplied by a sampled binary mask produces a selected subnetwork."),
            _scene("Find changes to a shared reference", "A publicly shared seed lets every participant sample the same reference binary mask from global probabilities. Compare the trained local sample with that reference and collect the differing positions.", _mask_difference(), "An illustrative shared reference mask and local mask differ at positions two, four, five and seven; only those positions enter the change set."),
            _scene("Keep the most informative changes", "Rank differing positions by KL divergence between local and global mask probabilities. Retain a top-κ subset, controlling how much information enters the transmission.", _mask_rank(), "Four schematic changed positions are ranked by relative entropy; three are retained and one is omitted."),
            _scene("Encode positions as fingerprints", "A four-wise BFuse8 filter stores the selected positions compactly. Its fingerprint array is then losslessly DEFLATE-compressed in a PNG-like representation for upload.", _mask_filter(), "Selected index positions are hashed into a binary fuse fingerprint array, then losslessly compressed for transmission."),
            _scene("Reconstruct, then aggregate masks", "The server queries the filter and flips reference bits at reported positions. Recovery is approximate: ranking omits some changes and membership queries can return false positives. Bayesian aggregation updates the next global probabilities.", _mask_recover(), "Membership queries flip reference bits; an illustrative false positive changes an extra bit before reconstructed masks enter Bayesian aggregation."),
        ],
        "method": [
            {"title": "Optimize a stochastic mask", "text": "Transform unconstrained mask scores with a sigmoid, sample binary activations, and apply them to <strong>fixed pretrained weights</strong>. The classifier first receives one round of linear probing.",
             "formula": _math('<mi>θ</mi><mo>=</mo><mi>sigmoid</mi><mo>(</mo><mi>s</mi><mo>)</mo><mo>,</mo><mspace width="0.5em"/><mi>m</mi><mo>∼</mo><mi>Bern</mi><mo>(</mo><mi>θ</mi><mo>)</mo><mo>,</mo><mspace width="0.5em"/><msup><mi>w</mi><mo>′</mo></msup><mo>=</mo><mi>m</mi><mo>⊙</mo><msub><mi>w</mi><mi>init</mi></msub>', "Mask probabilities are sigmoid of scores; a Bernoulli mask multiplies the fixed initial weights."),
             "note": "Sections III-A–C and Algorithm 1, PDF pages 4–6. The experiments target the last five backbone blocks."},
            {"title": "Form and rank mask differences", "text": "Sample the global reference with a shared seed. Collect positions where local and reference bits disagree, rank them by <strong>relative entropy of their probabilities</strong>, and retain a top-κ subset.",
             "formula": _math('<mi>Δ</mi><mo>=</mo><mo>{</mo><mi>i</mi><mo>:</mo><msub><mi>m</mi><mrow><mi>local</mi><mo>,</mo><mi>i</mi></mrow></msub><mo>≠</mo><msub><mi>m</mi><mrow><mi>ref</mi><mo>,</mo><mi>i</mi></mrow></msub><mo>}</mo>', "The difference set contains positions whose local and reference mask bits disagree."),
             "note": "Section III-B and Equation 4, PDF page 5, with simplified round/client notation. The main setup schedules κ from 0.8."},
            {"title": "Filter first, compress bytes second", "text": "Encode selected positions in a <strong>four-wise binary fuse filter</strong> using 8-bit fingerprints by default. PNG-like DEFLATE compression then shrinks the fingerprint bytes losslessly.",
             "note": "Section III-B, PDF page 5. Selection and probabilistic membership make mask recovery approximate; DEFLATE itself does not discard fingerprint data."},
            {"title": "Recover masks and update probabilities", "text": "Query membership for every possible position, flip the corresponding reference bits, and feed reconstructed client masks to <strong>Bayesian aggregation</strong> for the next round.",
             "formula": _math('<mover><mi>m</mi><mo>^</mo></mover><mo>=</mo><msub><mi>m</mi><mi>ref</mi></msub><mo>⊕</mo><msub><mi>𝟙</mi><mover><msup><mi>Δ</mi><mo>′</mo></msup><mo>^</mo></mover></msub>', "Recovered mask equals reference mask XOR the indicator of positions returned by membership queries."),
             "note": "Equation 5 and Algorithm 1, PDF pages 5–6. False positives can flip extra bits; this is not a lossless-recovery or formal privacy guarantee."},
        ],
        "takeaways": [
            "<strong>Send changes to a shared mask.</strong> The small update set is the key resource exploited by the filter.",
            "<strong>Low bitrate still has an accuracy cost.</strong> The selected eight-task panels report 0.151 and 0.233 bpp, with accuracy below their fine-tuning references.",
            "<strong>Approximation is explicit.</strong> Ranking and filter false positives affect recovery; lossless byte compression does not make the whole pipeline lossless.",
        ],
        "result_titles": ["IID, full participation", "Non-IID, partial participation", "Backbone comparison"],
        "result_leads": [
            "DeltaMask reports <strong>85.44% average accuracy at 0.151 bpp</strong>: 0.63 percentage points below FedPM and 2.64 below the fine-tuning reference.",
            "With 20% participation, DeltaMask reports <strong>81.13% at 0.233 bpp</strong>: 0.51 percentage points below FedPM and 2.06 below fine-tuning.",
            "All five backbones use approximately <strong>0.2–0.25 bpp</strong>. Only CLIP ViT-L/14 exceeds its fine-tuning accuracy in this separate ten-client study.",
        ],
        "scope": ["Accepted IEEE BigData manuscript; image classification across eight datasets and five pretrained backbones.", "The 0.09 bpp headline is a lowest reported setting, not the mean across tasks; fine-tuning targets the same last five blocks."],
    },
}

for _slug, _titles in {
    "fedcompress": ["Cluster weights", "Average models", "Distill and compress", "Adjust capacity"],
    "fedcode": ["Values and positions", "Map local weights", "Combine codebooks", "Recalibrate periodically"],
    "deltamask": ["Learn masks", "Find changes", "Rank changes", "Encode positions", "Recover and aggregate"],
}.items():
    for _step, _short_title in zip(STORIES[_slug]["steps"], _titles):
        _step["short_title"] = _short_title
