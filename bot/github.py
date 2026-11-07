import xml.etree.ElementTree as ET
from markdownify import markdownify as md
import httpx2 as httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from config import Settings

ATOM_NS = "{http://www.w3.org/2005/Atom}"

_client = httpx.Client(
    timeout=httpx.Timeout(15.0, connect=10.0),
    headers={"User-Agent": "mm-github-bot"},
    follow_redirects=True,
)


@retry(
    wait=wait_exponential(multiplier=1, min=2, max=30),
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError)),
    reraise=True,
)
def _fetch_atom(owner: str, repo: str) -> bytes:
    url = f"https://github.com/{owner}/{repo}/releases.atom"
    resp = _client.get(url)
    resp.raise_for_status()
    return resp.content


def latest_release(owner: str, repo: str) -> dict | None:
    try:
        data = _fetch_atom(owner, repo)
    except Exception as e:
        raise RuntimeError(f"fetch failed: {e}") from e

    try:
        root = ET.fromstring(data)
    except ET.ParseError as e:
        raise RuntimeError(f"invalid XML: {e}") from e

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


def close_client():
    _client.close()