import asyncio
import logging

from github import latest_release
from mattermost import send_webhook
from state import State


async def run(repositories, interval, webhook_url, state: State, log: logging.Logger):
    while True:
        for repo in repositories:
            key = f"{repo['owner']}/{repo['repo']}"
            try:
                release = latest_release(repo["owner"], repo["repo"])
            except Exception as e:
                log.error("[%s] fetch error: %s", key, e)
                continue
            if release is None:
                log.warning("[%s] no release found", key)
                continue

            version = release["version"]
            last = state.get(key)
            if last == version:
                log.debug("[%s] already sent %s", key, version)
                continue

            changelog = release.get("changelog") or ""

            text = (
                f"New release: `{key}`\n"
                f"Version: {version}\n"
                f"Link: {release['link']}\n"
            )
            if changelog:
                text += f"\nChangelog:\n{changelog}"
            payload = {"text": text}

            try:
                ok = send_webhook(webhook_url, payload)
            except Exception as e:
                log.error("[%s] webhook failed after retries: %s", key, e)
                ok = False

            if ok:
                state.set(key, version)
                log.info("[%s] sent %s", key, version)
            else:
                log.error("[%s] failed to send %s", key, version)

        await asyncio.sleep(interval)