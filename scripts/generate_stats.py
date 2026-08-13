import json
import os
import urllib.request
from pathlib import Path

USER = "raviranjanroy01"
TOKEN = os.environ.get("GITHUB_TOKEN", "")
HEADERS = {"Accept": "application/vnd.github+json", "User-Agent": "profile-stats"}
if TOKEN:
    HEADERS["Authorization"] = f"Bearer {TOKEN}"

def get(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

u = get(f"https://api.github.com/users/{USER}")
repos = get(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner")
stars = sum(r.get("stargazers_count", 0) for r in repos)
forks = sum(r.get("forks_count", 0) for r in repos)
langs = {}
for r in repos:
    if r.get("fork"):
        continue
    try:
        data = get(r["languages_url"])
        for k, v in data.items():
            langs[k] = langs.get(k, 0) + v
    except Exception:
        pass
langs = sorted(langs.items(), key=lambda x: x[1], reverse=True)[:5]
total = sum(v for _, v in langs) or 1
colors = ["#00ADB5", "#3776AB", "#F7DF1E", "#A855F7", "#22C55E"]

def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def compact(n):
    return f"{n/1000:.1f}k" if n >= 1000 else str(n)

svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="420" viewBox="0 0 900 420"><rect width="900" height="420" rx="18" fill="#0d1117" stroke="#30363d"/><text x="40" y="48" fill="#f0f6fc" font-family="Arial" font-size="24" font-weight="700">GitHub Statistics</text><text x="40" y="72" fill="#8b949e" font-family="Arial" font-size="13">Automatically generated from the GitHub API</text>'''

cards = [(40, "Repositories", u.get("public_repos", 0)), (260, "Followers", u.get("followers", 0)), (480, "Stars", compact(stars)), (700, "Forks", compact(forks))]
for x, label, value in cards:
    svg += f'<rect x="{x}" y="100" width="180" height="90" rx="12" fill="#161b22" stroke="#30363d"/><text x="{x+18}" y="128" fill="#8b949e" font-family="Arial" font-size="13">{esc(label)}</text><text x="{x+18}" y="168" fill="#f0f6fc" font-family="Arial" font-size="28" font-weight="700">{esc(value)}</text>'

svg += '<text x="40" y="235" fill="#f0f6fc" font-family="Arial" font-size="19" font-weight="700">Top Languages</text>'
y = 270
for i, (name, value) in enumerate(langs):
    pct = value / total * 100
    width = max(12, pct * 5.5)
    svg += f'<text x="40" y="{y}" fill="#c9d1d9" font-family="Arial" font-size="14">{esc(name)}</text><rect x="170" y="{y-12}" width="540" height="14" rx="7" fill="#21262d"/><rect x="170" y="{y-12}" width="{width:.1f}" height="14" rx="7" fill="{colors[i % len(colors)]}"/><text x="735" y="{y}" fill="#c9d1d9" font-family="Arial" font-size="14">{pct:.1f}%</text>'
    y += 30

svg += '</svg>\n'
Path("assets").mkdir(exist_ok=True)
Path("assets/github-stats.svg").write_text(svg, encoding="utf-8")
