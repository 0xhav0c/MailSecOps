import readline
import sys
import compliance
from colorama import init, Fore, Style
from tabulate import tabulate
from assesment import get_exchange_info, mail_spoofing_menu, malware_spoofing_menu
from malware import create_malware
from report import report_menu
from utils import print_centered, delete_malwares_dir_contents, check_msfvenom


# ASCII Banner
ascii_banner = """
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⠿⠿⠿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠋⠀⠀⢠⣴⡄⠈⠻⢿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠛⠁⠀⠈⠀⠀⠀⠀⠀⠉⠁⠀⠀⣀⣀⣀⣉⣻⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣶⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⢠⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⠀⠀⠀⠀⠀⠀⣠⣄⠘⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⠃⠀⠀⠀⠀⠀⠀⠹⠛⣀⡉⠙⢿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⡏⠀⠀⠀⠀⠀⠀⠀⠀⢿⣿⣿⣿⣮⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣇⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⣶⣦⣤⣴⣶⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
"""

# Main menu
def main_menu():
    init(autoreset=True)
    show_banner = True
    menu_items = [
        ("1", "Mail Spoofing - Send spoofed emails"),
        ("2", "Send Malware with Spoofing"),
        ("3", "SPF, DMARC, SSL/TLS Check"),
        ("4", "Malware Create (msfvenom)"),
        ("5", "Reports - Create sended mail reports"),
        ("6", "Delete created malware files"),
        ("7", "Exit - Exit the script"),
    ]
    headers = ["#", "Menu Item"]

    while True:
        try:
            if show_banner:
                print_centered(ascii_banner)
                print_centered("Welcome to MailSecOps. Perform tests from the options below.")
                print_centered("!!! If you want to send the malware files, create malwares before sending spoofed mails.")
                show_banner = False

            print_centered(tabulate(menu_items, headers, tablefmt="psql"))

            prompt_text = (
                Fore.LIGHTRED_EX + "> " +
                Fore.LIGHTCYAN_EX + "Choose an option (1-7 or type " +
                Fore.LIGHTRED_EX + Style.BRIGHT + "exit" +
                Fore.LIGHTCYAN_EX + "):" +
                Style.RESET_ALL
            )
            choice = input(prompt_text).strip().lower()
            readline.add_history(choice)

            if choice == 'exit' or choice == '7':
                print_centered("Exiting the script. Thank you for using the tool!", Fore.LIGHTRED_EX)
                sys.exit()
            elif choice == '1':
                exchange_server, port = get_exchange_info()
                mail_spoofing_menu(exchange_server, port)
            elif choice == '2':
                exchange_server, port = get_exchange_info()
                malware_spoofing_menu(exchange_server, port)
            elif choice == '3':
                compliance.run_compliance_tests()
            elif choice == '4':
                if check_msfvenom():
                    create_malware()
            elif choice == '5':
                report_menu()
            elif choice == '6':
                print_centered("Cleaning created Malware files", Fore.LIGHTRED_EX)
                delete_malwares_dir_contents()
            else:
                print_centered("Invalid choice. Please try again with a number between 1-7.", Fore.LIGHTRED_EX)

        except KeyboardInterrupt:
            print_centered("Exiting the script. Thank you for using the tool!", Fore.LIGHTRED_EX)
            sys.exit()

if __name__ == "__main__":
    main_menu()
