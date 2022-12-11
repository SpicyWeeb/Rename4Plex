import sys
from PyQt5 import QtWidgets, QtCore

app = QtWidgets.QApplication(sys.argv)
window = QtWidgets.QMainWindow()
window.setWindowTitle("Rename4Plex")

def browse_directory(line_edit):
    # Get the directory from a QFileDialog
    directory = QtWidgets.QFileDialog.getExistingDirectory()

    # Set the text of the line edit to the selected directory
    line_edit.setText(directory)

# Create a layout for the "TV Shows" tab
tab_widget = QtWidgets.QTabWidget()

# Add any widgets you want to the "TV Shows" tab layout
# Create a checkbox and a spin box
checkbox = QtWidgets.QCheckBox("Enable")
spinbox = QtWidgets.QSpinBox()

# Set the minimum and maximum values for the spin box
spinbox.setMinimum(1)
spinbox.setMaximum(999999)

# Set the default value for the spin box
spinbox.setValue(5)

# Set the minimum width for the spin box
spinbox.setMaximumWidth(100)

# Create a timer
timer = QtCore.QTimer()

# Connect the timer's timeout signal to a lambda function that will call the on_checkbox_toggled function with the checked value from the checkbox
timer.timeout.connect(lambda: on_checkbox_toggled(checkbox.isChecked()))

# Start the timer when the checkbox is enabled
checkbox.toggled.connect(lambda checked: timer.start() if checked else timer.stop())

# Connect the spin box's valueChanged signal to a lambda function that will set the timer's interval
spinbox.valueChanged.connect(lambda value: timer.setInterval(value * 1000))

# Create a layout and add the checkbox, spin box, and label to it
tv_shows_layout = QtWidgets.QVBoxLayout()
tv_shows_layout.addWidget(checkbox)
label = QtWidgets.QLabel("How long the code will wait before running again")
tv_shows_layout.addWidget(label)
tv_shows_layout.addWidget(spinbox)

# Create the line edit widgets for the directories
source_directory_edit = QtWidgets.QLineEdit()
target_directory_edit = QtWidgets.QLineEdit()

# Create the "Browse" buttons
source_browse_button = QtWidgets.QPushButton("Browse")
target_browse_button = QtWidgets.QPushButton("Browse")

# Connect the "Browse" buttons to the browse_directory slot function
source_browse_button.clicked.connect(lambda: browse_directory(source_directory_edit))
target_browse_button.clicked.connect(lambda: browse_directory(target_directory_edit))

# Create the line edit widgets for the directories
source_directory_edit = QtWidgets.QLineEdit()
target_directory_edit = QtWidgets.QLineEdit()

# Set the placeholder text for the line edit widgets
source_directory_edit.setPlaceholderText("Enter the source directory")
target_directory_edit.setPlaceholderText("Enter the target directory")

# Add the line edit widgets and the "Browse" buttons to the "TV Shows" tab layout
tv_shows_layout.addWidget(source_directory_edit)
tv_shows_layout.addWidget(source_browse_button)
tv_shows_layout.addWidget(target_directory_edit)
tv_shows_layout.addWidget(target_browse_button)

# Create a widget to hold the layout, and set it as the central widget for the main window
tv_shows_widget = QtWidgets.QWidget()
tv_shows_widget.setLayout(tv_shows_layout)

# Create a widget to hold the contents of the "TV Shows" tab
tv_shows_tab_contents = QtWidgets.QWidget()

# Set the layout for the "TV Shows" tab widget contents
tv_shows_tab_contents.setLayout(tv_shows_layout)

# Add the "TV Shows" tab to the tab widget
tab_widget.addTab(tv_shows_tab_contents, "TV Shows")

def on_checkbox_toggled(checked):
    if checked:
        import os
        import re
        import time
        import shutil
        
        # Define the directories
        source_dir = source_directory_edit.text()
        target_dir = target_directory_edit.text()
        
        # get all files in source_dir and its subdirectories
        all_files = []
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                all_files.append(os.path.join(root, file))

        # move all files to the source_dir
        for file in all_files:
            shutil.move(file, source_dir)

        # delete all empty subdirectories
        for root, dirs, files in os.walk(source_dir, topdown=False):
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
        
        # Define the regex pattern for removing everything inside brackets and parentheses
        pattern = r"\[.*?\]|\(.*?\)"

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
                season_episode = "S" + season_number.zfill(2) + "E" + season_episode
                show_name = show_name[:-len(match.group(0))].strip()
                
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

        pass

checkbox.stateChanged.connect(on_checkbox_toggled)

# Create a layout for the "Movies" tab
movies_layout = QtWidgets.QVBoxLayout()

# Add any widgets you want to the "Movies" tab layout
label = QtWidgets.QLabel("Nothing here yet")
movies_layout.addWidget(label)

# Create a widget to hold the "Movies" tab layout
movies_widget = QtWidgets.QWidget()
movies_widget.setLayout(movies_layout)

# Create a widget to hold the contents of the "Movies" tab
movies_tab_contents = QtWidgets.QWidget()

# Set the layout for the "Movies" tab widget contents
movies_tab_contents.setLayout(movies_layout)

# Add the "Movies" tab to the tab widget
tab_widget.addTab(movies_tab_contents, "Movies")

# Create a layout for the "Music" tab
music_layout = QtWidgets.QVBoxLayout()

# Add any widgets you want to the "Music" tab layout
label = QtWidgets.QLabel("Working on one thing at a time")
music_layout.addWidget(label)

# Create a widget to hold the "Music" tab layout
music_widget = QtWidgets.QWidget()
music_widget.setLayout(music_layout)

# Create a widget to hold the contents of the "Music" tab
music_tab_contents = QtWidgets.QWidget()

# Set the layout for the "Music" tab widget contents
music_tab_contents.setLayout(music_layout)

# Add the "Music" tab to the tab widget
tab_widget.addTab(music_tab_contents, "Music")

# Add the tab widget to your main window
window.setCentralWidget(tab_widget)

window.show()
app.exec_()
