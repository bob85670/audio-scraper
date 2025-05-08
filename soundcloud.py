"""Search SoundCloud playlists for audio."""

import json
import logging
import os
import string
import sys

import requests
from sclib import SoundcloudAPI, Track
from tqdm import tqdm

logger = logging.getLogger(__name__)


def sanitize(s):
    valid = f"-_.() {string.ascii_letters}{string.digits}"
    return "".join(c for c in s if c in valid)


if "SOUNDCLOUD_API_KEY" in os.environ:
    API_KEY = os.environ["SOUNDCLOUD_API_KEY"]
else:
    API_KEY = "81f430860ad96d8170e3bf1639d4e072"


def scrape(query, include, exclude, quiet, verbose, overwrite, limit):
    """
    Search SoundCloud and download audio from discovered playlists using web scraping.
    Only scrapes the first song from the first (most related) playlist.
    """
    print("[soundcloud] Starting scrape with api")
    client = SoundcloudAPI()

    # Step 1: Search for playlists using SoundCloud search page
    search_url = f"https://soundcloud.com/search/sets?q={requests.utils.quote(query)}"
    resp = requests.get(search_url)
    print("[soundcloud] Fetching search results")
    if not resp.ok:
        logger.error(f"Failed to fetch search results for query: {query}")
        return

    # Step 2: Find playlist URLs in search results (look for '/{user}/sets/{playlist-name}')
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(resp.text, "html.parser")
    playlist_urls = set()
    print("[soundcloud] Found {len(playlist_urls)} playlists")
    for link in soup.find_all("a", href=True):
        href = link["href"]
        # Playlist URLs follow /user/sets/playlist-title
        if href.startswith("/") and "/sets/" in href:
            playlist_urls.add("https://soundcloud.com" + href)
        if len(playlist_urls) >= limit:
            break

    # Step 3: Process only the first playlist that passes filters
    print("[soundcloud] Processing only the first playlist")
    for playlist_url in playlist_urls:
        try:
            playlist = client.resolve(playlist_url)
        except Exception as e:
            if verbose:
                logger.warning(f"Could not resolve: {playlist_url} ({e})")
            continue

        # Apply exclude filter to playlist title/description
        metadata = [playlist.title]
        if getattr(playlist, "description", None):
            metadata.append(playlist.description)
        haystack = " ".join(metadata).lower()
        if any(needle.lower() in haystack for needle in exclude):
            continue

        # Create directory for playlist
        directory = sanitize(playlist.title)
        if not directory:
            continue
        if not os.path.exists(directory):
            os.mkdir(directory)

        # Download only the first track in the playlist
        print("[soundcloud] Downloading only the first track")
        logger.info(f"Downloading {playlist.title}")
        tracks = list(playlist.tracks)
        if tracks:
            track = tracks[0]
            file = os.path.join(directory, sanitize(track.title) + ".mp3")

            # Skip existing files
            if os.path.exists(file) and not overwrite:
                continue

            # Skip tracks that are not allowed to be streamed
            if not getattr(track, "streamable", True):
                continue

            # Skip tracks named with filter terms
            track_haystack = (track.title + " " + getattr(track, "description", "") + " " + getattr(track, "tag_list", "")).lower()
            if any(needle.lower() in track_haystack for needle in exclude):
                continue

                # Download track
                r = requests.get(client.get(track.stream_url, allow_redirects=False).location, stream=True)
                total_size = int(r.headers["content-length"])
                chunk_size = 1000000  # 1 MB chunks
                with open(file, "wb") as f:
                    for data in tqdm(
                        r.iter_content(chunk_size),
                        desc=track.title,
                        total=total_size / chunk_size,
                        unit="MB",
                        file=sys.stdout,
                        disable=quiet,
                    ):
                        f.write(data)
            
            # Break after processing the first valid playlist
            break
