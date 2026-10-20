"""Compact, source-bound result panels, rendered without a charting runtime.

Presentation selections live separately from the full paper evidence records.
Reported strings (including uncertainty and missing cells) remain unchanged.
"""
from html import escape as esc
import json
import math
from pathlib import Path
from urllib.parse import urlparse
from xml.etree import ElementTree as ET

from research_visuals import numeric_value

ROOT = Path(__file__).resolve().parents[1]


def emphasis(text):
    root = ET.fromstring('<span>' + text + '</span>')
    if any(e.tag not in {'span', 'strong', 'em', 'sub', 'sup'} or e.attrib for e in root.iter()):
        raise ValueError('Results allow only simple editorial emphasis')
    return text


def selected_result(p, panel):
    index = panel['result_index']
    if not isinstance(index, int) or not 0 <= index < len(p['insight']['results']):
        raise ValueError('Result index outside source evidence')
    result = p['insight']['results'][index]
    indices = panel.get('rows', list(range(len(result['rows']))))
    if not indices or len(set(indices)) != len(indices):
        raise ValueError('Result rows must be a nonempty unique selection')
    if any(not isinstance(i, int) or i < 0 or i >= len(result['rows']) for i in indices):
        raise ValueError('Result row outside source table')
    return {**result, 'rows': [result['rows'][i] for i in indices]}


def load_results(p):
    data = json.loads((ROOT / 'data/results' / (p['slug'] + '.json')).read_text())
    validate_results(p, data)
    return data


def validate_results(p, data):
    if data['slug'] != p['slug'] or not 1 <= len(data['panels']) <= 3:
        raise ValueError('Results must match this paper and contain 1–3 panels')
    if not 2 <= len(data['takeaways']) <= 3 or not data.get('audit', {}).get('sources'):
        raise ValueError('Results require concise takeaways and source audit')
    for text in data['takeaways']:
        emphasis(text)
    for panel in data['panels']:
        if not all(panel.get(k) for k in ('title', 'subtitle', 'source', 'finding')):
            raise ValueError('Result panel needs a heading, setting, source and finding')
        emphasis(panel['finding'])
        source = urlparse(panel['source']['url'])
        if source.scheme != 'https' or not source.hostname or source.hostname in {'localhost', '127.0.0.1'}:
            raise ValueError('Result source must be a public HTTPS URL')
        if panel['kind'] == 'curves':
            from result_curves import validate_curve_groups
            validate_curve_groups(panel['groups'])
            if 'summary_result_index' in panel:
                selected_result(p, {'result_index': panel['summary_result_index']})
        elif panel['kind'] == 'scatter':
            plot = panel['plot']
            for axis in ('x', 'y'):
                spec = plot[axis]
                if not all(math.isfinite(spec[k]) for k in ('min', 'max')) or spec['max'] <= spec['min']:
                    raise ValueError('Invalid scatter axis')
                if spec.get('scale', 'linear') not in {'linear', 'log'}:
                    raise ValueError('Unknown scatter scale')
                if spec.get('scale') == 'log' and spec['min'] <= 0:
                    raise ValueError('Log axes require positive values')
                if any(not math.isfinite(v) or not spec['min'] <= v <= spec['max'] for v in spec.get('ticks', [])):
                    raise ValueError('Scatter ticks must lie within the axis')
                for point in plot['points']:
                    if not math.isfinite(point[axis]) or not spec['min'] <= point[axis] <= spec['max']:
                        raise ValueError('Scatter axis clips an observation')
                    if axis + '_display' in point:
                        printed = str(point[axis + '_display'])
                        number = numeric_value(printed)
                        places = len(printed.partition('.')[2])
                        if number is None or not math.isclose(number, round(point[axis], places), abs_tol=1e-9):
                            raise ValueError('Scatter label disagrees with plotted value')
            if not plot['points'] or len({v['label'] for v in plot['points']}) != len(plot['points']):
                raise ValueError('Scatter observations need unique labels')
        elif panel['kind'] in {'bars', 'table'}:
            result = selected_result(p, panel)
            selections = [c['columns'] for c in panel['charts']] if panel['kind'] == 'bars' else [panel.get('columns', list(range(len(result['columns']) - 1)))]
            for columns in selections:
                if not columns or any(not isinstance(c, int) or c < 0 or c >= len(result['columns']) - 1 for c in columns):
                    raise ValueError('Result column outside source table')
            if panel.get('column_labels') and len(panel['column_labels']) != len(selections[0]) + 1:
                raise ValueError('Table label count must match selected columns')
            if panel['kind'] == 'bars':
                for chart in panel['charts']:
                    bar_chart(result, chart)
        else:
            raise ValueError('Unknown result panel type')


