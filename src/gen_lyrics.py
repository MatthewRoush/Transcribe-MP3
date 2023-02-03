import os
from time import monotonic
import whisper
from mutagen import MutagenError
from mutagen.mp3 import MP3, HeaderNotFoundError
from mutagen.id3 import ID3, SYLT, USLT, Encoding

def gen_lyrics(model, song_path, lrc):
    start_time = monotonic() # To print how long it took to process the mp3.

    try:
        song = MP3(song_path)
        tag = ID3(song_path)
    except HeaderNotFoundError:
        print("Not an mp3 file or invalid mp3 file.")
        return
    except MutagenError:
        print("Could not find mp3 file. Invalid file path.")
        return

    # Try to get the artist name from the mp3 metadata.
    try:
        artist_name = song["TPE1"].text[0]
    except KeyError:
        artist_name = "Unknown Artist"

    # Try to get the album name from the mp3 metadata.
    try:
        album_name = song["TALB"].text[0]
    except KeyError:
        album_name = "Unknown Album"

    # Try to get the song name from the mp3 metadata.
    try:
        song_name = song["TIT2"].text[0]
    except KeyError:
        song_name = "Unknown Song"

    try:
        model = whisper.load_model(model)
    except RuntimeError:
        print(
            "Invalid model. \n"
            "Valid models are: tiny, tiny.en, base, base.en, "
            "small, small.en, medium, medium.en, large, large-v1, large-v2")
        return

    # song_path has already been checked, so assume it's good.
    result = model.transcribe(song_path)

    sylt = [] # Synced lyrics metadata.
    uslt = "" # Unsynced lyrics metadata.

    if lrc:
        lrc_file = "" # Synced lyrics file.
        # Initialize .lrc file.
        lrc_file += f"[ar:{artist_name}]\n"
        lrc_file += f"[al:{album_name}]\n"
        lrc_file += f"[ti:{song_name}]\n"
        lrc_file += f"[la:{result['language'].upper()}]\n"
        lrc_file += "[by:Matthew Roush]\n"
        lrc_file += "[re:https://github.com/MatthewRoush/Transcribe-MP3]\n\n"

    for segment in result["segments"]:
        start = segment["start"] # Time when the line starts, in seconds.
        start_ms = int(start * 1000) # Convert to milliseconds, for sylt.
        line = segment["text"].strip()

        if lrc:
            if start < 60.0:
                start_str = f"[00:{round(start, 3)}]"
            else:
                minutes = int(start / 60.0)
                seconds = start % 60.0
                start_str = f"[{minutes}:{round(seconds, 3)}]"
        
            lrc_file += start_str + line + "\n"

        uslt += line + "\n"
        sylt.append((line, start_ms))

    if lrc:
        song_folder = os.path.split(song_path)[0]

        # .lrc file will be put in a folder called "lyrics" in the same
        # directory that the .mp3 file was in.
        lrc_folder = os.path.join(song_folder, "lyrics")
        if not os.path.exists(lrc_folder): # Check if lyrics folder exists.
            try:
                os.mkdir(lrc_folder) # If not then make it.
            except FileNotFoundError:
                print(f"Could not create lyrics folder in {song_folder}.")
                return

        lrc_path = os.path.join(lrc_folder, song_name + ".lrc")

        with open(lrc_path, "w", encoding="UTF-8") as f:
            f.write(lrc_file)

    tag.setall("SYLT",
                [SYLT(encoding=Encoding.UTF8, format=2, type=1,text=sylt)])
    tag.setall("USLT", [USLT(encoding=Encoding.UTF8, text=uslt)])
    tag.save(v2_version=3)

    completion_time = round(monotonic() - start_time, 3)
    print(f"Successfully generated lyrics | {song_name} | {completion_time}s")
