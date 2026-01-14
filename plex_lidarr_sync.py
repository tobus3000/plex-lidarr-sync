"""Synchronize disliked albums from Plex to Lidarr.

This script reads a Plex playlist to identify disliked albums and automatically
deletes them and adds them to the blocklist to prevent them from being re-downloaded in Lidarr.
It provides a dry-run mode to preview changes before applying them, and supports configurable
timeouts for API requests.

Environment Variables:
    PLEX_URL: URL of the Plex server (required)
    PLEX_TOKEN: Authentication token for Plex API (required)
    PLEX_MUSIC_LIBRARY: Name of the Plex music library (required)
    PLEX_PLAYLIST_NAME: Name of the Plex playlist containing disliked albums (required)
    LIDARR_URL: URL of the Lidarr server (required)
    LIDARR_API_KEY: Authentication key for Lidarr API (required)
    REQUEST_TIMEOUT: API request timeout in seconds (default: 10)
    DRY_RUN: Preview changes without applying them (default: 'true')
"""

import os
import sys
import logging
from typing import Any
import requests
from plexapi.server import PlexServer

# Configure logging to output to console (STDOUT)
# Docker's logging driver automatically captures and manages log rotation
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Load configuration from environment variables
PLEX_URL = os.getenv("PLEX_URL")
PLEX_TOKEN = os.getenv("PLEX_TOKEN")
LIDARR_URL = os.getenv("LIDARR_URL")
LIDARR_API_KEY = os.getenv("LIDARR_API_KEY")
LIBRARY_NAME = os.getenv("PLEX_MUSIC_LIBRARY")
PLAYLIST_NAME = os.getenv("PLEX_PLAYLIST_NAME")
DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "10"))

headers = {"X-Api-Key": LIDARR_API_KEY}


def validate_config() -> None:
    """Validate that all required environment variables are set.

    Raises:
        SystemExit: If any required environment variable is missing.
    """
    required_vars = {
        "PLEX_URL": PLEX_URL,
        "PLEX_TOKEN": PLEX_TOKEN,
        "PLEX_MUSIC_LIBRARY": LIBRARY_NAME,
        "PLEX_PLAYLIST_NAME": PLAYLIST_NAME,
        "LIDARR_URL": LIDARR_URL,
        "LIDARR_API_KEY": LIDARR_API_KEY,
    }

    missing_vars = [name for name, value in required_vars.items() if not value]
    if missing_vars:
        logger.error(
            "Missing required environment variables: %s", ", ".join(missing_vars)
        )
        sys.exit(1)


def lidarr_get(endpoint: str) -> Any:
    """Fetch data from Lidarr API.

    Args:
        endpoint: The API endpoint path (without base URL).

    Returns:
        The JSON response from the API.

    Raises:
        SystemExit: If the request fails or returns invalid JSON.
    """
    try:
        response = requests.get(
            f"{LIDARR_URL}/api/v1/{endpoint}", headers=headers, timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error("Failed to GET from Lidarr (%s): %s", endpoint, e)
        sys.exit(1)
    except ValueError as e:
        logger.error("Invalid JSON response from Lidarr (%s): %s", endpoint, e)
        sys.exit(1)


def lidarr_delete(endpoint: str) -> requests.Response:
    """Send a DELETE request to the Lidarr API.

    Args:
        endpoint: The API endpoint path (without base URL).

    Returns:
        The response object from the API.

    Raises:
        SystemExit: If the request fails.
    """
    try:
        response = requests.delete(
            f"{LIDARR_URL}/api/v1/{endpoint}", headers=headers, timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        logger.error("Failed to DELETE from Lidarr (%s): %s", endpoint, e)
        sys.exit(1)


def main() -> None:
    """Synchronize disliked albums from Plex to Lidarr.

    Reads a Plex playlist to identify disliked albums and tags them in Lidarr
    with a configured tag. Supports dry run mode for preview without making changes.
    """
    validate_config()

    if DRY_RUN:
        logger.info("DRY RUN MODE ENABLED - No changes will be made to Lidarr")

    try:
        logger.info("Connecting to Plex server at %s", PLEX_URL)
        plex = PlexServer(PLEX_URL, PLEX_TOKEN)

        logger.info("Loading Plex playlist: %s", PLAYLIST_NAME)
        playlist = plex.playlist(PLAYLIST_NAME)

        disliked_albums = set()
        if playlist:
            for item in playlist.items():
                if hasattr(item, "parentTitle"):
                    disliked_albums.add(item.parentTitle)

        logger.info("Found %d disliked albums in Plex", len(disliked_albums))

        logger.info("Fetching albums from Lidarr")
        lidarr_albums = lidarr_get("album")

        delete_count = 0
        for album in lidarr_albums:
            if album["title"] in disliked_albums:
                artist_name = album.get("artist", {}).get("artistName", "Unknown")

                if DRY_RUN:
                    logger.info(
                        "Skipping delete due to dry-run: %s - %s",
                        artist_name,
                        album["title"],
                    )
                    delete_count += 1
                    continue

                logger.info(
                    "Deleting album in Lidarr: %s - %s", artist_name, album["title"]
                )
                lidarr_delete(
                    f"album/{album['id']}?deleteFiles=true&addImportListExclusion=true"
                )
                delete_count += 1

        logger.info("Sync complete. Deleted %d albums", delete_count)

    except (
        requests.exceptions.RequestException,
        ConnectionError,
        TimeoutError,
        ValueError,
        KeyError,
        AttributeError,
    ) as e:
        logger.error("Sync failed: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
