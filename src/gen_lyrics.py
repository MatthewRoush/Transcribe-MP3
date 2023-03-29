import os
import io
from time import monotonic
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

    print(f"\nGenerating lyrics for '{song_name}'...")
    # song_path has already been checked, so assume it's good.
    result = model.transcribe(song_path, verbose=False)

    sylt = [] # Synced lyrics metadata.
    uslt = io.StringIO() # Unsynced lyrics metadata.

    if lrc:
        lrc_file = io.StringIO() # Synced lyrics file.
        # Initialize .lrc file.
        lrc_file.write(f"[ar:{artist_name}]\n")
        lrc_file.write(f"[al:{album_name}]\n")
        lrc_file.write(f"[ti:{song_name}]\n")
        lrc_file.write(f"[la:{result['language'].upper()}]\n")
        lrc_file.write("[by:Matthew Roush]\n")
        lrc_file.write("[re:https://github.com/MatthewRoush/Transcribe-MP3]\n\n")

    for segment in result["segments"]:
        start = segment["start"] # Time when the line starts, in seconds.
        start_ms = int(start * 1000) # Convert to milliseconds, for sylt.
        line = segment["text"].strip()

        if lrc:
            xx = start * 100
            ss, xx = divmod(xx, 100)
            mm, ss = divmod(ss, 60)

            xx = fill_zeros(xx)
            ss = fill_zeros(ss)
            mm = fill_zeros(mm)

            start_str = f"[{mm}:{ss}.{xx}]"
        
            lrc_file.write(start_str + line + "\n")

        uslt.write(line + "\n")
        sylt.append((line, start_ms))

    uslt = uslt.getvalue()
    lrc_file = lrc_file.getvalue()

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

    tag.setall("SYLT", [SYLT(encoding=Encoding.UTF8, 
                             format=2, type=1, text=sylt)])
    tag.setall("USLT", [USLT(encoding=Encoding.UTF8, text=uslt)])
    tag.save(v2_version=3)

    time = round(monotonic() - start_time, 3)
    print(f"Successfully generated lyrics for '{song_name}' | {time}s")

def fill_zeros(num):
    num = str(int(num))
    length = len(num)

    if length == 1:
        num = "0" + num

    return num
