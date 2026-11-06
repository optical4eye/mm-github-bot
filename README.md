# mm-github-bot

A bot that monitors GitHub releases for configured repositories and posts notifications to Mattermost via an incoming webhook.

## Features

- Polls the GitHub releases Atom feed for each configured repository
- Detects new releases by comparing against a persisted state file
- Posts a formatted message (repository, version, link, changelog) to Mattermost
- Runs as a long-running loop with a configurable check interval
- Runs standalone with Docker Compose or on Kubernetes via Helm chart

## Project structure

```
mm-github-bot/
├── bot/                 # Python bot application
│   ├── main.py          # Entry point: loads config and starts the scheduler
│   ├── github.py        # Fetches latest release from GitHub releases.atom
│   ├── mattermost.py    # Sends POST to Mattermost incoming webhook
│   ├── scheduler.py     # Polling loop: checks versions and sends notifications
│   ├── state.py         # JSON persistence of the last sent version per repository
│   ├── config.yaml      # Example configuration
│   ├── state.json       # Persisted state (last versions per repo)
│   ├── Dockerfile       # Python 3.15-slim based image
│   └── requirements.txt # PyYAML, markdownify
├── helm/                # Helm chart for Kubernetes deployment
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
│       ├── deployment.yaml
│       ├── configmap.yaml
│       ├── secret.yaml
│       ├── pvc.yaml
│       └── _helpers.tpl
├── docker-compose.yml   # Local stack: Postgres + Mattermost + bot
└── README.md
```

## Quick start (Docker Compose)

The `docker-compose.yml` spins up Postgres, Mattermost, and the bot:

```bash
docker-compose up -d
```

Configure the bot in `bot/config.yaml` before starting:

```yaml
repositories:
  - owner: openbao
    repo: openbao
  - owner: hashicorp
    repo: terraform

check_interval_seconds: 3600

mattermost:
  webhook_url: http://mattermost:8065/hooks/your-webhook-url

state_file: /data/state.json
log_level: INFO
```

Then run the bot standalone:

```bash
docker build -t mm-github-bot ./bot
docker run --rm \
  -e CONFIG_PATH=/app/config.yaml \
  -e MM_WEBHOOK_URL=http://mattermost:8065/hooks/your-webhook-url \
  -v $(pwd)/bot/config.yaml:/app/config.yaml:ro \
  -v $(pwd)/bot/state.json:/data/state.json \
  mm-github-bot
```

## Configuration

| Field | Description | Default |
|-------|-------------|---------|
| `repositories` | List of `{owner, repo}` to monitor | required |
| `check_interval_seconds` | Polling interval in seconds | `3600` |
| `mattermost.webhook_url` | Mattermost incoming webhook URL | from `MM_WEBHOOK_URL` env |
| `state_file` | Path to JSON state file | `/data/state.json` |
| `log_level` | Python logging level | `INFO` |

The webhook URL can also be provided via the `MM_WEBHOOK_URL` environment variable, which takes precedence over the config file.

## Kubernetes (Helm)

Install the Helm chart:

```bash
helm install mm-github-bot ./helm
```

Key `values.yaml` options:

```yaml
replicaCount: 1

image:
  repository: local_mm-bot
  pullPolicy: IfNotPresent
  tag: "latest"

mattermostWebhookUrl: ""  # creates a Secret automatically when set

repositories:
  - owner: openbao
    repo: openbao

checkIntervalSeconds: 3600
logLevel: INFO

state:
  enabled: true
  size: 1Gi
  storageClassName: ""
  accessMode: ReadWriteOnce
```

The chart creates a Deployment, ConfigMap (bot config), optional Secret (webhook URL), and optional PersistentVolumeClaim (state file).

## How it works

1. `main.py` loads `config.yaml`, validates repositories, and starts the async scheduler.
2. `scheduler.run()` loops forever, fetching the latest release from `https://github.com/{owner}/{repo}/releases.atom` for each repository.
3. If the release version differs from the value stored in `state.json`, a message is posted to Mattermost via `mattermost.send_webhook()` and the new version is saved to state.
4. On error fetching a release, the error is logged and the bot continues with the next repository.

Notification messages are in Russian, e.g.:

```
*Новый релиз:* `openbao/openbao`
Версия: *v2.7.2*
Ссылка: https://github.com/openbao/openbao/releases/tag/v2.7.2

*Описание:*
...
```

## Requirements

- Python 3.15+
- PyYAML==6.0.3
- markdownify==1.2.3

## License

MIT