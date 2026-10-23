import sys
from models import Playlist
from config import get_gemini_client
from playlist_extractor import fetch_playlist_tracks
from genre_sorter import sort_by_genre
from best_fit_sorter import sort_by_best_fit

def main():
    print("=" * 60)
    print("        YouTube Music Playlist Splitter")
    print("=" * 60)

    # 1. User Inputs
    playlist_url = input("Enter playlist URL (Youtube Music): ").strip()
    if not playlist_url:
        print("Error: Playlist URL cannot be empty.")
        sys.exit(1)

    try:
        min_songs = int(input("How many songs would you like to have in you playlist at a minimum: ").strip())
        max_songs = int(input("How many songs would you like to have in you playlist at a maximum: ").strip())
    except ValueError:
        print("Error: Minimum and maximum songs must be valid integers.")
        sys.exit(1)

    if min_songs <= 0 or max_songs <= 0:
        print("Error: Song counts must be greater than 0.")
        sys.exit(1)

    if min_songs > max_songs:
        print("Error: Minimum songs cannot be greater than maximum songs.")
        sys.exit(1)

    sort_base = input("Would you like to sort based on Genre (G) or  Best Fit (B): ").lower().strip()
    is_best_fit = sort_base.startswith("b")
    mode_label = "Best Fit (Emotion, Content & Vibe)" if is_best_fit else "Genre"

    # 2. Setup Gemini AI Client
    try:
        client = get_gemini_client()
    except Exception as e:
        print(f"\nConfiguration error: {e}")
        sys.exit(1)

    # 3. Fetch Playlist Songs
    print("\n[1/2] Fetching tracks from YouTube Music playlist...")
    try:
        playlist_title, tracks = fetch_playlist_tracks(playlist_url)
        print(f"✓ Found '{playlist_title}' with {len(tracks)} songs.")
    except Exception as e:
        print(f"Failed to load playlist: {e}")
        sys.exit(1)

    if not tracks:
        print("No songs found in the playlist.")
        sys.exit(1)

    # 4. Sort and Cluster by Genre or Best Fit with Gemini
    print(f"\n[2/2] Analyzing songs based on {mode_label} (Min: {min_songs}, Max: {max_songs})...")
    try:
        if is_best_fit:
            playlists = sort_by_best_fit(client, tracks, min_songs, max_songs)
        else:
            playlists = sort_by_genre(client, tracks, min_songs, max_songs)
    except Exception as e:
        print(f"Error sorting playlist with Gemini: {e}")
        sys.exit(1)

    # 5. Output Results
    print("\n" + "=" * 60)
    print("Here are the playlist and the list of songs in it")
    print("=" * 60 + "\n")

    for playlist in playlists:
        print(f"--- {playlist.name} ({len(playlist.songs)} songs) ---")
        if playlist.description:
            print(f"  Vibe: {playlist.description}")
        for song in playlist.songs:
            print(f"  • {song}")
        print()

    # Optional: Save to file
    save_choice = input("Would you like to save these playlists to a text file? (y/n): ").strip().lower()
    if save_choice in ("y", "yes"):
        filename = "generated_playlists.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"Source Playlist: {playlist_title}\n")
            f.write(f"Total Songs: {len(tracks)}\n")
            f.write(f"Sorting Mode: {mode_label}\n\n")
            for playlist in playlists:
                f.write(f"=== {playlist.name} ({len(playlist.songs)} songs) ===\n")
                if playlist.description:
                    f.write(f"Vibe: {playlist.description}\n")
                for song in playlist.songs:
                    f.write(f"  - {song}\n")
                f.write("\n")
        print(f"Saved playlists to {filename} successfully!")

if __name__ == "__main__":
    main()
