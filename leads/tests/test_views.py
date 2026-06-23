from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from unittest.mock import patch
from accounts.models import Organization
from leads.models import SearchQuery, Lead, AuditResult

User = get_user_model()

class SearchStudioViewsTest(TestCase):
    def setUp(self):
        # Create organizations
        self.org1 = Organization.objects.create(name="Agency 1", credits_balance=5)
        self.org2 = Organization.objects.create(name="Agency 2", credits_balance=0)
        
        # Create users
        self.user1 = User.objects.create_user(
            email="user1@agency1.com",
            password="securepassword123",
            organization=self.org1
        )
        self.user2 = User.objects.create_user(
            email="user2@agency2.com",
            password="securepassword123",
            organization=self.org2
        )

    def test_views_require_login(self):
        # Test Search Studio view redirects to login
        response = self.client.get(reverse("leads:search_studio"))
        self.assertEqual(response.status_code, 302)
        
        # Test Search Status view redirects to login
        response = self.client.get(reverse("leads:search_status", args=[1]))
        self.assertEqual(response.status_code, 302)

        # Test Search Results view redirects to login
        response = self.client.get(reverse("leads:search_results", args=[1]))
        self.assertEqual(response.status_code, 302)

    def test_search_studio_get_authenticated(self):
        self.client.force_login(self.user1)
        response = self.client.get(reverse("leads:search_studio"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "leads/search_studio.html")
        self.assertEqual(response.context["credits_balance"], 5)

    def test_search_studio_post_missing_fields(self):
        self.client.force_login(self.user1)
        response = self.client.post(reverse("leads:search_studio"), {
            "nicho": "",
            "localizacao": "Natal - RN"
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "leads/search_studio.html")
        self.assertIn("error", response.context)
        self.org1.refresh_from_db()
        self.assertEqual(self.org1.credits_balance, 5)

    def test_search_studio_post_insufficient_credits(self):
        self.client.force_login(self.user2)
        response = self.client.post(reverse("leads:search_studio"), {
            "nicho": "Restaurantes",
            "localizacao": "Natal - RN"
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "leads/search_studio.html")
        self.assertTrue(response.context.get("paywall"))
        self.assertEqual(SearchQuery.objects.count(), 0)

    @patch("leads.views.dispatch_search_query")
    def test_search_studio_post_success(self, mock_dispatch):
        self.client.force_login(self.user1)
        response = self.client.post(reverse("leads:search_studio"), {
            "nicho": "Restaurantes",
            "localizacao": "Natal - RN"
        })
        self.org1.refresh_from_db()
        self.assertEqual(self.org1.credits_balance, 4)
        
        query = SearchQuery.objects.first()
        self.assertIsNotNone(query)
        self.assertEqual(query.organization, self.org1)
        self.assertEqual(query.user, self.user1)
        self.assertEqual(query.nicho, "Restaurantes")
        self.assertEqual(query.localizacao, "Natal - RN")
        self.assertEqual(query.status, "PENDING")

        mock_dispatch.assert_called_once_with(query.id)
        self.assertRedirects(response, reverse("leads:search_results", args=[query.id]))

    def test_search_status_view_success(self):
        self.client.force_login(self.user1)
        query = SearchQuery.objects.create(
            organization=self.org1,
            user=self.user1,
            nicho="Restaurantes",
            localizacao="Natal - RN",
            status="PENDING"
        )
        response = self.client.get(reverse("leads:search_status", args=[query.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "PENDING"})

    def test_search_status_view_unauthorized(self):
        self.client.force_login(self.user2)
        query = SearchQuery.objects.create(
            organization=self.org1,
            user=self.user1,
            nicho="Restaurantes",
            localizacao="Natal - RN",
            status="PENDING"
        )
        response = self.client.get(reverse("leads:search_status", args=[query.id]))
        self.assertEqual(response.status_code, 404)

    def test_search_results_view_success_ordering(self):
        self.client.force_login(self.user1)
        query = SearchQuery.objects.create(
            organization=self.org1,
            user=self.user1,
            nicho="Restaurantes",
            localizacao="Natal - RN",
            status="COMPLETED"
        )
        
        # Create leads and their audit results
        lead_low = Lead.objects.create(organization=self.org1, search_query=query, name="Low Score Co")
        AuditResult.objects.create(lead=lead_low, score=30)
        
        lead_high = Lead.objects.create(organization=self.org1, search_query=query, name="High Score Co")
        AuditResult.objects.create(lead=lead_high, score=80)
        
        lead_med = Lead.objects.create(organization=self.org1, search_query=query, name="Med Score Co")
        AuditResult.objects.create(lead=lead_med, score=50)

        response = self.client.get(reverse("leads:search_results", args=[query.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "leads/search_results.html")
        self.assertEqual(response.context["query"], query)
        
        leads_in_context = list(response.context["leads"])
        self.assertEqual(len(leads_in_context), 3)
        self.assertEqual(leads_in_context[0], lead_high)
        self.assertEqual(leads_in_context[1], lead_med)
        self.assertEqual(leads_in_context[2], lead_low)

    def test_search_results_view_unauthorized(self):
        self.client.force_login(self.user2)
        query = SearchQuery.objects.create(
            organization=self.org1,
            user=self.user1,
            nicho="Restaurantes",
            localizacao="Natal - RN",
            status="COMPLETED"
        )
        response = self.client.get(reverse("leads:search_results", args=[query.id]))
        self.assertEqual(response.status_code, 404)
