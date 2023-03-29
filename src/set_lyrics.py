import io
from mutagen import MutagenError
from mutagen.id3 import ID3, SYLT, USLT, Encoding

def set_lyrics(song_path, lrc_path):
    try:
        tag = ID3(song_path)
    except HeaderNotFoundError:
        print("Not an mp3 file or invalid mp3 file.")
        return

    # lrc_path was checked in transcribe.py, so no need to here.
    with open(lrc_path, "r", encoding="UTF-8") as f:
        lrc_file = f.readlines()

    sylt = [] # Synced lyrics metadata.
    uslt = io.StringIO() # Unsynced lyrics metadata.

    for i, line in enumerate(lrc_file):
        line = line.strip()

        if line == "":
            continue

        split_line = line[1:].split("]")

        if split_line[1] == "":
            continue

        time = split_line[0]
        lyrics = split_line[1]

        # Time is in mm:ss.xx format.
        minutes, seconds = time.split(":")
        start_ms = int(minutes) * 60 * 1000
        start_ms += int(float(seconds) * 1000)

        uslt.write(lyrics + "\n")
        sylt.append((lyrics, start_ms))

    uslt = uslt.getvalue()

    tag.setall("SYLT",
                [SYLT(encoding=Encoding.UTF8, format=2, type=1,text=sylt)])
    tag.setall("USLT", [USLT(encoding=Encoding.UTF8, text=uslt)])
    tag.save(v2_version=3)

    print(f"Successfully set lyrics.")
