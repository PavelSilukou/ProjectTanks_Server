import ConfigParser

class ConfigReader:

    def __init__(self):
        self.config = ConfigParser.ConfigParser()
        self.server_ip = None
        self.server_port = None

    def get(self, configpath):
        self.config.read(configpath)
        self.server_ip = self.config.get("ServerSettings", "ip")
        self.server_port = self.config.getint("ServerSettings", "port")
