import xml.etree.ElementTree as ET
from markdownify import markdownify as md
from urllib.request import Request, urlopen

ATOM_NS = "{http://www.w3.org/2005/Atom}"


def latest_release(owner: str, repo: str) -> dict | None:
    url = f"https://github.com/{owner}/{repo}/releases.atom"
    req = Request(url, headers={"User-Agent": "mm-github-bot"})
    with urlopen(req, timeout=15) as resp:
        data = resp.read()

    root = ET.fromstring(data)
    entry = root.find(f"{ATOM_NS}entry")
    if entry is None:
        return None

    title_el = entry.find(f"{ATOM_NS}title")
    link_el = entry.find(f"{ATOM_NS}link")
    updated_el = entry.find(f"{ATOM_NS}updated")
    id_el = entry.find(f"{ATOM_NS}id")
    content_el = entry.find(f"{ATOM_NS}content")

    version = title_el.text.strip() if title_el is not None and title_el.text else None
    link = link_el.get("href") if link_el is not None else None
    updated = updated_el.text if updated_el is not None else None
    release_id = id_el.text if id_el is not None else None
    changelog = md(content_el.text) if content_el is not None and content_el.text else None

    return {
        "version": version,
        "link": link,
        "updated": updated,
        "id": release_id,
        "changelog": changelog,
    }
