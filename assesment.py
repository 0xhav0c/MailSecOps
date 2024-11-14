import yaml
from templates import list_templates, choose_template
from utils import is_valid_email, generate_reference_id, is_valid_ip, is_valid_domain, is_valid_port, check_connection
from mail import send_mail, send_malware
from colorama import Fore, Style

def get_exchange_info():
    print("To perform mail tests, you need to enter the domain or IP address of the relevant mail server.")
    while True:
        while True:
            exchange_server = input(
                Fore.LIGHTRED_EX + "> " + Fore.LIGHTCYAN_EX + "Enter the Exchange server address" + Fore.LIGHTRED_EX + " = > " + Style.RESET_ALL)
            if is_valid_ip(exchange_server) or is_valid_domain(exchange_server):
                break
            else:
                print(Fore.LIGHTRED_EX + "Invalid input. Please enter a valid domain or IP address." + Style.RESET_ALL)

        while True:
            port_number = input(Fore.LIGHTRED_EX + "> " + Fore.LIGHTCYAN_EX + "Enter the port number for Exchange server" + Fore.LIGHTRED_EX + " = > " + Style.RESET_ALL)
            if is_valid_port(port_number):
                break
            else:
                print(Fore.LIGHTRED_EX + "Invalid input. Please enter a valid port number (1-65535)." + Style.RESET_ALL)

        if check_connection(exchange_server, port_number):
            print(Fore.LIGHTGREEN_EX + "Connection successful!" + Style.RESET_ALL)
            break
        else:
            print(Fore.LIGHTRED_EX + "Connection failed. Please check the server address and port number." + Style.RESET_ALL)

    return exchange_server, port_number

def mail_spoofing_menu(exchange_server, port):
    while True:
        templates = list_templates(template_type='spoof')
        if not templates:
            break
        template_choice = choose_template(templates)
        if template_choice is None:
            break
        template_path = f"./templates/{template_choice}"
        with open(template_path, 'r') as file:
            template_data = yaml.safe_load(file)

        print(f"\nDescription: {template_data.get('description', 'No Description')}")
        sender_address = input(Fore.LIGHTRED_EX + "> " + Fore.LIGHTCYAN_EX + "Enter the sender email address" + Fore.LIGHTRED_EX + " = > " + Style.RESET_ALL)
        while not is_valid_email(sender_address):
            print("\033[1;31m" + "Invalid email address. Please try again." + "\033[0m")
            sender_address = input(Fore.LIGHTRED_EX + "> " + Fore.LIGHTCYAN_EX + "Enter the sender email address" + Fore.LIGHTRED_EX + " = > " + Style.RESET_ALL)

        target_address = input(Fore.LIGHTRED_EX + "> " + Fore.LIGHTCYAN_EX + "Enter the target email address" + Fore.LIGHTRED_EX + " = > " + Style.RESET_ALL)
        while not is_valid_email(target_address):
            print("\033[1;31m" + "Invalid email address. Please try again." + "\033[0m")
            target_address = input(Fore.LIGHTRED_EX + "> " + Fore.LIGHTCYAN_EX + "Enter the target email address" + Fore.LIGHTRED_EX + " = > " + Style.RESET_ALL)

        reference_id = generate_reference_id()

        send_mail(template_data, sender_address, target_address, exchange_server, port, reference_id, template_choice)

        another_test = input(
            Fore.LIGHTRED_EX + "> " +
            Fore.LIGHTCYAN_EX + "Do you want to perform another test? (" +
            Fore.GREEN + Style.BRIGHT + "yes" +
            Fore.LIGHTCYAN_EX + "/" +
            Fore.LIGHTRED_EX + Style.BRIGHT + "no" +
            Fore.LIGHTCYAN_EX + ") " +
            Fore.LIGHTRED_EX + "= > " +
            Style.RESET_ALL
        ).strip().lower()
        if another_test != 'yes':
            break # başka test yoksa kaç :P


def malware_spoofing_menu(exchange_server, port):
    while True:
        templates = list_templates(template_type='malware')
        if not templates:
            break
        template_choice = choose_template(templates)
        if template_choice is None:
            break
        template_path = f"./templates/{template_choice}"
        with open(template_path, 'r') as file:
            template_data = yaml.safe_load(file)

        print(f"\nDescription: {template_data.get('description', 'No Description')}")
        sender_address = input(Fore.LIGHTRED_EX + "> " + Fore.LIGHTCYAN_EX + "Enter the sender email address" + Fore.LIGHTRED_EX + " = > " + Style.RESET_ALL)
        while not is_valid_email(sender_address):
            print("\033[1;31m" + "Invalid email address. Please try again." + "\033[0m")
            sender_address = input(Fore.LIGHTRED_EX + "> " + Fore.LIGHTCYAN_EX + "Enter the sender email address" + Fore.LIGHTRED_EX + " = > " + Style.RESET_ALL)

        target_address = input(Fore.LIGHTRED_EX + "> " + Fore.LIGHTCYAN_EX + "Enter the target email address" + Fore.LIGHTRED_EX + " = > " + Style.RESET_ALL)
        while not is_valid_email(target_address):
            print("\033[1;31m" + "Invalid email address. Please try again." + "\033[0m")
            target_address = input(Fore.LIGHTRED_EX + "> " + Fore.LIGHTCYAN_EX + "Enter the target email address" + Fore.LIGHTRED_EX + " = > " + Style.RESET_ALL)

        send_malware(template_data, sender_address, target_address, exchange_server, port, template_choice)

        # Yeni test için kullanıcıya soralım
        another_test = input(
            Fore.LIGHTRED_EX + "> " +
            Fore.LIGHTCYAN_EX + "Do you want to perform another test? (" +
            Fore.GREEN + Style.BRIGHT + "yes" +
            Fore.LIGHTCYAN_EX + "/" +
            Fore.LIGHTRED_EX + Style.BRIGHT + "no" +
            Fore.LIGHTCYAN_EX + ") " +
            Fore.LIGHTRED_EX + "= > " +
            Style.RESET_ALL
        ).strip().lower()
        if another_test != 'yes':
            break # başka test yoksa kaç :P