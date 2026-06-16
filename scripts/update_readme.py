#!/usr/bin/env python3
"""GitHub リポジトリ一覧を取得して README.md を更新するスクリプト。"""
import os
import json
import urllib.request
from datetime import datetime, timezone

TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")

if not TOKEN:
    raise RuntimeError("GH_TOKEN が設定されていません")

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "X-GitHub-Api-Version": "2022-11-28",
}


def fetch_repos() -> list[dict]:
    repos: list[dict] = []
    page = 1
    while True:
        url = (
            f"https://api.github.com/user/repos"
            f"?per_page=100&page={page}&type=owner&sort=updated"
        )
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req) as resp:
            data: list[dict] = json.loads(resp.read())
        if not data:
            break
        repos.extend(r for r in data if not r["archived"])
        if len(data) < 100:
            break
        page += 1
    return repos


def build_readme(repos: list[dict]) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    rows = []
    for i, repo in enumerate(repos, 1):
        visibility = "🔒" if repo["private"] else "🌐"
        name = f"[{repo['name']}]({repo['html_url']})"
        desc = (repo.get("description") or "").replace("|", "\\|")
        lang = repo.get("language") or ""
        updated = repo["updated_at"][:10]
        rows.append(f"| {i} | {visibility} {name} | {desc} | {lang} | {updated} |")

    table = "\n".join(rows)
    return (
        "# My GitHub Repositories\n"
        "\n"
        f"> 最終更新: {now}　｜　アーカイブ済みリポジトリを除く\n"
        "\n"
        "| # | リポジトリ | 概要 | 言語 | 更新日 |\n"
        "|---|---|---|---|---|\n"
        f"{table}\n"
        "\n"
        "---\n"
        "*このファイルは [GitHub Actions](../../actions) により毎週月曜日に自動更新されます。*\n"
    )


if __name__ == "__main__":
    repos = fetch_repos()
    print(f"取得: {len(repos)} 件（アーカイブ除外済み）")
    readme = build_readme(repos)
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme)
    print("README.md を更新しました")
