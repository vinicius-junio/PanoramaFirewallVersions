from logging.config import listen
import requests
import urllib3
import requests
import logging
import xml.etree.ElementTree as ET
import os
import xlsxwriter
import licenses as Licenses

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

list_tags = ["serial", "connected", "unsupported-version", "hostname", "ip-address", "ipv6-address", "mac-addr", "uptime", "family", "model", "sw-version",
             "app-version", "av-version", "wildfire-version", "threat-version", "url-db", "url-filtering-version", "logdb-version",
             "vpnclient-package-version", "global-protect-client-package-version", "prev-app-version", "prev-av-version", "prev-threat-version",
             "prev-wildfire-version", "domain", "vpn-disable-mode", "operational-mode", "certificate-status", "certificate-subject-name", "certificate-expiry",
             "connected-at", "custom-certificate-usage", "multi-vsys", "last-masterkey-push-status", "last-masterkey-push-timestamp", "express-mode",
             "device-cert-present", "device-cert-expiry-date"]

class WebService():
    #
    # Connect API Server
    #
    def __init__(self, keys: list[str], user: str, password: str) -> None:
        self.keys = keys
        self.credential = {
            'type': 'keygen',
            'user': user,
            'password': password,
        }

    def get_credential(self, url: str) -> str:
        service = "{}/api/".format(url)
        response = requests.post(service, params=self.credential, verify=False)

        status_code = response.status_code
        if(status_code != 200):
            raise Exception("StatusCode {} != 200".format(status_code))

        return ET.fromstring(response.text).findall('result')[0].find('key').text

    def get_firewall_info(self, url: str, credential: str) -> list[str]:
        url = "{}/api/?key={}&type=op&cmd=<show><devices><all></all></devices></show>".format(
            url, credential)
        response = requests.post(url, verify=False)

        status_code = response.status_code
        if status_code != 200:
            raise Exception("StatusCode {} != 200".format(status_code))

        doc = ET.fromstring(response.text)
        session = doc.find('result')
        devices = session.find('devices')

        listEntry = []

        for entry in devices.findall("entry"):

            values = []
            for tag in self.keys:

                element = entry.find(tag)
                if type(element) == type(None):
                    values.append("NULL")
                else:
                    values.append('"{}"'.format(element.text))

            listEntry.append(values)

        return listEntry

    def get_firewall_info_license(self, url: str, credential: str) -> Licenses.Response:
        url = "{}/api/?key={}&type=op&cmd=<request><batch><license><info></info></license></batch></request>".format(
            url, credential)
        response = requests.post(url, verify=False)
        status_code = response.status_code
        if status_code != 200:
            raise Exception("StatusCode {} != 200".format(status_code))
        return Licenses.Response.from_string(response.text)


class Discover:
    #
    # Search IP's (Panorama)
    #
    def __init__(self, file: str) -> None:
        with open(file, 'r') as f:
            self.urls = f.read().splitlines()

class TableLicenses():

    def __init__(self, file: str, name: str) -> None:
        self.row = 1
        self.col = 0
        self.total = 0
        self.workbook = xlsxwriter.Workbook(file)
        self.worksheet = self.workbook.add_worksheet(name)
        self.fields = ['name', 'type', 'feature-description',
                               'expiry-date', 'warning']

    def insert_information_license(self, response: Licenses.Response):
        for entry in response.result.devices.entry:
            self.col = 0
            self.worksheet.write(self.row, self.col, entry.serial_no)
            self.col += 1
            self.worksheet.write(self.row, self.col, entry.devicename)
            self.col += 1
            self.total = max(len(entry.licenses.licenses_entry), self.total)
            for license in entry.licenses.licenses_entry:
                data = license.to_dict()
                for key in self.fields:
                    key = key.replace("-", "_")
                    if key in data:
                        self.worksheet.write(self.row, self.col, data[key])
                    self.col += 1

            self.row += 1

    def insert_format(self):
        columns = [{'header': "serial-no"}, {'header': "devicename"}]
        for i in range(0, self.total):
            for field in self.fields:
                columns.append({'header': "%s-%i" % (field, i)})
        max_cols = len(columns)
        table = {
            'name': "Licenses",
            'columns': columns
        }
        self.worksheet.add_table(0, 0, self.row -1, max_cols, table)

    def close(self) -> None:
        self.workbook.close()

class TableFirewall():
    def __init__(self, path, nameFile) -> None:

        self.max_devices = 0

        self.row = 0
        self.col = 0
        self.workbook = xlsxwriter.Workbook(path)
        self.worksheet = self.workbook.add_worksheet(nameFile)

    def create_table(self, keys: list[str]):
        for i in range(0, len(keys)):
            self.worksheet.write(self.row, i, keys[i])

    def insert_information(self, value: list[list[str]]):
        for entry in value:
            self.row += 1
            self.col = 0
            for tag in entry:
                if isinstance(tag, str):
                    tag = tag.replace('"', '').strip()
                self.worksheet.write(self.row, self.col, tag)
                self.col += 1

    def insert_format(self):
        header_full = []
        for j in list_tags:
            header_full.append({'header': j})
        self.worksheet.add_table(0, 0, self.row, len(
            header_full) - 1, {'name': 'Firewall', 'columns': header_full})

    def close(self) -> None:
        self.workbook.close()


def main():
    logging.basicConfig(
        format='%(asctime)s %(levelname)s %(message)s',
        level=logging.INFO,
        filename='error_panorama.log',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    directory = os.path.dirname(__file__)
    file = os.path.join(directory, "ips", "ip_list_panorama.txt")
    discover = Discover(file)

    # Table - Firewalls
    firewalls = TableFirewall("panorama.xlsx", "PanoramaFirewalls")
    firewalls.create_table(list_tags)

    # Table - Licenses
    licenses = TableLicenses("licenses.xlsx", "PanoramaLicense")

    connector = WebService(list_tags, 'XXXXXXXXXXXXXXXXXX', 'YYYYYYYYYYYYYYYYYY')

    for url in discover.urls:
        try:
            credential = connector.get_credential(url)

            values = connector.get_firewall_info(url, credential)
            firewalls.insert_information(values)

            response = connector.get_firewall_info_license(url, credential)
            licenses.insert_information_license(response)

        except Exception as e:
            logging.warning("URL Panorama Failed: {}".format(url))

    firewalls.insert_format()
    firewalls.close()

    licenses.insert_format()
    licenses.close()


if __name__ == '__main__':
    main()
