import requests
from datetime import datetime
import logging

__author__ = 'guglielmo'



class Visitor(object):
    """
    Module to visit urls. Uses requests.
    """

    urls = []
    logger = None


    def reset_urls(self):
        """
        Resets list of urls to be visited
        """
        self.urls = []

    def add_url(self, url):
        """
        Adds a url to the list of urls to be visited
        """
        self.urls.append(url)

    def set_logger(self, logger):
        """
        Inject a logger
        """
        self.logger = logger

    def visit(self):
        """
        Visits all the urls.
        Returns an array of dictionaries, with url, status and elapsed (millisecs)

        >>> from cache_generation.visitor import Visitor
        >>> v = Visitor()
        >>> v.urls = ['http://www.opencoesione.gov.it', 'http://www.openopzione.it']
        >>> v.visit() #doctest: +ELLIPSIS
        [{'url': 'http://www.opencoesione.gov.it', 'status': 200, 'elapsed-ms': ...}, {'url': 'http://www.openopzione.it', 'status': 400, 'elapsed-ms': ...}]
        """

        results = []
        for u in self.urls:
            t_0 = datetime.now()
            r = requests.get(u)
            t_delta = datetime.now() - t_0
            result = {'url': u, 'status': r.status_code, 'elapsed-ms': int(t_delta.microseconds/1000)}
            if self.logger:
                self.logger.info(result)
            results.append(result)

        return results

    def display(self):
        """
        displays all urls (preview)
        """
        for u in self.urls:
            print u

if __name__ == "__main__":
    import doctest
    doctest.testmod()
