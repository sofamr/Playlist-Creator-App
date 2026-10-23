import re
from typing import Tuple, List
from ytmusicapi import YTMusic
from yt_dlp import YoutubeDL

def extract_playlist_id(url_or_id: str) -> str:
    """Extract playlist ID from a YouTube / YouTube Music URL or return input ID."""
    match = re.search(r"[?&]list=([a-zA-Z0-9_-]+)", url_or_id)
    if match:
        return match.group(1)
    return url_or_id.strip()

def fetch_playlist_tracks(url_or_id: str) -> Tuple[str, List[str]]:
    """
    Fetches the playlist title and a list of song strings ("Title by Artist").
    Tries ytmusicapi first, then falls back to yt-dlp.
    """
    playlist_id = extract_playlist_id(url_or_id)
    tracks: List[str] = []
    playlist_title = "My Playlist"

    # 1. Try ytmusicapi
    try:
        ytm = YTMusic()
        # User playlists often require "VL" prefix in ytmusicapi browseId
        browse_id = playlist_id if playlist_id.startswith("VL") else f"VL{playlist_id}"
        data = ytm.get_playlist(browse_id)
        if data and "tracks" in data:
            playlist_title = data.get("title", playlist_title)
            for item in data.get("tracks", []):
                title = item.get("title")
                artists = ", ".join(a["name"] for a in item.get("artists", [])) if item.get("artists") else "Unknown Artist"
                if title:
                    tracks.append(f"{title} by {artists}")
            if tracks:
                return playlist_title, tracks
    except Exception:
        # Fall through to yt-dlp
        pass

    # 2. Fallback to yt-dlp
    try:
        target_url = url_or_id
        if not (url_or_id.startswith("http://") or url_or_id.startswith("https://")):
            target_url = f"https://www.youtube.com/playlist?list={playlist_id}"

        ydl_opts = {
            "extract_flat": True,
            "quiet": True,
            "skip_download": True,
            "ignoreerrors": True,
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(target_url, download=False)
            if info:
                playlist_title = info.get("title", playlist_title)
                entries = info.get("entries") or []
                for entry in entries:
                    if not entry:
                        continue
                    title = entry.get("title")
                    uploader = entry.get("uploader") or entry.get("artist") or entry.get("channel") or "Unknown Artist"
                    if title:
                        tracks.append(f"{title} by {uploader}")
                if tracks:
                    return playlist_title, tracks
    except Exception as e:
        raise RuntimeError(f"Failed to fetch songs from playlist: {e}")

    if not tracks:
        raise ValueError("No songs could be found in the provided playlist URL.")

    return playlist_title, tracks
