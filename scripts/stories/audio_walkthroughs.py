"""Connected audio walkthroughs, grounded in PLiX §2/Fig.1 and DA-MLDG §III.

Coordinates, waveforms and energy glyphs are explanatory, not measurements.
PLiX inference uses support-only means and a frozen shared encoder. DA-MLDG
keeps target data outside the full meta-training loop (Algorithm 1).
"""
from html import escape
from research_icons import research_icon


def icon(name):
    return research_icon(name, 'ax-icon')


def reveal(body, at=0, cls=''):
    return f'<div class="{cls}" data-reveal="{at}">{body}</div>'


def arrow(label=''):
    return f'<div class="ax-arrow" aria-hidden="true"><svg viewBox="0 0 40 24"><path d="M2 12h34m-7-7 7 7-7 7"/></svg><span>{label}</span></div>'


def wave(tone=''):
    return f'<span class="ax-wave {tone}" aria-hidden="true">'+''.join(f'<i style="--h:{h}px;--i:{i}"></i>' for i,h in enumerate([5,9,18,30,21,11,24,35,18,9,5]))+'</span>'


def clip(word, tone='', query=False):
    return f'<div class="ax-clip {tone}" data-clip-kind="{"query" if query else "support"}">{wave(tone)}<strong>{word}</strong>{icon("unlabeled" if query else "labeled")}</div>'


def card(title, body, name, tone='', attrs=''):
    return f'<section class="ax-card {tone}" {attrs}><header>{icon(name)}<strong>{title}</strong></header>{body}</section>'


def encoder(frozen=True):
    return '<div class="ax-encoder" data-encoder-state="'+('frozen' if frozen else 'trainable')+'">'+icon('encoder')+'<strong>Audio encoder</strong><span>'+icon('frozen' if frozen else 'train')+('Fixed weights' if frozen else 'Learn embeddings')+'</span></div>'


def prototype(word, tone=''):
    return f'<div class="ax-prototype {tone}" data-prototype="{word}"><i></i><strong>{word}</strong></div>'


def embedding_plot(query=False, collapse=False):
    # The class means exactly match the centers in this illustrative geometry.
    sets=[('Go','',[(75,66),(105,80),(90,94)],(90,80)),('Stop','ax-purple',[(220,146),(250,160),(235,174)],(235,160))]
    content='<path class="ax-axis" d="M25 20v190h290"/>'
    for word,tone,points,center in sets:
        cx,cy=center
        for i,(x,y) in enumerate(points):
            content+=f'<g class="{tone}" data-reveal="{600+i*500}"><path class="ax-mean-line" d="M{x} {y}L{cx} {cy}"/><circle class="ax-support-dot" cx="{x}" cy="{y}" r="5"/></g>'
            if collapse:
                content+=f'<circle class="ax-contribution {tone}" cx="{x}" cy="{y}" r="4" style="--dx:{cx-x}px;--dy:{cy-y}px" data-reveal="{600+i*500}"/>'
        content+=f'<g class="{tone}" data-reveal="2400"><circle class="ax-centroid" cx="{cx}" cy="{cy}" r="12"/><text x="{cx+20}" y="{cy-17}" class="ax-plot-label">{word}</text></g>'
    if query:
        content+='<g data-reveal="1200"><path class="ax-distance ax-purple" d="M136 103 235 160"/><path class="ax-distance ax-nearest" d="M136 103 90 80"/><path class="ax-query-point" d="m136 94 9 9-9 9-9-9Z"/><text x="140" y="133" class="ax-plot-label">Query</text></g>'
    return f'<svg class="ax-plot {"ax-collapse" if collapse else ""}" viewBox="0 0 340 230" role="img" aria-label="Support embeddings average to Go and Stop prototypes. A separate query is closer to Go." data-prototype-source="support-only">{content}</svg>'


def plix_context(index):
    training=index==0
    return f'<div class="ax-context"><span class="ax-context-active">{icon("train" if training else "client")}<strong>{"Training" if training else "Recognition"}</strong></span><span>{icon("globe" if training else "frozen")}{"Multilingual episodes" if training else "Same frozen encoder"}</span><span>{icon("language")}<b>{"Learn a space" if training else "New vocabulary"}</b></span></div>'


