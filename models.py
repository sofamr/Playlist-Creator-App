"""Data models for playlist creation."""

class Playlist:
    def __init__(self, name: str, songs: list[str] | None = None, description: str | None = None):
        self.name = name
        self.songs = songs if songs is not None else []
        self.description = description

    def add_song(self, song: str):
        self.songs.append(song)

    def __repr__(self) -> str:
        return f"Playlist(name={self.name!r}, song_count={len(self.songs)})"
