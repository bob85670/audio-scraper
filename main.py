"""Download audio."""

import logging
import sys
import soundcloud
import youtube
import os
import shutil

logger = logging.getLogger(__name__)

def download(query):
    """Scrape various websites for audio. Try YouTube first, then SoundCloud only if YouTube fails or finds nothing."""
    def list_mp3_files():
        audio_dir = "audio_data"
        return set(
            f
            for f in os.listdir(audio_dir)
            if f.lower().endswith(".mp3")
        ) if os.path.isdir(audio_dir) else set()

    before_mp3s = list_mp3_files()
    youtube_success = True
    try:
        youtube.scrape(query)
    except Exception as e:
        print(f"YouTube scrape failed: {e}")
        youtube_success = False

    after_mp3s = list_mp3_files()
    produced_new_mp3 = len(after_mp3s - before_mp3s) > 0

    if youtube_success and produced_new_mp3:
        print("Audio downloaded from YouTube.")
        return

    logger.info("Trying SoundCloud scrape...")
    soundcloud.scrape(query)
    logger.info("Completed SoundCloud scrape.")


if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "Cerulean Crayons"
    download(query)
    logger.info("Finished downloading 1 audio track.")

    # Remove any folder in root except “audio_data”, “__pycache__”, “.venv”, “.git”, and “year_lists”
    root_dir = os.path.dirname(os.path.abspath(__file__))
    for entry in os.listdir(root_dir):
        entry_path = os.path.join(root_dir, entry)
        if os.path.isdir(entry_path) and entry not in ["audio_data", "__pycache__", ".venv", ".git", "year_lists"]:
            shutil.rmtree(entry_path)
