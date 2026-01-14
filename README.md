# Plex → Lidarr Sync

Automatically sync your Plex music ratings and playlists with Lidarr to **remove disliked albums** but also to **block** the album from being re-downloaded.

This Dockerized service is ideal for users who rate music manually in Plex and maintain smart playlists for disliked tracks.

## Features

- Sync albums from Plex based on **ratings** and **smart playlist**.
- Prevent Lidarr from re-downloading deleted albums.
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

### **Option A**: Latest development version (main branch)

```bash
git clone https://github.com/tobus3000/plex-lidarr-sync.git
cd plex-lidarr-sync
```

### **Option B**: Specific release version (stable)

```bash
git clone --branch v1.0.1 https://github.com/tobus3000/plex-lidarr-sync.git
cd plex-lidarr-sync
```

> Replace `v1.0.1` with your desired release tag. See [releases](https://github.com/tobus3000/plex-lidarr-sync/releases) for available versions.

1. Create a `.env` file based on the provided template:

```bash
PLEX_URL=http://plex:32400
PLEX_TOKEN=YOUR_PLEX_TOKEN
LIDARR_URL=http://lidarr:8686
LIDARR_API_KEY=YOUR_LIDARR_API_KEY
PLEX_MUSIC_LIBRARY=Music
PLEX_PLAYLIST_NAME=Disliked Music
REQUEST_TIMEOUT=10
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

You should see output listing albums that would be deleted in Lidarr. Once verified:

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
0 3 * * * cd /path-to-plex-lidarr-sync/plex-lidarr-sync && docker-compose up plex-lidarr-sync
```

- Update the path `/path-to-plex-lidarr-sync/plex-lidarr-sync` to your repository location.
- Logs are saved to /var/log/plex-lidarr-sync.log.

### Viewing Logs

The application outputs logs to the Docker container's STDOUT, which Docker automatically captures and rotates.

**View logs in real-time:**

```bash
docker-compose logs -f plex-lidarr-sync
```

**View last 50 log lines:**

```bash
docker-compose logs --tail=50 plex-lidarr-sync
```

**Log rotation details:**

- Individual log files are limited to **10 MB**
- Docker keeps the **latest 3 rotated files** (~30 MB total)
- Logs are stored in Docker's data directory and automatically rotated

## Plex Smart Playlist Setup

To automate disliked album detection:

1. In Plex, create a Smart Playlist named exactly as `PLEX_PLAYLIST_NAME` (default: Disliked Music).

1. Playlist rules example:

- Album Rating ≤ 2 stars
- Media Type = Music
- Match all rules

1. The container will automatically read this playlist and tag albums in Lidarr.

## Lidarr Setup

No special setup is required.

## Dry-Run Mode

- `DRY_RUN=true` in `.env` mode will only print actions without deleting albums from Lidarr.
- Once verified, set `DRY_RUN=false` for production.

## Updating

To update to a new version:

### **Option A**: Update to latest development version (main branch)

```bash
git pull origin main
```

### **Option B**: Update to specific release version (stable)

```bash
git fetch --tags
git checkout v1.0.1
```

> Replace `v1.0.1` with your desired release tag. See [releases](https://github.com/tobus3000/plex-lidarr-sync/releases) for available versions.

1. Rebuild the Docker image:

```bash
docker-compose build --no-cache
```

1. Test with dry-run mode first:

```bash
DRY_RUN=true docker-compose up plex-lidarr-sync
```

1. Once verified, run with your configured settings:

```bash
docker-compose up plex-lidarr-sync
```

Check [CHANGELOG.md](CHANGELOG.md) for version-specific changes.

## Example Workflow

1. Rate music in Plex manually (1–5 stars).
1. The smart playlist automatically updates with albums rated ≤ 2 stars.
1. Nightly cron runs the container:
   - Reads disliked albums from Plex playlist
   - Deletes them in Lidarr
   - Blocks future downloads

## Contributing

1. Fork the repo
1. Create a feature branch (`git checkout -b feature-name`)
1. Commit changes (`git commit -m 'Add feature'`)
1. Push branch (`git push origin feature-name`)
1. Open a Pull Request
