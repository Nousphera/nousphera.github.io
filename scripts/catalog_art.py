"""Original, theme-aware thumbnail art for the public paper catalog.

Each scene summarizes the audited method in data/projects and scripts/stories.
Positions, masks, waveforms and weights are schematic, not measured results.
No definitions or element IDs are needed, so all scenes can coexist inline.
"""

from html import escape
from math import atan2, degrees


def _color(tone):
    return f"var(--tile-{tone})"


def _label(x, text, y=155):
    return (f'<text x="{x}" y="{y}" text-anchor="middle" '
            'fill="currentColor" font-family="inherit" font-size="18" '
            f'font-weight="600" letter-spacing="-.2">{escape(text)}</text>')


def _path(d, tone="accent", width=2, dash=False, opacity=1):
    return (f'<path d="{d}" fill="none" stroke="{_color(tone)}" '
            f'stroke-width="{width}" stroke-linecap="round" '
            f'stroke-linejoin="round" opacity="{opacity}"'
            + (' stroke-dasharray="4 5"' if dash else '') + '/>')


def _box(x, y, width, height, tone="line", fill="surface", radius=9):
    return (f'<rect x="{x}" y="{y}" width="{width}" height="{height}" '
            f'rx="{radius}" fill="{_color(fill)}" '
            f'stroke="{_color(tone)}" stroke-width="1.6"/>')


def _dot(x, y, radius=5, tone="accent", hollow=False, opacity=1):
    return (f'<circle cx="{x}" cy="{y}" r="{radius}" '
            f'fill="{_color("surface" if hollow else tone)}" '
            f'stroke="{_color(tone)}" stroke-width="2" opacity="{opacity}"/>')


def _arrow(x1, y1, x2, y2, tone="accent", curve=None, angle=None):
    path = curve or f"M{x1} {y1} L{x2} {y2}"
    rotation = degrees(atan2(y2 - y1, x2 - x1)) if angle is None else angle
    return (_path(path, "line", 2)
            + f'<path class="ca-flow" d="{path}" fill="none" '
              f'stroke="{_color(tone)}" stroke-width="2.4" '
              'stroke-dasharray="4 7" stroke-linecap="round"/>'
            + _path("M-6 -4 L0 0 L-6 4", tone, 2.4).replace(
                '<path ', f'<path transform="translate({x2} {y2}) rotate({rotation})" ', 1))


def _pulse(content):
    return f'<g class="ca-pulse">{content}</g>'


