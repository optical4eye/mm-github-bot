import asyncio
import logging
import os
import sys

import yaml

from scheduler import run
from state import State


def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


async def amain():
    config_path = os.getenv("CONFIG_PATH", "/app/config.yaml")
    config = load_config(config_path)

    logging.basicConfig(
        level=getattr(logging, config.get("log_level", "INFO").upper()),
        format="%(asctime)s %(levelname)s %(message)s",
    )

    repositories = config.get("repositories")
    if not isinstance(repositories, list) or not repositories:
        print("ERROR: 'repositories' must be a non-empty list in config", file=sys.stderr)
        sys.exit(1)

    for repo in repositories:
        if not repo.get("owner") or not repo.get("repo"):
            print(f"ERROR: repository missing owner/repo: {repo}", file=sys.stderr)
            sys.exit(1)

    state = State(config.get("state_file", "/data/state.json"))
    webhook_url = os.getenv("MM_WEBHOOK_URL") or config["mattermost"]["webhook_url"]
    interval = int(config.get("check_interval_seconds", 3600))

    await run(repositories, interval, webhook_url, state)


if __name__ == "__main__":
    asyncio.run(amain())
