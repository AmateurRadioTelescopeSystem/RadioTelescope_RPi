import xml.etree.ElementTree as etree
import logging


class confDataPi(object):
    # Class constructor
    def __init__(self, filename):
        self.log_data = logging.getLogger(__name__)
        self.filename = filename  # Create a variable with the given filename

        # Parse the XML file
        try:
            self.tree = etree.parse(self.filename)
            self.root = self.tree.getroot()
        except Exception:
            self.log_data.exception(
                "An exception occurred trying parse the XML settings file. See the traceback below.")
            exit(1)  # Exit the program since the settings file is important

    def parse(self):
        try:
            self.tree = etree.parse(self.filename)
            self.root = self.tree.getroot()
        except Exception:
            self.log_data.exception(
                "An exception occurred trying parse the XML settings file. See the traceback below.")
            exit(1)  # Exit the program since the settings file is important

    def getConfig(self, child, subchild):
        children = list(self.root.find(child))
        for item in children:
            if item.tag == subchild:
                return item.text
            else:
                continue

    def setConfig(self, element, child, value):
        elm = self.root.find(element)  # Get the required element from the tree
        children = list(elm)  # List the children of the element
        for item in children:
            if item.tag == child:
                item.text = str(value)  # Make the value into a string before appending it on the settings file
                # elm.set("updated", "yes")
                self.tree.write(self.filename)
                break
            else:
                continue

    def getSteps(self):
        elm = self.root.find("Steps")
        return [float(self.getConfig("Steps", "RA")), float(self.getConfig("Steps", "DEC")), elm.get("home_calib")]

    # Make it as direct as possible to save time
    def setSteps(self, m_steps, calib=""):
        elm = self.root.find("Steps")  # Get the required element from the tree
        if m_steps[0] == "RA":
            elm[0].text = str(m_steps[1])  # Set the RA element on XML
        elif m_steps[0] == "DEC":
            elm[1].text = str(m_steps[2])  # Set the DEC element on XML
        elif m_steps[0] == "BOTH":
            elm[0].text = str(m_steps[1])  # Set the RA element on XML
            elm[1].text = str(m_steps[2])  # Set the DEC element on XML

        if calib != "":
            elm = self.root.find("Steps")
            elm.set("home_calib", str(calib))
        self.tree.write(self.filename)  # Write the data to the XML file

    # Server data
    def getHost(self):
        return self.getConfig("TCPServer", "host")

    def setHost(self, host):
        self.setConfig("TCPServer", "host", str(host))

    def getPort(self):
        return self.getConfig("TCPServer", "port")

    def setPort(self, port):
        self.setConfig("TCPServer", "port", str(port))

    # Client data
    def getClientHost(self):
        return self.getConfig("TCPClient", "host")

    def setClientHost(self, host):
        self.setConfig("TCPClient", "host", str(host))

    def getClientPort(self):
        return self.getConfig("TCPClient", "port")

    def setClientPort(self, port):
        self.setConfig("TCPClient", "port", str(port))
