import os
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3NoHeaderError

# Ask the user for the folder and target text
while True:
    folder_location = input("Enter a Path: ").strip()
    if not os.path.exists(folder_location):
        print("Folder doesn't exist. Please try again.")
        continue
    if not os.path.isdir(folder_location):
        print(f"The path '{folder_location}' exists but is not a directory.")
        continue
    break

folder_location = folder_location.replace("\\", "/")
if not folder_location.endswith("/"):
    folder_location += "/"

target_remove = input("Enter the text you want to remove from song titles: ").strip()

# --- Utility Functions ---
def get_music_files(directory):
    """Collect all audio files in the folder and subfolders."""
    extensions = ('.mp3', '.flac', '.m4a', '.aac', '.wav', '.ogg', '.wma')
    music_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(extensions):
                music_files.append(os.path.join(root, file))
    return music_files


def remove_text_from_title(file_path, target_text):
    """Remove target text from title tags of an audio file."""
    try:
        audio = EasyID3(file_path)
        if 'title' in audio:
            title = audio['title'][0]
            new_title = title.replace(target_text, '').replace(target_text.lower(), '').replace(target_text.upper(), '').strip()
            if new_title != title:
                audio['title'] = new_title
                audio.save()
                print(f"Updated title for '{file_path}' → '{new_title}'")
        else:
            print(f"Title tag not found for '{file_path}'")
    except ID3NoHeaderError:
        print(f"No ID3 header found for '{file_path}'")
    except Exception as e:
        print(f"Error processing '{file_path}': {e}")


def remove_text_in_directory(directory, target_text):
    """Apply text removal to all audio files in given folder."""
    music_files = get_music_files(directory)
    for file_path in music_files:
        remove_text_from_title(file_path, target_text)


# --- Main Execution ---
if __name__ == "__main__":
    print(f"Processing folder: {folder_location}")
    print(f"Removing text: '{target_remove}' from all song titles...")
    remove_text_in_directory(folder_location, target_remove)
    print("\nDone ✅")

