import os
import time
import threading
import sounddevice as sd
import numpy as np
import soundfile as sf
from pyscreenrec import ScreenRecorder
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from datetime import datetime

class MeetingBot:
    def __init__(self):
        self.recording = False
        self.audio_frames = []
        self.output_dir = os.path.join(os.path.expanduser('~'), 'Desktop', 'MeetingRecords')
        os.makedirs(self.output_dir, exist_ok=True)
        
    def kill_chromium_processes(self):
        """Kill all Chromium processes before starting"""
        try:
            os.system('taskkill /f /im chromium.exe')
            os.system('taskkill /f /im chromedriver.exe')
            time.sleep(2)
        except:
            pass

    def audio_callback(self, indata, frames, time, status):
        """Audio capture callback"""
        if self.recording:
            self.audio_frames.append(indata.copy())

    def start_recording(self):
        """Start synchronized recording"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.video_file = os.path.join(self.output_dir, f"meeting_{timestamp}_video.mp4")
        self.audio_file = os.path.join(self.output_dir, f"meeting_{timestamp}_audio.wav")
        self.final_file = os.path.join(self.output_dir, f"meeting_{timestamp}.mp4")

        # Start screen recording
        self.screen_rec = ScreenRecorder()
        self.screen_rec.start_recording(
            save_as=self.video_file,
            fps=30,
            region=(0, 0, 1280, 720)
        )
        
        # Start audio recording
        self.sample_rate = 44100
        self.audio_frames = []
        self.recording = True
        self.audio_stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=2,
            callback=self.audio_callback,
            dtype='float32'
        )
        self.audio_stream.start()
        
        print(f"Recording started to {self.output_dir}")

    def stop_recording(self):
        """Stop and finalize recording"""
        self.recording = False
        
        # Stop screen recording
        self.screen_rec.stop_recording()
        
        # Stop audio recording
        self.audio_stream.stop()
        self.audio_stream.close()
        
        # Save audio
        sf.write(self.audio_file, np.concatenate(self.audio_frames), self.sample_rate)
        
        # Combine audio/video (optional - requires moviepy)
        # self.combine_audio_video()
        
        print(f"Recording saved to {self.output_dir}")

    def create_profile(self):
        """Create Chromium profile for meetings"""
        self.kill_chromium_processes()
        
        local_app_data = os.getenv('LOCALAPPDATA')
        user_data_dir = os.path.join(local_app_data, 'Chromium', 'User Data')
        profile_dir = "meetingbot"
        os.makedirs(os.path.join(user_data_dir, profile_dir), exist_ok=True)
        
        options = Options()
        options.add_argument(f"--user-data-dir={user_data_dir}")
        options.add_argument(f"--profile-directory={profile_dir}")
        options.add_argument("--no-first-run")
        options.add_argument("--no-default-browser-check")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--remote-debugging-port=9222")
        options.binary_location = r"C:\Path\To\Chromium\Application\chromium.exe"
        
        service = Service(executable_path=r".\chromedriver.exe")
        
        try:
            driver = webdriver.Chrome(service=service, options=options)
            driver.get("chrome://version/")
            print("Profile created at:", driver.capabilities["chrome"]["userDataDir"])
            driver.quit()
            return True
        except Exception as e:
            print(f"Profile creation failed: {str(e)}")
            return False

    def list_audio_devices(self):
        """Display available recording devices"""
        print("\nAvailable Audio Input Devices:")
        devices = sd.query_devices()
        for i, dev in enumerate(devices):
            if dev['max_input_channels'] > 0:
                print(f"{i}: {dev['name']} (Inputs: {dev['max_input_channels']})")

if __name__ == "__main__":
    bot = MeetingBot()
    
    # Create profile first
    if bot.create_profile():
        # Show recording devices
        bot.list_audio_devices()
        
        # Start meeting recording
        input("\nPress Enter to start recording...")
        bot.start_recording()
        
        # Stop recording
        input("Press Enter to stop recording...")
        bot.stop_recording()