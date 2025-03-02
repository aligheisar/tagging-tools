import os
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, ID3NoHeaderError

while True:
    folder_location = input("Enter a Path: ")
    if not os.path.exists(folder_location):
        print("Folder dosn't exist")
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

def add_remix_to_title(file_path):
    try:
        audio = EasyID3(file_path)
        if 'title' in audio:
            title = audio['title'][0]
            if title.lower().endswith("(remix)"):
                title = title.replace(" (Remix)", "")
                audio['title'] = title
                audio.save()
                print(f"Added ' - DJ Remix' to title for '{file_path}'")
            else:
                print(f"Title already contains '(remix)' for '{file_path}'")
        else:
            print(f"Title tag not found for '{file_path}'")
    except ID3NoHeaderError:
        print(f"No ID3 header found for '{file_path}'")
    except Exception as e:
        print(f"Error processing '{file_path}': {e}")

def add_remix_to_titles_in_directory(directory):
    music_files = get_music_files(directory)
    for file_path in music_files:
        add_remix_to_title(file_path)

def check_folder_exists(directory):
    if os.path.exists(directory):
        if os.path.isdir(directory):
            return True
        else:
            print(f"The path '{directory}' exists but is not a directory.")
            return False
    else:
        print(f"The directory '{directory}' does not exist.")
        return False

if __name__ == "__main__":
    add_remix_to_titles_in_directory(folder_location)
