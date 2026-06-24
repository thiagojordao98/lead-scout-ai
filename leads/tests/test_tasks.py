from django.test import TransactionTestCase
from unittest.mock import patch
import time
from accounts.models import Organization
from leads.models import SearchQuery, Lead
from leads.tasks import process_search_query_task, dispatch_search_query

class TaskExecutionTest(TransactionTestCase):
    def setUp(self):
        self.org = Organization.objects.create(name="Async Agency")
        
    @patch('leads.services.SerperClient.search')
    def test_background_task_creates_leads_and_audits(self, mock_search):
        mock_search.return_value = [
            {
                "place_id": "test_place_1",
                "name": "Test Dental",
                "website": "https://testdental.com",
                "phone": "123456",
                "address": "123 St"
            }
        ]
        query = SearchQuery.objects.create(
            organization=self.org,
            nicho="Dentista",
            localizacao="Natal, RN",
            status="PENDING"
        )
        process_search_query_task(query.id)
        
        query.refresh_from_db()
        self.assertEqual(query.status, "COMPLETED")
        self.assertGreater(query.leads.count(), 0)
        
        first_lead = query.leads.first()
        self.assertIsNotNone(first_lead.audit)

    def test_process_search_query_task_nonexistent_query(self):
        # Should return silently without errors
        process_search_query_task(99999)

    @patch('leads.services.SerperClient.search')
    def test_process_search_query_task_failure_sets_failed_status(self, mock_search):
        mock_search.side_effect = Exception("API error")
        query = SearchQuery.objects.create(
            organization=self.org,
            nicho="Dentista",
            localizacao="Natal, RN",
            status="PENDING"
        )
        process_search_query_task(query.id)
        
        query.refresh_from_db()
        self.assertEqual(query.status, "FAILED")

    @patch('leads.services.SerperClient.search')
    def test_dispatch_search_query(self, mock_search):
        mock_search.return_value = [
            {
                "place_id": "test_place_1",
                "name": "Test Dental",
                "website": "https://testdental.com",
                "phone": "123456",
                "address": "123 St"
            }
        ]
        query = SearchQuery.objects.create(
            organization=self.org,
            nicho="Dentista",
            localizacao="Natal, RN",
            status="PENDING"
        )
        thread = dispatch_search_query(query.id)
        if thread:
            thread.join(timeout=3)
            
        query.refresh_from_db()
        self.assertEqual(query.status, "COMPLETED")
