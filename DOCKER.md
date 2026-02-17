# Plex -> Lidarr Sync - Docker Deployment Guide

This image is published on Docker Hub:

```plaintext
tobotec/plex-lidarr-sync:latest
```

## Setup options

* [Option 1 – Standalone Docker (Docker Hub Image)](#-option-1--standalone-docker-docker-hub-image)
* [Option 2 – Docker Swarm Mode (Cluster / Scheduled Job)](#-option-2--docker-swarm-mode-cluster--scheduled-job)

## ⚙️ Configuration

All setup options read the configuration from a `.env` file.  
Create a `.env` file in your working directory:

```env
# Required
PLEX_URL=http://your-plex-server:32400
PLEX_TOKEN=your_token_here
LIDARR_URL=http://your-lidarr-server:8686
LIDARR_API_KEY=your_api_key_here
PLEX_MUSIC_LIBRARY=Music
PLEX_PLAYLIST_NAME="Disliked Albums"
REQUEST_TIMEOUT=10

# Safety
DRY_RUN=false
```

---

## 🐳 Option 1 – Standalone Docker (Docker Hub Image)

The simplest way to run the container using Docker directly.

---

## 📦 Installation

Pull the latest image:

```bash
docker pull tobotec/plex-lidarr-sync:latest
```

---

## ▶️ Manual Run

```bash
docker run --rm \
  --env-file .env \
  tobotec/plex-lidarr-sync:latest
```

The container will execute once and exit.

---

## ⏰ Nightly Automation with Cron

Edit root crontab:

```bash
sudo crontab -e
```

Add a nightly job (runs at 3:00 AM):

```bash
0 4 * * * cd /path-to-plex-lidarr-sync && docker run --rm --env-file .env tobotec/plex-lidarr-sync:latest
```

Update `/path-to-plex-lidarr-sync` to your actual directory.

---

## 📜 Viewing Logs

Since the container runs with `--rm`, logs are visible only during execution.

To persist logs for scheduled runs:

```bash
0 4 * * * cd /path-to-plex-lidarr-sync && docker run --rm --env-file .env tobotec/plex-lidarr-sync:latest >> plex-lidarr-sync.log 2>&1
```

---

## 🔄 Updating

Pull the latest version:

```bash
docker pull tobotec/plex-lidarr-sync:latest
```

---

## 🐳 Option 2 – Docker Swarm Mode (Cluster / Scheduled Job)

Deploy the application as a scheduled service in a Docker Swarm cluster.

---

## 📋 Prerequisites

* Docker Swarm initialized
* `swarm-cronjob` service deployed

---

## 🧱 Initialize Swarm (if needed)

```bash
docker swarm init
```

---

## ⏱ Deploy swarm-cronjob Service

```bash
docker service create \
  --name swarm-cronjob \
  --constraint "node.role==manager" \
  --mount type=bind,source=/var/run/docker.sock,target=/var/run/docker.sock \
  crazymax/swarm-cronjob:latest
```

---

## 📝 Create `docker-swarm-compose.yml`

```yaml
version: "3.8"

services:
  plex-lidarr-sync:
    image: tobotec/plex-lidarr-sync:latest
    environment:
      environment:
      PLEX_URL: ${PLEX_URL}
      PLEX_TOKEN: ${PLEX_TOKEN}
      LIDARR_URL: ${LIDARR_URL}
      LIDARR_API_KEY: ${LIDARR_API_KEY}
      PLEX_MUSIC_LIBRARY: ${PLEX_MUSIC_LIBRARY}
      PLEX_PLAYLIST_NAME: ${PLEX_PLAYLIST_NAME}
      REQUEST_TIMEOUT: ${REQUEST_TIMEOUT}
      DRY_RUN: ${DRY_RUN}
      PYTHONUNBUFFERED: "1"
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
        labels: "service=plex-lidarr-sync"
    deploy:
      mode: replicated
      replicas: 0
      placement:
        constraints:
          - node.role == worker
      labels:
        - "swarm.cronjob.enable=true"
        - "swarm.cronjob.schedule=0 7 * * *"
        - "swarm.cronjob.skip-running=false"
      restart_policy:
        condition: none
```

---

## 🚀 Deploy the Stack

Load your `.env` into the shell:

```bash
export $(grep -v '^#' .env | xargs)
```

Deploy:

```bash
docker stack deploy -c docker-swarm-compose.yml plex-lidarr-sync
```

Verify:

```bash
docker stack services plex-lidarr-sync
```

---

## 🕒 Cron Schedule Examples

Edit the schedule under:

```
swarm.cronjob.schedule=
```

Common patterns:

```
* * * * *    # Every minute
0 * * * *    # Every hour
0 3 * * *    # Daily at 3:00 AM
0 2 * * 0    # Weekly (Sunday 2 AM)
0 0 1 * *    # Monthly (1st at midnight)
```

---

## 📜 Swarm Logs

View service logs:

```bash
docker service logs plex-lidarr-sync
```

Stream logs:

```bash
docker service logs -f plex-lidarr-sync_plex-lidarr-sync
```

Inspect tasks:

```bash
docker stack ps plex-lidarr-sync
```

---

## 🔄 Updating in Swarm

Pull the latest image:

```bash
docker pull tobotec/plex-lidarr-sync:latest
```

Force service update:

```bash
docker service update --force plex-lidarr-sync_plex-lidarr-sync
```

Or redeploy:

```bash
docker stack rm plex-lidarr-sync
docker stack deploy -c docker-swarm-compose.yml plex-lidarr-sync
```

---

## 🛠 Troubleshooting

**Service not running**

```bash
docker service ls | grep swarm-cronjob
docker stack ps plex-lidarr-sync
docker service logs plex-lidarr-sync
```

**Cronjob not firing**

```bash
docker service logs swarm-cronjob
```

Ensure:

* Valid cron syntax
* At least one worker node available
* `replicas: 0` is set
* `restart_policy.condition: none` is set

---

# Summary

| Mode              | Best For                                       |
| ----------------- | ---------------------------------------------- |
| Standalone Docker | Single host, simple cron usage                 |
| Docker Swarm      | Clustered environments, centralized scheduling |

Both modes pull the image directly from Docker Hub and do not require building locally.
