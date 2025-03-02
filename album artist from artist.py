import os
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, ID3NoHeaderError
from mutagen.flac import FLAC
from mutagen.mp4 import MP4, MP4Tags

while True:
    folder_location = input("Enter a Path: ")
    if not os.path.exists(folder_location):
        print("Folder doesn't exist")
        continue
    break

folder_location = folder_location.replace("\\", "/")
if not folder_location[-1] == "/":
    folder_location += "/"

def get_music_files(directory):
    # Supported music file extensions
    extensions = ('.mp3', '.flac', '.m4a', '.aac', '.wav', '.ogg', '.wma')

    music_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(extensions):
                music_files.append(os.path.join(root, file))
    return music_files

def get_audio(file_path):
    if file_path.lower().endswith('.mp3'):
        return EasyID3(file_path)
    elif file_path.lower().endswith('.flac'):
        return FLAC(file_path)
    elif file_path.lower().endswith('.m4a'):
        return MP4(file_path)
    else:
        return None

def get_artist(audio, file_path):
    try:
        if isinstance(audio, EasyID3):
            return audio['artist'][0]
        elif isinstance(audio, FLAC):
            return audio['artist'][0]
        elif isinstance(audio, MP4):
            tags = audio.tags
            if '\xa9ART' in tags:
                return tags['\xa9ART'][0]
    except KeyError:
        print(f"Artist tag not found for '{file_path}'")
        return None

def copy_artist_to_album_artist(file_path):
    try:
        audio = get_audio(file_path)
        if audio is not None:
            artist = get_artist(audio, file_path)
            if artist:
                artist = artist.strip()
                old_albumartist = audio.get('albumartist', [''])[0]
                if not old_albumartist == str(artist).split(", ")[0]:
                    audio['albumartist'] = str(artist).split(", ")[0]
                    audio.save()
                    print(f"'{file_path.replace(folder_location, "")}' from '{old_albumartist}' to '{str(artist).split(', ')[0]}'")
            else:
                print(f"Artist tag not found for '{file_path}'")
        else:
            print(f"Unsupported file format: {file_path}")
    except ID3NoHeaderError:
        print(f"No ID3 header found for '{file_path}'")
    except Exception as e:
        print(f"Error processing '{file_path}': {e}")

def copy_artist_to_album_artist_in_directory(directory):
    music_files = get_music_files(directory)
    for file_path in music_files:
        copy_artist_to_album_artist(file_path)

if __name__ == "__main__":
    copy_artist_to_album_artist_in_directory(folder_location)
