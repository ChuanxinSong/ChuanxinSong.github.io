"""Build the static homepage from data/site.json. Python standard library only."""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / 'data/site.json').read_text(encoding='utf-8'))

def esc(value):
    return html.escape(str(value), quote=True)

def link(label, url, cls=''):
    external = ' target="_blank" rel="noopener noreferrer"' if url.startswith('https://') else ''
    return f'<a href="{esc(url)}" class="{cls}"{external}>{esc(label)}</a>'

def links(items):
    return '<div class="resource-links">' + ''.join(link(x['label'], x['url']) for x in items) + '</div>'

def bio_html(text):
    rendered = esc(text)
    for item in DATA['profile'].get('bioLinks', []):
        rendered = rendered.replace(esc(item['label']), link(item['label'], item['url']))
    return rendered


def media(paper):
    m = paper['media']
    title = esc(paper['title'])
    if m['type'] == 'image':
        return f'''<button class="paper-preview image-preview" type="button" data-image="{esc(m['full'])}" data-caption="{title}" aria-label="Enlarge method diagram: {title}"><img src="{esc(m['src'])}" alt="{esc(m['alt'])}" loading="lazy" width="{m['width']}" height="{m['height']}"><span class="preview-caption">Method overview <span aria-hidden="true">↗</span></span></button>'''
    if m['type'] == 'video':
        destination = next((x['url'] for x in paper['links'] if x['label'] == 'Project'), None)
        video = f'''<video muted loop playsinline preload="none" data-src="{esc(m['src'])}" poster="{esc(m['poster'])}" aria-label="{esc(m.get('alt', paper['title'] + ' video preview'))}" width="{m.get('width', 640)}" height="{m.get('height', 640)}"></video>'''
        if m.get('panelLabels'):
            labels = ''.join(f'<span class="video-panel-label video-panel-label-{position}">{esc(m["panelLabels"][position])}</span>' for position in ('top', 'bottom'))
            video = f'<span class="video-panel-frame">{video}{labels}</span>'
        if m.get('full'):
            preview = f'<a class="video-enlarge" href="{esc(m["full"])}" data-full-video data-title="{esc(paper["short"])} · {esc(m.get("caption", "Video preview"))}" aria-label="Enlarge {esc(paper["short"])} video" aria-haspopup="dialog" target="_blank" rel="noopener">{video}<span class="video-enlarge-hint" aria-hidden="true">Enlarge ↗</span></a>'
        else:
            preview = f'<a href="{esc(destination)}" target="_blank" rel="noopener noreferrer" aria-label="Open {esc(paper["short"])} project">{video}</a>' if destination else video
        compact = ' video-only' if m.get('compact') else ''
        compact += ' video-labeled' if m.get('panelLabels') else ''
        caption = '' if m.get('compact') else f'<span>{esc(m.get("caption", paper["short"] + " · Video preview"))}</span>'
        return f'''<div class="paper-preview video-preview{compact}">{preview}<div class="video-toolbar">{caption}<button type="button" class="video-toggle" aria-label="Play {esc(paper['short'])} preview">Play</button></div><span class="video-error" role="status"></span></div>'''
    return '''<div class="paper-preview pending-preview"><svg viewBox="0 0 72 40" fill="none" aria-hidden="true"><rect x="1" y="1" width="70" height="38" rx="3"/><path d="M1 12c20 8 50 8 70 0M1 28c20-8 50-8 70 0M25 1c-6 12-6 26 0 38M47 1c6 12 6 26 0 38"/></svg><span>Panoramic video wandering</span><small>Video preview coming soon</small></div>'''

def cycle_diagram(start, end, paper=None):
    label = f'{start} to {end} and back to {start}'
    if paper:
        return f'''<svg class="cycle-diagram" viewBox="0 0 180 54" role="img" aria-label="{esc(label)}" focusable="false"><path class="cycle-return" d="M164 33V12Q164 5 157 5H23Q16 5 16 12V33 M12 29L16 33L20 29"/><path d="M36 44H138 M132 39L138 44L132 49"/><text class="cycle-node" x="16" y="48">{esc(start)}</text><text class="cycle-node" x="164" y="48">{esc(end)}</text><text class="cycle-paper" x="90" y="30">{esc(paper)}</text></svg>'''
    return f'''<svg class="cycle-diagram cycle-diagram-small" viewBox="0 0 110 36" role="img" aria-label="{esc(label)}" focusable="false"><path class="cycle-return" d="M94 17V10Q94 4 88 4H20Q14 4 14 10V17 M10 13L14 17L18 13"/><path d="M30 27H72 M68 23L72 27L68 31"/><text class="cycle-node" x="14" y="31">{esc(start)}</text><text class="cycle-node" x="94" y="31">{esc(end)}</text></svg>'''