def plix_body(index):
    supports=clip('Go')+clip('Stop','ax-purple')
    if index==0:
        episode = supports + '<div class="ax-training-query" data-clip-kind="query" data-query-label="Go">' + icon('waveform') + '<span>Query</span><b>Go</b>' + icon('labeled') + '</div>'
        objective = '<div class="ax-training-prototypes" data-prototype-source="support-only"><span>Support means</span>' + prototype('Go') + prototype('Stop','ax-purple') + '</div><div class="ax-training-distance">'+icon('target')+'<b>Query distances</b></div><div class="ax-training-loss" data-loss="cross-entropy" data-label-source="query-ground-truth"><b>Cross-entropy</b><span>Known query label: <strong>Go</strong></span></div>'
        return '<div class="ax-pipeline">'+reveal(card('Word episode',episode,'language'),0)+reveal(arrow('Both'),700)+reveal(encoder(False),1200)+reveal(arrow(),2000)+reveal(card('Compare + learn',objective,'target'),2600)+'</div>'+reveal('<div class="ax-cycle">'+icon('loop')+'<strong>Query loss</strong><span>→</span><strong>Update encoder</strong><span>→</span><strong>New episode</strong></div>',4300)
    if index==1:
        return '<div class="ax-pipeline">'+reveal(card('Labeled supports',supports,'labeled'),0)+reveal(arrow('Encode'),900)+reveal(encoder(),1500)+reveal(arrow(),2400)+reveal(card('Word embeddings','<div class="ax-dot-row"><i></i><i></i><i></i><b>Go</b></div><div class="ax-dot-row ax-purple"><i></i><i></i><i></i><b>Stop</b></div>','embedding'),3000)+'</div>'+reveal('<div class="ax-rule">'+icon('labeled')+'<strong>Support clips</strong><span>→</span>Reference words</div>',4200)
    if index==2:
        return '<div class="ax-map-layout">'+card('Same embedding space',embedding_plot(collapse=True),'embedding')+reveal(card('One mean per word',prototype('Go')+prototype('Stop','ax-purple')+'<div class="ax-rule"><strong>Support only</strong></div>','aggregate',attrs='data-query-in-mean="false"'),3300)+'</div>'
    if index==3:
        return '<div class="ax-map-layout">'+card('Distance to prototypes',embedding_plot(query=True),'target')+'<div class="ax-query-column">'+reveal(clip('?', 'ax-amber', True),0)+reveal(encoder(),600)+reveal('<div class="ax-answer">'+icon('check')+'<span>Nearest word</span><strong>Go</strong></div>',3400)+'</div></div>'
    return '<div class="ax-pipeline">'+reveal(card('New supports',clip('Left')+clip('Right','ax-purple'),'language'),0)+reveal(arrow('Encode'),900)+reveal(encoder(),1500)+reveal(arrow('Average'),2300)+reveal(card('New prototypes',prototype('Left')+prototype('Right','ax-purple'),'aggregate'),3000)+'</div>'+reveal('<div class="ax-cycle">'+icon('frozen')+'<strong>Fixed encoder</strong><span>+</span>'+icon('adapt')+'<strong>Replace prototypes</strong></div>',4300)


def domain(word,tone=''):
    return f'<span class="ax-domain {tone}">{icon("waveform")}<b>{word}</b></span>'


def da_context(index):
    return f'<div class="ax-context"><span class="{"ax-context-active" if index<4 else ""}">{icon("database")}<strong>Source corpora</strong></span><span>{icon("train")}{"Meta-training" if index<4 else "Training complete"}</span><span class="ax-target {"ax-context-active" if index==4 else ""}" data-target-access="{"evaluation-only" if index==4 else "excluded"}">{icon("target")}<b>Unseen target</b><small>{"Evaluate" if index==4 else "Held out"}</small></span></div>'


def model(symbol,adapted=False):
    return '<div class="ax-model '+('ax-purple' if adapted else '')+'">'+icon('model')+f'<strong>{symbol}</strong></div>'


def energy(tone, value):
    # Symbolic unequal logits, intentionally no measured numeric scale.
    return '<div class="ax-energy '+tone+'">'+''.join(f'<i style="--bar:{v}px"></i>' for v in value)+'</div>'


