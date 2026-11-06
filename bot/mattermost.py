import json
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


def send_webhook(webhook_url: str, payload: dict) -> bool:
    data = json.dumps(payload).encode("utf-8")
    req = Request(
        webhook_url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(req, timeout=15) as resp:
            return resp.status == 200
    except (URLError, HTTPError) as e:
        print(f"Mattermost webhook error: {e}")
        return False
