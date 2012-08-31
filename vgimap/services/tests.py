"""
Simple tests for the VGI services available
"""

from django.test import TestCase
from django.test.client import Client

class ServiceTest(TestCase):
    def test_index(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
    def test_search(self):
        resp = self.client.get('/search/')
        self.assertEqual(resp.status_code,200)
    def test_wfs(self):
        resp = self.client.get('/wfs')
        self.assertEqual(resp.status_code,200)
    def test_twitterwfs(self):
        resp = self.client.get('/twitter_wfs')
        self.assertEqual(resp.status_code,200)
