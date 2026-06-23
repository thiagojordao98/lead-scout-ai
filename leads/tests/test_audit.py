from django.test import TestCase
from unittest.mock import patch
import requests

from accounts.models import Organization
from leads.models import Lead, AuditResult
from leads.services import AuditService

class AuditServiceTest(TestCase):
    def setUp(self):
        self.org = Organization.objects.create(name="Test Agency")
        
    def test_audit_lead_no_website(self):
        lead = Lead.objects.create(organization=self.org, name="No Website Co", website=None)
        service = AuditService()
        audit_res = service.audit_lead(lead)
        
        self.assertEqual(audit_res.has_website, False)
        self.assertEqual(audit_res.has_ssl, False)
        self.assertEqual(audit_res.has_professional_email, False)
        self.assertEqual(audit_res.score, 100)  # +50 no site, +30 no SSL, +20 no professional email
        self.assertTrue(lead.is_hot)

    @patch('requests.get')
    def test_audit_lead_with_ssl_and_professional_email(self, mock_get):
        class MockResponse:
            def __init__(self, text, status_code=200):
                self.text = text
                self.status_code = status_code

        mock_get.side_effect = [
            MockResponse("Contact us at info@cleancompany.com or sales@cleancompany.com", status_code=200)
        ]

        lead = Lead.objects.create(organization=self.org, name="Clean Co", website="https://cleancompany.com")
        service = AuditService()
        audit_res = service.audit_lead(lead)

        self.assertEqual(audit_res.has_website, True)
        self.assertEqual(audit_res.has_ssl, True)
        self.assertEqual(audit_res.has_professional_email, True)
        self.assertEqual(audit_res.score, 0)
        self.assertFalse(lead.is_hot)
        
        # Verify lead email is updated if not already set
        lead.refresh_from_db()
        self.assertIn(lead.email, ["info@cleancompany.com", "sales@cleancompany.com"])

    @patch('requests.get')
    def test_audit_lead_no_ssl_but_with_professional_email(self, mock_get):
        class MockResponse:
            def __init__(self, text, status_code=200):
                self.text = text
                self.status_code = status_code

        mock_get.side_effect = [
            requests.exceptions.SSLError("SSL verification failed"),  # SSL probe fails
            MockResponse("Contact us at admin@insecure.com", status_code=200)  # scrape
        ]

        lead = Lead.objects.create(organization=self.org, name="Insecure Co", website="http://insecure.com")
        service = AuditService()
        audit_res = service.audit_lead(lead)

        self.assertEqual(audit_res.has_website, True)
        self.assertEqual(audit_res.has_ssl, False)
        self.assertEqual(audit_res.has_professional_email, True)
        self.assertEqual(audit_res.score, 30)  # +30 no SSL
        self.assertFalse(lead.is_hot)
        
        lead.refresh_from_db()
        self.assertEqual(lead.email, "admin@insecure.com")

    @patch('requests.get')
    def test_audit_lead_with_ssl_but_generic_email(self, mock_get):
        class MockResponse:
            def __init__(self, text, status_code=200):
                self.text = text
                self.status_code = status_code

        mock_get.side_effect = [
            MockResponse("Contact us at business@gmail.com", status_code=200)
        ]

        lead = Lead.objects.create(organization=self.org, name="Gmail Co", website="https://gmailco.com")
        service = AuditService()
        audit_res = service.audit_lead(lead)

        self.assertEqual(audit_res.has_website, True)
        self.assertEqual(audit_res.has_ssl, True)
        self.assertEqual(audit_res.has_professional_email, False)
        self.assertEqual(audit_res.score, 20)  # +20 no professional email
        self.assertFalse(lead.is_hot)
        
        # Lead email should NOT be set to the generic email according to brief (we only set professional emails to lead.email)
        lead.refresh_from_db()
        self.assertFalse(lead.email)

    @patch('requests.get')
    def test_audit_lead_no_ssl_and_generic_email(self, mock_get):
        class MockResponse:
            def __init__(self, text, status_code=200):
                self.text = text
                self.status_code = status_code

        mock_get.side_effect = [
            requests.exceptions.ConnectionError("Connection refused"),  # SSL probe fails
            MockResponse("Contact us at user@hotmail.com", status_code=200)  # scrape
        ]

        lead = Lead.objects.create(organization=self.org, name="Bad Co", website="http://badco.com")
        service = AuditService()
        audit_res = service.audit_lead(lead)

        self.assertEqual(audit_res.has_website, True)
        self.assertEqual(audit_res.has_ssl, False)
        self.assertEqual(audit_res.has_professional_email, False)
        self.assertEqual(audit_res.score, 50)  # +30 no SSL, +20 no professional email
        self.assertFalse(lead.is_hot)

    @patch('requests.get')
    def test_audit_lead_request_exception_handling(self, mock_get):
        # Simulate timeout or connection failure for all requests
        mock_get.side_effect = requests.exceptions.Timeout("Request timed out")

        lead = Lead.objects.create(organization=self.org, name="Timeout Co", website="https://timeoutco.com")
        service = AuditService()
        audit_res = service.audit_lead(lead)

        self.assertEqual(audit_res.has_website, True)
        self.assertEqual(audit_res.has_ssl, False)
        self.assertEqual(audit_res.has_professional_email, False)
        self.assertEqual(audit_res.score, 50)  # +30 no SSL, +20 no professional email
        self.assertFalse(lead.is_hot)
        
        self.assertIn("ssl_error", audit_res.details)
        self.assertIn("http_error", audit_res.details)
