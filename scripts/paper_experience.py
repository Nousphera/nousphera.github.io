"""FedLN reading standard, with paper-specific artwork and source-bound results."""
from html import escape as esc
import importlib
import math
import re
from xml.etree import ElementTree as ET
from research_visuals import numeric_value, table_markup

GROUPS = ('compression', 'audio', 'foundations', 'privacy')


def load_story(slug):
    for name in GROUPS:
        try:
            module = importlib.import_module('stories.' + name)
        except ModuleNotFoundError as error:
            if error.name != 'stories.' + name:
                raise
            continue
        if slug in module.STORIES:
            story = module.STORIES[slug]
            validate_story(story)
            return story
    return None


def inline(text):
    """Only editorial emphasis is allowed in prose, never arbitrary HTML."""
    root = ET.fromstring('<span>' + text + '</span>')
    for element in root.iter():
        if element.tag not in {'span', 'strong', 'em', 'sub', 'sup', 'code', 'br'} or element.attrib:
            raise ValueError('Unsupported story prose markup')
    return text


def validate_story(s):
    for key in ('overview', 'contributions', 'steps', 'method', 'takeaways'):
        if not s.get(key): raise ValueError('Story missing ' + key)
    inline(s['overview'])
    for value in s['contributions'] + s['takeaways'] + s.get('scope',[]) + s.get('result_leads',[]): inline(value)
    if not 3 <= len(s['steps']) <= 5: raise ValueError('Story needs 3–5 steps')
    for step in s['steps']:
        if not step.get('title') or not step.get('caption'): raise ValueError('Story step needs a title and caption')
        svg = ET.fromstring(step['svg'])
        if svg.tag.split('}')[-1] != 'svg' or not svg.get('aria-label'):
            raise ValueError('Story SVG needs an accessible description')
        for element in svg.iter():
            if element.tag.split('}')[-1] in {'script','foreignObject','image'}:
                raise ValueError('Story artwork must be self-contained vector markup')
            if any(k.startswith('on') for k in element.attrib): raise ValueError('Inline event handler')
            if 'data-reveal' in element.attrib and not 0 <= int(element.get('data-reveal')) < 5000:
                raise ValueError('Artwork must be fully visible before a scene ends')
    for card in s['method']:
        inline(card['text'])
        if card.get('note'): inline(card['note'])
        if card.get('formula'):
            formula = ET.fromstring(card['formula'])
            if formula.tag != '{http://www.w3.org/1998/Math/MathML}math': raise ValueError('Use native MathML')


def tour_markup(p, s):
    buttons = ''.join(f'<button type="button" data-story-step="{i}" aria-pressed="{str(i==0).lower()}"><span>{i+1:02d}</span>{esc(step.get("short_title",step["title"]))}</button>' for i,step in enumerate(s['steps']))
    scenes = ''.join(f'<figure data-story-scene="{i}"><div class="story-picture">{step["svg"]}</div><figcaption><strong>{esc(step["title"])}</strong><span>{esc(step["caption"])}</span></figcaption></figure>' for i,step in enumerate(s['steps']))
    return f'''<section class="paper-story" data-paper-story data-running="false" aria-label="{esc(p['name'])} visual walkthrough">
<header class="story-head"><span class="px-kicker">Inside {esc(p['name'])}</span><button type="button" class="story-toggle" data-story-toggle hidden><svg viewBox="0 0 20 20" aria-hidden="true"><path class="story-play-icon" d="m6 3 11 7-11 7Z"/><path class="story-pause-icon" d="M4 3h4v14H4zM12 3h4v14h-4z"/></svg><span data-story-toggle-label>Play overview</span></button></header>
<nav class="story-steps" aria-label="Explore the method" data-story-controls hidden>{buttons}</nav><div class="story-progress" aria-hidden="true"><span data-story-progress></span></div>
<div class="story-viewport">{scenes}<button type="button" class="story-expand" data-story-expand hidden aria-label="Expand current diagram"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><path d="M8 3H3v5m13-5h5v5M3 16v5h5m13-5v5h-5"/></svg>Expand diagram</button></div><span class="sr-only" role="status" data-story-status></span><dialog class="story-dialog" data-story-dialog aria-label="{esc(p['name'])} enlarged diagram"><header><span>Method diagram</span><button type="button" data-story-close aria-label="Close enlarged diagram">Close ×</button></header><p class="story-dialog-hint">Swipe across the diagram</p><div class="story-dialog-scroll" data-story-expanded tabindex="0" aria-label="Enlarged diagram; scroll horizontally on small screens"></div><p data-story-expanded-caption></p></dialog></section>'''


