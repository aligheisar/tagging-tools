#!/usr/bin/env python3

import os
from mutagen.mp3 import MP3 # Still useful for general MP3 info if needed
from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC
from mutagen.id3 import ID3NoHeaderError, ID3, error as ID3Error # Import ID3 for completeness, but EasyID3 is preferred for MP3s here
from mutagen.mp4 import MP4 # Assuming you might need this later for M4A

def prompt_directory():
    dir_path = input("Please enter the path to your music directory: ")
    if not os.path.isdir(dir_path):
        print("Error: Directory not found.")
        exit(1)
    return dir_path

def split_tags(tags):
    # Converts comma-separated string to list (multi-value)
    if isinstance(tags, list):
        return tags
    elif isinstance(tags, str):
        return [t.strip() for t in tags.split(",") if t.strip()]
    return []

def join_tags(tags):
    # Converts list to comma-separated string
    if isinstance(tags, list):
        return ", ".join(tags)
    elif isinstance(tags, str):
        return tags
    return ""

def process_flac(file_path, split=True):
    try:
        audio = FLAC(file_path)
        changed = False

        for field in ['artist', 'albumartist']:
            if field in audio:
                current_values = audio[field]
                if split:
                    # Convert comma string to list
                    if isinstance(current_values, str):
                        new_value = split_tags(current_values)
                        if new_value and new_value != current_values:
                            audio[field] = new_value
                            changed = True
                else:
                    # Convert list to comma string
                    if isinstance(current_values, list):
                        new_value = join_tags(current_values)
                        if new_value and new_value != current_values:
                            audio[field] = new_value
                            changed = True

        if changed:
            audio.save()
            print(f"Updated FLAC: {os.path.basename(file_path)}")
    except Exception as e:
        print(f"Error processing FLAC {file_path}: {e}")

def process_mp3(file_path, split=True):
    """
    Processes MP3 files to adjust artist/albumartist tag separators.
    Uses EasyID3 for simpler tag manipulation.
    """
    try:
        # Attempt to load the MP3 file using EasyID3
        # EasyID3 automatically handles cases where tags might not exist initially
        audio = EasyID3(file_path)
        
        # If EasyID3 succeeds, it means tags are accessible or can be created.
        # Now, let's process the fields.
        
        fields_to_process = ["artist", "albumartist"] # These are EasyID3 keys
        changed = False

        for field_name in fields_to_process:
            if field_name in audio:
                current_values = audio[field_name] # This is a list of strings

                if split:
                    # Split each string in the list by comma or semicolon
                    processed_values = []
                    for val in current_values:
                        # Split by comma or semicolon, strip whitespace, and add if not empty
                        items = [item.strip() for item in val.replace(',', ';').split(';') if item.strip()]
                        processed_values.extend(items)
                    
                    # Remove duplicates and sort to ensure consistent order (optional but good practice)
                    unique_values = sorted(list(set(processed_values)))

                    # Only update if the processed list is different from the current list
                    if unique_values != current_values:
                        audio[field_name] = unique_values
                        changed = True
                        print(f"Split '{field_name}' in {os.path.basename(file_path)}: {current_values} -> {unique_values}")
                else: # reverse=True, join values
                    # Join the list of values into a single comma-separated string
                    joined_value = ", ".join(current_values)
                    
                    # Only update if the joined string is different from the current single string value
                    # EasyID3 stores multi-value tags as a list, so we compare against the first element if it's a single string.
                    # A more robust check: if the list has more than one item, join them.
                    if len(current_values) > 1:
                         joined_value_from_list = ", ".join(current_values)
                         if joined_value_from_list != current_values[0] or len(current_values) > 1: # Check if joining is needed or if list representation differs
                             audio[field_name] = [joined_value_from_list] # Assign back as a list with the single joined string
                             changed = True
                             print(f"Joined '{field_name}' in {os.path.basename(file_path)}: {current_values} -> {joined_value_from_list}")
                    # If there's only one value, we don't need to join it, but maybe we need to normalize it.
                    # For now, let's assume if len is 1, it's already "joined".

            # Note: EasyID3 doesn't automatically create tags if they don't exist.
            # If a tag is missing, it won't be added by this logic.
            # This script focuses on modifying existing tags.

        if changed:
            audio.save()
            print(f"Successfully saved tags for {os.path.basename(file_path)}")

    except ID3NoHeaderError:
        # This exception is raised by EasyID3 if the file has no ID3 tags at all.
        # We can choose to create a new tag or skip the file.
        # For this script, skipping seems appropriate as we're modifying existing tags.
        print(f"No ID3 header found for '{os.path.basename(file_path)}'. Skipping.")
        return # Exit the function if no header
        
    except Exception as e:
        # Catch any other potential errors during file processing or tag manipulation
        print(f"General Error processing MP3 '{os.path.basename(file_path)}': {e}")

def process_m4a(file_path, split=True):
    try:
        audio = MP4(file_path)
        changed = False

        for field_key, display_field in [('\xa9ART', 'Artist'), ('aART', 'Album Artist')]:
            if field_key in audio.tags:
                current_values = audio.tags[field_key]
                if split:
                    new_value = split_tags(current_values)
                    if list(current_values) != new_value:
                        audi.tags[field_key] = new_value
                        changed = True
                else:
                    new_value = join_tags(current_values)
                    if new_value != list(current_values)[0]:
                        audio.tags[field_key] = new_value
                        changed = True

        if changed:
            audio.save()
            print(f"Updated M4A: {os.path.basename(file_path)}")
    except Exception as e:
        print(f"Error processing M4A {file_path}: {e}")

def main():
    dir_path = prompt_directory()
    if not dir_path:
        return

    while True:
        choice = input("Type 'split' to convert comma to multi-value, or 'combine' to merge multi-value to comma: ").strip().lower()
        if choice in ['split', 'combine']:
            break
        else:
            print("Invalid choice. Please enter 'split' or 'combine'.")

    split_mode = choice == 'split'

    for root, _, files in os.walk(dir_path):
        for filename in files:
            file_path = os.path.join(root, filename)
            ext = os.path.splitext(filename)[1].lower()

            if ext == ".flac":
                process_flac(file_path, split=split_mode)
            elif ext == ".mp3":
                process_mp3(file_path, split=split_mode)
            elif ext in [".m4a", ".mp4"]: # .mp4 is also common for M4A audio
                process_m4a(file_path, split=split_mode)

if __name__ == "__main__":
    main()
