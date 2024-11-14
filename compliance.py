import re
import dns.resolver
import subprocess
import logging
from colorama import Fore, init, Style
from concurrent.futures import ThreadPoolExecutor, as_completed
from tabulate import tabulate
from utils import print_centered, format_date

init(autoreset=True)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def fetch_dns_record(domain, record_type, expected_prefix=None):
    try:
        logging.info(f"Fetching {record_type} records for domain: {domain}")
        answers = dns.resolver.resolve(domain, record_type)
        records = [rdata.strings[0].decode() if record_type == 'TXT' else str(rdata.exchange).rstrip('.') for rdata in answers]

        if records:
            logging.info(f"{record_type} records found: {records}")
        else:
            logging.warning(f"No {record_type} records found.")

        return records if expected_prefix is None else [record for record in records if record.startswith(expected_prefix)]
    except Exception as e:
        logging.error(f"Error occurred while fetching {record_type} records: {e}")
        return None if expected_prefix is None else []


def spf_check(domain):
    return fetch_dns_record(domain, 'TXT', expected_prefix="v=spf1")


def dmarc_check(domain):
    return fetch_dns_record(f"_dmarc.{domain}", 'TXT', expected_prefix="v=DMARC1")


def get_mx_records(domain):
    return fetch_dns_record(domain, 'MX')


def run_ssl_checks(mail_server):
    try:
        logging.info(f"Starting SSL/TLS check for {mail_server}")
        command = ["openssl", "s_client", "-starttls", "smtp", "-connect", f"{mail_server}:25"]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate(input="quit\n")

        if process.returncode != 0:
            logging.error(f"SSL check failed for {mail_server}: {stderr}")
            return None

        cert_subject_command = f"echo | openssl s_client -starttls smtp -connect {mail_server}:25 2>/dev/null | openssl x509 -noout -subject"
        cert_info_command = f"echo | openssl s_client -starttls smtp -connect {mail_server}:25 2>/dev/null | openssl x509 -noout -dates -text"

        subject_line = subprocess.getoutput(cert_subject_command).strip()
        cert_info = subprocess.getoutput(cert_info_command)

        protocol_match = re.search(r"New,\s*(TLSv\d+\.\d+)", stdout)
        tls_version = protocol_match.group(1) if protocol_match else "N/A"

        cn_match = re.search(r"CN\s*=\s*([^,]+)", subject_line)
        cn_value = cn_match.group(1) if cn_match else "N/A"

        valid_from_match = re.search(r"Not Before:\s+([A-Za-z0-9: ]+ GMT)", cert_info)
        valid_to_match = re.search(r"Not After :\s+([A-Za-z0-9: ]+ GMT)", cert_info)
        signature_match = re.search(r"Signature Algorithm:\s+(\S+)", cert_info)
        public_key_match = re.search(r"Public-Key:\s+\((\d+)\s+bit\)", cert_info)

        valid_from = format_date(valid_from_match.group(1)) if valid_from_match else "N/A"
        valid_to = format_date(valid_to_match.group(1)) if valid_to_match else "N/A"
        signature_type = signature_match.group(1) if signature_match else "N/A"
        public_key_size = f"{public_key_match.group(1)} bit" if public_key_match else "N/A"

        logging.info(f"SSL/TLS check completed for {mail_server}")
        return {
            "MX Host": mail_server,
            "Certificate Subject (CN)": cn_value,
            "Cert Validity": f"{valid_from} - {valid_to}",
            "Signature Type": signature_type,
            "Public Key Size": public_key_size,
            "TLS Version": tls_version.rstrip(',')
        }

    except Exception as e:
        logging.error(f"Error occurred during SSL check for {mail_server}: {e}")
        return None


def generate_report(domain, spf_record, dmarc_record, ssl_results):
    logging.info("Generating report...")
    print_centered("Report")
    print(f"{Fore.LIGHTCYAN_EX}{Style.BRIGHT}Domain:{Fore.RESET}{Style.RESET_ALL} {domain}")
    print(f"{Fore.LIGHTCYAN_EX}{Style.BRIGHT}SPF Record:{Fore.RESET}{Style.RESET_ALL} {spf_record}")
    print(f"{Fore.LIGHTCYAN_EX}{Style.BRIGHT}DMARC Record:{Fore.RESET}{Style.RESET_ALL} {dmarc_record}")
    print(f"{Fore.LIGHTCYAN_EX}{Style.BRIGHT}\nSSL/TLS Results:{Fore.RESET}{Style.RESET_ALL}")

    headers = ['Domain', 'Certificate Subject (CN)', 'TLS Version', 'Signature Type', 'Public Key Size', 'Cert Validity']
    table = []

    if ssl_results:
        for result in ssl_results:
            if result is not None:
                table.append([
                    result.get('MX Host', 'N/A'),
                    result.get('Certificate Subject (CN)', 'N/A'),
                    result.get('TLS Version', 'N/A'),
                    result.get('Signature Type', 'N/A'),
                    result.get('Public Key Size', 'N/A'),
                    result.get('Cert Validity', 'N/A')
                ])

        table_output = tabulate(table, headers=headers, tablefmt="pipe", stralign="center")
        print("\n\n")
        print(table_output)
        print("\n\n")
        logging.info("Report generated successfully.")
    else:
        logging.warning("No SSL/TLS information found.")


def run_tests(mail_servers):
    logging.info(f"Running tests for {len(mail_servers)} mail servers...")
    ssl_results = []
    with ThreadPoolExecutor(max_workers=1) as executor:  # Execute one by one
        futures = {executor.submit(run_ssl_checks, server): server for server in mail_servers}
        for future in as_completed(futures):
            server = futures[future]
            try:
                ssl_results.append(future.result())
            except Exception as e:
                logging.error(f"Error occurred during the test: {e}")
    logging.info(f"Completed tests for {len(ssl_results)} mail servers.")
    return ssl_results


def run_compliance_tests():
    domain = input(
        f"{Fore.LIGHTRED_EX}{Style.BRIGHT}> {Fore.LIGHTCYAN_EX}Enter the domain address: {Fore.RESET}{Style.RESET_ALL}")
    print_centered("Test Starting")
    logging.info(f"Started checks for domain: {domain}")

    spf_record = spf_check(domain)
    dmarc_record = dmarc_check(domain)
    mail_servers = get_mx_records(domain)

    ssl_results = run_tests(mail_servers) if mail_servers else None
    generate_report(domain, spf_record, dmarc_record, ssl_results)
    logging.info("Process completed successfully.")


if __name__ == "__main__":
    run_compliance_tests()