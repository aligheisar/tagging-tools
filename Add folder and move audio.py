import os
from shutil import move
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3NoHeaderError

def get_music_files(directory):
    extensions = ('.mp3', '.flac', '.m4a', '.aac', '.wav', '.ogg', '.wma')

    music_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(extensions):
                music_files.append(os.path.join(root, file))
    return music_files

def move_files_by_album_artist(music_files, destination):
    for file_path in music_files:
        try:
            audio = EasyID3(file_path)
            if 'albumartist' in audio:
                album_artist = audio['albumartist'][0]
                new_folder = os.path.join(destination, album_artist)
                if not os.path.exists(new_folder):
                    os.makedirs(new_folder)
                new_file_path = os.path.join(new_folder, os.path.basename(file_path))
                move(file_path, new_file_path)
                print(f"Moved '{file_path}' to '{new_file_path}'")
            else:
                print(f"No album artist tag found for '{file_path}', skipping.")
        except ID3NoHeaderError:
            print(f"No ID3 header found for '{file_path}', skipping.")
        except Exception as e:
            print(f"Error processing '{file_path}': {e}")

if __name__ == "__main__":
    source_location = input("Enter the source directory: ")
    source_location = source_location.replace("\\", "/")
    if not source_location.endswith("/"):
        source_location += "/"

    destination_location = input("Enter the destination directory: ")
    destination_location = destination_location.replace("\\", "/")
    if not destination_location.endswith("/"):
        destination_location += "/"

    music_files = get_music_files(source_location)
    if music_files:
        move_files_by_album_artist(music_files, destination_location)
        print("Job complete.")
    else:
        print("No music files found in the source directory.")