def overview_markup(p, s):
    source = p.get('abstract_source', {'url':p['provenance']['source_url']})
    note = '<p>'+esc(source['note'])+'</p>' if source.get('note') else ''
    contributions = ''.join(f'<li><span class="px-bullet">{i:02d}</span><p>{inline(text)}</p></li>' for i,text in enumerate(s['contributions'],1))
    return f'''<section id="overview" data-tab-panel class="px-panel"><div class="px-intro"><span class="px-kicker">At a glance</span><p class="px-lead">{inline(s['overview'])}</p></div>{tour_markup(p,s)}<section class="px-contributions" aria-label="Contributions"><h2>What this adds</h2><ul>{contributions}</ul></section><details class="px-details"><summary>Abstract</summary><div class="px-details-body"><p>{esc(p['abstract'])}</p>{note}<a href="{esc(source['url'])}">Read more ↗</a></div></details></section>'''


def method_markup(p, s, originals):
    cards=[]
    for i, card in enumerate(s['method'],1):
        formula = f'<div class="px-equation">{card["formula"]}</div>' if card.get('formula') else ''
        note = f'<p class="px-formula-note">{inline(card["note"])}</p>' if card.get('note') else ''
        extra = f'<div class="px-technical">{formula}{note}</div>' if formula or note else ''
        cards.append(f'<article class="px-method-card"><header><span>{i:02d}</span><h3>{esc(card["title"])}</h3></header><div class="px-method-body {"has-technical" if extra else ""}"><p>{inline(card["text"])}</p>{extra}</div></article>')
    source=p['insight']['evidence_inventory']
    return f'''<section id="method" data-tab-panel class="px-panel"><header class="px-section-heading"><span class="px-kicker">How it works</span><h2>{esc(p['name'])}</h2></header><div class="px-method-cards">{''.join(cards)}</div><p class="px-source"><a href="{esc(source['source_url'])}">Method details in the paper ↗</a></p>{originals}</section>'''

# Each panel selects explicit columns from an audited table. Same-unit comparisons
# share an axis; accuracy and costs are separate, never mixed into one scale.
# (columns, label, axis maximum or None, higher/lower/None)
CHARTS = {
 'fedcompress': [ [([2],'Communication reduction (×)',None,'higher'),([1],'Accuracy change (pp)',None,None)], [([1],'Communication reduction (×)',4,'higher')], [([0,1],'Inference speedup (×)',None,'higher')] ],
 'fedcode': [ [([3],'Joint traffic reduction (×)',None,'higher'),([0],'Accuracy (%)',100,'higher')], [([1],'Joint traffic reduction (×)',None,'higher'),([0],'Accuracy change (pp)',None,None)], [([0,1],'Accuracy change (pp)',None,None)] ],
 'deltamask': [ [([0],'Accuracy (%)',100,'higher'),([1],'Bitrate (bits / parameter)',None,'lower')], [([0],'Accuracy (%)',100,'higher'),([1],'Bitrate (bits / parameter)',None,'lower')], [([0,1],'Accuracy (%)',100,'higher')] ],
 'fedstar': [ [([0,1],'Accuracy (%)',100,'higher')], [([0,1],'Accuracy (%)',100,'higher')], [([0,1],'Accuracy (%)',100,'higher')] ],
 'fedser': [ [([0,1,2],'Unweighted accuracy (%)',100,'higher')], [([0,1],'Unweighted accuracy (%)',100,'higher')] ],
 'plix': [ [], [([0,1],'Encoder latency (ms)',None,'lower')], [([0,1],'Encoder energy (mJ)',None,'lower')] ],
 'da-mldg': [ [([0,3],'Accuracy (%)',100,'higher')], [([0,1],'Accuracy (%)',100,'higher')] ],
 'mpsl': [ [([0,1,2],'Task accuracy (%)',100,'higher'),([3],'Client computation (GFLOPs)',None,'lower')], [([0,1],'Image-to-text recall@1 (%)',100,'higher')], [([0,1],'Normalized recall (%)',100,'higher')] ],
 'ae-psl': [ [([0,1,2],'Global accuracy (%)',100,'higher')], [([0],'Local accuracy (%)',100,'higher')], [([0,1],'Accuracy (%)',100,'higher')] ],
 'matu': [ [([0],'Accuracy (%)',100,'higher'),([1],'Traffic (Mbits / task / round)',None,'lower')], [([0],'Accuracy (%)',100,'higher'),([1],'Traffic (Mbits / task / round)',None,'lower')] ],
 'enccluster': [ [([2],'Upstream volume / FedAvg',4,'lower'),([3],'Encryption time (s)',None,'lower')], [([0,1],'Accuracy change (pp)',None,None)] ],
 'efu': [ [([0],'Retained accuracy (%)',100,'higher'),([1],'Forgotten accuracy (%)',100,'lower')], [([0],'Gender accuracy (%)',100,'higher'),([1],'Identity accuracy (%)',100,'lower')] ],
 'fiba': [ [([1,2],'Attack success rate (%)',100,None)], [([0],'Clean accuracy (%)',100,'higher'),([1],'Attack success rate (%)',100,'lower')], [([0],'Attack success rate (%)',100,None)] ]
}


