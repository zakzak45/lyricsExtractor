
from fastapi import FastAPI, HTTPException
import requests

app = FastAPI()


def extract_lyrics(artist: str, song: str) -> str:
	artist_name = artist.strip()
	song_name = song.strip().lower()
	if not artist_name or not song_name:
		raise ValueError("Artist and song are required")

	link = (
		"https://api.lyrics.ovh/v1/"
		+ artist_name.replace(" ", "%20")
		+ "/"
		+ song_name.replace(" ", "%20")
	)

	response = requests.get(link, timeout=10)
	if response.status_code == 404:
		raise LookupError("Song not found")

	response.raise_for_status()
	json_data = response.json()
	lyrics = json_data.get("lyrics")
	if not lyrics:
		raise LookupError("Lyrics not available")

	return lyrics


@app.get("/")
def root():
	return {"status": "running"}


@app.get("/lyrics")
def lyrics(artist: str, song: str):
	try:
		result = extract_lyrics(artist, song)
		return {"artist": artist, "song": song, "lyrics": result}
	except ValueError as exc:
		raise HTTPException(status_code=400, detail=str(exc))
	except LookupError as exc:
		raise HTTPException(status_code=404, detail=str(exc))
	except requests.RequestException as exc:
		raise HTTPException(status_code=502, detail=str(exc))