def compact_table(result, columns=None, labels=None):
    columns = columns if columns is not None else list(range(len(result['columns']) - 1))
    headers = labels or [result['columns'][0], *[result['columns'][c + 1] for c in columns]]
    head = ''.join(f'<th scope="col">{esc(h)}</th>' for h in headers)
    rows = []
    for row in result['rows']:
        cells = ''.join(f'<td>{esc(str(row["values"][c]))}</td>' for c in columns)
        own = ' class="rs-own"' if row.get('highlight') else ''
        rows.append(f'<tr{own}><th scope="row">{esc(row["label"])}</th>{cells}</tr>')
    return f'<div class="rs-table-scroll" role="region" aria-label="{esc(result["title"])} table" tabindex="0"><table class="rs-table"><caption class="sr-only">{esc(result["title"])}. {esc(result["context"])}</caption><thead><tr>{head}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>'


def bar_chart(result, spec):
    columns = spec['columns']
    values = [numeric_value(row['values'][c]) for row in result['rows'] for c in columns]
    raw = [str(row['values'][c]).strip() for row in result['rows'] for c in columns]
    if any(v is None and s not in {'—', '–'} for v, s in zip(values, raw)):
        raise ValueError('Bars require explicit numeric observations, not ranges or estimates')
    finite = [v for v in values if v is not None]
    if not finite or any(not math.isfinite(v) for v in finite):
        raise ValueError('Bars require finite observations')
    lower = min(0, math.floor(min(finite)))
    upper = spec.get('maximum')
    if upper is None:
        upper = max(0, math.ceil(max(finite)))
    if not math.isfinite(upper) or upper < 0:
        raise ValueError('Bar maximum must be finite and include zero')
    if upper <= lower:
        upper = lower + 1
    if max(finite) > upper or spec.get('minimum', lower) != lower:
        raise ValueError('Bar axes must include zero and all observations')
    extent = upper - lower
    zero = (0 - lower) / extent * 100
    series = spec.get('series_labels', [result['columns'][c + 1] for c in columns])
    if len(series) != len(columns):
        raise ValueError('Each plotted series needs exactly one label')
    highlighted = spec.get('highlight_series', [])
    if any(not isinstance(j, int) or not 0 <= j < len(columns) for j in highlighted):
        raise ValueError('Highlighted series outside plotted columns')
    def series_class(j):
        if j in highlighted:
            return 'rs-series-own'
        if highlighted and j == 0:
            return 'rs-series-muted'
        return f'rs-series-{j}'
    legend = '<div class="rs-legend">' + ''.join(f'<span class="{series_class(j)}"><i aria-hidden="true"></i>{esc(label)}</span>' for j, label in enumerate(series)) + '</div>' if len(columns) > 1 else ''
    ticks = [lower, (lower + upper) / 2, upper]
    axis = '<div class="rs-bar-axis" aria-hidden="true">' + ''.join(f'<span>{v:g}</span>' for v in ticks) + '</div>'
    rows = []
    for row in result['rows']:
        measures = []
        for j, c in enumerate(columns):
            value = numeric_value(row['values'][c])
            printed = esc(str(row['values'][c]))
            if value is None:
                graphic = '<span class="rs-no-value" aria-hidden="true"></span>'
            else:
                start = (min(0, value) - lower) / extent * 100
                width = abs(value) / extent * 100
                graphic = f'<span class="rs-bar-track" style="--zero:{zero:.5f}%" aria-hidden="true"><span style="left:{start:.5f}%;width:{width:.5f}%"></span></span>'
            measures.append(f'<div class="rs-measure {series_class(j)}">{graphic}<span class="rs-number"><span class="sr-only">{esc(series[j])}: </span>{printed}</span></div>')
        own = ' rs-own' if row.get('highlight') else ''
        rows.append(f'<div class="rs-bar-row{own}"><span class="rs-row-name">{esc(row["label"])}</span><div class="rs-measures">{"".join(measures)}</div></div>')
    direction = {'higher': '↑', 'lower': '↓'}.get(spec.get('direction'), '')
    hint = f'<span class="sr-only"> {"Higher" if direction == "↑" else "Lower"} is better</span>' if direction else ''
    single = ' rs-single-series' if len(columns) == 1 else ''
    return f'<div class="rs-bars{single}"><h4>{esc(spec["title"])} <span class="rs-direction">{direction}{hint}</span></h4>{legend}{axis}<div>{"".join(rows)}</div></div>'