def chart_markup(result, spec):
    columns, title, upper, direction = spec
    values=[numeric_value(row['values'][col]) for row in result['rows'] for col in columns]
    for row in result['rows']:
        for col in columns:
            if numeric_value(row['values'][col]) is None and str(row['values'][col]).strip() not in {'—','–'}:
                return ''
    values = [value for value in values if value is not None]
    if not values or any(not math.isfinite(value) for value in values): return ''
    lower = min(0, math.floor(min(values)))
    upper = upper if upper is not None else max(0,math.ceil(max(values)))
    if upper <= lower: upper = lower + 1
    if max(values)>upper: raise ValueError('Chart axis clips observations')
    extent = upper-lower
    zero=100*(0-lower)/extent
    legend = ''
    if len(columns)>1:
        legend = '<div class="px-legend">'+''.join(f'<span class="px-series-{j}"><i></i>{esc(result["columns"][col+1])}</span>' for j,col in enumerate(columns))+'</div>'
    rows=[]
    for row in result['rows']:
        bars=[]
        for j,col in enumerate(columns):
            raw=str(row['values'][col]); value=numeric_value(raw)
            if value is None:
                bars.append(f'<div class="px-measure px-series-{j}"><div class="px-missing"></div><span class="px-value">{esc(raw)}<span class="sr-only"> Not reported or not applicable in the source table</span></span></div>')
                continue
            start=100*(min(0,value)-lower)/extent; width=100*abs(value)/extent
            bars.append(f'<div class="px-measure px-series-{j}"><div class="px-track" style="--zero:{zero:.4f}%"><span class="px-bar" style="left:{start:.4f}%;width:{width:.4f}%"></span></div><span class="px-value">{esc(raw)}</span></div>')
        rows.append(f'<div class="px-chart-row {"is-own" if row.get("highlight") else ""}"><span class="px-row-label">{esc(row["label"])}</span><div>{"".join(bars)}</div></div>')
    unit = f'<span>{"Higher" if direction=="higher" else "Lower"} is better</span>' if direction else ''
    # Semantic table below preserves every cell and reported uncertainty. Text labels
    # make bars readable without colour and do not imply uncertainty intervals.
    return f'<div class="px-chart"><header><h4>{esc(title)}</h4>{unit}</header>{legend}<div class="px-chart-scale"><span>{lower:g}</span><span>{upper:g}</span></div>{"".join(rows)}</div>'


def results_markup(p, s):
    insight=p['insight']; blocks=[]
    titles=s.get('result_titles',[])
    leads=s.get('result_leads',[])
    for i,r in enumerate(insight['results']):
        charts=''.join(chart_markup(r,spec) for spec in CHARTS[p['slug']][i])
        count=charts.count('class="px-chart"')
        title=titles[i] if len(titles)>i else r['title']
        lead=leads[i] if len(leads)>i else r['interpretation']
        data=table_markup(r,f'{p["slug"]}-result-{i}')
        plot=f'<div class="px-chart-grid {"paired" if count>1 else ""}">{charts}</div>' if charts else data
        details=f'<details class="px-details px-experiment"><summary>Experiment details</summary><div class="px-details-body"><p>{esc(r["context"])}</p><p>{esc(r["caveat"])}</p>{data if charts else ""}</div></details>'
        blocks.append(f'<article class="px-result"><header class="px-result-heading"><span>{i+1:02d}</span><h3>{esc(title)}</h3></header><p class="px-result-lead">{inline(lead) if i<len(leads) else esc(lead)}</p>{plot}{details}<a class="px-result-source" href="{esc(r["source"]["url"])}">{esc(r["source"]["label"])} ↗</a></article>')
    settings=''.join(f'<div><dt>{esc(e["label"])}</dt><dd>{esc(e["value"])}</dd></div>' for e in insight['evaluation'])
    limits=''.join(f'<li>{esc(t)}</li>' for t in insight['limitations'])
    scope='<ul>'+''.join(f'<li>{inline(t)}</li>' for t in s.get('scope',[]))+'</ul>' if s.get('scope') else ''
    takeaways=''.join(f'<li>{inline(t)}</li>' for t in s['takeaways'])
    source=insight['evidence_inventory']
    version = re.search(r'arXiv:\s*([0-9.]+v[0-9]+)', source['version'], re.I)
    source_label = 'arXiv:' + version.group(1) if version else 'the source manuscript'
    source_line = f'<p class="px-source">Results from <a href="{esc(source["source_url"])}">{esc(source_label)} ↗</a></p>'
    return f'''<section id="findings" data-tab-panel class="px-panel"><header class="px-section-heading"><span class="px-kicker">Evaluation</span><h2>Results</h2>{source_line}</header>{''.join(blocks)}<aside class="px-takeaways"><h2>Takeaways</h2><ul>{takeaways}</ul></aside><details class="px-details"><summary>Study scope &amp; sources</summary><div class="px-details-body">{scope}<dl class="px-settings">{settings}</dl><h3>Scope &amp; limitations</h3><ul>{limits}</ul><p><a href="{esc(source['source_url'])}">{esc(source['version'])} ↗</a></p></div></details></section>'''
