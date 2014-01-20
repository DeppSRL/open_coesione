from django.utils.unittest.case import TestCase
import requests


def test_totali(data, tipologia):
    costi = data['aggregati']['totali']['costi']
    pagamenti = data['aggregati']['totali']['pagamenti']
    progetti = data['aggregati']['totali']['progetti']
    oggetti = data['aggregati'][tipologia]
    for t,v in oggetti.iteritems():
        costi -= v['totali']['costi']
        pagamenti -= v['totali']['pagamenti']
        progetti -= v['totali']['progetti']

    assert abs(costi) + abs(pagamenti) + abs(progetti) <= 0.001


class HomeTestCase(TestCase):

    def setUp(self):
        url = 'http://localhost:8020/api'
        self.r = requests.get("{0}/aggregati.json".format(url))
        self.data = self.r.json()

    def test_totali_temi(self):
        test_totali(self.data, 'temi')

    def test_totali_nature(self):
        test_totali(self.data, 'nature')

    def test_isup(self):
        assert self.r.status_code == 200


class TemiTestCase(TestCase):

    def setUp(self):
        self.url = 'http://localhost:8020/api/aggregati/temi'

    def test(self):
        r = requests.get("{0}.json".format(self.url))
        temi = r.json()
        for label,url in temi.iteritems():
            url = "{0}?with_territori=False".format(url)
            r = requests.get(url)
            assert r.status_code == 200

            data = r.json()
            test_totali(data, 'nature')

class NatureTestCase(TestCase):

    def setUp(self):
        self.url = 'http://localhost:8020/api/aggregati/nature'

    def test(self):
        r = requests.get("{0}.json".format(self.url))
        nature = r.json()
        for label,url in nature.iteritems():
            url = "{0}?with_territori=False".format(url)
            r = requests.get(url)
            assert r.status_code == 200

            data = r.json()
            test_totali(data, 'temi')