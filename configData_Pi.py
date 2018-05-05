import xml.etree.ElementTree as etree
import logData_Pi
import os


class confDataPi(object):
    # Class constructor
    def __init__(self, filename):
        self.logdt = logData_Pi.logData(__name__)
        self.filename = filename  # Create a variable with the given filename
        self.parse()  # Parse the XML file

    def parse(self):
        try:
            self.tree = etree.parse(self.filename)
            self.root = self.tree.getroot()
        except:
            self.log_data.log("EXCEPT",
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

    def setSteps(self, m_steps, calib=""):
        self.setConfig("Steps", "RA", float(m_steps[0]))
        self.setConfig("Steps", "DEC", float(m_steps[1]))
        if calib != "":
            elm = self.root.find("Steps")
            elm.set("home_calib", str(calib))

    def getPort(self):
        return self.getConfig("TCP", "port")

    def setPort(self, port):
        self.setConfig("TCP", "port", str(port))
