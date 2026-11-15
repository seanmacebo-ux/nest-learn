#!/usr/bin/env python3
"""Nest Learn: its own app (not The Nest). Builds index.html + one page per track from tracks/<slug>.json.

Track JSON: slug, title, emoji, intro, system{who_pays, who_decides, who_profits, what_it_means_for_us},
sections[{title, points}], deep_sections[...], do[], ask[], watch_out[],
resources[{type, title, source, url, year?, why, takeaways[], by?}].
Run: python3 build.py
"""
import json
import re
from html import escape as e
from pathlib import Path

ROOT = Path(__file__).parent
ORDER = ["cervix", "money", "body", "food", "water"]
V = "20261115e"

TYPE_IC = {"article": "📰", "website": "🌐", "study": "🔬", "book": "📚", "video": "🎬", "podcast": "🎧", "place": "📍", "tool": "🧰"}
TYPE_NAME = {"article": "Articles", "website": "Websites", "study": "Studies", "book": "Books", "video": "Videos", "podcast": "Podcasts", "place": "Places", "tool": "Tools"}
# each track gets its own colour pair (gradient)
HUE = {"cervix": ("#C2185B", "#7B1FA2"), "money": ("#0E9F6E", "#0B6E99"), "body": ("#E8553D", "#C2185B"),
       "food": ("#5A9E2F", "#D9822B"), "water": ("#1E88E5", "#00ACC1")}
SYS = [("who_pays", "💸", "Who pays"), ("who_decides", "⚖️", "Who decides"), ("who_profits", "🏦", "Who profits"),
       ("what_it_means_for_us", "🫶", "What it means for us")]


def views(t):
    v = []
    if t.get("system"): v.append(("system", "🧭", "The system"))
    v.append(("understand", "🧠", "Understand"))
    if t.get("deep_sections"): v.append(("deep", "🔬", "Deep dive"))
    v.append(("do", "✅", "What we do"))
    if t.get("ask"): v.append(("ask", "❓", "Questions"))
    if t.get("watch_out"): v.append(("watch", "⚠️", "Watch out"))
    v.append(("library", "📚", "Library"))
    return v


def load():
    return [json.loads((ROOT / "tracks" / f"{s}.json").read_text()) for s in ORDER if (ROOT / "tracks" / f"{s}.json").exists()]


def head(title, emoji, slug=""):
    a, b = HUE.get(slug, ("#FF6B4A", "#7C3AED"))
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#0F1B2D">
<meta name="color-scheme" content="light dark">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Nest Learn">
<link rel="manifest" href="manifest.webmanifest">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<meta name="robots" content="noindex, nofollow">
<title>{e(title)} · Nest Learn</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>{emoji}</text></svg>">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500..800&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap">
<link rel="stylesheet" href="learn.css?v={V}">
<style>:root {{ --t1: {a}; --t2: {b}; }}</style>
</head>
<body>
"""


def topbar(tracks, current):
    items = ['<a class="mi" href="index.html"><span class="mic">🏠</span><span><b>Home</b><small>All tracks</small></span></a>']
    for t in tracks:
        a, b = HUE.get(t["slug"], ("#FF6B4A", "#7C3AED"))
        vs = "".join(f'<a href="{t["slug"]}.html#{k}">{ic} {n}</a>' for k, ic, n in views(t))
        cur = ' aria-current="page"' if current == t["slug"] else ""
        items.append(f'<div class="mgroup" style="--t1:{a};--t2:{b}"><a class="mi"{cur} href="{t["slug"]}.html"><span class="mic">{t["emoji"]}</span>'
                     f'<span><b>{e(t["title"])}</b><small>{len(t.get("resources", []))} sources</small></span></a><div class="mviews">{vs}</div></div>')
    return f"""<header class="top"><div class="top-in">
  <a class="brand" href="index.html"><span class="logo">📖</span><span>Nest <i>Learn</i></span></a>
  <button type="button" class="menubtn" aria-expanded="false" aria-controls="menu"><span class="bars"></span> Menu</button>
</div></header>
<div class="menu" id="menu" hidden><div class="menu-in"><p class="mlbl">Jump to any track, or straight to one view</p>{''.join(items)}</div></div>
"""


def addbox(title="", tracks=None):
    pick = ""
    if tracks:
        pick = ('<div class="qchips tpick" role="group" aria-label="Which track">'
                + "".join(f'<button type="button" aria-pressed="false" data-t="{e(t["title"])}">{t["emoji"]} {e(t["title"])}</button>' for t in tracks)
                + '<button type="button" aria-pressed="false" data-t="New topic">🆕 New topic</button></div>')
    kinds = "".join(f'<button type="button" aria-pressed="false">{TYPE_IC[k]} {n}</button>'
                    for k, n in [("book", "Book"), ("video", "Video"), ("article", "Article"), ("website", "Website"), ("podcast", "Podcast"), ("place", "Place")])
    return f"""<details class="addbox" data-track="{e(title)}"><summary><span class="pl">＋</span><span><b>Add a find</b>
