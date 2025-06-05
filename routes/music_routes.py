from flask import Blueprint, request, jsonify, session
from textblob import TextBlob
import os
import requests
import certifi
import random
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

music_bp = Blueprint('music_routes', __name__)

# Load environment or fallback values
SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID", "8cfb27cc08c54cfd97ed4952f6fa3397")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET", "1c0f981c0f4541d1bc0077d6b336fa35")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "AIzaSyBf_NrqORxcOA-ZkSJeNeIjG5T4WcniEgY")

# 🎵 Static fallback songs for moods
FALLBACK_SONGS = {
    "happy": [
        {"name": "Happy - Pharrell Williams", "url": "https://www.youtube.com/watch?v=y6Sxv-sUYtM"},
        {"name": "Good Time - Owl City", "url": "https://www.youtube.com/watch?v=H7HmzwI67ec"},
        {"name": "Can't Stop the Feeling - Justin Timberlake", "url": "https://www.youtube.com/watch?v=ru0K8uYEZWw"},
    ],
    "sad": [
        {"name": "Let Her Go - Passenger", "url": "https://www.youtube.com/watch?v=RBumgq5yVrA"},
        {"name": "Someone Like You - Adele", "url": "https://www.youtube.com/watch?v=hLQl3WQQoQ0"},
        {"name": "Fix You - Coldplay", "url": "https://www.youtube.com/watch?v=k4V3Mo61fJM"},
    ],
    "relaxed": [
        {"name": "Weightless - Marconi Union", "url": "https://www.youtube.com/watch?v=UfcAVejslrU"},
        {"name": "Breathe Me - Sia", "url": "https://www.youtube.com/watch?v=SFGvmrJ5rjM"},
        {"name": "Pure Shores - All Saints", "url": "https://www.youtube.com/watch?v=O1OTWCd40rY"},
    ],
    "anxious": [
        {"name": "River Flows In You - Yiruma", "url": "https://www.youtube.com/watch?v=7maJOI3QMu0"},
        {"name": "Meditation Music", "url": "https://www.youtube.com/watch?v=1ZYbU82GVz4"},
        {"name": "Clair de Lune - Debussy", "url": "https://www.youtube.com/watch?v=CvFH_6DNRCY"},
    ],
    "angry": [
        {"name": "In The End - Linkin Park", "url": "https://www.youtube.com/watch?v=eVTXPUF4Oz4"},
        {"name": "Bring Me to Life - Evanescence", "url": "https://www.youtube.com/watch?v=3YxaaGgTQYM"},
        {"name": "Stronger - Kanye West", "url": "https://www.youtube.com/watch?v=PsO6ZnUZI0g"},
    ],
    "energetic": [
        {"name": "Eye of the Tiger - Survivor", "url": "https://www.youtube.com/watch?v=btPJPFnesV4"},
        {"name": "Uptown Funk - Bruno Mars", "url": "https://www.youtube.com/watch?v=OPf0YbXqDm0"},
        {"name": "Stronger - Britney Spears", "url": "https://www.youtube.com/watch?v=AJWtLf4-WWs"},
    ],
    "sleepy": [
        {"name": "Ambient Sleep Music", "url": "https://www.youtube.com/watch?v=1ZYbU82GVz4"},
        {"name": "Soft Piano for Sleep", "url": "https://www.youtube.com/watch?v=WUXEeAXywCY"},
        {"name": "Relaxing Rain", "url": "https://www.youtube.com/watch?v=eJf3W2VAai4"},
    ],
    "excited": [
        {"name": "Don't Stop Me Now - Queen", "url": "https://www.youtube.com/watch?v=HgzGwKwLmgM"},
        {"name": "Feel This Moment - Pitbull", "url": "https://www.youtube.com/watch?v=5jlI4uzZGjU"},
        {"name": "Roar - Katy Perry", "url": "https://www.youtube.com/watch?v=CevxZvSJLk8"},
    ],
}

def get_spotify_token():
    url = "https://accounts.spotify.com/api/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": SPOTIPY_CLIENT_ID,
        "client_secret": SPOTIPY_CLIENT_SECRET,
    }
    try:
        response = requests.post(url, headers=headers, data=data, verify=certifi.where())
        #response = requests.post(url, headers=headers, data=data, verify=False)

        response.raise_for_status()
        return response.json().get("access_token")
    except Exception as e:
        print("❌ Spotify token error:", e)
        return None

def get_youtube_link(query):
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": f"{query} official audio",
        "key": YOUTUBE_API_KEY,
        "maxResults": 1,
        "type": "video"
    }

    try:
        response = requests.get(url, params=params, timeout=5, verify=certifi.where())
        data = response.json()

        if "items" in data and len(data["items"]) > 0:
            video_id = data["items"][0]["id"]["videoId"]
            return f"https://www.youtube.com/watch?v={video_id}"
        else:
            raise ValueError("No items found")
    except Exception as e:
        print(f"⚠️ YouTube fallback failed for {query}: {e}")
        return None



def get_spotify_songs(mood):
    token = get_spotify_token()
    if not token:
        return []

    url = f"https://api.spotify.com/v1/search?q={mood}&type=track&limit=30&offset={random.randint(0, 50)}"
    headers = {"Authorization": f"Bearer {token}"}

    session_requests = requests.Session()
    retry = Retry(total=3, backoff_factor=1, status_forcelist=[502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session_requests.mount('http://', adapter)
    session_requests.mount('https://', adapter)

    try:
        response = session_requests.get(url, headers=headers, verify=certifi.where())
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("Spotify request failed:", e)
        return []

    tracks = response.json().get("tracks", {}).get("items", [])
    print(f"🔎 Retrieved {len(tracks)} tracks from Spotify for mood: {mood}")

    songs = []
    for track in tracks:
        name = track["name"]
        artist = track["artists"][0]["name"]
        preview_url = track.get("preview_url")

        if preview_url:
            songs.append({
                "name": name,
                "artist": artist,
                "url": preview_url,
                "source": "spotify"
            })
        else:
            #yt_link = get_youtube_link(f"{name} {artist}")
            search_query = f"{name} by {artist}"
            yt_link = get_youtube_link(search_query)

            if yt_link:
                songs.append({
                    "name": name,
                    "artist": artist,
                    "url": yt_link,
                    "source": "youtube"
                })

    if not songs:
        print("🎵 Using fallback songs for:", mood)
        fallback = FALLBACK_SONGS.get(mood, [])
        return random.sample(fallback, min(3,len(fallback)))

    print(f"🎵 Returning {len(songs)} total songs (Spotify + YouTube)")
    return songs


@music_bp.route('/api/music/', methods=['POST'])
def get_music():
    data = request.json
    mood = data.get("mood", "happy").lower()
    songs = get_spotify_songs(mood)
    return jsonify({"songs": songs})
