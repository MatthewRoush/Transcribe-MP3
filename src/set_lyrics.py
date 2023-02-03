from mutagen import MutagenError
from mutagen.id3 import ID3, SYLT, USLT, Encoding

def set_lyrics(song_path, lrc_path):
    try:
        tag = ID3(song_path)
    except MutagenError:
        print("Could not find mp3 file. Invalid file path.")
        return

    # lrc_path was checked in transcribe.py, so no need to here.
    with open(lrc_path, "r", encoding="UTF-8") as f:
        lrc_file = f.readlines()

    sylt = [] # Synced lyrics metadata.
    uslt = "" # Unsynced lyrics metadata.

    for line in lrc_file:
        line = line.strip()

        if line == "":
            continue

        if line[0] == "[":
            split_line = line[1:].split("]")
            time = split_line[0]
            lyrics = split_line[-1]

            minutes, seconds = time.split(":")
            
            try:
                start_ms = 0
                start_ms += int(minutes) * 60 * 1000
                start_ms += int(float(seconds) * 1000)
            except ValueError:
                continue

            uslt += lyrics + "\n"
            sylt.append((lyrics, start_ms))

    tag.setall("SYLT",
                [SYLT(encoding=Encoding.UTF8, format=2, type=1,text=sylt)])
    tag.setall("USLT", [USLT(encoding=Encoding.UTF8, text=uslt)])
    tag.save(v2_version=3)

    print(f"Successfully set lyrics")
