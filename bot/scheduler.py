import asyncio

from github import latest_release
from mattermost import send_webhook
from state import State


async def run(repositories, interval, webhook_url, state: State):
    while True:
        for repo in repositories:
            key = f"{repo['owner']}/{repo['repo']}"
            try:
                release = latest_release(repo["owner"], repo["repo"])
            except Exception as e:
                print(f"[{key}] fetch error: {e}")
                continue
            if release is None:
                print(f"[{key}] no release found")
                continue

            version = release["version"]
            last = state.get(key)
            if last == version:
                print(f"[{key}] already sent {version}")
                continue

            changelog = release.get("changelog") or ""

            text = (
                f"*Новый релиз:* `{key}`\n"
                f"Версия: *{version}*\n"
                f"Ссылка: {release['link']}\n"
            )
            if changelog:
                text += f"\n*Описание:*\n{changelog}"
            payload = {"text": text}
            ok = send_webhook(webhook_url, payload)
            if ok:
                state.set(key, version)
                print(f"[{key}] sent {version}")
            else:
                print(f"[{key}] failed to send {version}")

        await asyncio.sleep(interval)
