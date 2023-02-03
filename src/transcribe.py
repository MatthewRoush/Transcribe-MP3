import os
import argparse
from gen_lyrics import gen_lyrics
from set_lyrics import set_lyrics

def main():
    parser = argparse.ArgumentParser(
        prog = "transcribe",
        description = "Automatically transcribe mp3 files.")

    parser.add_argument("path",
                        help=("Path to folder or file. "
                            "Put in single or double quotes if the "
                            "path contains spaces."))
    
    parser.add_argument("--model",
                        default="base.en",
                        help=("Whisper model to use (tiny, tiny.en, base, "
                            "base.en, small, small.en, medium, medium.en, "
                            "large, large-v1, large-v2)"))
    
    parser.add_argument("--lrc",
                        action="store_true",
                        help=("Flag for creating an lrc file to output "
                            "synced lyrics data to."))
    
    parser.add_argument("--set-lyrics",
                        help=("You can use this to fix generated lyrics by "
                            "fixing the lyrics in the lrc file this script "
                            "creates, then set path to the path of the mp3 "
                            " file and give the path to the lrc file after "
                            "this argument."))

    args = parser.parse_args()

    if not os.path.exists(args.path):
        print("\nInvalid path.")
        return

    if os.path.isfile(args.path):
        if args.set_lyrics is not None:
            if not os.path.exists(args.set_lyrics):
                print("\nInvalid lrc path.")
                return

            if os.path.isfile(args.set_lyrics):
                set_lyrics(args.path, args.set_lyrics)
            else:
                print("\nlrc must be a file.")
                return
        else:
            gen_lyrics(args.model, args.path, args.lrc)
    else:
        for dirpath, folders, files_list in os.walk(args.path):
            for file in files_list:
                if file[-4:] == ".mp3":
                    path = os.path.join(dirpath, file)
                    gen_lyrics(args.model, path, args.lrc)

if __name__ == '__main__':
    main()
