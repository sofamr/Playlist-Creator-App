import json
import time
from typing import List
from google import genai
from google.genai import types
from models import Playlist

def sort_by_best_fit(
    client: genai.Client,
    tracks: List[str],
    min_songs: int,
    max_songs: int,
    model_name: str = "gemini-3.8-flash"
) -> List[Playlist]:
    """
    Uses Gemini AI to organize songs into playlists based on 'Best Fit':
    matching sound characteristics, emotional mood, lyrical themes, and overall vibe.
    Strictly adheres to min_songs and max_songs constraints per playlist.
    """
    if not tracks:
        return []

    # If the total number of songs is less than min_songs, create 1 combined playlist
    if len(tracks) < min_songs:
        print(f"[Notice] Total songs ({len(tracks)}) is less than min_songs ({min_songs}). Creating a single playlist.")
        p = Playlist(
            name="Eclectic Mix",
            songs=tracks,
            description="All tracks combined into a single diverse playlist."
        )
        return [p]

    formatted_song_list = "\n".join(f"{i+1}. {song}" for i, song in enumerate(tracks))

    prompt = f"""You are an intuitive music producer, psychologist, and elite playlist curator.
Your task is to cluster the following {len(tracks)} songs based on "BEST FIT" — grouping tracks that share the closest emotional resonance, lyrical themes, acoustic/production characteristics, and overall vibe (rather than strictly by broad genre).

FACTORS TO CONSIDER FOR BEST FIT:
- Emotional Tone: Melancholic, euphoric, introspective, angry/rebellious, serene, bittersweet, triumphant, etc.
- Lyrical Themes & Content: Heartbreak, healing, identity/self-discovery, late-night contemplation, romance, partying/celebration, escapism, etc.
- Sonic Characteristics: Energy level, tempo, textures (analog synths, distorted guitars, mellow acoustic instruments, punchy 808s), atmospheric space, and vocal intensity.
- Setting / Vibe: "Late Night Neon Drive", "Cathartic Heartbreak & Rage", "Cozy Coffeehouse Reflections", "Golden Hour Euphoria", etc.

STRICT CONSTRAINTS:
1. Minimum Songs: Each created playlist MUST contain at least {min_songs} songs.
   - If a specific mood cluster has fewer than {min_songs} songs, merge it with the most emotionally or sonically compatible group.
2. Maximum Songs: No playlist should have more than {max_songs} songs.
   - If a cluster exceeds {max_songs} songs, split it into subtle variations (e.g., "High-Energy Rage Anthems" vs "Mid-Tempo Rebellious Rock").
3. Creative Vibe Naming: Give each playlist an evocative, descriptive name reflecting its mood/vibe, plus a 1-sentence vibe description.
4. Coverage: Every single song from the input list must appear in exactly ONE playlist. Do not omit any songs and do not invent new ones.
5. Output Format: Return a valid JSON object matching this schema:
{{
  "playlists": [
    {{
      "name": "Evocative Vibe/Mood Name",
      "vibe_description": "Brief 1-sentence description of the mood, sonic feel, and lyrical themes",
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
                    temperature=0.3,
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
        vibe_name = item.get("name", "Vibe Playlist")
        vibe_desc = item.get("vibe_description", "")
        song_list = item.get("songs", [])

        playlist_obj = Playlist(name=vibe_name, description=vibe_desc)
        for song in song_list:
            if isinstance(song, str):
                playlist_obj.add_song(song)
                assigned_songs.add(song.lower().strip())

        if playlist_obj.songs:
            parsed_playlists.append(playlist_obj)

    # Sanity check: Ensure all original tracks are assigned
    for original_song in tracks:
        if original_song.lower().strip() not in assigned_songs:
            eligible = [p for p in parsed_playlists if len(p.songs) < max_songs]
            if eligible:
                target_p = min(eligible, key=lambda p: len(p.songs))
                target_p.add_song(original_song)
            elif parsed_playlists:
                parsed_playlists[0].add_song(original_song)
            else:
                parsed_playlists.append(
                    Playlist(name="General Vibe", songs=[original_song], description="Diverse collection")
                )

    return parsed_playlists
