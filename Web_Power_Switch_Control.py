
try:
    # python 3
    import urllib.request as urllib
except:
    # python 2
    import urllib


class authenticatingURLOpener(urllib.FancyURLopener):
    """
    An opener to supply the username and password when the website asks for it.
    """
    def __init__(self, username, password):
        urllib.FancyURLopener.__init__(self)
        self.username = username
        self.password = password

    def prompt_user_passwd(self, host, realm):
        return self.username, self.password


class webPowerSwitch():
    """
    Very stripped down power switch control. You can only turn on/off outlets.
    A much more exhaustive control is available from the dlipower package.
    Required input: hostname, username, password
    ***Note: hostname can be either the name or the ip address of the WPS
    """
    def __init__(self, hostname, username, password, simulate = False):
        self.url = "http://{username}:{password}@{hostname}/outlet?".format(
            username = username,
            password = password,
            hostname = hostname
            )
        self.local_opener = authenticatingURLOpener(username, password)
        self.simulate = simulate
                
    def on(self, outlet):
        """ Turn on the specified port of this web power switch """
        if self.simulate:
            return 0
        self.__try("{url}{outlet}=ON".format(
            url = self.url,
            outlet = outlet))

    def off(self, outlet):
        """ Turn off the specified port of this web power switch """
        if self.simulate:
            return 0
        self.__try("{url}{outlet}=OFF".format(
            url = self.url,
            outlet = outlet))

    def alloff(self):
        """ Turn off all ports of the web power switch """
        if self.simulate:
            return 0
        for i in range(1,9):
            self.off(i)

    def allon(self):
        """ Turn on all ports of the web power switch """
        if self.simulate:
            return 0
        for i in range(1,9):
            self.on(i)

    def __try(self, url):
        """ encapsulate the url opener to catch exceptions """
        try:
            self.local_opener.open(url)
        except OSError as e:
            print("OSError talking to the switch: {}".format(e))
            exit(1)

    def name(self):
    	return self.hostname