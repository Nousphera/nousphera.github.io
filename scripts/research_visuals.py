"""Accessible, theme-aware visual explanations and source-bound evidence panels."""
from html import escape as esc
import math
import re
from research_icons import research_icon, ICONS

NUMBER = re.compile(r'^\s*([+−-]?\d+(?:\.\d+)?)(?:\s*(?:±|\+/-)\s*\d+(?:\.\d+)?)?\s*(?:%|×|x)?\s*$')

def numeric_value(cell):
    match = NUMBER.fullmatch(str(cell))
    return float(match.group(1).replace('−','-')) if match else None

def validate_insight(d, public_url):
    for key in ('slug','problem','contribution','reading_guide','diagram','results','evaluation','limitations','takeaways','evidence_inventory'):
        if not d.get(key): raise ValueError(f'{d.get("slug")}: missing insight {key}')
    diagram = d['diagram']
    if diagram.get('type') not in ('pipeline','cycle','comparison','alternatives'):
        raise ValueError('Unknown method topology')
    if not 2 <= len(diagram.get('stages',[])) <= 6:
        raise ValueError('Method requires 2-6 readable stages')
    for node in diagram['stages']:
        if node.get('icon') not in ICONS or not all(node.get(k) for k in ('title','detail','location')):
            raise ValueError('Diagram node needs known icon, title, detail and location')
    connections = diagram.get('connections',[])
    if connections and diagram['type'] in ('pipeline','cycle') and len(connections) != len(diagram['stages'])-1:
        raise ValueError('Diagram connections must match stage boundaries')
    public_url(d['evidence_inventory']['source_url'])
    for result in d['results']:
        for key in ('title','question','context','source','columns','rows','interpretation','caveat'):
            if not result.get(key): raise ValueError(f'Result is missing {key}')
        public_url(result['source']['url'])
        for row in result['rows']:
            if len(row['values']) != len(result['columns'])-1:
                raise ValueError('Result row has wrong column count')
        chart = result.get('chart')
        if chart:
            col = chart['column']
            if not isinstance(col,int) or col < 0 or col >= len(result['columns'])-1:
                raise ValueError('Chart column outside result values')
            values = [numeric_value(r['values'][col]) for r in result['rows']]
            if any(v is None or not math.isfinite(v) for v in values):
                raise ValueError('Chart values must be explicit numeric observations')
            lo, hi = chart.get('min',0), chart['max']
            if lo != 0 or hi <= 0 or any(v < 0 or v > hi for v in values):
                raise ValueError('Bar charts require a zero baseline and a range containing all observations')

def diagram_markup(d, slug, compact=False):
    typ = d['type']
    nodes = []
    for index,s in enumerate(d['stages']):
        items = ''.join(f'<span>{esc(item)}</span>' for item in s.get('items',[]))
        relation = d.get('connections',[])[index-1] if index and len(d.get('connections',[])) >= index else ''
        connector = f'<span class="diagram-connector" aria-hidden="true"><span>{esc(relation)}</span><svg viewBox="0 0 24 24"><path d="M3 12h18m-5-5 5 5-5 5"/></svg></span>' if index and typ in ('pipeline','cycle') else ''
        nodes.append(f'''<li class="diagram-stage">{connector}<span class="stage-context">{esc(s['location'])}</span><span class="stage-symbol">{research_icon(s['icon'])}</span><div class="stage-copy"><h3>{esc(s['title'])}</h3><p>{esc(s['detail'])}</p></div>{f'<div class="stage-items">{items}</div>' if items else ''}</li>''')
    if compact:
        symbols = ''.join(f'<span>{research_icon(s["icon"])}<small>{esc(s["title"])}</small></span>' for s in d['stages'])
        return f'<div class="mini-diagram mini-{typ}" aria-hidden="true">{symbols}</div>'
    title_id = f'{slug}-diagram-title'
    desc_id = f'{slug}-diagram-description'
    type_label = {'pipeline':'Training flow','cycle':'Collaborative cycle','comparison':'Method comparison','alternatives':'Alternative approaches'}[typ]
    channels = ''.join(f'<span><b>{i:02d} → {i+1:02d}</b>{esc(c)}</span>' for i,c in enumerate(d.get('connections',[]),1))
    channels = f'<div class="diagram-channels" aria-label="Connections between stages">{channels}</div>' if channels and typ in ('pipeline','cycle') else ''
    return f'''<figure id="{slug}-visual-overview" class="method-diagram diagram-{typ}" aria-labelledby="{title_id}" aria-describedby="{desc_id}"><div class="diagram-heading"><span class="diagram-type">{type_label}</span><h2 id="{title_id}">{esc(d['title'])}</h2><p id="{desc_id}">{esc(d['description'])}</p></div><ol class="diagram-stages" style="--stage-count:{len(nodes)}">{''.join(nodes)}</ol>{channels}<figcaption>{research_icon('book')}<span>{esc(d['footnote'])}</span></figcaption></figure>'''

