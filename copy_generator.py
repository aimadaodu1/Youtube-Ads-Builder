"""Local copy generator for music/video ads.

This does not call an AI API, so the app works immediately. You can replace
this file later with OpenAI/Gemini calls if you want smarter copy generation.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class AdCopy:
    headlines: List[str]
    descriptions: List[str]
    short_ctas: List[str]
    video_hooks: List[str]


def _clean(text: str) -> str:
    return " ".join((text or "").split())


def _trim(text: str, limit: int) -> str:
    text = _clean(text)
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 1)].rstrip() + "…"


def generate_music_ad_copy(
    artist_name: str,
    song_title: str,
    genre: str,
    mood: str,
    release_note: str = "",
) -> AdCopy:
    artist = _clean(artist_name) or "the artist"
    song = _clean(song_title) or "the new release"
    genre_text = _clean(genre) or "music"
    mood_text = _clean(mood) or "fresh"
    release = _clean(release_note)

    raw_headlines = [
        f"Watch {song} Now",
        f"New Music From {artist}",
        f"Discover {artist}",
        f"Fresh {genre_text} Energy",
        f"{song} Official Video",
        f"Stream {song} Today",
        f"A New Sound From {artist}",
        f"{mood_text.title()} {genre_text.title()}",
        "Tap To Watch The Video",
        "New Music Worth Hearing",
        "Hear The Full Song",
        "Watch The Music Video",
        "Discover Your Next Song",
        "Play The New Release",
        "Listen Now On YouTube",
    ]

    raw_descriptions = [
        f"Watch {artist}'s new {genre_text} release and hear the full song today.",
        f"Discover {song}, a {mood_text} track built for fans of new {genre_text}.",
        f"Tap to watch the video and stream more music from {artist}.",
        f"New visuals, new sound, and a fresh release from {artist}.",
    ]
    if release:
        raw_descriptions.insert(0, release)

    hooks = [
        f"New {genre_text} from {artist}.",
        f"This is {song}.",
        "If you like fresh Afrobeats, start here.",
        "Give this hook ten seconds.",
        f"{artist} is bringing a new sound.",
    ]

    return AdCopy(
        headlines=[_trim(h, 30) for h in raw_headlines],
        descriptions=[_trim(d, 90) for d in raw_descriptions],
        short_ctas=["Watch now", "Listen now", "Stream today", "Play video", "Discover more"],
        video_hooks=[_trim(h, 60) for h in hooks],
    )
