import os
import time
import socket  # Added import for socket
import win32file
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import getpass

# Email configuration
SMTP_SERVER = 'smtp.example.com'
SMTP_PORT = 25  # Change to the appropriate port for your SMTP server
EMAIL_ADDRESS = 'UsbAlerts@example.com'
# No EMAIL_PASSWORD needed in this case
RECIPIENT_EMAIL = 'security@example.com'

def get_computer_info():
    # Get the computer's IP address
    ip_address = socket.gethostbyname(socket.gethostname())

    # Get the computer name
    computer_name = os.environ['COMPUTERNAME']

    return ip_address, computer_name


def send_email(subject, message):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = subject

    ip_address, computer_name = get_computer_info()
    username = getpass.getuser()

    # Include IP address, computer name, and username in the message
    full_message = f"IP Address: {ip_address}\nComputer Name: {computer_name}\nLogged-in User: {username}\n\n{message}"

    msg.attach(MIMEText(full_message, 'plain'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        text = msg.as_string()
        server.sendmail(EMAIL_ADDRESS, RECIPIENT_EMAIL, text)
        server.quit()
        print("Email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")


def check_usb_drives(detected_drives):
    drives = [d for d in range(ord('A'), ord('Z') + 1) if os.path.exists(f"{chr(d)}:\\")]
    for drive in drives:
        drive_name = f"{chr(drive)}:\\"
        drive_type = win32file.GetDriveType(drive_name)
        if drive_type == win32file.DRIVE_REMOVABLE:
            if drive_name not in detected_drives:
                message = f"USB drive detected: {drive_name}"
                print(message)
                detected_drives.add(drive_name)
                send_email("USB Drive Inserted", message)


detected_drives = set()

while True:
    check_usb_drives(detected_drives)
    time.sleep(10)
