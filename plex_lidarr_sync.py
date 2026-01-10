"""Synchronize disliked albums from Plex to Lidarr.

This script reads a Plex playlist to identify disliked albums and automatically
tags them in Lidarr with a configured tag label. It provides a dry-run mode to
preview changes before applying them, and supports configurable timeouts for API requests.

Environment Variables:
    PLEX_URL: URL of the Plex server (required)
    PLEX_TOKEN: Authentication token for Plex API (required)
    PLEX_MUSIC_LIBRARY: Name of the Plex music library (required)
    PLEX_PLAYLIST_NAME: Name of the Plex playlist containing disliked albums (required)
    LIDARR_URL: URL of the Lidarr server (required)
    LIDARR_API_KEY: Authentication key for Lidarr API (required)
    LIDARR_TAG: Tag label to apply in Lidarr (default: 'plex_disliked')
    REQUEST_TIMEOUT: API request timeout in seconds (default: 10)
    DRY_RUN: Preview changes without applying them (default: 'true')
"""
import os
import sys
import logging
from typing import Any, Dict, Optional
import requests
from plexapi.server import PlexServer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

PLEX_URL = os.getenv("PLEX_URL")
PLEX_TOKEN = os.getenv("PLEX_TOKEN")
LIDARR_URL = os.getenv("LIDARR_URL")
LIDARR_API_KEY = os.getenv("LIDARR_API_KEY")
LIBRARY_NAME = os.getenv("PLEX_MUSIC_LIBRARY")
PLAYLIST_NAME = os.getenv("PLEX_PLAYLIST_NAME")
LIDARR_TAG = os.getenv("LIDARR_TAG", "plex_disliked")
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
            "Missing required environment variables: %s",
            ", ".join(missing_vars)
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
            f"{LIDARR_URL}/api/v1/{endpoint}",
            headers=headers,
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error("Failed to fetch from Lidarr (%s): %s", endpoint, e)
        sys.exit(1)
    except ValueError as e:
        logger.error("Invalid JSON response from Lidarr (%s): %s", endpoint, e)
        sys.exit(1)


def lidarr_post(endpoint: str, payload: Dict[str, Any]) -> requests.Response:
    """Send a POST request to the Lidarr API.
    
    Args:
        endpoint: The API endpoint path (without base URL).
        payload: The JSON payload to send in the request body.
        
    Returns:
        The response object from the API.
        
    Raises:
        SystemExit: If the request fails.
    """
    try:
        response = requests.post(
            f"{LIDARR_URL}/api/v1/{endpoint}",
            json=payload,
            headers=headers,
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        logger.error("Failed to post to Lidarr (%s): %s", endpoint, e)
        sys.exit(1)


def get_or_create_tag() -> Optional[int]:
    """Get or create a tag in Lidarr.
    
    Searches for an existing tag with the configured name. If not found and not in
    dry run mode, creates a new tag.
    
    Returns:
        The tag ID if found or created, None in dry run mode when tag doesn't exist.
    """
    tags = lidarr_get("tag")
    for tag in tags:
        if tag["label"] == LIDARR_TAG:
            logger.info("Found existing tag: %s (ID: %s)", LIDARR_TAG, tag["id"])
            return tag["id"]

    if DRY_RUN:
        logger.info("[DRY RUN] Would create tag: %s", LIDARR_TAG)
        return None

    logger.info("Creating new tag: %s", LIDARR_TAG)
    res = lidarr_post("tag", {"label": LIDARR_TAG})
    tag_id = res.json()["id"]
    logger.info("Created tag: %s (ID: %s)", LIDARR_TAG, tag_id)
    return tag_id


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
        for item in playlist.items():
            if hasattr(item, "parentTitle"):
                disliked_albums.add(item.parentTitle)

        logger.info("Found %d disliked albums in Plex", len(disliked_albums))

        logger.info("Fetching albums from Lidarr")
        lidarr_albums = lidarr_get("album")
        tag_id = get_or_create_tag()

        tagged_count = 0
        for album in lidarr_albums:
            if album["title"] in disliked_albums:
                artist_name = album.get("artist", {}).get("artistName", "Unknown")
                logger.info("Tagging: %s - %s", artist_name, album["title"])

                if DRY_RUN:
                    tagged_count += 1
                    continue

                if tag_id is not None:
                    album["tags"].append(tag_id)
                    lidarr_post("album/editor", {
                        "albumIds": [album["id"]],
                        "tags": album["tags"],
                        "applyTags": "add"
                    })
                    tagged_count += 1

        logger.info("Sync complete. Tagged %d albums", tagged_count)

    except (requests.exceptions.RequestException,
            ConnectionError,
            TimeoutError,
            ValueError,
            KeyError,
            AttributeError) as e:
        logger.error("Sync failed: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
