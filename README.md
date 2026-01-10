# Plex → Lidarr Sync

Automatically sync your Plex music ratings and playlists with Lidarr to **tag, block, and optionally remove disliked albums**. This Dockerized service is ideal for users who rate music manually in Plex or maintain smart playlists for disliked tracks.

## Features

- Sync albums from Plex based on **ratings** or **smart playlists**.
- Automatically add a **Lidarr tag** to disliked albums.
- Optionally prevent Lidarr from re-downloading tagged albums.
- Fully **Dockerized** for Linux hosts.
- Safe-by-default **dry-run mode** before making changes.
- Works with **Plex Pass** users and multiple libraries.
- Can be scheduled nightly via **cron** for automated management.

## Requirements

- Plex Media Server (Plex Pass recommended)
- Lidarr server
- Docker & Docker Compose
- Linux host (cron recommended for scheduling)
- Python 3.12+ (used inside container)
- Manual rating of music in Plex or use of Smart Playlists

## Installation

1. Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/plex-lidarr-sync.git
cd plex-lidarr-sync
```

1. Create a `.env` file based on the provided template:

```bash
PLEX_URL=http://plex:32400
PLEX_TOKEN=YOUR_PLEX_TOKEN
LIDARR_URL=http://lidarr:8686
LIDARR_API_KEY=YOUR_LIDARR_API_KEY
PLEX_MUSIC_LIBRARY=Music
PLEX_PLAYLIST_NAME=Disliked Music
RATING_THRESHOLD=2
LIDARR_TAG=plex_disliked
REQUEST_TIMEOUT=15
DRY_RUN=true
```

> Tip: Keep `DRY_RUN=true` for your first run to preview actions without modifying Lidarr.

1. Build the Docker container:

```bash
docker-compose build
```

## Usage

### Manual run

```bash
docker-compose up plex-lidarr-sync
```

You should see output listing albums that would be tagged in Lidarr. Once verified:

```bash
# Disable dry-run
sed -i 's/DRY_RUN=true/DRY_RUN=false/' .env
docker-compose up plex-lidarr-sync
```

### Nightly automation with cron

1. Open root crontab:

```bash
sudo crontab -e
```

1. Add a nightly job (runs at 3:00 AM):

```cron
0 3 * * * cd /path-to-plex-lidarr-sync/plex-lidarr-sync && docker-compose up plex-lidarr-sync >> /var/log/plex-lidarr-sync.log 2>&1
```

- Update the path `/path-to-plex-lidarr-sync/plex-lidarr-sync` to your repository location.
- Logs are saved to /var/log/plex-lidarr-sync.log.

## Plex Smart Playlist Setup

To automate disliked album detection:

1. In Plex, create a Smart Playlist named exactly as `PLEX_PLAYLIST_NAME` (default: Disliked Music).

1. Playlist rules example:

- Album Rating ≤ 2 stars
- Media Type = Music
- Match all rules

1. The container will automatically read this playlist and tag albums in Lidarr.

## Lidarr Setup

1. Create or let the script create a tag (default: plex_disliked).

1. Update Lidarr profiles:

- Enable Do not download tagged albums.
- Enable Do not upgrade tagged albums (optional).

1. Optional: Use Lidarr Album Editor → Delete Files to remove tagged albums automatically.

## Docker-Compose Example

```yaml
version: "3.8"

services:
  plex-lidarr-sync:
    build: .
    container_name: plex-lidarr-sync
    env_file:
      - .env
    restart: "no"
```

> Container exits after each run; scheduling handled via cron.

## Dry-Run Mode

- `DRY_RUN=true` in `.env` mode will only print actions without tagging or modifying Lidarr.
- Once verified, set `DRY_RUN=false` for production.

## Example Workflow

1. Rate music in Plex manually (1–5 stars).
1. The smart playlist automatically updates with albums rated ≤ 2 stars.
1. Nightly cron runs the container:
   - inds disliked albums in Plex
   - Tags them in Lidarr
   - Blocks future downloads

1. Optional: Manually or automatically remove tagged albums via Lidarr.

## Contributing

1. Fork the repo
1. Create a feature branch (`git checkout -b feature-name`)
1. Commit changes (`git commit -m 'Add feature'`)
1. Push branch (`git push origin feature-name`)
1. Open a Pull Request
