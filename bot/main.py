import asyncio
import logging
import sys
from contextlib import asynccontextmanager

import yaml
from pydantic import ValidationError

from config import Config, Settings
from github import latest_release, close_client as close_github_client
from mattermost import send_webhook, close_client as close_mm_client
from scheduler import run
from state import State


def load_config(path: str) -> Config:
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    try:
        return Config(**raw)
    except ValidationError as e:
        logging.error("Config validation failed: %s", e)
        sys.exit(1)


def setup_logging(level: str):
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


async def amain():
    settings = Settings()
    config = load_config(settings.config_path)

    setup_logging(config.log_level)
    log = logging.getLogger("mm-github-bot")

    repositories = [r.model_dump() for r in config.repositories]

    state = State(config.state_file)

    webhook_url = settings.mm_webhook_url or (
        str(config.mattermost.webhook_url) if config.mattermost else None
    )
    if not webhook_url:
        log.error("Mattermost webhook URL not set (MM_WEBHOOK_URL env or config)")
        sys.exit(1)

    interval = config.check_interval_seconds

    log.info("starting mm-github-bot, interval=%ds, repos=%d", interval, len(repositories))

    try:
        await run(repositories, interval, webhook_url, state, log)
    finally:
        close_github_client()
        close_mm_client()


if __name__ == "__main__":
    asyncio.run(amain())