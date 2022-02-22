import xml.etree.ElementTree as ET

class LicensesEntry:
    type: str
    feature_description: str
    expiry_date: str
    warning: str
    name: None

    @staticmethod
    def from_xml(node: ET.Element):
        if node == None: return None
        data = LicensesEntry()
        data.type = node.findtext('type')
        data.feature_description = node.findtext('feature-description')
        data.expiry_date = node.findtext('expiry-date')
        data.warning = node.findtext('warning')
        data.name = node.attrib.get('name')
        return data

    def to_dict(self):
        return {
            'type': self.type,
            'feature_description': self.feature_description,
            'expiry_date': self.expiry_date,
            'warning': self.warning,
            'name': self.name,
        }

class Licenses:
    licenses_entry: list[LicensesEntry]

    @staticmethod
    def from_xml(node: ET.Element):
        if node == None: return None
        data = Licenses()
        data.licenses_entry = [LicensesEntry.from_xml(i) for i in node.findall("entry")]
        return data

    def to_dict(self):
        return {
            'licenses_entry': [i.to_dict() for i in self.licenses_entry],
        }

class Entry:
    serial_no: str
    devicename: str
    licenses: Licenses

    @staticmethod
    def from_xml(node: ET.Element):
        if node == None: return None
        data = Entry()
        data.serial_no = node.findtext('serial-no')
        data.devicename = node.findtext('devicename')
        data.licenses = Licenses.from_xml(node.find("licenses"))
        return data

    def to_dict(self):
        return {
            'serial_no': self.serial_no,
            'devicename': self.devicename,
            'licenses': self.licenses.to_dict() if isinstance(self.licenses, Licenses) else None,
        }

class Devices:
    entry: list[Entry]

    @staticmethod
    def from_xml(node: ET.Element):
        if node == None: return None
        data = Devices()
        data.entry = [Entry.from_xml(i) for i in node.findall("entry")]
        return data

    def to_dict(self):
        return {
            'entry': [i.to_dict() for i in self.entry],
        }

class Result:
    devices: Devices

    @staticmethod
    def from_xml(node: ET.Element):
        if node == None: return None
        data = Result()
        data.devices = Devices.from_xml(node.find("devices"))
        return data

    def to_dict(self):
        return {
            'devices': self.devices.to_dict() if isinstance(self.devices, Devices) else None,
        }

class Response:
    result: Result
    status: None

    @staticmethod
    def from_string(xml: str):
        return Response.from_xml(ET.fromstring(xml))

    @staticmethod
    def from_file(xml: str):
        return Response.from_xml(ET.parse(xml).getroot())

    @staticmethod
    def from_xml(node: ET.Element):
        if node == None: return None
        data = Response()
        data.result = Result.from_xml(node.find("result"))
        data.status = node.attrib.get('status')
        return data

    def to_dict(self):
        return {
            'result': self.result.to_dict() if isinstance(self.result, Result) else None,
            'status': self.status,
        }

