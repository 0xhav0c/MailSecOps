import os
import random
import shutil
import re
import socket
import subprocess
import logging
from colorama import Style
from termcolor import colored
from datetime import datetime

def get_terminal_width():
    try:
        return os.get_terminal_size().columns
    except OSError:
        return 80

def format_date(date_str):
    try:
        date_obj = datetime.strptime(date_str, "%b %d %H:%M:%S %Y GMT")
        logging.info(f"Formatted date: {date_str} to {date_obj.strftime('%d/%m/%Y')}")
        return date_obj.strftime("%d/%m/%Y")
    except ValueError:
        logging.error(f"Date formatting failed for {date_str}")
        return "N/A"

def generate_reference_id():
    return ''.join(random.choices('0123456789', k=6))

def generate_malwared_reference_id():
    return ''.join(random.choices('0123456789', k=6))

def delete_malwares_dir_contents():
    dir_path = "./attachments/malwares/"
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            file_path = os.path.join(root, file)
            os.remove(file_path)
            print(f"Deleted: {file_path}")

        for dir in dirs:
            dir_path = os.path.join(root, dir)
            shutil.rmtree(dir_path)
            print(f"Deleted: {dir_path}")


def check_msfvenom():
    try:
        result = subprocess.run(
            ['echo', 'no |', 'msfvenom', '-h'],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5
        )
        return True
    except subprocess.TimeoutExpired:
        print("msfvenom installation is not complete. Please perform initial settings. Returning to main menu...")
    except FileNotFoundError:
        print("msfvenom is not installed, operation is not possible. Returning to main menu...")
    except subprocess.CalledProcessError:
        print("An error occurred while running the msfvenom command. Returning to the main menu...")
    return False


def print_centered(text, color=None):
    terminal_width = os.get_terminal_size().columns
    for line in text.strip().split("\n"):
        if color:
            print(color + line.center(terminal_width) + Style.RESET_ALL)
        else:
            print(line.center(terminal_width))


def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email) is not None


def is_valid_ip(ip):
    octets = ip.split('.')
    return len(octets) == 4 and all(o.isdigit() and 0 <= int(o) <= 255 for o in octets)


def is_valid_domain(domain):
    pattern = r'^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.[A-Za-z]{2,})+$'
    if not re.match(pattern, domain):
        return False
    try:
        socket.gethostbyname(domain)
        return True
    except socket.gaierror:
        return False


def is_valid_port(port):
    return port.isdigit() and 1 <= int(port) <= 65535


def check_connection(exchange_server, port):
    try:
        with socket.create_connection((exchange_server, int(port)), timeout=5):
            return True
    except (socket.timeout, socket.error):
        return False


def check_special_commands(input_text):
    commands = {
        "exit": ("Exiting the program...", "red", exit),
        "back": ("Returning to the previous menu...", "yellow", lambda: "back"),
        "ctrl+c": ("Program interrupted by user", "red", exit)
    }

    command_info = commands.get(input_text.lower())
    if command_info:
        print(colored(command_info[0], command_info[1]))
        return command_info[2]()
    return None

def prompt_input(prompt_text):
    while True:
        user_input = input(prompt_text).strip()
        command_result = check_special_commands(user_input)
        if command_result == "back":
            return "back"
        return user_input

