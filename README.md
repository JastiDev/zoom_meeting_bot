# Automatic Meeting Recorder
This script automates the recording of online meetings on Google Meet, Zoom, and Microsoft Teams using a headless Chromium browser.

## Features
  - Records both audio and video from meetings
  
  - Supports Google Meet, Zoom, and Microsoft Teams
  
  - Automatically stops recording when meeting ends
  
  - Saves recordings in MP4 format with synchronized audio
  
  - Simple graphical user interface

## Requirements
  - Python 3.7+
  
  - Windows OS (for screen capture functionality)
  
  - Stable internet connection
  
  - Google Chrome browser installed

## Installation
  1. Clone this repository or download the script file.
  
  2. Install the required Python packages:

      ```
      pip install -r requirements.txt
      ```
      Or install them manually:
          
        ```
        pip install opencv-python numpy pyautogui selenium sounddevice soundfile pygetwindow moviepy webdriver-manager
        ```
      
### Usage
  1. Run the script:
 
   ```
   python mian.py
   ```
    
  2. In the GUI that appears:
    - Select the meeting type (Google Meet, Zoom, or Teams)
    - Enter the meeting URL
    - Optionally select a save location (defaults to temporary folder)
    - Click "Start Recording"
  
  3.  The script will:  
    - Open a Chrome window and join the meeting
    - Begin recording automatically        
    - Stop recording when the meeting ends or after a period of inactivity    
    - Save the final recording to the specified location

## Notes
  - For Zoom and Teams, the script joins via browser which may have some limitations compared to the desktop apps
  
  - The recording quality depends on your internet speed and system resources
  
  - Make sure your microphone and camera permissions are enabled for Chrome
  
  - The script runs in the background - you can minimize the GUI window after starting

## Troubleshooting
If you encounter issues:

1. Check that all dependencies are installed

2. Ensure you have the latest version of Google Chrome

3. Verify the meeting URL is correct

4. Check your microphone and camera permissions

5. Look for error messages in the console output

For privacy considerations, please ensure you have permission to record any meetings before using this tool.
