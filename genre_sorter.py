import json
import time
from typing import List
from google import genai
from google.genai import types
from models import Playlist

def sort_by_genre(
    client: genai.Client,
    tracks: List[str],
    min_songs: int,
    max_songs: int,
    model_name: str = "gemini-3.8-flash"
) -> List[Playlist]:
    """
    Uses Gemini AI to organize a list of songs into genre-based mini playlists,
    strictly respecting min_songs and max_songs constraints per playlist.
    """
    if not tracks:
        return []

    # If the total number of songs is less than min_songs, we can only create 1 combined playlist
    if len(tracks) < min_songs:
        print(f"[Notice] Total songs ({len(tracks)}) is less than min_songs ({min_songs}). Creating a single playlist.")
        p = Playlist(name="Assorted Genres", songs=tracks)
        return [p]

    formatted_song_list = "\n".join(f"{i+1}. {song}" for i, song in enumerate(tracks))

    prompt = f"""You are an expert music curator and DJ.
Your job is to cluster the following {len(tracks)} songs into distinct, coherent genre-based playlists.

RULES:
1. Minimum Songs: Each created playlist MUST contain at least {min_songs} songs.
   - If a specific genre doesn't have enough songs to meet {min_songs}, combine it with closely related genres (for example: "Indie Pop & Alternative Rock", "R&B & Soul", or "Assorted / Eclectic").
2. Maximum Songs: No playlist should have more than {max_songs} songs.
   - If a major genre has more than {max_songs} songs, split it into intuitive sub-genres or vibes (for example: "Upbeat Dance Pop" and "Acoustic Pop").
3. Coverage: Every single song from the provided list must be assigned to exactly ONE playlist. Do not omit any songs and do not invent new songs.
4. Output Format: Return a valid JSON object matching this schema:
{{
  "playlists": [
    {{
      "genre": "Genre or Subgenre Name",
      "songs": ["Title by Artist", ...]
    }}
  ]
}}

SONGS TO SORT:
{formatted_song_list}
"""

    max_retries = 3
    response = None
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.2,
                ),
            )
            break
        except Exception as e:
            err_str = str(e)
            if ("503" in err_str or "429" in err_str or "UNAVAILABLE" in err_str) and attempt < max_retries - 1:
                wait_seconds = 3 * (attempt + 1)
                print(f"[Notice] Model service temporarily busy ({err_str[:40]}...). Retrying in {wait_seconds}s...")
                time.sleep(wait_seconds)
            else:
                raise e

    try:
        raw_text = response.text.strip()
        data = json.loads(raw_text)
    except Exception as e:
        raise RuntimeError(f"Failed to parse Gemini response as JSON: {e}\nRaw output: {response.text}")

    parsed_playlists: List[Playlist] = []
    assigned_songs = set()

    for item in data.get("playlists", []):
        genre_name = item.get("genre", "Miscellaneous")
        song_list = item.get("songs", [])
        
        # Clean and verify songs
        playlist_obj = Playlist(name=genre_name)
        for song in song_list:
            if isinstance(song, str):
                playlist_obj.add_song(song)
                assigned_songs.add(song.lower().strip())
        
        if playlist_obj.songs:
            parsed_playlists.append(playlist_obj)

    # Sanity check: Ensure all original tracks were included
    for original_song in tracks:
        if original_song.lower().strip() not in assigned_songs:
            # Assign missed track to the smallest playlist that is under max_songs
            eligible = [p for p in parsed_playlists if len(p.songs) < max_songs]
            if eligible:
                target_p = min(eligible, key=lambda p: len(p.songs))
                target_p.add_song(original_song)
            elif parsed_playlists:
                parsed_playlists[0].add_song(original_song)
            else:
                parsed_playlists.append(Playlist(name="General", songs=[original_song]))

    return parsed_playlists
