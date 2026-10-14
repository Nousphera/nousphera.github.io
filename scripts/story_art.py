"""Small theme-aware SVG vocabulary for paper-specific explanatory scenes."""
from html import escape
from math import atan2, degrees

def label(x, y, text, cls='sa-label', anchor='middle'):
    return f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anchor}">{escape(text)}</text>'

def node(x, y, w, h, title, sub='', icon=None, tone='accent'):
    from research_icons import research_icon
    art = f'<g class="sa-node sa-{tone}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14"/>'
    if icon:
        art += f'<g transform="translate({x+w/2-18} {y+16})">' + research_icon(icon).replace('<svg ', '<svg width="36" height="36" ',1) + '</g>'
    art += label(x+w/2, y+h-(37 if sub else 22), title)
    if sub: art += label(x+w/2, y+h-14, sub, 'sa-small')
    return art+'</g>'

def arrow(x1,y1,x2,y2, text='', tone='accent', curved=None):
    path = curved or f'M{x1} {y1} L{x2} {y2}'
    angle=degrees(atan2(y2-y1,x2-x1))
    art=f'<g class="sa-{tone}"><path class="sa-link" d="{path}"/><path class="sa-flow" d="{path}"/><path d="M-7 -4 L0 0 L-7 4" transform="translate({x2} {y2}) rotate({angle})" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>'
    if text: art+=label((x1+x2)/2,(y1+y2)/2-10,text,'sa-small')
    return art+'</g>'

def matrix(x,y,values,cols=4,size=22,gap=5,tone='accent'):
    art=f'<g class="sa-matrix sa-{tone}">'
    for i,v in enumerate(values):
        art+=f'<rect x="{x+(i%cols)*(size+gap)}" y="{y+(i//cols)*(size+gap)}" width="{size}" height="{size}" rx="4" class="sa-cell {"sa-on" if v else "sa-off"}"/>'
    return art+'</g>'

def group(content, at=0):
    return f'<g data-reveal="{at}">{content}</g>'

def svg(content, label_text, viewbox='0 0 600 300'):
    return f'<svg class="story-art" viewBox="{viewbox}" role="img" aria-label="{escape(label_text, quote=True)}" xmlns="http://www.w3.org/2000/svg">{content}</svg>'
