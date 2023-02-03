# Transcribe-MP3
 Generate synced and unsynced lyrics for .mp3 songs using openai-whisper.

## Dependencies
[mutagen](https://pypi.org/project/mutagen/) for working with mp3 files.

[openai-whisper](https://pypi.org/project/openai-whisper/) for transcribing the mp3 file.

## Usage
This is a command-line program that lets you set lyrics for a mp3 file by generating lyrics using openai-whisper or setting lyrics using a lrc file.

It generates SYLT and USLT lyrics and has the option to output a lrc file in a folder called "lyrics" in the same directory as the mp3 file.

`transcribe.py` is the main script.

Use `transcribe.py -h` for information on arguments.