def _number(value):
    return f'{value:g}'


def _ticks(spec):
    if spec.get('ticks'):
        return spec['ticks']
    if spec.get('scale') == 'log':
        ticks = [10 ** n for n in range(math.ceil(math.log10(spec['min'])), math.floor(math.log10(spec['max'])) + 1)]
        return ticks or [spec['min'], spec['max']]
    return [spec['min'] + i * (spec['max'] - spec['min']) / 4 for i in range(5)]


def _position(value, spec):
    transform = math.log10 if spec.get('scale') == 'log' else float
    return (transform(value) - transform(spec['min'])) / (transform(spec['max']) - transform(spec['min']))


def scatter_svg(plot, mobile=False):
    width, height = (350, 310) if mobile else (700, 390)
    left, top, right, bottom = (43, 40, 18, 58) if mobile else (52, 45, 25, 58)
    w, h = width - left - right, height - top - bottom
    x = lambda v: left + _position(v, plot['x']) * w
    y = lambda v: top + h - _position(v, plot['y']) * h
    lines = []
    for v in _ticks(plot['x']):
        lines.append(f'<line x1="{x(v):.3f}" y1="{top}" x2="{x(v):.3f}" y2="{top+h}" class="rs-grid"/><text x="{x(v):.3f}" y="{top+h+22}" text-anchor="middle" class="rs-tick">{_number(v)}</text>')
    for v in _ticks(plot['y']):
        lines.append(f'<line x1="{left}" y1="{y(v):.3f}" x2="{left+w}" y2="{y(v):.3f}" class="rs-grid"/><text x="{left-10}" y="{y(v)+4:.3f}" text-anchor="end" class="rs-tick">{_number(v)}</text>')
    points = []
    for i, point in enumerate(plot['points']):
        px, py = x(point['x']), y(point['y'])
        own = bool(point.get('highlight'))
        cls = 'rs-point-own' if own else f'rs-series-{i % 5 + 1}'
        desc = f'{point["label"]}: {plot["x"]["label"]} {point["x"]:g}; {plot["y"]["label"]} {point["y"]:g}'
        marker = f'<path d="M{px:.3f} {py-7:.3f}l7 7-7 7-7-7Z"/>' if own else f'<circle cx="{px:.3f}" cy="{py:.3f}" r="5.5"/>'
        halo = f'<circle class="rs-point-halo" cx="{px:.3f}" cy="{py:.3f}" r="14"/>' if own else ''
        label = str(i + 1) if mobile else point['label']
        # Mobile points map to the value key; desktop labels name each method.
        dx, dy = point.get('label_offset_mobile' if mobile else 'label_offset', [11, -10])
        anchor = 'start'
        if not mobile and _position(point['x'], plot['x']) > .78:
            dx = -11
            anchor = 'end'
        points.append(f'<g class="rs-point {cls}" data-result-x="{point["x"]}" data-result-y="{point["y"]}"><title>{esc(desc)}</title>{halo}{marker}<text class="rs-point-label" x="{px+dx:.3f}" y="{py+dy:.3f}" text-anchor="{anchor}">{esc(label)}</text></g>')
    suffix = ' · log scale' if plot['x'].get('scale') == 'log' else ''
    x_label = plot['x'].get('short_label', plot['x']['label']) if mobile else plot['x']['label']
    return f'<svg class="rs-scatter-svg rs-scatter-{ "mobile" if mobile else "desktop"}" viewBox="0 0 {width} {height}" aria-hidden="true"><text x="{left}" y="18" class="rs-axis-title">{esc(plot["y"]["label"])} ↑</text>{"".join(lines)}<path class="rs-axis" d="M{left} {top}V{top+h}H{left+w}"/>{"".join(points)}<text x="{left+w/2}" y="{height-8}" text-anchor="middle" class="rs-axis-title">{esc(x_label + suffix)} →</text></svg>'


