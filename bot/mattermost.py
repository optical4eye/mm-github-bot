import json
import httpx2 as httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

_client = httpx.Client(
    timeout=httpx.Timeout(15.0, connect=10.0),
    headers={"Content-Type": "application/json"},
)


@retry(
    wait=wait_exponential(multiplier=1, min=2, max=30),
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError)),
    reraise=True,
)
def send_webhook(webhook_url: str, payload: dict) -> bool:
    resp = _client.post(webhook_url, json=payload)
    resp.raise_for_status()
    return True


def close_client():
    _client.close()