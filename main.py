"""Download audio."""

import logging
import sys
import soundcloud
import youtube
import os
import shutil

logger = logging.getLogger(__name__)

def download(query, output_dir=None):
    """Scrape various websites for audio. Try YouTube first, then SoundCloud only if YouTube fails or finds nothing."""
    def list_mp3_files(audio_dir):
        return set(
            f
            for f in os.listdir(audio_dir)
            if f.lower().endswith(".mp3")
        ) if os.path.isdir(audio_dir) else set()

    audio_dir = output_dir if output_dir else "audio_data"
    before_mp3s = list_mp3_files(audio_dir)
    youtube_success = True
    try:
        youtube.scrape(query, output_dir=audio_dir)
    except Exception as e:
        print(f"YouTube scrape failed: {e}")
        youtube_success = False

    after_mp3s = list_mp3_files(audio_dir)
    produced_new_mp3 = len(after_mp3s - before_mp3s) > 0

    if youtube_success and produced_new_mp3:
        print("Audio downloaded from YouTube.")
        return

    logger.info("Trying SoundCloud scrape...")
    soundcloud.scrape(query, output_dir=audio_dir)
    logger.info("Completed SoundCloud scrape.")


import glob
import json

def scrape_all_years():
    """Iterate over year_lists JSONs, scrape/download each song, and store mp3s in the audio_data/<year>/ folder."""
    yearlists_dir = "year_lists"
    for json_path in glob.glob(os.path.join(yearlists_dir, "*_songs.json")):
        base = os.path.basename(json_path)
        try:
            year = base.split("_")[0]
            with open(json_path, "r", encoding="utf-8") as f:
                songlist = json.load(f)
            for entry in songlist:
                if not isinstance(entry, list) or len(entry) != 2:
                    logger.warning(f"Skipping malformed entry in {json_path}: {entry}")
                    continue
                artist, title = entry
                # Remove single quotes from title if present
                clean_title = title.strip("'").strip('"')
                query = f"{artist} {clean_title}"
                print(f"Scraping: {query} into audio_data/{year}/")
                download(query, output_dir=os.path.join("audio_data", year))
        except Exception as e:
            logger.error(f"Error processing {json_path}: {e}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Audio scraper")
    parser.add_argument("--all-years", action="store_true", help="Process all year_lists/*.json files and download songs.")
    parser.add_argument("query", nargs="?", default=None, help="Single audio query to download (artist and song name).")
    args = parser.parse_args()

    if args.all_years:
        scrape_all_years()
        logger.info("Finished downloading all year audio tracks.")
    elif args.query:
        download(args.query)
        logger.info("Finished downloading 1 audio track.")
    else:
        print("Provide a query or --all-years for batch mode.")

    # Remove any folder in root except “audio_data”, “__pycache__”, “.venv”, “.git”, and “year_lists”
    root_dir = os.path.dirname(os.path.abspath(__file__))
    for entry in os.listdir(root_dir):
        entry_path = os.path.join(root_dir, entry)
        if os.path.isdir(entry_path) and entry not in ["audio_data", "__pycache__", ".venv", ".git", "year_lists"]:
            shutil.rmtree(entry_path)