<small>Something you came across. Babybean digs into it, breaks it down, and adds it here.</small></span></summary>
<div class="abd">{pick}<div class="qchips kpick" role="group" aria-label="What is it">{kinds}</div>
<textarea placeholder="Paste the link, or the name of the book or video. Add a note: why it caught your eye."></textarea>
<button type="button" class="sendbtn">Send to Babybean →</button>
<p class="how">Opens Telegram with your find ready to send.</p></div></details>"""


MDLINK = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")


def rich(x):
    """Escape text, then turn [label](url) source citations into small links."""
    return MDLINK.sub(lambda m: f'<a class="cite" href="{m.group(2)}" target="_blank" rel="noopener">{m.group(1)} ↗</a>', e(x))


def ul(items, cls="pts"):
    return f'<ul class="{cls}">' + "".join(f"<li>{rich(x)}</li>" for x in items) + "</ul>"


def acc(sections, start=1, open_first=True):
    out = []
    for i, s in enumerate(sections):
        op = " open" if (i == 0 and open_first) else ""
        out.append(f'<details class="acc"{op}><summary><span class="n">{i + start}</span><span class="st"><b>{e(s["title"])}</b>'
                   f'<small>{len(s["points"])} key points</small></span></summary><div class="bd">{ul(s["points"])}</div></details>')
    return '<div class="accs">' + "".join(out) + "</div>"


def track_page(t, tracks):
    slug = t["slug"]
    res = t.get("resources", [])
    vs = views(t)
    h = [head(t["title"], t["emoji"], slug), topbar(tracks, slug)]
    h.append(f"""<section class="hero"><div class="hero-in">
<a class="crumb" href="index.html">← All tracks</a>
<div class="hemoji">{t["emoji"]}</div><h1>{e(t["title"])}</h1><p class="lede">{e(t["intro"])}</p>
<div class="stats"><span><b>{len(t["sections"]) + len(t.get("deep_sections", []))}</b> topics</span><span><b>{len(res)}</b> sources</span>
<span><b>{sum(1 for r in res if r.get("takeaways"))}</b> broken down</span></div>
<div class="tprog" data-track="{slug}"><div class="bar"><span></span></div><small class="pc"></small></div>
</div></section>""")
    h.append('<nav class="views" aria-label="Views"><div class="views-in">'
             + "".join(f'<a href="#{k}" data-v="{k}"><span>{ic}</span>{n}</a>' for k, ic, n in vs) + "</div></nav>")
    h.append('<main class="wrap">')

    if t.get("system"):
        cards = "".join(f'<div class="sys"><div class="sysh"><span>{ic}</span><b>{n}</b></div>{ul(t["system"].get(k, []))}</div>'
                        for k, ic, n in SYS if t["system"].get(k))
        h.append(f'<section class="view" id="system"><h2>🧭 The system</h2><p class="vsub">The same four questions for every track. Follow the money, then decide.</p><div class="sysgrid">{cards}</div></section>')

    h.append(f'<section class="view" id="understand"><h2>🧠 Understand it</h2><p class="vsub">The basics, in plain words.</p>{acc(t["sections"])}</section>')
    if t.get("deep_sections"):
        h.append(f'<section class="view" id="deep"><h2>🔬 Deep dive</h2><p class="vsub">Past the basics: the evidence, the economics, the misconceptions.</p>'
                 f'{acc(t["deep_sections"], start=1, open_first=False)}</section>')

    checks = "".join(f'<li><label><input type="checkbox" data-ck="{slug}:do:{i}"><span>{rich(x)}</span></label></li>' for i, x in enumerate(t.get("do", [])))
    h.append(f'<section class="view" id="do"><h2>✅ What we actually do</h2><p class="vsub">Tick them off as you go.</p><ul class="checks">{checks}</ul></section>')
    if t.get("ask"):
        h.append(f'<section class="view" id="ask"><h2>❓ Questions to ask</h2><p class="vsub">Screenshot these or read them out.</p>'
                 + '<ol class="asks">' + "".join(f"<li>{rich(x)}</li>" for x in t["ask"]) + "</ol></section>")
    if t.get("watch_out"):
        h.append(f'<section class="view" id="watch"><h2>⚠️ Watch out for</h2><p class="vsub">Myths, traps and red flags.</p>{ul(t["watch_out"], "warns")}</section>')

    types = [k for k in TYPE_IC if any(r.get("type") == k for r in res)]
    h.append(f'<section class="view" id="library"><h2>📚 Library</h2><p class="vsub">{len(res)} sources. Tap a card for the breakdown. Tap ✓ when you\'ve read, watched or been.</p>')
    h.append(addbox(t["title"]))
    h.append('<div class="filt" role="group" aria-label="Filter"><button aria-pressed="true" data-f="all">All</button>'
             + "".join(f'<button aria-pressed="false" data-f="{k}">{TYPE_IC[k]} {TYPE_NAME[k]}</button>' for k in types) + "</div>")
    h.append('<div class="rlist">')
    for i, r in enumerate(res):
        ty = r.get("type", "article")
        key = f"{slug}:r:{r.get('url') or i}"
        tk = r.get("takeaways") or []
        meta = " · ".join(x for x in [r.get("source", ""), str(r.get("year", "") or "")] if x)
        mine = ' mine' if r.get("by") else ""
        h.append(f'<article class="rc{mine}" data-type="{e(ty)}" data-rk="{e(key)}">'
                 f'<div class="rtop"><span class="ric">{TYPE_IC.get(ty, "📰")}</span><div class="rtx"><span class="rty">{e(TYPE_NAME.get(ty, ty).rstrip("s"))}'
                 + (f' · found by {e(r["by"])}' if r.get("by") else "") + f'</span><b>{e(r["title"])}</b><small>{e(meta)}</small></div></div>'
                 f'<p class="rwhy">{e(r.get("why", ""))}</p>'
                 + (f'<details class="brk"><summary>🧠 Breakdown · {len(tk)} key points</summary>{ul(tk)}</details>' if tk else "")
                 + '<div class="racts">'
                 + (f'<a class="op" href="{e(r["url"])}" target="_blank" rel="noopener">Open ↗</a>' if r.get("url") else "")
                 + '<button type="button" class="done">✓ Done</button></div></article>')
    h.append("</div></section></main>")
    h.append(foot())
    return "\n".join(h)


def index_page(tracks):
    h = [head("Home", "📖"), topbar(tracks, "index")]
    total = sum(len(t.get("resources", [])) for t in tracks)
    broken = sum(1 for t in tracks for r in t.get("resources", []) if r.get("takeaways"))
    h.append(f"""<section class="hero home"><div class="hero-in">
