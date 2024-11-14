import os
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders
from colorama import Fore, Style
from utils import generate_malwared_reference_id


# Mail send function
def send_mail(template_data, sender_email, recipient_email, exchange_server, port, reference_id, template_choice):
    subject_base = template_data['subject'].split('(Ref:')[0]
    subject = subject_base + f"(Ref: {reference_id})"
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = recipient_email

    body = MIMEText(template_data['body'], 'html')
    msg.attach(body)

    attachment_path = "N/A"  # Attachment yok varsayımı

    try:
        with smtplib.SMTP(exchange_server, port) as server:
            server.set_debuglevel(0)
            server.sendmail(sender_email, recipient_email, msg.as_string())
            print(f"Mail sent to {recipient_email} with reference_id {reference_id} without any attachment successfully.")
    except Exception as e:
        print(f"Failed to send mail due to the following error: {str(e)}")
        reports.append({
            'template': template_choice,
            'reference_id': reference_id,
            'status': None,
            'subject': subject,
            'attachment_path': attachment_path  # Attachment bilgisi eklendi
        })
        return

    reports.append({
        'template': template_choice,
        'reference_id': reference_id,
        'status': 'sent',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'subject': subject,
        'attachment_path': attachment_path  # Attachment bilgisi eklendi
    })


def select_malware():
    user_input = input(
        Fore.LIGHTCYAN_EX + "Send only one malware or send all malwares in ./attachments/malwares/? (" +
        Fore.LIGHTGREEN_EX + Style.BRIGHT + "single" +
        Fore.LIGHTCYAN_EX + "/" +
        Fore.LIGHTYELLOW_EX + Style.BRIGHT + "all" +
        Fore.LIGHTCYAN_EX + "): " +
        Style.RESET_ALL
    ).strip().lower()
    malware_files = []

    if user_input == 'single':
        malware_folder = './attachments/malwares/'
        malware_files = [f for f in os.listdir(malware_folder) if os.path.isfile(os.path.join(malware_folder, f))]
        if not malware_files:
            print("There are no files in the folder. Please add malware files or create malwares from main menu.")
            return None

        print("Available malware files:")
        for index, filename in enumerate(malware_files):
            file_size = os.path.getsize(os.path.join(malware_folder, filename)) / 1024
            print(f"{index + 1}. {filename} - {file_size:.2f} KB")

        while True:
            try:
                choice = int(input("Which file would you like to attach? (enter number): "))
                if 1 <= choice <= len(malware_files):
                    selected_file = os.path.join(malware_folder, malware_files[choice - 1])
                    return [selected_file]
                else:
                    print("Invalid selection, please try again.")
            except ValueError:
                print("Please enter a valid number.")

    elif user_input == 'all':
        malware_folder = './attachments/malwares/'
        malware_files = [os.path.join(malware_folder, f) for f in os.listdir(malware_folder) if
                         os.path.isfile(os.path.join(malware_folder, f))]

        if not malware_files:
            print("There are no files in the folder. Please add malware files or create malwares from main menu.")
            return None

        return malware_files

    else:
        return None


# Mail send function for malware
def send_malware(template_data, sender_email, recipient_email, exchange_server, port, template_choice):
    malware_files = select_malware()
    if malware_files is None:
        print("No malware file selected.")
        return

    for malware_file in malware_files:
        malwared_reference_id = generate_malwared_reference_id()
        subject_base = template_data['subject'].split('(Ref:')[0]
        subject = subject_base + f"(Ref: {malwared_reference_id})"

        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = recipient_email

        body = MIMEText(template_data['body'], 'html')
        msg.attach(body)

        attachment_path = malware_file  # Attachment varsa dosya yolu atanıyor

        try:
            with open(malware_file, 'rb') as file:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(file.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(malware_file)}')
                msg.attach(part)

            with smtplib.SMTP(exchange_server, port) as server:
                server.sendmail(sender_email, recipient_email, msg.as_string())
                print(f"Mail sent to {recipient_email} with attachment {os.path.basename(malware_file)} and malwared_reference_id {malwared_reference_id} successfully.")

        except Exception as e:
            print(f"Failed to send mail due to the following error: {str(e)}")
            reports.append({
                'template': template_choice,
                'reference_id': malwared_reference_id,
                'status': 'failed',
                'subject': subject,
                'attachment_path': attachment_path  # Attachment bilgisi eklendi
            })
            return

        reports.append({
            'template': template_choice,
            'reference_id': malwared_reference_id,
            'status': 'sent',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'subject': subject,
            'attachment_path': attachment_path  # Attachment bilgisi eklendi
        })


reports = []