def _grid(x, y, tones, cols=3, size=19, gap=5):
    return ''.join(
        _box(x + (i % cols) * (size + gap),
             y + (i // cols) * (size + gap), size, size,
             tone="line" if tone == "soft" else tone, fill=tone, radius=4)
        for i, tone in enumerate(tones))


def _wave(x, y, heights, tone="accent", step=9, width=3):
    return ''.join(_path(f"M{x + i * step} {y - h / 2} v{h}", tone, width)
                   for i, h in enumerate(heights))


def _lock(x, y, width=26, tone="accent"):
    return (_path(f"M{x + 5} {y + 14} v-7 a{width / 2 - 5} {width / 2 - 5} "
                  f"0 0 1 {width - 10} 0 v7", tone, 2.4)
            + _box(x, y + 14, width, 23, tone, "surface", 5)
            + _path(f"M{x + width / 2} {y + 23} v6", tone, 2.4))


def _network(x, y, width=54, height=56, tone="accent"):
    points = [(x, y), (x, y + height), (x + width / 2, y + height / 2),
              (x + width, y), (x + width, y + height)]
    art = _path(f"M{x} {y} L{x + width} {y + height} "
                f"M{x} {y + height} L{x + width} {y} "
                f"M{x} {y} V{y + height} M{x + width} {y} V{y + height}",
                "line", 1.8)
    return art + ''.join(_dot(px, py, 6, tone, hollow=i != 2)
                         for i, (px, py) in enumerate(points))


def _ae_psl():
    # The narrowing/widening shapes are the encoder and decoder; the middle
    # represents the compact patch-token exchange, not an accuracy metric.
    encoder = ('<path d="M42 42 L139 66 V111 L42 135 Z" '
               f'fill="{_color("soft")}" stroke="{_color("accent")}" stroke-width="2"/>')
    decoder = ('<path d="M261 66 L358 42 V135 L261 111 Z" '
               f'fill="{_color("soft")}" stroke="{_color("secondary")}" stroke-width="2"/>')
    for start, end in [(55, 76), (76, 84), (101, 94), (122, 102)]:
        encoder += _path(f"M53 {start} Q99 {start} 127 {end}", "accent", 1.8, opacity=.62)
        decoder += _path(f"M273 {end} Q315 {start} 347 {start}", "secondary", 1.8, opacity=.62)
    latents = ''.join(_box(177 + i * 17, 74, 12, 30, "accent", "accent", 4)
                      for i in range(3))
    return (encoder + decoder + _arrow(147, 89, 167, 89)
            + _pulse(latents) + _arrow(232, 89, 252, 89, "secondary")
            + _label(89, "Encode") + _label(200, "Compress") + _label(310, "Decode"))


def _mpsl():
    # Image and text are one example of the paired modalities in the paper.
    client = _box(31, 31, 119, 99)
    client += _box(43, 43, 42, 35, "accent", "soft", 5)
    client += _dot(72, 52, 3, "secondary")
    client += _path("M48 70 L58 59 L67 67 L73 62 L80 70", "accent")
    client += _path("M98 49 H135 M98 59 H128 M98 69 H132", "secondary", 3)
    client += ''.join(_box(47 + i * 22, 94, 14, 18, "accent" if i < 2 else "secondary",
                           "accent" if i < 2 else "secondary", 3) for i in range(4))
    server = (_box(265, 43, 96, 75, "line", "soft")
              + _box(258, 49, 96, 75, "secondary", "surface")
              + _network(278, 65, 55, 41))
    return (client + _path("M202 25 V132", "muted", 1.5, True)
            + _arrow(157, 66, 249, 66) + _arrow(157, 107, 249, 107, "secondary")
            + _pulse(server) + _label(90, "Paired inputs") + _label(202, "Split")
            + _label(309, "Shared model"))


def _matu():
    vectors = (_path("M46 126 H165 M57 129 V39", "line", 1.5)
               + _arrow(61, 118, 98, 43, "accent")
               + _arrow(61, 118, 151, 68, "secondary")
               + _arrow(61, 118, 164, 111, "muted") + _dot(61, 118, 5))
    unified = (_path("M257 126 H356 M265 129 V39", "line", 1.5)
               + _arrow(269, 118, 340, 43, "accent") + _dot(269, 118, 5)
               + _grid(304, 106, ["accent", "soft", "secondary"], 3, 12, 6))
    return (vectors + _arrow(184, 83, 235, 83) + _pulse(unified)
            + _label(111, "Task vectors") + _label(306, "Unified update"))


def _deltamask():
    local = [1, 0, 1, 0, 1, 1, 1, 0, 1]
    reference = [1, 1, 1, 0, 1, 0, 1, 0, 0]
    changed = [a != b for a, b in zip(local, reference)]
    def mask(x, values, tone):
        return _grid(x, 49, [tone if v else "soft" for v in values], size=19, gap=6)
    return (mask(35, local, "accent") + _path("M123 83 H137", "muted", 3)
            + mask(166, reference, "secondary") + _arrow(253, 83, 279, 83)
            + _pulse(mask(297, changed, "accent"))
            + _label(70, "Local mask") + _label(201, "Reference") + _label(331, "Changes"))


def _fedcompress():
    clusters = ''
    for x, tone, ys in [(51, "accent", (51, 79, 107)),
                         (89, "secondary", (65, 93, 121))]:
        clusters += _path(f"M{x} 39 V128", tone, 1.5, True, .6)
        clusters += ''.join(_dot(x, y, 8, tone) for y in ys)
    teacher = _network(174, 53, 54, 60, "secondary")
    student = _grid(294, 63, ["accent", "accent", "secondary", "secondary", "accent", "secondary"],
                    cols=3, size=18, gap=6)
    # Different model sizes signal a compressed student; no numeric ratio.
    student += _path("M300 122 H352", "accent", 2)
    return (clusters + _arrow(117, 82, 155, 82) + teacher
            + _arrow(246, 82, 280, 82, "secondary") + _pulse(student)
            + _label(70, "Cluster") + _label(201, "Teacher") + _label(327, "Student"))


def _fedcode():
    pattern = ["accent", "secondary", "accent", "muted", "secondary", "muted",
               "accent", "accent", "secondary"]
    weights = _grid(36, 49, pattern, size=19, gap=5)
    codebook = ''.join(_box(169, y - 11, 56, 23, "line", "surface", 6)
                       + _dot(182, y, 5, tone) + _path(f"M195 {y} h18", tone, 3)
                       for y, tone in [(52, "accent"), (84, "secondary"), (116, "muted")])
    index = _grid(296, 49, ["soft"] * 9, size=19, gap=5)
    index += ''.join(_dot(305.5 + (i % 3) * 24, 58.5 + (i // 3) * 24, 3, tone)
                     for i, tone in enumerate(pattern))
    return (weights + _arrow(119, 83, 153, 83) + _pulse(codebook)
            + _path("M240 70 V98 M232 84 H248", "muted", 2)
            + index + _label(70, "Weights") + _label(198, "Codebook") + _label(329, "Index map"))


def _fedln():
    # These are three alternative interventions, not a sequential pipeline.
    badges = ''.join(_box(x, 31, 104, 98, "line", "soft", 16)
                      for x in (24, 148, 272))
    correct = _path("M49 59 H77 L104 86 L79 111 L49 81 Z", "accent", 2.5)
    correct += _dot(61, 69, 3, "accent", True)
    correct += _path("M72 85 L80 93 L94 76", "accent", 3)
    guide = _path("M171 59 L200 45 L229 59 L200 73 Z M181 68 V78 Q200 91 219 78 V68", "secondary", 2.5)
    guide += _path("M200 91 V105 M186 112 L200 105 L214 112", "accent", 2.5)
    guide += ''.join(_dot(x, 113, 4) for x in (184, 200, 216))
    weight = ''.join(_box(x, 100 - h, 12, h, tone, tone, 3)
                     for x, h, tone in [(292, 34, "accent"), (316, 16, "muted"), (340, 47, "secondary")])
    weight += _path("M291 111 H353", "line", 2)
    return (badges + _pulse(correct) + guide + weight
            + _label(76, "Correct") + _label(200, "Guide") + _label(324, "Weight"))


def _fedstar():
    clips = _box(29, 34, 112, 41) + _box(29, 95, 112, 41)
    clips += _wave(42, 54, [9, 20, 12, 28, 17, 8], step=10)
    clips += _wave(42, 115, [12, 27, 17, 9, 24, 12], "secondary", 10)
    clips += _dot(119, 54, 11, "accent", True)
    clips += _path("M113 54 L117 58 L125 49", "accent", 2.4)
    clips += _dot(119, 115, 11, "secondary", True)
    clips += _path("M115 115 H123", "secondary", 2)
    model = _box(249, 51, 80, 71, "accent", "surface", 12) + _network(264, 68, 49, 37)
    loop = _arrow(331, 61, 333, 111, "secondary",
                  curve="M331 61 C372 38 375 130 333 111", angle=205)
    return (clips + _arrow(151, 54, 237, 77) + _arrow(151, 115, 237, 96, "secondary")
            + _pulse(model) + loop
            + _label(85, "Labeled", 25) + _label(85, "Unlabeled", 162)
            + _label(290, "Self-train"))


def _fedser():
    speech = _wave(36, 85, [16, 32, 54, 26, 67, 37, 18, 43, 24], step=10, width=4)
    spectrum = _box(227, 37, 131, 94, "line", "soft", 10)
    spectrum += _box(221, 43, 131, 94, "line", "surface", 10)
    for row in range(4):
        for col in range(7):
            focused = col in (2, 3, 4) and row in (1, 2)
            spectrum += (f'<rect x="{231 + col * 16}" y="{55 + row * 18}" '
                         f'width="10" height="12" rx="3" fill="{_color("accent" if focused else "secondary")}" '
                         f'opacity="{1 if focused else .24 + ((row + col) % 3) * .12}"/>')
    attention = _path("M261 31 V25 H307 V31 M363 69 H369 V108 H363", "accent", 2)
    return (speech + _arrow(139, 85, 201, 85) + _pulse(spectrum) + attention
            + _label(78, "Speech") + _label(291, "Attention"))


def _plix():
    supports = ''
    for y, tone in [(57, "accent"), (112, "secondary")]:
        supports += ''.join(_dot(x, y + dy, 5, tone)
                            for x, dy in [(43, -8), (68, 4), (91, -10), (108, 8)])
    means = ''.join(_dot(219, y, 13, tone, True) + _dot(219, y, 4, tone)
                    for y, tone in [(57, "accent"), (112, "secondary")])
    query = (f'<path d="M330 42 L343 55 L330 68 L317 55 Z" '
             f'fill="{_color("soft")}" stroke="{_color("accent")}" stroke-width="2.4"/>')
    return (supports + _arrow(128, 57, 194, 57) + _arrow(128, 112, 194, 112, "secondary")
            + _pulse(means) + _path("M316 66 L237 110", "line", 1.5, True)
            + _arrow(307, 55, 244, 57) + query
            + _label(76, "Supports") + _label(219, "Prototypes") + _label(330, "Query"))


def _da_mldg():
    train = _box(29, 42, 123, 87, "accent", "soft", 13)
    train += _wave(44, 84, [12, 23, 42, 57, 28, 15, 22, 9], "accent", 12)
    test = _box(248, 42, 123, 87, "secondary", "soft", 13)
    test += _wave(264, 84, [27, 12, 18, 33, 13, 53, 37, 20], "secondary", 12)
    shift = _dot(200, 85, 23, "accent", True)
    # A drawn delta marks the domain-shift estimate without adding small text.
    shift += _path("M200 71 L189 96 H211 Z", "accent", 2.4)
    return (train + test + _arrow(155, 85, 173, 85) + _pulse(shift)
            + _arrow(227, 85, 245, 85, "secondary")
            + _path("M153 39 Q200 15 247 39", "line", 1.5, True)
            + _label(90, "Meta-train") + _label(200, "Shift") + _label(310, "Meta-test"))


def _enccluster():
    centroids = _box(39, 46, 73, 84, "accent", "surface", 12)
    centroids += _lock(62, 19)
    centroids += ''.join(_dot(x, y, 7, tone)
                         for x, y, tone in [(61, 78, "accent"), (90, 88, "secondary"), (65, 111, "muted")])
    mapping = _grid(169, 52, ["accent", "secondary", "soft", "soft", "accent", "muted",
                             "secondary", "soft", "accent"], size=17, gap=6)
    aggregate = _box(286, 49, 76, 79, "secondary", "surface", 13)
    aggregate += _path("M342 65 H307 L326 88 L307 111 H342", "secondary", 3)
    return (centroids + _arrow(121, 87, 155, 87) + mapping
            + _arrow(241, 87, 273, 87, "secondary") + _pulse(aggregate)
            + _label(76, "Centroids") + _label(201, "Mapping") + _label(324, "Aggregate"))


def _efu():
    updates = _dot(75, 58, 24, "accent", True) + _dot(75, 117, 24, "secondary", True)
    updates += _path("M65 58 H85 M75 48 V68", "accent", 3)
    updates += _path("M65 117 H85", "secondary", 3)
    aggregate = _box(248, 54, 104, 77, "accent", "surface", 13)
    aggregate += _path("M278 54 V43 a22 22 0 0 1 44 0 V54", "accent", 2.6)
    aggregate += _path("M317 72 H282 L300 94 L282 115 H317", "accent", 3)
    return (updates + _arrow(112, 58, 235, 78) + _arrow(112, 117, 235, 103, "secondary")
            + _pulse(aggregate) + _label(75, "Learn", 25) + _label(75, "Unlearn", 166)
            + _label(300, "One aggregate"))


def _fiba():
    picture = _box(32, 42, 131, 90, "line", "surface", 12)
    picture += _dot(132, 63, 9, "secondary", True)
    picture += (f'<path d="M41 119 L79 74 L109 103 L126 85 L154 119 Z" '
                f'fill="{_color("soft")}" stroke="{_color("line")}" stroke-width="1.6"/>')
    picture += _grid(132, 107, ["soft", "secondary", "secondary", "soft"], 2, 6, 2)
    callout = _path("M153 114 L213 93 M148 106 L213 66", "line", 1.5)
    trigger = _dot(247, 78, 33, "secondary", True)
    pattern = ["soft", "accent", "secondary", "soft", "secondary", "soft", "accent", "secondary",
               "accent", "secondary", "soft", "accent", "soft", "accent", "secondary", "soft"]
    trigger += _grid(227, 58, pattern, 4, 7, 4)
    target = _dot(344, 78, 25, "accent", True) + _dot(344, 78, 13, "accent", True)
    target += _dot(344, 78, 4) + _path("M344 45 V52 M344 104 V111 M311 78 H318 M370 78 H377", "accent", 2)
    return (picture + callout + _pulse(trigger) + _arrow(287, 78, 308, 78)
            + target + _label(98, "Input") + _label(247, "Trigger") + _label(344, "Target"))


def _sdapt():
    client = _box(25, 40, 90, 90)
    client += _path("M38 61 L51 49 L65 62 L78 54 L102 76", "accent")
    client += _grid(41, 91, ["accent", "soft", "secondary"], 3, 14, 6)
    shared = _box(170, 40, 90, 90, "accent", "soft")
    shared += _network(188, 58, 54, 52)
    head = _box(316, 54, 57, 62, "secondary", "surface")
    head += _path("M328 73 H359 M328 86 H352 M328 99 H355", "secondary", 2.4)
    return (client + _arrow(121, 82, 161, 82) + _pulse(shared)
            + _arrow(268, 82, 308, 82, "secondary") + head
            + _label(70, "Local views") + _label(215, "Adapt")
            + _label(344, "Task heads"))


_SCENES = {
    "sdapt": _sdapt,
    "ae-psl": _ae_psl,
    "mpsl": _mpsl,
    "matu": _matu,
    "deltamask": _deltamask,
    "fedcompress": _fedcompress,
    "fedcode": _fedcode,
    "fedln": _fedln,
    "fedstar": _fedstar,
    "fedser": _fedser,
    "plix": _plix,
    "da-mldg": _da_mldg,
    "enccluster": _enccluster,
    "efu": _efu,
    "fiba": _fiba,
}


def thumbnail(slug):
    """Return a decorative inline SVG; reject unknown or untrusted slugs."""
    try:
        scene = _SCENES[slug]
    except (KeyError, TypeError) as exc:
        raise ValueError(f"Unknown paper thumbnail: {slug!r}") from exc
    return ('<svg class="catalog-art" viewBox="0 0 400 180" '
            'aria-hidden="true" focusable="false" xmlns="http://www.w3.org/2000/svg">'
            + scene() + '</svg>')