def chart_markup(result):
    chart = result.get('chart')
    if not chart: return ''
    rows = []
    for r in result['rows']:
        val = numeric_value(r['values'][chart['column']])
        width = 100*val/chart['max']
        rows.append(f'<div class="bar-row {"is-highlight" if r.get("highlight") else ""}"><div class="bar-label"><span>{esc(r["label"])}</span><strong>{esc(str(r["values"][chart["column"]]))}</strong></div><div class="bar-track"><span style="--bar-width:{width:.4f}%"></span></div></div>')
    uncertainty = any('±' in str(r['values'][chart['column']]) or '+/-' in str(r['values'][chart['column']]) for r in result['rows'])
    description = chart['metric'] + '. ' + '; '.join(r['label'] + ': ' + str(r['values'][chart['column']]) for r in result['rows']) + '.'
    return f'''<div class="result-chart" role="img" aria-label="{esc(description)}"><div class="chart-heading"><strong>{esc(chart['metric'])}</strong><span>{'Higher' if chart.get('higher_is_better',True) else 'Lower'} is better</span></div>{''.join(rows)}<div class="chart-scale"><span>0</span><span>{esc(str(chart['max']))}</span></div>{'<p class="chart-note">Bars show central values; reported uncertainty is preserved in the labels.</p>' if uncertainty else ''}</div>'''

def table_markup(result, table_id):
    head = ''.join(f'<th scope="col">{esc(c)}</th>' for c in result['columns'])
    rows=[]
    for r in result['rows']:
        cells=''.join(f'<td data-label="{esc(result["columns"][i+1])}">{esc(str(v))}</td>' for i,v in enumerate(r['values']))
        rows.append(f'<tr class="{"is-highlight" if r.get("highlight") else ""}"><th scope="row">{esc(r["label"])}</th>{cells}</tr>')
    return f'<div class="table-scroll" tabindex="0" role="region" aria-label="{esc(result["title"])} data table"><table class="evidence-table"><caption class="sr-only">{esc(result["title"])}. {esc(result["context"])}</caption><thead><tr>{head}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>'

def result_markup(result, slug, i):
    title_id=f'{slug}-result-{i}'
    table = table_markup(result,title_id)
    if result.get('chart'):
        table=f'<details class="result-data"><summary>{research_icon("table")}View data table</summary>{table}</details>'
    return f'''<article class="evidence-panel" aria-labelledby="{title_id}"><header><span class="evidence-index">{i:02d}</span><div><h3 id="{title_id}">{esc(result['title'])}</h3><p class="result-question">{esc(result['question'])}</p></div></header><p class="result-context">{esc(result['context'])}</p>{chart_markup(result)}{table}<p class="result-interpretation">{research_icon('chart')}<span>{esc(result['interpretation'])}</span></p><div class="result-footnote"><p>{esc(result['caveat'])}</p><a href="{esc(result['source']['url'])}">{esc(result['source']['label'])} ↗</a></div></article>'''

def evidence_markup(d):
    settings=''.join(f'<div><dt>{esc(x["label"])}</dt><dd>{esc(x["value"])}</dd></div>' for x in d['evaluation'])
    results=''.join(result_markup(r,d['slug'],i) for i,r in enumerate(d['results'],1))
    limits=''.join(f'<li>{esc(x)}</li>' for x in d['limitations'])
    source = d['evidence_inventory']
    return f'''<section id="findings" data-tab-panel class="evidence-section"><div class="evidence-heading"><div><span class="kicker">Experiments &amp; evidence</span><h2>What the results show</h2></div><p>{esc(d['reading_guide'])}</p></div><dl class="evaluation-grid">{settings}</dl><p class="evidence-source"><span>Evidence source</span><a href="{esc(source['source_url'])}">{esc(source['version'])} ↗</a></p><div class="evidence-panels">{results}</div><aside class="study-boundaries" aria-labelledby="boundaries-title"><div>{research_icon('scale')}<h3 id="boundaries-title">Scope &amp; limitations</h3></div><ul>{limits}</ul></aside></section>'''

def research_brief(d):
    return f'''<div class="research-brief"><div><span class="kicker">The challenge</span><p>{esc(d['problem'])}</p></div><div><span class="kicker">The contribution</span><p>{esc(d['contribution'])}</p></div></div>'''

def takeaways_markup(d):
    items = ''.join(f'<li>{research_icon("check")}<span>{esc(t)}</span></li>' for t in d['takeaways'])
    return f'<ul class="research-takeaways">{items}</ul>'
