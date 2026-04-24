import os
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, ID3NoHeaderError
from mutagen.flac import FLAC

def get_music_files(directory):
    extensions = ('.mp3', '.flac', '.m4a', '.aac', '.ogg', '.wma')
    music_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(extensions):
                music_files.append(os.path.join(root, file))
    return music_files

def get_audio_file(file_path):
    try:
        if file_path.lower().endswith('.mp3'):
            return EasyID3(file_path)
        elif file_path.lower().endswith('.flac'):
            return FLAC(file_path)
        else:
            raise ValueError(f"Unsupported file format for tagging: {os.path.basename(file_path)}")
    except ID3NoHeaderError:
        print(f"No ID3 header found for '{os.path.basename(file_path)}'. Skipping.")
        return None
    except Exception as e:
        print(f"Error opening file '{os.path.basename(file_path)}': {e}")
        return None

def save_audio_file(audio, file_path):
    try:
        audio.save()
        print(f"Saved tags for: {os.path.basename(file_path)}")
    except Exception as e:
        print(f"Error saving tags for '{os.path.basename(file_path)}': {e}")

def adjust_separator_in_field(file_path, reverse=False, fields=[], modified_files=None):
    if modified_files is None:
        modified_files = set()

    audio = get_audio_file(file_path)
    if audio is None:
        return
    
    is_dirty = False

    for field_name in fields:
        tag_key = None
        original_value = None
        
        try:
            if isinstance(audio, EasyID3):
                tag_key = field_name
                if tag_key in audio:
                    target_tag = audio[tag_key]
                    new_items = []
                    for i, val in enumerate(target_tag):
                        if ("," in val or ";" in val):
                            temp = target_tag[i].replace(",", ";").split(";")
                            for item in temp:
                                new_items.append(item.strip())
                        else:
                            new_items.append(val)
                    original_value = new_items
            elif isinstance(audio, FLAC):
                tag_key = field_name
                if tag_key in audio:
                    original_value = audio[tag_key][0]

            if original_value is not None and tag_key is not None:
                new_value = original_value
                
                if reverse:
                    new_value = '; '.join(original_value)
                else:
                    new_value = ', '.join(original_value)

                if new_value != audio[tag_key][0]:
                    if isinstance(audio, EasyID3) or isinstance(audio, FLAC):
                        audio[tag_key] = new_value
                        is_dirty = True
            else:
                print(f"'{field_name}' tag not found or empty for '{os.path.basename(file_path)}'")
                    
        except Exception as e:
            print(f"Error processing '{field_name}' for '{os.path.basename(file_path)}': {e}")
    if is_dirty:
        save_audio_file(audio, file_path)
        modified_files.add(file_path)

def tag_in_dir(directory):
    modified_files = set()
    music_files = get_music_files(directory)
    
    print(f"Found {len(music_files)} music files. Processing tags...")

    for file_path in music_files:
        adjust_separator_in_field(file_path, reverse=False, fields=["albumartist", "artist"], modified_files=modified_files)

    if modified_files:
        print(f"\nSuccessfully modified tags in {len(modified_files)} files.")
        modified_folders = set(os.path.dirname(file_path) for file_path in modified_files)
        print("\nFolders with modified files:")
        for folder in sorted(list(modified_folders)):
            print(folder)
    else:
        print("\nNo files were modified.")


if __name__ == "__main__":
    while True:
        folder_location = input("Enter the directory path containing your music files: ")
        folder_location = folder_location.strip().replace("\\", "/")
        
        if not folder_location:
            print("Path cannot be empty. Please try again.")
            continue
            
        if not os.path.isdir(folder_location):
            print(f"Error: The path '{folder_location}' does not exist or is not a directory. Please check and try again.")
            continue
        
        if not folder_location.endswith("/"):
            folder_location += "/"
            
        break
    
    tag_in_dir(folder_location)

