import xml.etree.ElementTree as etree
import logging


class confDataPi(object):
    """
    Handle the XML file, containing the required settings
    """

    def __init__(self, filename):
        """Configuration data handling class constructor

        Args:
            filename (str): Provide the path of the XML settings file

        Todo:
            Specify possible exception types to catch

        Warnings:
            The constructor tries to parse the provided file and if there is an error in that process,
            then the program exits, appending the appropriate message in the log file. The parsing is done by calling
            the appropriate method.
        """
        self.log_data = logging.getLogger(__name__)  # Create the logger object
        self.filename = filename  # Create a variable with the given filename

        # Parse the XML file
        try:
            self.tree = etree.parse(self.filename)
            self.root = self.tree.getroot()
        except Exception:
            self.log_data.exception("An exception occurred while parsing the XML settings file. See the traceback "
                                    "below.")
            exit(1)  # Exit the program since the settings file is important

    def parse(self):
        """Parses the XML settings file, or a general XML file

        Parse the XML settings file, the path of which is provided as the constructor's argument. If any error has
        encountered during the parsing process and an exception has been thrown, then the program exits with a return
        code equal to 1.

        Todo:
           Specify possible exception types to catch

        Returns:
            Does not return anything

        Warnings:
            If an exception is thrown during the parsing process, then the program exits in order to avoid undefined
            behaviour when the data from the XML settings file is absent.
        """
        try:
            self.tree = etree.parse(self.filename)
            self.root = self.tree.getroot()
        except Exception:
            self.log_data.exception(
                    "An exception occurred trying parse the XML settings file. See the traceback below.")
            exit(1)  # Exit the program since the settings file is important

    def getConfig(self, child, subchild):
        """Get the desired configuration from the parsed XML file

        This method tries to find the provided configuration in the parsed XML file. A parsed XML file is assumed.

        Todo:
            Check whether an exception catch is required during the search process

        Args:
            child (str): Provide the child element to be found
            subchild (str): Sub-child attribute

        Returns:

        """
        children = list(self.root.find(child))
        for item in children:
            if item.tag == subchild:
                return item.text
            else:
                continue

    def setConfig(self, element, child, value):
        """

        Args:
            element:
            child:
            value:

        Returns:

        """
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
        """

        Returns:

        """
        elm = self.root.find("Steps")
        return [float(self.getConfig("Steps", "RA")), float(self.getConfig("Steps", "DEC")), elm.get("home_calib")]

    # Make it as direct as possible to save time
    def setSteps(self, m_steps, calib=""):
        """

        Args:
            m_steps:
            calib:

        Returns:

        """
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
        """

        Returns:

        """
        return self.getConfig("TCPServer", "host")

    def setHost(self, host):
        """

        Args:
            host:

        Returns:

        """
        self.setConfig("TCPServer", "host", str(host))

    def getPort(self):
        """

        Returns:

        """
        return self.getConfig("TCPServer", "port")

    def setPort(self, port):
        """

        Args:
            port:

        Returns:

        """
        self.setConfig("TCPServer", "port", str(port))

    # Client data
    def getClientHost(self):
        """

        Returns:

        """
        return self.getConfig("TCPClient", "host")

    def setClientHost(self, host):
        """

        Args:
            host:

        Returns:

        """
        self.setConfig("TCPClient", "host", str(host))

    def getClientPort(self):
        """

        Returns:

        """
        return self.getConfig("TCPClient", "port")

    def setClientPort(self, port):
        """

        Args:
            port:

        Returns:

        """
        self.setConfig("TCPClient", "port", str(port))
