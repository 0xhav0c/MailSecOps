import os
import yaml
import sys
from tabulate import tabulate
from colorama import Fore, Style
from utils import print_centered


def list_templates(template_type=None):
    templates_path = "./templates"
    yml_files = [f for f in os.listdir(templates_path) if f.endswith('.yml')]

    if not yml_files:
        print(Fore.LIGHTRED_EX + "No templates found." + Style.RESET_ALL)
        return []

    templates_info = []
    for file in yml_files:
        template_file = os.path.join(templates_path, file)
        try:
            with open(template_file, 'r') as f:
                template_data = yaml.safe_load(f)
                title = template_data.get('Title', 'No Title')
                order = template_data.get('Order', float('inf'))
                t_type = template_data.get('type', 'default')

                if template_type is None or t_type == template_type:
                    templates_info.append((file, title, order))

        except yaml.YAMLError:
            print(Fore.RED + f"Error reading YAML from '{template_file}'." + Style.RESET_ALL)
            continue

    templates_info.sort(key=lambda x: x[2])

    headers = ["#", "Template Title"]
    table_data = [(str(idx).center(2), title) for idx, (_, title, _) in enumerate(templates_info, 1)]

    table_text = tabulate(table_data, headers, tablefmt="psql")
    print(Fore.LIGHTYELLOW_EX + "Available email templates (sorted by Order):" + Style.RESET_ALL)
    print_centered(table_text)

    return [file for file, _, _ in templates_info]


def choose_template(templates):
    prompt_text = Fore.LIGHTRED_EX + "> " + Fore.LIGHTCYAN_EX + "Select a template by number: " + Style.RESET_ALL
    exit_message = Fore.LIGHTRED_EX + Style.BRIGHT + "Exiting the script. Thank you for using the tool!" + Style.RESET_ALL

    while True:
        choice = input(prompt_text).strip().lower()

        if choice == 'back':
            print(Fore.LIGHTCYAN_EX + "Returning to the previous menu..." + Style.RESET_ALL)
            return None
        elif choice == 'exit':
            print(exit_message)
            sys.exit()

        try:
            choice_idx = int(choice)
            if 1 <= choice_idx <= len(templates):
                selected_template = templates[choice_idx - 1]
                print(f"{Fore.LIGHTCYAN_EX}You have selected the template:{Style.RESET_ALL} {selected_template}")
                return selected_template
        except ValueError:
            pass

        print(Fore.LIGHTRED_EX + "Invalid selection. Please enter a number." + Style.RESET_ALL)
