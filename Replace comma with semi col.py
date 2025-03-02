import os
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, ID3NoHeaderError
from mutagen.flac import FLAC
from mutagen.mp4 import MP4
from mutagen.mp4 import MP4Tags

os.system("cls")

def get_music_files(directory):
    extensions = ('.mp3', '.flac', '.m4a', '.aac', '.wav', '.ogg', '.wma')
    music_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(extensions):
                music_files.append(os.path.join(root, file))
    return music_files

def get_audio_file(file_path):
    if file_path.lower().endswith('.mp3'):
        return EasyID3(file_path)
    elif file_path.lower().endswith('.flac'):
        return FLAC(file_path)
    elif file_path.lower().endswith('.m4a'):
        return MP4(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_path}")

def save_audio_file(audio, file_path):
    if isinstance(audio, EasyID3) or isinstance(audio, ID3):
        audio.save()
    elif isinstance(audio, FLAC):
        audio.save()
    elif isinstance(audio, MP4):
        audio.save()
    else:
        raise ValueError(f"Unsupported file format: {file_path}")

def fix_title(file_path, modified_files):
    try:
        audio = get_audio_file(file_path)
        if isinstance(audio, (EasyID3, FLAC, MP4Tags)):
            if "title" in audio:
                original_title = audio["title"][0]
                has_comma = False
                has_semicol = False
                has_space = False
                for i, char in enumerate(original_title):
                    if char == "," or char == ";":
                        if char == ",":
                            has_comma = True
                        elif char == ";":
                            has_semicol = True
                        if i < len(original_title) - 1 and original_title[i + 1] == " ":
                            has_space = True
                if has_semicol and has_space:
                    new_title = original_title.replace(";", ",")
                elif has_semicol and not has_space:
                    new_title = original_title.replace(";", ", ")
                elif has_comma and not has_space:
                    new_title = original_title.replace(",", ", ")
                else:
                    new_title = original_title

                if new_title != original_title:
                    audio["title"] = new_title
                    save_audio_file(audio, file_path)
                    modified_files.add(file_path)
            else:
                print(f"title tag not found for '{os.path.basename(file_path)}'")
    except ID3NoHeaderError:
        print(f"No ID3 header found for '{os.path.basename(file_path)}'")
    except Exception as e:
        print(f"Error processing '{os.path.basename(file_path)}': {e}")

def replace_comma_with_semicol(file_path, reverse=True, field_name="artist", modified_files=None):
    try:
        audio = get_audio_file(file_path)
        if isinstance(audio, (EasyID3, FLAC, MP4Tags)):
            if field_name in audio:
                original_value = audio[field_name][0]
                has_comma = False
                has_semicol = False
                has_space = False
                for i, char in enumerate(original_value):
                    if char == ',' or char == ";":
                        if char == ",":
                            has_comma = True
                        elif char == ";":
                            has_semicol = True
                        if i < len(original_value) - 1 and original_value[i + 1] == ' ':
                            has_space = True
                if reverse:
                    if has_semicol and has_space:
                        new_value = original_value.replace(";", ",")
                    elif has_semicol and not has_space:
                        new_value = original_value.replace(";", ", ")
                    elif has_comma and not has_space:
                        new_value = original_value.replace(",", ", ")
                    else:
                        new_value = original_value
                else:
                    if has_comma and has_space:
                        new_value = original_value.replace(",", ";")
                    elif has_comma and not has_space:
                        new_value = original_value.replace(",", "; ")
                    elif has_semicol and not has_space:
                        new_value = original_value.replace(";", "; ")
                    else:
                        new_value = original_value

                if new_value != original_value:
                    audio[field_name] = new_value
                    save_audio_file(audio, file_path)
                    modified_files.add(file_path)
            else:
                print(f"{field_name} tag not found for '{os.path.basename(file_path)}'")
    except ID3NoHeaderError:
        print(f"No ID3 header found for '{os.path.basename(file_path)}'")
    except Exception as e:
        print(f"Error processing '{os.path.basename(file_path)}': {e}")

def tag_in_dir(directory):
    modified_files = set()
    music_files = get_music_files(directory)
    for file_path in music_files:
        fix_title(file_path, modified_files)
        replace_comma_with_semicol(file_path, False, "artist", modified_files)
        replace_comma_with_semicol(file_path, False, "albumartist", modified_files)
    
    modified_folders = set(os.path.dirname(file_path) for file_path in modified_files)
    print("\nFolders with modified files:")
    for folder in modified_folders:
        print(folder)

if __name__ == "__main__":
    while True:
        folder_location = input("Enter a Path: ")
        folder_location = folder_location.replace("\\", "/")
        if not folder_location.endswith("/"):
            folder_location += "/"
        if not os.path.exists(folder_location):
            print("Folder doesn't exist")
            continue
        break
    
    tag_in_dir(folder_location)
