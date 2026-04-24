import os
import re
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, ID3NoHeaderError
from mutagen.flac import FLAC
from mutagen.mp4 import MP4

os.system("cls")

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

def get_title(audio, file_path):
    try:
        if isinstance(audio, EasyID3):
            return audio['title'][0]
        elif isinstance(audio, FLAC):
            return audio['title'][0]
        elif isinstance(audio, MP4):
            return audio.tags['\xa9nam'][0]
    except KeyError:
        print(f"Title tag not found for '{file_path}'")
        return None

def sanitize_filename(filename):
    # Replace invalid characters with an underscore
    return re.sub(r'[<>:"/\\|?*]', '', filename).strip() 

def rename_music_file(file_path):
    try:
        audio = get_audio(file_path)
        if audio is not None:
            title = get_title(audio, file_path)
            if title:
                title = title.strip()
                sanitized_title = sanitize_filename(title)
                current_file_name = os.path.splitext(os.path.basename(file_path))[0].strip()
                new_file_name = sanitized_title + os.path.splitext(file_path)[1]
                new_file_path = os.path.join(os.path.dirname(file_path), new_file_name)
                if current_file_name != sanitized_title:
                    os.rename(file_path, new_file_path.strip())
                    print(f"'{current_file_name}' renamed to '{sanitized_title}'")
        else:
            print(f"Unsupported file format: {file_path}")
    except ID3NoHeaderError:
        print(f"No ID3 header found for '{file_path}'")
    except FileExistsError:
        print(f"----'{str(file_path).replace(folder_location, "")}' allready exest")
    except Exception as e:
        print(f"Error processing '{file_path}': {e}")

def rename_music_files_in_directory(directory):
    music_files = get_music_files(directory)
    for file_path in music_files:
        rename_music_file(file_path)

if __name__ == "__main__":
    rename_music_files_in_directory(folder_location)
