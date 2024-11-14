import yaml
from colorama import Fore, Style
from mail import reports

def generate_report(template_titles):
    table_data = []

    for report in reports:
        status_icons = {
            "Inbox": "✔" if report['status'] == 'Inbox' else "",
            "Spam": "✔" if report['status'] == 'Spam' else "",
            "Blocked": "✔" if report['status'] == 'Blocked' else ""
        }

        title = template_titles.get(report['template'], 'No Title')

        table_data.append([
            title,
            report['subject'],
            status_icons['Inbox'],
            status_icons['Spam'],
            status_icons['Blocked'],
            report.get('attachment_path', "N/A")
        ])

    headers = ['Mail Template', 'Mail Subject', 'Inbox', 'Spam', 'Not Bypassed', 'Attachment Path']
    max_lengths = [max(len(str(row[i])) for row in [headers] + table_data) for i in range(len(headers))]

    header_row = " | ".join(f"{headers[i]:<{max_lengths[i]}}" for i in range(len(headers)))
    print(header_row)
    print("-" * len(header_row))

    for row in table_data:
        print(" | ".join(f"{str(row[i]):<{max_lengths[i]}}" for i in range(len(row))))

    print(Fore.LIGHTYELLOW_EX + "\nAll reports completed. Exiting the script." + Style.RESET_ALL)
    exit()

def load_template_titles():
    template_titles = {}
    for report in reports:
        template_file = f"./templates/{report['template']}"
        try:
            with open(template_file, 'r') as f:
                template_data = yaml.safe_load(f)
                template_titles[report['template']] = template_data.get('Title', 'No Title')
        except FileNotFoundError:
            print(Fore.RED + f"Template file '{template_file}' not found." + Style.RESET_ALL)
            template_titles[report['template']] = 'No Title'
        except yaml.YAMLError:
            print(Fore.RED + f"Error reading YAML from '{template_file}'." + Style.RESET_ALL)
            template_titles[report['template']] = 'No Title'
    return template_titles

def report_menu():
    if not reports:
        print("No reports available to display.")
        return

    template_titles = load_template_titles()

    for report in reports:
        title = template_titles.get(report['template'], 'No Title')
        print(f"\n{Fore.LIGHTCYAN_EX}Template Title:{Style.RESET_ALL} {title}")
        print(f"{Fore.LIGHTCYAN_EX}Mail Subject:{Style.RESET_ALL} {report['subject']}")
        print(f"{Fore.LIGHTCYAN_EX}Reference ID:{Style.RESET_ALL} {report['reference_id']}")
        print("Select status: ")
        print("1. Inbox")
        print("2. Spam")
        print("3. Not (not seen)")

        status_choice = input( Fore.LIGHTCYAN_EX + "Enter the number corresponding to the status: " + Style.RESET_ALL).strip()
        status_map = {'1': 'Inbox', '2': 'Spam', '3': 'Blocked'}

        if status_choice in status_map:
            report['status'] = status_map[status_choice]
        else:
            print(Fore.RED + "Invalid choice. Status not updated." + Style.RESET_ALL)

    generate_report(template_titles)