<p class="kicker">Sean &amp; Mishka · learning for The Nest</p>
<h1>Know how it works.<br><span class="grad">Then decide for yourselves.</span></h1>
<p class="lede">Every track asks the same four things: who pays, who decides, who profits, and what it means for us. Real sources: regulators, doctors' bodies, the research, the reporting.</p>
<div class="stats"><span><b>{len(tracks)}</b> tracks</span><span><b>{total}</b> sources</span><span><b>{broken}</b> broken down</span></div>
<div class="herobtns"><button type="button" class="sharebtn">💌 Share with Mishka</button><button type="button" class="installbtn" hidden>📲 Install app</button></div>
</div></section>""")
    h.append('<main class="wrap"><div class="tgrid">')
    for t in tracks:
        a, b = HUE.get(t["slug"], ("#FF6B4A", "#7C3AED"))
        vs = "".join(f'<a href="{t["slug"]}.html#{k}">{ic} {n}</a>' for k, ic, n in views(t))
        h.append(f'<div class="tcard" style="--t1:{a};--t2:{b}"><a class="tmain" href="{t["slug"]}.html">'
                 f'<span class="tic">{t["emoji"]}</span><b>{e(t["title"])}</b>'
                 f'<small>{e(t["intro"].split(". ")[0].rstrip("."))}.</small>'
                 f'<span class="tmeta">{len(t.get("resources", []))} sources · {len(t["sections"]) + len(t.get("deep_sections", []))} topics</span>'
                 f'<div class="tprog mini" data-track="{t["slug"]}"><div class="bar"><span></span></div><small class="pc"></small></div></a>'
                 f'<div class="tviews">{vs}</div></div>')
    h.append("</div>")
    h.append(f'<section class="view homeadd"><h2>＋ Your research</h2><p class="vsub">Found something? Send it in and it gets broken down and filed in the right track.</p>{addbox("", tracks)}</section>')
    h.append('<section class="view"><h2>🗺️ Coming next</h2><p class="vsub">AI, and insurance &amp; medical aid as a system. Tell Babybean which one you want first.</p></section>')
    h.append("</main>")
    totals = {t["slug"]: len(t.get("resources", [])) + len(t.get("do", [])) for t in tracks}
    h.append(f"<script>window.LEARN_TOTALS={json.dumps(totals)};</script>")
    h.append(foot())
    return "\n".join(h)


def foot():
    return f"""<footer class="lfoot">Nest Learn helps you ask better questions. It doesn't replace a doctor, bank or advisor.
<br>Sister app: <a href="https://seanmacebo-ux.github.io/nest/">🪺 The Nest</a></footer>
<script src="learn.js?v={V}"></script>
</body>
</html>
"""


def main():
    tracks = load()
    (ROOT / "index.html").write_text(index_page(tracks))
    for t in tracks:
        (ROOT / f'{t["slug"]}.html').write_text(track_page(t, tracks))
    print("built", ["index"] + [t["slug"] for t in tracks])


if __name__ == "__main__":
    main()
