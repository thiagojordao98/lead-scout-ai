from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from unittest.mock import patch
from accounts.models import Organization
from leads.models import Lead, AuditResult
from leads.ai import AIScriptGenerator

User = get_user_model()

class AITestCase(TestCase):
    def setUp(self):
        self.org = Organization.objects.create(name="AI Agency")
        self.user = User.objects.create_user(
            email="agent@agency.com",
            password="securepassword123",
            organization=self.org
        )
        self.lead = Lead.objects.create(organization=self.org, name="Restaurante Central")
        self.audit = AuditResult.objects.create(lead=self.lead, has_website=False, score=100)
        
    def test_fallback_script_generation_no_website(self):
        generator = AIScriptGenerator(api_key="")
        script = generator.generate(self.lead)
        self.assertIn("Restaurante Central", script)
        self.assertIn("site", script.lower())
        self.assertIn("não possui um site institucional próprio", script)

    def test_fallback_script_generation_no_ssl(self):
        # Update audit to have website but no ssl
        self.audit.has_website = True
        self.audit.has_ssl = False
        self.audit.score = 50
        self.audit.save()
        
        generator = AIScriptGenerator(api_key="")
        script = generator.generate(self.lead)
        self.assertIn("Restaurante Central", script)
        self.assertIn("seguro", script.lower())
        self.assertIn("ausência do certificado de segurança SSL", script)

    def test_fallback_script_generation_no_professional_email(self):
        # Update audit to have website and ssl but no professional email
        self.audit.has_website = True
        self.audit.has_ssl = True
        self.audit.has_professional_email = False
        self.audit.score = 30
        self.audit.save()
        
        generator = AIScriptGenerator(api_key="")
        script = generator.generate(self.lead)
        self.assertIn("Restaurante Central", script)
        self.assertIn("e-mail", script.lower())
        self.assertIn("domínio genérico", script)

    @patch("openai.resources.chat.completions.Completions.create")
    def test_openai_script_generation_success(self, mock_create):
        # Mock OpenAI response
        class MockChoice:
            class MockMessage:
                content = "Olá do OpenAI! Script de vendas para Restaurante Central."
            message = MockMessage()
        
        class MockResponse:
            choices = [MockChoice()]
            
        mock_create.return_value = MockResponse()
        
        generator = AIScriptGenerator(api_key="mock-api-key")
        script = generator.generate(self.lead)
        self.assertEqual(script, "Olá do OpenAI! Script de vendas para Restaurante Central.")
        mock_create.assert_called_once()

    def test_lead_detail_modal_view_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("leads:lead_detail_modal", args=[self.lead.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "leads/lead_detail_modal.html")
        self.assertEqual(response.context["lead"], self.lead)
        self.assertEqual(response.context["audit"], self.audit)

    def test_lead_detail_modal_view_unauthorized(self):
        # Unauthenticated user
        response = self.client.get(reverse("leads:lead_detail_modal", args=[self.lead.id]))
        self.assertEqual(response.status_code, 302)  # Redirects to login

    def test_generate_sales_script_view_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("leads:generate_sales_script", args=[self.lead.id]))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("script", data)
        self.assertIn("Restaurante Central", data["script"])

    def test_generate_sales_script_view_unauthorized(self):
        response = self.client.post(reverse("leads:generate_sales_script", args=[self.lead.id]))
        self.assertEqual(response.status_code, 302)