def scatter_plot(panel):
    plot = panel['plot']
    rows = []
    for i, point in enumerate(plot['points']):
        own = ' rs-own' if point.get('highlight') else ''
        series = 'rs-point-own' if point.get('highlight') else f'rs-series-{i % 5 + 1}'
        x_value = str(point.get('x_display', f'{point["x"]:g}'))
        y_value = str(point.get('y_display', f'{point["y"]:.2f}'))
        rows.append(f'<tr class="{series}{own}"><th scope="row"><span class="rs-point-key" aria-hidden="true">{i+1}</span>{esc(point["label"])}</th><td>{esc(y_value)}</td><td>{esc(x_value)}</td></tr>')
    table = f'<table class="rs-table rs-scatter-key"><caption class="sr-only">{esc(panel["title"])}. {esc(plot["y"]["label"])} and {esc(plot["x"]["label"])}.</caption><thead><tr><th scope="col">Method</th><th scope="col">{esc(plot["y"].get("table_label", "Accuracy (%)"))}</th><th scope="col">{esc(plot["x"].get("table_label", "Cost"))}</th></tr></thead><tbody>{"".join(rows)}</tbody></table>'
    return f'<div class="rs-scatter-layout"><div class="rs-scatter">{scatter_svg(plot)}{scatter_svg(plot, True)}</div><div class="rs-scatter-summary">{table}</div></div>'


def results_markup(p):
    data = load_results(p)
    blocks = []
    for i, panel in enumerate(data['panels']):
        if panel['kind'] == 'curves':
            from result_curves import curve_groups
            content = curve_groups(panel, f'{p["slug"]}-metric-{i}')
            if 'summary_result_index' in panel:
                summary = selected_result(p, {'result_index': panel['summary_result_index']})
                content += f'<h4 class="rs-summary-title">{esc(summary["title"])}</h4>' + compact_table(summary)
        elif panel['kind'] == 'scatter':
            content = scatter_plot(panel)
        else:
            result = selected_result(p, panel)
            if panel['kind'] == 'bars':
                charts = ''.join(bar_chart(result, chart) for chart in panel['charts'])
                content = f'<div class="rs-chart-grid" style="--chart-count:{len(panel["charts"])}">{charts}</div>'
            else:
                content = compact_table(result, panel.get('columns'), panel.get('column_labels'))
        source = panel['source']
        link_label = source.get('link_label', 'Paper')
        blocks.append(f'<article class="rs-card rs-kind-{panel["kind"]}" aria-labelledby="result-{i}-title"><header class="rs-card-heading"><div><h3 id="result-{i}-title">{esc(panel["title"])}</h3><p>{esc(panel["subtitle"])}</p></div></header>{content}<footer class="rs-card-footer"><p>{emphasis(panel["finding"])}</p><a href="{esc(source["url"])}" title="{esc(source["label"])}" aria-label="Source: {esc(source["label"])}">{esc(link_label)} ↗</a></footer></article>')
    takeaways = ''.join(f'<li>{emphasis(text)}</li>' for text in data['takeaways'])
    return f'<section id="findings" data-tab-panel class="results-panel" aria-labelledby="results-title"><header class="rs-heading"><span>Evaluation</span><h2 id="results-title">Results</h2></header>{"".join(blocks)}<aside class="rs-takeaways"><h3>Takeaways</h3><ul>{takeaways}</ul></aside></section>'
