# YouTube Music Playlist Splitter

An intelligent Python application that divides a major YouTube Music playlist into cohesive mini-playlists based on musical **Genre** or **Best Fit** (analyzing emotion, lyrical content, and sound characteristics/vibes), respecting customizable minimum and maximum song limits per playlist.

---

## Features

- **Automated Playlist Track Extraction**: Reads songs and artist information directly from YouTube and YouTube Music playlist links using `ytmusicapi` and `yt-dlp`.
- **Genre-Based Clustering (G)**: Groups songs into clean, distinct musical genres.
- **Best Fit Clustering (B)**: Analyzes song emotion, lyrical themes, sonic textures, and overall atmosphere (e.g., late-night melancholy, cathartic angst, sun-drenched euphoria) to group matching tracks.
- **Min & Max Constraints**: Guarantees that every generated playlist meets your requested minimum (`min_songs`) and maximum (`max_songs`) sizes.
- **Easy API Key Setup**: Store your key in `.env` or simply enter it during the first run.
- **Export Ready**: Optionally saves generated playlists, vibe descriptions, and tracklists to `generated_playlists.txt`.

---

## Quick Setup

### 1. Set Your Gemini API Key
You can get an API key at [Google AI Studio](https://aistudio.google.com/app/apikey).

Open the [`.env`](.env) file in this directory and paste your API key:
```env
GEMINI_API_KEY=AIzaSy...
```
*(If you run the app without setting this, the app will ask you once in the terminal and automatically save it for you!)*

### 2. Run the App
Use the included virtual environment:
```bash
.venv/bin/python3 main.py
```
*(Or activate the virtual environment first with `source .venv/bin/activate` and run `python3 main.py`)*

Important Note: Make sure playlist is set to 'unlisted' or 'public' so the program is able to access it.

---

## File Structure

- [`main.py`](main.py): Main terminal interface with support for Genre (`G`) and Best Fit (`B`) sorting.
- [`.env`](.env): Stores your `GEMINI_API_KEY` securely.
- [`config.py`](config.py): Configuration loader and Gemini client manager.
- [`playlist_extractor.py`](playlist_extractor.py): Extracts tracks and titles from YouTube Music URLs.
- [`genre_sorter.py`](genre_sorter.py): Prompts Gemini to group tracks into genre playlists obeying min/max rules.
- [`best_fit_sorter.py`](best_fit_sorter.py): Clusters tracks by emotion, lyrical themes, and sonic atmosphere.
- [`models.py`](models.py): Contains the `Playlist` data model.
- [`requirements.txt`](requirements.txt): List of dependencies (`google-genai`, `ytmusicapi`, `yt-dlp`, `python-dotenv`).