def da_body(index):
    if index==0:
        return '<div class="ax-pipeline">'+reveal(card('Source pool',domain('A')+domain('B','ax-purple')+domain('C'),'database'),0)+reveal(arrow('Resample'),800)+reveal(card('Meta-train',domain('A')+domain('C')+'<b class="ax-symbol">S′</b>','train'),1500)+reveal(card('Meta-test',domain('B','ax-purple')+'<b class="ax-symbol">V</b>','target','ax-purple'),2500)+'</div>'+reveal('<div class="ax-rule"><strong>Disjoint source subsets</strong><span>·</span>Same training pool</div>',3600)
    if index==1:
        return '<div class="ax-pipeline">'+reveal(card('Meta-train',domain('A')+domain('C'),'train'),0)+reveal(arrow(),600)+reveal(model('θ'),1200)+reveal(arrow('Loss gradient'),2200)+reveal(model('θ′',True),3000)+'</div>'+reveal('<div class="ax-equation"><span>Inner step</span><strong>θ′ = θ − η ∇L<sub>train</sub>(θ)</strong></div>',4000)
    if index==2:
        return '<div class="ax-pipeline ax-energy-pipeline">'+reveal(card('Meta-train · θ′',energy('',[31,51,40])+'<strong>E<sub>train</sub></strong>','chart'),0)+reveal('<div class="ax-gap">'+icon('compare')+'<strong>|ΔE|</strong><span>Energy gap</span><b>γ</b></div>',2400)+reveal(card('Meta-test · θ′',energy('ax-purple',[52,24,35])+'<strong>E<sub>test</sub></strong>','chart','ax-purple'),1000)+'</div>'+reveal('<div class="ax-rule"><strong>Mean log-sum-exp</strong><span>→</span><strong>Meta-test weight</strong></div>',3900)
    if index==3:
        return '<div class="ax-objective"><div class="ax-losses">'+reveal(card('Meta-train','<b class="ax-symbol">L<sub>train</sub>(θ)</b>','train'),0)+reveal('<b class="ax-plus">+</b>',900)+reveal(card('Meta-test','<b class="ax-symbol"><em>γ</em> L<sub>test</sub>(θ′)</b>','target','ax-purple'),1500)+'</div>'+reveal(arrow('Outer gradient'),2300)+reveal(model('θ ← update'),3100)+'</div>'+reveal('<div class="ax-cycle">'+icon('exchange')+'<strong>Update θ</strong><span>→</span><strong>Resample sources</strong><span>→</span><strong>Repeat</strong></div>',4400)
    return '<div class="ax-pipeline">'+reveal(card('Unseen corpus',domain('Target','ax-purple'),'target','ax-purple',attrs='data-target-access="evaluation-only"'),0)+reveal(arrow(),900)+reveal(card('Trained model',model('θ*'),'model'),1600)+reveal(arrow(),2300)+reveal(card('Emotion prediction',icon('emotion')+'<strong>Held-out evaluation</strong>','check'),3100)+'</div>'+reveal('<div class="ax-rule"><strong>New corpus</strong><span>·</span>Weights fixed at evaluation</div>',4200)


def scenes(slug,items,context,body):
    return [{'title':title,'short_title':short,'title_in_art':True,'caption':caption,'duration_ms':duration,
             'art':f'<div class="story-art ax-art" role="group" aria-label="{escape(description,quote=True)}">{context(i)}<div class="ax-stage"><header><span>{i+1:02d} / {len(items):02d}</span><h3>{title}</h3></header>{body(i)}</div></div>'}
            for i,(short,title,caption,duration,description) in enumerate(items)]

PLIX_STEPS=scenes('plix',[
 ('Train','Learn an acoustic space','Multilingual training · Changing word episodes',7500,'Training uses changing support and query episodes. Query classification loss updates the encoder. Demonstration words and shapes are schematic, not measured embeddings.'),
 ('Encode','New words → embeddings','Labeled supports · Shared encoder · Fixed weights',7500,'At inference, labeled support clips for Go and Stop pass through the same frozen encoder. These words illustrate a supplied vocabulary, not recognition measurements.'),
 ('Average','Supports → word prototypes','One word · One mean embedding',8000,'Prototype geometry is illustrative. Only support embeddings contribute to each word mean; queries are excluded. Animated dots converge on their class mean without moving the underlying support observations.'),
 ('Recognize','Query → nearest word','Separate query · Squared Euclidean distance',8000,'The same frozen encoder embeds a separate query. In this schematic geometry, it is closer to Go than Stop. Query data never enter the support averages. Choice is among supplied words.'),
 ('Replace','New vocabulary · Same encoder','New supports → New prototypes · No retraining',7500,'Replace support clips to define new Left and Right prototypes while retaining encoder weights. This is closed-set segmented-clip classification, not unknown-word rejection.')
],plix_context,plix_body)

DA_STEPS=scenes('da-mldg',[
 ('Split','Rehearse a domain shift','Meta-train + Meta-test = Source domains',7500,'Source domains are randomly divided into disjoint meta-train and meta-test subsets. Both are source training data. The unseen target remains outside all training computations.'),
 ('Adapt','One inner update','Meta-train loss → Adapted parameters',7500,'A gradient update on source meta-train loss maps theta to theta prime. This temporary model is used for meta-test evaluation and energy estimation.'),
 ('Weight','Energy gap → Shift weight','Adapted model · Two source energies · One weight',8000,'Under theta prime, average log-sum-exp energies of each source subset produce gamma, their absolute difference. Symbolic bars have no numeric scale and are not empirical energy measurements.'),
 ('Update','Learn across the split','Weighted meta-test loss · Outer update · Repeat',8000,'The outer objective is meta-train loss at theta plus gamma times meta-test loss at theta prime. Its gradient accounts for inner adaptation. The next iteration resamples source partitions; the target is excluded.'),
 ('Evaluate','Test an unseen corpus','Training complete · Target evaluation',7500,'Only after training is the final model evaluated on the unseen target corpus. This diagram makes no claim about performance; all seven source/target comparisons appear in Results.')
],da_context,da_body)
