#!/usr/bin/env python3
"""Merge a Codex deep-dive (/tmp/learn/codex/<slug>.json) into tracks/<slug>.json.

Every NEW url is opened with the stealth browser (browser-kit) first; anything that
doesn't load (error, 404 page, blocked) is dropped and listed. Usage: python3 merge_codex.py <slug>
"""
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).parent
BK = [str(Path.home() / "Workspace/browser-kit/.venv/bin/python3"), str(Path.home() / "Workspace/browser-kit/browser.py")]
BAD = ("page not found", "404 not found", "this page doesn't exist", "page could not be found", "no longer available")


def check(url):
    for engine in ([], ["--engine", "chrome"]):
        try:
            out = subprocess.run(BK + ["extract", url, "--format", "json", "--timeout", "30"] + engine,
                                 capture_output=True, text=True, timeout=75).stdout
            d = json.loads(out)
        except Exception:
            continue
        txt = (d.get("content") or "")[:4000].lower()
        title = (d.get("title") or "").lower()
        if d.get("ok") and not (d.get("block_signal") or {}).get("blocked") and len(txt) > 200 and not any(b in title or b in txt[:600] for b in BAD):
            return True, d.get("title", "")
    # fallback for PDFs and pages the stealth browser can't render: plain HTTP check (flagged)
    try:
        r = subprocess.run(["curl", "-sL", "-o", "/dev/null", "-w", "%{http_code} %{content_type}", "-A", "Mozilla/5.0", "--max-time", "30", url],
                           capture_output=True, text=True, timeout=40).stdout.split(" ", 1)
        if r[0] == "200":
            return True, "curl:" + (r[1] if len(r) > 1 else "")
    except Exception:
        pass
    return False, ""


def main(slug):
    tp, cp = ROOT / "tracks" / f"{slug}.json", Path(f"/tmp/learn/codex/{slug}.json")
    t, c = json.loads(tp.read_text()), json.loads(cp.read_text())
    if c.get("system"):
        t["system"] = c["system"]
    if c.get("deep_sections"):
        t["deep_sections"] = c["deep_sections"]
    for x in c.get("existing_takeaways", []):
        i = x.get("i")
        if isinstance(i, int) and 0 <= i < len(t["resources"]) and x.get("takeaways"):
            t["resources"][i]["takeaways"] = x["takeaways"]
    have = {r.get("url", "").rstrip("/") for r in t["resources"]}
    new = [r for r in c.get("resources", []) if r.get("url") and r["url"].rstrip("/") not in have]
    with ThreadPoolExecutor(max_workers=6) as ex:
        results = list(ex.map(lambda r: check(r["url"]), new))
    kept, dropped = [], []
    for r, (ok, title) in zip(new, results):
        (kept if ok else dropped).append(r)
    for r, (ok, title) in zip(new, results):
        if ok and title.startswith("curl:"):
            r["checked_by"] = "curl"
    for r in kept:
        r["verified"] = True
        r["new"] = True
    t["resources"].extend(kept)
    tp.write_text(json.dumps(t, ensure_ascii=False, indent=1))
    print(json.dumps({"slug": slug, "added": len(kept), "dropped": [d["url"] for d in dropped],
                      "existing_broken_down": sum(1 for r in t["resources"] if r.get("takeaways")), "total": len(t["resources"])}))


if __name__ == "__main__":
    main(sys.argv[1])
