
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
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


@app.get("/ui", response_class=HTMLResponse)
def ui():
	return """<!DOCTYPE html>
<html lang="en">
	<head>
		<meta charset="utf-8" />
		<meta name="viewport" content="width=device-width, initial-scale=1" />
		<title>Lyrics Extractor</title>
		<link rel="preconnect" href="https://fonts.googleapis.com" />
		<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
		<link
			href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600&family=IBM+Plex+Serif:wght@600&display=swap"
			rel="stylesheet"
		/>
		<style>
			:root {
				--ink: #0f172a;
				--muted: #475569;
				--accent: #0ea5a4;
				--accent-dark: #0f766e;
				--paper: #f8fafc;
				--panel: #ffffff;
				--shadow: 0 20px 60px rgba(15, 23, 42, 0.2);
			}
			* {
				box-sizing: border-box;
			}
			body {
				margin: 0;
				font-family: "IBM Plex Sans", system-ui, -apple-system, sans-serif;
				color: var(--ink);
				background: radial-gradient(1200px 800px at 10% 10%, #e0f2fe, transparent 60%),
					radial-gradient(1000px 700px at 90% 20%, #ecfeff, transparent 60%),
					linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%);
				min-height: 100vh;
				display: flex;
				align-items: center;
				justify-content: center;
				padding: 32px 16px;
			}
			.card {
				width: min(900px, 100%);
				background: var(--panel);
				border-radius: 24px;
				box-shadow: var(--shadow);
				overflow: hidden;
				display: grid;
				grid-template-columns: 1.1fr 1.4fr;
			}
			.hero {
				padding: 36px;
				background: linear-gradient(160deg, #0ea5a4 0%, #22c55e 100%);
				color: white;
				display: flex;
				flex-direction: column;
				justify-content: center;
				gap: 18px;
			}
			.hero h1 {
				font-family: "IBM Plex Serif", "Times New Roman", serif;
				font-size: clamp(28px, 3vw, 36px);
				margin: 0;
				letter-spacing: -0.02em;
			}
			.hero p {
				margin: 0;
				opacity: 0.9;
				line-height: 1.6;
			}
			.content {
				padding: 36px;
				display: flex;
				flex-direction: column;
				gap: 16px;
			}
			label {
				font-weight: 600;
				color: var(--muted);
				display: block;
				margin-bottom: 6px;
			}
			input {
				width: 100%;
				padding: 12px 14px;
				border-radius: 12px;
				border: 1px solid #cbd5f5;
				font-size: 16px;
				outline: none;
			}
			input:focus {
				border-color: var(--accent);
				box-shadow: 0 0 0 3px rgba(14, 165, 164, 0.2);
			}
			button {
				border: none;
				background: var(--accent);
				color: white;
				padding: 12px 18px;
				font-size: 16px;
				border-radius: 12px;
				cursor: pointer;
				font-weight: 600;
				transition: transform 0.15s ease, background 0.2s ease;
			}
			button:hover {
				background: var(--accent-dark);
				transform: translateY(-1px);
			}
			.result {
				margin-top: 8px;
				padding: 16px;
				border-radius: 14px;
				background: var(--paper);
				min-height: 160px;
				white-space: pre-wrap;
				font-family: "IBM Plex Sans", system-ui, -apple-system, sans-serif;
			}
			.hint {
				font-size: 13px;
				color: var(--muted);
			}
			@media (max-width: 860px) {
				.card {
					grid-template-columns: 1fr;
				}
			}
		</style>
	</head>
	<body>
		<div class="card">
			<section class="hero">
				<h1>Lyrics Extractor</h1>
				<p>
					Paste an artist and song name to fetch lyrics from the API.
					Results appear instantly below.
				</p>
			</section>
			<section class="content">
				<div>
					<label for="artist">Artist</label>
					<input id="artist" placeholder="Coldplay" />
				</div>
				<div>
					<label for="song">Song</label>
					<input id="song" placeholder="Yellow" />
				</div>
				<button id="extract">Extract lyrics</button>
				<div class="hint">Tip: try Coldplay - Yellow</div>
				<div id="result" class="result">Lyrics will show up here.</div>
			</section>
		</div>
		<script>
			const artistInput = document.getElementById("artist");
			const songInput = document.getElementById("song");
			const result = document.getElementById("result");
			const button = document.getElementById("extract");

			function setResult(message) {
				result.textContent = message;
			}

			async function fetchLyrics() {
				const artist = artistInput.value.trim();
				const song = songInput.value.trim();
				if (!artist || !song) {
					setResult("Please enter both artist and song.");
					return;
				}

				setResult("Fetching lyrics...");
				try {
					const params = new URLSearchParams({ artist, song });
					const response = await fetch(`/lyrics?${params.toString()}`);
					const data = await response.json();
					if (!response.ok) {
						setResult(data.detail || "Something went wrong.");
						return;
					}
					setResult(data.lyrics || "No lyrics returned.");
				} catch (error) {
					setResult("Request failed. Please try again.");
				}
			}

			button.addEventListener("click", fetchLyrics);
			[artistInput, songInput].forEach((input) => {
				input.addEventListener("keydown", (event) => {
					if (event.key === "Enter") {
						fetchLyrics();
					}
				});
			});
		</script>
	</body>
</html>
"""


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