"""Small multiples from exact checkpoints; no smoothing or extrapolation."""
from html import escape as esc
import math


def validate_curve_groups(groups):
    if not groups or len(groups) > 3:
        raise ValueError('Expected one to three metric groups')
    labels = [group['label'] for group in groups]
    if len(set(labels)) != len(labels):
        raise ValueError('Metric groups must have unique labels')
    for group in groups:
        if not 1 <= len(group['charts']) <= 3:
            raise ValueError('Expected one to three dataset panels')
        for chart in group['charts']:
            if not chart.get('title') or not chart.get('series'):
                raise ValueError('A curve needs a dataset and observations')
            for axis in ('x', 'y'):
                spec = chart[axis]
                if not spec.get('label') or not all(math.isfinite(spec[k]) for k in ('min', 'max')) or spec['max'] <= spec['min']:
                    raise ValueError('Invalid curve axis')
                if spec.get('scale', 'linear') not in ('linear', 'log') or spec.get('scale') == 'log' and spec['min'] <= 0:
                    raise ValueError('Invalid logarithmic curve axis')
                if any(not math.isfinite(v) or not spec['min'] <= v <= spec['max'] for v in spec['ticks']):
                    raise ValueError('Curve ticks outside axis')
            if len({s['label'] for s in chart['series']}) != len(chart['series']):
                raise ValueError('Method labels must be unique')
            for series in chart['series']:
                if series.get('tone', 'muted') not in {'muted', 'purple', 'orange', 'accent'}:
                    raise ValueError('Unsupported method color')
                points = series['points']
                if not points or any(len(point) != 2 for point in points):
                    raise ValueError('Expected x/y checkpoints')
                for x, y in points:
                    if not all(math.isfinite(v) and chart[a]['min'] <= v <= chart[a]['max'] for a, v in [('x', x), ('y', y)]):
                        raise ValueError('Curve axis clips an observation')
                if any(a[0] >= b[0] for a, b in zip(points, points[1:])):
                    raise ValueError('Checkpoint costs must increase strictly')


def _class(series, index):
    if series.get('highlight'):
        return 'rs-curve-own'
    if series.get('tone'):
        return 'rs-curve-' + series['tone']
    return f'rs-curve-series-{index}'


def curve_svg(chart):
    from paper_results import _position
    left, top, width, height = 44, 30, 272, 172
    x = lambda value: left + width * _position(value, chart['x'])
    y = lambda value: top + height - height * _position(value, chart['y'])
    desc = '; '.join(s['label'] + ': ' + ', '.join(f'{a:g}, {b:g}' for a, b in s['points']) for s in chart['series'])
    grid = []
    for value in chart['x']['ticks']:
        grid.append(f'<line class="rs-grid" x1="{x(value):.3f}" y1="{top}" x2="{x(value):.3f}" y2="{top+height}"/><text class="rs-tick" x="{x(value):.3f}" y="{top+height+21}" text-anchor="middle">{value:g}</text>')
    for value in chart['y']['ticks']:
        grid.append(f'<line class="rs-grid" x1="{left}" y1="{y(value):.3f}" x2="{left+width}" y2="{y(value):.3f}"/><text class="rs-tick" x="{left-9}" y="{y(value)+4:.3f}" text-anchor="end">{value:g}</text>')
    curves = []
    for index, series in enumerate(chart['series']):
        points = ' '.join(f'{x(a):.3f},{y(b):.3f}' for a, b in series['points'])
        markers = []
        for a, b in series['points']:
            px, py = x(a), y(b)
            if series.get('highlight'):
                shape = f'<path d="M{px:.3f} {py-4:.3f}l4 4-4 4-4-4Z"/>'
            elif index % 2:
                shape = f'<rect x="{px-3:.3f}" y="{py-3:.3f}" width="6" height="6" rx=".5"/>'
            else:
                shape = f'<circle cx="{px:.3f}" cy="{py:.3f}" r="3"/>'
            markers.append(f'<g data-result-x="{a}" data-result-y="{b}"><title>{esc(series["label"])} · {a:g}, {b:g}</title>{shape}</g>')
        curves.append(f'<g class="rs-curve {_class(series, index)}"><polyline points="{points}"/>{"".join(markers)}</g>')
    suffix = ' · log scale' if chart['x'].get('scale') == 'log' else ''
    return f'<svg class="rs-curve-svg" viewBox="0 0 340 260" role="img" aria-label="{esc(chart["title"] + ": " + chart["y"]["label"] + " by " + chart["x"]["label"])}"><desc>{esc(desc)}</desc><text class="rs-axis-title" x="{left}" y="15">{esc(chart["y"]["label"])} ↑</text>{"".join(grid)}<path class="rs-axis" d="M{left} {top}V{top+height}H{left+width}"/>{"".join(curves)}<text class="rs-axis-title" x="{left+width/2}" y="247" text-anchor="middle">{esc(chart["x"]["label"] + suffix)}</text></svg>'


def curve_groups(panel, key):
    groups = panel['groups']
    validate_curve_groups(groups)
    default = panel.get('default_group', 0)
    if not isinstance(default, int) or not 0 <= default < len(groups):
        raise ValueError('Invalid default metric group')
    controls = ''
    if len(groups) > 1:
        choices = ''.join(f'<span><input type="radio" name="{key}" id="{key}-choice-{i}"{" checked" if i == default else ""}><label for="{key}-choice-{i}">{esc(g["label"])}</label></span>' for i, g in enumerate(groups))
        controls = f'<fieldset class="rs-metric-controls"><legend class="sr-only">Compare adaptation budgets</legend>{choices}</fieldset>'
    series = groups[0]['charts'][0]['series']
    legend = '<div class="rs-curve-legend">' + ''.join(f'<span class="{_class(s, i)}"><i aria-hidden="true"></i>{esc(s["label"])}</span>' for i, s in enumerate(series)) + '</div>'
    panels = []
    for i, group in enumerate(groups):
        charts = ''.join(f'<div class="rs-curve-chart"><h4>{esc(chart["title"])}</h4>{curve_svg(chart)}</div>' for chart in group['charts'])
        panels.append(f'<div class="rs-curve-group" data-metric="{i}" role="group" aria-label="{esc(group["label"])}">{charts}</div>')
    return f'<div class="rs-curves">{controls}{legend}{"".join(panels)}</div>'