def publication(p):
    authors = ', '.join((f'<strong>{esc(a)}</strong>' if a == DATA['profile']['name'] else esc(a)) + ('<sup title="Corresponding author" aria-label="Corresponding author">†</sup>' if a in p.get('correspondingAuthors', []) else '') for a in (p['authors'] or []))
    if not authors:
        authors = '<strong>Chuanxin Song</strong><span class="pending-copy"> · Full author list to be confirmed</span>'
    venue_class = 'venue under-review' if p.get('status') == 'under-review' else 'venue'
    focus = f'<span class="research-focus">{esc(p["focus"])}</span>' if p.get('focus') else ''
    if p.get('focusLoop'):
        loop = p['focusLoop']
        focus = f'<span class="research-focus research-focus-cycle">{cycle_diagram(loop["from"], loop["to"])}</span>'
    return f'''<article class="publication" id="{esc(p['id'])}">{media(p)}<div class="paper-info"><div class="publication-meta"><p class="{venue_class}">{esc(p['venue'])}</p>{focus}</div><h4>{esc(p['title'])}</h4><p class="authors">{authors}</p><p class="paper-summary">{esc(p['summary'])}</p>{links(p['links'])}</div></article>'''

def research_path(group):
    steps = group.get('trajectory', [])
    if not steps:
        return ''
    parts = []
    pending_node = steps[0]['from']
    for step in steps:
        label = f'{step["paper"]}: {step["from"]} to {step["to"]}'
        if step.get('loop'):
            label += f' and back to {step["from"]}'
            parts.append(f'<a class="path-cycle" href="#{esc(step["id"])}" aria-label="{esc(label)}">{cycle_diagram(step["from"], step["to"], step["paper"])}</a>')
            pending_node = None
        else:
            if pending_node:
                parts.append(f'<span class="path-node">{esc(pending_node)}</span>')
            arrow = '<svg class="path-arrow" viewBox="0 0 80 20" aria-hidden="true" focusable="false"><path d="M2 10H78 M72 4L78 10L72 16"/></svg>'
            parts.append(f'<a class="path-transition" href="#{esc(step["id"])}" aria-label="{esc(label)}"><span>{esc(step["paper"])}</span>{arrow}</a>')
            pending_node = step['to']
    if pending_node:
        parts.append(f'<span class="path-node">{esc(pending_node)}</span>')
    return '<div class="research-path" role="group" aria-label="Research directions between video and 3D">' + ''.join(parts) + '</div>'

def publication_group(group):
    show_title = group.get('showTitle', True)
    heading = f'<h3 id="{esc(group["id"])}">{esc(group["title"])}</h3>' if show_title else ''
    path = research_path(group)
    group_heading = f'<div class="publication-group-heading">{heading}{path}</div>' if heading or path else ''
    description_id = '' if show_title else f' id="{esc(group["id"])}"'
    description = f'<p class="group-description"{description_id}>{esc(group["description"])}</p>' if group.get('description') else ''
    entries = ''.join(publication(paper) for paper in DATA['publications'] if paper['group'] == group['id'])
    return f'<section class="publication-group" aria-labelledby="{esc(group["id"])}">{group_heading}{description}{entries}</section>'


def competition(item):
    return f'''<article class="competition-award"><button class="competition-photo" type="button" data-image="{esc(item['image'])}" data-caption="{esc(item['title'])}" aria-label="Enlarge photo: {esc(item['title'])}"><img src="{esc(item['preview'])}" alt="{esc(item['alt'])}" loading="lazy" width="{item['previewWidth']}" height="{item['previewHeight']}"><span>View photo ↗</span></button><div class="competition-copy"><p class="venue">{esc(item['year'])} · {esc(item['category'])}</p><h3>{esc(item['title'])}</h3><p class="competition-achievement">{esc(item['achievement'])}</p><a class="competition-watch" href="{esc(item['video'])}" data-competition-video data-title="{esc(item['title'])}" target="_blank" rel="noopener">{esc(item['videoLabel'])} ↗</a></div></article>'''


p = DATA['profile']
portrait_patch = f'<img class="portrait-watermark-patch" src="{esc(p["photoPatch"])}" alt="" aria-hidden="true" width="{p['photoPatchWidth']}" height="{p['photoPatchHeight']}">' if p.get('photoPatch') else ''
publications = ''.join(publication_group(group) for group in DATA['publicationGroups'])
honors = ''.join(f'<li>{esc(h["title"])}</li>' for h in DATA['honors'])
service = ''.join(f'<p><strong>{esc(item["role"])}:</strong> {esc(item["venues"])}</p>' for item in DATA['academicService'])

