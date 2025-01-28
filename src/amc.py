import requests
import csv
import lxml.etree
import json
import os
from typing import List, Tuple


def generate_amc_ids():
    """Fetch AMC IDs from AMFI website."""
    url = "https://www.amfiindia.com/research-information/other-data/scheme-details"
    response = requests.get(url)
    response.raise_for_status()

    # Find all option values in the HTML content
    content = response.text
    amc_ids = []

    # Simple parsing to extract values from option tags
    for line in content.split('\n'):
        if 'option value="' in line:
            try:
                value = line.split('option value="')[1].split('"')[0]
                fund_name = line.split('option value="')[1].split('>')[1].split('<')[0]
                if value.isdigit():
                    yield (value, fund_name)
            except IndexError:
                continue

    return sorted(amc_ids)


def fetch_fund_ids(amc_id: str) -> List[Tuple[str, str]]:
    """Fetch fund IDs for a given AMC ID."""
    url = 'https://www.amfiindia.com/modules/FetchSchemeFromMFID'
    headers = {
        "X-Requested-With": "XMLHttpRequest"
    }
    data = {
        "ID": amc_id
    }

    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()

    funds = response.json()
    funds_list = [(fund['Value'], fund['Text']) for fund in funds if int(fund['Value']) > 0]
    # The MF is no longer alive
    if len(funds_list) > 0:
        if funds_list[0][0] == "-1":
            return []
        else:
            return funds_list
    else:
        return []


def write_to_csv(data: List[Tuple[str, str]], filename: str = 'amfi_funds.csv'):
    """Write AMC and Fund IDs to CSV file."""
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['AMC_ID', 'MF_ID', 'MF_NAME'])  # Write headers
        writer.writerows(data)


def download_fund_ssd(fund_id: str, fund_name: str, amc_name: str):
    file_name = f'details/{fund_id}.xml'
    if not os.path.exists(file_name):
        url = f"https://portal.amfiindia.com/spages/SSD_{fund_id}.xml"
        response = requests.get(url)

        if response.status_code == 404:
            return
        elif response.status_code != 200:
            response.raise_for_status()

        with open(file_name, 'wb') as f:
            f.write(response.content)
            print(f"\"{amc_name}\", {fund_id}, \"{fund_name}\", DOWNLOADED")


def main():

    all_data = []
    for amc_id, amc_name in generate_amc_ids():
        for fund_id, fund_name in fetch_fund_ids(amc_id):
            download_fund_ssd(fund_id, fund_name, amc_name)
            all_data.append((amc_id, fund_id, fund_name))

    write_to_csv(all_data)


if __name__ == "__main__":
    main()
