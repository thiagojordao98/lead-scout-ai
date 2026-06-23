from django.test import TestCase
from unittest.mock import patch
from leads.services import SerperClient

class SerperIntegrationTest(TestCase):
    @patch('requests.post')
    def test_serper_client_parses_results(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "places": [
                {
                    "title": "Restaurante Central",
                    "address": "Av. Principal, 100",
                    "phoneNumber": "+55 84 99999-9999",
                    "website": "http://restaurantecentral.com",
                    "cid": "123456789"
                }
            ]
        }
        client = SerperClient(api_key="fake-key")
        results = client.search(nicho="Restaurante", localizacao="Natal, RN")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], "Restaurante Central")
        self.assertEqual(results[0]['place_id'], "123456789")
        
    def test_serper_client_mock_mode_when_key_missing(self):
        client = SerperClient(api_key="")
        results = client.search(nicho="Restaurante", localizacao="Natal, RN")
        self.assertGreater(len(results), 0)
        self.assertTrue(any(r['name'] for r in results))