competitions = ''.join(competition(item) for item in DATA['competitionAwards'])

t = DATA['thesis']
page = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Chuanxin Song</title>
  <meta name="description" content="Chuanxin Song is a CS Ph.D. candidate at Peking University researching scene generation and understanding, controllable generation, and embodied applications of generative models.">
  <meta name="theme-color" content="#f5f6f7">
  <meta property="og:title" content="Chuanxin Song | Academic Homepage">
  <meta property="og:description" content="Scene generation and understanding, controllable generation, and embodied applications of generative models.">
  <meta property="og:type" content="website">
  <link rel="icon" href="favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="styles.css?v=misc-36">
  <script src="app.js?v=pvwander-17" defer></script>
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
<main id="main" class="page">
<section id="about" class="profile" aria-labelledby="profile-name"><div class="profile-copy"><h1 id="profile-name">{esc(p['name'])} <span lang="zh">{esc(p['nameZh'])}</span></h1>{''.join(f'<p class="bio">{bio_html(b)}</p>' for b in p['bio'])}{links(p['links'])}</div><figure class="portrait"><div class="portrait-frame"><img src="{esc(p['photo'])}" alt="Chuanxin Song at a spatial intelligence conference" width="{p['photoWidth']}" height="{p['photoHeight']}" fetchpriority="high">{portrait_patch}</div><figcaption><span class="portrait-name">{esc(p["photoCaption"])}</span><div class="portrait-interests"><strong>Recent interests:</strong>{"".join(f"<span>{esc(interest)}</span>" for interest in p["recentInterests"])}</div></figcaption></figure></section>
<section id="publications" class="section" aria-labelledby="publications-title"><div class="section-heading"><h2 id="publications-title">Selected works</h2>{link('Google Scholar ↗', p['scholar'], 'section-link')}</div>{publications}</section>
<section id="thesis" class="section" aria-labelledby="thesis-title"><div class="section-heading"><h2 id="thesis-title">Master’s Thesis</h2></div><article class="thesis"><a class="thesis-cover" href="{esc(t['pdf'])}" target="_blank" rel="noopener" aria-label="Read the complete master's thesis PDF"><img src="{esc(t['cover'])}" alt="Original cover of Chuanxin Song's master's thesis at Shandong University" loading="lazy" width="150" height="212"></a><div class="thesis-info"><p class="venue">SHANDONG UNIVERSITY · 2024</p><h3>{esc(t['title'])}</h3><p class="chinese-title" lang="zh">{esc(t['titleZh'])}</p><p class="thesis-meta">Chuanxin Song · Advised by Prof. Xin Ma</p><p class="thesis-award">{esc(t['award'])}</p><p>{esc(t['description'])}</p><div class="resource-links"><a href="{esc(t['pdf'])}" target="_blank" rel="noopener">Read thesis <span class="link-detail">PDF · 111 pages</span></a></div></div></article></section>
<section id="honors" class="section" aria-labelledby="honors-title"><div class="section-heading"><h2 id="honors-title">Selected Honors &amp; Awards</h2></div><ul class="honors-list">{honors}</ul><div class="competition-awards">{competitions}</div></section>
<section id="academic-service" class="section" aria-labelledby="service-title"><div class="section-heading"><h2 id="service-title">Academic Service</h2></div><div class="service-list">{service}</div></section>
<section id="misc" class="section" aria-labelledby="misc-title">
  <div class="section-heading"><h2 id="misc-title">Misc</h2></div>
  <p class="misc-copy">{esc(DATA['misc'])}</p>
</section>
</main>
<footer class="page site-footer"><span>© {esc(DATA['updated'][:4])} Chuanxin Song</span><span>Last updated {esc(DATA['updatedLabel'])}</span><a href="#about">Back to top ↑</a></footer>
<dialog id="image-dialog" aria-labelledby="image-dialog-caption"><div class="dialog-toolbar"><span>Method overview</span><button type="button" class="dialog-close" aria-label="Close enlarged image">Close ×</button></div><img id="enlarged-image" alt=""><p id="image-dialog-caption"></p><a id="original-image" target="_blank" rel="noopener">Open full-resolution image ↗</a></dialog>
<dialog id="video-dialog" aria-labelledby="video-dialog-title"><div class="dialog-toolbar"><span id="video-dialog-title"></span><button type="button" class="dialog-close" aria-label="Close video">Close ×</button></div><video controls playsinline preload="none"></video><p class="dialog-video-error" role="status" hidden>Playback unavailable. <a target="_blank" rel="noopener">Open video directly ↗</a></p></dialog>
</body>
</html>
'''
(ROOT / 'index.html').write_text(page, encoding='utf-8')
print(f'Built index.html with {len(DATA["publications"])} publications.')
