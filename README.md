# Plex → Lidarr Sync

![Latest Release](https://img.shields.io/github/v/release/tobus3000/plex-lidarr-sync)

Automatically sync your Plex music ratings and playlists with Lidarr to **remove disliked albums** but also to **block** the album from being re-downloaded.

This Dockerized service is ideal for users who rate music manually in Plex and maintain smart playlists for disliked tracks.

## Features

- Sync albums from Plex based on **ratings** and **smart playlist**.
- Prevent Lidarr from re-downloading deleted albums.
- Fully **Dockerized** for Linux hosts.
- Safe-by-default **dry-run mode** before making changes.
- Works with **Plex Pass** users and multiple libraries.
- Can be scheduled nightly via **cron** for automated management.

> Check [CHANGELOG.md](CHANGELOG.md) for version-specific changes.

## Requirements

- Plex Media Server (Plex Pass recommended)
- Lidarr server
- Docker & Docker Compose
- Linux host (cron recommended for scheduling)
- Python 3.12+ (used inside container)
- Manual rating of music in Plex or use of Smart Playlists

## Installation & Usage

See [DOCKER.md](DOCKER.md) for complete setup and deployment instructions, including:

- Standalone Docker Compose setup for local or NAS deployment
- Docker Swarm Mode setup for clustered deployments
- Cronjob scheduling and automation

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
