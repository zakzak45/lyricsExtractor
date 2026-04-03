import tkinter as tk
from tkinter import messagebox, scrolledtext
import requests


def fetch_lyrics(base_url: str, artist: str, song: str) -> str:
    url = f"{base_url.rstrip('/')}/lyrics"
    response = requests.get(url, params={"artist": artist, "song": song}, timeout=10)
    if response.status_code == 404:
        raise LookupError(response.json().get("detail", "Song not found"))
    response.raise_for_status()
    data = response.json()
    return data.get("lyrics", "")


def on_extract():
    base_url = base_url_var.get().strip()
    artist = artist_var.get().strip()
    song = song_var.get().strip()

    if not base_url or not artist or not song:
        messagebox.showerror("Missing input", "Base URL, artist, and song are required.")
        return

    try:
        lyrics = fetch_lyrics(base_url, artist, song)
        lyrics_box.delete("1.0", tk.END)
        lyrics_box.insert(tk.END, lyrics)
    except LookupError as exc:
        messagebox.showerror("Not found", str(exc))
    except requests.RequestException as exc:
        messagebox.showerror("Request failed", str(exc))


root = tk.Tk()
root.title("Lyrics Extractor GUI")
root.geometry("700x500")
root.resizable(0, 0)

base_url_var = tk.StringVar(value="http://127.0.0.1:8000")
artist_var = tk.StringVar()
song_var = tk.StringVar()

frame = tk.Frame(root, padx=12, pady=12)
frame.pack(fill=tk.BOTH, expand=True)

row = 0

tk.Label(frame, text="API Base URL").grid(row=row, column=0, sticky="w")
tk.Entry(frame, textvariable=base_url_var, width=50).grid(row=row, column=1, sticky="w")

row += 1

tk.Label(frame, text="Artist").grid(row=row, column=0, sticky="w", pady=(8, 0))
tk.Entry(frame, textvariable=artist_var, width=50).grid(row=row, column=1, sticky="w", pady=(8, 0))

row += 1

tk.Label(frame, text="Song").grid(row=row, column=0, sticky="w", pady=(8, 0))
tk.Entry(frame, textvariable=song_var, width=50).grid(row=row, column=1, sticky="w", pady=(8, 0))

row += 1

tk.Button(frame, text="Extract lyrics", width=20, command=on_extract).grid(
    row=row, column=1, sticky="w", pady=(10, 0)
)

row += 1

tk.Label(frame, text="Lyrics").grid(row=row, column=0, sticky="nw", pady=(12, 0))
lyrics_box = scrolledtext.ScrolledText(frame, width=70, height=18, wrap=tk.WORD)
lyrics_box.grid(row=row, column=1, sticky="w", pady=(12, 0))

root.mainloop()
