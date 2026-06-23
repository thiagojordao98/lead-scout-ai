from django.test import TransactionTestCase
from unittest.mock import patch
import time
from accounts.models import Organization
from leads.models import SearchQuery, Lead
from leads.tasks import process_search_query_task, dispatch_search_query

class TaskExecutionTest(TransactionTestCase):
    def setUp(self):
        self.org = Organization.objects.create(name="Async Agency")
        
    def test_background_task_creates_leads_and_audits(self):
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

    def test_dispatch_search_query(self):
        query = SearchQuery.objects.create(
            organization=self.org,
            nicho="Dentista",
            localizacao="Natal, RN",
            status="PENDING"
        )
        dispatch_search_query(query.id)
        
        # Since it runs in a background thread, we wait up to 2 seconds for it to complete.
        # This is safe and reliable as it uses the mock search client.
        for _ in range(20):
            query.refresh_from_db()
            if query.status in ["COMPLETED", "FAILED"]:
                break
            time.sleep(0.1)
            
        self.assertEqual(query.status, "COMPLETED")
