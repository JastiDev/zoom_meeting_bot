# Chromium Meeting Recorder
An automated tool to record Google Meet, Zoom, and Microsoft Teams meetings using Selenium and Chromium.

## Features
  - Automatically joins meetings with fake camera/microphone
  
  - Records both audio and video
  
  - Monitors meeting activity and stops when empty
  
  - Supports Google Meet, Zoom, and Microsoft Teams
  
  - Generates timestamped output files

## Requirements
  - Python 3.7+
  
  - Chrome or Chromium browser
  
  - FFmpeg (for audio/video merging)

## Installation
  1. Clone the repository or download the script

  2. Install dependencies:

      ```
      pip install -r requirements.txt
      ```

3. Install FFmpeg:

    - **Windows**: Download from FFmpeg website
    
    - **Mac**: brew install ffmpeg
    
    - **Linux**: sudo apt install ffmpeg

## Usage
### Basic command:

```
python meeting_recorder.py https://meet.google.com/abc-xyz-def --output ./recordings
```

### Arguments:

  - **meeting_url**: URL of the meeting to join (required)
  
  - **--output** or **-o**: Output directory for recordings (optional)

## Notes
  - The script uses fake media devices to join meetings anonymously
  
  - Recording stops automatically when meeting becomes empty
  
  - Output files are saved as meeting_final_[timestamp].mp4

## Troubleshooting
  1. If you get WebDriver errors:

      - Make sure Chrome/Chromium is installed

      - Check your Chrome version matches the WebDriver version

  2. For audio recording issues:

      - Verify your system has audio input devices
      
      - Check system permissions for microphone access

  3. For video quality issues:

      - Adjust the video_fps parameter in the script (line 45)


## Additional Notes:
1. The script creates temporary files during recording which are automatically cleaned up.

2. For best results, run the script on a machine with:

    - Minimum 8GB RAM
    
    - Stable internet connection
    
    - Chrome/Chromium browser installed

3. First run may take longer as it downloads the appropriate ChromeDriver.
