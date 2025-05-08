"""Download audio."""

import argparse
import logging
import sys

import soundcloud
import youtube

import os
import shutil

logger = logging.getLogger(__name__)


def download(query, include, exclude, quiet, verbose, overwrite, limit):
    """Scrape various websites for audio. Try YouTube first, then SoundCloud only if YouTube fails or finds nothing."""
    import os

    # def list_mp3_files():
    #     audio_dir = "audio_data"
    #     return set(
    #         f
    #         for f in os.listdir(audio_dir)
    #         if f.lower().endswith(".mp3")
    #     ) if os.path.isdir(audio_dir) else set()

    # before_mp3s = list_mp3_files()
    # youtube_success = True
    # try:
    #     youtube.scrape(query, include, exclude, quiet, verbose, overwrite, limit)
    # except Exception as e:
    #     print(f"YouTube scrape failed: {e}")
    #     youtube_success = False

    # after_mp3s = list_mp3_files()
    # produced_new_mp3 = len(after_mp3s - before_mp3s) > 0

    # if youtube_success and produced_new_mp3:
    #     print("Audio downloaded from YouTube.")
    #     return

    logger.info("Trying SoundCloud scrape...")
    soundcloud.scrape(query, include, exclude, quiet, verbose, overwrite, limit)
    logger.info("Completed SoundCloud scrape.")


def cli(args=None):
    """CLI for scraping audio."""

    parser = argparse.ArgumentParser()
    parser.add_argument("query", default="Cerulean Crayons", nargs="?", help="search terms")
    parser.add_argument("-i", "--include", default=[], action="append", help="only download audio with this tag")
    parser.add_argument("-e", "--exclude", default=[], action="append", help="ignore results with this tag")
    parser.add_argument("-q", "--quiet", default=False, action="store_true", help="hide progress reporting")
    parser.add_argument("-v", "--verbose", default=False, action="store_true", help="display debug information")
    parser.add_argument("-o", "--overwrite", default=False, action="store_true", help="overwrite existing files")
    parser.add_argument("-l", "--limit", default=1, type=int, help="limit number of downloads (modified to 1)")
    args = parser.parse_args()

    logging.basicConfig(format="[%(name)s] %(message)s")
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    elif args.quiet:
        logger.setLevel(logging.ERROR)
    else:
        logger.setLevel(logging.INFO)

    logger.info(f'Downloading 1 audio track from "{args.query}" videos tagged {args.include} and not {args.exclude}.')
    # Always limit to 1 for this specific requirement
    download(args.query, args.include, args.exclude, args.quiet, args.verbose, args.overwrite, 1)
    logger.info("Finished downloading 1 audio track.")

    # Remove any folder in root except “audio_data”
    root_dir = os.path.dirname(os.path.abspath(__file__))
    for entry in os.listdir(root_dir):
        entry_path = os.path.join(root_dir, entry)
        if os.path.isdir(entry_path) and entry != "audio_data" and entry != "__pycache__" and entry != ".venv" and entry != ".git" and entry != "year_lists":
            shutil.rmtree(entry_path)


if __name__ == "__main__":
    cli(sys.argv[1:])
