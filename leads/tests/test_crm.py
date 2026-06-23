from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from accounts.models import Organization
from leads.models import Lead, PipelineCard

User = get_user_model()

class CRMTestCase(TestCase):
    def setUp(self):
        # Create organizations
        self.org1 = Organization.objects.create(name="CRM Agency A")
        self.org2 = Organization.objects.create(name="CRM Agency B")
        
        # Create users
        self.user1 = User.objects.create_user(
            email="user1@agencya.com",
            password="password123",
            organization=self.org1
        )
        self.user2 = User.objects.create_user(
            email="user2@agencyb.com",
            password="password123",
            organization=self.org2
        )
        
        # Create leads
        self.lead1 = Lead.objects.create(organization=self.org1, name="Prospect Agency A")
        self.lead2 = Lead.objects.create(organization=self.org2, name="Prospect Agency B")

    def test_add_lead_creates_pipeline_card(self):
        # Create card manually to test model behavior
        card = PipelineCard.objects.create(organization=self.org1, lead=self.lead1, stage="NOVO")
        self.assertEqual(card.stage, "NOVO")
        self.assertEqual(card.order, 0)
        self.assertEqual(str(card), f"{self.lead1.name} - NOVO")

    def test_crm_board_requires_login(self):
        response = self.client.get(reverse("leads:crm_kanban"))
        self.assertEqual(response.status_code, 302)

    def test_crm_board_displays_only_own_organization_cards(self):
        self.client.force_login(self.user1)
        # Create card for org1 and org2
        card1 = PipelineCard.objects.create(organization=self.org1, lead=self.lead1, stage="NOVO")
        card2 = PipelineCard.objects.create(organization=self.org2, lead=self.lead2, stage="CONTATO")
        
        response = self.client.get(reverse("leads:crm_kanban"))
        self.assertEqual(response.status_code, 200)
        
        stages = response.context["stages"]
        # org1 should see lead1 but NOT lead2
        self.assertIn(card1, stages["NOVO"])
        self.assertNotIn(card2, stages["CONTATO"])

    def test_add_to_pipeline_view(self):
        self.client.force_login(self.user1)
        response = self.client.get(reverse("leads:add_to_pipeline", args=[self.lead1.id]))
        # Should redirect to CRM Kanban
        self.assertRedirects(response, reverse("leads:crm_kanban"))
        
        # Verify card is created
        self.assertTrue(PipelineCard.objects.filter(lead=self.lead1, organization=self.org1, stage="NOVO").exists())

    def test_add_to_pipeline_unauthorized_lead(self):
        self.client.force_login(self.user1)
        # Try to add lead belonging to org2
        response = self.client.get(reverse("leads:add_to_pipeline", args=[self.lead2.id]))
        self.assertEqual(response.status_code, 404)
        self.assertFalse(PipelineCard.objects.filter(lead=self.lead2).exists())

    def test_update_card_stage_success(self):
        self.client.force_login(self.user1)
        card = PipelineCard.objects.create(organization=self.org1, lead=self.lead1, stage="NOVO")
        
        response = self.client.post(
            reverse("leads:update_stage"),
            {"card_id": card.id, "stage": "NEGOCIACAO"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "success"})
        
        card.refresh_from_db()
        self.assertEqual(card.stage, "NEGOCIACAO")

    def test_update_card_stage_unauthorized(self):
        self.client.force_login(self.user1)
        # Card of org2
        card2 = PipelineCard.objects.create(organization=self.org2, lead=self.lead2, stage="NOVO")
        
        response = self.client.post(
            reverse("leads:update_stage"),
            {"card_id": card2.id, "stage": "NEGOCIACAO"}
        )
        # Should return 404 since it's not the user's organization card
        self.assertEqual(response.status_code, 404)
        
        card2.refresh_from_db()
        self.assertEqual(card2.stage, "NOVO")

    def test_update_card_stage_invalid(self):
        self.client.force_login(self.user1)
        card = PipelineCard.objects.create(organization=self.org1, lead=self.lead1, stage="NOVO")
        
        response = self.client.post(
            reverse("leads:update_stage"),
            {"card_id": card.id, "stage": "INVALID_STAGE"}
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"status": "error"})
        
        card.refresh_from_db()
        self.assertEqual(card.stage, "NOVO")
