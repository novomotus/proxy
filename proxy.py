import requests
import random
from datetime import datetime, timedelta
import os
from lxml import etree
import settings

# Define Path Variables
CURDIR = os.path.dirname(__file__)


# Check that credentials are defined
if settings.APIKEY or settings.USERID == '':
    raise Exception("Error: APIKEY or USERID incorrectly configured in proxy/settings.py.")


def elapsed_time(previous_time):
    """
    Calculates the elapsed time, in seconds, since a given previous time.
    :param previous_time: Datetime string formatted as YYYY-mm-dd HH:MM:SS.FF
    :return: Seconds float object.
    """

    # Create Datetime Object from Previous Time ( in standard datetime.now() format )
    before = datetime.strptime(previous_time, '%Y-%m-%d %H:%M:%S.%f')

    # Get Nowtime
    now = datetime.now()

    # Return elapsed time, in seconds as ssss.ssss
    return timedelta.total_seconds(now - before)


class Proxy(object):
    """
    Handles proxy requests with proxies provided by BuyProxies.org.
    Requests handled via requests library.

    NOTE: Creates a 'proxydata.xml' datafile in whatever directory file is located to store proxies to avoid
    unnecessary lookups.
    """

    def __init__(self):

        # Define Record variables
        self.record = os.path.join(CURDIR, 'proxydata.xml')
        self.root = 'update'

        # Define Nuances
        self.delimiter = ':'
        self.protocol = 'https'

        # Define Format Options
        self.formats = {
            '1': ('proxy', 'port', 'username', 'password')
        }
        # Define Format
        self.format = '1'

        # Ingest Credentials
        self.USERID = settings.USERID
        self.APIKEY = settings.APIKEY

        # Enforce type for commonly mistyped.
        if type(self.USERID) is int:
            self.USERID = str(self.USERID)

        # Define Check Frequency
        self.check_frequency = 86400 * 1  # 1 day

        # Create Record if Not Already Found
        if os.path.exists(self.record) is False:

            # Create New File
            with open(self.record, 'w') as file:
                file.write(f'<{self.root}></{self.root}>')

            # Parse Datafile
            tree = etree.parse(self.record)
            root = tree.getroot()

            # Create Update & Empty Proxy Element
            updated = etree.SubElement(root, 'time')
            updated.text = str(datetime.now())

            # Save File
            tree.write(self.record)

            self.last_update = datetime.now()
            self.proxies = None

        # Get Existing File & Find Last Update Time (checks proxies for validity)
        else:

            # Parse File
            with open(self.record, 'r')as file:
                data = "".join(file.readlines())
            root = etree.fromstring(data)

            # Get last Updated Time
            self.last_update = root.find('time').text

            # Get Proxies as [(proxy, status)]
            self.proxies = []
            for x in root.findall('proxy'):
                self.proxies.append((
                    x.text,  # Host IP
                    x.get('port'),
                    x.get('user'),
                    x.get('password'),
                    ))

        # Define API URL
        self.apiurl = f'http://api.buyproxies.org/?a=showProxies&pid={settings.USERID}&key={settings.APIKEY}'

    @staticmethod
    def random_test_url():
        """
        Gets a random url to use in testing proxy health.
        NOTE: All urls are assumed to be highly-likely as active, and each page is lightweight.
        :return: url string
        """
        # Define Trusted Urls
        urls = [
            'http://yahoo.com/robots.txt',
            'https://www.reddit.com//robots.txt',
            'http://www.cnn.com//robots.txt',
            'https://twitter.com/robots.txt',
            'https://pinterest.com/robots.txt',
            'https://plus.google.com/robots.txt',
            'https://tumblr.com/robots.txt',
            'http://last.fm/robots.txt',
            'https://amazon.com/robots.txt',
            'https://bing.com/robots.txt',
            'http://instagram.com/robots.txt',
            'http://ebay.com/robots.txt',
            'http://netflix.com/robots.txt',
            'http://microsoft.com/robots.txt',
            'https://wordpress.com/robots.txt',
            'https://medium.com/robots.txt',
            'https://blogger.com/robots.txt',
            'https://stackoverflow.com/robots.txt',
            'https://imgur.com/robots.txt'
        ]
        return urls[random.sample(range(0, len(urls)), 1)[0]]

    @staticmethod
    def random_user_agent():
        """
        Provides a random user-agent from a list.
        @Reference: https://developers.whatismybrowser.com/useragents/explore/
        NOTES: This method generates a random user-agent to assign to proxies. Using a different user-agent with each
        proxy request is likely to trigger bot filters. For example, most single IP addresses wouldn't present with 10+
        user-agents. However, most IP addresses WOULD present with several, as well as several devices. Consider
        implementing an IP:User-Agent record that limits x number of User-Agents (assigned) per IP.
        @todo implement generative approach for user agents rather than simple lists
        :return: http user-agent request header formatted string
        """
        user_agents = [

            # Chrome
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
            'Mozilla/5.0 (Windows NT 5.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',

            # Internet Explorer
            'Mozilla/5.0 (Windows NT 6.2; WOW64; Trident/7.0; rv:11.0) like Gecko',
            'Mozilla/5.0 (Windows NT 6.1; Win64; x64; Trident/7.0; rv:11.0) like Gecko',
            'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; Touch; rv:11.0) like Gecko',

            # Mozilla
            'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0',
            'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:63.0) Gecko/20100101 Firefox/63.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0',
            'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0'
        ]

        # Get Random Index
        r = random.sample(range(0, len(user_agents)), 1)[0]

        return user_agents[r]

    def request_proxies(self):
        """
        Gets a list of proxies using the BuyProxies.org API.
        :return: List of tuple Proxy Data formatted as [(ip, port, username, password)]
        """
        # Update & Check Proxies
        data = requests.get(self.apiurl)

        # Parse API Response
        proxies = []
        for line in data.text.split('\n')[:-1]:

            # Get Raw Response Data
            parts = line.split(self.delimiter)

            # ID Data, given format
            if self.format == '1':

                # ID Data
                proxy = parts[0]
                port = parts[1]
                username = parts[2]
                password = parts[3]

                # Save to Check Later
                proxies.append((proxy, port, username, password))

        return proxies

    def get_proxies(self):
        """
        Gets list of most current proxies. If none, fetches new.
        :return: list of proxy data tuples as [(proxy, port, username, password)]
        """
        # If no existing proxies
        if self.proxies is None or len(self.proxies) == 0:

            # Get Proxies
            self.proxies = self.request_proxies()

            # Update Record
            self.update_record(self.proxies)

        return self.proxies

    def get_proxy(self):
        """
        Gets a single random proxy from available proxies
        :return: proxy as (host, port, username, password)
        """
        if self.proxies is None or len(self.proxies) == 0:
            self.get_proxies()

        return self.proxies[random.sample(range(0, len(self.proxies)), 1)[0]]

    def format_proxy(self, user, password, port, host):
        """
        Formats a proxy for use as requests.proxies argument.
        :param user: string username
        :param password: string password
        :param port: string port
        :param host: string ip address
        :return: dict as {'protocol': 'protocol://user:password@host:port'}
        """
        return {f'{self.protocol}': f'{self.protocol}://{user}:{password}@{host}:{port}'}

    def check_proxy(self, user, password, host, port):
        """
        Checks if proxy is valid.
        :param user: string username text.
        :param password: string password
        :param host: string IP address as xx.xxx.xxx.xxx
        :param port: string port. ex 80
        :return: Boolean for active or not, determined by http request status code of random url request.
        """

        # Define Proxy for Check
        proxy = self.format_proxy(user=user, password=password, host=host, port=port)

        # Check health, as much as 3 times before assuming proxy is dead.
        errors = 0
        valid = False
        while errors < 3:
            r = requests.get(self.random_test_url(), proxies=proxy)
            if r.status_code == 200:
                valid = True
                break
            else:
                errors += 1

        return valid

    def update_record(self, proxy_list):
        """
        Updates the proxy record with active proxies.
        NOTE: Updates the Class variable self.proxies as well.
        :param proxy_list: list of tuples as such: [(host, user, password, port)]
        """
        # Create New File
        with open(self.record, 'w')as file:
            file.write(f'<{self.root}></{self.root}>')

        # Define Root Node
        tree = etree.parse(self.record)
        root = tree.getroot()

        # Do Update Time
        updated = etree.SubElement(root, 'time')
        updated.text = str(datetime.now())

        # Save Each Proxy
        proxies = etree.SubElement(root, 'proxies')
        for p in proxy_list:

            # Create Proxy Node
            proxy = etree.SubElement(proxies, 'proxy')

            # Add Data
            proxy.text = p[0]

            # Add Attributes
            proxy.attrib['user'] = p[2]
            proxy.attrib['password'] = p[3]
            proxy.attrib['port'] = p[1]

        # Update Global List
        self.proxies = [(x[0], x[1], x[2], x[3]) for x in proxy_list]

        # Save Data
        tree.write(self.record)

    def update(self, force=False):
        """
        Checks if proxies still active.
        :param force: Boolean argument check status regardless of time elapsed since last check.

        NOTE: Updates the self.record datafile.
        """

        # If existing proxies
        if len(self.proxies) > 0:

            # If elapsed time long enough or force is true
            if elapsed_time(self.last_update) > self.check_frequency or force is True:

                # Check Each proxy
                good = []
                for p in self.proxies:

                    # ID Data
                    user = p[2]
                    pwrd = p[3]
                    host = p[0]
                    port = p[1]

                    # Check if Active
                    valid = self.check_proxy(user=user, password=pwrd, host=host, port=port)

                    # Keep good proxies
                    if valid is True:
                        good.append(p)  # (host, user, password, port)

                # Update Proxy Datafile
                self.update_record(good)

                # Update class variable
                self.proxies = good

        # If no existing proxies are found do update
        else:
            # Get New Proxies
            proxies = self.request_proxies()  # (ip, port, user, password)

            # Check Each proxy
            good = []
            for p in proxies:

                # ID Data
                user = p[2]
                pwrd = p[3]
                host = p[0]
                port = p[1]

                # Check if Active
                valid = self.check_proxy(user=user, password=pwrd, host=host, port=port)

                # Keep Good Proxies
                if valid is True:
                    good.append(p)

            # Update Proxy Record
            # NOTE: Updates self.proxies variable as well.
            self.update_record(good)

    def get(self, url, headers=None):
        """
        Makes a proxy request using the requests library and a buyproxy.org proxy.
        NOTE: No error handling or conditional operation other than methods, paramters, and headers.
        :param url url string to send proxy request to.
        :return: request response object
        """

        # Use random user-agent at least, if no headers specified
        if headers is None:
            headers = {'user-agent': self.random_user_agent()}

        # Get Random Proxy
        p = self.get_proxy()

        # Format Proxy
        proxy = self.format_proxy(user=p[2], password=p[3], host=p[0], port=p[1])

        # make request
        return requests.get(url, headers=headers, proxies=proxy)
