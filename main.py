import os
import cv2
import time
import random
import logging
import threading
import subprocess
import numpy as np
import tkinter as tk
import soundfile as sf
import sounddevice as sd
import pygetwindow as gw
import pyautogui
from PIL import ImageGrab
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from tkinter import ttk, messagebox

# Configure logging
logging.basicConfig(    
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ChromiumMeetingRecorder:
    def __init__(self, meeting_url, meeting_type):
        self.meeting_url = meeting_url
        self.meeting_type = meeting_type
        self.driver = None
        self.is_recording = False
        self.audio_stream = None
        self.video_writer = None
        self.recording_thread = None
        self.temp_dir = os.path.join(os.getenv('TEMP', 'C:\\temp'), 'meeting_records')
        os.makedirs(self.temp_dir, exist_ok=True)
        self.sample_rate = 44100
        self.channels = 2
        self.video_fps = 15

    def get_audio_devices(self):
        """List available audio input devices."""
        try:
            devices = sd.query_devices()
            input_devices = [d['name'] for d in devices if d['max_input_channels'] > 0]
            return input_devices
        except Exception as e:
            logger.error(f"Audio device error: {str(e)}")
            return []
    

    def check_devices(self):    
        # Camera check
        has_camera = False
        for i in range(3):  # Check first 3 camera indices
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                has_camera = True
                cap.release()
                break
            cap.release()

        # Microphone check
        has_microphone = False
        try:
            devices = sd.query_devices()
            has_microphone = any(d['max_input_channels'] > 0 for d in devices)
        except:
            pass

        return has_camera, has_microphone

    def setup_chromium_driver(self):
        """Configure Chrome to join meetings."""
        try:
            chrome_options = ChromeOptions()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument('--use-fake-device-for-media-stream')
            chrome_options.add_argument('--use-fake-ui-for-media-stream')
            # chrome_options.add_argument('--disable-webrtc-stun-origin')
            # chrome_options.add_argument('--disable-features=WebRtcHideLocalIpsWithMdns')
            # chrome_options.add_argument('--enable-unsafe-swiftshader')
            chrome_options.add_argument('--disable-infobars')
            chrome_options.add_argument('--disable-encryption')
            chrome_options.add_argument('--disable-popup-blocking')
            chrome_options.add_argument('--auto-accept-camera-capture')
            chrome_options.add_argument('--auto-accept-microphone-capture')            
            chrome_options.add_experimental_option('prefs', {
                'webrtc.ip_handling_policy': 'default_public_interface_only',
                'webrtc.use_legacy_tls_version': False,  # Force modern TLS
            })
            # Fake video (required for some meeting sites)
            fake_video = os.path.join(self.temp_dir, "fake_video.y4m")
            if not os.path.exists(fake_video):
                with open(fake_video, 'wb') as f:
                    f.write(b'YUV4MPEG2 W1280 H720 F30:1 Ip A0:0 C420jpeg XYSCSS=420JPEG\n')
                    f.write(b'FRAME\n')
                    f.write(b'\x80' * (1280 * 720 * 3 // 2))
            chrome_options.add_argument(f'--use-file-for-fake-video-capture={fake_video}')

            # Auto-download ChromeDriver
            service = ChromeService(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.implicitly_wait(15)
            
        except Exception as e:
            logger.error(f"Chrome setup failed: {str(e)}")
            raise

    def join_meeting(self):
        """Join Google Meet, Zoom, or Teams."""
        try:
            logger.info(f"Joining {self.meeting_type} meeting: {self.meeting_url}")
            self.driver.get(self.meeting_url)
            
            if self.meeting_type == 'google':
                self._join_google_meet()
            elif self.meeting_type == 'zoom':
                self._join_zoom_meeting()
            elif self.meeting_type == 'teams':
                self._join_teams_meeting()
                
            logger.info("Meeting joined successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to join meeting: {str(e)}")
            return False

    def _join_google_meet(self):
        """Google Meet joining logic."""
        try:
            mic_button = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Turn off microphone']"))
            )
            mic_button.click()
            video_button = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Turn off camera']"))
            )
            video_button.click()
            name_input = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "//input[@aria-label='Your name']"))
            )
            name_input.send_keys(f"User{random.randint(1000, 9999)}")
            
            join_button = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Ask to join') or contains(text(), 'Join now')]"))
            )
            join_button.click()
            time.sleep(5)  # Wait for meeting to load
            
        except Exception as e:
            logger.error(f"Google Meet error: {str(e)}")
            raise

    def _join_zoom_meeting(self):
        try:
            try:
                pyautogui.press('esc')  # Close any pop-ups
                time.sleep(1)                
            except Exception as e:
                logger.error(f"ESC key press error: {str(e)}")

            # Click "Launch Meeting" button (using class selector)
            launch_button = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "div.mbTuDeF1[role='button']"))
            )
            launch_button.click()
            logger.info("Clicked 'Launch Meeting' button")
            time.sleep(2)

            try:
                pyautogui.press('esc')  # Dismiss any additional pop-ups
                time.sleep(1)
            except Exception as e:
                logger.error(f"ESC key press error: {str(e)}")

            # Click "Join from your browser" link (using attribute selector)
            join_browser_link = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a[web_client][role='button']"))
            )
            join_browser_link.click()            
            logger.info("Clicked 'Join from your browser' link")
            
            iframe = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.ID, "webclient"))
            )
            self.driver.switch_to.frame(iframe)
            time.sleep(10)
            
            mic_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "preview-audio-control-button"))
            )
            mic_button.click()
            camera_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "preview-video-control-button"))
            )
            camera_button.click()
            logger.info("Clicked 'Turn off camera' and 'Turn off microphone' buttons")

            name_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "input-for-name"))
            )
            
            logger.warning(f"Enter random name {name_input}")

            random_name = f"User{random.randint(1000, 9999)}"
            name_input.clear()
            name_input.send_keys(random_name)
            logger.info(f"Entered name: {random_name}")
            time.sleep(1)

            # Click Join button
            join_button = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.preview-join-button"))
            )
            join_button.click()
            logger.info("Clicked 'Join' button")

            self.driver.switch_to.default_content()  # Switch back to main content
            pyautogui.press('esc')
            time.sleep(5)  # Wait for meeting to load
            logger.info("Waiting for meeting to load...")
            
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH,
                    "//div[contains(@class, 'pwa') or contains(@id, 'pwa-client')]"))
            )
            pyautogui.press('esc')
            logger.info("Zoom meeting joined successfully")
            return True

        except Exception as e:
            logger.error(f"Zoom meeting join failed: {str(e)}")
            self._take_screenshot("zoom_join_error")
            raise

    def _join_teams_meeting(self):
        try:
            try:
                pyautogui.press('esc')
                time.sleep(1)                
            except Exception as e:
                logger.error(f"JavaScript execution error: {str(e)}")

            continue_button = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, 
                    "//button[contains(@data-tid, 'joinOnWeb') or "
                    "contains(@aria-label, 'Join meeting from this browser')]"))
            )
            continue_button.click()
            logger.info("Clicked 'Continue on this browser' button")
            time.sleep(50)  # Wait for next screen to load

            pyautogui.press('esc')
            mic_button = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@data-tid='toggle-mute']"))
            )
            mic_button.click()
            logger.info("Toggled microphone")

            video_button = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@data-tid='toggle-video']"))
            )
            video_button.click()
            logger.info("Toggled video")
            name_input = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.XPATH,
                    "//input[@data-tid='prejoin-display-name-input' or "
                    "@placeholder='Type your name']"))
            )
            random_name = f"User{random.randint(1000, 9999)}"
            name_input.clear()
            name_input.send_keys(random_name)
            logger.info(f"Entered name: {random_name}")
            time.sleep(1)  # Let the name be processed
            

            join_button = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH,
                    "//button[@data-tid='prejoin-join-button' or "
                    "@aria-label='Join now' or "
                    "contains(text(), 'Join now')]"))
            )
            join_button.click()
            logger.info("Clicked 'Join now' button")

            WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.XPATH,
                    "//span[contains(@data-tid, 'call-duration') or "
                    "contains(@class, 'meeting-container')]"))
            )
            logger.info("Teams meeting joined successfully")
            return True

        except Exception as e:
            logger.error(f"Teams meeting join failed: {str(e)}")
            self._take_screenshot("teams_join_error")
            raise

    def _check_ffmpeg_installed(self):
        try:
            subprocess.run(['ffmpeg', '-version'],
                           check=True,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE
                           ),
            return True
        except:
            return False

    def start_recording(self):
        """Start audio + video recording."""
        if not self._check_ffmpeg_installed():
            messagebox.showwarning(
                "FFmpeg Not Found",
            )
        try:
            timestamp = int(time.time())
            self.audio_file = os.path.join(self.temp_dir, f"meeting_{timestamp}.wav")
            self.video_file = os.path.join(self.temp_dir, f"meeting_{timestamp}.mp4")
            self.output_file = os.path.join(self.temp_dir, f"meeting_final_{timestamp}.mp4")
            
            # Start audio recording
            self._start_audio_recording()
            
            # Start video recording in a thread
            self.recording_thread = threading.Thread(target=self._capture_video)
            self.recording_thread.start()
            
            self.is_recording = True
            logger.info("Recording started (audio + video)")
            
        except Exception as e:
            logger.error(f"Recording start failed: {str(e)}")
            raise

    def _start_audio_recording(self):
        """Capture microphone audio."""
        devices = self.get_audio_devices()
        if not devices:
            raise Exception("No audio input devices found")
        
        # Select first available microphone
        selected_device = next((d for d in devices if 'microphone' in d.lower()), devices[0])
        device_index = next((i for i, d in enumerate(sd.query_devices()) if d['name'] == selected_device), None)
        
        if device_index is None:
            raise Exception(f"Audio device not found: {selected_device}")
        
        self.frames = []
        def audio_callback(indata, frames, time, status):
            self.frames.append(indata.copy())
        
        self.audio_stream = sd.InputStream(
            device=device_index,
            channels=self.channels,
            samplerate=self.sample_rate,
            callback=audio_callback,
            dtype='float32'
        )
        self.audio_stream.start()

    def _capture_video(self):
        """Record only the browser window."""
        try:
            time.sleep(3)  # Wait for browser to open
            
            # Find Chrome window
            chrome_windows = [w for w in gw.getWindowsWithTitle('') 
                            if 'chrome' in w.title.lower() or 'meet' in w.title.lower() or 'zoom' in w.title.lower()]
            if not chrome_windows:
                raise Exception("Browser window not found")
            
            chrome_window = chrome_windows[0]
            width, height = chrome_window.width, chrome_window.height
            
            # Set up video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.video_writer = cv2.VideoWriter(
                self.video_file,
                fourcc,
                self.video_fps,
                (width, height)
            )
            
            while self.is_recording:
                try:
                    # Capture window region
                    img = ImageGrab.grab(bbox=(
                        chrome_window.left,
                        chrome_window.top,
                        chrome_window.left + width,
                        chrome_window.top + height
                    ))
                    frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                    self.video_writer.write(frame)
                    time.sleep(1 / self.video_fps)
                    
                except Exception as e:
                    logger.warning(f"Video capture warning: {str(e)}")
                    time.sleep(0.1)
                    
        except Exception as e:
            logger.error(f"Video capture failed: {str(e)}")
            raise

    def _merge_audio_video(self):
        """Combine audio (WAV) + video (MP4) into one file."""
        try:
            if not (os.path.exists(self.audio_file) and os.path.exists(self.video_file)):
                raise Exception("Audio/Video files missing")
            
            # Option 1: FFmpeg (faster)
            try:
                subprocess.run([
                    'ffmpeg', '-y',
                    '-i', self.video_file,
                    '-i', self.audio_file,
                    '-c:v', 'copy',
                    '-c:a', 'aac',
                    '-strict', 'experimental',
                    self.output_file
                ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                logger.info("Merged with FFmpeg")
                return
            except Exception:
                logger.warning("FFmpeg not available, using other method")
            
            # # Option 2: MoviePy (slower but Python-only)
            # video = VideoFileClip(self.video_file)
            # audio = AudioFileClip(self.audio_file)
            # video = video.set_audio(audio)
            # video.write_videofile(
            #     self.output_file,
            #     codec='libx264',
            #     audio_codec='aac',
            #     threads=4  # Use multiple threads for faster encoding
            # )
            # logger.info("Merged with MoviePy")
            
        except Exception as e:
            logger.error(f"Merge failed: {str(e)}")
            raise

    def stop_recording(self):
        if not self.is_recording:
            return
        
        self.is_recording = False
        
        if not hasattr(self, '_cleanup_performed'):
            self.cleanup_performed = True
            try:
                # Stop audio recording
                if hasattr(self, 'audio_stream') and self.audio_stream:
                    self.audio_stream.stop()
                    self.audio_stream.close()
                    
                    # Save audio to WAV
                    if hasattr(self, 'frames') and self.frames:
                        audio_data = np.concatenate(self.frames, axis=0)
                        sf.write(self.audio_file, audio_data, self.sample_rate)
                        logger.info(f"Audio saved: {self.audio_file}")

                # Stop video recording
                if hasattr(self, 'video_writer') and self.video_writer:
                    self.video_writer.release()
                    logger.info(f"Video saved: {self.video_file}")

                # Wait for threads to finish
                if hasattr(self, 'recording_thread') and self.recording_thread:
                    self.recording_thread.join(timeout=2)

                # Merge audio + video
                self._merge_audio_video()
                logger.info(f"Final recording: {self.output_file}")

            except Exception as e:
                logger.error(f"Stop error: {str(e)}")
                raise
            finally:
                self._cleanup()
                logger.info(f"Finished recording: {self.output_file}")

    def _cleanup(self):
        """Close resources."""
        try:
            if hasattr(self, 'driver') and self.driver:
                self.driver.quit()
            if hasattr(self, 'video_writer') and self.video_writer:
                self.video_writer.release()
            logger.info("Cleanup complete")
        except Exception as e:
            logger.error(f"Cleanup error: {str(e)}")

class MeetingRecorderUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Meeting Recorder")
        
        # UI Setup
        tk.Label(root, text="Meeting Type:").grid(row=0, column=0, padx=10, pady=5, sticky='e')
        self.meeting_type = ttk.Combobox(root, values=["google", "zoom", "teams"])
        self.meeting_type.current(0)
        self.meeting_type.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(root, text="Meeting URL:").grid(row=1, column=0, padx=10, pady=5, sticky='e')
        self.url_entry = tk.Entry(root, width=40)
        self.url_entry.grid(row=1, column=1, padx=10, pady=5)
        
        tk.Label(root, text="Duration (seconds):").grid(row=2, column=0, padx=10, pady=5, sticky='e')
        self.duration_entry = tk.Entry(root, width=40)
        self.duration_entry.grid(row=2, column=1, padx=10, pady=5)
        
        self.start_button = tk.Button(root, text="Start Recording", command=self.start_recording)
        self.start_button.grid(row=3, column=1, pady=10, sticky='e')
        
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        tk.Label(root, textvariable=self.status_var).grid(row=4, column=0, columnspan=2, pady=5)

    def start_recording(self):
        """Start recording in a background thread."""
        meeting_url = self.url_entry.get()
        meeting_type = self.meeting_type.get()
        duration = self.duration_entry.get()
        
        if not meeting_url:
            messagebox.showerror("Error", "Meeting URL is required")
            return
            
        try:
            duration = int(duration) if duration else None
        except ValueError:
            messagebox.showerror("Error", "Duration must be a number")
            return
            
        self.status_var.set("Starting...")
        self.start_button.config(state=tk.DISABLED)
        
        # Run in background thread
        threading.Thread(
            target=self._run_recording,
            args=(meeting_url, meeting_type, duration),
            daemon=True
        ).start()

    def _run_recording(self, meeting_url, meeting_type, duration):
        """Handle recording session."""
        recorder = None
        try:
            recorder = ChromiumMeetingRecorder(meeting_url, meeting_type)
            
            self.root.after(0, lambda: self.status_var.set("Setting up browser..."))
            recorder.setup_chromium_driver()
            
            self.root.after(0, lambda: self.status_var.set("Joining meeting..."))
            if not recorder.join_meeting():
                raise Exception("Failed to join meeting")
            
            self.root.after(0, lambda: self.status_var.set("Recording started!"))
            recorder.start_recording()
            
            # Countdown if duration specified
            if duration:
                for i in range(duration, 0, -1):
                    self.root.after(0, lambda i=i: self.status_var.set(f"Recording... {i}s left"))
                    time.sleep(1)
                recorder.stop_recording()
                self.root.after(0, lambda: self.status_var.set("Recording saved!"))
            else:
                self.root.after(0, lambda: self.status_var.set("Recording - Close to stop"))
                while True:
                    time.sleep(1)
                    
        except Exception as e:
            self.root.after(0, lambda: self.status_var.set(f"Error: {str(e)}"))
            logger.error(f"Recording failed: {str(e)}")
        finally:
            self.root.after(0, lambda: self.start_button.config(state=tk.NORMAL))
            if recorder:
                try:
                    recorder.stop_recording()
                except:
                    pass

def main():
    root = tk.Tk()
    app = MeetingRecorderUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()