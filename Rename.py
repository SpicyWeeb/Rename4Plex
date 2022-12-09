import os
import re
import time

# Define the directories
source_dir = r"C:\Users\Main\Desktop\done"
target_dir = r"C:\Users\Main\Desktop\renamed"

# Define the regex pattern for removing everything inside brackets and parentheses
pattern = r"\[.*?\]|\(.*?\)"

# Loop indefinitely
while True:
    # Get a list of all files in the source directory
    files = os.listdir(source_dir)
    
    # Loop through the files
    for file in files:
        # Remove everything inside brackets and parentheses using the regex pattern
        new_name = re.sub(pattern, "", file)
        
        # Split the file name at " - "
        parts = new_name.split(" - ")
        
        # If there are less than 2 parts, skip this file
        if len(parts) < 2:
            continue
        
        # Get the show name, season and episode details
        show_name = parts[0].strip()
        season_episode = parts[1].strip()
        
        # Check if the show name ends with "Sx", where x is a number. If it does, extract the season number
        # and add it to the season_episode string. Also, remove the "Sx" part from the show name.
        match = re.search(r"S(\d+)$", show_name, re.IGNORECASE)
        if match:
            season_number = match.group(1)
            season_episode = "S" + season_number.zfill(2) + season_episode
            show_name = show_name[:-len(match.group(0))].strip()
        
        # If there are more than 2 digits after the "S", assume that they are episode numbers and
        # add "E" before the numbers
        if len(season_episode[1:]) > 2:
            season_episode = "S" + season_episode[1:3] + "E" + season_episode[3:]
        
        # If the season and episode details do not start with "S" and "E", assume that it is just the episode number
        # and add "S01E" before the numbers
        if not season_episode.startswith("S") and not season_episode.startswith("E"):
            season_episode = "S01E" + season_episode
        
        # Remove any spaces after the season and episode details
        season_episode = season_episode.replace(" ", "")
        
        # Compute the new file name
        new_file_name = show_name + " - " + season_episode
        
        # Compute the full path of the source and target files
        old_file_path = os.path.join(source_dir, file)
        
        # Create a new directory for the show, if it doesn't already exist
        show_dir = os.path.join(target_dir, show_name)
        os.makedirs(show_dir, exist_ok=True)
        
        # Compute the full path of the new file, including the new show directory
        new_file_path = os.path.join(show_dir, new_file_name)
        
        # Try to rename the file
        try:
            os.rename(old_file_path, new_file_path)
        except OSError as e:
            # If the error is WinError 32, print a message and wait for 5 seconds before continuing
            if e.winerror == 32:
                print("Error: The file is being used by another process")
                time.sleep(5)
            # If the error is WinError 183, print a message and try to replace the file
            elif e.winerror == 183:
                print("Error: The file already exists, replaceing it.")
                os.replace(old_file_path, new_file_path)
            # Otherwise, re-raise the error
            else:
                raise e
                
    # Sleep for 5 seconds before checking for new files again
    time.sleep(5)
